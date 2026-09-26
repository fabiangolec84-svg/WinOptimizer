import os
import time
import datetime
import subprocess
import psutil

FILE_CATEGORIES = {
    "Instalator": [".exe", ".msi", ".bat", ".cmd", ".vbs"],
    "Archiwum": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
    "Obraz dysku": [".iso", ".img", ".vhd", ".vhdx", ".bin", ".cue"],
    "Wideo / Media": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mp3", ".wav", ".flac"],
    "Dokument": [".pdf", ".docx", ".doc", ".xlsx", ".pptx", ".txt", ".csv", ".epub"],
    "Wirtualizacja / Dane": [".vmdk", ".vdi", ".qcow2", ".blob", ".bin", ".pak", ".db", ".sqlite"],
}

SKIP_DIRS = {
    "$recycle.bin", "system volume information", "$windows.~bt", "$windows.~ws",
    "windows.old", "recovery", "appdata\\local\\application data"
}

def format_bytes(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    elif size < 1024 ** 2:
        return f"{size / 1024:.1f} KB"
    elif size < 1024 ** 3:
        return f"{size / (1024 ** 2):.1f} MB"
    else:
        return f"{size / (1024 ** 3):.2f} GB"

def get_category_for_ext(ext: str) -> str:
    ext_lower = ext.lower()
    for cat_name, ext_list in FILE_CATEGORIES.items():
        if ext_lower in ext_list:
            return cat_name
    return "Inne pliki"

def format_age(mtime: float) -> tuple[str, float]:
    """Returns (human_age_str, days_old)."""
    now = time.time()
    diff_seconds = max(0, now - mtime)
    days_old = diff_seconds / 86400.0

    if diff_seconds < 60:
        return "Przed chwilą", days_old
    elif diff_seconds < 3600:
        mins = int(diff_seconds / 60)
        return f"{mins} min. temu", days_old
    elif diff_seconds < 86400:
        hours = int(diff_seconds / 3600)
        return f"{hours} godz. temu", days_old
    elif days_old < 30:
        d = int(days_old)
        return f"{d} dni temu", days_old
    elif days_old < 365:
        m = max(1, int(days_old / 30))
        return f"{m} mies. temu", days_old
    else:
        y = round(days_old / 365, 1)
        return f"{y} lat temu", days_old

def resolve_scan_targets(target_dir: str) -> list[str]:
    user_prof = os.environ.get("USERPROFILE", "C:\\Users\\Default")
    t_upper = str(target_dir).strip().upper()

    if t_upper in ("DOWNLOADS", "DOWNLOAD"):
        p = os.path.join(user_prof, "Downloads")
        return [p] if os.path.exists(p) else [user_prof]
    elif t_upper in ("USER", "USERPROFILE"):
        return [user_prof] if os.path.exists(user_prof) else ["C:\\Users"]
    elif t_upper in ("GAMES", "GAME"):
        game_candidates = [
            r"C:\Program Files (x86)\Steam\steamapps\common",
            r"C:\Program Files\Epic Games",
            r"C:\Riot Games",
            r"D:\SteamLibrary\steamapps\common",
            r"D:\Games",
            r"E:\SteamLibrary\steamapps\common",
            r"E:\Games",
            r"C:\Games"
        ]
        found = [p for p in game_candidates if os.path.exists(p)]
        return found if found else [user_prof]
    elif t_upper in ("ALL", "ALL_DRIVES", "DRIVES"):
        roots = []
        try:
            for part in psutil.disk_partitions(all=False):
                if "cdrom" in part.opts or not part.device:
                    continue
                mount = part.mountpoint
                if os.path.exists(mount):
                    roots.append(mount)
        except Exception:
            roots = ["C:\\"]
        return roots if roots else ["C:\\"]
    else:
        if os.path.exists(target_dir):
            return [target_dir]
        return [user_prof]

def matches_category(cat: str, category_filter: str) -> bool:
    filt = str(category_filter).strip().lower()
    if not filt or filt in ("all", "wszystkie", "all types", "any"):
        return True
    if filt in ("installers", "instalatory", "instalator"):
        return cat in ("Instalator", "Obraz dysku")
    if filt in ("archives", "archiwa", "archiwum"):
        return cat == "Archiwum"
    if filt in ("videos", "wideo", "media", "wideo / media"):
        return cat == "Wideo / Media"
    if filt in ("documents", "dokumenty", "dokument"):
        return cat == "Dokument"
    return cat.lower() == filt

def get_scan_locations() -> list[dict]:
    """Returns list of scan locations including user profile, drives, and special folders."""
    user_prof = os.environ.get("USERPROFILE", "C:\\Users\\Default")
    downloads_dir = os.path.join(user_prof, "Downloads")
    captures_dir = os.path.join(user_prof, "Videos", "Captures")
    videos_dir = os.path.join(user_prof, "Videos")
    docs_dir = os.path.join(user_prof, "Documents")

    locs = [
        {"id": "user_profile", "name": f"Profil Użytkownika ({user_prof})", "path": user_prof},
        {"id": "downloads", "name": "Folder Pobrane (Downloads)", "path": downloads_dir},
        {"id": "videos", "name": "Folder Wideo i Nagrania (Videos)", "path": videos_dir},
        {"id": "docs", "name": "Folder Dokumenty (Documents)", "path": docs_dir},
    ]

    # Add physical drives (C:\, D:\, etc.)
    try:
        for part in psutil.disk_partitions(all=False):
            if "cdrom" in part.opts or not part.device:
                continue
            mount = part.mountpoint
            if os.path.exists(mount):
                locs.append({
                    "id": f"drive_{mount[:1].lower()}",
                    "name": f"Cały Dysk {mount} (Wszystkie foldery)",
                    "path": mount
                })
    except Exception:
        locs.append({"id": "drive_c", "name": "Cały Dysk C:\\", "path": "C:\\"})

    return locs

def scan_all_large_files(target_dir: str,
                         min_size_mb: float = 50.0,
                         min_days_old: float = 0.0,
                         category_filter: str = "Wszystkie",
                         progress_cb=None,
                         stop_event=None) -> list[dict]:
    """
    Scans target directory recursively for files matching the minimum size threshold and age.
    Results are strictly sorted from largest to smallest!
    """
    scan_roots = resolve_scan_targets(target_dir)
    min_bytes = int(min_size_mb * 1024 * 1024)
    results = []
    scanned_folders = 0
    scanned_files = 0

    try:
        for s_root in scan_roots:
            if not os.path.exists(s_root):
                continue
            for root, dirs, files in os.walk(s_root, topdown=True):
                if stop_event and stop_event.is_set():
                    break

                # Filter out inaccessible / junction / system dirs
                root_lower = root.lower()
                dirs[:] = [
                    d for d in dirs
                    if not d.startswith("$")
                    and not d.startswith(".")
                    and d.lower() not in ("system volume information", "windows.old", "recovery", "windows", "appdata", "node_modules", "package cache")
                    and not os.path.islink(os.path.join(root, d))
                ]

                scanned_folders += 1
                if progress_cb and scanned_folders % 25 == 0:
                    progress_cb(scanned_folders, scanned_files, len(results), root)

                for f in files:
                    scanned_files += 1
                    fp = os.path.join(root, f)
                    try:
                        # Skip symlinks
                        if os.path.islink(fp):
                            continue

                        st = os.stat(fp)
                        size = st.st_size

                        # Size Filter (threshold)
                        if size < min_bytes:
                            continue

                        mtime = st.st_mtime
                        age_str, days_old = format_age(mtime)

                        # Age Filter (min_days_old)
                        if days_old < min_days_old:
                            continue

                        ext = os.path.splitext(f)[1]
                        cat = get_category_for_ext(ext)

                        # Category Filter
                        if not matches_category(cat, category_filter):
                            continue

                        mod_date = datetime.datetime.fromtimestamp(mtime).strftime("%d.%m.%Y %H:%M")

                        results.append({
                            "name": f,
                            "path": fp,
                            "dir": root,
                            "size": size,
                            "size_str": format_bytes(size),
                            "category": cat,
                            "age_str": age_str,
                            "mod_date": mod_date,
                            "days_old": days_old,
                            "accessed_days_ago": max(0, int(days_old))
                        })
                    except (PermissionError, OSError):
                        continue
    except Exception as e:
        print(f"Error during scan: {e}")

    # SORT STRICTLY FROM LARGEST TO SMALLEST
    results.sort(key=lambda x: x["size"], reverse=True)
    return results

def open_in_explorer(file_path: str):
    """Opens Windows Explorer and highlights the specified file."""
    if not os.path.exists(file_path):
        return False
    try:
        norm_path = os.path.normpath(file_path)
        subprocess.Popen(f'explorer.exe /select,"{norm_path}"', shell=True)
        return True
    except Exception as e:
        print(f"Error opening explorer: {e}")
        return False

def delete_files(file_paths: list[str]) -> tuple[int, int]:
    """Safely deletes specified files. Returns (freed_bytes, count)."""
    freed = 0
    count = 0

    for path in file_paths:
        try:
            if os.path.exists(path) and os.path.isfile(path):
                size = os.path.getsize(path)
                os.remove(path)
                freed += size
                count += 1
        except Exception:
            continue

    return freed, count
