import customtkinter as ctk
import threading
from ui.theme import *
from tweaks.game_profiles import GAME_PROFILES, clean_fivem_cache

class GameProfilesPage(ctk.CTkScrollableFrame):
    def __init__(self, master, show_toast_callback=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.show_toast = show_toast_callback

        self._build_header()
        self._build_profiles()

    def _safe_after(self, delay_ms: int, callback):
        try:
            if self.winfo_exists():
                self.after(delay_ms, callback)
        except Exception:
            pass

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 12))

        title = ctk.CTkLabel(header, text="Profile Gier & Optymalizacja Tytułów (Game Profiles)", font=FONT_HEADING, text_color=TEXT_PRIMARY)
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header,
            text="Gotowe parametry startowe (Launch Options), czyszczenie specyficznych pamięci podręcznych i sprawdzone porady dla najpopularniejszych gier.",
            font=FONT_BODY,
            text_color=TEXT_SECONDARY
        )
        subtitle.pack(anchor="w", pady=(2, 0))

    def _build_profiles(self):
        for profile in GAME_PROFILES:
            card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
            card.pack(fill="x", padx=20, pady=(0, 10))

            header_f = ctk.CTkFrame(card, fg_color="transparent")
            header_f.pack(fill="x", padx=16, pady=(12, 6))

            title_lbl = ctk.CTkLabel(
                header_f,
                text=f"{profile['icon']}  {profile['name']}",
                font=FONT_SUBHEADING,
                text_color=TEXT_PRIMARY
            )
            title_lbl.pack(side="left")

            desc_lbl = ctk.CTkLabel(card, text=profile["description"], font=FONT_SMALL, text_color=TEXT_SECONDARY)
            desc_lbl.pack(anchor="w", padx=16, pady=(0, 8))

            # Launch args or special action
            if "launch_args" in profile:
                args_box = ctk.CTkFrame(card, fg_color="#161b22", corner_radius=8)
                args_box.pack(fill="x", padx=16, pady=(0, 8))
                args_box.grid_columnconfigure(0, weight=1)
                args_box.grid_columnconfigure(1, weight=0)

                arg_entry = ctk.CTkEntry(
                    args_box,
                    font=FONT_MONO,
                    fg_color="transparent",
                    border_width=0,
                    text_color=ACCENT_CYAN,
                    height=32
                )
                arg_entry.insert(0, profile["launch_args"])
                arg_entry.configure(state="readonly")
                arg_entry.grid(row=0, column=0, sticky="ew", padx=8, pady=4)

                copy_btn = ctk.CTkButton(
                    args_box,
                    text="📋 Kopiuj",
                    font=FONT_SMALL,
                    fg_color="#2b313a",
                    hover_color=BG_CARD_HOVER,
                    text_color=TEXT_PRIMARY,
                    width=75,
                    height=28,
                    corner_radius=6,
                    command=lambda a=profile["launch_args"]: self._copy_to_clipboard(a)
                )
                copy_btn.grid(row=0, column=1, sticky="e", padx=8, pady=4)

            if "special_action" in profile:
                act_row = ctk.CTkFrame(card, fg_color="transparent")
                act_row.pack(fill="x", padx=16, pady=(0, 8))

                act_btn = ctk.CTkButton(
                    act_row,
                    text=profile["action_label"],
                    font=FONT_BODY_BOLD,
                    fg_color=ACCENT_PURPLE,
                    hover_color="#9333ea",
                    text_color="#ffffff",
                    height=32,
                    corner_radius=6,
                    command=self._clean_fivem
                )
                act_btn.pack(side="left")

            # Pro tip line
            tip_box = ctk.CTkFrame(card, fg_color="#1c2128", corner_radius=6)
            tip_box.pack(fill="x", padx=16, pady=(0, 12))

            tip_lbl = ctk.CTkLabel(
                tip_box,
                text=f"💡 Pro Tip: {profile['tips']}",
                font=("Segoe UI", 10),
                text_color=TEXT_MUTED,
                wraplength=640,
                justify="left"
            )
            tip_lbl.pack(anchor="w", padx=10, pady=6)

    def _copy_to_clipboard(self, text: str):
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
            if self.show_toast:
                self.show_toast("✓ Skopiowano parametry startowe do schowka!")
        except Exception as e:
            if self.show_toast:
                self.show_toast(f"Błąd schowka: {e}")

    def _clean_fivem(self):
        if self.show_toast:
            self.show_toast("Czyszczenie pamięci podręcznej FiveM...")

        def worker():
            ok, msg = clean_fivem_cache()
            if self.show_toast:
                self._safe_after(0, lambda: self.show_toast(msg))

        threading.Thread(target=worker, daemon=True).start()
