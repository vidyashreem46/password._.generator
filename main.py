"""
Required Libraries:
    pip install customtkinter pyperclip

Run Instructions:
    python main.py
"""

import datetime
import json
import math
import os
import platform
import random
import string
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk
import pyperclip


APP_NAME = "SecurePass Pro"
APP_SUBTITLE = "Smart Password Generator & Analyzer"
APP_VERSION = "1.0"
DEVELOPER = "B.Sc. (Hons.) Data Science & Artificial Intelligence Student"

HISTORY_FILE = "history.json"
MIN_LENGTH = 8
MAX_LENGTH = 64
AMBIGUOUS_CHARS = "0OolI1"

PLATFORM_RECOMMENDATIONS = {
    "Gmail": {
        "length": 16,
        "upper": True,
        "lower": True,
        "numbers": True,
        "symbols": True,
        "text": "Recommended: 16+ characters with uppercase, lowercase, numbers, and symbols.",
    },
    "Instagram": {
        "length": 14,
        "upper": True,
        "lower": True,
        "numbers": True,
        "symbols": True,
        "text": "Recommended: 14+ characters with mixed character types.",
    },
    "Facebook": {
        "length": 14,
        "upper": True,
        "lower": True,
        "numbers": True,
        "symbols": True,
        "text": "Recommended: 14+ characters with numbers and symbols.",
    },
    "Banking": {
        "length": 20,
        "upper": True,
        "lower": True,
        "numbers": True,
        "symbols": True,
        "text": "Recommended: 20+ characters with maximum complexity.",
    },
    "GitHub": {
        "length": 18,
        "upper": True,
        "lower": True,
        "numbers": True,
        "symbols": True,
        "text": "Recommended: 18+ characters for developer accounts.",
    },
    "College Portal": {
        "length": 12,
        "upper": True,
        "lower": True,
        "numbers": True,
        "symbols": False,
        "text": "Recommended: 12+ characters with letters and numbers.",
    },
    "Other": {
        "length": 16,
        "upper": True,
        "lower": True,
        "numbers": True,
        "symbols": True,
        "text": "Recommended: 16+ characters for general safe usage.",
    },
}


class SecurePassPro(ctk.CTk):
    """Main SecurePass Pro desktop application."""

    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry("980x650")
        self.resizable(False, False)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.password_var = tk.StringVar()
        self.length_var = tk.IntVar(value=16)
        self.status_var = tk.StringVar(value="Ready")
        self.platform_var = tk.StringVar(value="Other")
        self.password_visible = True

        self.uppercase_var = tk.BooleanVar(value=True)
        self.lowercase_var = tk.BooleanVar(value=True)
        self.numbers_var = tk.BooleanVar(value=True)
        self.symbols_var = tk.BooleanVar(value=True)
        self.avoid_ambiguous_var = tk.BooleanVar(value=False)

        self.history_window = None
        self.history_box = None

        self.ensure_history_file()
        self.create_menu()
        self.create_layout()
        self.update_platform_recommendation()
        self.update_strength_display("")

    def create_menu(self):
        """Create the application menu bar."""
        menu_bar = tk.Menu(self)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Generate", command=self.generate_password)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)
        menu_bar.add_cascade(label="File", menu=file_menu)

        generate_menu = tk.Menu(menu_bar, tearoff=0)
        generate_menu.add_command(label="Generate Password", command=self.generate_password)
        generate_menu.add_command(label="Copy Password", command=self.copy_password)
        generate_menu.add_command(label="Clear", command=self.clear_password)
        generate_menu.add_command(label="Show / Hide Password", command=self.toggle_password_visibility)
        menu_bar.add_cascade(label="Generate", menu=generate_menu)

        history_menu = tk.Menu(menu_bar, tearoff=0)
        history_menu.add_command(label="View History", command=self.view_history)
        history_menu.add_command(label="Delete History", command=self.delete_history)
        menu_bar.add_cascade(label="History", menu=history_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menu_bar)

    def create_layout(self):
        """Create all main GUI widgets with a scrollable body."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, corner_radius=0, fg_color="#102a43")
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text=APP_NAME,
            font=ctk.CTkFont(size=34, weight="bold"),
            text_color="#e0f2fe",
        )
        title.grid(row=0, column=0, pady=(16, 2))

        subtitle = ctk.CTkLabel(
            header,
            text=APP_SUBTITLE,
            font=ctk.CTkFont(size=15),
            text_color="#bae6fd",
        )
        subtitle.grid(row=1, column=0, pady=(0, 16))

        main = ctk.CTkScrollableFrame(
            self,
            corner_radius=0,
            fg_color="#182c3f",
            scrollbar_button_color="#2563eb",
            scrollbar_button_hover_color="#1d4ed8",
        )
        main.grid(row=1, column=0, sticky="nsew")
        main.grid_columnconfigure((0, 1), weight=1)

        self.create_left_panel(main)
        self.create_right_panel(main)

        footer = ctk.CTkFrame(self, corner_radius=0, fg_color="#102a43")
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_columnconfigure((0, 1), weight=1)

        status = ctk.CTkLabel(
            footer,
            textvariable=self.status_var,
            anchor="w",
            font=ctk.CTkFont(size=12),
            text_color="#dbeafe",
        )
        status.grid(row=0, column=0, padx=18, pady=9, sticky="w")

        footer_label = ctk.CTkLabel(
            footer,
            text="SecurePass Pro © 2026",
            anchor="e",
            font=ctk.CTkFont(size=12),
            text_color="#dbeafe",
        )
        footer_label.grid(row=0, column=1, padx=18, pady=9, sticky="e")

    def create_left_panel(self, parent):
        """Create settings, platform recommendation, and action buttons."""
        panel = ctk.CTkFrame(parent, corner_radius=18, fg_color="#243b53")
        panel.grid(row=0, column=0, padx=(22, 11), pady=22, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)

        heading = ctk.CTkLabel(
            panel,
            text="Password Settings",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#f8fafc",
        )
        heading.grid(row=0, column=0, padx=24, pady=(18, 8), sticky="w")

        platform_label = ctk.CTkLabel(
            panel,
            text="Where will you use this password?",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        platform_label.grid(row=1, column=0, padx=24, pady=(6, 5), sticky="w")

        self.platform_menu = ctk.CTkOptionMenu(
            panel,
            values=list(PLATFORM_RECOMMENDATIONS.keys()),
            variable=self.platform_var,
            command=lambda _: self.update_platform_recommendation(),
            height=36,
            corner_radius=10,
            fg_color="#2563eb",
            button_color="#1d4ed8",
            button_hover_color="#1e40af",
        )
        self.platform_menu.grid(row=2, column=0, padx=24, pady=(0, 7), sticky="ew")

        self.recommendation_label = ctk.CTkLabel(
            panel,
            text="",
            wraplength=400,
            justify="left",
            font=ctk.CTkFont(size=12),
            text_color="#dbeafe",
        )
        self.recommendation_label.grid(row=3, column=0, padx=24, pady=(0, 8), sticky="w")

        apply_btn = ctk.CTkButton(
            panel,
            text="Apply Recommended Settings",
            command=self.apply_recommended_settings,
            height=34,
            corner_radius=10,
            fg_color="#0891b2",
            hover_color="#0e7490",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        apply_btn.grid(row=4, column=0, padx=24, pady=(0, 12), sticky="ew")

        length_frame = ctk.CTkFrame(panel, fg_color="transparent")
        length_frame.grid(row=5, column=0, padx=24, pady=(4, 0), sticky="ew")
        length_frame.grid_columnconfigure(0, weight=1)

        length_label = ctk.CTkLabel(
            length_frame,
            text="Password Length",
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        length_label.grid(row=0, column=0, sticky="w")

        self.length_entry = ctk.CTkEntry(
            length_frame,
            width=75,
            height=36,
            justify="center",
            textvariable=self.length_var,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.length_entry.grid(row=0, column=1, sticky="e")
        self.length_entry.bind("<KeyRelease>", self.on_length_entry_change)

        self.length_slider = ctk.CTkSlider(
            panel,
            from_=MIN_LENGTH,
            to=MAX_LENGTH,
            number_of_steps=MAX_LENGTH - MIN_LENGTH,
            command=self.on_slider_change,
        )
        self.length_slider.set(self.length_var.get())
        self.length_slider.grid(row=6, column=0, padx=24, pady=(12, 14), sticky="ew")

        option_title = ctk.CTkLabel(
            panel,
            text="Character Selection",
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        option_title.grid(row=7, column=0, padx=24, pady=(4, 4), sticky="w")

        self.add_checkbox(panel, "Include Uppercase", self.uppercase_var, 8)
        self.add_checkbox(panel, "Include Lowercase", self.lowercase_var, 9)
        self.add_checkbox(panel, "Include Numbers", self.numbers_var, 10)
        self.add_checkbox(panel, "Include Symbols", self.symbols_var, 11)
        self.add_checkbox(panel, "Avoid Ambiguous Characters (0 O l I)", self.avoid_ambiguous_var, 12)

        button_frame = ctk.CTkFrame(panel, fg_color="transparent")
        button_frame.grid(row=13, column=0, padx=24, pady=(13, 10), sticky="ew")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        self.add_button(button_frame, "Generate Password", self.generate_password, 0, 0, "#2563eb", "#1d4ed8")
        self.add_button(button_frame, "Copy Password", self.copy_password, 0, 1, "#0e7490", "#155e75")
        self.add_button(button_frame, "Clear", self.clear_password, 1, 0, "#64748b", "#475569")
        self.add_button(button_frame, "View History", self.view_history, 1, 1, "#4f46e5", "#4338ca")
        self.add_button(button_frame, "Delete History", self.delete_history, 2, 0, "#b45309", "#92400e")
        self.add_button(button_frame, "Exit", self.exit_app, 2, 1, "#dc2626", "#b91c1c")

    def create_right_panel(self, parent):
        """Create generated password and strength analysis panel."""
        panel = ctk.CTkFrame(parent, corner_radius=18, fg_color="#243b53")
        panel.grid(row=0, column=1, padx=(11, 22), pady=22, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)

        heading = ctk.CTkLabel(
            panel,
            text="Generated Password",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#f8fafc",
        )
        heading.grid(row=0, column=0, padx=24, pady=(18, 12), sticky="w")

        password_frame = ctk.CTkFrame(panel, fg_color="transparent")
        password_frame.grid(row=1, column=0, padx=24, pady=(4, 16), sticky="ew")
        password_frame.grid_columnconfigure(0, weight=1)

        self.password_entry = ctk.CTkEntry(
            password_frame,
            textvariable=self.password_var,
            height=46,
            corner_radius=12,
            state="readonly",
            font=ctk.CTkFont(family="Consolas", size=15),
            text_color="#dbeafe",
        )
        self.password_entry.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        self.show_hide_btn = ctk.CTkButton(
            password_frame,
            text="Hide",
            command=self.toggle_password_visibility,
            width=90,
            height=46,
            corner_radius=12,
            fg_color="#475569",
            hover_color="#334155",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.show_hide_btn.grid(row=0, column=1, sticky="e")

        analysis = ctk.CTkFrame(panel, corner_radius=14, fg_color="#1f3448")
        analysis.grid(row=2, column=0, padx=24, pady=(6, 16), sticky="ew")
        analysis.grid_columnconfigure(0, weight=1)

        analysis_title = ctk.CTkLabel(
            analysis,
            text="Password Strength",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#f8fafc",
        )
        analysis_title.grid(row=0, column=0, padx=18, pady=(16, 6), sticky="w")

        self.strength_label = ctk.CTkLabel(
            analysis,
            text="Very Weak",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#ef4444",
        )
        self.strength_label.grid(row=1, column=0, padx=18, pady=(0, 6), sticky="w")

        self.strength_bar = ctk.CTkProgressBar(
            analysis,
            height=16,
            corner_radius=8,
            progress_color="#ef4444",
        )
        self.strength_bar.grid(row=2, column=0, padx=18, pady=(6, 16), sticky="ew")
        self.strength_bar.set(0)

        stats = ctk.CTkFrame(panel, corner_radius=14, fg_color="#1f3448")
        stats.grid(row=3, column=0, padx=24, pady=(0, 16), sticky="ew")
        stats.grid_columnconfigure(1, weight=1)

        self.entropy_value = self.add_stat_row(stats, "Entropy", "0 bits", 0)
        self.crack_time_value = self.add_stat_row(stats, "Estimated Crack Time", "Not available", 1)
        self.pool_value = self.add_stat_row(stats, "Character Pool", "0 characters", 2)
        self.policy_value = self.add_stat_row(stats, "Platform Policy", "Not checked", 3)

        advice_frame = ctk.CTkFrame(panel, corner_radius=14, fg_color="#1f3448")
        advice_frame.grid(row=4, column=0, padx=24, pady=(0, 12), sticky="ew")
        advice_frame.grid_columnconfigure(0, weight=1)

        advice_title = ctk.CTkLabel(
            advice_frame,
            text="Security Advice",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#f8fafc",
        )
        advice_title.grid(row=0, column=0, padx=18, pady=(14, 4), sticky="w")

        self.advice_label = ctk.CTkLabel(
            advice_frame,
            text="Generate a password to view security advice.",
            wraplength=390,
            justify="left",
            font=ctk.CTkFont(size=13),
            text_color="#dbeafe",
        )
        self.advice_label.grid(row=1, column=0, padx=18, pady=(0, 14), sticky="w")

        warning = ctk.CTkLabel(
            panel,
            text="Security note: Do not share passwords. Use a trusted password manager for important accounts.",
            wraplength=400,
            justify="left",
            font=ctk.CTkFont(size=12),
            text_color="#fde68a",
        )
        warning.grid(row=5, column=0, padx=24, pady=(2, 18), sticky="w")

    def add_checkbox(self, parent, text, variable, row):
        """Add a styled checkbox."""
        checkbox = ctk.CTkCheckBox(
            parent,
            text=text,
            variable=variable,
            font=ctk.CTkFont(size=14),
            checkbox_width=22,
            checkbox_height=22,
            corner_radius=6,
        )
        checkbox.grid(row=row, column=0, padx=24, pady=5, sticky="w")

    def add_button(self, parent, text, command, row, column, color, hover_color):
        """Add a rounded action button."""
        button = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            height=40,
            corner_radius=10,
            fg_color=color,
            hover_color=hover_color,
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        button.grid(row=row, column=column, padx=6, pady=6, sticky="ew")

    def add_stat_row(self, parent, label_text, value_text, row):
        """Create one statistic row."""
        label = ctk.CTkLabel(
            parent,
            text=label_text,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#93c5fd",
        )
        label.grid(row=row, column=0, padx=(18, 8), pady=8, sticky="w")

        value = ctk.CTkLabel(
            parent,
            text=value_text,
            font=ctk.CTkFont(size=13),
            text_color="#e5e7eb",
        )
        value.grid(row=row, column=1, padx=(8, 18), pady=8, sticky="e")
        return value

    def update_platform_recommendation(self):
        """Show recommendation text for selected platform."""
        platform_name = self.platform_var.get()
        recommendation = PLATFORM_RECOMMENDATIONS.get(platform_name, PLATFORM_RECOMMENDATIONS["Other"])
        self.recommendation_label.configure(text=recommendation["text"])
        self.set_status(f"Platform selected: {platform_name}")

    def apply_recommended_settings(self):
        """Apply recommended password settings for selected platform."""
        platform_name = self.platform_var.get()
        recommendation = PLATFORM_RECOMMENDATIONS.get(platform_name, PLATFORM_RECOMMENDATIONS["Other"])

        self.length_var.set(recommendation["length"])
        self.length_slider.set(recommendation["length"])
        self.uppercase_var.set(recommendation["upper"])
        self.lowercase_var.set(recommendation["lower"])
        self.numbers_var.set(recommendation["numbers"])
        self.symbols_var.set(recommendation["symbols"])

        self.set_status(f"Recommended settings applied for {platform_name}")

    def on_slider_change(self, value):
        """Update entry when slider changes."""
        self.length_var.set(int(round(value)))

    def on_length_entry_change(self, event=None):
        """Update slider when entry changes."""
        try:
            value = int(self.length_entry.get())
            if MIN_LENGTH <= value <= MAX_LENGTH:
                self.length_slider.set(value)
        except ValueError:
            pass

    def validate_length(self):
        """Validate password length."""
        try:
            length = int(self.length_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Length", "Password length must be a number.")
            self.set_status("Invalid length")
            return None

        if length < MIN_LENGTH:
            messagebox.showerror("Invalid Length", f"Length cannot be below {MIN_LENGTH}.")
            self.set_status("Length below minimum")
            return None

        if length > MAX_LENGTH:
            messagebox.showerror("Invalid Length", f"Length cannot be above {MAX_LENGTH}.")
            self.set_status("Length above maximum")
            return None

        self.length_var.set(length)
        self.length_slider.set(length)
        return length

    def get_selected_sets(self):
        """Return selected character sets."""
        selected_sets = []

        if self.uppercase_var.get():
            selected_sets.append(string.ascii_uppercase)
        if self.lowercase_var.get():
            selected_sets.append(string.ascii_lowercase)
        if self.numbers_var.get():
            selected_sets.append(string.digits)
        if self.symbols_var.get():
            selected_sets.append(string.punctuation)

        return selected_sets

    def remove_ambiguous(self, chars):
        """Remove ambiguous characters if option is enabled."""
        if not self.avoid_ambiguous_var.get():
            return chars
        return "".join(char for char in chars if char not in AMBIGUOUS_CHARS)

    def generate_password(self):
        """Generate a password and save it to history."""
        try:
            length = self.validate_length()
            if length is None:
                return

            selected_sets = self.get_selected_sets()
            if not selected_sets:
                messagebox.showerror("Selection Required", "Select at least one character option.")
                self.set_status("No character option selected")
                return

            filtered_sets = [self.remove_ambiguous(char_set) for char_set in selected_sets]
            filtered_sets = [char_set for char_set in filtered_sets if char_set]

            if not filtered_sets:
                messagebox.showerror("Invalid Selection", "No usable characters are available.")
                self.set_status("No usable characters")
                return

            password_chars = []

            if length >= len(filtered_sets):
                for char_set in filtered_sets:
                    password_chars.append(random.choice(char_set))

            all_chars = "".join(filtered_sets)

            while len(password_chars) < length:
                password_chars.append(random.choice(all_chars))

            random.shuffle(password_chars)
            password = "".join(password_chars[:length])

            self.set_password(password)
            strength, _, _ = self.update_strength_display(password)
            self.save_history(password, length, strength, self.platform_var.get())
            self.refresh_history_window()
            self.set_status("Password Generated | History Saved")

        except Exception as error:
            messagebox.showerror("Unexpected Error", f"Password generation failed:\n{error}")
            self.set_status("Unexpected error")

    def calculate_strength(self, password):
        """Calculate strength label, progress value, and color."""
        if not password:
            return "Very Weak", 0.0, "#ef4444"

        score = 0
        length = len(password)

        has_upper = any(char.isupper() for char in password)
        has_lower = any(char.islower() for char in password)
        has_number = any(char.isdigit() for char in password)
        has_symbol = any(char in string.punctuation for char in password)

        if length >= 8:
            score += 1
        if length >= 12:
            score += 1
        if length >= 16:
            score += 1
        if length >= 24:
            score += 1

        score += has_upper + has_lower + has_number + has_symbol

        if score <= 2:
            return "Very Weak", 0.2, "#ef4444"
        if score <= 4:
            return "Weak", 0.4, "#f97316"
        if score <= 5:
            return "Medium", 0.6, "#eab308"
        if score <= 7:
            return "Strong", 0.8, "#22c55e"
        return "Very Strong", 1.0, "#14b8a6"

    def update_strength_display(self, password):
        """Update strength, entropy, crack time, pool size, and advice."""
        strength, progress, color = self.calculate_strength(password)
        entropy = self.calculate_entropy(password)
        pool_size = self.calculate_pool_size(password)
        crack_time = self.estimate_crack_time(entropy)
        policy_status = self.check_platform_policy(password)
        advice = self.get_security_advice(strength, policy_status)

        self.strength_label.configure(text=strength, text_color=color)
        self.strength_bar.configure(progress_color=color)
        self.strength_bar.set(progress)

        self.entropy_value.configure(text=f"{entropy:.1f} bits" if password else "0 bits")
        self.crack_time_value.configure(text=crack_time)
        self.pool_value.configure(text=f"{pool_size} characters")
        self.policy_value.configure(text=policy_status)
        self.advice_label.configure(text=advice)

        return strength, progress, color

    def calculate_pool_size(self, password):
        """Estimate character pool size used by the password."""
        pool_size = 0

        if any(char.isupper() for char in password):
            pool_size += len(string.ascii_uppercase)
        if any(char.islower() for char in password):
            pool_size += len(string.ascii_lowercase)
        if any(char.isdigit() for char in password):
            pool_size += len(string.digits)
        if any(char in string.punctuation for char in password):
            pool_size += len(string.punctuation)

        return pool_size

    def calculate_entropy(self, password):
        """Calculate password entropy in bits."""
        pool_size = self.calculate_pool_size(password)

        if not password or pool_size == 0:
            return 0.0

        return len(password) * math.log2(pool_size)

    def estimate_crack_time(self, entropy):
        """Estimate crack time using a simple guesses-per-second model."""
        if entropy <= 0:
            return "Not available"

        guesses_per_second = 1_000_000_000
        seconds = (2 ** entropy) / guesses_per_second

        if seconds < 1:
            return "Less than 1 second"
        if seconds < 60:
            return f"{seconds:.0f} seconds"
        if seconds < 3600:
            return f"{seconds / 60:.1f} minutes"
        if seconds < 86400:
            return f"{seconds / 3600:.1f} hours"
        if seconds < 31536000:
            return f"{seconds / 86400:.1f} days"
        if seconds < 31536000000:
            return f"{seconds / 31536000:.1f} years"

        return "Thousands of years"

    def check_platform_policy(self, password):
        """Check if password meets selected platform recommendation."""
        if not password:
            return "Not checked"

        platform_name = self.platform_var.get()
        recommendation = PLATFORM_RECOMMENDATIONS.get(platform_name, PLATFORM_RECOMMENDATIONS["Other"])

        has_upper = any(char.isupper() for char in password)
        has_lower = any(char.islower() for char in password)
        has_number = any(char.isdigit() for char in password)
        has_symbol = any(char in string.punctuation for char in password)

        checks = [
            len(password) >= recommendation["length"],
            has_upper if recommendation["upper"] else True,
            has_lower if recommendation["lower"] else True,
            has_number if recommendation["numbers"] else True,
            has_symbol if recommendation["symbols"] else True,
        ]

        return "Passed" if all(checks) else "Needs improvement"

    def get_security_advice(self, strength, policy_status):
        """Return useful security advice based on password quality."""
        if strength == "Very Weak":
            return "Increase the password length and use uppercase, lowercase, numbers, and symbols."
        if strength == "Weak":
            return "This password needs improvement. Add more length and mixed character types."
        if strength == "Medium":
            return "Acceptable for low-risk accounts, but stronger settings are recommended."
        if strength == "Strong":
            if policy_status == "Passed":
                return "Good password. It matches the selected platform recommendation."
            return "Strong password, but it does not fully match the selected platform policy."
        if strength == "Very Strong":
            return "Excellent password. Suitable for important accounts like banking or developer accounts."

        return "Generate a password to view security advice."

    def set_password(self, password):
        """Set password text in readonly entry."""
        self.password_entry.configure(state="normal")
        self.password_var.set(password)
        self.password_entry.configure(state="readonly")

    def toggle_password_visibility(self):
        """Show or hide the generated password."""
        self.password_visible = not self.password_visible

        self.password_entry.configure(state="normal")

        if self.password_visible:
            self.password_entry.configure(show="")
            self.show_hide_btn.configure(text="Hide")
            self.set_status("Password visible")
        else:
            self.password_entry.configure(show="*")
            self.show_hide_btn.configure(text="Show")
            self.set_status("Password hidden")

        self.password_entry.configure(state="readonly")

    def copy_password(self):
        """Copy generated password to clipboard."""
        password = self.password_var.get()

        if not password:
            messagebox.showwarning("No Password", "Generate a password first.")
            self.set_status("No password to copy")
            return

        try:
            pyperclip.copy(password)
            messagebox.showinfo("Copied", "Password copied successfully.")
            self.set_status("Copied Successfully")
        except pyperclip.PyperclipException as error:
            messagebox.showerror("Clipboard Error", f"Could not copy password:\n{error}")
            self.set_status("Clipboard error")
        except Exception as error:
            messagebox.showerror("Unexpected Error", f"Clipboard operation failed:\n{error}")
            self.set_status("Clipboard error")

    def clear_password(self):
        """Clear password and reset analyzer."""
        self.set_password("")
        self.update_strength_display("")
        self.set_status("Cleared")

    def ensure_history_file(self):
        """Create history.json if missing and repair invalid JSON."""
        try:
            if not os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, "w", encoding="utf-8") as file:
                    json.dump([], file, indent=4)
                return

            with open(HISTORY_FILE, "r", encoding="utf-8") as file:
                content = file.read().strip()

            if not content:
                raise json.JSONDecodeError("Empty file", content, 0)

            data = json.loads(content)

            if not isinstance(data, list):
                raise ValueError("History must be a list.")

        except (json.JSONDecodeError, ValueError):
            with open(HISTORY_FILE, "w", encoding="utf-8") as file:
                json.dump([], file, indent=4)
        except OSError as error:
            messagebox.showerror("History Error", f"Could not access history file:\n{error}")

    def load_history(self):
        """Load password history from JSON."""
        try:
            self.ensure_history_file()

            with open(HISTORY_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            if isinstance(data, list):
                return data

            return []

        except (json.JSONDecodeError, OSError) as error:
            messagebox.showerror("History Error", f"Could not read history:\n{error}")
            self.set_status("History read error")
            return []

    def save_history(self, password, length, strength, platform_name):
        """Save generated password details."""
        try:
            history = self.load_history()

            history.append(
                {
                    "platform": platform_name,
                    "password": password,
                    "length": length,
                    "strength": strength,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            )

            with open(HISTORY_FILE, "w", encoding="utf-8") as file:
                json.dump(history, file, indent=4)

        except OSError as error:
            messagebox.showerror("History Error", f"Could not save history:\n{error}")
            self.set_status("History save error")

    def view_history(self):
        """Open password history window."""
        if self.history_window and self.history_window.winfo_exists():
            self.history_window.focus()
            self.refresh_history_window()
            return

        self.history_window = ctk.CTkToplevel(self)
        self.history_window.title("Password History")
        self.history_window.geometry("760x540")
        self.history_window.resizable(False, False)
        self.history_window.transient(self)
        self.history_window.protocol("WM_DELETE_WINDOW", self.close_history_window)

        heading = ctk.CTkLabel(
            self.history_window,
            text="Password History",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        heading.pack(padx=20, pady=(18, 8), anchor="w")

        self.history_box = ctk.CTkTextbox(
            self.history_window,
            width=720,
            height=405,
            corner_radius=12,
            font=ctk.CTkFont(family="Consolas", size=12),
        )
        self.history_box.pack(padx=20, pady=10, fill="both", expand=True)

        button_frame = ctk.CTkFrame(self.history_window, fg_color="transparent")
        button_frame.pack(padx=20, pady=(4, 18), fill="x")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        refresh_btn = ctk.CTkButton(
            button_frame,
            text="Refresh",
            command=self.refresh_history_window,
            height=38,
            corner_radius=10,
        )
        refresh_btn.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        close_btn = ctk.CTkButton(
            button_frame,
            text="Close",
            command=self.close_history_window,
            height=38,
            corner_radius=10,
            fg_color="#475569",
            hover_color="#334155",
        )
        close_btn.grid(row=0, column=1, padx=(8, 0), sticky="ew")

        self.refresh_history_window()
        self.set_status("Viewing history")

    def refresh_history_window(self):
        """Refresh history window content."""
        if not self.history_window or not self.history_window.winfo_exists():
            return

        if not self.history_box:
            return

        history = list(reversed(self.load_history()))

        self.history_box.configure(state="normal")
        self.history_box.delete("1.0", "end")

        if not history:
            self.history_box.insert("end", "No password history available.\n")
        else:
            for index, item in enumerate(history, start=1):
                timestamp = item.get("timestamp", "Unknown")
                platform_name = item.get("platform", "Not saved")
                password = item.get("password", "Unknown")
                length = item.get("length", "Unknown")
                strength = item.get("strength", "Unknown")

                record = (
                    f"{index:03}. Date     : {timestamp}\n"
                    f"     Platform : {platform_name}\n"
                    f"     Password : {password}\n"
                    f"     Length   : {length}\n"
                    f"     Strength : {strength}\n"
                    f"{'-' * 72}\n"
                )
                self.history_box.insert("end", record)

        self.history_box.configure(state="disabled")

    def close_history_window(self):
        """Close history window."""
        if self.history_window and self.history_window.winfo_exists():
            self.history_window.destroy()

        self.history_window = None
        self.history_box = None
        self.set_status("Ready")

    def delete_history(self):
        """Delete password history after confirmation."""
        confirm = messagebox.askyesno(
            "Delete History",
            "Are you sure you want to delete all saved password history?",
        )

        if not confirm:
            self.set_status("Delete history cancelled")
            return

        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as file:
                json.dump([], file, indent=4)

            self.refresh_history_window()
            messagebox.showinfo("History Deleted", "Password history has been deleted.")
            self.set_status("History deleted")

        except OSError as error:
            messagebox.showerror("History Error", f"Could not delete history:\n{error}")
            self.set_status("History delete error")

    def show_about(self):
        """Show About dialog."""
        about_text = (
            f"Project Name: {APP_NAME}\n"
            f"Subtitle: {APP_SUBTITLE}\n"
            f"Developer: {DEVELOPER}\n"
            f"Python Version: {platform.python_version()}\n"
            "Libraries Used: CustomTkinter, pyperclip, random, string, json, os, datetime\n"
            f"Version: {APP_VERSION}"
        )

        messagebox.showinfo("About SecurePass Pro", about_text)
        self.set_status("About")

    def exit_app(self):
        """Exit application with confirmation."""
        confirm = messagebox.askyesno("Exit", "Do you want to exit SecurePass Pro?")

        if confirm:
            self.destroy()

    def set_status(self, message):
        """Update status bar text."""
        self.status_var.set(message)


def main():
    """Application entry point."""
    app = SecurePassPro()
    app.mainloop()


if __name__ == "__main__":
    main()
