import os
import sys
import customtkinter as ctk
from ui.theme import *
from core.elevation import is_admin, elevate
from ui.pages.dashboard_page import DashboardPage
from ui.pages.cleaner_page import CleanerPage
from ui.pages.gaming_page import GamingPage
from ui.pages.game_profiles_page import GameProfilesPage
from ui.pages.privacy_page import PrivacyPage
from ui.pages.startup_page import StartupPage
from ui.pages.storage_page import StoragePage
from ui.pages.bloatware_page import BloatwarePage

class AppWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Appearance configuration
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.title("WinOptimizer - Windows & Gaming FPS Booster")
        self.geometry("1100x720")
        self.minsize(960, 620)
        self.configure(fg_color=BG_DARK)

        if getattr(sys, 'frozen', False):
            base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        icon_path = os.path.join(base_dir, "assets", "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        # Main Layout Grid
        self.grid_columnconfigure(0, weight=0)  # Sidebar
        self.grid_columnconfigure(1, weight=1)  # Content
        self.grid_rowconfigure(0, weight=1)

        self.nav_buttons = {}
        self.pages = {}
        self.current_page = None

        self._build_sidebar()
        self._build_content_area()
        self._build_toast()

        # Show initial page
        self._navigate_to("dashboard")

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, fg_color=BG_SIDEBAR, width=230, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        # Logo / Brand
        brand_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", padx=16, pady=(20, 16))

        logo_lbl = ctk.CTkLabel(brand_frame, text="🚀 WinOptimizer", font=("Segoe UI", 18, "bold"), text_color=ACCENT_CYAN)
        logo_lbl.pack(anchor="w")

        sub_lbl = ctk.CTkLabel(brand_frame, text="Gaming & System Booster", font=FONT_SMALL, text_color=TEXT_MUTED)
        sub_lbl.pack(anchor="w")

        # Admin Badge
        admin_frame = ctk.CTkFrame(sidebar, fg_color="#1f242c", corner_radius=8)
        admin_frame.pack(fill="x", padx=16, pady=(0, 20))

        if is_admin():
            admin_lbl = ctk.CTkLabel(admin_frame, text="● Tryb Administratora: AKTYWNY", font=("Segoe UI", 10, "bold"), text_color=ACCENT_GREEN)
            admin_lbl.pack(padx=10, pady=6)
        else:
            admin_btn = ctk.CTkButton(
                admin_frame,
                text="▲ Nadaj Prawa Administratora",
                font=("Segoe UI", 10, "bold"),
                fg_color="#b91c1c",
                hover_color="#991b1b",
                text_color="#ffffff",
                height=28,
                corner_radius=6,
                command=elevate
            )
            admin_btn.pack(padx=6, pady=6, fill="x")

        # Nav items
        nav_items = [
            ("dashboard", "🏠  Pulpit Główny"),
            ("cleaner", "🧹  Czyszczenie Śmieci"),
            ("storage", "📦  Aplikacje & Pliki"),
            ("gaming", "⚡  Gaming & FPS"),
            ("profiles", "🎮  Profile Gier"),
            ("privacy", "🛡️  Prywatność (Debloat)"),
            ("startup", "🚀  Autostart"),
            ("bloatware", "🗑️  Bloatware"),
        ]

        nav_container = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav_container.pack(fill="both", expand=True, padx=12)

        for key, label in nav_items:
            btn = ctk.CTkButton(
                nav_container,
                text=label,
                font=FONT_BODY_BOLD,
                fg_color="transparent",
                hover_color=BG_CARD_HOVER,
                text_color=TEXT_SECONDARY,
                anchor="w",
                height=38,
                corner_radius=8,
                command=lambda k=key: self._navigate_to(k)
            )
            btn.pack(fill="x", pady=2)
            self.nav_buttons[key] = btn

        # Footer
        footer = ctk.CTkFrame(sidebar, fg_color="transparent")
        footer.pack(fill="x", padx=16, pady=16)

        tray_btn = ctk.CTkButton(
            footer,
            text="📥 Minimalizuj do Traya",
            font=FONT_SMALL,
            fg_color="#21262d",
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_SECONDARY,
            height=28,
            corner_radius=6,
            command=self._minimize_to_tray
        )
        tray_btn.pack(fill="x", pady=(0, 8))

        ver_lbl = ctk.CTkLabel(footer, text="v2.0 Pro • Windows 10/11", font=FONT_SMALL, text_color=TEXT_MUTED)
        ver_lbl.pack(anchor="w")

    def _minimize_to_tray(self):
        try:
            from core.tray_icon import start_tray
            self.withdraw()
            start_tray(
                on_show_callback=lambda: self.after(0, self._restore_from_tray),
                on_clean_ram_callback=self._tray_clean_ram,
                on_boost_callback=self._tray_boost,
                on_quit_callback=lambda: self.after(0, self._on_tray_quit)
            )
        except Exception:
            self.iconify()

    def _restore_from_tray(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def _on_tray_quit(self):
        try:
            from core.tray_icon import stop_tray
            stop_tray()
        except Exception:
            pass
        self.destroy()

    def _tray_clean_ram(self):
        from core.ram_cleaner import clean_ram
        clean_ram()

    def _tray_boost(self):
        from tweaks.gaming_tweaks import set_gamedvr_disabled, set_game_mode_enabled, set_power_plan
        from core.ram_cleaner import clean_ram
        set_gamedvr_disabled(True)
        set_game_mode_enabled(True)
        set_power_plan(True)
        clean_ram()

    def _build_content_area(self):
        self.content_container = ctk.CTkFrame(self, fg_color=BG_DARK, corner_radius=0)
        self.content_container.grid(row=0, column=1, sticky="nsew")
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

    def _build_toast(self):
        self.toast_frame = ctk.CTkFrame(self, fg_color=ACCENT_CYAN, corner_radius=10, height=40)
        self.toast_label = ctk.CTkLabel(self.toast_frame, text="", font=FONT_BODY_BOLD, text_color="#000000")
        self.toast_label.pack(padx=20, pady=8)
        self.toast_timer = None

    def show_toast(self, message: str, duration_ms: int = 3500):
        self.toast_label.configure(text=message)
        self.toast_frame.place(relx=0.5, rely=0.94, anchor="center")

        if self.toast_timer:
            self.after_cancel(self.toast_timer)
        self.toast_timer = self.after(duration_ms, self.toast_frame.place_forget)

    def _navigate_to(self, page_key: str):
        # Update button highlights
        for key, btn in self.nav_buttons.items():
            if key == page_key:
                btn.configure(fg_color=BG_CARD, text_color=ACCENT_CYAN)
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_SECONDARY)

        # Lazy load or show page
        if page_key not in self.pages:
            if page_key == "dashboard":
                self.pages[page_key] = DashboardPage(self.content_container, show_toast_callback=self.show_toast)
            elif page_key == "cleaner":
                self.pages[page_key] = CleanerPage(self.content_container, show_toast_callback=self.show_toast)
            elif page_key == "storage":
                self.pages[page_key] = StoragePage(self.content_container, show_toast_callback=self.show_toast)
            elif page_key == "gaming":
                self.pages[page_key] = GamingPage(self.content_container, show_toast_callback=self.show_toast)
            elif page_key == "profiles":
                self.pages[page_key] = GameProfilesPage(self.content_container, show_toast_callback=self.show_toast)
            elif page_key == "privacy":
                self.pages[page_key] = PrivacyPage(self.content_container, show_toast_callback=self.show_toast)
            elif page_key == "startup":
                self.pages[page_key] = StartupPage(self.content_container, show_toast_callback=self.show_toast)
            elif page_key == "bloatware":
                self.pages[page_key] = BloatwarePage(self.content_container, show_toast_callback=self.show_toast)

        # Hide current page and show new one
        if self.current_page:
            self.current_page.grid_forget()

        self.current_page = self.pages[page_key]
        self.current_page.grid(row=0, column=0, sticky="nsew")
