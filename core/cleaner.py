import os
import shutil
import ctypes
import glob
import psutil

BROWSER_PROCESSES = {
    "chrome.exe": "Google Chrome",
    "msedge.exe": "Microsoft Edge",
    "brave.exe": "Brave Browser",
    "firefox.exe": "Mozilla Firefox",
    "opera.exe": "Opera"
}

def get_running_browsers() -> list[str]:
    """Returns list of user-friendly names of currently running web browsers."""
    running = set()
    for proc in psutil.process_iter(['name']):
        try:
            pname = proc.info['name'].lower()
            for b_exe, b_name in BROWSER_PROCESSES.items():
                if pname == b_exe.lower():
                    running.add(b_name)
        except Exception:
            continue
    return sorted(list(running))

def close_browsers() -> int:
    """Closes all running browser processes to free cache file locks. Returns closed count."""
    closed = 0
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            pname = proc.info['name'].lower()
            if pname in BROWSER_PROCESSES:
                proc.kill()
                closed += 1
        except Exception:
            continue
    return closed

def get_folder_size(path: str) -> tuple[int, int]:
    """Returns (total_bytes, file_count) in a folder."""
    total_size = 0
    total_files = 0
    if not os.path.exists(path):
        return 0, 0

    try:
        for root, dirs, files in os.walk(path, topdown=True, onerror=None):
            for f in files:
                try:
                    fp = os.path.join(root, f)
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)
                        total_files += 1
                except Exception:
                    continue
    except Exception:
        pass
    return total_size, total_files

def format_bytes(size: int) -> str:
    """Formats bytes to KB, MB or GB."""
    if size < 1024:
        return f"{size} B"
    elif size < 1024 ** 2:
        return f"{size / 1024:.1f} KB"
    elif size < 1024 ** 3:
        return f"{size / (1024 ** 2):.1f} MB"
    else:
        return f"{size / (1024 ** 3):.2f} GB"

def get_cleaner_targets() -> dict:
    """Returns dictionary of cleanup targets with display names, paths and default states."""
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    app_data = os.environ.get("APPDATA", "")
    user_temp = os.environ.get("TEMP", "")
    win_dir = os.environ.get("SystemRoot", "C:\\Windows")
    prog_data = os.environ.get("ProgramData", "C:\\ProgramData")

    targets = {
        "user_temp": {
            "name": "Pliki tymczasowe użytkownika (%TEMP%)",
            "desc": "Tymczasowe pliki programów, instalatorów i rozpakowywanych archiwów",
            "paths": [user_temp],
            "default": True,
            "recommended": True
        },
        "win_temp": {
            "name": "Tymczasowe pliki systemowe Windows",
            "desc": "Pozostałości po aktualizacjach i instalatorach w C:\\Windows\\Temp",
            "paths": [os.path.join(win_dir, "Temp")],
            "default": True,
            "recommended": True
        },
        "win_update": {
            "name": "Pamięć podręczna Windows Update",
            "desc": "Stare pobrane pakiety aktualizacji Windows (SoftwareDistribution\\Download)",
            "paths": [os.path.join(win_dir, "SoftwareDistribution", "Download")],
            "default": True,
            "recommended": True
        },
        "delivery_opt": {
            "name": "Optymalizacja dostarczania (Delivery Optimization)",
            "desc": "P2P cache aktualizacji Windows zajmujący gigabajty przestrzeni",
            "paths": [os.path.join(win_dir, "SoftwareDistribution", "DeliveryOptimization")],
            "default": True,
            "recommended": True
        },
        "shader_cache": {
            "name": "DirectX & GPU Shader Cache (NVIDIA / AMD / Intel)",
            "desc": "Pamięć podręczna shaderów DirectX/GPU (częsta przyczyna mikro-przycięć w grach)",
            "paths": [
                os.path.join(local_app_data, "D3DSCache"),
                os.path.join(local_app_data, "NVIDIA", "DXCache"),
                os.path.join(local_app_data, "NVIDIA", "GLCache"),
                os.path.join(local_app_data, "AMD", "DxCache"),
            ],
            "default": True,
            "recommended": True
        },
        "discord_cache": {
            "name": "Pamięć podręczna Discorda (Cache & Code Cache)",
            "desc": "Tymczasowe miniaturki zdjęć, filmów i cache czatu z serwerów Discord",
            "paths": [
                os.path.join(app_data, "discord", "Cache"),
                os.path.join(app_data, "discord", "Code Cache"),
                os.path.join(app_data, "discord", "GPUCache"),
            ],
            "default": True,
            "recommended": True
        },
        "spotify_cache": {
            "name": "Pamięć podręczna Spotify (Storage Cache)",
            "desc": "Pobrane utwory i buforowane okładki albumów Spotify",
            "paths": [
                os.path.join(local_app_data, "Spotify", "Storage"),
                os.path.join(local_app_data, "Spotify", "Data"),
            ],
            "default": True,
            "recommended": True
        },
        "steam_cache": {
            "name": "Pamięć podręczna przeglądarki Steam",
            "desc": "Tymczasowe pliki przeglądarki sklepu i społeczności Steam (htmlcache)",
            "paths": [
                os.path.join(local_app_data, "Steam", "htmlcache"),
            ],
            "default": True,
            "recommended": True
        },
        "crash_dumps": {
            "name": "Dzienniki awarii i raporty błędów (Crash Dumps / WER)",
            "desc": "Raporty błędów aplikacji i zrzuty pamięci po awariach",
            "paths": [
                os.path.join(local_app_data, "CrashDumps"),
                os.path.join(win_dir, "Minidump"),
                os.path.join(prog_data, "Microsoft", "Windows", "WER", "ReportArchive"),
                os.path.join(prog_data, "Microsoft", "Windows", "WER", "ReportQueue")
            ],
            "default": True,
            "recommended": True
        },
        "browser_cache": {
            "name": "Pamięć podręczna przeglądarek (Chrome, Edge, Brave, Opera)",
            "desc": "Tymczasowy cache stron WWW (nie usuwa haseł ani historii logowania)",
            "paths": [
                os.path.join(local_app_data, "Google", "Chrome", "User Data", "Default", "Cache"),
                os.path.join(local_app_data, "Microsoft", "Edge", "User Data", "Default", "Cache"),
                os.path.join(local_app_data, "BraveSoftware", "Brave-Browser", "User Data", "Default", "Cache"),
                os.path.join(app_data, "Opera Software", "Opera Stable", "Cache"),
            ],
            "default": False,
            "recommended": False
        },
        "recycle_bin": {
            "name": "Kosz systemowy (Wszystkie dyski)",
            "desc": "Trwale opróżnia kosz systemowy wszystkich partycji",
            "paths": [],
            "special": "recycle_bin",
            "default": True,
            "recommended": True
        }
    }
    return targets

def scan_targets(selected_keys: list[str] = None) -> dict:
    """Scans targets and returns dictionary with sizes and file counts."""
    targets = get_cleaner_targets()
    results = {}
    total_size = 0
    total_files = 0

    for key, info in targets.items():
        if selected_keys is not None and key not in selected_keys:
            continue

        if info.get("special") == "recycle_bin":
            class SHQUERYRBINFO(ctypes.Structure):
                _fields_ = [
                    ("cbSize", ctypes.c_ulong),
                    ("i64Size", ctypes.c_int64),
                    ("i64NumItems", ctypes.c_int64),
                ]
            try:
                rb_info = SHQUERYRBINFO()
                rb_info.cbSize = ctypes.sizeof(SHQUERYRBINFO)
                res = ctypes.windll.shell32.SHQueryRecycleBinW(None, ctypes.byref(rb_info))
                if res == 0:
                    size = rb_info.i64Size
                    files = rb_info.i64NumItems
                else:
                    size, files = 0, 0
            except Exception:
                size, files = 0, 0
            results[key] = {"size": size, "files": files, "size_str": format_bytes(size), "name": info["name"]}
            total_size += size
            total_files += files
            continue

        cat_size = 0
        cat_files = 0
        for p in info["paths"]:
            if os.path.exists(p):
                s, f = get_folder_size(p)
                cat_size += s
                cat_files += f
        results[key] = {"size": cat_size, "files": cat_files, "size_str": format_bytes(cat_size), "name": info["name"]}
        total_size += cat_size
        total_files += cat_files

    return {
        "categories": results,
        "total_size": total_size,
        "total_size_str": format_bytes(total_size),
        "total_files": total_files
    }

def clean_targets(selected_keys: list[str], progress_callback=None, log_callback=None) -> tuple[int, int]:
    """
    Cleans selected targets safely.
    progress_callback(percent: float, current_status: str)
    log_callback(msg: str)
    Returns: (freed_bytes, deleted_files_count)
    """
    targets = get_cleaner_targets()
    total_freed = 0
    total_deleted = 0

    num_keys = len(selected_keys)
    if num_keys == 0:
        return 0, 0

    for idx, key in enumerate(selected_keys):
        if key not in targets:
            continue

        info = targets[key]
        if log_callback:
            log_callback(f"Czyszczenie: {info['name']}...")

        if info.get("special") == "recycle_bin":
            try:
                ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
                if log_callback:
                    log_callback("✓ Opróżniono kosz systemowy.")
            except Exception as e:
                if log_callback:
                    log_callback(f"! Błąd opróżniania kosza: {e}")
            continue

        for path in info["paths"]:
            if not os.path.exists(path):
                continue

            try:
                for root, dirs, files in os.walk(path, topdown=False):
                    for f in files:
                        fp = os.path.join(root, f)
                        try:
                            size = os.path.getsize(fp) if not os.path.islink(fp) else 0
                            os.remove(fp)
                            total_freed += size
                            total_deleted += 1
                        except (PermissionError, OSError):
                            continue

                    for d in dirs:
                        dp = os.path.join(root, d)
                        try:
                            os.rmdir(dp)
                        except (PermissionError, OSError):
                            continue
            except Exception as e:
                if log_callback:
                    log_callback(f"! Pominięto folder {path}: {e}")

        pct = (idx + 1) / num_keys
        if progress_callback:
            progress_callback(pct, f"Ukończono: {info['name']}")

    if log_callback:
        log_callback(f"✓ Zakończono czyszczenie! Zwolniono: {format_bytes(total_freed)} ({total_deleted} plików).")

    return total_freed, total_deleted
