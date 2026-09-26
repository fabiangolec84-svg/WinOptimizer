import customtkinter as ctk
from ui.theme import *

class MetricCard(ctk.CTkFrame):
    def __init__(self, master, title: str, initial_value: str = "--", subtext: str = "", progress: float = 0.0, **kwargs):
        super().__init__(master, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COLOR, **kwargs)

        self.title_label = ctk.CTkLabel(self, text=title, font=FONT_BODY_BOLD, text_color=TEXT_SECONDARY)
        self.title_label.pack(anchor="w", padx=16, pady=(12, 4))

        self.value_label = ctk.CTkLabel(self, text=initial_value, font=("Segoe UI", 24, "bold"), text_color=TEXT_PRIMARY)
        self.value_label.pack(anchor="w", padx=16, pady=(0, 4))

        self.progress_bar = ctk.CTkProgressBar(self, height=8, corner_radius=4, fg_color="#1c2128", progress_color=ACCENT_CYAN)
        self.progress_bar.set(progress)
        self.progress_bar.pack(fill="x", padx=16, pady=(4, 6))

        self.subtext_label = ctk.CTkLabel(self, text=subtext, font=FONT_SMALL, text_color=TEXT_MUTED)
        self.subtext_label.pack(anchor="w", padx=16, pady=(0, 12))

    def update_metric(self, value: str, subtext: str = None, progress: float = None, color: str = None):
        self.value_label.configure(text=value)
        if subtext is not None:
            self.subtext_label.configure(text=subtext)
        if progress is not None:
            self.progress_bar.set(min(1.0, max(0.0, progress)))
        if color is not None:
            self.progress_bar.configure(progress_color=color)
