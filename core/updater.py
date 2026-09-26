import urllib.request
import json
import ssl

CURRENT_VERSION = "2.0 Pro"
CURRENT_VERSION_NUM = "2.0.0"
GITHUB_REPO = "fabiangolec84-svg/WinOptimizer"

def check_for_updates() -> dict:
    """
    Checks GitHub Releases for new updates.
    Returns status dictionary with version info and links.
    """
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "WinOptimizer-Updater/2.0"}
    )

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    from core.legal_manager import LegalManager
    lang = LegalManager().get_language()

    try:
        with urllib.request.urlopen(req, timeout=4, context=ctx) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                tag_name = data.get("tag_name", "v2.0.0").lstrip("v")
                html_url = data.get("html_url", f"https://github.com/{GITHUB_REPO}/releases")
                body = data.get("body", "")

                is_newer = _is_newer_version(tag_name, CURRENT_VERSION_NUM)
                msg_pl = f"Dostępna jest nowa wersja: v{tag_name}!" if is_newer else f"Używasz najnowszej wersji ({CURRENT_VERSION})."
                msg_en = f"A new version is available: v{tag_name}!" if is_newer else f"You are using the latest version ({CURRENT_VERSION})."
                msg = msg_en if lang == 'en' else msg_pl

                return {
                    "success": True,
                    "has_update": is_newer,
                    "is_latest": not is_newer,
                    "current_version": CURRENT_VERSION,
                    "latest_version": f"v{tag_name}",
                    "download_url": html_url,
                    "notes": body[:200] if body else "",
                    "message": msg,
                    "message_pl": msg_pl,
                    "message_en": msg_en
                }
    except Exception:
        # Fallback for offline / network errors
        pass

    msg_pl = f"Używasz najnowszej wersji ({CURRENT_VERSION})."
    msg_en = f"You are using the latest version ({CURRENT_VERSION})."
    msg = msg_en if lang == 'en' else msg_pl

    return {
        "success": True,
        "has_update": False,
        "is_latest": True,
        "current_version": CURRENT_VERSION,
        "latest_version": CURRENT_VERSION,
        "download_url": f"https://github.com/{GITHUB_REPO}/releases",
        "notes": "",
        "message": msg,
        "message_pl": msg_pl,
        "message_en": msg_en
    }

def _is_newer_version(remote: str, current: str) -> bool:
    try:
        r_parts = [int(x) for x in remote.split(".") if x.isdigit()]
        c_parts = [int(x) for x in current.split(".") if x.isdigit()]
        return r_parts > c_parts
    except Exception:
        return False
