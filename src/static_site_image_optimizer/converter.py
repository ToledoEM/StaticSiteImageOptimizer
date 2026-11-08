import io
import logging
import os
from collections.abc import Iterable

from PIL import Image, ImageCms

logger = logging.getLogger("ssio.converter")


def _normalize_extensions(extensions: Iterable[str]) -> set:
    return {e.lower() if e.startswith(".") else f".{e.lower()}" for e in extensions}


def _find_images(root: str, ext_whitelist: Iterable[str]) -> list[str]:
    images = []
    for dirpath, dirnames, filenames in os.walk(root):
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() in ext_whitelist:
                images.append(os.path.join(dirpath, fn))
    return images


_SRGB = ImageCms.createProfile("sRGB")
_SRGB_ICC = ImageCms.ImageCmsProfile(_SRGB).tobytes()


def _to_srgb(im: Image.Image) -> Image.Image:
    """Return an RGB/RGBA image whose pixels are in sRGB.

    Wide-gamut (Adobe RGB, ProPhoto, Display P3) and CMYK images are
    colour-converted using their embedded ICC profile. Dropping the profile
    instead makes browsers read the values as sRGB, which desaturates them.
    """
    has_alpha = im.mode in ("RGBA", "LA", "PA") or (
        im.mode == "P" and "transparency" in im.info
    )
    target = "RGBA" if has_alpha else "RGB"

    # 16-bit and 32-bit greyscale: scale to 8-bit first, a plain convert clips to white.
    if im.mode.startswith("I;16") or im.mode == "I":
        im = im.convert("I").point(lambda v: v * (1 / 256)).convert("L")
    elif im.mode == "F":
        im = im.point(lambda v: v * 255).convert("L")

    icc = im.info.get("icc_profile")
    if icc:
        try:
            src_profile = ImageCms.ImageCmsProfile(io.BytesIO(icc))
            if im.mode not in ("RGB", "RGBA", "CMYK", "L"):
                im = im.convert(target)
            out_mode = "RGBA" if im.mode == "RGBA" else "RGB"
            return ImageCms.profileToProfile(
                im,
                src_profile,
                _SRGB,
                renderingIntent=ImageCms.Intent.PERCEPTUAL,
                outputMode=out_mode,
            )
        except (ImageCms.PyCMSError, OSError, ValueError) as e:
            logger.warning("Could not apply ICC profile, assuming sRGB: %s", e)

    return im if im.mode == target else im.convert(target)


def _convert_with_pillow(src: str, dst: str, quality: int) -> bool:
    try:
        with Image.open(src) as im:
            exif = im.info.get("exif")
            out = _to_srgb(im)
            extra = {"icc_profile": _SRGB_ICC}
            if exif:
                extra["exif"] = exif
            out.save(dst, "WEBP", quality=quality, **extra)
        return True
    except OSError as e:
        logger.debug("Pillow conversion failed for %s: %s", src, e)
        return False


def convert_images(
    root: str,
    ext_whitelist: Iterable[str] = (".jpg", ".jpeg", ".png"),
    quality: int = 80,
    dry_run: bool = False,
    delete_original: bool = False,
) -> dict[str, str]:
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
        if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(
            image_path
        ):
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
