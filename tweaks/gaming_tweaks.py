import winreg
import subprocess
import os
import time
from core.registry_manager import get_reg_value, set_reg_value, delete_reg_value

def restart_explorer() -> tuple[bool, str]:
    """Restarts Windows Explorer (explorer.exe) to apply shell/UI tweaks."""
    try:
        subprocess.run("taskkill /f /im explorer.exe", shell=True, capture_output=True)
        time.sleep(0.5)
        subprocess.Popen("explorer.exe", shell=True)
        return True, "Zrestartowano Eksplorator Windows."
    except Exception as e:
        return False, f"Błąd restartu eksploratora: {e}"

# 1. Xbox Game Bar & DVR
def is_gamedvr_disabled() -> bool:
    val = get_reg_value("HKCU", r"System\GameConfigStore", "GameDVR_Enabled")
    return val == 0

def set_gamedvr_disabled(disabled: bool) -> tuple[bool, str]:
    val = 0 if disabled else 1
    s1, m1 = set_reg_value("HKCU", r"System\GameConfigStore", "GameDVR_Enabled", winreg.REG_DWORD, val)
    set_reg_value("HKCU", r"SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR", "AppCaptureEnabled", winreg.REG_DWORD, val)
    set_reg_value("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\GameDVR", "AllowGameDVR", winreg.REG_DWORD, val)
    return s1, "Wyłączono nagrywanie w tle Xbox DVR" if disabled else "Włączono Xbox DVR"

# 2. Game Mode
def is_game_mode_enabled() -> bool:
    val = get_reg_value("HKCU", r"Software\Microsoft\GameBar", "AutoGameModeEnabled")
    return val == 1 or val is None

def set_game_mode_enabled(enabled: bool) -> tuple[bool, str]:
    val = 1 if enabled else 0
    s1, m1 = set_reg_value("HKCU", r"Software\Microsoft\GameBar", "AutoGameModeEnabled", winreg.REG_DWORD, val)
    set_reg_value("HKCU", r"Software\Microsoft\GameBar", "AllowAutoGameMode", winreg.REG_DWORD, val)
    return s1, "Włączono Tryb Gry (Game Mode)" if enabled else "Wyłączono Game Mode"

# 3. Mouse Acceleration
def is_mouse_accel_disabled() -> bool:
    speed = get_reg_value("HKCU", r"Control Panel\Mouse", "MouseSpeed")
    return str(speed) == "0"

def set_mouse_accel_disabled(disabled: bool) -> tuple[bool, str]:
    val = "0" if disabled else "1"
    t1 = "0" if disabled else "6"
    t2 = "0" if disabled else "10"
    s1, m1 = set_reg_value("HKCU", r"Control Panel\Mouse", "MouseSpeed", winreg.REG_SZ, val)
    set_reg_value("HKCU", r"Control Panel\Mouse", "MouseThreshold1", winreg.REG_SZ, t1)
    set_reg_value("HKCU", r"Control Panel\Mouse", "MouseThreshold2", winreg.REG_SZ, t2)
    return s1, "Wyłączono akcelerację myszy (Raw Input 1:1)" if disabled else "Włączono akcelerację myszy"

# 4. Network Throttling
def is_network_throttling_disabled() -> bool:
    val = get_reg_value("HKLM", r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile", "NetworkThrottlingIndex")
    return val == 0xFFFFFFFF or val == -1

def set_network_throttling_disabled(disabled: bool) -> tuple[bool, str]:
    val = 0xFFFFFFFF if disabled else 10
    resp_val = 0 if disabled else 20
    s1, m1 = set_reg_value("HKLM", r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile", "NetworkThrottlingIndex", winreg.REG_DWORD, val)
    set_reg_value("HKLM", r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile", "SystemResponsiveness", winreg.REG_DWORD, resp_val)
    return s1, "Wyłączono dławienie pakietów sieciowych (niższy ping)" if disabled else "Przywrócono domyślne dławienie sieci"

# 5. Power Plan (Ultimate vs Balanced)
def is_ultimate_power_plan_active() -> bool:
    try:
        out = subprocess.check_output("powercfg /getactivescheme", text=True, shell=True)
        return "ultimate" in out.lower() or "najwyższa" in out.lower() or "high performance" in out.lower()
    except Exception:
        return False

def set_power_plan(ultimate: bool) -> tuple[bool, str]:
    try:
        if ultimate:
            # Duplicate and set Ultimate Performance
            out = subprocess.run("powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61", capture_output=True, text=True, shell=True)
            guid = "e9a42b02-d5df-448d-aa00-03f14749eb61"
            if out.stdout and "GUID" in out.stdout:
                parts = out.stdout.split()
                for p in parts:
                    if len(p) == 36 and "-" in p:
                        guid = p
                        break
            subprocess.run(f"powercfg /setactive {guid}", shell=True, check=True)
            return True, "Aktywowano plan zasilania 'Najwyższa wydajność' (Ultimate Performance)."
        else:
            # Revert to standard Balanced plan (381b4222-f694-41f0-9685-ff5bb260df2e)
            subprocess.run("powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e", shell=True, check=True)
            return True, "Przywrócono plan zasilania 'Zrównoważony' (Balanced)."
    except Exception as e:
        return False, f"Błąd zmiany planu zasilania: {e}"

# 6. Gaming DNS (Cloudflare 1.1.1.1)
def is_gaming_dns_active() -> bool:
    try:
        cmd = 'powershell.exe -NoProfile -Command "(Get-DnsClientServerAddress -AddressFamily IPv4 | Where-Object {$_.ServerAddresses -contains \'1.1.1.1\'}).Count"'
        out = subprocess.check_output(cmd, text=True, shell=True, timeout=5).strip()
        return out.isdigit() and int(out) > 0
    except Exception:
        return False

def flush_dns() -> tuple[bool, str]:
    try:
        subprocess.run("ipconfig /flushdns", shell=True, check=True, capture_output=True)
        return True, "Pomyślnie wyczyszczono pamięć podręczną DNS (Flush DNS)."
    except Exception as e:
        return False, f"Błąd czyszczenia DNS: {e}"

def set_gaming_dns(enable: bool) -> tuple[bool, str]:
    try:
        if enable:
            ps_cmd = (
                "Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | "
                "Set-DnsClientServerAddress -ServerAddresses ('1.1.1.1', '1.0.0.1')"
            )
            subprocess.run(f'powershell.exe -NoProfile -Command "{ps_cmd}"', shell=True, check=True, capture_output=True)
            flush_dns()
            return True, "Ustawiono szybki Gaming DNS Cloudflare (1.1.1.1) i wyczyszczono DNS cache."
        else:
            ps_cmd = (
                "Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | "
                "Set-DnsClientServerAddress -ResetServerAddresses"
            )
            subprocess.run(f'powershell.exe -NoProfile -Command "{ps_cmd}"', shell=True, check=True, capture_output=True)
            flush_dns()
            return True, "Przywrócono automatyczny DNS dostawcy (DHCP)."
    except Exception as e:
        return False, f"Błąd konfiguracji DNS: {e}"

# 7. Classic Context Menu (Windows 11)
def is_classic_context_menu_enabled() -> bool:
    val = get_reg_value("HKCU", r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32", "")
    return val == ""

def set_classic_context_menu(enabled: bool) -> tuple[bool, str]:
    subkey = r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32"
    try:
        if enabled:
            set_reg_value("HKCU", subkey, "", winreg.REG_SZ, "")
            restart_explorer()
            return True, "Przywrócono klasyczne pełne menu kontekstowe Windows 11."
        else:
            delete_reg_value("HKCU", subkey, "")
            # Delete parent key if needed
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\CLSID", 0, winreg.KEY_SET_VALUE) as k:
                    winreg.DeleteKey(k, r"{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32")
                    winreg.DeleteKey(k, r"{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}")
            except Exception:
                pass
            restart_explorer()
            return True, "Przywrócono nowoczesne menu Windows 11."
    except Exception as e:
        return False, f"Błąd menu kontekstowego: {e}"

# 8. Disable Sticky Keys & Filter Keys
def is_sticky_keys_disabled() -> bool:
    flags = get_reg_value("HKCU", r"Control Panel\Accessibility\StickyKeys", "Flags")
    return str(flags) == "506"

def set_sticky_keys_disabled(disabled: bool) -> tuple[bool, str]:
    sk_flags = "506" if disabled else "510"
    tk_flags = "58" if disabled else "62"
    kr_flags = "122" if disabled else "126"
    set_reg_value("HKCU", r"Control Panel\Accessibility\StickyKeys", "Flags", winreg.REG_SZ, sk_flags)
    set_reg_value("HKCU", r"Control Panel\Accessibility\ToggleKeys", "Flags", winreg.REG_SZ, tk_flags)
    set_reg_value("HKCU", r"Control Panel\Accessibility\Keyboard Response", "Flags", winreg.REG_SZ, kr_flags)
    return True, "Wyłączono klawisze trwałe (brak okna 5x Shift w grach)" if disabled else "Włączono klawisze trwałe"

# 9. Disable MPO (Multi-Plane Overlay - Stutter fix for GPU)
def is_mpo_disabled() -> bool:
    val = get_reg_value("HKLM", r"SOFTWARE\Microsoft\Windows\Dwm", "OverlayTestMode")
    return val == 5

def set_mpo_disabled(disabled: bool) -> tuple[bool, str]:
    if disabled:
        set_reg_value("HKLM", r"SOFTWARE\Microsoft\Windows\Dwm", "OverlayTestMode", winreg.REG_DWORD, 5)
        return True, "Wyłączono MPO (zapobiega czarnym ekranom i stutteringowi GPU)."
    else:
        delete_reg_value("HKLM", r"SOFTWARE\Microsoft\Windows\Dwm", "OverlayTestMode")
        return True, "Włączono domyślne MPO."

# 10. MMCSS Game GPU Priority
def is_game_priority_boosted() -> bool:
    val = get_reg_value("HKLM", r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games", "GPU Priority")
    return val == 8

def set_game_priority_boosted(enabled: bool) -> tuple[bool, str]:
    gpu_p = 8 if enabled else 2
    pri = 6 if enabled else 2
    sched = "High" if enabled else "Medium"
    sfio = "High" if enabled else "Normal"
    subkey = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games"
    set_reg_value("HKLM", subkey, "GPU Priority", winreg.REG_DWORD, gpu_p)
    set_reg_value("HKLM", subkey, "Priority", winreg.REG_DWORD, pri)
    set_reg_value("HKLM", subkey, "Scheduling Category", winreg.REG_SZ, sched)
    set_reg_value("HKLM", subkey, "SFIO Priority", winreg.REG_SZ, sfio)
    return True, "Włączono wysoki priorytet CPU/GPU dla procesów gier (MMCSS)" if enabled else "Przywrócono domyślny priorytet gier"

# 11. Visual Effects Optimization (Performance)
def is_visual_effects_optimized() -> bool:
    val = get_reg_value("HKCU", r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", "VisualFXSetting")
    return val == 2

def set_visual_effects_optimized(enabled: bool) -> tuple[bool, str]:
    val = 2 if enabled else 0
    set_reg_value("HKCU", r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", "VisualFXSetting", winreg.REG_DWORD, val)
    # Turn off menu animations and taskbar animations
    anim_val = "0" if enabled else "1"
    set_reg_value("HKCU", r"Control Panel\Desktop\WindowMetrics", "MinAnimate", winreg.REG_SZ, anim_val)
    return True, "Zoptymalizowano efekty wizualne pod maksymalną wydajność" if enabled else "Domyślne efekty wizualne"

def get_gaming_tweaks_list() -> list[dict]:
    """Returns a dynamic list of all gaming tweaks with current system states."""
    return [
        {
            "id": "gamedvr",
            "name": "Wyłącz Xbox DVR i nagrywanie w tle",
            "desc": "Wyłącza ciągłe buforowanie wideo i nakładkę Xbox, eliminując spadki FPS i micro-stuttering.",
            "tag": "FPS / Stuttering",
            "is_active": is_gamedvr_disabled(),
            "setter": set_gamedvr_disabled
        },
        {
            "id": "gamemode",
            "name": "Włącz oficjalny Tryb Gry (Game Mode)",
            "desc": "Priorytetyzuje rdzenie procesora i pamięć RAM dla aktualnie uruchomionego okna gry.",
            "tag": "CPU Priority",
            "is_active": is_game_mode_enabled(),
            "setter": set_game_mode_enabled
        },
        {
            "id": "mouse_accel",
            "name": "Wyłącz akcelerację myszy (Raw Input 1:1)",
            "desc": "Wyłącza funkcję 'Zwiększ precyzję wskaźnika'. Mysz porusza się zawsze o tę samą odległość (niezbędne w shooterach).",
            "tag": "Aim / Precyzja",
            "is_active": is_mouse_accel_disabled(),
            "setter": set_mouse_accel_disabled
        },
        {
            "id": "sticky_keys",
            "name": "Zablokuj Klawisze Trwałe (Sticky Keys)",
            "desc": "Blokuje irytujące okienko Windows po 5-krotnym wciśnięciu klawisza Shift, które minimalizuje grę.",
            "tag": "Gaming QoL",
            "is_active": is_sticky_keys_disabled(),
            "setter": set_sticky_keys_disabled
        },
        {
            "id": "mpo_fix",
            "name": "Wyłącz MPO (Multi-Plane Overlay Stutter Fix)",
            "desc": "Znany tweak rozwiązujący problem czarnych ekranów, migotania i spadków klatek na kartach NVIDIA RTX i AMD Radeon.",
            "tag": "GPU Fix",
            "is_active": is_mpo_disabled(),
            "setter": set_mpo_disabled
        },
        {
            "id": "game_priority",
            "name": "Wysoki priorytet MMCSS dla silników gier",
            "desc": "Zwiększa priorytet szeregowania zadań multimedialnych i graficznych (Games Task Scheduling).",
            "tag": "Latencja",
            "is_active": is_game_priority_boosted(),
            "setter": set_game_priority_boosted
        },
        {
            "id": "network_throttle",
            "name": "Wyłącz dławienie pakietów sieciowych (Network Throttling)",
            "desc": "Usuwa sztuczne limity pakietów Windows, zmniejszając ping i eliminując lag spikes.",
            "tag": "Sieć / Ping",
            "is_active": is_network_throttling_disabled(),
            "setter": set_network_throttling_disabled
        },
        {
            "id": "power_plan",
            "name": "Plan zasilania 'Najwyższa Wydajność' (Ultimate Performance)",
            "desc": "Zapobiega parkowaniu rdzeni procesora i obniżaniu taktowania w trakcie rozgrywki.",
            "tag": "Wydajność CPU",
            "is_active": is_ultimate_power_plan_active(),
            "setter": set_power_plan
        },
        {
            "id": "gaming_dns",
            "name": "Gaming DNS (Cloudflare 1.1.1.1 + 1.0.0.1)",
            "desc": "Zmienia serwer DNS karty sieciowej na najszybszy resolver Cloudflare o ultra-niskim czasie odpowiedzi.",
            "tag": "Niższy Ping",
            "is_active": is_gaming_dns_active(),
            "setter": set_gaming_dns
        },
        {
            "id": "classic_menu",
            "name": "Klasyczne menu kontekstowe Windows 11",
            "desc": "Przywraca szybkie, pełne menu prawego przycisku myszy bez uciążliwego 'Pokaż więcej opcji'.",
            "tag": "Windows 11",
            "is_active": is_classic_context_menu_enabled(),
            "setter": set_classic_context_menu
        },
        {
            "id": "visual_effects",
            "name": "Wyłącz animacje okien i cienie (Max FPS)",
            "desc": "Zmniejsza obciążenie procesora DWM (pulpitu Windows) na rzecz maksymalnej responsywności.",
            "tag": "Interfejs",
            "is_active": is_visual_effects_optimized(),
            "setter": set_visual_effects_optimized
        }
    ]
