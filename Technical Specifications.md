
**Live System Architecture (Target: Two-Machine Deployment):**

```mermaid
graph TD
    subgraph Machine 1 (Processing & Audio - e.g., Mac Mini M4/Pro)
        direction LR
        PerformerIn[Performer Input (Audio Interface: Quantum 2626, Control Surface)]
        Ableton[Ableton Live (Sound Generation Engine)]
        subgraph Python Agents
            AA[Audio Analysis Agent]
            SM[Session Manager Agent]
            CA[Control Interface Agent]
            BA_Group{Bandmate Agents (Drums, Bass...)}
            MIDI_Gen[MIDI Generation Agent (controls Ableton)]
            Anim_Ctrl[Animation Control Agent]
            Stage_Vis[Stage Visuals Agent (Optional)]
        end
        PerformerIn -- Audio Stream --> AA;
        PerformerIn -- MIDI/OSC Control --> CA;
        AA -- Analysis Results (Chord, Tempo, Dynamics) --> SM;
        CA -- Performer Commands --> SM;
        SM -- Unified Musical Context --> BA_Group;
        BA_Group -- Musical Plans --> MIDI_Gen;
        BA_Group -- Animation Plans --> Anim_Ctrl;
        SM -- High-Level Cues --> Stage_Vis;
        MIDI_Gen -- AbletonOSC Commands --> Ableton;
        Ableton -- Master Audio Out --> PA_System;
        Anim_Ctrl -- OSC/WebSocket Commands --> Network;
        Stage_Vis -- DMX/OSC Commands --> Network;
    end

    subgraph Machine 2 (Rendering - e.g., High-End Mac/Nvidia PC)
        direction LR
        subgraph Game Engine (Godot/Unity/Unreal)
            Listener[OSC/WebSocket Listener Script]
            SceneMgr[Scene Manager Script (Engine Logic)]
            AvatarLoader[Avatar Loader (.glb)]
            AnimPlayer[Animation State Machine/Player]
            ShapeKeyCtrl[Shape Key Controller Script]
            Renderer[Real-time Renderer]
        end
        Network -- OSC/WebSocket Commands --> Listener;
        Listener -- Parsed Commands --> SceneMgr;
        SceneMgr -- Controls --> AvatarLoader;
        SceneMgr -- Controls --> AnimPlayer;
        SceneMgr -- Controls --> ShapeKeyCtrl;
        Renderer -- Rendered Video --> Display;
    end

    subgraph Outputs
      PA_System[PA System / Monitors]
      Display[Projector / Screens]
      Lights[DMX Lighting Rig (Optional)]
    end

    Network -- DMX/OSC Commands --> Lights;