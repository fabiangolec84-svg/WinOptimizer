import subprocess
import os

def is_restore_enabled() -> bool:
    """Checks whether System Restore is enabled on the system drive."""
    cmd = 'powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "(Get-ComputerRestorePoint).Count"'
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=10)
        return res.returncode == 0
    except Exception:
        return False

def enable_system_restore() -> tuple[bool, str]:
    """Enables System Restore on C: drive."""
    cmd = 'powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Enable-ComputerRestore -Drive \'C:\\\'"'
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=20)
        if res.returncode == 0:
            return True, "Ochrona systemu została włączona na dysku C:."
        return False, res.stderr.strip() or "Nie udało się włączyć ochrony systemu."
    except Exception as e:
        return False, str(e)

def create_restore_point(description: str = "WinOptimizer Backup") -> tuple[bool, str]:
    """Creates a Windows System Restore Point."""
    # Check if restore frequency limit is reached or enable if needed
    cmd = (
        f'powershell.exe -NoProfile -ExecutionPolicy Bypass -Command '
        f'"Enable-ComputerRestore -Drive \'C:\\\'; '
        f'Checkpoint-Computer -Description \'{description}\' -RestorePointType \'MODIFY_SETTINGS\'"'
    )
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=60)
        if res.returncode == 0:
            return True, "Punkt przywracania systemu został pomyślnie utworzony!"
        else:
            err = res.stderr.strip() or res.stdout.strip()
            # Often Windows limits restore points to 1 every 24h unless SystemRestore registry key is altered
            if "0x80042306" in err or "frequency" in err.lower() or "limit" in err.lower():
                return True, "Punkt przywracania już istnieje (utworzony w ciągu ostatnich 24h)."
            return False, f"Błąd tworzenia punktu: {err}"
    except subprocess.TimeoutExpired:
        return False, "Przekroczono limit czasu podczas tworzenia punktu przywracania."
    except Exception as e:
        return False, f"Błąd: {e}"
