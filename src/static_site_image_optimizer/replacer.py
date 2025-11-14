import os
import re
import logging
from typing import Dict, Iterable

logger = logging.getLogger("ssio.replacer")


def _normalize_extensions(extensions: Iterable[str]) -> set:
    return {e.lower() if e.startswith('.') else f".{e.lower()}" for e in extensions}


def _files_to_process(root: str, include_exts: Iterable[str]):
    include_set = _normalize_extensions(include_exts)
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext in include_set:
                files.append(os.path.join(dirpath, fn))
    return files


def replace_references(
    root: str,
    convert_map: Dict[str, str],
    text_ext_whitelist: Iterable[str] = (".html", ".css", ".js"),
    dry_run: bool = False,
    backup: bool = False,
):
    """Search text files for references to converted images and replace with .webp extensions.

    Args:
        root: Root directory to scan
        convert_map: Mapping of original_path -> webp_path (absolute paths)
        text_ext_whitelist: File extensions to process
        dry_run: If True, only log changes without writing
        backup: If True, create .bak files before modifying
    """
    if not os.path.isdir(root):
        logger.error("Root path does not exist or is not a directory: %s", root)
        return
    
    if not convert_map:
        logger.info("No conversions to update references for")
        return
    
    files = _files_to_process(root, text_ext_whitelist)
    logger.info("Scanning %s files for references", len(files))

    basename_map = {}
    for orig, webp in convert_map.items():
        basename = os.path.basename(orig)
        basename_map[basename] = (orig, webp)

    replace_count = 0
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as fh:
                text = fh.read()
        except (IOError, OSError, UnicodeDecodeError) as e:
            logger.debug("Could not read file %s: %s", file_path, e)
            continue

        new_text = text
        replacements_made = set()
        
        for basename, (orig_abs, webp_abs) in basename_map.items():
            if basename not in new_text:
                continue

            file_dir = os.path.dirname(file_path)
            try:
                rel_to_orig = os.path.relpath(orig_abs, start=file_dir)
            except ValueError:
                rel_to_orig = basename

            rel_to_orig_posix = rel_to_orig.replace(os.path.sep, '/')
            rel_to_webp_posix = os.path.relpath(webp_abs, start=file_dir).replace(os.path.sep, '/')
            webp_basename = os.path.basename(webp_abs)

            if rel_to_orig_posix in new_text and rel_to_orig_posix not in replacements_made:
                new_text = new_text.replace(rel_to_orig_posix, rel_to_webp_posix)
                replacements_made.add(rel_to_orig_posix)
            
            if basename in new_text and basename != webp_basename and basename not in replacements_made:
                new_text = new_text.replace(basename, webp_basename)
                replacements_made.add(basename)

        if new_text != text:
            replace_count += 1
            if dry_run:
                logger.info("[DRY RUN] Would update references in %s", file_path)
            else:
                logger.info("Updated references in %s", file_path)
                if backup:
                    try:
                        with open(file_path + '.bak', 'w', encoding='utf-8') as fh:
                            fh.write(text)
                    except (IOError, OSError) as e:
                        logger.warning("Could not create backup for %s: %s", file_path, e)
                try:
                    with open(file_path, 'w', encoding='utf-8') as fh:
                        fh.write(new_text)
                except (IOError, OSError) as e:
                    logger.error("Could not write to %s: %s", file_path, e)
                    replace_count -= 1

    logger.info("Reference replacement complete, %s files updated", replace_count)
