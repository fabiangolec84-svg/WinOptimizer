import subprocess

BLOATWARE_LIST = [
    {
        "id": "Microsoft.BingWeather",
        "name": "Pogoda (Bing Weather)",
        "desc": "Aplikacja pogody stale odświeżająca dane w tle."
    },
    {
        "id": "Microsoft.BingNews",
        "name": "Wiadomości (Bing News)",
        "desc": "Kanał informacyjny Microsoftu."
    },
    {
        "id": "Microsoft.MicrosoftSolitaireCollection",
        "name": "Microsoft Solitaire Collection",
        "desc": "Kolekcja gier karcianych z reklamami."
    },
    {
        "id": "Microsoft.WindowsFeedbackHub",
        "name": "Centrum Opinii (Feedback Hub)",
        "desc": "Narzędzie do zgłaszania opinii i analityki."
    },
    {
        "id": "Microsoft.GetHelp",
        "name": "Uzyskaj Pomoc (Get Help)",
        "desc": "Wbudowany asystent pomocy technicznej."
    },
    {
        "id": "Microsoft.Getstarted",
        "name": "Wskazówki (Tips / Get Started)",
        "desc": "Podpowiedzi i samouczki Windows."
    },
    {
        "id": "Microsoft.Microsoft3DViewer",
        "name": "Przeglądarka 3D (3D Viewer)",
        "desc": "Program do modeli 3D."
    },
    {
        "id": "Microsoft.SkypeApp",
        "name": "Skype App",
        "desc": "Wbudowana wersja Skype."
    },
    {
        "id": "Clipchamp.Clipchamp",
        "name": "Clipchamp Video Editor",
        "desc": "Edytor wideo instalowany domyślnie w nowszych wersjach Windows."
    },
    {
        "id": "Microsoft.ZuneMusic",
        "name": "Media Player / Groove Music",
        "desc": "Odtwarzacz muzyczny z procesami w tle."
    },
    {
        "id": "Microsoft.ZuneVideo",
        "name": "Filmy i TV (Movies & TV)",
        "desc": "Domyślny odtwarzacz wideo Windows."
    },
    {
        "id": "Microsoft.WindowsMaps",
        "name": "Mapy Windows",
        "desc": "Usługa map i geolokalizacji offline."
    },
    {
        "id": "Microsoft.YourPhone",
        "name": "Łącze z telefonem (Phone Link)",
        "desc": "Aplikacja synchronizująca smartfon w tle."
    },
    {
        "id": "Microsoft.Windows.PeopleExperienceHost",
        "name": "Kontakty Windows (People)",
        "desc": "Wbudowany pasek kontaktów na pasku zadań."
    },
    {
        "id": "Microsoft.549981C3F5F10",
        "name": "Cortana",
        "desc": "Asystent głosowy Microsoftu."
    },
    {
        "id": "Microsoft.XboxGamingOverlay",
        "name": "Xbox Game Bar Overlay",
        "desc": "Nakładka Xbox często powodująca spadek FPS."
    },
    {
        "id": "Microsoft.Todos",
        "name": "Microsoft To Do",
        "desc": "Aplikacja zadań Microsoftu."
    }
]

def get_installed_bloatware() -> list[dict]:
    """Scans system to check which bloatware apps are installed."""
    try:
        cmd = 'powershell.exe -NoProfile -Command "Get-AppxPackage | Select-Object -ExpandProperty Name"'
        out = subprocess.check_output(cmd, text=True, shell=True, timeout=15)
        installed_names = set(line.strip().lower() for line in out.splitlines() if line.strip())

        results = []
        for app in BLOATWARE_LIST:
            app_copy = dict(app)
            app_copy["installed"] = app["id"].lower() in installed_names
            results.append(app_copy)
        return results
    except Exception:
        # Fallback
        return [dict(app, installed=False) for app in BLOATWARE_LIST]

def uninstall_bloatware(package_id: str) -> tuple[bool, str]:
    """Uninstalls a specific AppX package."""
    cmd = f'powershell.exe -NoProfile -Command "Get-AppxPackage *{package_id}* | Remove-AppxPackage"'
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if res.returncode == 0:
            return True, f"Pomyślnie odinstalowano {package_id}."
        else:
            return False, res.stderr.strip() or "Nie udało się odinstalować."
    except Exception as e:
        return False, str(e)
