#!/usr/bin/env python3
"""
Revert script for static-site-image-optimizer
Restores files from .bak backups and optionally removes .webp files
"""
import os
import sys
import argparse
import logging

logger = logging.getLogger("ssio-revert")


def parse_args():
    parser = argparse.ArgumentParser(
        prog="ssio-revert",
        description="Revert changes made by ssio using .bak files",
    )
    parser.add_argument(
        "path",
        help="Path to root directory to revert"
    )
    parser.add_argument(
        "--remove-webp",
        action="store_true",
        help="Remove .webp files after reverting"
    )
    parser.add_argument(
        "--extensions",
        default=".html,.css,.js",
        help="Comma-separated text file extensions to revert (default: .html,.css,.js)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without making them"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)"
    )
    return parser.parse_args()


def find_backup_files(root, extensions):
    backup_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        for fn in filenames:
            if fn.endswith('.bak'):
                original = fn[:-4]
                ext = os.path.splitext(original)[1].lower()
                if ext in extensions:
                    backup_path = os.path.join(dirpath, fn)
                    original_path = os.path.join(dirpath, original)
                    backup_files.append((backup_path, original_path))
    return backup_files


def find_webp_files(root):
    webp_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        for fn in filenames:
            if fn.endswith('.webp'):
                webp_files.append(os.path.join(dirpath, fn))
    return webp_files


def main():
    args = parse_args()
    
    log_level = getattr(logging, args.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format='%(levelname)s: %(message)s'
    )
    
    root = os.path.abspath(args.path)
    
    if not os.path.isdir(root):
        logger.error("Path does not exist or is not a directory: %s", root)
        sys.exit(1)
    
    # Safety check
    root_dirs = ['/', '/home', '/Users', '/System', '/usr', '/bin', '/sbin', '/etc', '/var', '/tmp']
    if root in root_dirs:
        logger.error("Cannot run at filesystem root or system directory: %s", root)
        sys.exit(1)
    
    extensions = set([e.strip().lower() for e in args.extensions.split(",") if e.strip()])
    
    logger.info("Searching for backup files in: %s", root)
    backup_files = find_backup_files(root, extensions)
    
    if not backup_files:
        logger.info("No .bak files found")
    else:
        logger.info("Found %d backup files", len(backup_files))
        
        restored = 0
        for backup_path, original_path in backup_files:
            if args.dry_run:
                logger.info("[DRY RUN] Would restore: %s -> %s", backup_path, original_path)
            else:
                try:
                    with open(backup_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    with open(original_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    os.remove(backup_path)
                    logger.info("Restored: %s", original_path)
                    restored += 1
                except (IOError, OSError) as e:
                    logger.error("Failed to restore %s: %s", original_path, e)
        
        if not args.dry_run:
            logger.info("Restored %d files", restored)
    
    if args.remove_webp:
        logger.info("Searching for .webp files...")
        webp_files = find_webp_files(root)
        
        if not webp_files:
            logger.info("No .webp files found")
        else:
            logger.info("Found %d .webp files", len(webp_files))
            
            removed = 0
            for webp_path in webp_files:
                if args.dry_run:
                    logger.info("[DRY RUN] Would remove: %s", webp_path)
                else:
                    try:
                        os.remove(webp_path)
                        logger.info("Removed: %s", webp_path)
                        removed += 1
                    except (IOError, OSError) as e:
                        logger.error("Failed to remove %s: %s", webp_path, e)
            
            if not args.dry_run:
                logger.info("Removed %d .webp files", removed)
    
    logger.info("Revert complete")


if __name__ == '__main__':
    main()
