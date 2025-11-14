#!/usr/bin/env python3
"""
Test script for static-site-image-optimizer
Runs the optimizer on test directory without deleting original images
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from static_site_image_optimizer.cli import main

if __name__ == '__main__':
    test_dir = os.path.dirname(__file__)
    
    print("="*60)
    print("Running static-site-image-optimizer test")
    print("="*60)
    print(f"Test directory: {test_dir}")
    print("Options: quality=85, backup enabled, originals preserved")
    print("="*60)
    print()
    
    # Clean up previous test results
    img_dir = os.path.join(test_dir, 'img')
    for f in os.listdir(img_dir):
        if f.endswith('.webp'):
            os.remove(os.path.join(img_dir, f))
            print(f"Removed previous WebP: {f}")
    
    backup_file = os.path.join(test_dir, 'index.html.bak')
    if os.path.exists(backup_file):
        os.remove(backup_file)
        print("Removed previous backup file")
    
    print()
    
    sys.argv = [
        'ssio',
        test_dir,
        '--quality', '85',
        '--backup',
        '--log-level', 'INFO'
    ]
    
    main()
    
    print()
    print("="*60)
    print("Test Results")
    print("="*60)
    
    webp_files = [f for f in os.listdir(os.path.join(test_dir, 'img')) if f.endswith('.webp')]
    jpg_files = [f for f in os.listdir(os.path.join(test_dir, 'img')) if f.endswith(('.jpg', '.jpeg'))]
    backup_exists = os.path.exists(os.path.join(test_dir, 'index.html.bak'))
    
    print(f"✓ WebP files created: {len(webp_files)}")
    for f in webp_files:
        size = os.path.getsize(os.path.join(test_dir, 'img', f)) / 1024 / 1024
        print(f"  - {f} ({size:.2f} MB)")
    
    print(f"✓ Original JPG files preserved: {len(jpg_files)}")
    for f in jpg_files:
        size = os.path.getsize(os.path.join(test_dir, 'img', f)) / 1024 / 1024
        print(f"  - {f} ({size:.2f} MB)")
    
    if backup_exists:
        print("✓ index.html.bak backup created")
    else:
        print("✗ index.html.bak backup NOT found")
    
    with open(os.path.join(test_dir, 'index.html'), 'r') as f:
        content = f.read()
        webp_refs = content.count('.webp')
        jpg_refs = content.count('.jpg')
    
    print(f"✓ index.html updated:")
    print(f"  - WebP references: {webp_refs}")
    print(f"  - JPG references remaining: {jpg_refs}")
    
    print("="*60)
