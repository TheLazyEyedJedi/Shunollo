"""
visual_cortex.py
================
The Core Video Processor.
Generates generic visual representations (images) of sensory events.
Expects abstract "light" and "position" data.

Protocol (Input Dict):
{
    "light": {
        "hue": 0-360,
        "brightness": 0-255,
        "saturation": 0.0-1.0
    },
    "position": {
        "x": 0.0-1.0, (Normalized)
        "y": 0.0-1.0
    }
}
"""
import os
import random
import time
from typing import Dict, Any
from shunollo_core.config import config

def analyze_scene(sensory_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts cognitive features from the visual field ONE-WAY (Retina -> V1).
    Used by the Manager to 'See' patterns without rendering pixels.
    """
    light = sensory_data.get("light", {})
    pos = sensory_data.get("position", {})
    
    # Feature 1: Visual Saliency (Brightness * Saturation)
    # Bright = High Energy, Saturated = Pure/Specific
    brightness = light.get("brightness", 0) / 255.0
    saturation = light.get("saturation", 0.0)
    saliency = brightness * saturation
    
    # Feature 2: Color Semantics (Red = Danger, Blue = Calm)
    hue = light.get("hue", 0)
    semantic_tag = "neutral"
    if (hue < 20) or (hue > 340): semantic_tag = "danger" # Red
    elif (hue > 200) and (hue < 260): semantic_tag = "stable" # Blue
    elif (hue > 80) and (hue < 140): semantic_tag = "safe" # Green
    
    return {
        "saliency": round(saliency, 2),
        "semantic_color": semantic_tag,
        "centroid": {
            "x": round(pos.get("x", 0.5), 2),
            "y": round(pos.get("y", 0.5), 2)
        }
    }

def synthesize_visual_event(sensory_data: Dict[str, Any], output_dir: str = None, correlation_id: str = None, **kwargs) -> str:
    """Generates a PPM image file based on generic Light/Position sensory data."""
    if output_dir is None:
        output_dir = config.storage["cache_dir"]
        
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Extract Light Data
    light = sensory_data.get("light", {})
    hue = light.get("hue", 180)
    brightness = light.get("brightness", 128)
    saturation = light.get("saturation", 0.5)
    
    # 2. Extract Position Data
    pos = sensory_data.get("position", {})
    norm_x = pos.get("x", 0.5)
    norm_y = pos.get("y", 0.5)
    
    # Size Logic
    width, height = 64, 64
    center_x = int(norm_x * (width - 1))
    center_y = int(norm_y * (height - 1))
    
    center_x = max(0, min(width-1, center_x))
    center_y = max(0, min(height-1, center_y))
    
    # 3. Generate Pixels (Fast Rendering)
    header = f"P3\n{width} {height}\n255\n"
    grid = [["0 0 0" for _ in range(width)] for _ in range(height)]
    
    # Color Math
    r_base, g_base, b_base = _hsl_to_rgb(hue, saturation, 0.5)
    intensity = max(0.1, min(brightness / 255.0, 1.0))
    
    r = int(r_base * intensity * 255)
    g = int(g_base * intensity * 255)
    b = int(b_base * intensity * 255)
    color_str = f"{r} {g} {b}"
    
    # Draw Cross
    size = 1 if brightness < 100 else 2
    for dy in range(-size + 1, size):
        for dx in range(-size + 1, size):
            if (dx == 0) or (dy == 0):
                px, py = center_x + dx, center_y + dy
                if 0 <= px < width and 0 <= py < height:
                    grid[py][px] = color_str
    
    pixel_data = "\n".join([" ".join(row) for row in grid])
    
    # 4. Write File
    filename = f"event_visual_{random.randint(1000,9999)}.ppm"
    filepath = os.path.join(output_dir, filename)
    absolute_path = os.path.abspath(filepath)
    
    with open(absolute_path, "w") as f:
        f.write(header)
        f.write(pixel_data)
        f.write("\n")

    # 5. Log to Artifact Database
    if correlation_id and "memory" in kwargs and kwargs["memory"]:
        try:
             kwargs["memory"].store_artifact(correlation_id, "visual", filename)
        except Exception as e:
             # Fail silently or log
             pass
    elif correlation_id: # Legacy fallback if memory not passed (won't work if DB deleted)
         pass 
                
    return absolute_path

def generate_heatmap(events: list, output_dir: str = None) -> str:
    """
    Generates a 2D density map (Heatmap) of multiple events.
    Useful for seeing clusters of activity over time.
    """
    if output_dir is None:
        output_dir = config.storage["cache_dir"]
    os.makedirs(output_dir, exist_ok=True)

    width, height = 128, 128 # Higher resolution for heatmaps
    grid = [[0.0 for _ in range(width)] for _ in range(height)]
    
    # 1. Accumulate Density
    for ev in events:
        pos = ev.get("position", {})
        nx = pos.get("x", 0.5)
        ny = pos.get("y", 0.5)
        
        cx = int(nx * (width - 1))
        cy = int(ny * (height - 1))
        
        # Draw a small "glow" around the point
        radius = 3
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                px, py = cx + dx, cy + dy
                if 0 <= px < width and 0 <= py < height:
                    # Falloff based on distance
                    dist = (dx**2 + dy**2)**0.5
                    if dist <= radius:
                        grid[py][px] += (radius - dist) / radius

    # 2. Render to PPM
    header = f"P3\n{width} {height}\n255\n"
    pixels = []
    
    # Target normalization
    max_val = max([max(row) for row in grid]) if grid else 1.0
    if max_val == 0: max_val = 1.0
    
    for y in range(height):
        row_str = []
        for x in range(width):
            intensity = grid[y][x] / max_val
            # Heat Gradient: Black -> Blue -> Red -> White
            if intensity < 0.2: # Low (Blue)
                r, g, b = 0, 0, int(intensity * 5 * 255)
            elif intensity < 0.7: # Med (Red)
                r, g, b = int((intensity - 0.2) * 2 * 255), 0, 255 - int((intensity - 0.2) * 2 * 255)
            else: # High (White)
                r, g, b = 255, int((intensity - 0.7) * 3 * 255), int((intensity - 0.7) * 3 * 255)
            
            row_str.append(f"{r} {g} {b}")
        pixels.append(" ".join(row_str))
        
    filename = f"heatmap_{int(time.time())}_{random.randint(100,999)}.ppm"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, "w") as f:
        f.write(header)
        f.write("\n".join(pixels))
        f.write("\n")
        
    return os.path.abspath(filepath)

def _hsl_to_rgb(h: int, s: float, l: float):
    # Minimal HSL to RGB conversion
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2
    
    r_p, g_p, b_p = 0, 0, 0
    
    if 0 <= h < 60:
        r_p, g_p, b_p = c, x, 0
    elif 60 <= h < 120:
        r_p, g_p, b_p = x, c, 0
    elif 120 <= h < 180:
        r_p, g_p, b_p = 0, c, x
    elif 180 <= h < 240:
        r_p, g_p, b_p = 0, x, c
    elif 240 <= h < 300:
        r_p, g_p, b_p = x, 0, c
    elif 300 <= h < 360:
        r_p, g_p, b_p = c, 0, x
        
    return (r_p + m, g_p + m, b_p + m)
