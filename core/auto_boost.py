import os
import time
import threading
import psutil
from core.ram_cleaner import clean_ram

KNOWN_GAMES = {
    "cs2.exe": "Counter-Strike 2",
    "csgo.exe": "CS:GO",
    "valorant-win64-shipping.exe": "VALORANT",
    "valorant.exe": "VALORANT",
    "fortniteclient-win64-shipping.exe": "Fortnite",
    "fortnite.exe": "Fortnite",
    "gta5.exe": "Grand Theft Auto V",
    "fivem.exe": "FiveM",
    "fivem_b2699_gtaprocess.exe": "FiveM (GTA V)",
    "fivem_b2802_gtaprocess.exe": "FiveM (GTA V)",
    "cod.exe": "Call of Duty: Warzone",
    "modernwarfare.exe": "Call of Duty: Modern Warfare",
    "javaw.exe": "Minecraft",
    "minecraft.exe": "Minecraft",
    "overwatch.exe": "Overwatch 2",
    "r5pc_r5.exe": "Apex Legends",
    "apexlegends.exe": "Apex Legends",
    "rainbowsix.exe": "Rainbow Six Siege",
    "league of legends.exe": "League of Legends",
    "leagueclientux.exe": "League of Legends Client",
    "dota2.exe": "Dota 2",
    "cyberpunk2077.exe": "Cyberpunk 2077",
    "witcher3.exe": "Wiedźmin 3",
    "helldivers2.exe": "Helldivers 2",
    "rustclient.exe": "Rust",
    "rust.exe": "Rust",
    "rocketleague.exe": "Rocket League",
    "robloxplayerbeta.exe": "Roblox",
    "fc24.exe": "EA Sports FC 24",
    "fc25.exe": "EA Sports FC 25",
    "genshinimpact.exe": "Genshin Impact",
    "starrail.exe": "Honkai: Star Rail",
    "tslgame.exe": "PUBG: BATTLEGROUNDS",
    "pubg.exe": "PUBG",
}

class AutoBoostDaemon:
    """
    Background worker monitoring active processes for running games.
    Upon detection, boosts CPU priority to High and flushes Standby RAM.
    """

    def __init__(self, check_interval_sec: float = 3.0):
        self.check_interval = check_interval_sec
        self.is_running = False
        self.is_enabled = True
        self.boosted_pids = set()
        self.active_game = None
        self.recent_events = []
        self._thread = None
        self._lock = threading.Lock()

    @property
    def enabled(self) -> bool:
        return self.is_enabled

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self.is_running = True
        self._thread = threading.Thread(target=self._worker_loop, daemon=True, name="AutoBoostThread")
        self._thread.start()

    def stop(self):
        self.is_running = False

    def set_enabled(self, enabled: bool):
        with self._lock:
            self.is_enabled = bool(enabled)
            if not self.is_enabled:
                self.boosted_pids.clear()
                self.active_game = None

    def get_state(self) -> dict:
        with self._lock:
            return {
                "enabled": self.is_enabled,
                "active_game": self.active_game,
                "boosted_count": len(self.boosted_pids),
                "recent_event": self.recent_events[-1] if self.recent_events else None
            }

    def pop_notifications(self) -> list[dict]:
        with self._lock:
            events = list(self.recent_events)
            self.recent_events.clear()
            return events

    def _worker_loop(self):
        while self.is_running:
            try:
                if self.is_enabled:
                    self._check_processes()
            except Exception as e:
                pass
            time.sleep(self.check_interval)

    def _check_processes(self):
        current_game = None
        current_pids = set()

        for proc in psutil.process_iter(['pid', 'name']):
            try:
                pid = proc.info['pid']
                name = (proc.info['name'] or "").lower()
                current_pids.add(pid)

                if name in KNOWN_GAMES:
                    game_title = KNOWN_GAMES[name]
                    current_game = {"pid": pid, "name": game_title, "exe": name}

                    # If not yet boosted
                    if pid not in self.boosted_pids:
                        self._apply_boost(pid, game_title, name)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        with self._lock:
            # Clean up terminated PIDs
            self.boosted_pids = {p for p in self.boosted_pids if p in current_pids}
            self.active_game = current_game

    def _apply_boost(self, pid: int, game_title: str, exe_name: str):
        try:
            p = psutil.Process(pid)
            # Set High CPU Priority
            p.nice(psutil.HIGH_PRIORITY_CLASS)
            
            # Flush Standby List & RAM working sets
            b, a, freed_mb = clean_ram()

            with self._lock:
                self.boosted_pids.add(pid)
                event = {
                    "time": time.strftime("%H:%M:%S"),
                    "game": game_title,
                    "pid": pid,
                    "freed_mb": freed_mb,
                    "message": f"Wykryto grę: {game_title}. Zastosowano Auto-Boost (Wysoki priorytet CPU + zwolniono {freed_mb} MB RAM)!",
                    "message_pl": f"Wykryto grę: {game_title}. Zastosowano Auto-Boost (Wysoki priorytet CPU + zwolniono {freed_mb} MB RAM)!",
                    "message_en": f"Game detected: {game_title}. Auto-Boost applied (High CPU Priority + freed {freed_mb} MB RAM)!"
                }
                self.recent_events.append(event)
                # Keep history reasonable
                if len(self.recent_events) > 10:
                    self.recent_events.pop(0)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        except Exception:
            pass

# Global Singleton
auto_boost_daemon = AutoBoostDaemon()
