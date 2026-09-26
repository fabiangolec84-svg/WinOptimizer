import customtkinter as ctk
import threading
from ui.theme import *
from ui.components.toggle_card import ToggleCard
from tweaks.gaming_tweaks import (
    get_gaming_tweaks_list,
    flush_dns,
    restart_explorer
)

class GamingPage(ctk.CTkScrollableFrame):
    def __init__(self, master, show_toast_callback=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.show_toast = show_toast_callback
        self.toggle_cards = {}

        self._build_header()
        self._build_action_bar()
        self._build_tweaks_list()

    def _safe_after(self, delay_ms: int, callback):
        try:
            if self.winfo_exists():
                self.after(delay_ms, callback)
        except Exception:
            pass

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 12))

        title = ctk.CTkLabel(header, text="Optymalizacja Gier & FPS 2.0 (Gaming Suite)", font=FONT_HEADING, text_color=TEXT_PRIMARY)
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header,
            text="Kompletny pakiet optymalizacji gier: eliminacja stutteringu, redukcja input laga, naprawa MPO GPU, priorytety MMCSS oraz klasyczne menu Windows 11.",
            font=FONT_BODY,
            text_color=TEXT_SECONDARY
        )
        subtitle.pack(anchor="w", pady=(2, 0))

    def _build_action_bar(self):
        bar = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        bar.pack(fill="x", padx=20, pady=(0, 12))

        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)

        all_btn = ctk.CTkButton(
            inner,
            text="⚡ WŁĄCZ WSZYSTKIE TWEAKI FPS",
            font=FONT_BODY_BOLD,
            fg_color=ACCENT_GREEN,
            hover_color=ACCENT_GREEN_HOVER,
            text_color="#ffffff",
            height=36,
            corner_radius=8,
            command=self._enable_all_gaming
        )
        all_btn.pack(side="left", padx=(0, 10))

        restore_def_btn = ctk.CTkButton(
            inner,
            text="🔄 Przywróć domyślne",
            font=FONT_BODY,
            fg_color="#2b313a",
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY,
            height=36,
            corner_radius=8,
            command=self._restore_defaults
        )
        restore_def_btn.pack(side="left", padx=(0, 10))

        dns_btn = ctk.CTkButton(
            inner,
            text="🌐 Flush DNS",
            font=FONT_BODY,
            fg_color="#2b313a",
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY,
            height=36,
            corner_radius=8,
            command=self._flush_dns_action
        )
        dns_btn.pack(side="left", padx=(0, 10))

        expl_btn = ctk.CTkButton(
            inner,
            text="🔄 Restart Eksploratora",
            font=FONT_BODY,
            fg_color="#2b313a",
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_PRIMARY,
            height=36,
            corner_radius=8,
            command=self._restart_explorer_action
        )
        expl_btn.pack(side="left")

    def _build_tweaks_list(self):
        tweaks = get_gaming_tweaks_list()

        for tweak in tweaks:
            card = ToggleCard(
                self,
                title=tweak["name"],
                description=tweak["desc"],
                tag=tweak.get("tag", "Gaming"),
                initial_state=tweak["is_active"],
                on_toggle=lambda val, t=tweak: self._on_tweak_toggle(t, val)
            )
            card.pack(fill="x", padx=20, pady=(0, 8))
            self.toggle_cards[tweak["id"]] = card

        ctk.CTkFrame(self, fg_color="transparent", height=12).pack()

    def _on_tweak_toggle(self, tweak: dict, new_val: bool):
        def worker():
            ok, msg = tweak["setter"](new_val)
            if self.show_toast:
                self._safe_after(0, lambda: self.show_toast(msg))
            self._safe_after(500, self._refresh_all_cards)
        threading.Thread(target=worker, daemon=True).start()

    def _flush_dns_action(self):
        ok, msg = flush_dns()
        if self.show_toast:
            self.show_toast(msg)

    def _restart_explorer_action(self):
        ok, msg = restart_explorer()
        if self.show_toast:
            self.show_toast(msg)

    def _enable_all_gaming(self):
        if self.show_toast:
            self.show_toast("Aplikowanie wszystkich optymalizacji gamingowych...")

        def worker():
            tweaks = get_gaming_tweaks_list()
            for t in tweaks:
                try:
                    t["setter"](True)
                except Exception:
                    pass
            self._safe_after(500, self._refresh_all_cards)
            if self.show_toast:
                self._safe_after(0, lambda: self.show_toast("✓ Zastosowano kompletny pakiet optymalizacji gier!"))

        threading.Thread(target=worker, daemon=True).start()

    def _restore_defaults(self):
        if self.show_toast:
            self.show_toast("Przywracanie domyślnych ustawień Windows...")

        def worker():
            tweaks = get_gaming_tweaks_list()
            for t in tweaks:
                try:
                    t["setter"](False)
                except Exception:
                    pass
            self._safe_after(500, self._refresh_all_cards)
            if self.show_toast:
                self._safe_after(0, lambda: self.show_toast("✓ Przywrócono domyślne ustawienia systemowe."))

        threading.Thread(target=worker, daemon=True).start()

    def _refresh_all_cards(self):
        tweaks = get_gaming_tweaks_list()
        for t in tweaks:
            if t["id"] in self.toggle_cards:
                self.toggle_cards[t["id"]].set_state(t["is_active"])
