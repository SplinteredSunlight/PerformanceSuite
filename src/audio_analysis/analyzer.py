"""
Audio analysis module for the Performance Suite.

This module provides functionality to analyze audio input and extract musical features.
"""

import numpy as np
import librosa
import scipy.signal
import collections
import threading
from typing import Dict, Any, Optional, Tuple, List, Deque


class AudioAnalyzer:
    """
    Audio analyzer for extracting musical features from audio input.
    
    This class handles the analysis of audio data to extract features such as:
    - Pitch/notes
    - Chords
    - Tempo
    - Dynamics
    - Timbre
    """

    def __init__(
        self, 
        sample_rate: int = 44100, 
        buffer_size: int = 1024, 
        hop_length: int = 512,
        analysis_mode: str = "balanced"
    ):
        """
        Initialize the audio analyzer.
        
        Args:
            sample_rate: Audio sample rate in Hz
            buffer_size: Size of the audio buffer for analysis
            hop_length: Hop length for feature extraction
            analysis_mode: Analysis mode ("low_latency", "balanced", or "high_accuracy")
        """
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.hop_length = hop_length
        self.analysis_mode = analysis_mode
        
        # Analysis window parameters
        self.n_fft = 2048  # FFT window size
        if analysis_mode == "low_latency":
            self.n_fft = 1024
        elif analysis_mode == "high_accuracy":
            self.n_fft = 4096
        
        # Initialize analysis state
        self.current_tempo: Optional[float] = None
        self.current_key: Optional[str] = None
        self.current_chords: List[str] = []
        self.current_dynamics: float = 0.0
        
        # Tempo tracking
        self.tempo_history: Deque[float] = collections.deque(maxlen=10)
        self.onset_env_history: Deque[np.ndarray] = collections.deque(maxlen=3)
        
        # Pitch tracking
        self.pitch_history: Deque[float] = collections.deque(maxlen=5)
        self.pitch_confidence_history: Deque[float] = collections.deque(maxlen=5)
        
        # Chord tracking
        self.chroma_history: Deque[np.ndarray] = collections.deque(maxlen=3)
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Chord templates (major and minor triads)
        self._initialize_chord_templates()
        
    def _initialize_chord_templates(self) -> None:
        """Initialize chord templates for chord recognition."""
        # Major and minor chord templates (12 semitones)
        self.chord_templates = {}
        
        # Major chords (root, major third, perfect fifth)
        for i in range(12):
            template = np.zeros(12)
            template[i] = 1.0  # Root
            template[(i + 4) % 12] = 0.8  # Major third
            template[(i + 7) % 12] = 0.8  # Perfect fifth
            self.chord_templates[f"{librosa.note_to_name(i, octave=False)}"] = template
        
        # Minor chords (root, minor third, perfect fifth)
        for i in range(12):
            template = np.zeros(12)
            template[i] = 1.0  # Root
            template[(i + 3) % 12] = 0.8  # Minor third
            template[(i + 7) % 12] = 0.8  # Perfect fifth
            self.chord_templates[f"{librosa.note_to_name(i, octave=False)}m"] = template
        
    def analyze_frame(self, audio_frame: np.ndarray) -> Dict[str, Any]:
        """
        Analyze a frame of audio data and extract musical features.
        
        Args:
            audio_frame: Audio data as numpy array
            
        Returns:
            Dictionary containing extracted features
        """
        with self._lock:
            # Ensure audio frame is the right shape
            if len(audio_frame.shape) > 1 and audio_frame.shape[1] > 1:
                # Convert stereo to mono by averaging channels
                audio_frame = np.mean(audio_frame, axis=1)
            
            # Apply pre-emphasis filter to enhance high frequencies
            audio_frame = self._apply_pre_emphasis(audio_frame)
            
            # Extract features
            pitch_data = self._extract_pitch(audio_frame)
            chords_data = self._extract_chords(audio_frame)
            tempo_data = self._estimate_tempo(audio_frame)
            dynamics_data = self._extract_dynamics(audio_frame)
            timbre_data = self._extract_timbre(audio_frame)
            
            # Combine all features with confidence metrics
            features = {
                "tempo": {
                    "value": tempo_data["tempo"],
                    "confidence": tempo_data["confidence"]
                },
                "pitch": {
                    "value": pitch_data["pitch"],
                    "confidence": pitch_data["confidence"],
                    "note": pitch_data["note"] if "note" in pitch_data else None
                },
                "chords": {
                    "value": chords_data["chords"],
                    "confidence": chords_data["confidence"]
                },
                "dynamics": {
                    "value": dynamics_data["value"],
                    "peak": dynamics_data["peak"],
                    "rms": dynamics_data["rms"]
                },
                "timbre": {
                    "mfcc": timbre_data["mfcc"],
                    "spectral_centroid": timbre_data["spectral_centroid"],
                    "spectral_contrast": timbre_data["spectral_contrast"]
                },
            }
            
            # Update internal state
            self.current_tempo = features["tempo"]["value"]
            if chords_data["chords"]:
                self.current_chords = chords_data["chords"]
            self.current_dynamics = features["dynamics"]["value"]
            
            return features
    
    def _apply_pre_emphasis(self, audio_frame: np.ndarray, coef: float = 0.97) -> np.ndarray:
        """
        Apply pre-emphasis filter to the audio frame.
        
        Args:
            audio_frame: Audio data as numpy array
            coef: Pre-emphasis coefficient
            
        Returns:
            Filtered audio frame
        """
        return np.append(audio_frame[0], audio_frame[1:] - coef * audio_frame[:-1])
    
    def _estimate_tempo(self, audio_frame: np.ndarray) -> Dict[str, Any]:
        """
        Estimate the tempo from an audio frame.
        
        Args:
            audio_frame: Audio data as numpy array
            
        Returns:
            Dictionary with tempo estimation and confidence
        """
        result = {
            "tempo": 120.0,  # Default tempo
            "confidence": 0.0
        }
        
        # Check if we have enough data
        if len(audio_frame) < self.hop_length:
            return result
        
        try:
            # Calculate onset strength envelope
            onset_env = librosa.onset.onset_strength(
                y=audio_frame, 
                sr=self.sample_rate,
                hop_length=self.hop_length
            )
            
            # Add to history
            self.onset_env_history.append(onset_env)
            
            # Combine recent onset envelopes for more stable estimation
            if len(self.onset_env_history) >= 2:
                combined_onset_env = np.concatenate(list(self.onset_env_history))
                
                # Estimate tempo
                tempo, tempo_confidence = self._get_tempo_from_onset_env(combined_onset_env)
                
                # Add to history for smoothing
                self.tempo_history.append(tempo)
                
                # Calculate smoothed tempo (weighted average)
                weights = np.linspace(0.5, 1.0, len(self.tempo_history))
                weighted_tempos = np.array(list(self.tempo_history)) * weights
                smoothed_tempo = np.sum(weighted_tempos) / np.sum(weights)
                
                result["tempo"] = smoothed_tempo
                result["confidence"] = tempo_confidence
        except Exception as e:
            print(f"Error in tempo estimation: {e}")
        
        return result
    
    def _get_tempo_from_onset_env(self, onset_env: np.ndarray) -> Tuple[float, float]:
        """
        Estimate tempo from onset strength envelope.
        
        Args:
            onset_env: Onset strength envelope
            
        Returns:
            Tuple of (tempo, confidence)
        """
        # Get tempo distribution
        tempo_dist = librosa.beat.tempo(
            onset_envelope=onset_env,
            sr=self.sample_rate,
            hop_length=self.hop_length,
            aggregate=None
        )
        
        # Find peaks in the distribution
        peaks, _ = scipy.signal.find_peaks(tempo_dist)
        
        if len(peaks) == 0:
            return 120.0, 0.0
        
        # Get the highest peak
        max_peak_idx = peaks[np.argmax(tempo_dist[peaks])]
        max_peak_value = tempo_dist[max_peak_idx]
        
        # Calculate confidence based on peak prominence
        if np.sum(tempo_dist) > 0:
            confidence = max_peak_value / np.sum(tempo_dist)
        else:
            confidence = 0.0
        
        # Get the tempo value at the peak
        tempo = librosa.beat.tempo(
            onset_envelope=onset_env,
            sr=self.sample_rate,
            hop_length=self.hop_length
        )[0]
        
        return float(tempo), float(confidence)
    
    def _extract_pitch(self, audio_frame: np.ndarray) -> Dict[str, Any]:
        """
        Extract the fundamental pitch from an audio frame.
        
        Args:
            audio_frame: Audio data as numpy array
            
        Returns:
            Dictionary with pitch information and confidence
        """
        result = {
            "pitch": None,
            "confidence": 0.0,
            "note": None
        }
        
        # Check if we have enough data
        if len(audio_frame) < self.hop_length:
            return result
        
        try:
            # Use librosa's piptrack for pitch estimation
            pitches, magnitudes = librosa.piptrack(
                y=audio_frame,
                sr=self.sample_rate,
                hop_length=self.hop_length,
                fmin=50,
                fmax=2000
            )
            
            # Find the pitch with the highest magnitude
            pitch_idx = np.unravel_index(magnitudes.argmax(), magnitudes.shape)
            pitch = pitches[pitch_idx]
            
            # Calculate confidence based on magnitude
            confidence = magnitudes[pitch_idx] / np.max(magnitudes) if np.max(magnitudes) > 0 else 0.0
            
            # Add to history for smoothing
            if pitch > 0:
                self.pitch_history.append(pitch)
                self.pitch_confidence_history.append(confidence)
                
                # Calculate weighted average based on confidence
                if len(self.pitch_history) > 0:
                    weights = np.array(list(self.pitch_confidence_history))
                    if np.sum(weights) > 0:
                        weighted_pitches = np.array(list(self.pitch_history)) * weights
                        smoothed_pitch = np.sum(weighted_pitches) / np.sum(weights)
                        
                        # Convert to note name
                        note = librosa.hz_to_note(smoothed_pitch)
                        
                        result["pitch"] = float(smoothed_pitch)
                        result["confidence"] = float(np.mean(self.pitch_confidence_history))
                        result["note"] = note
        except Exception as e:
            print(f"Error in pitch extraction: {e}")
        
        return result
    
    def _extract_chords(self, audio_frame: np.ndarray) -> Dict[str, Any]:
        """
        Extract chord information from an audio frame.
        
        Args:
            audio_frame: Audio data as numpy array
            
        Returns:
            Dictionary with chord information and confidence
        """
        result = {
            "chords": [],
            "confidence": 0.0
        }
        
        # Check if we have enough data
        if len(audio_frame) < self.hop_length:
            return result
        
        try:
            # Extract chroma features
            chroma = librosa.feature.chroma_cqt(
                y=audio_frame,
                sr=self.sample_rate,
                hop_length=self.hop_length
            )
            
            # Add to history
            self.chroma_history.append(chroma)
            
            # Average recent chroma features for stability
            if len(self.chroma_history) > 0:
                avg_chroma = np.mean(np.array(list(self.chroma_history)), axis=0)
                
                # Normalize
                if np.max(avg_chroma) > 0:
                    avg_chroma = avg_chroma / np.max(avg_chroma)
                
                # Compare with chord templates
                chord_scores = {}
                for chord_name, template in self.chord_templates.items():
                    # Reshape template to match chroma
                    template_2d = np.tile(template.reshape(-1, 1), avg_chroma.shape[1])
                    
                    # Calculate correlation
                    correlation = np.sum(avg_chroma * template_2d) / avg_chroma.shape[1]
                    chord_scores[chord_name] = correlation
                
                # Get the top 3 chords
                top_chords = sorted(chord_scores.items(), key=lambda x: x[1], reverse=True)[:3]
                
                # Only include chords with score above threshold
                threshold = 0.5
                valid_chords = [chord for chord, score in top_chords if score > threshold]
                
                # Calculate confidence based on difference between top and second chord
                if len(top_chords) >= 2:
                    confidence = (top_chords[0][1] - top_chords[1][1]) / top_chords[0][1] if top_chords[0][1] > 0 else 0.0
                else:
                    confidence = 1.0 if len(top_chords) > 0 else 0.0
                
                result["chords"] = valid_chords
                result["confidence"] = float(confidence)
        except Exception as e:
            print(f"Error in chord extraction: {e}")
        
        return result
    
    def _extract_dynamics(self, audio_frame: np.ndarray) -> Dict[str, Any]:
        """
        Extract dynamics (volume/intensity) information from an audio frame.
        
        Args:
            audio_frame: Audio data as numpy array
            
        Returns:
            Dictionary with dynamics information
        """
        result = {
            "value": 0.0,
            "peak": 0.0,
            "rms": 0.0
        }
        
        if len(audio_frame) == 0:
            return result
        
        try:
            # Calculate peak level
            peak = np.max(np.abs(audio_frame))
            
            # Calculate RMS energy
            rms = np.sqrt(np.mean(np.square(audio_frame)))
            
            # Normalize to 0.0-1.0 range
            normalized_rms = min(1.0, rms * 10)
            
            # Apply perceptual weighting (emphasize mid-range frequencies)
            # This is a simplified approach - a proper implementation would use
            # frequency-dependent weighting
            
            result["value"] = float(normalized_rms)
            result["peak"] = float(peak)
            result["rms"] = float(rms)
        except Exception as e:
            print(f"Error in dynamics extraction: {e}")
        
        return result
    
    def _extract_timbre(self, audio_frame: np.ndarray) -> Dict[str, Any]:
        """
        Extract timbre information from an audio frame.
        
        Args:
            audio_frame: Audio data as numpy array
            
        Returns:
            Dictionary with timbre features
        """
        result = {
            "mfcc": np.zeros(13),
            "spectral_centroid": 0.0,
            "spectral_contrast": np.zeros(6)
        }
        
        # Check if we have enough data
        if len(audio_frame) < self.hop_length:
            return result
        
        try:
            # Extract MFCCs
            mfcc = librosa.feature.mfcc(
                y=audio_frame,
                sr=self.sample_rate,
                n_mfcc=13,
                hop_length=self.hop_length
            )
            
            # Extract spectral centroid
            spectral_centroid = librosa.feature.spectral_centroid(
                y=audio_frame,
                sr=self.sample_rate,
                hop_length=self.hop_length
            )
            
            # Extract spectral contrast
            spectral_contrast = librosa.feature.spectral_contrast(
                y=audio_frame,
                sr=self.sample_rate,
                hop_length=self.hop_length
            )
            
            # Average across time
            avg_mfcc = np.mean(mfcc, axis=1)
            avg_centroid = np.mean(spectral_centroid)
            avg_contrast = np.mean(spectral_contrast, axis=1)
            
            result["mfcc"] = avg_mfcc
            result["spectral_centroid"] = float(avg_centroid)
            result["spectral_contrast"] = avg_contrast
        except Exception as e:
            print(f"Error in timbre extraction: {e}")
        
        return result
