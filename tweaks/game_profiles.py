import os
import shutil
import subprocess

def clean_fivem_cache() -> tuple[bool, str]:
    """Cleans FiveM server cache to fix crashes and free disk space."""
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    fivem_data = os.path.join(local_app_data, "FiveM", "FiveM.app", "data")
    cache_dirs = [
        os.path.join(fivem_data, "cache"),
        os.path.join(fivem_data, "server-cache"),
        os.path.join(fivem_data, "server-cache-priv"),
        os.path.join(fivem_data, "nui-storage"),
    ]

    freed = 0
    cleaned = False
    for cd in cache_dirs:
        if os.path.exists(cd):
            try:
                for root, dirs, files in os.walk(cd):
                    for f in files:
                        try:
                            fp = os.path.join(root, f)
                            freed += os.path.getsize(fp)
                        except Exception:
                            pass
                shutil.rmtree(cd, ignore_errors=True)
                cleaned = True
            except Exception:
                pass

    if cleaned:
        mb = round(freed / (1024 * 1024), 1)
        return True, f"Pomyślnie wyczyszczono cache FiveM! Zwolniono {mb} MB."
    else:
        return False, "Nie znaleziono folderu cache FiveM lub jest już pusty."

GAME_PROFILES = [
    {
        "id": "cs2",
        "name": "Counter-Strike 2 (CS2)",
        "icon": "🎯",
        "description": "Zalecane parametry startowe w Steam dla maksymalnego FPS i najniższego tick-latency.",
        "launch_args": "-novid -high -threads 8 +fps_max 0 -nojoy +engine_low_latency_sleep_after_client_tick true",
        "tips": "W opcjach gry włącz NVIDIA Reflex na 'Włączony + Boost' oraz wyłącz MSAA powyżej 4x."
    },
    {
        "id": "valorant",
        "name": "Valorant (Riot Games)",
        "icon": "⚡",
        "description": "Optymalizacja pod silnik Unreal Engine i usługę antycheat Riot Vanguard (vgc).",
        "launch_args": "Wyłączenie optymalizacji pełnoekranowych dla VALORANT-Win64-Shipping.exe",
        "tips": "Upewnij się, że w grze włączone jest 'RawInputBuffer' (Bufor surowych danych wejściowych) dla 1:1 polling rate 1000-8000Hz."
    },
    {
        "id": "fortnite",
        "name": "Fortnite (Unreal Engine 5)",
        "icon": "🛡️",
        "description": "Parametry startowe w Epic Games Launcher zapobiegające spadkom klatek przy lądowaniu.",
        "launch_args": "-USEALLAVAILABLECORES -NOTEXTURESTREAMING -preferredProcessor 8",
        "tips": "Dla maksymalnego FPS wybierz tryb renderowania 'Performance Mode' (Tryb wydajnościowy) w ustawieniach wideo."
    },
    {
        "id": "warzone",
        "name": "Call of Duty: Warzone / MW3",
        "icon": "💥",
        "description": "Optymalizacja alokacji pamięci VRAM i renderowania wątków CPU.",
        "launch_args": "-d3d11 -high",
        "tips": "Ustaw 'Target VRAM Scale' w grze na 70-80%, aby zapobiec alokacji pamięci wirtualnej przez Windows."
    },
    {
        "id": "fivem",
        "name": "FiveM / GTA V Roleplay",
        "icon": "🚗",
        "description": "Czyszczenie zasobów serwerowych FiveM (częsta przyczyna zacinania tekstur i crashów).",
        "special_action": "clean_fivem",
        "action_label": "🧹 Wyczyść Cache FiveM",
        "tips": "Wyczyszczenie cache usuwa uszkodzone modele pojazdów i skrypty ze starych serwerów."
    },
    {
        "id": "minecraft",
        "name": "Minecraft (Java Edition)",
        "icon": "⛏️",
        "description": "Optymalne argumenty maszyny wirtualnej Java (JVM) z garbage collectorem G1GC.",
        "launch_args": "-Xmx8G -Xms4G -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200",
        "tips": "Zainstaluj modyfikację Sodium lub Embeddium zamiast OptiFine dla 3-krotnego wzrostu FPS."
    }
]
