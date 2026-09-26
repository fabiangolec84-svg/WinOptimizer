import os
import sys
import psutil
import platform
import subprocess
import time

from core.system_info import get_system_specs, get_realtime_metrics, get_top_processes, kill_process
from core.ram_cleaner import clean_ram
from core.restore_point import create_restore_point
from core.registry_manager import restore_all_settings
from core.cleaner import get_cleaner_targets, scan_targets, clean_targets, format_bytes, get_running_browsers, close_browsers
from tweaks.gaming_tweaks import get_gaming_tweaks_list, flush_dns, restart_explorer
from tweaks.privacy_tweaks import get_privacy_tweaks_list
from tweaks.startup_manager import get_startup_apps, toggle_startup_app, toggle_all_startup_apps
from tweaks.bloatware_remover import get_installed_bloatware, uninstall_bloatware
from tweaks.game_profiles import GAME_PROFILES, clean_fivem_cache
from core.file_hunter import scan_all_large_files, delete_files, get_scan_locations, open_in_explorer
from core.app_manager import get_installed_applications, uninstall_application
from core.legal_manager import LegalManager
from core.auto_boost import auto_boost_daemon
from core.updater import check_for_updates

class ApiBridge:
    """Bridge object exposed to JavaScript in WebView."""

    def __init__(self):
        self._window = None
        self._is_maximized = False
        self.legal_mgr = LegalManager()
        # Initialize auto-boost state from saved config
        auto_boost_daemon.set_enabled(self.legal_mgr.get_auto_boost())

    def set_window(self, window):
        self._window = window

    def window_minimize(self):
        if self._window:
            self._window.minimize()
        return True

    def window_maximize(self):
        if self._window:
            if self._is_maximized:
                self._window.restore()
                self._is_maximized = False
            else:
                self._window.maximize()
                self._is_maximized = True
        return True

    def window_close(self):
        if self._window:
            self._window.destroy()
        return True

    def get_dashboard_data(self):
        try:
            auto_state = auto_boost_daemon.get_state()
            active_game = auto_state.get("active_game")
            m = get_realtime_metrics(active_game)
            specs = get_system_specs()
            procs = get_top_processes(limit=6)

            # Add process trend and system flag
            for p in procs:
                pname = p["name"].lower()
                p["is_system"] = pname in ("msmpeng.exe", "memcompression", "csrss.exe", "lsass.exe", "services.exe")
                # Format memory percent of total RAM
                mem_pct = round((p["memory_mb"] / (specs["ram_total_gb"] * 1024)) * 100, 1)
                p["memory_str"] = f"{round(p['memory_mb'] / 1024, 1)} GB ({mem_pct}%)" if p["memory_mb"] >= 1024 else f"{p['memory_mb']} MB ({mem_pct}%)"
                p["cpu_percent"] = round(p.get("cpu_percent", 0.5), 1)

            # CPU Details
            cpu_count = psutil.cpu_count(logical=True)
            phys_count = psutil.cpu_count(logical=False) or int(cpu_count / 2)
            try:
                freq = round(psutil.cpu_freq().current / 1000, 2)
            except Exception:
                freq = 3.80

            # Real Temperatures and Display Hz / FPS
            cpu_temp = m.get("cpu_temp", 42)
            gpu_temp = m.get("gpu_temp", 45)
            fps_val = m.get("fps", 144)

            return {
                "cpu": {
                    "percent": m["cpu_percent"],
                    "freq_ghz": f"{freq:.2f} GHz",
                    "cores_info": f"{phys_count} rdzeni / {cpu_count} wątków",
                    "name": specs["cpu"],
                    "temp": cpu_temp
                },
                "ram": {
                    "percent": m["ram_percent"],
                    "used_gb": m["ram_used_gb"],
                    "free_gb": m["ram_free_gb"],
                    "total_gb": specs["ram_total_gb"],
                    "info": f"{m['ram_used_gb']} GB używane / {m['ram_free_gb']} GB wolne"
                },
                "disk": {
                    "percent": m["disk_c_percent"],
                    "free_gb": m["disk_c_free_gb"],
                    "total_gb": specs["disk_c_total_gb"],
                    "info": f"{m['disk_c_free_gb']} GB wolne / {specs['disk_c_total_gb']} GB"
                },
                "gpu": {
                    "name": specs["gpu"],
                    "temp": gpu_temp
                },
                "fps": fps_val,
                "processes": procs,
                "system_status": "System działa optymalnie" if m["cpu_percent"] < 75 and m["ram_percent"] < 80 else "Wymaga optymalizacji",
                "auto_boost": auto_state,
                "notifications": auto_boost_daemon.pop_notifications()
            }
        except Exception as e:
            print(f"Error in get_dashboard_data: {e}")
            return {}

    def clean_ram(self):
        before, after, freed = clean_ram()
        if freed > 0:
            msg = f"Zwolniono {freed} MB pamięci RAM."
        else:
            msg = "Pamięć RAM jest już optymalnie wyczyszczona."
        return {"freed_mb": freed, "message": msg}

    def run_1click_boost(self):
        from tweaks.gaming_tweaks import set_gamedvr_disabled, set_game_mode_enabled, set_power_plan, set_network_throttling_disabled
        set_gamedvr_disabled(True)
        set_game_mode_enabled(True)
        set_power_plan(True)
        set_network_throttling_disabled(True)
        b, a, freed_ram = clean_ram()
        freed_bytes, _ = clean_targets(["user_temp", "shader_cache", "crash_dumps", "discord_cache", "spotify_cache"])
        freed_mb = int(freed_bytes / (1024 * 1024))
        return {
            "success": True,
            "message": f"Aktywowano Tryb Gry i Najwyższą Wydajność. Zwolniono {freed_ram} MB RAM oraz {freed_mb} MB na dysku."
        }

    def kill_proc(self, pid):
        ok, msg = kill_process(int(pid))
        return {"success": ok, "message": msg}

    def rollback_all_registry(self):
        succ, tot = restore_all_settings()
        return {"success": True, "message": f"Przywrócono {succ} z {tot} wartości rejestru."}

    def create_restore_point_action(self):
        ok, msg = create_restore_point()
        return {"success": ok, "message": msg}

    def restart_explorer_action(self):
        ok, msg = restart_explorer()
        return {"success": ok, "message": msg}

    # Cleaner
    def scan_cleaner_targets(self):
        scan_data = scan_targets()
        raw_targets = get_cleaner_targets()
        cats = scan_data.get("categories", {})
        result_list = []
        for key, info in raw_targets.items():
            cat_stat = cats.get(key, {})
            result_list.append({
                "key": key,
                "name": info["name"],
                "desc": info["desc"],
                "size_bytes": cat_stat.get("size", 0),
                "size_str": cat_stat.get("size_str", "0 B"),
                "files_count": cat_stat.get("files", 0),
                "default_check": info.get("default", True)
            })
        return result_list

    def clean_cleaner_targets(self, selected_keys):
        freed, count = clean_targets(selected_keys)
        return {"freed_str": format_bytes(freed), "freed_bytes": freed, "count": count}

    def get_open_browsers(self):
        return get_running_browsers()

    def close_all_browsers(self):
        closed = close_browsers()
        return {"closed": closed, "message": f"Zamknięto {closed} procesów przeglądarek."}

    # Gaming Tweaks
    def get_gaming_tweaks(self):
        tweaks = get_gaming_tweaks_list()
        clean = []
        for t in tweaks:
            is_act = bool(t.get("is_active", False))
            clean.append({
                "id": t["id"],
                "name": t["name"],
                "desc": t["desc"],
                "tag": t.get("tag", ""),
                "is_active": is_act,
                "is_enabled": is_act
            })
        return clean

    def toggle_gaming_tweak(self, tweak_id, enabled):
        tweaks = get_gaming_tweaks_list()
        for t in tweaks:
            if t["id"] == tweak_id:
                ok, msg = t["setter"](bool(enabled))
                return {"success": ok, "message": msg}
        return {"success": False, "message": "Nieznany tweak"}

    def enable_all_gaming(self):
        tweaks = get_gaming_tweaks_list()
        for t in tweaks:
            try:
                t["setter"](True)
            except Exception:
                pass
        return {"success": True, "message": "Włączono wszystkie zalecane optymalizacje gamingowe."}

    def restore_default_gaming(self):
        tweaks = get_gaming_tweaks_list()
        for t in tweaks:
            try:
                t["setter"](False)
            except Exception:
                pass
        return {"success": True, "message": "Przywrócono domyślne ustawienia systemowe."}

    def flush_dns_action(self):
        ok, msg = flush_dns()
        return {"success": ok, "message": msg}

    # Game Profiles
    def get_game_profiles(self):
        return GAME_PROFILES

    def clean_fivem_action(self):
        ok, msg = clean_fivem_cache()
        return {"success": ok, "message": msg}

    # Privacy Tweaks
    def get_privacy_tweaks(self):
        tweaks = get_privacy_tweaks_list()
        clean = []
        for t in tweaks:
            is_act = bool(t.get("is_active", False))
            clean.append({
                "id": t["id"],
                "name": t["name"],
                "desc": t["desc"],
                "is_active": is_act,
                "is_enabled": is_act
            })
        return clean

    def toggle_privacy_tweak(self, tweak_id, enabled):
        tweaks = get_privacy_tweaks_list()
        for t in tweaks:
            if t["id"] == tweak_id:
                ok, msg = t["setter"](bool(enabled))
                return {"success": ok, "message": msg}
        return {"success": False, "message": "Nieznany tweak"}

    def disable_all_privacy(self):
        from tweaks.privacy_tweaks import set_telemetry_disabled, set_bing_search_disabled, set_cortana_disabled, set_ads_suggestions_disabled
        set_telemetry_disabled(True)
        set_bing_search_disabled(True)
        set_cortana_disabled(True)
        set_ads_suggestions_disabled(True)
        return {"success": True, "message": "Wyłączono telemetrię i zbędne usługi Microsoftu w tle."}

    # Startup Manager
    def get_startup_items(self):
        items = get_startup_apps()
        clean = []
        for item in items:
            it = dict(item)
            is_en = bool(it.get("enabled", True))
            it["is_enabled"] = is_en
            it["enabled"] = is_en
            clean.append(it)
        return clean

    def toggle_startup_item(self, app_id, enabled):
        apps = get_startup_apps()
        for a in apps:
            if a["id"] == app_id:
                ok, msg = toggle_startup_app(a, bool(enabled))
                return {"success": ok, "message": msg}
        return {"success": False, "message": "Nie znaleziono aplikacji"}

    def toggle_all_startup(self, enabled):
        succ, tot = toggle_all_startup_apps(bool(enabled))
        msg = f"Zaktualizowano {succ} z {tot} wpisów autostartu."
        return {"success": True, "message": msg}

    # Storage & File Hunter
    def get_storage_locations(self):
        return get_scan_locations()

    def scan_storage_files(self, target_dir, min_size_mb, min_days_old, cat_filter):
        files = scan_all_large_files(
            target_dir=target_dir,
            min_size_mb=float(min_size_mb),
            min_days_old=float(min_days_old),
            category_filter=cat_filter
        )
        total_bytes = sum(f["size"] for f in files)
        return {
            "files": files,
            "total_count": len(files),
            "total_size_str": format_bytes(total_bytes)
        }

    def open_file_in_explorer(self, file_path):
        ok = open_in_explorer(file_path)
        return {"success": ok}

    def delete_storage_files(self, paths):
        freed, count = delete_files(paths)
        return {"success": True, "freed_str": format_bytes(freed), "count": count}

    # App Uninstaller
    def get_installed_apps(self):
        return get_installed_applications()

    def uninstall_application(self, cmd):
        ok, msg = uninstall_application(cmd)
        return {"success": ok, "message": msg}

    # Bloatware
    def get_bloatware_apps(self):
        apps = get_installed_bloatware()
        clean = []
        for a in apps:
            if a.get("installed", False):
                clean.append({
                    "id": a["id"],
                    "package_name": a["id"],
                    "name": a["name"],
                    "desc": a.get("desc", ""),
                    "installed": True
                })
        return clean

    def uninstall_bloatware_app(self, pkg_id):
        ok, msg = uninstall_bloatware(pkg_id)
        return {"success": ok, "message": msg}

    # Legal, Privacy, and Consent
    def get_legal_status(self):
        return self.legal_mgr.get_consent_status()

    def accept_legal_terms(self, create_restore_pt=False):
        res = self.legal_mgr.accept_terms()
        restore_res = None
        if create_restore_pt:
            ok, msg = create_restore_point()
            restore_res = {"success": ok, "message": msg}
        return {
            "success": True,
            "message": res["message"],
            "restore_point": restore_res
        }

    def get_legal_documents(self):
        return self.legal_mgr.get_legal_texts()

    # Auto-Boost Game Detection Daemon
    def get_auto_boost_status(self):
        return auto_boost_daemon.get_state()

    def toggle_auto_boost(self, enabled):
        en = bool(enabled)
        auto_boost_daemon.set_enabled(en)
        self.legal_mgr.set_auto_boost(en)
        lang = self.legal_mgr.get_language()
        if lang == 'en':
            msg = "Background Auto-Boost is now ACTIVE." if en else "Background Auto-Boost is now DISABLED."
        else:
            msg = "Włączono automatyczną optymalizację gier w tle." if en else "Wyłączono optymalizację w tle."
        return {"success": True, "enabled": en, "message": msg}

    # Auto-Updater
    def check_for_updates(self):
        return check_for_updates()

    def check_updates(self):
        return check_for_updates()

    # Language (i18n)
    def get_current_language(self):
        return self.legal_mgr.get_language()

    def get_language(self):
        return self.legal_mgr.get_language()

    def set_system_language(self, lang):
        chosen = self.legal_mgr.set_language(str(lang))
        return {"success": True, "language": chosen}

    def set_language(self, lang):
        return self.set_system_language(lang)

