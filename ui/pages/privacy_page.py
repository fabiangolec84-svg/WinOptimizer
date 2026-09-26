import customtkinter as ctk
import threading
from ui.theme import *
from ui.components.toggle_card import ToggleCard
from tweaks.privacy_tweaks import (
    get_privacy_tweaks_list,
    set_telemetry_disabled,
    set_bing_search_disabled,
    set_cortana_disabled,
    set_ads_suggestions_disabled
)

class PrivacyPage(ctk.CTkScrollableFrame):
    def __init__(self, master, show_toast_callback=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.show_toast = show_toast_callback
        self.toggle_cards = {}

        self._build_header()
        self._build_action_bar()
        self._build_tweaks_list()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 12))

        title = ctk.CTkLabel(header, text="Prywatność & Usługi Systemowe (Debloat)", font=FONT_HEADING, text_color=TEXT_PRIMARY)
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(header, text="Wyłącz ukryte procesy szpiegujące, telemetrię diagnostyczną Microsoftu oraz reklamy wbudowane w Windows.",
                                font=FONT_BODY, text_color=TEXT_SECONDARY)
        subtitle.pack(anchor="w", pady=(2, 0))

    def _build_action_bar(self):
        bar = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        bar.pack(fill="x", padx=20, pady=(0, 12))

        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)

        all_btn = ctk.CTkButton(
            inner,
            text="🛡️ WYŁĄCZ CAŁĄ TELEMETRIĘ I REKLAMY",
            font=FONT_BODY_BOLD,
            fg_color=ACCENT_PURPLE,
            hover_color="#9333ea",
            text_color="#ffffff",
            height=36,
            corner_radius=8,
            command=self._disable_all_telemetry
        )
        all_btn.pack(side="left")

    def _build_tweaks_list(self):
        tweaks = get_privacy_tweaks_list()

        for tweak in tweaks:
            card = ToggleCard(
                self,
                title=tweak["name"],
                description=tweak["desc"],
                tag="Prywatność / CPU",
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
                self.after(0, lambda: self.show_toast(msg))
        threading.Thread(target=worker, daemon=True).start()

    def _disable_all_telemetry(self):
        def worker():
            set_telemetry_disabled(True)
            set_bing_search_disabled(True)
            set_cortana_disabled(True)
            set_ads_suggestions_disabled(True)
            self.after(0, self._refresh_all_cards)
            if self.show_toast:
                self.after(0, lambda: self.show_toast("✓ Zablokowano całą telemetrię i zbędne usługi w tle!"))

        threading.Thread(target=worker, daemon=True).start()

    def _refresh_all_cards(self):
        tweaks = get_privacy_tweaks_list()
        for t in tweaks:
            if t["id"] in self.toggle_cards:
                self.toggle_cards[t["id"]].set_state(t["is_active"])
