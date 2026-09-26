import customtkinter as ctk
import threading
import os
from ui.theme import *
from core.app_manager import get_installed_applications, uninstall_application, format_size
from core.file_hunter import (
    scan_all_large_files,
    delete_files,
    get_scan_locations,
    format_bytes,
    open_in_explorer
)

class StoragePage(ctk.CTkFrame):
    def __init__(self, master, show_toast_callback=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.show_toast = show_toast_callback

        self.current_subtab = "files"
        self.scan_stop_event = threading.Event()
        self.is_scanning = False

        # Data
        self.apps = []
        self.files = []
        self.file_checkbox_vars = {}

        self._build_header()
        self._build_subtab_selector()

        self.tab_container = ctk.CTkFrame(self, fg_color="transparent")
        self.tab_container.pack(fill="both", expand=True)

        self._show_tab("files")

    def _safe_after(self, delay_ms: int, callback):
        try:
            if self.winfo_exists():
                self.after(delay_ms, callback)
        except Exception:
            pass

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 8))

        title = ctk.CTkLabel(header, text="Menedżer Dysku, Plików & Aplikacji", font=FONT_HEADING, text_color=TEXT_PRIMARY)
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header,
            text="Skanuj cały dysk lub wybrane foldery w poszukiwaniu największych i zapomnianych plików (od największych do najmniejszych) oraz odinstalowuj programy.",
            font=FONT_BODY,
            text_color=TEXT_SECONDARY
        )
        subtitle.pack(anchor="w", pady=(2, 0))

    def _build_subtab_selector(self):
        nav_bar = ctk.CTkFrame(self, fg_color="transparent")
        nav_bar.pack(fill="x", padx=20, pady=(0, 10))

        self.btn_subtab_files = ctk.CTkButton(
            nav_bar,
            text="🔍 Skaner Największych & Zapomnianych Plików",
            font=FONT_BODY_BOLD,
            fg_color=BG_CARD,
            hover_color=BG_CARD_HOVER,
            text_color=ACCENT_CYAN,
            height=34,
            corner_radius=8,
            command=lambda: self._show_tab("files")
        )
        self.btn_subtab_files.pack(side="left", padx=(0, 8))

        self.btn_subtab_apps = ctk.CTkButton(
            nav_bar,
            text="🖥️ Zainstalowane Programy (App Uninstaller)",
            font=FONT_BODY_BOLD,
            fg_color="transparent",
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_SECONDARY,
            height=34,
            corner_radius=8,
            command=lambda: self._show_tab("apps")
        )
        self.btn_subtab_apps.pack(side="left")

    def _show_tab(self, tab_name: str):
        self.current_subtab = tab_name
        if tab_name == "files":
            self.btn_subtab_files.configure(fg_color=BG_CARD, text_color=ACCENT_CYAN)
            self.btn_subtab_apps.configure(fg_color="transparent", text_color=TEXT_SECONDARY)
            self._render_files_view()
        else:
            self.btn_subtab_files.configure(fg_color="transparent", text_color=TEXT_SECONDARY)
            self.btn_subtab_apps.configure(fg_color=BG_CARD, text_color=ACCENT_CYAN)
            self._render_apps_view()

    # =========================================================================
    # TAB 1: LARGE & OLD FILE SCANNER (Global Drive / Downloads / Profile)
    # =========================================================================
    def _render_files_view(self):
        for child in self.tab_container.winfo_children():
            child.destroy()

        control_box = ctk.CTkFrame(self.tab_container, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        control_box.pack(fill="x", padx=20, pady=(0, 10))

        # Row 1: Filters (Drive / Location, Min Size, Age, Category)
        r1 = ctk.CTkFrame(control_box, fg_color="transparent")
        r1.pack(fill="x", padx=16, pady=(12, 6))

        # Scan Scope / Drive
        self.locations_list = get_scan_locations()
        loc_names = [l["name"] for l in self.locations_list]

        ctk.CTkLabel(r1, text="Zakres:", font=FONT_SMALL, text_color=TEXT_MUTED).pack(side="left", padx=(0, 4))
        self.loc_var = ctk.StringVar(value=loc_names[0] if loc_names else "C:\\")
        self.loc_menu = ctk.CTkOptionMenu(
            r1,
            variable=self.loc_var,
            values=loc_names,
            font=FONT_SMALL,
            width=230,
            height=28,
            corner_radius=6,
            fg_color="#1c2128",
            button_color="#2b313a"
        )
        self.loc_menu.pack(side="left", padx=(0, 10))

        # Min Size Threshold
        ctk.CTkLabel(r1, text="Rozmiar min:", font=FONT_SMALL, text_color=TEXT_MUTED).pack(side="left", padx=(0, 4))
        self.size_var = ctk.StringVar(value="Od 100 MB")
        self.size_menu = ctk.CTkOptionMenu(
            r1,
            variable=self.size_var,
            values=[
                "Od 50 MB",
                "Od 100 MB",
                "Od 250 MB",
                "Od 500 MB",
                "Od 1 GB (Giganty)",
                "Od 2 GB",
                "Od 1 MB (Wszystkie)"
            ],
            font=FONT_SMALL,
            width=135,
            height=28,
            corner_radius=6,
            fg_color="#1c2128",
            button_color="#2b313a"
        )
        self.size_menu.pack(side="left", padx=(0, 10))

        # Age Filter (from 1 min / all to 1 year)
        ctk.CTkLabel(r1, text="Wiek:", font=FONT_SMALL, text_color=TEXT_MUTED).pack(side="left", padx=(0, 4))
        self.age_var = ctk.StringVar(value="Dowolny wiek (Wszystkie)")
        self.age_menu = ctk.CTkOptionMenu(
            r1,
            variable=self.age_var,
            values=[
                "Dowolny wiek (Wszystkie)",
                "Starsze niż 1 dzień",
                "Starsze niż 7 dni",
                "Starsze niż 30 dni",
                "Starsze niż 60 dni",
                "Starsze niż 90 dni",
                "Starsze niż 180 dni",
                "Starsze niż 1 rok"
            ],
            font=FONT_SMALL,
            width=165,
            height=28,
            corner_radius=6,
            fg_color="#1c2128",
            button_color="#2b313a"
        )
        self.age_menu.pack(side="left", padx=(0, 10))

        # Category Filter
        ctk.CTkLabel(r1, text="Typ:", font=FONT_SMALL, text_color=TEXT_MUTED).pack(side="left", padx=(0, 4))
        self.cat_var = ctk.StringVar(value="Wszystkie typy")
        self.cat_menu = ctk.CTkOptionMenu(
            r1,
            variable=self.cat_var,
            values=["Wszystkie typy", "Instalator", "Archiwum", "Obraz dysku", "Wideo / Media", "Dokument", "Wirtualizacja / Dane"],
            font=FONT_SMALL,
            width=135,
            height=28,
            corner_radius=6,
            fg_color="#1c2128",
            button_color="#2b313a"
        )
        self.cat_menu.pack(side="left")

        # Row 2: Action Buttons & Live Status
        r2 = ctk.CTkFrame(control_box, fg_color="transparent")
        r2.pack(fill="x", padx=16, pady=(0, 10))

        self.scan_btn = ctk.CTkButton(
            r2,
            text="🔍 SKANUJ DYSK (OD NAJWIĘKSZYCH)",
            font=("Segoe UI", 12, "bold"),
            fg_color=ACCENT_CYAN,
            hover_color=ACCENT_CYAN_HOVER,
            text_color="#000000",
            height=34,
            corner_radius=6,
            command=self._start_scan
        )
        self.scan_btn.pack(side="left", padx=(0, 8))

        self.stop_btn = ctk.CTkButton(
            r2,
            text="🛑 Zatrzymaj",
            font=FONT_SMALL,
            fg_color="#374151",
            hover_color=ACCENT_RED,
            text_color="#ffffff",
            height=34,
            corner_radius=6,
            state="disabled",
            command=self._stop_scan
        )
        self.stop_btn.pack(side="left", padx=(0, 12))

        self.del_btn = ctk.CTkButton(
            r2,
            text="🗑️ USUŃ ZAZNACZONE",
            font=("Segoe UI", 11, "bold"),
            fg_color=ACCENT_RED,
            hover_color="#dc2626",
            text_color="#ffffff",
            height=34,
            corner_radius=6,
            command=self._delete_selected_files
        )
        self.del_btn.pack(side="left", padx=(0, 12))

        btn_sel_all = ctk.CTkButton(
            r2,
            text="✅ Zaznacz",
            font=FONT_SMALL,
            fg_color="#1f2937",
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY,
            height=28,
            corner_radius=6,
            command=lambda: [v.set(True) for v in self.file_checkbox_vars.values()]
        )
        btn_sel_all.pack(side="left", padx=(0, 4))

        btn_desel_all = ctk.CTkButton(
            r2,
            text="❌ Odznacz",
            font=FONT_SMALL,
            fg_color="#1f2937",
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY,
            height=28,
            corner_radius=6,
            command=lambda: [v.set(False) for v in self.file_checkbox_vars.values()]
        )
        btn_desel_all.pack(side="left")

        self.file_summary_lbl = ctk.CTkLabel(r2, text="", font=FONT_BODY_BOLD, text_color=ACCENT_CYAN)
        self.file_summary_lbl.pack(side="right")

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(control_box, height=4, corner_radius=2, fg_color="#1c2128", progress_color=ACCENT_GREEN)
        self.progress_bar.set(0.0)
        self.progress_bar.pack(fill="x", padx=16, pady=(0, 10))

        # Scrollable container for file rows
        self.files_scroll = ctk.CTkScrollableFrame(self.tab_container, fg_color="transparent")
        self.files_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Run fast scan of profile on load
        self._start_scan()

    def _get_selected_target_dir(self) -> str:
        sel_name = self.loc_var.get()
        for loc in self.locations_list:
            if loc["name"] == sel_name:
                return loc["path"]
        return os.environ.get("USERPROFILE", "C:\\")

    def _get_min_size_mb(self) -> float:
        val = self.size_var.get()
        if "50 MB" in val:
            return 50.0
        elif "100 MB" in val:
            return 100.0
        elif "250 MB" in val:
            return 250.0
        elif "500 MB" in val:
            return 500.0
        elif "1 GB" in val:
            return 1024.0
        elif "2 GB" in val:
            return 2048.0
        return 1.0

    def _get_min_days_old(self) -> float:
        val = self.age_var.get()
        if "1 dzień" in val:
            return 1.0
        elif "7 dni" in val:
            return 7.0
        elif "30 dni" in val:
            return 30.0
        elif "60 dni" in val:
            return 60.0
        elif "90 dni" in val:
            return 90.0
        elif "180 dni" in val:
            return 180.0
        elif "1 rok" in val:
            return 365.0
        return 0.0

    def _start_scan(self):
        if self.is_scanning:
            return

        self.is_scanning = True
        self.scan_stop_event.clear()
        self.scan_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.progress_bar.set(0.0)

        for child in self.files_scroll.winfo_children():
            child.destroy()

        load_lbl = ctk.CTkLabel(self.files_scroll, text="Rozpoczynanie skanowania dysku w poszukiwaniu największych plików...", font=FONT_BODY, text_color=ACCENT_CYAN)
        load_lbl.pack(anchor="w", pady=10)

        target_dir = self._get_selected_target_dir()
        min_size = self._get_min_size_mb()
        min_days = self._get_min_days_old()
        cat_filter = self.cat_var.get()
        if cat_filter == "Wszystkie typy":
            cat_filter = "Wszystkie"

        def progress_cb(folders, files, found_count, curr_path):
            short_path = curr_path if len(curr_path) < 55 else "..." + curr_path[-52:]
            self._safe_after(0, lambda: self.file_summary_lbl.configure(text=f"Przeszukano {folders} folderów | Wykryto: {found_count}"))

        def worker():
            results = scan_all_large_files(
                target_dir=target_dir,
                min_size_mb=min_size,
                min_days_old=min_days,
                category_filter=cat_filter,
                progress_cb=progress_cb,
                stop_event=self.scan_stop_event
            )
            self._safe_after(0, lambda: self._on_scan_finished(results))

        threading.Thread(target=worker, daemon=True).start()

    def _stop_scan(self):
        self.scan_stop_event.set()
        self.stop_btn.configure(state="disabled")
        if self.show_toast:
            self.show_toast("Zatrzymywanie skanowania...")

    def _on_scan_finished(self, files: list[dict]):
        self.is_scanning = False
        self.scan_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.progress_bar.set(1.0)

        for child in self.files_scroll.winfo_children():
            child.destroy()

        self.files = files
        self.file_checkbox_vars.clear()

        if not files:
            empty_lbl = ctk.CTkLabel(self.files_scroll, text="Brak plików spełniających wybrane kryteria w wybranej lokalizacji.", font=FONT_BODY, text_color=TEXT_MUTED)
            empty_lbl.pack(anchor="w", pady=20)
            self.file_summary_lbl.configure(text="0 plików (0 MB)")
            return

        total_bytes = sum(f["size"] for f in files)
        self.file_summary_lbl.configure(text=f"Znaleziono: {len(files)} plików ({format_bytes(total_bytes)})")

        for f in files:
            row = ctk.CTkFrame(self.files_scroll, fg_color=BG_CARD, corner_radius=10, border_width=1, border_color=BORDER_COLOR)
            row.pack(fill="x", pady=3)
            row.grid_columnconfigure(0, weight=1)
            row.grid_columnconfigure(1, weight=0)
            row.grid_columnconfigure(2, weight=0)

            var = ctk.BooleanVar(value=False)
            self.file_checkbox_vars[f["path"]] = var

            # Left Container: Checkbox & Name
            left_f = ctk.CTkFrame(row, fg_color="transparent")
            left_f.grid(row=0, column=0, sticky="w", padx=10, pady=6)

            chk = ctk.CTkCheckBox(
                left_f,
                text=f["name"],
                variable=var,
                font=FONT_BODY_BOLD,
                text_color=TEXT_PRIMARY,
                checkbox_height=18,
                checkbox_width=18,
                corner_radius=4,
                fg_color=ACCENT_CYAN,
                hover_color=ACCENT_CYAN_HOVER
            )
            chk.pack(anchor="w")

            meta_lbl = ctk.CTkLabel(
                left_f,
                text=f"Typ: {f['category']}  •  Zmodyfikowano: {f['mod_date']} ({f['age_str']})  •  Ścieżka: {f['path']}",
                font=("Segoe UI", 9),
                text_color=TEXT_MUTED
            )
            meta_lbl.pack(anchor="w", padx=(26, 0), pady=(1, 0))

            # Open containing folder button
            open_btn = ctk.CTkButton(
                row,
                text="📂 Pokaż w folderze",
                font=FONT_SMALL,
                fg_color="#21262d",
                hover_color=BG_CARD_HOVER,
                text_color=TEXT_SECONDARY,
                height=28,
                corner_radius=6,
                command=lambda p=f["path"]: open_in_explorer(p)
            )
            open_btn.grid(row=0, column=1, sticky="e", padx=6)

            # Size badge
            is_huge = f["size"] >= (1024 * 1024 * 1024)
            size_color = ACCENT_ORANGE if is_huge else ACCENT_CYAN
            size_badge = ctk.CTkLabel(
                row,
                text=f" {f['size_str']} ",
                font=("Segoe UI", 11, "bold"),
                fg_color="#161b22",
                text_color=size_color,
                corner_radius=6,
                padx=8,
                pady=2
            )
            size_badge.grid(row=0, column=2, sticky="e", padx=10)

    def _delete_selected_files(self):
        to_delete = [p for p, v in self.file_checkbox_vars.items() if v.get()]
        if not to_delete:
            if self.show_toast:
                self.show_toast("Wybierz pliki do usunięcia zaznaczając checkboxy!")
            return

        def worker():
            freed, count = delete_files(to_delete)
            msg = f"✓ Usunięto {count} plików, zwalniając {format_bytes(freed)} miejsca!"
            if self.show_toast:
                self._safe_after(0, lambda: self.show_toast(msg))
            self._safe_after(500, self._start_scan)

        threading.Thread(target=worker, daemon=True).start()

    # =========================================================================
    # TAB 2: APP UNINSTALLER (Installed Desktop Programs)
    # =========================================================================
    def _render_apps_view(self):
        for child in self.tab_container.winfo_children():
            child.destroy()

        control_box = ctk.CTkFrame(self.tab_container, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        control_box.pack(fill="x", padx=20, pady=(0, 10))

        r1 = ctk.CTkFrame(control_box, fg_color="transparent")
        r1.pack(fill="x", padx=16, pady=12)

        # Search bar
        self.app_search_entry = ctk.CTkEntry(
            r1,
            placeholder_text="Szukaj zainstalowanego programu...",
            font=FONT_BODY,
            height=32,
            corner_radius=6,
            fg_color="#0d1117",
            border_color=BORDER_COLOR
        )
        self.app_search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.app_search_entry.bind("<KeyRelease>", self._on_app_search)

        # Filter option
        self.app_filter_var = ctk.StringVar(value="Wszystkie")
        f_menu = ctk.CTkOptionMenu(
            r1,
            variable=self.app_filter_var,
            values=["Wszystkie", "Duże (> 1 GB)", "Średnie (> 200 MB)", "Starsze (> 3 mies.)"],
            font=FONT_SMALL,
            width=150,
            height=32,
            corner_radius=6,
            fg_color="#1c2128",
            button_color="#2b313a",
            command=lambda _: self._render_app_list()
        )
        f_menu.pack(side="left", padx=(0, 10))

        ref_btn = ctk.CTkButton(
            r1,
            text="🔄 Odśwież",
            font=FONT_BODY,
            fg_color="#2b313a",
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY,
            height=32,
            corner_radius=6,
            command=self._load_apps
        )
        ref_btn.pack(side="left")

        self.apps_scroll = ctk.CTkScrollableFrame(self.tab_container, fg_color="transparent")
        self.apps_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        self._load_apps()

    def _on_app_search(self, event=None):
        self._render_app_list()

    def _load_apps(self):
        for child in self.apps_scroll.winfo_children():
            child.destroy()

        load_lbl = ctk.CTkLabel(self.apps_scroll, text="Wyszukiwanie zainstalowanych aplikacji w rejestrze...", font=FONT_BODY, text_color=ACCENT_CYAN)
        load_lbl.pack(anchor="w", pady=10)

        def worker():
            apps = get_installed_applications()
            self._safe_after(0, lambda: self._on_apps_loaded(apps))

        threading.Thread(target=worker, daemon=True).start()

    def _on_apps_loaded(self, apps: list[dict]):
        self.apps = apps
        self._render_app_list()

    def _render_app_list(self):
        for child in self.apps_scroll.winfo_children():
            child.destroy()

        search_txt = self.app_search_entry.get().strip().lower() if hasattr(self, 'app_search_entry') else ""
        filt = self.app_filter_var.get() if hasattr(self, 'app_filter_var') else "Wszystkie"

        filtered = []
        for a in self.apps:
            if search_txt and search_txt not in a["name"].lower() and search_txt not in a["publisher"].lower():
                continue
            if filt == "Duże (> 1 GB)" and a["size_mb"] < 1024:
                continue
            elif filt == "Średnie (> 200 MB)" and a["size_mb"] < 200:
                continue
            elif filt == "Starsze (> 3 mies.)" and a["days_ago"] < 90:
                continue
            filtered.append(a)

        if not filtered:
            lbl = ctk.CTkLabel(self.apps_scroll, text="Brak pasujących aplikacji.", font=FONT_BODY, text_color=TEXT_MUTED)
            lbl.pack(anchor="w", pady=20)
            return

        for app in filtered:
            card = ctk.CTkFrame(self.apps_scroll, fg_color=BG_CARD, corner_radius=10, border_width=1, border_color=BORDER_COLOR)
            card.pack(fill="x", pady=3)
            card.grid_columnconfigure(0, weight=1)
            card.grid_columnconfigure(1, weight=0)
            card.grid_columnconfigure(2, weight=0)

            # Left Info
            info_f = ctk.CTkFrame(card, fg_color="transparent")
            info_f.grid(row=0, column=0, sticky="w", padx=14, pady=10)

            name_lbl = ctk.CTkLabel(info_f, text=app["name"], font=FONT_BODY_BOLD, text_color=TEXT_PRIMARY)
            name_lbl.pack(anchor="w")

            meta_lbl = ctk.CTkLabel(
                info_f,
                text=f"{app['publisher']}  •  Wersja: {app['version'] or 'Brak'}  •  Zainstalowano: {app['install_date']}",
                font=("Segoe UI", 9),
                text_color=TEXT_MUTED
            )
            meta_lbl.pack(anchor="w", pady=(2, 0))

            # Size badge
            is_large = app["size_mb"] >= 1024
            size_col = ACCENT_ORANGE if is_large else ACCENT_CYAN
            size_badge = ctk.CTkLabel(
                card,
                text=f" {app['size_str']} ",
                font=("Segoe UI", 11, "bold"),
                fg_color="#1c2128",
                text_color=size_col,
                corner_radius=6,
                padx=8,
                pady=2
            )
            size_badge.grid(row=0, column=1, sticky="e", padx=10)

            # Uninstall button
            uninst_btn = ctk.CTkButton(
                card,
                text="🗑️ Odinstaluj",
                font=FONT_SMALL,
                fg_color="#374151",
                hover_color=ACCENT_RED,
                text_color="#ffffff",
                height=30,
                corner_radius=6,
                command=lambda cmd=app["uninstall_cmd"], name=app["name"]: self._handle_uninstall(cmd, name)
            )
            uninst_btn.grid(row=0, column=2, sticky="e", padx=12)

    def _handle_uninstall(self, cmd: str, name: str):
        if not cmd:
            if self.show_toast:
                self.show_toast(f"Brak polecenia deinstalacji dla: {name}")
            return

        if self.show_toast:
            self.show_toast(f"Uruchamianie deinstalatora {name}...")

        ok, msg = uninstall_application(cmd)
        if self.show_toast:
            self.show_toast(msg)
