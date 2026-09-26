import winreg
import os
import subprocess
import datetime

UNINSTALL_KEYS = [
    ("HKLM (64-bit)", winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    ("HKLM (32-bit)", winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
    ("HKCU", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
]

def format_size(size_mb: float) -> str:
    if size_mb >= 1024:
        return f"{size_mb / 1024:.2f} GB"
    elif size_mb > 0:
        return f"{size_mb:.1f} MB"
    else:
        return "Nieznany"

def parse_install_date(date_str: str, location: str = "") -> tuple[str, int]:
    """
    Parses date string (YYYYMMDD or similar) or falls back to folder mtime.
    Returns (display_str, days_ago).
    """
    now = datetime.datetime.now()

    if date_str and len(str(date_str)) == 8 and str(date_str).isdigit():
        try:
            d = datetime.datetime.strptime(str(date_str), "%Y%m%d")
            delta_days = (now - d).days
            if delta_days < 0:
                delta_days = 0
            return _format_days_ago(d.strftime("%d.%m.%Y"), delta_days), delta_days
        except Exception:
            pass

    # Fallback to folder mtime if install location exists
    if location and os.path.exists(location):
        try:
            mtime = os.path.getmtime(location)
            d = datetime.datetime.fromtimestamp(mtime)
            delta_days = (now - d).days
            if delta_days < 0:
                delta_days = 0
            return _format_days_ago(d.strftime("%d.%m.%Y"), delta_days), delta_days
        except Exception:
            pass

    return "Nieznana data", 99999

def _format_days_ago(date_formatted: str, days: int) -> str:
    if days == 0:
        return f"{date_formatted} (Dzisiaj)"
    elif days == 1:
        return f"{date_formatted} (Wczoraj)"
    elif days < 30:
        return f"{date_formatted} ({days} dni temu)"
    elif days < 365:
        months = max(1, round(days / 30))
        return f"{date_formatted} ({months} mies. temu)"
    else:
        years = round(days / 365, 1)
        return f"{date_formatted} ({years} lat temu)"

def get_installed_applications() -> list[dict]:
    """Retrieves all desktop applications installed on the system."""
    apps = []
    seen_names = set()

    for hive_label, hive, subkey in UNINSTALL_KEYS:
        try:
            with winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as root_key:
                num_subkeys, _, _ = winreg.QueryInfoKey(root_key)
                for i in range(num_subkeys):
                    try:
                        subkey_name = winreg.EnumKey(root_key, i)
                        with winreg.OpenKey(root_key, subkey_name, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as app_key:
                            def get_val(val_name):
                                try:
                                    v, _ = winreg.QueryValueEx(app_key, val_name)
                                    return v
                                except Exception:
                                    return None

                            display_name = get_val("DisplayName")
                            if not display_name:
                                continue

                            # Skip Windows system updates / hotfixes
                            if get_val("SystemComponent") == 1 or get_val("ParentKeyName"):
                                continue

                            name = str(display_name).strip()
                            clean_id = name.lower()
                            if clean_id in seen_names:
                                continue
                            seen_names.add(clean_id)

                            publisher = str(get_val("Publisher") or "Nieznany wydawca").strip()
                            version = str(get_val("DisplayVersion") or "").strip()
                            uninstall_str = str(get_val("UninstallString") or "").strip()
                            quiet_str = str(get_val("QuietUninstallString") or "").strip()
                            install_loc = str(get_val("InstallLocation") or "").strip()
                            raw_date = get_val("InstallDate")

                            # Calculate size (EstimatedSize is in KB)
                            size_kb = get_val("EstimatedSize")
                            size_mb = 0.0
                            if size_kb and str(size_kb).isdigit():
                                size_mb = round(int(size_kb) / 1024, 1)
                            elif install_loc and os.path.exists(install_loc) and len(install_loc) > 4:
                                # Quick folder size estimation (limit scan count for instant speed)
                                try:
                                    total_b = 0
                                    file_count = 0
                                    for root, _, files in os.walk(install_loc):
                                        for f in files:
                                            try:
                                                total_b += os.path.getsize(os.path.join(root, f))
                                                file_count += 1
                                                if file_count > 1000:
                                                    break
                                            except Exception:
                                                pass
                                        if file_count > 1000:
                                            break
                                    size_mb = round(total_b / (1024 * 1024), 1)
                                except Exception:
                                    pass

                            date_display, days_ago = parse_install_date(raw_date, install_loc)

                            apps.append({
                                "name": name,
                                "publisher": publisher,
                                "version": version,
                                "size_mb": size_mb,
                                "size_str": format_size(size_mb),
                                "install_date": date_display,
                                "days_ago": days_ago,
                                "uninstall_cmd": quiet_str or uninstall_str,
                                "location": install_loc,
                                "hive": hive_label
                            })
                    except OSError:
                        continue
        except Exception:
            pass

    # Sort default by size descending
    apps.sort(key=lambda x: x["size_mb"], reverse=True)
    return apps

def uninstall_application(cmd: str) -> tuple[bool, str]:
    """Runs the uninstaller command for an application."""
    if not cmd:
        return False, "Brak zdefiniowanego polecenia deinstalacji w rejestrze."

    try:
        # If it's an MsiExec command, handle arguments
        if "msiexec" in cmd.lower():
            subprocess.Popen(cmd, shell=True)
            return True, "Uruchomiono deinstalator Windows Installer (MSI)."
        else:
            subprocess.Popen(cmd, shell=True)
            return True, "Uruchomiono deinstalator aplikacji."
    except Exception as e:
        return False, f"Błąd uruchamiania deinstalatora: {e}"
