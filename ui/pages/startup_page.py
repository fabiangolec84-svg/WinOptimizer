import customtkinter as ctk
import threading
from ui.theme import *
from tweaks.startup_manager import get_startup_apps, toggle_startup_app, toggle_all_startup_apps

class StartupPage(ctk.CTkScrollableFrame):
    def __init__(self, master, show_toast_callback=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.show_toast = show_toast_callback

        self.apps = []
        self.search_filter = ""
        self.switch_vars = {}

        self._build_header()
        self._build_action_bar()

        self.list_container = ctk.CTkFrame(self, fg_color="transparent")
        self.list_container.pack(fill="x", padx=20, pady=(0, 20))

        self._refresh_list()

    def _safe_after(self, delay_ms: int, callback):
        try:
            if self.winfo_exists():
                self.after(delay_ms, callback)
        except Exception:
            pass

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 12))

        title = ctk.CTkLabel(header, text="Menedżer Autostartu 2.0 (Startup Apps)", font=FONT_HEADING, text_color=TEXT_PRIMARY)
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header,
            text="Włączaj i wyłączaj programy startujące z Windows (rejestr 64/32-bit oraz foldery autostartu). Wyłączenie zbędnych aplikacji przyspiesza start o kilkadziesiąt procent.",
            font=FONT_BODY,
            text_color=TEXT_SECONDARY
        )
        subtitle.pack(anchor="w", pady=(2, 0))

    def _build_action_bar(self):
        bar = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        bar.pack(fill="x", padx=20, pady=(0, 12))

        # Row 1: Action Buttons
        btn_row = ctk.CTkFrame(bar, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(12, 8))

        disable_all_btn = ctk.CTkButton(
            btn_row,
            text="⚡ WYŁĄCZ WSZYSTKIE ZBĘDNE",
            font=FONT_BODY_BOLD,
            fg_color="#b91c1c",
            hover_color="#991b1b",
            text_color="#ffffff",
            height=36,
            corner_radius=8,
            command=self._disable_all_unneeded
        )
        disable_all_btn.pack(side="left", padx=(0, 10))

        enable_all_btn = ctk.CTkButton(
            btn_row,
            text="🔄 Włącz wszystkie",
            font=FONT_BODY,
            fg_color="#2b313a",
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY,
            height=36,
            corner_radius=8,
            command=self._enable_all
        )
        enable_all_btn.pack(side="left", padx=(0, 10))

        ref_btn = ctk.CTkButton(
            btn_row,
            text="🔍 Odśwież",
            font=FONT_BODY,
            fg_color="#2b313a",
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY,
            height=36,
            corner_radius=8,
            command=self._refresh_list
        )
        ref_btn.pack(side="left")

        self.stats_lbl = ctk.CTkLabel(btn_row, text="", font=FONT_BODY_BOLD, text_color=ACCENT_CYAN)
        self.stats_lbl.pack(side="right")

        # Row 2: Search Input
        search_row = ctk.CTkFrame(bar, fg_color="transparent")
        search_row.pack(fill="x", padx=16, pady=(0, 12))

        self.search_entry = ctk.CTkEntry(
            search_row,
            placeholder_text="Szukaj aplikacji (np. Discord, Steam, Spotify)...",
            font=FONT_BODY,
            height=34,
            corner_radius=6,
            fg_color="#0d1117",
            border_color=BORDER_COLOR
        )
        self.search_entry.pack(fill="x")
        self.search_entry.bind("<KeyRelease>", self._on_search_change)

    def _on_search_change(self, event=None):
        self.search_filter = self.search_entry.get().strip().lower()
        self._render_apps_list()

    def _refresh_list(self):
        for child in self.list_container.winfo_children():
            child.destroy()

        loading_lbl = ctk.CTkLabel(self.list_container, text="Skanowanie rejestru i folderów autostartu...", font=FONT_BODY, text_color=ACCENT_CYAN)
        loading_lbl.pack(anchor="w", pady=10)

        def worker():
            apps = get_startup_apps()
            self._safe_after(0, lambda: self._on_apps_loaded(apps))

        threading.Thread(target=worker, daemon=True).start()

    def _on_apps_loaded(self, apps: list[dict]):
        self.apps = apps
        enabled_count = sum(1 for a in apps if a["enabled"])
        self.stats_lbl.configure(text=f"Wszystkich: {len(apps)} (Aktywne: {enabled_count})")
        self._render_apps_list()

    def _render_apps_list(self):
        for child in self.list_container.winfo_children():
            child.destroy()

        filtered = [
            a for a in self.apps
            if not self.search_filter or self.search_filter in a["name"].lower() or self.search_filter in a["command"].lower()
        ]

        if not filtered:
            empty_lbl = ctk.CTkLabel(self.list_container, text="Brak pasujących aplikacji.", font=FONT_BODY, text_color=TEXT_MUTED)
            empty_lbl.pack(anchor="w", pady=20)
            return

        for app in filtered:
            card = ctk.CTkFrame(self.list_container, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
            card.pack(fill="x", pady=4)
            card.grid_columnconfigure(0, weight=1)
            card.grid_columnconfigure(1, weight=0)

            # Left Info Container
            info_f = ctk.CTkFrame(card, fg_color="transparent")
            info_f.grid(row=0, column=0, sticky="w", padx=16, pady=12)

            header_line = ctk.CTkFrame(info_f, fg_color="transparent")
            header_line.pack(anchor="w")

            name_lbl = ctk.CTkLabel(header_line, text=app["name"], font=FONT_BODY_BOLD, text_color=TEXT_PRIMARY)
            name_lbl.pack(side="left")

            # Source Tag
            src_lbl = ctk.CTkLabel(
                header_line,
                text=f" {app['source']} ",
                font=("Segoe UI", 9, "bold"),
                fg_color="#1c2128",
                text_color=TEXT_MUTED,
                corner_radius=4
            )
            src_lbl.pack(side="left", padx=(8, 4))

            # Impact Badge
            imp = app["impact"]
            imp_col = ACCENT_RED if imp == "Wysoki" else (ACCENT_ORANGE if imp == "Średni" else ACCENT_GREEN)
            imp_lbl = ctk.CTkLabel(
                header_line,
                text=f" Wpływ: {imp} ",
                font=("Segoe UI", 9, "bold"),
                fg_color="#2b313a",
                text_color=imp_col,
                corner_radius=4
            )
            imp_lbl.pack(side="left", padx=4)

            # Command / Path
            cmd_lbl = ctk.CTkLabel(
                info_f,
                text=app["command"],
                font=FONT_SMALL,
                text_color=TEXT_SECONDARY,
                wraplength=480,
                justify="left"
            )
            cmd_lbl.pack(anchor="w", pady=(2, 0))

            # Recommendation hint
            rec_lbl = ctk.CTkLabel(info_f, text=app["recommendation"], font=("Segoe UI", 9), text_color=TEXT_MUTED)
            rec_lbl.pack(anchor="w", pady=(1, 0))

            # Right Switch Container
            sw_f = ctk.CTkFrame(card, fg_color="transparent")
            sw_f.grid(row=0, column=1, sticky="e", padx=16, pady=12)

            var = ctk.BooleanVar(value=app["enabled"])
            self.switch_vars[app["id"]] = var

            switch = ctk.CTkSwitch(
                sw_f,
                text="Włączony" if app["enabled"] else "Wyłączony",
                variable=var,
                font=FONT_SMALL,
                text_color=ACCENT_GREEN if app["enabled"] else TEXT_MUTED,
                progress_color=ACCENT_GREEN,
                button_color="#ffffff",
                button_hover_color="#e5e7eb",
                command=lambda a=app, v=var, sw=None: self._on_switch_toggle(a, v)
            )
            # Store reference to update text dynamically
            switch.configure(command=lambda a=app, v=var, s=switch: self._on_switch_toggle(a, v, s))
            switch.pack(side="right")

    def _on_switch_toggle(self, app: dict, var: ctk.BooleanVar, switch_widget=None):
        new_state = var.get()
        if switch_widget:
            switch_widget.configure(
                text="Włączony" if new_state else "Wyłączony",
                text_color=ACCENT_GREEN if new_state else TEXT_MUTED
            )

        def worker():
            ok, msg = toggle_startup_app(app, new_state)
            app["enabled"] = new_state
            if self.show_toast:
                self._safe_after(0, lambda: self.show_toast(msg))
            # Refresh count
            enabled_count = sum(1 for a in self.apps if a["enabled"])
            self._safe_after(0, lambda: self.stats_lbl.configure(text=f"Wszystkich: {len(self.apps)} (Aktywne: {enabled_count})"))

        threading.Thread(target=worker, daemon=True).start()

    def _disable_all_unneeded(self):
        if self.show_toast:
            self.show_toast("Wyłączanie zbędnych aplikacji autostartu...")

        def worker():
            succ, tot = toggle_all_startup_apps(False)
            msg = f"✓ Wyłączono {succ} z {tot} zbędnych aplikacji autostartu!"
            if self.show_toast:
                self._safe_after(0, lambda: self.show_toast(msg))
            self._safe_after(500, self._refresh_list)

        threading.Thread(target=worker, daemon=True).start()

    def _enable_all(self):
        if self.show_toast:
            self.show_toast("Włączanie aplikacji autostartu...")

        def worker():
            succ, tot = toggle_all_startup_apps(True)
            msg = f"✓ Włączono {succ} aplikacji autostartu!"
            if self.show_toast:
                self._safe_after(0, lambda: self.show_toast(msg))
            self._safe_after(500, self._refresh_list)

        threading.Thread(target=worker, daemon=True).start()
