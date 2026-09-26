import customtkinter as ctk
import threading
from ui.theme import *
from core.cleaner import (
    get_cleaner_targets,
    scan_targets,
    clean_targets,
    format_bytes,
    get_running_browsers,
    close_browsers
)

class CleanerPage(ctk.CTkScrollableFrame):
    def __init__(self, master, show_toast_callback=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.show_toast = show_toast_callback

        self.targets = get_cleaner_targets()
        self.checkbox_vars = {}
        self.size_labels = {}

        self._build_header()
        self._build_browser_banner()
        self._build_action_bar()
        self._build_categories()
        self._build_log_console()

        self._check_running_browsers()
        self._start_scan()

    def _safe_after(self, delay_ms: int, callback):
        try:
            if self.winfo_exists():
                self.after(delay_ms, callback)
        except Exception:
            pass

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 8))

        title = ctk.CTkLabel(header, text="Czyszczenie Śmieci & Cache 2.0", font=FONT_HEADING, text_color=TEXT_PRIMARY)
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header,
            text="Zaawansowane czyszczenie plików tymczasowych, cache DirectX shaderów GPU, pamięci Discord/Spotify/Steam, Delivery Optimization oraz kosza.",
            font=FONT_BODY,
            text_color=TEXT_SECONDARY
        )
        subtitle.pack(anchor="w", pady=(2, 0))

    def _build_browser_banner(self):
        self.browser_frame = ctk.CTkFrame(self, fg_color="#2b2314", corner_radius=10, border_width=1, border_color="#f59e0b")
        # Hidden by default, placed if browsers are running

        inner = ctk.CTkFrame(self.browser_frame, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=10)

        self.browser_lbl = ctk.CTkLabel(
            inner,
            text="⚠️ Wykryto otwarte przeglądarki.",
            font=FONT_BODY_BOLD,
            text_color="#fbbf24"
        )
        self.browser_lbl.pack(side="left")

        self.close_browser_btn = ctk.CTkButton(
            inner,
            text="🛑 Zamknij przeglądarki",
            font=FONT_SMALL,
            fg_color="#f59e0b",
            hover_color="#d97706",
            text_color="#000000",
            height=28,
            corner_radius=6,
            command=self._handle_close_browsers
        )
        self.close_browser_btn.pack(side="right")

    def _check_running_browsers(self):
        browsers = get_running_browsers()
        if browsers:
            b_list = ", ".join(browsers)
            self.browser_lbl.configure(text=f"⚠️ Otwarte przeglądarki ({b_list}). Mogą blokować czyszczenie plików cache.")
            self.browser_frame.pack(fill="x", padx=20, pady=(0, 10), before=self.action_bar)
        else:
            self.browser_frame.pack_forget()

    def _handle_close_browsers(self):
        closed = close_browsers()
        if self.show_toast:
            self.show_toast(f"Zamknięto {closed} procesów przeglądarek!")
        self.browser_frame.pack_forget()

    def _build_action_bar(self):
        self.action_bar = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        self.action_bar.pack(fill="x", padx=20, pady=(0, 12))

        # Row 1: Actions
        r1 = ctk.CTkFrame(self.action_bar, fg_color="transparent")
        r1.pack(fill="x", padx=16, pady=(12, 8))

        self.scan_btn = ctk.CTkButton(
            r1,
            text="🔍 SKANUJ DYSK",
            font=FONT_BODY_BOLD,
            fg_color="#2b313a",
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY,
            height=38,
            corner_radius=8,
            command=self._start_scan
        )
        self.scan_btn.pack(side="left", padx=(0, 10))

        self.clean_btn = ctk.CTkButton(
            r1,
            text="🧹 WYCZYŚĆ ZAZNACZONE",
            font=("Segoe UI", 12, "bold"),
            fg_color=ACCENT_CYAN,
            hover_color=ACCENT_CYAN_HOVER,
            text_color="#000000",
            height=38,
            corner_radius=8,
            command=self._start_clean
        )
        self.clean_btn.pack(side="left", padx=(0, 16))

        self.summary_lbl = ctk.CTkLabel(
            r1,
            text="Skanowanie w toku...",
            font=FONT_BODY_BOLD,
            text_color=ACCENT_CYAN
        )
        self.summary_lbl.pack(side="left")

        # Row 2: Selection Presets
        r2 = ctk.CTkFrame(self.action_bar, fg_color="transparent")
        r2.pack(fill="x", padx=16, pady=(0, 10))

        lbl_presets = ctk.CTkLabel(r2, text="Wybór:", font=FONT_SMALL, text_color=TEXT_MUTED)
        lbl_presets.pack(side="left", padx=(0, 8))

        btn_rec = ctk.CTkButton(
            r2,
            text="⭐ Tylko zalecane (bezpieczne)",
            font=FONT_SMALL,
            fg_color="#1f2937",
            hover_color=BG_CARD_HOVER,
            text_color=ACCENT_GREEN,
            height=26,
            corner_radius=6,
            command=self._select_recommended
        )
        btn_rec.pack(side="left", padx=(0, 6))

        btn_all = ctk.CTkButton(
            r2,
            text="✅ Zaznacz wszystko",
            font=FONT_SMALL,
            fg_color="#1f2937",
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY,
            height=26,
            corner_radius=6,
            command=self._select_all
        )
        btn_all.pack(side="left", padx=(0, 6))

        btn_none = ctk.CTkButton(
            r2,
            text="❌ Odznacz wszystko",
            font=FONT_SMALL,
            fg_color="#1f2937",
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY,
            height=26,
            corner_radius=6,
            command=self._select_none
        )
        btn_none.pack(side="left")

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.action_bar, height=6, corner_radius=3, fg_color="#1c2128", progress_color=ACCENT_GREEN)
        self.progress_bar.set(0.0)
        self.progress_bar.pack(fill="x", padx=16, pady=(0, 12))

    def _select_recommended(self):
        for k, info in self.targets.items():
            if k in self.checkbox_vars:
                self.checkbox_vars[k].set(info.get("recommended", True))

    def _select_all(self):
        for var in self.checkbox_vars.values():
            var.set(True)

    def _select_none(self):
        for var in self.checkbox_vars.values():
            var.set(False)

    def _build_categories(self):
        cat_box = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        cat_box.pack(fill="x", padx=20, pady=(0, 12))

        cat_title = ctk.CTkLabel(cat_box, text="Lokalizacje do wyczyszczenia", font=FONT_SUBHEADING, text_color=TEXT_PRIMARY)
        cat_title.pack(anchor="w", padx=16, pady=(12, 6))

        for key, info in self.targets.items():
            row = ctk.CTkFrame(cat_box, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=6)
            row.grid_columnconfigure(0, weight=1)
            row.grid_columnconfigure(1, weight=0)

            var = ctk.BooleanVar(value=info.get("default", True))
            self.checkbox_vars[key] = var

            chk = ctk.CTkCheckBox(
                row,
                text=info["name"],
                variable=var,
                font=FONT_BODY_BOLD,
                text_color=TEXT_PRIMARY,
                checkbox_height=20,
                checkbox_width=20,
                corner_radius=6,
                fg_color=ACCENT_CYAN,
                hover_color=ACCENT_CYAN_HOVER
            )
            chk.grid(row=0, column=0, sticky="w")

            desc = ctk.CTkLabel(row, text=info["desc"], font=FONT_SMALL, text_color=TEXT_MUTED)
            desc.grid(row=1, column=0, sticky="w", padx=(28, 0))

            size_badge = ctk.CTkLabel(
                row,
                text="Obliczanie...",
                font=("Segoe UI", 11, "bold"),
                fg_color="#1c2128",
                text_color=ACCENT_CYAN,
                corner_radius=6,
                padx=8,
                pady=2
            )
            size_badge.grid(row=0, column=1, rowspan=2, sticky="e")
            self.size_labels[key] = size_badge

        ctk.CTkFrame(cat_box, fg_color="transparent", height=8).pack()

    def _build_log_console(self):
        log_box = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        log_box.pack(fill="x", padx=20, pady=(0, 20))

        log_title = ctk.CTkLabel(log_box, text="Dziennik operacji (Live Log)", font=FONT_SUBHEADING, text_color=TEXT_PRIMARY)
        log_title.pack(anchor="w", padx=16, pady=(12, 6))

        self.textbox = ctk.CTkTextbox(log_box, height=120, fg_color="#0d1117", text_color=TEXT_SECONDARY, font=FONT_MONO, corner_radius=8)
        self.textbox.pack(fill="x", padx=16, pady=(0, 16))
        self.textbox.insert("end", "[WinOptimizer 2.0] Moduł czyszczenia gotowy.\n")

    def _log(self, text: str):
        self.textbox.insert("end", f"{text}\n")
        self.textbox.see("end")

    def _start_scan(self):
        self.scan_btn.configure(state="disabled")
        self.clean_btn.configure(state="disabled")
        self.summary_lbl.configure(text="Skanowanie w toku...")
        self.progress_bar.set(0.0)
        self._check_running_browsers()
        self._log("Rozpoczynanie skanowania dysku...")

        def worker():
            res = scan_targets()
            self._safe_after(0, lambda: self._finish_scan(res))

        threading.Thread(target=worker, daemon=True).start()

    def _finish_scan(self, res: dict):
        self.scan_btn.configure(state="normal")
        self.clean_btn.configure(state="normal")

        for key, data in res["categories"].items():
            if key in self.size_labels:
                lbl = self.size_labels[key]
                lbl.configure(text=f"{data['size_str']} ({data['files']} plików)")

        total_str = res["total_size_str"]
        total_files = res["total_files"]
        self.summary_lbl.configure(text=f"Do odzyskania: {total_str} ({total_files} plików)")
        self._log(f"Zakończono skanowanie. Wykryto {total_str} zbędnych danych w {total_files} plikach.")

    def _start_clean(self):
        selected = [k for k, v in self.checkbox_vars.items() if v.get()]
        if not selected:
            if self.show_toast:
                self.show_toast("Wybierz co najmniej jedną kategorię do wyczyszczenia!")
            return

        self.scan_btn.configure(state="disabled")
        self.clean_btn.configure(state="disabled")
        self.summary_lbl.configure(text="Trwa usuwanie plików...")
        self.progress_bar.set(0.0)

        def progress_cb(pct, status):
            self._safe_after(0, lambda: self.progress_bar.set(pct))
            self._safe_after(0, lambda: self.summary_lbl.configure(text=status))

        def log_cb(msg):
            self._safe_after(0, lambda: self._log(msg))

        def worker():
            freed, count = clean_targets(selected, progress_callback=progress_cb, log_callback=log_cb)
            self._safe_after(0, lambda: self._finish_clean(freed, count))

        threading.Thread(target=worker, daemon=True).start()

    def _finish_clean(self, freed: int, count: int):
        self.progress_bar.set(1.0)
        freed_str = format_bytes(freed)
        self.summary_lbl.configure(text=f"✓ Sukces! Zwolniono {freed_str}!")
        if self.show_toast:
            self.show_toast(f"Pomyślnie zwolniono {freed_str} miejsca na dysku!")

        self._safe_after(1000, self._start_scan)
