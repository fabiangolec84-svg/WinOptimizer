import customtkinter as ctk
from ui.theme import *

class ToggleCard(ctk.CTkFrame):
    def __init__(self, master, title: str, description: str, tag: str = "Tweak",
                 initial_state: bool = False, on_toggle=None, **kwargs):
        super().__init__(master, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER_COLOR, **kwargs)

        self.on_toggle = on_toggle
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        # Left Container (Text & Info)
        text_frame = ctk.CTkFrame(self, fg_color="transparent")
        text_frame.grid(row=0, column=0, sticky="w", padx=16, pady=12)

        # Header with Tag
        header_frame = ctk.CTkFrame(text_frame, fg_color="transparent")
        header_frame.pack(anchor="w")

        title_lbl = ctk.CTkLabel(header_frame, text=title, font=FONT_BODY_BOLD, text_color=TEXT_PRIMARY)
        title_lbl.pack(side="left")

        tag_lbl = ctk.CTkLabel(header_frame, text=f" {tag} ", font=("Segoe UI", 9, "bold"),
                               fg_color="#2b313a", text_color=ACCENT_CYAN, corner_radius=4)
        tag_lbl.pack(side="left", padx=(8, 0))

        # Description
        desc_lbl = ctk.CTkLabel(text_frame, text=description, font=FONT_SMALL, text_color=TEXT_SECONDARY,
                                wraplength=480, justify="left")
        desc_lbl.pack(anchor="w", pady=(4, 0))

        # Right Container (Switch)
        self.switch_var = ctk.BooleanVar(value=initial_state)
        self.switch = ctk.CTkSwitch(
            self,
            text="",
            variable=self.switch_var,
            command=self._handle_toggle,
            width=48,
            progress_color=ACCENT_GREEN,
            button_color="#ffffff",
            button_hover_color="#e5e7eb"
        )
        self.switch.grid(row=0, column=1, sticky="e", padx=16, pady=12)

    def _handle_toggle(self):
        new_val = self.switch_var.get()
        if self.on_toggle:
            self.on_toggle(new_val)

    def set_state(self, val: bool):
        self.switch_var.set(val)
