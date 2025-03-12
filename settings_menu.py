import customtkinter as ct
import pygame as pg

class SettingsMenu:
    def __init__(self, unpause_callback, restart_callback, exit_callback, auto_start_callback):
        self.unpause_callback = unpause_callback
        self.restart_callback = restart_callback
        self.exit_callback = exit_callback
        self.auto_start_callback = auto_start_callback

        # Create the settings menu window
        self.settings_window = ct.CTk()
        self.settings_window.title("Settings Menu")
        self.settings_window.geometry("400x400")
        self.settings_window.protocol("WM_DELETE_WINDOW", self.unpause_game)  # Bind window close event


        # Unpause button
        unpause_button = ct.CTkButton(self.settings_window, text="Unpause", command=self.unpause_game, width=200, height=50, font=("Arial", 16))
        unpause_button.pack(pady=20)

        # Music volume slider
        self.volume_label = ct.CTkLabel(self.settings_window, text=f"Volume: {int(pg.mixer.music.get_volume() * 100)}", font=("Arial", 16))
        self.volume_label.pack(pady=10)
        music_volume_slider = ct.CTkSlider(self.settings_window, from_=0, to=100, command=self.adjust_music_volume, width=200)
        music_volume_slider.set(pg.mixer.music.get_volume() * 100)
        music_volume_slider.pack(pady=20)

        # Exit to main menu button
        exit_button = ct.CTkButton(self.settings_window, text="Exit to Main Menu", command=self.exit_to_main_menu, width=200, height=50, font=("Arial", 16))
        exit_button.pack(pady=20)

        # Restart button
        restart_button = ct.CTkButton(self.settings_window, text="Restart", command=self.restart_game, width=200, height=50, font=("Arial", 16))
        restart_button.pack(pady=20)

        # Auto-start switch
        auto_start_switch = ct.CTkSwitch(self.settings_window, text="Auto Start", command=self.toggle_auto_start, width=200, font=("Arial", 16))
        auto_start_switch.pack(pady=20)

    def unpause_game(self):
        self.unpause_callback()
        self.settings_window.destroy()

    def adjust_music_volume(self, value):
        pg.mixer.music.set_volume(float(value) / 100)
        self.volume_label.configure(text=f"Volume: {int(value)}")

    def exit_to_main_menu(self):
        self.exit_callback()
        self.settings_window.destroy()

    def restart_game(self):
        self.restart_callback()
        self.settings_window.destroy()

    def toggle_auto_start(self):
        self.auto_start_callback()

    def show(self):
        self.settings_window.mainloop()