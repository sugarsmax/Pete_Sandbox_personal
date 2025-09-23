https://vimeo.com/63653873

## Street View Hyperlapse Automation - Project Complete! ✅

**Date**: September 23, 2025
**Status**: Successfully implemented and tested

### Key Findings:
- **Hybrid Navigation System**: Combines keyboard and mouse interaction for optimal movement
- **Forward Movement**: Up-arrow key provides reliable movement along street paths for traditional hyperlapses
- **Panoramic Sweeps**: Left/right side clicking enables natural 360° rotational captures for architectural tours
- **Natural Panning**: Side clicking mimics natural mouse behavior for smoother left/right rotation
- **Better Continuity**: Each navigation method optimized for its specific use case
- **Organized Captures**: Each run creates a unique timestamped folder for better file management
- **Cross-Platform**: Works reliably with Playwright automation

### Test Results:
1. **Times Square, NYC**: Captured 5 frames showing various Street View photos from different contributors (2017-2023)
2. **Bridge of the Gods, WA/OR**: Captured 5 frames showing smooth progression across the bridge from Washington to Oregon

### Files Created:
- `street_view_hyperlapse_20250923.py` - Complete automation script with CLI interface
- Frame captures in `.playwright-mcp/` directory
- This documentation file

### Usage:
```bash
# Traditional forward hyperlapse (default - uses up-arrow key)
python street_view_hyperlapse_20250923.py --url "STREET_VIEW_URL" --frames 10 --output frames/

# Panoramic sweep left (uses left-side clicking for natural panning)
python street_view_hyperlapse_20250923.py --url "STREET_VIEW_URL" --frames 20 --direction left

# Panoramic sweep right (uses right-side clicking for natural panning)
python street_view_hyperlapse_20250923.py --url "STREET_VIEW_URL" --frames 20 --direction right
```

### Navigation Methods:
- **Forward**: Up-arrow key navigation → Street-to-street movement along paths
- **Left**: Click left side of Street View → Counter-clockwise panoramic rotation  
- **Right**: Click right side of Street View → Clockwise panoramic rotation

### Next Steps:
- Use FFmpeg to create video: `ffmpeg -r 2 -pattern_type glob -i "frames/*.png" -c:v libx264 -pix_fmt yuv420p hyperlapse.mp4`
- Experiment with different locations and frame counts
- Consider adding rotation/panning controls for more dynamic shots

