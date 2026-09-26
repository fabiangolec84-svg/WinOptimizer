import os
import json
from datetime import datetime

CONFIG_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "WinOptimizer")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

class LegalManager:
    """Manages legal consent, EULA, Privacy Policy (RODO), and third-party licenses."""

    def __init__(self):
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        try:
            if not os.path.exists(CONFIG_DIR):
                os.makedirs(CONFIG_DIR, exist_ok=True)
        except Exception as e:
            print(f"Error creating config directory: {e}")

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error reading config: {e}")
        return {
            "first_run_completed": False,
            "terms_accepted": False,
            "terms_accepted_date": None,
            "version": "2.0 Pro"
        }

    def save_config(self, data):
        self._ensure_config_dir()
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get_consent_status(self):
        config = self.load_config()
        return {
            "has_consented": bool(config.get("terms_accepted", False)),
            "accepted_date": config.get("terms_accepted_date"),
            "version": config.get("version", "2.0 Pro")
        }

    def accept_terms(self):
        config = self.load_config()
        config["first_run_completed"] = True
        config["terms_accepted"] = True
        config["terms_accepted_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_config(config)
        return {"success": True, "message": "Zgody prawne zostały pomyślnie zapisane."}

    def get_language(self) -> str:
        config = self.load_config()
        return config.get("language", "pl")

    def set_language(self, lang: str) -> str:
        config = self.load_config()
        chosen = "en" if lang.lower() == "en" else "pl"
        config["language"] = chosen
        self.save_config(config)
        return chosen

    def get_auto_boost(self) -> bool:
        config = self.load_config()
        return config.get("auto_boost", True)

    def set_auto_boost(self, enabled: bool) -> bool:
        config = self.load_config()
        config["auto_boost"] = bool(enabled)
        self.save_config(config)
        return config["auto_boost"]

    def get_legal_texts(self):
        """Returns full Polish legal texts for Privacy Policy, EULA, Licenses, and FAQ."""
        return {
            "privacy_policy": self._get_privacy_policy_text(),
            "eula": self._get_eula_text(),
            "licenses": self._get_licenses_text(),
            "smartscreen_faq": self._get_smartscreen_faq_text()
        }

    def _get_privacy_policy_text(self):
        return """
### POLITYKA PRYWATNOŚCI APLIKACJI WINOPTIMIZER (ZGODNA Z RODO / GDPR)
**Wersja:** 2.0 Pro | **Ostatnia aktualizacja:** 2026

#### 1. Wstęp i Zasada „Zero-Telemetry” (Local-First Architecture)
Szanujemy prywatność naszych użytkowników. Aplikacja **WinOptimizer** została zaprojektowana w oparciu o fundamentalną zasadę **Zero-Telemetry** oraz architekturę **100% Local-First**. Oznacza to, że:
- Aplikacja **nie gromadzi, nie przechowuje na zewnętrznych serwerach ani nie przesyła przez Internet** żadnych danych osobowych, identyfikatorów sprzętowych, historii przeglądania ani logów systemowych użytkownika.
- Wszelkie analizy, skanowanie plików i pomiary wydajności (CPU, RAM, Dysk, procesy) odbywają się **wyłącznie lokalnie w pamięci RAM komputera użytkownika**.

#### 2. Administrator Danych
Administratorem danych przetwarzanych lokalnie na Twoim urządzeniu jesteś Ty sam (użytkownik końcowy). Twórcy aplikacji WinOptimizer nie mają dostępu do Twojego komputera, plików ani wpisów w rejestrze.

#### 3. Zakres Danych Odczytywanych Lokalnie
Aplikacja odczytuje następujące parametry systemowe za pośrednictwem natywnych interfejsów API systemu Microsoft Windows:
1. **Metryki sprzętowe**: Obciążenie procesora, pamięci RAM, dostępna przestrzeń na dysku systemowym oraz lista aktualnie uruchomionych procesów – w celu prezentacji obciążenia w czasie rzeczywistym.
2. **Katalogi plików tymczasowych**: Ścieżki i rozmiary plików w folderach `%TEMP%`, pamięci podręcznej shaderów DirectX/Vulkan oraz cache przeglądarek – w celu umożliwienia użytkownikowi ich wyczyszczenia.
3. **Klucze rejestru Windows**: Ustawienia autostartu (`Run`, `RunOnce`) oraz flagi gamingowe/telemetrii (`DiagTrack`, `GameDVR`) – w celu ich włączania lub wyłączania na żądanie użytkownika.
*Żadne z powyższych danych nie opuszczają urządzenia użytkownika.*

#### 4. Podstawa Prawna i Prawa Użytkownika (RODO)
Zgodnie z Rozporządzeniem Parlamentu Europejskiego i Rady (UE) 2016/679 (RODO):
- Przetwarzanie informacji na urządzeniu końcowym odbywa się za Twoją wyraźną zgodą (Art. 6 ust. 1 lit. a RODO) wyrażoną przy pierwszym uruchomieniu programu.
- Masz pełne prawo do odinstalowania aplikacji w dowolnym momencie, co spowoduje usunięcie wszystkich lokalnych plików konfiguracyjnych z katalogu `%APPDATA%\\WinOptimizer`.
        """.strip()

    def _get_eula_text(self):
        return """
### REGULAMIN UŻYTKOWANIA I UMOWA LICENCYJNA (EULA)
**Dla aplikacji:** WinOptimizer 2.0 Pro

#### 1. Przedmiot Umowy
Niniejsza Umowa Licencyjna dla Użytkownika Końcowego („EULA”) stanowi prawnie wiążącą umowę pomiędzy Tobą („Użytkownik”) a twórcami aplikacji WinOptimizer. Pobierając, instalując lub uruchamiając WinOptimizer, Użytkownik wyraża zgodę na warunki niniejszego Regulaminu.

#### 2. Udzielenie Licencji
Twórcy udzielają Użytkownikowi bezpłatnej, niewyłącznej, niezbywalnej licencji na korzystanie z aplikacji WinOptimizer na prywatnych oraz firmowych komputerach z systemem operacyjnym Windows 10 lub Windows 11.

#### 3. Wyłączenie Odpowiedzialności i Gwarancji (Klauzula „AS IS”)
Zgodnie z art. 473 § 1 Kodeksu Cywilnego:
1. **Aplikacja jest dostarczana w stanie, w jakim się znajduje („AS IS”)**, bez jakichkolwiek gwarancji, wyraźnych lub dorozumianych, w tym gwarancji przydatności handlowej, nieprzerwanego działania czy przydatności do określonego celu.
2. Aplikacja WinOptimizer ingeruje w zaawansowane mechanizmy systemu Windows (w tym Rejestr Systemowy, Usługi Windows, Plan Zasilania, procesy w tle oraz pliki tymczasowe).
3. **Użytkownik korzysta z funkcji optymalizacji, modyfikacji rejestru i usuwania plików na własną odpowiedzialność.**
4. Twórcy aplikacji nie ponoszą odpowiedzialności za jakiekolwiek bezpośrednie, pośrednie lub przypadkowe szkody, w tym: utratę danych, niestabilność gier zewnętrznych, zawieszenie procesów systemowych czy błędy konfiguracji sprzętowej.

#### 4. Wbudowane Środki Asekuracyjne
W trosce o maksymalne bezpieczeństwo Użytkownika, aplikacja została wyposażona w natywne mechanizmy ochronne:
- **Automatyczna kopia zapasowa rejestru**: Każda modyfikacja klucza rejestru zapisuje kopię pierwotnej wartości w pliku JSON przed dokonaniem zmiany.
- **Rollback jednym kliknięciem**: Możliwość przywrócenia pierwotnych ustawień rejestru w dowolnym momencie.
- **Wsparcie dla Punktów Przywracania Systemu Windows**: Integracja z mechanizmem VSS / System Restore.
        """.strip()

    def _get_licenses_text(self):
        return """
### LICENCJE KOMPONENTÓW ZEWNĘTRZNYCH (OPEN SOURCE NOTICES)
Aplikacja WinOptimizer została stworzona przy użyciu uznanych, bezpiecznych bibliotek Open Source:

1. **pywebview**
   - Licencja: BSD 3-Clause License
   - Copyright (c) 2014-2026 Roman Sirokov and contributors.
   - Redistribution and use in source and binary forms are permitted provided that the copyright notice and this list of conditions are retained.

2. **psutil**
   - Licencja: BSD 3-Clause License
   - Copyright (c) 2009, Jay Loden, Dave Daeschler, Giampaolo Rodola.
   - Używane do bezpiecznego odczytu telemetrii CPU, RAM i dysków.

3. **pythonnet (Python for .NET)**
   - Licencja: MIT License
   - Copyright (c) 2006-2026 Python.NET Contributors.
   - Używane do integracji z natywnym interfejsem WebView2 w systemie Windows.

4. **Python Programming Language**
   - Licencja: Python Software Foundation License (PSFL)
   - Copyright (c) 2001-2026 Python Software Foundation.

5. **Google Fonts (Plus Jakarta Sans, JetBrains Mono)**
   - Licencja: SIL Open Font License 1.1 (OFL)
   - Copyright (c) Tokotype, JetBrains.
        """.strip()

    def _get_smartscreen_faq_text(self):
        return """
### DLACZEGO WINDOWS DEFENDER / SMARTSCREEN MOŻE WYŚWIETLAĆ KOMUNIKAT?

#### 1. Komunikat „System Windows ochronił ten komputer”
Podczas uruchamiania darmowych aplikacji na nowo pobranym pliku `.exe`, filtr Microsoft Defender SmartScreen może wyświetlić niebieskie okienko informujące o „nierozpoznanej aplikacji”.

#### 2. Przyczyna Techniczna
Microsoft wymaga płatnych certyfikatów podpisów cyfrowych klasy **Extended Validation (EV Code Signing)**, których koszt wynosi od 1200 do 2500 zł rocznie. Darmowe, niezależne projekty open-source nie korzystają z komercyjnych certyfikatów korporacyjnych, przez co filtr SmartScreen traktuje każdy nowo skompilowany plik jako „nieznany”, dopóki nie pobierze go kilkadziesiąt tysięcy osób.

#### 3. Jak Bezpiecznie Uruchomić Aplikację?
1. W niebieskim oknie SmartScreen kliknij odnośnik **„Więcej informacji”**.
2. Następnie kliknij przycisk **„Uruchom mimo to”**.
3. Aplikacja poprosi o standardowe uprawnienia Administratora (UAC), które są niezbędne do optymalizacji rejestru Windows i zwalniania pamięci RAM.
        """.strip()
