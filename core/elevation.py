import sys
import os
import ctypes

def is_admin() -> bool:
    """Check if the current script is running with administrative privileges."""
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False

def elevate():
    """Relaunches the current script or executable with admin privileges (UAC prompt)."""
    if is_admin():
        return True

    try:
        if getattr(sys, 'frozen', False):
            # Running as compiled .exe
            executable = sys.executable
            params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
            ret = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", executable, params, None, 1
            )
        else:
            # Running as Python script
            executable = sys.executable
            script = os.path.abspath(sys.argv[0])
            params = f'"{script}" ' + " ".join([f'"{arg}"' for arg in sys.argv[1:]])
            ret = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", executable, params, None, 1
            )

        if ret > 32:
            # Successfully requested elevation, terminate non-elevated instance
            sys.exit(0)
        else:
            return False
    except Exception as e:
        print(f"Błąd podnoszenia uprawnień: {e}")
        return False
