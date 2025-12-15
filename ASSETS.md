# PNG Assets Guide

This guide explains how to add custom PNG graphics to the A* Assault tower defense game.

## Overview

The game supports PNG graphics for:
- **Tiles**: grass, road, forest, swamp, stone
- **Entities**: enemy
- **Buildings**: arrow_tower, bomb_tower, barricade
- **Markers**: START point, END point

If PNG files are not provided, the game automatically falls back to the original rendering (colored rectangles and circles).

## Directory Structure

Create the following directory structure in your game folder:

```
a*-assault/
├── assets/
│   ├── tiles/
│   │   ├── grass.png
│   │   ├── road.png
│   │   ├── forest.png
│   │   ├── swamp.png
│   │   └── stone.png
│   ├── entities/
│   │   └── enemy.png
│   ├── towers/
│   │   ├── arrow_tower.png
│   │   ├── bomb_tower.png
│   │   └── barricade.png
│   └── markers/
│       ├── start.png
│       └── end.png
├── game.py
├── Config.py
└── ... (other game files)
```

## Adding PNG Files

### Step 1: Create the Assets Directory

```bash
mkdir -p assets/tiles assets/entities assets/markers
```

### Step 2: Add Your PNG Files

Place your PNG files in the appropriate directories with the exact filenames shown above.

**Important**: Filenames are case-sensitive and must match exactly:
- Tile PNGs: `grass.png`, `road.png`, `forest.png`, `swamp.png`, `stone.png`
- Entity PNGs: `enemy.png`
- Marker PNGs: `start.png`, `end.png`

### Step 3: Run the Game

The game will automatically detect and load your PNG files. No code changes needed!

## PNG Requirements

### Size Recommendations

- **Tiles**: Design for 28x28 pixels (will be scaled automatically)
- **Enemy**: Design for 28x28 pixels (will be scaled automatically)
- **Markers**: Design for 28x28 pixels (will be scaled automatically)

Your PNG files can be any size - they will be automatically scaled to fit the game's tile size.

### PNG Format

 - Use standard PNG format
 - Keep files simple for best performance
 - Avoid excessive transparency or huge resolutions
 
 ### Example
 
 Any standard image editor (Photoshop, GIMP, Paint.NET) can create compatible PNG files. Just ensure they are saved as ".png".

## Configuration

### Enabling/Disabling PNG Graphics

Edit `Config.py` to control PNG rendering:

```python
# In Config.py
class Config:
    # ... other settings ...
    
    USE_PNG_GRAPHICS = True  # Set to False to always use fallback rendering
```

### Custom Asset Paths

If you want to use different filenames or locations, edit the paths in `Config.py`:

```python
# In Config.py
class Config:
    # ... other settings ...
    
    ASSETS_DIR = "assets"  # Change this to use a different directory
    
    TILE_PNG_PATHS = {
        'grass': 'tiles/grass.png',  # Change filename here
        'road': 'tiles/road.png',
        # ... etc
    }
```

## Troubleshooting

### PNG Files Not Loading

**Problem**: PNG files exist but game still shows fallback rendering

**Solutions**:
1. Verify filenames match exactly (case-sensitive)

2. Check that `USE_PNG_GRAPHICS = True` in `Config.py`

3. Look for warning messages in the console when starting the game

### Performance Issues

**Problem**: Game runs slowly with PNG graphics

**Solutions**:
1. Simplify your PNG files (remove unnecessary elements)
2. The game caches loaded PNGs, so performance should improve after initial load
3. If issues persist, set `USE_PNG_GRAPHICS = False` in `Config.py`

## Partial PNG Support

You don't need to provide all PNG files! The game works with any combination:
i
- **No PNG files**: Uses all fallback rendering (original look)
- **Some PNG files**: Uses PNG where available, fallback for missing files
- **All PNG files**: Full custom graphics

For example, you could provide only `grass.png` and `enemy.png`, and the game will use PNG for those elements while using fallback rendering for everything else.

## Tips for Creating PNG Graphics

1. **Keep it simple**: Simpler PNGs load faster and render better
2. **Use vector shapes**: Avoid embedding raster images in PNGs
3. **Test at small sizes**: Remember tiles are only 28x28 pixels
4. **Use consistent style**: Make all your PNGs match visually
5. **Optimize files**: Use tools like PNGO to reduce file size

## Example Workflow

1. Create PNG files in your favorite vector editor (Inkscape, Adobe Illustrator, etc.)
2. Export as plain PNG (not Inkscape PNG)
3. Save files with correct names in the `assets/` directory
4. Run the game to see your graphics!
