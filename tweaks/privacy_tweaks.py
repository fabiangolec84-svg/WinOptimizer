import winreg
import subprocess
from core.registry_manager import get_reg_value, set_reg_value

def is_telemetry_disabled() -> bool:
    val = get_reg_value("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\DataCollection", "AllowTelemetry")
    return val == 0

def set_telemetry_disabled(disabled: bool) -> tuple[bool, str]:
    val = 0 if disabled else 1
    set_reg_value("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\DataCollection", "AllowTelemetry", winreg.REG_DWORD, val)
    # Stop/disable or start DiagTrack service
    start_type = "disabled" if disabled else "auto"
    subprocess.run(f"sc config DiagTrack start= {start_type}", shell=True, capture_output=True)
    if disabled:
        subprocess.run("sc stop DiagTrack", shell=True, capture_output=True)
        subprocess.run("sc config dmwappushservice start= disabled", shell=True, capture_output=True)
        subprocess.run("sc stop dmwappushservice", shell=True, capture_output=True)
    return True, "Wyłączono usługi telemetryczne i zbieranie danych DiagTrack" if disabled else "Włączono telemetrię"

def is_bing_search_disabled() -> bool:
    val = get_reg_value("HKCU", r"Software\Policies\Microsoft\Windows\Explorer", "DisableSearchBoxSuggestions")
    return val == 1

def set_bing_search_disabled(disabled: bool) -> tuple[bool, str]:
    val = 1 if disabled else 0
    bing_val = 0 if disabled else 1
    set_reg_value("HKCU", r"Software\Policies\Microsoft\Windows\Explorer", "DisableSearchBoxSuggestions", winreg.REG_DWORD, val)
    set_reg_value("HKCU", r"Software\Microsoft\Windows\CurrentVersion\Search", "BingSearchEnabled", winreg.REG_DWORD, bing_val)
    return True, "Wyłączono wyszukiwarkę Bing w menu Start (szybsze wyszukiwanie)" if disabled else "Włączono Bing w menu Start"

def is_cortana_disabled() -> bool:
    val = get_reg_value("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\Windows Search", "AllowCortana")
    return val == 0

def set_cortana_disabled(disabled: bool) -> tuple[bool, str]:
    val = 0 if disabled else 1
    set_reg_value("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\Windows Search", "AllowCortana", winreg.REG_DWORD, val)
    return True, "Wyłączono Cortanę" if disabled else "Włączono Cortanę"

def is_ads_suggestions_disabled() -> bool:
    val = get_reg_value("HKCU", r"Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo", "Enabled")
    return val == 0

def set_ads_suggestions_disabled(disabled: bool) -> tuple[bool, str]:
    val = 0 if disabled else 1
    set_reg_value("HKCU", r"Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo", "Enabled", winreg.REG_DWORD, val)
    set_reg_value("HKCU", r"Software\Microsoft\Windows\CurrentVersion\Privacy", "TailoredExperiencesWithDiagnosticDataEnabled", winreg.REG_DWORD, val)
    set_reg_value("HKCU", r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "SubscribedContent-338389Enabled", winreg.REG_DWORD, val)
    set_reg_value("HKCU", r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "SubscribedContent-310093Enabled", winreg.REG_DWORD, val)
    return True, "Wyłączono reklamy, identyfikator reklamowy i podpowiedzi Microsoftu" if disabled else "Włączono sugestie i reklamy"

def get_privacy_tweaks_list() -> list[dict]:
    return [
        {
            "id": "telemetry",
            "name": "Wyłącz telemetrię Windows i usługę DiagTrack",
            "desc": "Zatrzymuje wysyłanie raportów diagnostycznych do Microsoftu i oszczędza zużycie CPU w tle.",
            "is_active": is_telemetry_disabled(),
            "setter": set_telemetry_disabled
        },
        {
            "id": "bing_search",
            "name": "Wyłącz wyszukiwarkę Bing w Menu Start",
            "desc": "Przyspiesza otwieranie i wyszukiwanie programów w menu Start, nie wysyłając zapytań do internetu.",
            "is_active": is_bing_search_disabled(),
            "setter": set_bing_search_disabled
        },
        {
            "id": "cortana",
            "name": "Wyłącz asystenta Cortana",
            "desc": "Całkowicie blokuje proces Cortany w tle, zwalniając zasoby RAM.",
            "is_active": is_cortana_disabled(),
            "setter": set_cortana_disabled
        },
        {
            "id": "ads_suggestions",
            "name": "Wyłącz reklamy i sugerowane aplikacje Windows",
            "desc": "Usuwa sponsorowane kafelki, porady i automatyczne pobieranie polecanych gier w tle.",
            "is_active": is_ads_suggestions_disabled(),
            "setter": set_ads_suggestions_disabled
        }
    ]
