import winreg
import os
import glob

RUN_REGISTRY_TARGETS = [
    ("HKCU", winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
    ("HKLM", winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
    ("HKLM (32-bit)", winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"),
]

KNOWN_HIGH_IMPACT = [
    "discord", "spotify", "steam", "epicgames", "riot", "origin", "battlenet",
    "onedrive", "teams", "skype", "cortana", "telegram", "viber", "overwolf",
    "razer", "synapse", "logitech", "ghub", "icue", "corsair"
]

KNOWN_ESSENTIAL = [
    "realtek", "nvidia", "amd", "intel", "securityhealth", "windowsdefender", "antivirus"
]

def _get_user_startup_dir() -> str:
    appdata = os.environ.get("APPDATA", "")
    return os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs", "Startup")

def _get_common_startup_dir() -> str:
    progdata = os.environ.get("ProgramData", "C:\\ProgramData")
    return os.path.join(progdata, "Microsoft", "Windows", "Start Menu", "Programs", "Startup")

def estimate_impact(name: str, cmd: str) -> tuple[str, str]:
    """Returns (impact_label, recommendation)."""
    text = (name + " " + cmd).lower()
    for ess in KNOWN_ESSENTIAL:
        if ess in text:
            return "Niski", "Zalecane: Włączony (Sterownik/System)"
    for high in KNOWN_HIGH_IMPACT:
        if high in text:
            return "Wysoki", "Zalecane: Wyłączony (Zwalnia RAM i start)"
    return "Średni", "Opcjonalny"

def get_startup_apps() -> list[dict]:
    """Retrieves all enabled AND disabled startup items from Registry and Startup Folders."""
    apps = []
    seen = set()

    # 1. Registry Run Keys (Enabled & Disabled)
    for hive_label, hive, subkey in RUN_REGISTRY_TARGETS:
        # A) Enabled
        try:
            with winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
                idx = 0
                while True:
                    try:
                        name, val, _ = winreg.EnumValue(key, idx)
                        key_id = f"reg:{hive_label}:{name}".lower()
                        if key_id not in seen:
                            seen.add(key_id)
                            impact, rec = estimate_impact(name, str(val))
                            apps.append({
                                "id": key_id,
                                "name": name,
                                "command": str(val),
                                "source": f"Rejestr ({hive_label})",
                                "type": "registry",
                                "hive": "HKCU" if "HKCU" in hive_label else "HKLM",
                                "subkey": subkey,
                                "enabled": True,
                                "impact": impact,
                                "recommendation": rec
                            })
                        idx += 1
                    except OSError:
                        break
        except Exception:
            pass

        # B) Disabled in subkey Run\Disabled
        dis_subkey = subkey + r"\Disabled"
        try:
            with winreg.OpenKey(hive, dis_subkey, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
                idx = 0
                while True:
                    try:
                        name, val, _ = winreg.EnumValue(key, idx)
                        key_id = f"reg:{hive_label}:{name}".lower()
                        if key_id not in seen:
                            seen.add(key_id)
                            impact, rec = estimate_impact(name, str(val))
                            apps.append({
                                "id": key_id,
                                "name": name,
                                "command": str(val),
                                "source": f"Rejestr ({hive_label})",
                                "type": "registry",
                                "hive": "HKCU" if "HKCU" in hive_label else "HKLM",
                                "subkey": subkey,
                                "enabled": False,
                                "impact": impact,
                                "recommendation": rec
                            })
                        idx += 1
                    except OSError:
                        break
        except Exception:
            pass

    # 2. Startup Folders (User & Common)
    folder_targets = [
        ("Folder Użytkownika", _get_user_startup_dir()),
        ("Folder Wspólny (System)", _get_common_startup_dir())
    ]

    for label, folder in folder_targets:
        if not os.path.exists(folder):
            continue

        try:
            for item in os.listdir(folder):
                full_path = os.path.join(folder, item)
                if not os.path.isfile(full_path):
                    continue

                if item.lower().endswith(".lnk") or item.lower().endswith(".url"):
                    name = os.path.splitext(item)[0]
                    key_id = f"folder:{folder}:{name}".lower()
                    if key_id not in seen:
                        seen.add(key_id)
                        impact, rec = estimate_impact(name, full_path)
                        apps.append({
                            "id": key_id,
                            "name": name,
                            "command": full_path,
                            "source": label,
                            "type": "folder",
                            "folder": folder,
                            "filename": item,
                            "enabled": True,
                            "impact": impact,
                            "recommendation": rec
                        })
                elif item.lower().endswith(".lnk.disabled") or item.lower().endswith(".url.disabled"):
                    raw_name = item[:-9]  # remove .disabled
                    name = os.path.splitext(raw_name)[0]
                    key_id = f"folder:{folder}:{name}".lower()
                    if key_id not in seen:
                        seen.add(key_id)
                        impact, rec = estimate_impact(name, full_path)
                        apps.append({
                            "id": key_id,
                            "name": name,
                            "command": full_path,
                            "source": label,
                            "type": "folder",
                            "folder": folder,
                            "filename": item,
                            "enabled": False,
                            "impact": impact,
                            "recommendation": rec
                        })
        except Exception:
            pass

    return apps

def toggle_startup_app(app: dict, enable: bool) -> tuple[bool, str]:
    """Enables or disables a startup app entry (Registry or Folder)."""
    app_type = app.get("type", "registry")
    name = app["name"]

    if app_type == "registry":
        hive = winreg.HKEY_CURRENT_USER if app["hive"] == "HKCU" else winreg.HKEY_LOCAL_MACHINE
        subkey = app["subkey"]
        val = app["command"]
        dis_subkey = subkey + r"\Disabled"

        try:
            if not enable:
                # 1. Delete from main Run key
                try:
                    with winreg.OpenKey(hive, subkey, 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as key:
                        winreg.DeleteValue(key, name)
                except FileNotFoundError:
                    pass

                # 2. Store in Run\Disabled
                with winreg.CreateKeyEx(hive, dis_subkey, 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as key:
                    winreg.SetValueEx(key, name, 0, winreg.REG_SZ, val)

                return True, f"Wyłączono autostart dla: {name}"
            else:
                # 1. Store in main Run key
                with winreg.CreateKeyEx(hive, subkey, 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as key:
                    winreg.SetValueEx(key, name, 0, winreg.REG_SZ, val)

                # 2. Delete from Run\Disabled
                try:
                    with winreg.OpenKey(hive, dis_subkey, 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as key:
                        winreg.DeleteValue(key, name)
                except (FileNotFoundError, OSError):
                    pass

                return True, f"Włączono autostart dla: {name}"
        except PermissionError:
            return False, f"Brak uprawnień administratora do modyfikacji: {name}"
        except Exception as e:
            return False, f"Błąd: {e}"

    elif app_type == "folder":
        folder = app["folder"]
        curr_filename = app["filename"]
        curr_path = os.path.join(folder, curr_filename)

        try:
            if not enable:
                if not curr_filename.endswith(".disabled"):
                    new_path = curr_path + ".disabled"
                    if os.path.exists(curr_path):
                        os.replace(curr_path, new_path)
                    return True, f"Wyłączono skrót autostartu: {name}"
                return True, "Już wyłączony"
            else:
                if curr_filename.endswith(".disabled"):
                    new_path = curr_path[:-9]  # strip .disabled
                    if os.path.exists(curr_path):
                        os.replace(curr_path, new_path)
                    return True, f"Włączono skrót autostartu: {name}"
                return True, "Już włączony"
        except Exception as e:
            return False, f"Błąd zmiany pliku skrótu: {e}"

    return False, "Nieznany typ aplikacji"

def toggle_all_startup_apps(enable: bool) -> tuple[int, int]:
    """Toggles all non-essential startup apps to enabled or disabled."""
    apps = get_startup_apps()
    success_count = 0
    total = 0

    for app in apps:
        if not enable and "Zalecane: Włączony" in app["recommendation"]:
            # Protect essential system drivers when mass disabling
            continue

        if app["enabled"] != enable:
            total += 1
            ok, _ = toggle_startup_app(app, enable)
            if ok:
                success_count += 1

    return success_count, total
