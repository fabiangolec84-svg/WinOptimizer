import sys
import os

# Ensure project root is in python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import webview
from core.elevation import is_admin, elevate
from core.api_bridge import ApiBridge
from core.auto_boost import auto_boost_daemon

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(CURRENT_DIR, relative_path)

def main():
    # If running with --elevate argument or explicitly requested, attempt elevation
    if "--elevate" in sys.argv and not is_admin():
        elevate()
        return

    # Start background auto-boost daemon
    auto_boost_daemon.start()

    bridge = ApiBridge()
    html_path = get_resource_path(os.path.join("web", "index.html"))

    # Frameless window matching modern cyber/glass design 1:1 with reference
    window = webview.create_window(
        title="WinOptimizer 2.0 Pro",
        url=html_path,
        js_api=bridge,
        width=1280,
        height=820,
        min_size=(1100, 720),
        frameless=True,
        easy_drag=True,
        background_color='#070a13'
    )
    bridge.set_window(window)
    webview.start(debug=False)

if __name__ == "__main__":
    main()
