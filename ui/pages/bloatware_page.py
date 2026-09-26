import customtkinter as ctk
import threading
from ui.theme import *
from tweaks.bloatware_remover import get_installed_bloatware, uninstall_bloatware

class BloatwarePage(ctk.CTkScrollableFrame):
    def __init__(self, master, show_toast_callback=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.show_toast = show_toast_callback

        self._build_header()
        self._build_action_bar()

        self.list_container = ctk.CTkFrame(self, fg_color="transparent")
        self.list_container.pack(fill="x", padx=20, pady=(0, 20))

        self._refresh_list()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 12))

        title = ctk.CTkLabel(header, text="Usuwanie Zbędnych Aplikacji (Bloatware)", font=FONT_HEADING, text_color=TEXT_PRIMARY)
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(header, text="Bezpiecznie odinstaluj fabryczne programy Windows, które obciążają system i zużywają przestrzeń dyskową.",
                                font=FONT_BODY, text_color=TEXT_SECONDARY)
        subtitle.pack(anchor="w", pady=(2, 0))

    def _build_action_bar(self):
        bar = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        bar.pack(fill="x", padx=20, pady=(0, 12))

        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)

        ref_btn = ctk.CTkButton(
            inner,
            text="🔍 SKANUJ ZAINSTALOWANE",
            font=FONT_BODY_BOLD,
            fg_color="#2b313a",
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY,
            height=36,
            corner_radius=8,
            command=self._refresh_list
        )
        ref_btn.pack(side="left")

    def _safe_after(self, delay_ms: int, callback):
        try:
            if self.winfo_exists():
                self.after(delay_ms, callback)
        except Exception:
            pass

    def _refresh_list(self):
        for child in self.list_container.winfo_children():
            child.destroy()

        load_lbl = ctk.CTkLabel(self.list_container, text="Skanowanie aplikacji systemowych...", font=FONT_BODY, text_color=ACCENT_CYAN)
        load_lbl.pack(anchor="w", pady=10)

        def worker():
            apps = get_installed_bloatware()
            self._safe_after(0, lambda: self._render_apps(apps))

        threading.Thread(target=worker, daemon=True).start()

    def _render_apps(self, apps: list[dict]):
        for child in self.list_container.winfo_children():
            child.destroy()

        for app in apps:
            card = ctk.CTkFrame(self.list_container, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
            card.pack(fill="x", pady=4)
            card.grid_columnconfigure(0, weight=1)
            card.grid_columnconfigure(1, weight=0)

            info_f = ctk.CTkFrame(card, fg_color="transparent")
            info_f.grid(row=0, column=0, sticky="w", padx=16, pady=12)

            name_f = ctk.CTkFrame(info_f, fg_color="transparent")
            name_f.pack(anchor="w")

            name_lbl = ctk.CTkLabel(name_f, text=app["name"], font=FONT_BODY_BOLD, text_color=TEXT_PRIMARY)
            name_lbl.pack(side="left")

            is_inst = app.get("installed", False)
            stat_text = "Zainstalowana" if is_inst else "Niezainstalowana"
            stat_col = ACCENT_ORANGE if is_inst else TEXT_MUTED

            stat_lbl = ctk.CTkLabel(name_f, text=f" [{stat_text}] ", font=("Segoe UI", 9, "bold"), text_color=stat_col)
            stat_lbl.pack(side="left", padx=8)

            desc_lbl = ctk.CTkLabel(info_f, text=app["desc"], font=FONT_SMALL, text_color=TEXT_SECONDARY, wraplength=480, justify="left")
            desc_lbl.pack(anchor="w", pady=(2, 0))

            if is_inst:
                uninst_btn = ctk.CTkButton(
                    card,
                    text="🗑️ Odinstaluj",
                    font=FONT_SMALL,
                    fg_color="#374151",
                    hover_color=ACCENT_RED,
                    text_color="#ffffff",
                    height=32,
                    corner_radius=6,
                    command=lambda a=app: self._uninstall_app(a)
                )
                uninst_btn.grid(row=0, column=1, sticky="e", padx=16, pady=12)

    def _uninstall_app(self, app: dict):
        if self.show_toast:
            self.show_toast(f"Odinstalowywanie {app['name']}...")

        def worker():
            ok, msg = uninstall_bloatware(app["id"])
            if self.show_toast:
                self._safe_after(0, lambda: self.show_toast(msg))
            self._safe_after(1000, self._refresh_list)

        threading.Thread(target=worker, daemon=True).start()
