import customtkinter as ctk
import threading
from ui.theme import *
from ui.components.metric_card import MetricCard
from core.system_info import get_system_specs, get_realtime_metrics, get_top_processes, kill_process
from core.ram_cleaner import clean_ram
from core.restore_point import create_restore_point
from core.registry_manager import restore_all_settings
from tweaks.gaming_tweaks import (
    set_gamedvr_disabled,
    set_game_mode_enabled,
    set_power_plan,
    set_network_throttling_disabled,
    restart_explorer
)
from core.cleaner import clean_targets

class DashboardPage(ctk.CTkScrollableFrame):
    def __init__(self, master, show_toast_callback=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.show_toast = show_toast_callback
        self.is_monitoring = True

        self._build_header()
        self._build_metrics()
        self._build_quick_actions()
        self._build_process_manager()
        self._build_safety_center()
        self._build_specs()

        self._start_metrics_loop()

    def _safe_after(self, delay_ms: int, callback):
        try:
            if self.winfo_exists():
                self.after(delay_ms, callback)
        except Exception:
            pass

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 12))

        title = ctk.CTkLabel(header, text="Pulpit Główny & Monitor Wydajności 2.0", font=FONT_HEADING, text_color=TEXT_PRIMARY)
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header,
            text="Centrum sterowania wydajnością: obciążenie podzespołów na żywo, top procesy w pamięci RAM, 1-Click Game Boost i centrum bezpieczeństwa.",
            font=FONT_BODY,
            text_color=TEXT_SECONDARY
        )
        subtitle.pack(anchor="w", pady=(2, 0))

    def _build_metrics(self):
        metrics_container = ctk.CTkFrame(self, fg_color="transparent")
        metrics_container.pack(fill="x", padx=20, pady=8)
        metrics_container.grid_columnconfigure((0, 1, 2), weight=1)

        self.cpu_card = MetricCard(metrics_container, title="PROCESOR (CPU)", initial_value="-- %", subtext="Odczytywanie...", progress=0.0)
        self.cpu_card.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.ram_card = MetricCard(metrics_container, title="PAMIĘĆ (RAM)", initial_value="-- %", subtext="Odczytywanie...", progress=0.0)
        self.ram_card.grid(row=0, column=1, sticky="ew", padx=4)

        self.disk_card = MetricCard(metrics_container, title="DYSK SYSTEMOWY (C:)", initial_value="-- %", subtext="Odczytywanie...", progress=0.0)
        self.disk_card.grid(row=0, column=2, sticky="ew", padx=(8, 0))

    def _build_quick_actions(self):
        box = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        box.pack(fill="x", padx=20, pady=12)

        box_header = ctk.CTkFrame(box, fg_color="transparent")
        box_header.pack(fill="x", padx=16, pady=(12, 6))

        lbl = ctk.CTkLabel(box_header, text="⚡ Szybka Optymalizacja (1-Click Boost)", font=FONT_SUBHEADING, text_color=TEXT_PRIMARY)
        lbl.pack(side="left")

        desc = ctk.CTkLabel(
            box,
            text="Jednym kliknięciem oczyść pamięć podręczną RAM (Standby List), włącz tryb gry, aktywuj plan zasilania Najwyższa Wydajność, wyłącz dławienie sieci i usuń zbędne pliki tymczasowe.",
            font=FONT_SMALL,
            text_color=TEXT_SECONDARY,
            wraplength=640,
            justify="left"
        )
        desc.pack(anchor="w", padx=16, pady=(0, 12))

        btn_row = ctk.CTkFrame(box, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(0, 14))

        self.boost_btn = ctk.CTkButton(
            btn_row,
            text="🚀 URUCHOM 1-CLICK GAME BOOST",
            font=("Segoe UI", 13, "bold"),
            fg_color=ACCENT_CYAN,
            hover_color=ACCENT_CYAN_HOVER,
            text_color="#000000",
            height=42,
            corner_radius=8,
            command=self._run_one_click_boost
        )
        self.boost_btn.pack(side="left", padx=(0, 12))

        self.ram_btn = ctk.CTkButton(
            btn_row,
            text="💾 Zwolnij RAM",
            font=FONT_BODY_BOLD,
            fg_color="#2b313a",
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY,
            height=42,
            corner_radius=8,
            command=self._run_ram_clean
        )
        self.ram_btn.pack(side="left", padx=(0, 12))

        self.status_lbl = ctk.CTkLabel(box, text="", font=FONT_SMALL, text_color=ACCENT_GREEN)
        self.status_lbl.pack(anchor="w", padx=16, pady=(0, 8))

    def _build_process_manager(self):
        box = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        box.pack(fill="x", padx=20, pady=(0, 12))

        header = ctk.CTkFrame(box, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 6))

        title = ctk.CTkLabel(header, text="🔥 Najbardziej Zasobożerne Procesy (RAM)", font=FONT_SUBHEADING, text_color=TEXT_PRIMARY)
        title.pack(side="left")

        ref_btn = ctk.CTkButton(
            header,
            text="🔄 Odśwież listę",
            font=FONT_SMALL,
            fg_color="#1c2128",
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY,
            height=26,
            corner_radius=6,
            command=self._refresh_processes
        )
        ref_btn.pack(side="right")

        self.proc_container = ctk.CTkFrame(box, fg_color="transparent")
        self.proc_container.pack(fill="x", padx=16, pady=(0, 12))

        self._refresh_processes()

    def _refresh_processes(self):
        for child in self.proc_container.winfo_children():
            child.destroy()

        def worker():
            procs = get_top_processes(limit=5)
            self._safe_after(0, lambda: self._render_processes(procs))

        threading.Thread(target=worker, daemon=True).start()

    def _render_processes(self, procs: list[dict]):
        for child in self.proc_container.winfo_children():
            child.destroy()

        if not procs:
            lbl = ctk.CTkLabel(self.proc_container, text="Brak aktywnych procesów przekraczających próg RAM.", font=FONT_SMALL, text_color=TEXT_MUTED)
            lbl.pack(anchor="w", pady=4)
            return

        for p in procs:
            row = ctk.CTkFrame(self.proc_container, fg_color="#161b22", corner_radius=8)
            row.pack(fill="x", pady=2)
            row.grid_columnconfigure(0, weight=1)
            row.grid_columnconfigure(1, weight=0)
            row.grid_columnconfigure(2, weight=0)

            # Name and PID
            info_f = ctk.CTkFrame(row, fg_color="transparent")
            info_f.grid(row=0, column=0, sticky="w", padx=12, pady=6)

            name_lbl = ctk.CTkLabel(info_f, text=p["name"], font=FONT_BODY_BOLD, text_color=TEXT_PRIMARY)
            name_lbl.pack(side="left")

            pid_lbl = ctk.CTkLabel(info_f, text=f" (PID: {p['pid']})", font=FONT_SMALL, text_color=TEXT_MUTED)
            pid_lbl.pack(side="left", padx=4)

            # RAM Badge
            ram_badge = ctk.CTkLabel(
                row,
                text=f" {p['memory_mb']} MB RAM ",
                font=("Segoe UI", 10, "bold"),
                fg_color="#21262d",
                text_color=ACCENT_CYAN,
                corner_radius=4
            )
            ram_badge.grid(row=0, column=1, sticky="e", padx=8, pady=6)

            # Kill Button
            kill_btn = ctk.CTkButton(
                row,
                text="🛑 Zakończ",
                font=FONT_SMALL,
                fg_color="#374151",
                hover_color=ACCENT_RED,
                text_color="#ffffff",
                height=26,
                corner_radius=6,
                command=lambda pid=p["pid"]: self._handle_kill_proc(pid)
            )
            kill_btn.grid(row=0, column=2, sticky="e", padx=(0, 12), pady=6)

    def _handle_kill_proc(self, pid: int):
        ok, msg = kill_process(pid)
        if self.show_toast:
            self.show_toast(msg)
        self._safe_after(500, self._refresh_processes)

    def _build_safety_center(self):
        box = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        box.pack(fill="x", padx=20, pady=(0, 12))

        header = ctk.CTkFrame(box, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 6))

        title = ctk.CTkLabel(header, text="🛡️ Centrum Bezpieczeństwa & Przywracanie (Rollback)", font=FONT_SUBHEADING, text_color=TEXT_PRIMARY)
        title.pack(side="left")

        desc = ctk.CTkLabel(
            box,
            text="Wszystkie modyfikacje rejestru posiadają automatyczną kopię zapasową w pliku JSON. Możesz jednym kliknięciem cofnąć wszelkie wprowadzone zmiany.",
            font=FONT_SMALL,
            text_color=TEXT_SECONDARY,
            wraplength=640,
            justify="left"
        )
        desc.pack(anchor="w", padx=16, pady=(0, 12))

        btn_row = ctk.CTkFrame(box, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(0, 14))

        self.rollback_btn = ctk.CTkButton(
            btn_row,
            text="🔄 COFNIJ WSZYSTKIE ZMIANY REJESTRU",
            font=FONT_BODY_BOLD,
            fg_color="#374151",
            hover_color=ACCENT_PURPLE,
            text_color="#ffffff",
            height=36,
            corner_radius=8,
            command=self._run_rollback_all
        )
        self.rollback_btn.pack(side="left", padx=(0, 10))

        self.restore_btn = ctk.CTkButton(
            btn_row,
            text="🛡️ Utwórz Punkt Przywracania",
            font=FONT_BODY,
            fg_color="#2b313a",
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY,
            height=36,
            corner_radius=8,
            command=self._run_restore_point
        )
        self.restore_btn.pack(side="left", padx=(0, 10))

        self.expl_btn = ctk.CTkButton(
            btn_row,
            text="🔄 Restart Eksploratora",
            font=FONT_BODY,
            fg_color="#2b313a",
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY,
            height=36,
            corner_radius=8,
            command=restart_explorer
        )
        self.expl_btn.pack(side="left")

    def _run_rollback_all(self):
        if self.show_toast:
            self.show_toast("Przywracanie oryginalnych kluczy rejestru z kopii zapasowej...")

        def worker():
            succ, tot = restore_all_settings()
            msg = f"✓ Pomyślnie cofnięto {succ} z {tot} zmodyfikowanych ustawień rejestru!"
            if self.show_toast:
                self._safe_after(0, lambda: self.show_toast(msg))

        threading.Thread(target=worker, daemon=True).start()

    def _build_specs(self):
        specs_box = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        specs_box.pack(fill="x", padx=20, pady=(0, 20))

        lbl = ctk.CTkLabel(specs_box, text="Specyfikacja Komputera", font=FONT_SUBHEADING, text_color=TEXT_PRIMARY)
        lbl.pack(anchor="w", padx=16, pady=(12, 8))

        specs = get_system_specs()
        items = [
            ("System operacyjny:", specs["os"]),
            ("Procesor (CPU):", specs["cpu"]),
            ("Karta graficzna (GPU):", specs["gpu"]),
            ("Pamięć fizyczna (RAM):", f"{specs['ram_total_gb']} GB"),
            ("Pojemność dysku systemowego:", f"{specs['disk_c_total_gb']} GB (Wolne: {specs['disk_c_free_gb']} GB)")
        ]

        for k, v in items:
            row = ctk.CTkFrame(specs_box, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=2)
            k_lbl = ctk.CTkLabel(row, text=k, font=FONT_BODY_BOLD, text_color=TEXT_SECONDARY, width=200, anchor="w")
            k_lbl.pack(side="left")
            v_lbl = ctk.CTkLabel(row, text=str(v), font=FONT_BODY, text_color=TEXT_PRIMARY, anchor="w")
            v_lbl.pack(side="left")

        ctk.CTkFrame(specs_box, fg_color="transparent", height=8).pack()

    def _start_metrics_loop(self):
        def update():
            if not self.is_monitoring:
                return
            try:
                m = get_realtime_metrics()
                # CPU
                cpu_p = m["cpu_percent"]
                cpu_col = ACCENT_GREEN if cpu_p < 60 else (ACCENT_ORANGE if cpu_p < 85 else ACCENT_RED)
                self.cpu_card.update_metric(f"{cpu_p:.0f} %", f"Aktywne obciążenie", cpu_p / 100, cpu_col)

                # RAM
                ram_p = m["ram_percent"]
                ram_col = ACCENT_GREEN if ram_p < 70 else (ACCENT_ORANGE if ram_p < 85 else ACCENT_RED)
                self.ram_card.update_metric(f"{ram_p:.0f} %", f"{m['ram_used_gb']} GB używane / {m['ram_free_gb']} GB wolne", ram_p / 100, ram_col)

                # Disk
                disk_p = m["disk_c_percent"]
                disk_col = ACCENT_CYAN if disk_p < 80 else ACCENT_RED
                self.disk_card.update_metric(f"{disk_p:.0f} %", f"Wolne: {m['disk_c_free_gb']} GB", disk_p / 100, disk_col)
            except Exception:
                pass

            self._safe_after(2000, update)

        self._safe_after(500, update)

    def _run_ram_clean(self):
        self.ram_btn.configure(state="disabled", text="Czyszczenie...")
        def worker():
            before, after, freed = clean_ram()
            msg = f"✓ Zwolniono {freed} MB pamięci RAM!"
            self._safe_after(0, lambda: self._finish_ram_clean(msg))
        threading.Thread(target=worker, daemon=True).start()

    def _finish_ram_clean(self, msg: str):
        self.ram_btn.configure(state="normal", text="💾 Zwolnij RAM")
        self.status_lbl.configure(text=msg, text_color=ACCENT_GREEN)
        if self.show_toast:
            self.show_toast(msg)
        self._refresh_processes()

    def _run_restore_point(self):
        self.restore_btn.configure(state="disabled", text="Tworzenie punktu...")
        self.status_lbl.configure(text="Tworzenie punktu przywracania systemu Windows (może zająć chwilę)...", text_color=ACCENT_CYAN)
        def worker():
            ok, msg = create_restore_point()
            self._safe_after(0, lambda: self._finish_restore_point(ok, msg))
        threading.Thread(target=worker, daemon=True).start()

    def _finish_restore_point(self, ok: bool, msg: str):
        self.restore_btn.configure(state="normal", text="🛡️ Utwórz Punkt Przywracania")
        color = ACCENT_GREEN if ok else ACCENT_RED
        self.status_lbl.configure(text=msg, text_color=color)
        if self.show_toast:
            self.show_toast(msg)

    def _run_one_click_boost(self):
        self.boost_btn.configure(state="disabled", text="⚡ OPTYMALIZOWANIE...")
        self.status_lbl.configure(text="Aplikowanie optymalizacji gier, czyszczenie RAM i plików tymczasowych...", text_color=ACCENT_CYAN)

        def worker():
            set_gamedvr_disabled(True)
            set_game_mode_enabled(True)
            set_power_plan(True)
            set_network_throttling_disabled(True)
            before, after, freed_ram = clean_ram()
            freed_bytes, _ = clean_targets(["user_temp", "shader_cache", "crash_dumps", "discord_cache", "spotify_cache"])

            freed_mb_disk = int(freed_bytes / (1024 * 1024))
            msg = f"🚀 Sukces! Włączono Tryb Gry, Najwyższą Wydajność, zwolniono {freed_ram} MB RAM i {freed_mb_disk} MB na dysku!"
            self._safe_after(0, lambda: self._finish_boost(msg))

        threading.Thread(target=worker, daemon=True).start()

    def _finish_boost(self, msg: str):
        self.boost_btn.configure(state="normal", text="🚀 URUCHOM 1-CLICK GAME BOOST")
        self.status_lbl.configure(text=msg, text_color=ACCENT_GREEN)
        if self.show_toast:
            self.show_toast(msg)
        self._refresh_processes()
