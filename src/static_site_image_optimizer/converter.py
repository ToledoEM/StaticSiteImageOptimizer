import os
import logging
from typing import Dict, Iterable, List
from PIL import Image

logger = logging.getLogger("ssio.converter")


def _normalize_extensions(extensions: Iterable[str]) -> set:
    return {e.lower() if e.startswith('.') else f".{e.lower()}" for e in extensions}


def _find_images(root: str, ext_whitelist: Iterable[str]) -> List[str]:
    images = []
    for dirpath, dirnames, filenames in os.walk(root):
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() in ext_whitelist:
                images.append(os.path.join(dirpath, fn))
    return images


def _convert_with_pillow(src: str, dst: str, quality: int) -> bool:
    try:
        with Image.open(src) as im:
            im.save(dst, "WEBP", quality=quality)
        return True
    except (IOError, OSError) as e:
        logger.debug("Pillow conversion failed for %s: %s", src, e)
        return False


def convert_images(
    root: str,
    ext_whitelist: Iterable[str] = (".jpg", ".jpeg", ".png"),
    quality: int = 80,
    dry_run: bool = False,
    delete_original: bool = False,
) -> Dict[str, str]:
    """Find image files (by extensions) and convert them to WebP.

    Returns a mapping original_path -> webp_path for successful conversions.
    """
    if not os.path.isdir(root):
        logger.error("Root path does not exist or is not a directory: %s", root)
        return {}
    
    if not 0 <= quality <= 100:
        logger.error("Quality must be between 0 and 100, got %s", quality)
        return {}
    
    ext_whitelist = _normalize_extensions(ext_whitelist)

    images = _find_images(root, ext_whitelist)
    converted = {}

    if not images:
        logger.info("No images found to convert in %s", root)
        return converted

    logger.info("Found %s images for conversion", len(images))

    for image_path in images:
        rel = os.path.splitext(image_path)[0]
        dst = f"{rel}.webp"

        # skip if output exists and is newer
        if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(image_path):
            logger.debug("Existing webp up to date: %s", dst)
            converted[image_path] = dst
            continue

        if dry_run:
            logger.info("[DRY RUN] Would convert: %s -> %s", image_path, dst)
            converted[image_path] = dst
            continue

        logger.info("Converting: %s -> %s", image_path, dst)
        success = _convert_with_pillow(image_path, dst, quality)

        if success:
            converted[image_path] = dst
            if delete_original:
                try:
                    os.remove(image_path)
                except OSError:
                    logger.warning("Failed to delete original %s", image_path)
        else:
            logger.warning("Conversion failed for %s", image_path)

    logger.info("Conversion complete. %s files converted", len(converted))
    return converted
