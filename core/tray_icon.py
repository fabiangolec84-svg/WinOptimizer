import threading
import os
import sys
from PIL import Image

_tray_icon = None

def get_icon_image():
    """Loads the application icon as PIL Image."""
    if getattr(sys, 'frozen', False):
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    png_path = os.path.join(base_dir, "assets", "icon.png")
    ico_path = os.path.join(base_dir, "assets", "icon.ico")

    if os.path.exists(png_path):
        return Image.open(png_path)
    elif os.path.exists(ico_path):
        return Image.open(ico_path)
    else:
        # Fallback simple image
        return Image.new("RGBA", (64, 64), color="#00d2ff")

def start_tray(on_show_callback, on_clean_ram_callback=None, on_boost_callback=None, on_quit_callback=None):
    """Starts the system tray icon in a background thread."""
    global _tray_icon
    try:
        import pystray
    except ImportError:
        return None

    if _tray_icon is not None:
        return _tray_icon

    def show_action(icon, item):
        on_show_callback()

    def ram_action(icon, item):
        if on_clean_ram_callback:
            on_clean_ram_callback()

    def boost_action(icon, item):
        if on_boost_callback:
            on_boost_callback()

    def quit_action(icon, item):
        icon.stop()
        if on_quit_callback:
            on_quit_callback()
        else:
            sys.exit(0)

    menu = pystray.Menu(
        pystray.MenuItem("🚀 Otwórz WinOptimizer", show_action, default=True),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("💾 Zwolnij RAM", ram_action),
        pystray.MenuItem("⚡ 1-Click Game Boost", boost_action),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("❌ Zamknij", quit_action)
    )

    image = get_icon_image()
    _tray_icon = pystray.Icon("WinOptimizer", image, "WinOptimizer Gaming Booster", menu)

    def run_thread():
        try:
            _tray_icon.run()
        except Exception:
            pass

    t = threading.Thread(target=run_thread, daemon=True)
    t.start()
    return _tray_icon

def stop_tray():
    """Stops the system tray icon."""
    global _tray_icon
    if _tray_icon:
        try:
            _tray_icon.stop()
        except Exception:
            pass
        _tray_icon = None
