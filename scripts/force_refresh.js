// Force Refresh Script
// This script adds a timestamp parameter to CSS and JS files to force a browser cache refresh

document.addEventListener('DOMContentLoaded', function() {
    console.log('Force refresh script running...');
    
    // Add timestamp to CSS files
    const cssLinks = document.querySelectorAll('link[rel="stylesheet"]');
    cssLinks.forEach(link => {
        const url = new URL(link.href);
        url.searchParams.set('t', Date.now());
        link.href = url.toString();
    });
    
    // Add timestamp to JS files
    const scriptTags = document.querySelectorAll('script[src]');
    scriptTags.forEach(script => {
        const url = new URL(script.src);
        url.searchParams.set('t', Date.now());
        script.src = url.toString();
    });
    
    console.log('Force refresh complete');
});