import argparse
import os
import logging
import sys

from .converter import convert_images
from .replacer import replace_references

logger = logging.getLogger("ssio")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="ssio",
        description="Recursively convert site images to WebP and replace references in HTML/CSS/JS",
    )
    parser.add_argument(
        "path", 
        help="Path to root directory to process"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Preview changes without making them"
    )
    parser.add_argument(
        "--quality", 
        type=int, 
        default=80, 
        help="WebP quality 0-100 (default: 80)"
    )
    parser.add_argument(
        "--delete-original", 
        action="store_true", 
        help="Delete original images after conversion"
    )
    parser.add_argument(
        "--backup", 
        action="store_true", 
        help="Create .bak files before modifying text files"
    )
    parser.add_argument(
        "--extensions", 
        default=".jpg,.jpeg,.png,.gif,.bmp,.tiff", 
        help="Comma-separated image extensions (default: jpg,jpeg,png,gif,bmp,tiff)"
    )
    parser.add_argument(
        "--include", 
        default=".html,.css,.js", 
        help="Comma-separated text file extensions to update (default: html,css,js)"
    )
    parser.add_argument(
        "--log-level", 
        default="INFO", 
        choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
        help="Logging level (default: INFO)"
    )

    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    log_level = getattr(logging, args.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format='%(levelname)s: %(message)s'
    )

    root = os.path.abspath(args.path)
    
    if not os.path.isdir(root):
        logger.error("Path does not exist or is not a directory: %s", root)
        sys.exit(1)
    
    # Safety check: prevent running at filesystem root
    root_dirs = ['/', '/home', '/Users', '/System', '/usr', '/bin', '/sbin', '/etc', '/var', '/tmp']
    if root in root_dirs:
        logger.error("Cannot run at filesystem root or system directory: %s", root)
        sys.exit(1)
    
    if not 0 <= args.quality <= 100:
        logger.error("Quality must be between 0 and 100, got %s", args.quality)
        sys.exit(1)

    logger.info("Processing directory: %s", root)
    if args.dry_run:
        logger.info("DRY RUN MODE - No changes will be made")

    image_exts = [e.strip() for e in args.extensions.split(",") if e.strip()]
    text_exts = [e.strip() for e in args.include.split(",") if e.strip()]
    
    if not image_exts:
        logger.error("No image extensions specified")
        sys.exit(1)
    
    if not text_exts:
        logger.error("No text file extensions specified")
        sys.exit(1)

    convert_map = convert_images(
        root,
        ext_whitelist=image_exts,
        quality=args.quality,
        dry_run=args.dry_run,
        delete_original=args.delete_original,
    )

    if not convert_map:
        logger.info("No images were converted")
        return

    replace_references(
        root,
        convert_map,
        text_ext_whitelist=text_exts,
        dry_run=args.dry_run,
        backup=args.backup,
    )
    
    logger.info("Processing complete")


if __name__ == "__main__":
    main()
