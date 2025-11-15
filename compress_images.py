#!/usr/bin/env python3
"""
Image optimization script - Compress JPG and convert to WebP
"""
import os
from PIL import Image
import glob

# Target directory
img_dir = os.path.join(os.path.dirname(__file__), 'assets', 'images')
os.chdir(img_dir)

print(f"📁 Working directory: {img_dir}\n")

# Process all JPG files
jpg_files = glob.glob('*.jpg') + glob.glob('*.JPG')
print(f"Found {len(jpg_files)} JPG files\n")

for jpg_file in jpg_files:
    try:
        # Open image
        img = Image.open(jpg_file)
        
        # Get original size
        orig_size = os.path.getsize(jpg_file) / 1024  # KB
        
        # Compress and save JPG (quality 85)
        img_rgb = img.convert('RGB')
        img_rgb.save(jpg_file, 'JPEG', quality=85, optimize=True)
        
        new_size = os.path.getsize(jpg_file) / 1024  # KB
        reduction = ((orig_size - new_size) / orig_size) * 100
        
        # Convert to WebP
        webp_file = jpg_file.rsplit('.', 1)[0] + '.webp'
        img_rgb.save(webp_file, 'WEBP', quality=85)
        webp_size = os.path.getsize(webp_file) / 1024  # KB
        
        print(f"✅ {jpg_file}")
        print(f"   JPG: {orig_size:.1f}KB → {new_size:.1f}KB ({reduction:.0f}% reduction)")
        print(f"   WebP: {webp_size:.1f}KB")
        print()
        
    except Exception as e:
        print(f"❌ {jpg_file}: {e}\n")

print("✨ Image optimization complete!")
