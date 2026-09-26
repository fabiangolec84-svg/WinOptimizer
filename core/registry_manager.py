import winreg
import os
import json

CONFIG_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "WinOptimizer")
os.makedirs(CONFIG_DIR, exist_ok=True)
BACKUP_FILE = os.path.join(CONFIG_DIR, "registry_backup.json")

HIVES = {
    "HKCU": winreg.HKEY_CURRENT_USER,
    "HKLM": winreg.HKEY_LOCAL_MACHINE,
    "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
    "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
}

def load_backup() -> dict:
    if os.path.exists(BACKUP_FILE):
        try:
            with open(BACKUP_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_backup(data: dict):
    try:
        with open(BACKUP_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving registry backup: {e}")

def get_reg_value(hive_str: str, subkey: str, value_name: str):
    """Reads a registry value. Returns value or None if not found."""
    hive = HIVES.get(hive_str.upper())
    if not hive:
        return None

    try:
        with winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
            val, _ = winreg.QueryValueEx(key, value_name)
            return val
    except FileNotFoundError:
        return None
    except PermissionError:
        return None
    except Exception:
        return None

def set_reg_value(hive_str: str, subkey: str, value_name: str, value_type: int, value) -> tuple[bool, str]:
    """Writes a registry value. Backs up previous value if not already backed up."""
    hive = HIVES.get(hive_str.upper())
    if not hive:
        return False, f"Nieznany hive: {hive_str}"

    backup_key = f"{hive_str}\\{subkey}\\{value_name}"
    backup_data = load_backup()

    # If not backed up before, record current value
    if backup_key not in backup_data:
        curr_val = get_reg_value(hive_str, subkey, value_name)
        backup_data[backup_key] = {
            "hive": hive_str,
            "subkey": subkey,
            "value_name": value_name,
            "value_type": value_type,
            "original_value": curr_val
        }
        save_backup(backup_data)

    try:
        # Create or open key with write access
        with winreg.CreateKeyEx(hive, subkey, 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as key:
            winreg.SetValueEx(key, value_name, 0, value_type, value)
        return True, "Zapisano pomyślnie"
    except PermissionError:
        return False, "Brak uprawnień Administratora do zapisu w rejestrze."
    except Exception as e:
        return False, str(e)

def delete_reg_value(hive_str: str, subkey: str, value_name: str) -> tuple[bool, str]:
    """Deletes a registry value."""
    hive = HIVES.get(hive_str.upper())
    if not hive:
        return False, f"Nieznany hive: {hive_str}"

    try:
        with winreg.OpenKey(hive, subkey, 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as key:
            winreg.DeleteValue(key, value_name)
        return True, "Wartość usunięta"
    except FileNotFoundError:
        return True, "Wartość nie istniała"
    except PermissionError:
        return False, "Brak uprawnień Administratora"
    except Exception as e:
        return False, str(e)

def restore_setting(backup_key: str) -> tuple[bool, str]:
    """Restores a registry value to its original backed-up state."""
    backup_data = load_backup()
    if backup_key not in backup_data:
        return False, "Brak kopii zapasowej dla tego ustawienia."

    info = backup_data[backup_key]
    orig_val = info.get("original_value")
    hive_str = info["hive"]
    subkey = info["subkey"]
    val_name = info["value_name"]
    val_type = info["value_type"]

    if orig_val is None:
        # Original didn't exist -> delete it
        return delete_reg_value(hive_str, subkey, val_name)
    else:
        # Restore original value
        hive = HIVES.get(hive_str.upper())
        try:
            with winreg.CreateKeyEx(hive, subkey, 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY) as key:
                winreg.SetValueEx(key, val_name, 0, val_type, orig_val)
            return True, "Przywrócono domyślną wartość."
        except Exception as e:
            return False, str(e)

def restore_all_settings() -> tuple[int, int]:
    """Restores ALL backed-up registry settings to their initial state. Returns (success_count, total)."""
    backup_data = load_backup()
    succ = 0
    total = len(backup_data)
    for b_key in list(backup_data.keys()):
        ok, _ = restore_setting(b_key)
        if ok:
            succ += 1
    return succ, total
