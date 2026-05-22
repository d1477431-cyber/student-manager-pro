import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import sqlite3

# Import de la logique métier extraite
from core.db import (
    db_session, setup_database, hash_password, log_event, 
    DB_P, DB_TYPE, DB_PATH
)

import json
import webbrowser
import os
from datetime import datetime
import csv
import shutil
import cv2
import hashlib
import threading
import urllib.request
import logging
import subprocess
from PIL import Image, ImageTk  # pip install pillow
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm

# --- CONFIGURATION DU LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- CONFIGURATION DES CHEMINS ---
if getattr(sys, 'frozen', False):
    # Dossier temporaire pour les ressources internes lors de l'exécution du .exe
    ASSETS_DIR = sys._MEIPASS
    # Dossier où se trouve réellement le fichier .exe (pour les données persistantes)
    DATA_DIR = os.path.dirname(sys.executable)
else:
    ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = ASSETS_DIR

DB_PATH = os.path.join(DATA_DIR, "etudiants.db")
JSON_PATH = os.path.join(DATA_DIR, "etudiants.json")
PHOTOS_DIR = os.path.join(DATA_DIR, "photos")
BASE_DIR = DATA_DIR

# --- CONFIGURATION BRANDING ---
APP_NAME = "Student Manager PRO"
APP_VERSION = "v2.1.0"
GITHUB_USER = "VOTRE_NOM_GITHUB"
GITHUB_REPO = "NOM_DU_REPO"
VERSION_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/version.json"
UPDATE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/gestionnaire.py"
APP_ICON = os.path.join(ASSETS_DIR, "app_icon.ico")
APP_LOGO = os.path.join(ASSETS_DIR, "logo.png")

def set_window_icon(window):
    """Applique l'icône favicon à une fenêtre"""
    try:
        if os.path.exists(APP_ICON):
            window.iconbitmap(APP_ICON)
        elif os.path.exists(APP_LOGO):
            img = tk.PhotoImage(file=APP_LOGO)
            window.iconphoto(False, img)
            return img # Garder une référence
    except Exception: pass
    return None

class SplashScreen:
    """Fenêtre de démarrage élégante pour le rendu PRO"""
    def __init__(self, root, on_complete):
        self.root = root
        self.on_complete = on_complete
        self.splash = tk.Toplevel(root)
        self.splash.overrideredirect(True) # Pas de bordures
        self.splash.attributes('-topmost', True)
        
        width, height = 500, 300
        screen_width = self.splash.winfo_screenwidth()
        screen_height = self.splash.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.splash.geometry(f"{width}x{height}+{x}+{y}")
        self.splash.config(bg="#0F172A")

        # Design du Splash
        frame = tk.Frame(self.splash, bg="#0F172A", highlightthickness=2, highlightbackground="#38BDF8")
        frame.pack(fill=tk.BOTH, expand=True)

        # Logo ou Emoji par défaut
        self.logo_img = set_window_icon(self.splash)
        
        tk.Label(frame, text="🎓", font=("Segoe UI", 60), bg="#0F172A", fg="#38BDF8").pack(pady=(35, 0))
        tk.Label(frame, text=APP_NAME, font=("Segoe UI", 24, "bold"), bg="#0F172A", fg="white").pack()
        tk.Label(frame, text=APP_VERSION, font=("Segoe UI", 9), bg="#0F172A", fg="#38BDF8").pack()
        tk.Label(frame, text="Chargement de votre espace de travail...", font=("Segoe UI", 10), bg="#0F172A", fg="#94A3B8").pack(pady=20)
        
        # Barre de progression de démarrage
        self.progress = ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=350, mode='determinate')
        self.progress.pack(pady=10)
        
        self.splash.attributes('-alpha', 0.0)
        self.fade_in(0.0)

    def fade_in(self, alpha):
        if alpha < 1.0:
            alpha += 0.05
            self.splash.attributes('-alpha', alpha)
            self.progress['value'] += 5
            self.root.after(30, lambda: self.fade_in(alpha))
        else:
            self.root.after(800, self.finish)

    def finish(self):
        self.splash.destroy()
        self.on_complete()

class LoginWindow:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success
        
        self.window = tk.Toplevel(root)
        self.window.title(f"{APP_NAME} - Connexion")
        self.window.geometry("400x480")
        self.window.attributes('-alpha', 0.0)
        set_window_icon(self.window)
        
        # Palette de couleurs moderne (Thème Ultra Moderne - Midnight)
        self.colors = {
            "bg": "#0F172A",      # Fond très sombre (Midnight Blue)
            "card": "#1E293B",    # Fond carte (Slate)
            "input": "#334155",   # Champs saisie
            "fg": "#94A3B8",      # Texte secondaire
            "accent": "#38BDF8",  # Cyan électrique
            "white": "#F8FAFC"    # Blanc éclatant
        }
        self.window.config(bg=self.colors["bg"])
        
        self.window.resizable(False, False)
        
        # Centrer la fenêtre
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 480) // 2
        self.window.geometry(f"400x480+{x}+{y}")
        
        # Design - Style Carte Flottante
        card_frame = tk.Frame(self.window, bg=self.colors["card"], padx=20, pady=30)
        card_frame.place(relx=0.5, rely=0.5, anchor="center", width=340)
        
        tk.Label(card_frame, text="🔐", font=("Segoe UI", 40), bg=self.colors["card"], fg=self.colors["accent"]).pack(pady=(0, 10))
        tk.Label(card_frame, text="CONNEXION", font=("Segoe UI", 18, "bold"), bg=self.colors["card"], fg=self.colors["white"]).pack(pady=(0, 25))
        
        # Formulaire dans la carte
        tk.Label(card_frame, text="Utilisateur", font=("Segoe UI", 10), bg=self.colors["card"], fg=self.colors["fg"]).pack(anchor=tk.W)
        self.user_entry = tk.Entry(card_frame, font=("Segoe UI", 11), bg=self.colors["input"], fg=self.colors["white"], relief=tk.FLAT, insertbackground=self.colors["accent"])
        self.user_entry.pack(fill=tk.X, pady=(5, 15), ipady=5)
        
        tk.Label(card_frame, text="Mot de passe", font=("Segoe UI", 10), bg=self.colors["card"], fg=self.colors["fg"]).pack(anchor=tk.W)
        self.pass_entry = tk.Entry(card_frame, font=("Segoe UI", 11), bg=self.colors["input"], fg=self.colors["white"], relief=tk.FLAT, show="•", insertbackground=self.colors["accent"])
        self.pass_entry.pack(fill=tk.X, pady=(5, 25), ipady=5)
        
        btn = tk.Button(card_frame, text="SE CONNECTER", command=self.login,
                       bg=self.colors["accent"], fg="#2E3440", font=("Segoe UI", 11, "bold"),
                       relief=tk.FLAT, cursor="hand2", pady=10)
        btn.pack(fill=tk.X, pady=10)
        
        # Bind Enter key
        self.window.bind('<Return>', lambda e: self.login())
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing) # Assurez-vous que cette ligne est bien là
        
        self.user_entry.focus()
        self.animate_window(self.window)

    def animate_window(self, window):
        """Animation d'ouverture en fondu"""
        def fade_in(alpha):
            if alpha < 1.0:
                alpha += 0.08
                window.attributes('-alpha', alpha)
                window.after(10, fade_in, alpha)
            else:
                window.attributes('-alpha', 1.0)
        fade_in(0.0)

    def login(self):
        user = self.user_entry.get()
        password = self.pass_entry.get()
        hashed_pw = hash_password(password)

        try:
            with db_session() as conn:
                cursor = conn.cursor()
                query = f"SELECT role, theme FROM users WHERE username = {DB_P} AND password_hash = {DB_P}"
                try:
                    cursor.execute(query, (user, hashed_pw))
                except sqlite3.OperationalError as e:
                    if "no such column: theme" in str(e).lower():
                        cursor.execute(f"SELECT role FROM users WHERE username = {DB_P} AND password_hash = {DB_P}", (user, hashed_pw))
                    else:
                        raise
                result = cursor.fetchone()
                
            if result:
                role = result[0]
                theme = result[1] if len(result) > 1 and result[1] else 'dark'
                log_event(user, "LOGIN_SUCCESS", f"Accès autorisé - Rôle: {role}")
                self.window.destroy()
                self.on_success(user, role, theme)
            else:
                log_event(user, "LOGIN_FAILURE", "Identifiants invalides")
                messagebox.showerror("Erreur", "Identifiants incorrects\n", parent=self.window)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur de base de données: {e}", parent=self.window)

    def on_closing(self):
        self.root.destroy()

class GestionEtudiantsApp:
    def __init__(self, root, username="Utilisateur", role="Professeur", user_theme="dark"):
        self.root = root
        self.root.title(f"{APP_NAME} {APP_VERSION}")
        self.username = username # Stocke le nom d'utilisateur
        self.role = role         # Stocke le rôle (Admin, Secrétaire, Professeur)
        self.root.geometry("1400x800")
        set_window_icon(self.root)

        # --- SÉCURITÉ : CONFIGURATION SESSION ---
        self.session_timeout = 10 * 60 * 1000  # 10 minutes d'inactivité
        self.timeout_id = None
        self.reset_session_timer()
        
        # Monitorer l'activité utilisateur pour réinitialiser le timer
        self.root.bind_all("<Any-KeyPress>", lambda e: self.reset_session_timer())
        self.root.bind_all("<Any-ButtonPress>", lambda e: self.reset_session_timer())

        self.root.attributes('-alpha', 0.0)
        
        # Thèmes disponibles et métadonnées d’affichage
        self.theme_data = {
            "dark": {
                "label": "🌙  Mode Sombre (Slate)", "preview": "#1E293B",
                "colors": {
                    "bg_main": "#0F172A", "bg_panel": "#1E293B", "bg_input": "#334155",
                    "bg_header": "#0F172A", "fg_text": "#CBD5E1", "fg_head": "#F8FAFC",
                    "accent": "#38BDF8", "success": "#4ADE80", "warning": "#FBBF24",
                    "danger": "#F87171", "border": "#475569",
                    "badge_bg": "#FBBF24", "badge_fg": "#0F172A"
                }
            },
            "light": {
                "label": "☀️  Mode Clair (Snow)", "preview": "#0EA5E9",
                "colors": {
                    "bg_main": "#F1F5F9", "bg_panel": "#FFFFFF", "bg_input": "#E2E8F0",
                    "bg_header": "#F8FAFC", "fg_text": "#334155", "fg_head": "#0F172A",
                    "accent": "#0EA5E9", "success": "#22C55E", "warning": "#F59E0B",
                    "danger": "#EF4444", "border": "#CBD5E1",
                    "badge_bg": "#0EA5E9", "badge_fg": "#FFFFFF"
                }
            },
            "nature": {
                "label": "🌿  Mode Nature (Emerald)", "preview": "#065F46",
                "colors": {
                    "bg_main": "#064E3B", "bg_panel": "#065F46", "bg_input": "#047857",
                    "bg_header": "#064E3B", "fg_text": "#D1FAE5", "fg_head": "#ECFDF5",
                    "accent": "#10B981", "success": "#34D399", "warning": "#FCD34D",
                    "danger": "#F87171", "border": "#059669",
                    "badge_bg": "#10B981", "badge_fg": "#064E3B"
                }
            },
            "amethyst": {
                "label": "💎  Mode Améthyste (Purple)", "preview": "#4C1D95",
                "colors": {
                    "bg_main": "#2E1065", "bg_panel": "#4C1D95", "bg_input": "#5B21B6",
                    "bg_header": "#2E1065", "fg_text": "#E9D5FF", "fg_head": "#F5F3FF",
                    "accent": "#A78BFA", "success": "#34D399", "warning": "#FBBF24",
                    "danger": "#F87171", "border": "#7C3AED",
                    "badge_bg": "#C084FC", "badge_fg": "#2E1065"
                }
            },
            "sunset": {
                "label": "🌅  Mode Sunset (Warm)", "preview": "#7C2D12",
                "colors": {
                    "bg_main": "#450A0A", "bg_panel": "#7C2D12", "bg_input": "#9A3412",
                    "bg_header": "#450A0A", "fg_text": "#FFEDD5", "fg_head": "#FFF7ED",
                    "accent": "#FB923C", "success": "#4ADE80", "warning": "#FBBF24",
                    "danger": "#F87171", "border": "#C2410C",
                    "badge_bg": "#FB923C", "badge_fg": "#450A0A"
                }
            },
            "forest": {
                "label": "🌲  Mode Forêt (Forest)", "preview": "#22C55E",
                "colors": {
                    "bg_main": "#0B3D2E", "bg_panel": "#14532D", "bg_input": "#166534",
                    "bg_header": "#0B3D2E", "fg_text": "#D9F7E8", "fg_head": "#EFFAF5",
                    "accent": "#22C55E", "success": "#4ADE80", "warning": "#FACC15",
                    "danger": "#F97316", "border": "#15803D",
                    "badge_bg": "#22C55E", "badge_fg": "#0B3D2E"
                }
            },
            "sahara": {
                "label": "🏜️  Mode Sahara (Desert)", "preview": "#F59E0B",
                "colors": {
                    "bg_main": "#7C510A", "bg_panel": "#A16207", "bg_input": "#C2410C",
                    "bg_header": "#7C510A", "fg_text": "#FFFBEB", "fg_head": "#FFFAF0",
                    "accent": "#F59E0B", "success": "#22C55E", "warning": "#FBBF24",
                    "danger": "#DC2626", "border": "#92400E",
                    "badge_bg": "#F59E0B", "badge_fg": "#7C510A"
                }
            },
            "coffee": {
                "label": "☕  Mode Coffee (Retro)", "preview": "#D97706",
                "colors": {
                    "bg_main": "#2B1B0F", "bg_panel": "#432F23", "bg_input": "#71503E",
                    "bg_header": "#2B1B0F", "fg_text": "#F5E6D3", "fg_head": "#FFF7ED",
                    "accent": "#D97706", "success": "#4ADE80", "warning": "#FBBF24",
                    "danger": "#EF4444", "border": "#7C2D12",
                    "badge_bg": "#D97706", "badge_fg": "#2B1B0F"
                }
            },
            "ocean": {
                "label": "🌊  Mode Océan (Blue)", "preview": "#38BDF8",
                "colors": {
                    "bg_main": "#0E3B66", "bg_panel": "#164A8A", "bg_input": "#1D4E89",
                    "bg_header": "#0E3B66", "fg_text": "#E0F2FE", "fg_head": "#F8FAFC",
                    "accent": "#38BDF8", "success": "#22C55E", "warning": "#F59E0B",
                    "danger": "#FB7185", "border": "#1E40AF",
                    "badge_bg": "#38BDF8", "badge_fg": "#0E3B66"
                }
            },
            "rose": {
                "label": "🌸  Mode Rose (Blush)", "preview": "#F472B6",
                "colors": {
                    "bg_main": "#311D3F", "bg_panel": "#4C1C74", "bg_input": "#6D28D9",
                    "bg_header": "#311D3F", "fg_text": "#F5F3FF", "fg_head": "#FFFFFF",
                    "accent": "#F472B6", "success": "#34D399", "warning": "#FCD34D",
                    "danger": "#F87171", "border": "#8B5CF6",
                    "badge_bg": "#F472B6", "badge_fg": "#311D3F"
                }
            },
            "aurora": {
                "label": "🌌  Mode Aurora (Glow)", "preview": "#7C3AED",
                "colors": {
                    "bg_main": "#0F172A", "bg_panel": "#1E293B", "bg_input": "#475569",
                    "bg_header": "#0F172A", "fg_text": "#E2E8F0", "fg_head": "#F8FAFC",
                    "accent": "#7C3AED", "success": "#34D399", "warning": "#F59E0B",
                    "danger": "#EF4444", "border": "#4338CA",
                    "badge_bg": "#7C3AED", "badge_fg": "#F8FAFC"
                }
            },
            "cobalt": {
                "label": "💾  Mode Cobalt (Neon)", "preview": "#2563EB",
                "colors": {
                    "bg_main": "#0B1220", "bg_panel": "#16213E", "bg_input": "#1E2A5B",
                    "bg_header": "#0B1220", "fg_text": "#E2E8F0", "fg_head": "#F8FAFC",
                    "accent": "#2563EB", "success": "#34D399", "warning": "#FACC15",
                    "danger": "#EF4444", "border": "#1D4ED8",
                    "badge_bg": "#2563EB", "badge_fg": "#0B1220"
                }
            },
            "cyber": {
                "label": "💾  Mode Cyber (Neon)", "preview": "#22D3EE",
                "colors": {
                    "bg_main": "#020617", "bg_panel": "#0F172A", "bg_input": "#0E7490",
                    "bg_header": "#020617", "fg_text": "#E0F2FE", "fg_head": "#F8FAFC",
                    "accent": "#22D3EE", "success": "#34D399", "warning": "#FACC15",
                    "danger": "#EF4444", "border": "#0284C7",
                    "badge_bg": "#22D3EE", "badge_fg": "#020617"
                }
            },
            "midnight_gold": {
                "label": "👑  Midnight Gold (Luxury)", "preview": "#D4AF37",
                "colors": {
                    "bg_main": "#000000", "bg_panel": "#171717", "bg_input": "#262626",
                    "bg_header": "#000000", "fg_text": "#E5E5E5", "fg_head": "#FFFFFF",
                    "accent": "#D4AF37", "success": "#10B981", "warning": "#F59E0B",
                    "danger": "#EF4444", "border": "#404040",
                    "badge_bg": "#D4AF37", "badge_fg": "#000000"
                }
            }
        }
        self.themes = {key: data["colors"] for key, data in self.theme_data.items()}
        self.theme_options = [(data["label"], key, data["preview"]) for key, data in self.theme_data.items()]

        # Définir le thème courant depuis la préférence utilisateur si fournie
        self.current_theme = user_theme if user_theme in self.themes else "dark"
        self.colors = self.themes[self.current_theme]
        self.root.config(bg=self.colors["bg_main"])
        
        # Configurer le style
        self.setup_styles()
        
        self.etudiants = []
        self.etudiants_filtres = []
        self.paiements = []
        self.editing_username = None
        self.editing_matricule = None
        self.current_photo_path = None
        self.tree = None
        self.active_notifications = []
        
        # Créer le dossier pour les photos s'il n'existe pas
        if not os.path.exists("photos"):
            os.makedirs("photos")
            
        self.root.minsize(1000, 600)
        self.start_loading()
        
        # Vérifier les mises à jour en arrière-plan
        self.verifier_mises_a_jour(automatique=True)

    def reset_session_timer(self):
        """Réinitialise le compte à rebours d'inactivité"""
        if self.timeout_id:
            self.root.after_cancel(self.timeout_id)
        self.timeout_id = self.root.after(self.session_timeout, self.session_expired)

    def session_expired(self):
        """Gère l'expiration de la session pour sécurité"""
        log_event(self.username, "SESSION_TIMEOUT", "Déconnexion automatique par inactivité")
        messagebox.showwarning("⏳ Session Expirée", 
                             "Votre session a expiré après 10 minutes d'inactivité.\n"
                             "Veuillez vous reconnecter.")
        self.deconnexion(ask_confirm=False)

    def start_loading(self):
        """Affiche un écran de chargement avec une barre de progression"""
        self.loading_frame = tk.Frame(self.root, bg=self.colors["bg_main"])
        self.loading_frame.pack(fill=tk.BOTH, expand=True)

        # Logo ou Icône de chargement
        tk.Label(self.loading_frame, text="🎓", font=("Segoe UI", 70), 
                 bg=self.colors["bg_main"], fg=self.colors["accent"]).pack(pady=(180, 20))

        tk.Label(self.loading_frame, text="Manager PRO", font=("Segoe UI", 24, "bold"), 
                 bg=self.colors["bg_main"], fg=self.colors["fg_head"]).pack()

        # Barre de progression personnalisée
        self.progress = ttk.Progressbar(self.loading_frame, orient=tk.HORIZONTAL, 
                                        length=400, mode='determinate')
        self.progress.pack(pady=30)

        self.loading_status = tk.Label(self.loading_frame, text="Initialisation...", 
                                       font=("Segoe UI", 10), bg=self.colors["bg_main"], 
                                       fg=self.colors["fg_text"])
        self.loading_status.pack()

        self.update_loading_progress(0)

    def update_loading_progress(self, value):
        self.progress['value'] = value
        
        if value == 30:
            self.loading_status.config(text="Connexion à la base de données...")
            self.init_db()
        elif value == 60:
            self.loading_status.config(text="Chargement des étudiants...")
            self.charger_donnees()
        elif value == 90:
            self.loading_status.config(text="Préparation de l'interface...")
        elif value >= 100:
            self.loading_frame.destroy()
            self.create_widgets()
            self.animate_window(self.root) # Anime l'apparition de la fenêtre principale
            self.notify(f"Bienvenue, {self.username} !", "info") # Affiche le message de bienvenue
            return

        # Simuler un délai pour l'effet visuel "PRO"
        self.root.after(25, lambda: self.update_loading_progress(value + 2))

    def adjust_color(self, hex_color, factor=1.2):
        try:
            hex_color = hex_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            new_rgb = [min(255, max(0, int(c * factor))) for c in rgb]
            return "#%02x%02x%02x" % tuple(new_rgb)
        except: return hex_color

    def show_loader_overlay(self, message="Traitement en cours...", duration=800):
        """Affiche un loader temporaire sur l'écran pour confirmer une action"""
        overlay = tk.Frame(self.root, bg=self.colors["bg_main"])
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        overlay.attributes = {'alpha': 0.7} # Simulation de transparence
        
        content = tk.Frame(overlay, bg=self.colors["bg_panel"], padx=40, pady=30, 
                          highlightthickness=2, highlightbackground=self.colors["accent"])
        content.place(relx=0.5, rely=0.5, anchor="center")
        
        # Icône de chargement animée (emoji tournant)
        loader_label = tk.Label(content, text="⌛", font=("Segoe UI", 30), bg=self.colors["bg_panel"], fg=self.colors["accent"])
        loader_label.pack()
        
        tk.Label(content, text=message, font=("Segoe UI", 11, "bold"), 
                 bg=self.colors["bg_panel"], fg=self.colors["fg_head"]).pack(pady=(10, 0))
        
        def rotate(angle):
            chars = ["⌛", "⏳"]
            if overlay.winfo_exists():
                loader_label.config(text=chars[angle % 2])
                self.root.after(200, lambda: rotate(angle + 1))
        
        rotate(0)
        self.root.after(duration, overlay.destroy)
    
    def animate_window(self, window):
        """Animation d'ouverture en fondu fluide"""
        def fade_in(alpha):
            if alpha < 1.0:
                alpha += 0.08
                window.attributes('-alpha', alpha)
                window.after(10, fade_in, alpha)
            else:
                window.attributes('-alpha', 1.0)
        fade_in(0.0)
    
    def setup_styles(self):
        """Configurer les styles personnalisés avec un thème moderne"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurations des styles
        style.configure('TNotebook', background=self.colors["bg_main"], borderwidth=0)
        style.configure('TNotebook.Tab', padding=[20, 10])
        style.configure('TFrame', background=self.colors["bg_main"])
        style.configure('Card.TFrame', background=self.colors["bg_panel"])
        
        # Style Treeview amélioré
        style.configure('Treeview', 
                       background=self.colors["bg_panel"], 
                       foreground=self.colors["fg_text"], 
                       fieldbackground=self.colors["bg_panel"], 
                       rowheight=40,  # Plus d'espace pour l'élégance
                       font=("Segoe UI", 10),
                       borderwidth=0)
        style.configure('Treeview.Heading', background=self.colors["bg_main"], foreground=self.colors["accent"],
                        font=("Segoe UI", 10, "bold"), padding=[0, 10])
        style.map('Treeview', background=[('selected', self.colors["accent"])], foreground=[('selected', 'white')])
        
    def create_widgets(self):
        """Créer l'interface complète avec Sidebar Moderne"""
        # Conteneur principal
        main_container = tk.Frame(self.root, bg=self.colors["bg_main"])
        main_container.pack(fill=tk.BOTH, expand=True)

        # --- SIDEBAR (Gauche) ---
        sidebar_bg = self.colors["bg_panel"]
        sidebar = tk.Frame(main_container, bg=sidebar_bg, width=260)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # Logo/Titre avec design hiérarchique moderne
        title_container = tk.Frame(sidebar, bg=sidebar_bg)
        title_container.pack(pady=(45, 30), fill=tk.X)

        tk.Label(title_container, text="🎓", font=("Segoe UI", 32),
                 bg=sidebar_bg, fg=self.colors["accent"]).pack()

        # Petit badge stylisé pour le "MANAGER PRO"
        badge_frame = tk.Frame(title_container, bg=self.colors["badge_bg"], padx=10, pady=2)
        badge_frame.pack(pady=(15, 0))
        tk.Label(badge_frame, text="MANAGER PRO", font=("Segoe UI", 7, "bold"),
                 bg=self.colors["badge_bg"], fg=self.colors["badge_fg"]).pack()
        
        # Séparateur visuel
        sep = tk.Frame(sidebar, bg=self.colors["border"], height=2)
        sep.pack(fill=tk.X, padx=15, pady=15)
        
        self.sidebar_btns = {}

        # Menu Navigation avec icônes améliorées
        self.create_sidebar_btn(sidebar, "dashboard", "📊 Tableau de bord", lambda: self.show_page("dashboard"))
        self.create_sidebar_btn(sidebar, "gestion", "👥 Gestion Étudiants", lambda: self.show_page("gestion"))
        self.create_sidebar_btn(sidebar, "paiements", "💰 Paiements", lambda: self.show_page("paiements")) # Ajout du bouton Paiements
        
        # Restriction : Seul l'Admin peut exporter ou sauvegarder en dur
        if self.role == "Admin":
            self.create_sidebar_btn(sidebar, "users", "👤 Utilisateurs", lambda: self.show_page("users"))
            self.create_sidebar_btn(sidebar, "export", "📊 Exporter CSV", self.exporter_csv)
            self.create_sidebar_btn(sidebar, "save", "💾 Sauvegarder", self.sauvegarder_donnees)

        # Séparateur
        sep2 = tk.Frame(sidebar, bg=self.colors["border"], height=1)
        sep2.pack(fill=tk.X, padx=15, pady=10)
        
        # Spacer
        tk.Frame(sidebar, bg=sidebar_bg).pack(fill=tk.Y, expand=True)

        # BOUTON PARAMÈTRES (Placé en bas près de déconnexion)
        self.create_sidebar_btn(sidebar, "theme", "⚙️ Paramètres", self.toggle_theme)
        
        self.create_sidebar_btn(sidebar, "logout", "🚪 Déconnexion", self.deconnexion, is_danger=True)

        # --- CONTENU PRINCIPAL (Droite) avec meilleur espacement ---
        self.content_area = tk.Frame(main_container, bg=self.colors["bg_main"])
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Afficher la page par défaut
        self.current_page = ""
        self.show_page("dashboard")
        
    def create_gestion_view(self, parent):
        # En-tête de la vue avec meilleur design
        header = tk.Frame(parent, bg=self.colors["bg_main"])
        header.pack(fill=tk.X, pady=(0, 20))
        
        title_frame = tk.Frame(header, bg=self.colors["bg_main"])
        title_frame.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(title_frame, text="👥 Gestion des Étudiants", font=("Segoe UI", 22, "bold"),
                 bg=self.colors["bg_main"], fg=self.colors["accent"]).pack(anchor="w")
        tk.Label(title_frame, text="Administrez vos étudiants en toute simplicité", font=("Segoe UI", 9),
                 bg=self.colors["bg_main"], fg=self.colors["fg_text"]).pack(anchor="w", pady=(3, 0))

        # Barre de recherche premium
        search_frame = tk.Frame(header, bg=self.colors["bg_input"], relief=tk.SUNKEN, bd=1)
        search_frame.config(highlightthickness=1, highlightbackground=self.colors["border"])
        search_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Rendre l'icône loupe cliquable
        search_icon = tk.Label(search_frame, text="🔍", bg=self.colors["bg_input"], 
                              fg=self.colors["accent"], font=("Segoe UI", 11), cursor="hand2")
        search_icon.pack(side=tk.LEFT, padx=8, pady=8)
        search_icon.bind("<Button-1>", lambda e: self.filtrer_etudiants())
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                               font=("Segoe UI", 10), bg=self.colors["bg_input"], fg=self.colors["fg_text"], width=25, relief=tk.FLAT, insertbackground=self.colors["accent"], bd=0)
        search_entry.pack(side=tk.LEFT, padx=(0, 12), pady=8)
        
        # Support de la touche Entrée
        search_entry.bind("<Return>", lambda e: self.filtrer_etudiants())

        search_placeholder = "Rechercher..."
        search_entry.insert(0, search_placeholder)
        def on_focus_in(event):
            if search_entry.get() == search_placeholder:
                search_entry.delete(0, tk.END)
                search_entry.config(fg=self.colors["fg_text"])
        def on_focus_out(event):
            if search_entry.get() == "":
                search_entry.insert(0, search_placeholder)
                search_entry.config(fg="gray")
        search_entry.bind("<FocusIn>", on_focus_in)
        search_entry.bind("<FocusOut>", on_focus_out)
        
        # PanedWindow avec meilleur style
        self.paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)
        
        # Colonne gauche - Formulaire avec design card
        if self.role != "Professeur":
            left_frame = tk.Frame(self.paned, bg=self.colors["bg_panel"], relief=tk.RAISED, bd=1)
            left_frame.config(highlightthickness=1, highlightbackground=self.colors["border"])
            self.paned.add(left_frame, weight=1)
            
            # En-tête du panneau gauche avec design moderne
            header_left = tk.Frame(left_frame, bg=self.colors["bg_main"], height=50)
            header_left.pack(fill=tk.X)
            header_left.pack_propagate(False)
            tk.Label(header_left, text="➕ Ajouter/Modifier Étudiant", font=("Segoe UI", 12, "bold"), 
                     bg=self.colors["bg_main"], fg=self.colors["accent"], padx=20, pady=12).pack(anchor="w")
            
            # --- FORMULAIRE SCROLLABLE (Pour voir les boutons Enregistrer) ---
            form_canvas = tk.Canvas(left_frame, bg=self.colors["bg_panel"], highlightthickness=0)
            form_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=form_canvas.yview)
            self.scrollable_form_container = tk.Frame(form_canvas, bg=self.colors["bg_panel"])

            self.scrollable_form_container.bind(
                "<Configure>",
                lambda e: form_canvas.configure(scrollregion=form_canvas.bbox("all"))
            )

            form_canvas.create_window((0, 0), window=self.scrollable_form_container, anchor="nw", width=340)
            form_canvas.configure(yscrollcommand=form_scrollbar.set)

            form_scrollbar.pack(side="right", fill="y")
            form_canvas.pack(side="left", fill="both", expand=True)
            
            self.create_form(self.scrollable_form_container)

            # Activer le défilement avec la molette de la souris sur le formulaire
            def _on_mousewheel(event):
                form_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
            form_canvas.bind_all("<MouseWheel>", _on_mousewheel)
            
            # Initialiser le formulaire avec un matricule généré et les réglages par défaut
            self.reinitialiser_formulaire()
        
        # Colonne droite - Liste avec meilleur design
        right_frame = tk.Frame(self.paned, bg=self.colors["bg_panel"], relief=tk.RAISED, bd=1)
        right_frame.config(highlightthickness=1, highlightbackground=self.colors["border"])
        self.paned.add(right_frame, weight=3)

        # En-tête du panneau droit
        header_right = tk.Frame(right_frame, bg=self.colors["bg_main"], height=50)
        header_right.pack(fill=tk.X)
        header_right.pack_propagate(False)
        tk.Label(header_right, text="📋 Étudiants Enregistrés", font=("Segoe UI", 12, "bold"), 
                 bg=self.colors["bg_main"], fg=self.colors["accent"], padx=20, pady=12).pack(side=tk.LEFT)

        # Barre d'état inférieure avec meilleur design
        status_frame = tk.Frame(right_frame, bg=self.colors["bg_main"], height=50, relief=tk.SUNKEN, bd=1)
        status_frame.config(highlightthickness=1, highlightbackground=self.colors["border"])
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="", bg=self.colors["bg_main"], fg=self.colors["accent"], 
                                    font=("Segoe UI", 10, "bold"), padx=15)
        self.status_label.pack(side=tk.LEFT, pady=12)
        
        # Boutons de gestion de la sélection (à droite)
        manage_frame = tk.Frame(status_frame, bg=self.colors["bg_main"])
        manage_frame.pack(side=tk.RIGHT, padx=15, pady=8)
        
        self.create_styled_button(manage_frame, "🖨️ Imprimer PDF", self.menu_impression_pdf, "#2c3e50").pack(side=tk.LEFT, padx=4)
        self.create_styled_button(manage_frame, "📧 Email", self.envoyer_email, "#9b59b6").pack(side=tk.LEFT, padx=4)
        
        if self.role != "Professeur":
            self.create_styled_button(manage_frame, "✏️ Modifier", self.modifier_etudiant, self.colors["warning"]).pack(side=tk.LEFT, padx=4)
            
        if self.role == "Admin":
            self.create_styled_button(manage_frame, "🗑️ Supprimer", self.supprimer_etudiant, self.colors["danger"]).pack(side=tk.LEFT, padx=4)

        # Liste des étudiants
        list_frame = tk.Frame(right_frame, bg=self.colors["bg_panel"]) # Panel pour la liste
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Conteneur du tableau
        tree_container = tk.Frame(list_frame, bg=self.colors["bg_panel"])
        tree_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Scrollbar premium
        scrollbar = ttk.Scrollbar(tree_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview avec colonnes optimisées
        self.tree = ttk.Treeview(tree_container, columns=("Matricule", "Nom", "Prénom", "Filière", "Niveau", "Âge", "Moyenne", "Appréciation"), 
                                 height=15, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("Matricule", anchor=tk.CENTER, width=85)
        self.tree.column("Nom", anchor=tk.W, width=90)
        self.tree.column("Prénom", anchor=tk.W, width=90)
        self.tree.column("Filière", anchor=tk.CENTER, width=80)
        self.tree.column("Niveau", anchor=tk.CENTER, width=60)
        self.tree.column("Âge", anchor=tk.CENTER, width=55)
        self.tree.column("Moyenne", anchor=tk.CENTER, width=85)
        self.tree.column("Appréciation", anchor=tk.CENTER, width=110)
        
        self.tree.heading("#0", text="", anchor=tk.W)
        for col in ["Matricule", "Nom", "Prénom", "Filière", "Niveau", "Âge", "Moyenne", "Appréciation"]:
            self.tree.heading(col, text=col, anchor=tk.CENTER, 
                            command=lambda c=col: self.trier_colonne(c, False))
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # On active la recherche UNIQUEMENT une fois que le tableau (self.tree) est prêt
        self.search_var.trace_add('write', self.filtrer_etudiants)

        # Menu contextuel (Clic Droit)
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="📧 Envoyer Email", command=self.envoyer_email)
        
        if self.role != "Professeur":
            self.context_menu.add_command(label="✏️ Modifier", command=self.modifier_etudiant)
        if self.role == "Admin":
            self.context_menu.add_command(label="️ Supprimer", command=self.supprimer_etudiant)
            
        self.tree.bind("<Button-3>", self.afficher_menu_contextuel)
        
        self.rafraichir()

    def show_page(self, page_name):
        """Changer de page dans la zone principale avec animation"""
        if self.current_page == page_name:
            return
            
        self.current_page = page_name
        
        # S'assurer que les données sont à jour avant d'afficher la page
        if page_name == "gestion":
            self.etudiants_filtres = self.etudiants.copy()
        
        # Mettre à jour l'apparence des boutons de navigation
        for name, btn in self.sidebar_btns.items():
            if name == page_name:
                btn.config(bg=self.colors["bg_main"], fg=self.colors["accent"], font=("Segoe UI", 11, "bold"))
            elif name not in ["export", "save", "theme", "logout"]: 
                btn.config(bg=self.colors["bg_panel"], fg=self.colors["fg_text"], font=("Segoe UI", 11))

        # Supprimer le contenu actuel
        for widget in self.content_area.winfo_children():
            widget.destroy()
            
        # Créer un conteneur pour la nouvelle page
        page_container = tk.Frame(self.content_area, bg=self.colors["bg_main"])
        
        # Charger le contenu selon la page demandée dans le conteneur animé
        if page_name == "dashboard":
            self.create_dashboard_view(page_container)
        elif page_name == "gestion":
            self.create_gestion_view(page_container)
        elif page_name == "paiements": # Ajout de la logique de navigation pour la page Paiements
            self.create_paiements_view(page_container)
        elif page_name == "users":
            self.create_users_view(page_container)

        # Lancer l'animation de transition
        self.animate_page_transition(page_container)

    def animate_page_transition(self, container):
        """Anime l'apparition d'une page avec effet Slide Up & Easing professionnel"""
        def slide(step):
            if step > 0:
                # Réduction exponentielle du pas pour l'effet d'amorti (easing)
                container.place(relx=0, rely=step**2, relwidth=1, relheight=1)
                self.root.after(10, lambda: slide(step - 0.015))
            else:
                container.place_forget()
                container.pack(fill=tk.BOTH, expand=True)

        container.place(relx=0, rely=1, relwidth=1, relheight=1) # Commence en bas
        slide(0.3) # Déclenche le slide

    def create_dashboard_view(self, parent):
        """Créer la vue Tableau de Bord avec design moderne"""
        # En-tête élégant
        header_frame = tk.Frame(parent, bg=self.colors["bg_main"])
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        tk.Label(header_frame, text="📊 Tableau de Bord", font=("Segoe UI", 26, "bold"),
                 bg=self.colors["bg_main"], fg=self.colors["accent"]).pack(anchor="w")
        tk.Label(header_frame, text="Vue d'ensemble de vos étudiants", font=("Segoe UI", 10),
                 bg=self.colors["bg_main"], fg=self.colors["fg_text"]).pack(anchor="w", pady=(5, 0))

        # Calcul des statistiques avancées
        total = len(self.etudiants)
        actifs = len([e for e in self.etudiants if e.get("statut") == "Actif"])
        suspendus = len([e for e in self.etudiants if e.get("statut") == "Suspendu"])
        moyennes = [sum(e.get("note", []))/len(e.get("note", [])) for e in self.etudiants if e.get("note")]
        moy_gen = sum(moyennes)/len(moyennes) if moyennes else 0

        # Zone défilante si nécessaire
        main_scroll = tk.Frame(parent, bg=self.colors["bg_main"])
        main_scroll.pack(fill=tk.BOTH, expand=True)

        # --- 1. CARTES DE STATISTIQUES (ANIMÉES) ---
        cards_frame = tk.Frame(main_scroll, bg=self.colors["bg_main"])
        cards_frame.pack(fill=tk.X, pady=(0, 25))
        
        self.create_stat_card(cards_frame, "Total", str(total), "👥").pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.create_stat_card(cards_frame, "Actifs", str(actifs), "🟢").pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.create_stat_card(cards_frame, "Suspendus", str(suspendus), "🔴", on_click=self.show_suspendus).pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.create_stat_card(cards_frame, "Moyenne", f"{moy_gen:.1f}", "📊").pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # --- 2. GRAPHIQUES (Pie & Bar) ---
        graphs_container = tk.Frame(main_scroll, bg=self.colors["bg_main"])
        graphs_container.pack(fill=tk.X, pady=(0, 25))

        # Graphique de répartition (Gauche)
        left_col = tk.Frame(graphs_container, bg=self.colors["bg_panel"], relief=tk.FLAT, bd=0)
        left_col.config(highlightthickness=1, highlightbackground=self.colors["border"])
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(left_col, text="📊 Répartition par Mention", font=("Segoe UI", 12, "bold"), 
                 bg=self.colors["bg_panel"], fg=self.colors["accent"], pady=15).pack()
        
        chart_area = tk.Frame(left_col, bg=self.colors["bg_panel"])
        chart_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.render_pie_chart(chart_area, moyennes)

        # Graphique Top 5 (Droite)
        right_col = tk.Frame(graphs_container, bg=self.colors["bg_panel"], relief=tk.FLAT, bd=0)
        right_col.config(highlightthickness=1, highlightbackground=self.colors["border"])
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        tk.Label(right_col, text="⭐ Top 5 Étudiants", font=("Segoe UI", 12, "bold"), 
                 bg=self.colors["bg_panel"], fg=self.colors["accent"], pady=15).pack()
        
        bar_area = tk.Frame(right_col, bg=self.colors["bg_panel"])
        bar_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.render_bar_chart(bar_area)

        # --- 3. DERNIÈRES INSCRIPTIONS (Pleine largeur) ---
        enroll_container = tk.Frame(main_scroll, bg=self.colors["bg_panel"], relief=tk.FLAT, bd=0)
        enroll_container.config(highlightthickness=1, highlightbackground=self.colors["border"])
        enroll_container.pack(fill=tk.X, pady=(0, 20))

        tk.Label(enroll_container, text="🕒 Dernières Inscriptions", font=("Segoe UI", 12, "bold"), 
                 bg=self.colors["bg_panel"], fg=self.colors["accent"], pady=15).pack()

        enroll_table = tk.Frame(enroll_container, bg=self.colors["bg_panel"], padx=20, pady=10)
        enroll_table.pack(fill=tk.BOTH, expand=True)

        # Récupérer les 5 dernières inscriptions
        last_students = sorted(self.etudiants, key=lambda x: x.get("date_ajout", ""), reverse=True)[:5]
        
        if last_students:
            for i, s in enumerate(last_students):
                row = tk.Frame(enroll_table, bg=self.colors["bg_panel"])
                row.pack(fill=tk.X, pady=5)
                
                # Badge couleur pour le statut
                status_color = self.colors["success"] if s.get("statut") == "Actif" else self.colors["danger"]
                tk.Label(row, text="●", fg=status_color, bg=self.colors["bg_panel"], font=("Arial", 12)).pack(side=tk.LEFT, padx=(0, 10))
                
                tk.Label(row, text=f"{s['prenom']} {s['nom']}", font=("Segoe UI", 10, "bold"), 
                         bg=self.colors["bg_panel"], fg=self.colors["fg_head"]).pack(side=tk.LEFT)
                
                tk.Label(row, text=s.get("date_ajout", ""), font=("Segoe UI", 8), 
                         bg=self.colors["bg_panel"], fg=self.colors["fg_text"]).pack(side=tk.RIGHT)
                
                if i < len(last_students) - 1:
                    tk.Frame(enroll_table, bg=self.colors["border"], height=1).pack(fill=tk.X, pady=2)
        else:
            tk.Label(enroll_table, text="Aucune donnée disponible", bg=self.colors["bg_panel"], 
                     fg=self.colors["fg_text"]).pack(expand=True)

    def render_pie_chart(self, parent, moyennes):
        """Génère le graphique de répartition"""
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        mentions = {"Exc": 0, "TB": 0, "B": 0, "AB": 0, "P": 0, "I": 0}
        for m in moyennes:
            if m >= 18: mentions["Exc"] += 1
            elif m >= 16: mentions["TB"] += 1
            elif m >= 14: mentions["B"] += 1
            elif m >= 12: mentions["AB"] += 1
            elif m >= 10: mentions["P"] += 1
            else: mentions["I"] += 1
            
        labels = [k for k, v in mentions.items() if v > 0]
        sizes = [v for v in mentions.values() if v > 0]
        
        # COULEURS DYNAMIQUES : Les graphiques s'adaptent à la palette du thème sélectionné
        chart_colors = [
            self.colors["success"], 
            self.adjust_color(self.colors["success"], 0.8),
            self.colors["accent"], 
            self.adjust_color(self.colors["accent"], 0.8),
            self.colors["warning"], 
            self.colors["danger"]
        ]
        
        if sizes:
            fig = plt.Figure(figsize=(3, 3), dpi=100)
            fig.patch.set_facecolor(self.colors["bg_panel"])
            ax = fig.add_subplot(111)
            ax.set_facecolor(self.colors["bg_panel"])
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.0f%%', 
                                            startangle=90, colors=chart_colors[:len(sizes)], 
                                            textprops={'color': self.colors["fg_text"], 'fontsize': 8})
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            tk.Label(parent, text="Données insuffisantes", bg=self.colors["bg_panel"], 
                     fg=self.colors["fg_text"]).pack(expand=True)

    def render_bar_chart(self, parent):
        """Génère le graphique du Top 5 des étudiants"""
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        top_students = sorted(self.etudiants, key=lambda x: sum(x.get("note", []))/len(x.get("note", [])) if x.get("note") else 0, reverse=True)[:5]

        if top_students:
            names = [s['prenom'] for s in top_students]
            vals = [sum(s.get("note", []))/len(s.get("note", [])) for s in top_students]

            fig = plt.Figure(figsize=(4, 3), dpi=100)
            fig.patch.set_facecolor(self.colors["bg_panel"])
            ax = fig.add_subplot(111)
            ax.set_facecolor(self.colors["bg_panel"])
            
            bar_colors = [self.colors["accent"], "#7dd3fc", self.colors["success"], "#86efac", "#fca5a5"]
            bars = ax.bar(names, vals, color=bar_colors[:len(vals)])
            
            ax.set_ylim(0, 20)
            ax.tick_params(axis='x', colors=self.colors["fg_text"], labelsize=9)
            ax.tick_params(axis='y', colors=self.colors["fg_text"], labelsize=9)
            ax.spines['bottom'].set_color(self.colors["border"])
            ax.spines['left'].set_color(self.colors["border"])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.grid(axis='y', alpha=0.1, color=self.colors["fg_text"])
            
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}', ha='center', va='bottom', 
                        color=self.colors["fg_text"], fontsize=8, fontweight='bold')
            
            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            tk.Label(parent, text="Données insuffisantes", bg=self.colors["bg_panel"], 
                     fg=self.colors["fg_text"]).pack(expand=True)

    def create_stat_card(self, parent, title, value, icon, on_click=None):
        """Créer une carte de statistique avec effet de survol Premium"""
        frame = tk.Frame(parent, bg=self.colors["bg_panel"], relief=tk.FLAT, bd=0)
        frame.config(highlightthickness=1, highlightbackground=self.colors["border"])

        inner = tk.Frame(frame, bg=self.colors["bg_panel"], padx=25, pady=22)
        inner.pack(fill=tk.BOTH, expand=True)

        icon_label = tk.Label(inner, text=icon, font=("Segoe UI", 32), bg=self.colors["bg_panel"], fg=self.colors["accent"])
        icon_label.pack(side=tk.LEFT, padx=(0, 20))

        content = tk.Frame(inner, bg=self.colors["bg_panel"])
        content.pack(side=tk.LEFT, fill=tk.Y, expand=True)

        tk.Label(content, text=title, font=("Segoe UI", 11), bg=self.colors["bg_panel"], fg=self.colors["fg_text"]).pack(anchor="w")
        tk.Label(content, text=value, font=("Segoe UI", 20, "bold"), bg=self.colors["bg_panel"], fg=self.colors["fg_head"]).pack(anchor="w", pady=(5, 0))

        def on_enter(e):
            # Effet de survol Premium : Bordure accentuée et éclaircissement dynamique du fond
            hover_bg = self.adjust_color(self.colors["bg_panel"], 1.1)
            frame.config(highlightbackground=self.colors["accent"], highlightthickness=2, bg=hover_bg)
            inner.config(bg=hover_bg)
            for widget in inner.winfo_children():
                widget.config(bg=hover_bg)

        def on_leave(e):
            frame.config(highlightbackground=self.colors["border"], highlightthickness=1)

            inner.config(bg=self.colors["bg_panel"])
            for widget in inner.winfo_children():
                widget.config(bg=self.colors["bg_panel"])
                
        def bind_click(widget):
            widget.bind("<Button-1>", lambda e: on_click())

        if on_click:
            frame.config(cursor="hand2")
            bind_click(frame)
            bind_click(inner)
            bind_click(icon_label)
            bind_click(content)
            for child in content.winfo_children():
                bind_click(child)

        inner.bind("<Enter>", on_enter)
        inner.bind("<Leave>", on_leave)

        return frame

    def generer_matricule(self):
        """Génère un matricule automatique au format YYYY-NNN"""
        year = datetime.now().year
        prefix = f"{year}-"
        max_seq = 0
        try:
            with db_session() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT matricule FROM etudiants WHERE matricule LIKE {DB_P}", (f"{prefix}%",))
                for row in cursor.fetchall():
                    try:
                        parts = str(row[0]).split('-')
                        if len(parts) == 2:
                            seq = int(parts[1])
                            if seq > max_seq:
                                max_seq = seq
                    except (ValueError, IndexError):
                        continue
        except Exception as e:
            print(f"Erreur génération matricule: {e}")
            
        return f"{prefix}{str(max_seq + 1).zfill(3)}"

    def create_sidebar_btn(self, parent, name, text, command, is_danger=False):
        bg_color = self.colors["bg_panel"]
        fg_color = self.colors["fg_text"]
        hover_color = self.colors["bg_main"]
        
        if is_danger:
            fg_color = self.colors["danger"]
            hover_color = self.colors["danger"]

        btn = tk.Button(parent, text=text, command=command,
                       bg=bg_color, fg=fg_color, font=("Segoe UI", 11, "bold"),
                       relief=tk.FLAT, activebackground=hover_color, 
                       activeforeground="white" if not is_danger else self.colors["danger"],
                       anchor="w", padx=30, pady=14, cursor="hand2", borderwidth=0,
                       highlightthickness=0, bd=0)
        btn.pack(fill=tk.X, pady=3, padx=10)
        self.sidebar_btns[name] = btn
        
        if not is_danger:
            def on_enter(e): 
                btn['bg'] = hover_color
                btn['fg'] = self.colors["accent"]
            def on_leave(e): 
                if self.current_page != name:
                    btn['bg'] = bg_color
                    btn['fg'] = fg_color
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            
    def notify(self, message, n_type="success"):
        """Système de notifications qui s'empilent et s'animent (Stacked Toasts)"""
        configs = {
            "success": {"bg": self.colors["success"], "icon": "✅"},
            "error": {"bg": self.colors["danger"], "icon": "❌"},
            "warning": {"bg": self.colors["warning"], "icon": "⚠️"},
            "info": {"bg": self.colors["accent"], "icon": "ℹ️"}
        }
        conf = configs.get(n_type, configs["info"])
        
        # Création du toast
        toast = tk.Frame(self.root, bg=conf["bg"], padx=18, pady=12, highlightthickness=1, highlightbackground="white")
        self.active_notifications.append(toast)
        
        # Calcul de la position cible basée sur l'empilement (2% du haut + 8% par notification)
        index = len(self.active_notifications) - 1
        target_y = 0.02 + (index * 0.08)
        
        toast.place(relx=0.98, rely=-0.1, anchor="ne")
        
        tk.Label(toast, text=conf["icon"], bg=conf["bg"], fg="white", font=("Segoe UI", 12)).pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(toast, text=message, bg=conf["bg"], fg="white", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
        
        # Animation de descente vers la position cible
        def slide_in(current_y):
            if not toast.winfo_exists(): return
            if current_y < target_y:
                current_y += 0.01
                toast.place(relx=0.98, rely=current_y, anchor="ne")
                self.root.after(10, lambda: slide_in(current_y))
            else:
                toast.place(relx=0.98, rely=target_y, anchor="ne")
        
        slide_in(-0.1)
        
        # Auto-destruction et réorganisation
        def cleanup():
            if toast.winfo_exists():
                self.active_notifications.remove(toast)
                toast.destroy()
                self.reorganize_notifications()
        
        self.root.after(4000, cleanup)

    def reorganize_notifications(self):
        """Réajuste la position de toutes les notifications actives après une suppression"""
        # On nettoie la liste pour ne garder que les notifications qui existent encore réellement
        self.active_notifications = [t for t in self.active_notifications if t.winfo_exists()]
        for i, toast in enumerate(self.active_notifications):
            target_y = 0.02 + (i * 0.08)
            toast.place(relx=0.98, rely=target_y, anchor="ne")

    def create_form(self, parent):
        """Créer le formulaire avec design moderne et élégant"""
        # --- Conteneur principal du formulaire ---
        form_container = tk.Frame(parent, bg=self.colors["bg_panel"])
        form_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=15)
        
        # --- Section 1 : Informations Personnelles ---
        sec1_title = tk.Label(form_container, text="📝 Infos Personnelles", 
                             font=("Segoe UI", 11, "bold"), bg=self.colors["bg_panel"], fg=self.colors["accent"])
        sec1_title.pack(anchor="w", pady=(0, 10))
        
        sep1 = tk.Frame(form_container, bg=self.colors["border"], height=1)
        sep1.pack(fill=tk.X, pady=(0, 12))
        
        # Conteneur pour info personnelles et photo
        info_container = tk.Frame(form_container, bg=self.colors["bg_panel"]) # Retrait de expand=True pour ne pas pousser le reste
        info_container.pack(fill=tk.BOTH, expand=True)
        
        # --- Colonne Droite : Photo (Packé en premier pour réserver l'espace à droite) ---
        photo_frame = tk.Frame(info_container, bg=self.colors["bg_panel"])
        photo_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0), anchor=tk.N)
        
        tk.Label(photo_frame, text="📷 Photo", font=("Segoe UI", 10, "bold"), 
                bg=self.colors["bg_panel"], fg=self.colors["accent"]).pack(pady=(0, 8))
        
        # Canvas pour afficher la photo avec meilleur design
        self.photo_canvas = tk.Canvas(photo_frame, width=130, height=130, bg=self.colors["bg_input"], 
                                      highlightthickness=2, highlightbackground=self.colors["border"], 
                                      highlightcolor=self.colors["accent"])
        self.photo_canvas.pack(pady=(0, 12))
        self.photo_canvas.create_text(67, 67, text="Aucune\nPhoto", fill="gray", justify=tk.CENTER, font=("Segoe UI", 9))
        
        # Boutons sous la photo
        self.create_styled_button(photo_frame, " Parcourir...", self.choisir_photo, self.colors["accent"]).pack(fill=tk.X, padx=0, pady=(0, 3))
        self.create_styled_button(photo_frame, "📸 Webcam", self.capturer_webcam, self.colors["accent"]).pack(fill=tk.X, padx=0, pady=(0, 3))

        # --- Colonne Gauche : Champs de saisie ---
        inputs_frame = tk.Frame(info_container, bg=self.colors["bg_panel"])
        inputs_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Matricule
        tk.Label(inputs_frame, text="Matricule:", font=("Segoe UI", 9, "bold"), bg=self.colors["bg_panel"], 
                fg=self.colors["accent"]).pack(anchor=tk.W, pady=(0, 3))
        self.matricule_entry = tk.Entry(inputs_frame, width=30, font=("Segoe UI", 10, "bold"), 
                                        bg=self.colors["bg_input"], fg=self.colors["accent"], insertbackground=self.colors["accent"], relief=tk.FLAT)
        self.matricule_entry.pack(anchor=tk.W, pady=(0, 8), ipady=4)
        
        # Nom
        tk.Label(inputs_frame, text="Nom:", font=("Segoe UI", 9, "bold"), bg=self.colors["bg_panel"], 
                fg=self.colors["accent"]).pack(anchor=tk.W, pady=(0, 3))
        self.nom_entry = tk.Entry(inputs_frame, width=30, font=("Segoe UI", 10), 
                                  bg=self.colors["bg_input"], fg="white", insertbackground=self.colors["accent"], relief=tk.FLAT)
        self.nom_entry.pack(anchor=tk.W, pady=(0, 8), ipady=4)
        
        # Prénom
        tk.Label(inputs_frame, text="Prénom:", font=("Segoe UI", 9, "bold"), bg=self.colors["bg_panel"], 
                fg=self.colors["accent"]).pack(anchor=tk.W, pady=(0, 3))
        self.prenom_entry = tk.Entry(inputs_frame, width=30, font=("Segoe UI", 10), 
                                     bg=self.colors["bg_input"], fg="white", insertbackground=self.colors["accent"], relief=tk.FLAT)
        self.prenom_entry.pack(anchor=tk.W, pady=(0, 8), ipady=4)
        
        # Email
        tk.Label(inputs_frame, text="Email:", font=("Segoe UI", 9, "bold"), bg=self.colors["bg_panel"], 
                fg=self.colors["accent"]).pack(anchor=tk.W, pady=(0, 3))
        self.email_entry = tk.Entry(inputs_frame, width=30, font=("Segoe UI", 10), 
                                     bg=self.colors["bg_input"], fg="white", insertbackground=self.colors["accent"], relief=tk.FLAT)
        self.email_entry.pack(anchor=tk.W, pady=(0, 8), ipady=4)
        
        # Téléphone
        tk.Label(inputs_frame, text="Téléphone:", font=("Segoe UI", 9, "bold"), bg=self.colors["bg_panel"], 
                fg=self.colors["accent"]).pack(anchor=tk.W, pady=(0, 3))
        self.telephone_entry = tk.Entry(inputs_frame, width=30, font=("Segoe UI", 10), 
                                     bg=self.colors["bg_input"], fg="white", insertbackground=self.colors["accent"], relief=tk.FLAT)
        self.telephone_entry.pack(anchor=tk.W, pady=(0, 8), ipady=4)
        
        # Âge
        tk.Label(inputs_frame, text="Âge:", font=("Segoe UI", 9, "bold"), bg=self.colors["bg_panel"], 
                fg=self.colors["accent"]).pack(anchor=tk.W, pady=(0, 3))
        self.age_entry = tk.Entry(inputs_frame, width=30, font=("Segoe UI", 10), 
                                  bg=self.colors["bg_input"], fg="white", insertbackground=self.colors["accent"], relief=tk.FLAT)
        self.age_entry.pack(anchor=tk.W, pady=(0, 8), ipady=4)
        
        # Filière
        tk.Label(inputs_frame, text="Filière:", font=("Segoe UI", 9, "bold"), bg=self.colors["bg_panel"], 
                fg=self.colors["accent"]).pack(anchor=tk.W, pady=(0, 3))
        self.filiere_entry = tk.Entry(inputs_frame, width=30, font=("Segoe UI", 10), 
                                     bg=self.colors["bg_input"], fg="white", insertbackground=self.colors["accent"], relief=tk.FLAT)
        self.filiere_entry.pack(anchor=tk.W, pady=(0, 8), ipady=4)

        # Niveau
        tk.Label(inputs_frame, text="Niveau:", font=("Segoe UI", 9, "bold"), bg=self.colors["bg_panel"], 
                fg=self.colors["accent"]).pack(anchor=tk.W, pady=(0, 3))
        self.niveau_var = tk.StringVar(value="L1")
        self.niveau_menu = ttk.Combobox(inputs_frame, textvariable=self.niveau_var, values=["L1", "L2", "L3", "M1", "M2"], state="readonly")
        self.niveau_menu.pack(anchor=tk.W, pady=(0, 8), ipady=2, fill=tk.X)

        # Statut (Nouveau champ pour le Dashboard)
        tk.Label(inputs_frame, text="Statut:", font=("Segoe UI", 9, "bold"), bg=self.colors["bg_panel"], 
                fg=self.colors["accent"]).pack(anchor=tk.W, pady=(0, 3))
        self.statut_var = tk.StringVar(value="Actif")
        self.statut_menu = ttk.Combobox(inputs_frame, textvariable=self.statut_var, values=["Actif", "Suspendu"], state="readonly", font=("Segoe UI", 10))
        self.statut_menu.pack(anchor=tk.W, pady=(0, 8), ipady=2, fill=tk.X)

        
        # --- Section 2 : Évaluation ---
        sec2_title = tk.Label(form_container, text="📊 Évaluation Académique", 
                             font=("Segoe UI", 11, "bold"), bg=self.colors["bg_panel"], fg=self.colors["accent"])
        sec2_title.pack(anchor="w", pady=(20, 10))
        
        sep2 = tk.Frame(form_container, bg=self.colors["border"], height=1)
        sep2.pack(fill=tk.X, pady=(0, 12))
        
        # Notes (grid 2 colonnes)
        notes_container = tk.Frame(form_container, bg=self.colors["bg_panel"])
        notes_container.pack(fill=tk.X)
        
        # Colonne gauche notes
        left_notes = tk.Frame(notes_container, bg=self.colors["bg_panel"])
        left_notes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        
        tk.Label(left_notes, text="Nombre de notes:", font=("Segoe UI", 9, "bold"), bg=self.colors["bg_panel"], 
                fg=self.colors["accent"]).pack(anchor=tk.W, pady=(0, 3))
        self.nb_notes_entry = tk.Entry(left_notes, width=15, font=("Segoe UI", 10), 
                                       bg=self.colors["bg_input"], fg="white", insertbackground=self.colors["accent"], relief=tk.FLAT)
        self.nb_notes_entry.pack(anchor=tk.W, pady=(0, 12), ipady=6, fill=tk.X)
        
        # Colonne droite notes
        right_notes = tk.Frame(notes_container, bg=self.colors["bg_panel"])
        right_notes.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))
        
        tk.Label(right_notes, text="Notes (séparées par virgules):", font=("Segoe UI", 9, "bold"), 
                bg=self.colors["bg_panel"], fg=self.colors["accent"]).pack(anchor=tk.W, pady=(0, 3))
        self.notes_entry = tk.Text(right_notes, width=20, height=2, font=("Segoe UI", 9), 
                                   bg=self.colors["bg_input"], fg="white", insertbackground=self.colors["accent"], relief=tk.FLAT)
        self.notes_entry.pack(anchor=tk.W, pady=(0, 0), ipady=4, fill=tk.BOTH, expand=True)
        sep3 = tk.Frame(form_container, bg=self.colors["border"], height=1)
        sep3.pack(fill=tk.X, pady=(10, 15))
        
        button_frame = tk.Frame(form_container, bg=self.colors["bg_panel"])
        button_frame.pack(anchor=tk.W, pady=0, fill=tk.X)
        
        self.btn_valider = self.create_styled_button(button_frame, "➕ Enregistrer", self.gerer_validation, self.colors["success"])
        self.btn_valider.pack(side=tk.LEFT, padx=3, pady=5)
        self.create_styled_button(button_frame, "🔄 Réinitialiser", self.reinitialiser_formulaire, "#95a5a6").pack(side=tk.LEFT, padx=3, pady=5)
        
    def create_styled_button(self, parent, text, command, bg_color):
        """Créer un bouton stylisé avec effet de survol premium"""
        btn = tk.Button(parent, text=text, command=command,
                       bg=bg_color, fg="white", font=("Segoe UI", 10, "bold"),
                       relief=tk.FLAT, activebackground=bg_color, activeforeground="white",
                       padx=18, pady=10, cursor="hand2", borderwidth=0,
                       highlightthickness=0, bd=0, overrelief=tk.RAISED)
        
        # Effet de survol avec éclaircissement
        def on_enter(e):
            # Éclaircissement de la couleur
            color_map = {
                "#27ae60": "#2ecc71", "#95a5a6": "#bdc3c7", "#3498db": "#5dade2",
                "#9b59b6": "#af7ac5", "#16a085": "#1abc9c", "#e74c3c": "#ec7063",
                "#f39c12": "#f1c40f", "#c0392b": "#e74c3c", "#38BDF8": "#7dd3fc",
                "#4ADE80": "#86efac", "#FBBF24": "#fcd34d", "#F87171": "#fca5a5"
            }
            btn['bg'] = color_map.get(bg_color, bg_color)
            btn.config(relief=tk.SUNKEN)
            
        def on_leave(e):
            btn['bg'] = bg_color
            btn.config(relief=tk.FLAT)
            
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    def choisir_photo(self):
        """Ouvrir un dialogue pour choisir une image"""
        filename = filedialog.askopenfilename(
            title="Choisir une photo de profil",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        
        if filename:
            self.afficher_photo_preview(filename)
            self.current_photo_path = filename

    def capturer_webcam(self):
        """Ouvrir une fenêtre de capture webcam"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Erreur", "Impossible d'accéder à la webcam")
            return

        webcam_win = tk.Toplevel(self.root)
        webcam_win.title("Capture Photo de Profil")
        webcam_win.geometry("500x560")
        webcam_win.config(bg=self.colors["bg_main"])
        webcam_win.grab_set()  # Fenêtre modale

        video_label = tk.Label(webcam_win, bg="black")
        video_label.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        def update_frame():
            ret, frame = cap.read()
            if ret:
                frame = cv2.flip(frame, 1)  # Effet miroir
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                img = img.resize((480, 360))
                self.tk_webcam_img = ImageTk.PhotoImage(image=img)
                video_label.configure(image=self.tk_webcam_img)
                video_label.after(10, update_frame)
        
        def take_snapshot():
            ret, frame = cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                if not os.path.exists("temp"):
                    os.makedirs("temp")
                temp_path = os.path.join("temp", f"webcam_{datetime.now().strftime('%H%M%S')}.jpg")
                cv2.imwrite(temp_path, frame)
                
                self.current_photo_path = temp_path
                self.afficher_photo_preview(temp_path)
                close_webcam()

        def close_webcam():
            cap.release()
            webcam_win.destroy()

        btn_frame = tk.Frame(webcam_win, bg=self.colors["bg_main"])
        btn_frame.pack(pady=20)
        self.create_styled_button(btn_frame, "📸 Capturer", take_snapshot, self.colors["success"]).pack(side=tk.LEFT, padx=10)
        self.create_styled_button(btn_frame, "❌ Annuler", close_webcam, self.colors["danger"]).pack(side=tk.LEFT, padx=10)

        webcam_win.protocol("WM_DELETE_WINDOW", close_webcam)
        update_frame()

    def afficher_photo_preview(self, path):
        """Afficher l'aperçu de la photo dans le canvas"""
        try:
            image = Image.open(path)
            # Redimensionner en gardant le ratio
            image.thumbnail((120, 120))
            self.photo_preview = ImageTk.PhotoImage(image)
            
            self.photo_canvas.delete("all")
            self.photo_canvas.create_image(60, 60, image=self.photo_preview, anchor=tk.CENTER)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger l'image: {e}")
            self.notify(f"Impossible de charger l'image: {e}", "error")

    def gerer_validation(self):
        """Diriger vers ajout ou modification selon le mode"""
        if self.editing_matricule is not None:
            self.sauvegarder_modification()
        else:
            self.ajouter_etudiant()
            
    def ajouter_etudiant(self):
        """Ajouter un nouvel étudiant avec validation améliorée"""
        try:
            matricule = self.matricule_entry.get().strip()
            if not matricule:
                matricule = self.generer_matricule()
                
            nom = self.nom_entry.get().strip().capitalize()
            prenom = self.prenom_entry.get().strip().capitalize()
            email = self.email_entry.get().strip()
            telephone = self.telephone_entry.get().strip()
            filiere = self.filiere_entry.get().strip().upper()
            niveau = self.niveau_var.get()
            
            age_str = self.age_entry.get().strip()
            if not age_str:
                self.notify("L'âge est obligatoire", "error")
                return
            age = int(age_str)
            
            if not nom or not prenom:
                self.notify("Le nom et le prénom sont obligatoires", "error")
                return
            
            self.show_loader_overlay("Enregistrement en cours...")
                
            if age < 15 or age > 40:
                self.notify("L'âge doit être entre 15 et 40 ans", "error")
                return
            
            # Vérification de l'unicité du matricule directement dans la base de données
            with db_session() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT matricule FROM etudiants WHERE matricule = {DB_P}", (matricule,))
                if cursor.fetchone():
                    self.notify(f"Le matricule '{matricule}' est déjà utilisé.", "error")
                    return

            # Traiter les notes
            notes_text = self.notes_entry.get("1.0", tk.END).strip()
            notes = []
            if notes_text:
                try:
                    notes = [float(n.strip()) for n in notes_text.split(",") if n.strip()]
                    for note in notes:
                        if note < 0 or note > 20:
                            self.notify("Les notes doivent être entre 0 et 20", "error")
                            return
                except ValueError:
                    self.notify("Veuillez entrer des nombres valides pour les notes", "error")
                    return
            
            # Sauvegarde de la photo
            photo_dest = ""
            if self.current_photo_path:
                ext = os.path.splitext(self.current_photo_path)[1]
                filename = f"{matricule}{ext}"
                photo_dest = os.path.join("photos", filename)
                shutil.copy(self.current_photo_path, photo_dest)

            # Sauvegarde en Base de Données
            with db_session() as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    INSERT INTO etudiants (matricule, nom, prenom, age, note, photo, date_ajout, email, telephone, statut, filiere, niveau)
                    VALUES ({DB_P},{DB_P},{DB_P},{DB_P},{DB_P},{DB_P},{DB_P},{DB_P},{DB_P},{DB_P},{DB_P},{DB_P})""", 
                    (matricule, nom, prenom, age, json.dumps(notes), 
                     photo_dest, datetime.now().strftime("%d/%m/%Y %H:%M"), email, telephone, self.statut_var.get(), filiere, niveau))

            etudiant = {
                "matricule": matricule,
                "nom": nom,
                "prenom": prenom,
                "email": email,
                "telephone": telephone,
                "age": age,
                "note": notes,
                "filiere": filiere,
                "niveau": niveau,
                "statut": self.statut_var.get(),
                "photo": photo_dest,
                "date_ajout": datetime.now().strftime("%d/%m/%Y %H:%M")
            }
            
            self.etudiants.append(etudiant)
            self.etudiants_filtres = self.etudiants.copy()
            self.notify(f"Étudiant {nom} ajouté avec succès", "success")
            self.reinitialiser_formulaire()
            self.rafraichir()
            self.update_status()
            
            # Sauvegarde automatique du backup JSON pour la sécurité des données
            self.sauvegarder_donnees_silencieux()
            
        except ValueError:
            self.notify("Veuillez entrer des nombres valides pour le matricule et l'âge", "error")
        except sqlite3.IntegrityError:
            self.notify("Ce matricule existe déjà dans la base de données", "error")
    
    def sauvegarder_modification(self):
        """Sauvegarder les modifications d'un étudiant existant"""
        try:
            # Retrouver l'étudiant
            etudiant = next((e for e in self.etudiants if e["matricule"] == self.editing_matricule), None)
            if not etudiant:
                return

            nom = self.nom_entry.get().strip().capitalize()
            prenom = self.prenom_entry.get().strip().capitalize()
            email = self.email_entry.get().strip()
            telephone = self.telephone_entry.get().strip()
            filiere = self.filiere_entry.get().strip().upper()
            niveau = self.niveau_var.get()
            statut = self.statut_var.get()
            age_str = self.age_entry.get().strip()
            
            if not nom or not prenom or not age_str:
                self.notify("Tous les champs sont obligatoires", "error")
                return
                
            age = int(age_str)
            if age < 15 or age > 40:
                self.notify("L'âge doit être entre 15 et 40 ans", "error")
                return

            # Traiter les notes
            notes_text = self.notes_entry.get("1.0", tk.END).strip()
            notes = []
            if notes_text:
                try:
                    notes = [float(n.strip()) for n in notes_text.split(",") if n.strip()]
                    for note in notes:
                        if note < 0 or note > 20:
                            self.notify("Les notes doivent être entre 0 et 20", "error")
                            return
                except ValueError:
                    self.notify("Notes invalides", "error")
                    return

            # Gestion de la photo lors de la modification
            photo_dest = etudiant.get("photo", "")
            if self.current_photo_path and self.current_photo_path != photo_dest:
                ext = os.path.splitext(self.current_photo_path)[1]
                filename = f"{etudiant['matricule']}{ext}"
                photo_dest = os.path.join("photos", filename)
                shutil.copy(self.current_photo_path, photo_dest)

            # Mise à jour Base de Données
            with db_session() as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    UPDATE etudiants SET nom={DB_P}, prenom={DB_P}, age={DB_P}, note={DB_P}, photo={DB_P}, email={DB_P}, telephone={DB_P}, statut={DB_P}, filiere={DB_P}, niveau={DB_P}
                    WHERE matricule={DB_P}
                """, (nom, prenom, age, json.dumps(notes), photo_dest, email, telephone, statut, filiere, niveau, etudiant['matricule']))

            # Mise à jour
            etudiant.update({"nom": nom, "prenom": prenom, "age": age, "note": notes, "photo": photo_dest, "email": email, "telephone": telephone, "statut": statut, "filiere": filiere, "niveau": niveau})
            self.notify("Modifications enregistrées", "success")
            self.reinitialiser_formulaire()
            self.rafraichir()
            self.update_status()
            
            # Mise à jour du backup JSON
            self.sauvegarder_donnees_silencieux()
            
        except ValueError:
            self.notify("Valeurs invalides", "error")

    def modifier_etudiant(self):
        """Modifier un étudiant sélectionné"""
        selected = self.tree.selection()
        if not selected:
            self.notify("Veuillez sélectionner un étudiant à modifier", "warning")
            return
        
        item = self.tree.item(selected[0])
        matricule = item['values'][0]
        
        for etudiant in self.etudiants:
            if etudiant["matricule"] == matricule:
                self.reinitialiser_formulaire() # Nettoyer d'abord
                self.editing_matricule = matricule
                
                self.matricule_entry.delete(0, tk.END)
                self.matricule_entry.insert(0, str(matricule))
                self.matricule_entry.config(state=tk.DISABLED)  # Matricule non modifiable
                
                self.nom_entry.delete(0, tk.END)
                self.nom_entry.insert(0, etudiant["nom"])
                self.prenom_entry.delete(0, tk.END)
                self.prenom_entry.insert(0, etudiant["prenom"])
                self.email_entry.delete(0, tk.END)
                self.email_entry.insert(0, etudiant.get("email") or "")
                self.telephone_entry.delete(0, tk.END)
                self.telephone_entry.insert(0, etudiant.get("telephone") or "")
                self.age_entry.delete(0, tk.END)
                self.age_entry.insert(0, str(etudiant["age"]))
                self.notes_entry.delete("1.0", tk.END)
                notes_str = ", ".join([str(n) for n in (etudiant.get("note") or [])])
                self.notes_entry.insert("1.0", notes_str)
                self.filiere_entry.delete(0, tk.END)
                self.filiere_entry.insert(0, etudiant.get("filiere") or "")
                self.niveau_var.set(etudiant.get("niveau") or "L1")
                self.statut_var.set(etudiant.get("statut") or "Actif")
                
                # Charger la photo existante
                photo_path = etudiant.get("photo", "")
                if photo_path and os.path.exists(photo_path):
                    self.afficher_photo_preview(photo_path)
                    self.current_photo_path = photo_path
                
                self.btn_valider.config(text="💾 Enregistrer", bg=self.colors["warning"])
                self.nom_entry.focus()
                break
    
    def supprimer_etudiant(self):
        """Supprimer un étudiant avec confirmation"""
        selected = self.tree.selection()
        if not selected:
            self.notify("Veuillez sélectionner un étudiant à supprimer", "warning")
            return
        
        item = self.tree.item(selected[0])
        nom = item['values'][1]
        prenom = item['values'][2]
        
        if messagebox.askyesno("🗑️  Confirmation", f"Êtes-vous sûr de vouloir supprimer {prenom} {nom} ?"):
            matricule = item['values'][0]
           
            # Suppression Base de Données
            with db_session() as conn:
                cursor = conn.cursor()
                cursor.execute(f"DELETE FROM etudiants WHERE matricule={DB_P}", (matricule,))

            self.etudiants = [e for e in self.etudiants if e["matricule"] != matricule]
                
                # Optionnel : Supprimer le fichier photo
                # for f in os.listdir("photos"):
                #     if f.startswith(str(matricule)):
                #         os.remove(os.path.join("photos", f))
                
            self.etudiants_filtres = self.etudiants.copy()
            self.rafraichir()
            self.update_status()
            
            # Mise à jour du backup JSON
            self.sauvegarder_donnees_silencieux()
            self.notify("L'étudiant a été supprimé", "warning")
        
    def envoyer_email(self):
        """Ouvrir le client mail par défaut pour l'étudiant sélectionné"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("⚠️  Avertissement", "Veuillez sélectionner un étudiant")
            return
        
        item = self.tree.item(selected[0])
        matricule = item['values'][0]
        
        etudiant = next((e for e in self.etudiants if e["matricule"] == matricule), None)
        
        if etudiant and etudiant.get("email"):
            email = etudiant["email"]
            subject = f"Information Étudiant - {etudiant['prenom']} {etudiant['nom']}"
            webbrowser.open(f"mailto:{email}?subject={subject}")
        else:
            messagebox.showinfo("ℹ️ Information", "Cet étudiant n'a pas d'adresse email enregistrée.")
    
    def filtrer_etudiants(self, *args):
        """Filtrer les étudiants en temps réel"""
        # Protection : Si le tableau n'est pas encore créé ou est détruit, on arrête
        if not hasattr(self, 'tree') or not self.tree or not self.tree.winfo_exists():
            return
            
        try:
            raw_value = self.search_var.get()
            # On ignore le filtrage si le champ contient encore le texte par défaut
            if raw_value == "Rechercher...":
                search_term = ""
            else:
                search_term = raw_value.lower().strip()

            if not search_term:
                self.etudiants_filtres = self.etudiants.copy()
            else:
                # Recherche multicritère simplifiée et sécurisée
                champs = ["nom", "prenom", "matricule", "filiere", "niveau", "telephone", "email", "statut"]
                self.etudiants_filtres = [
                    e for e in self.etudiants 
                    if any(search_term in str(e.get(c) or "").lower() for c in champs)
                ]
            
            self.rafraichir()
            self.update_status()
        except Exception as e:
            print(f"Erreur lors de la recherche: {e}")
            # En cas d'erreur, on remet la liste complète pour ne pas bloquer l'utilisateur
            self.etudiants_filtres = self.etudiants.copy()
            self.rafraichir()
    
    def trier_colonne(self, col, reverse):
        """Trier le Treeview par colonne"""
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        try:
            # Tentative de tri numérique (pour notes, âge, matricule)
            l.sort(key=lambda t: float(t[0]) if t[0] else 0, reverse=reverse)
        except ValueError:
            # Repli sur tri alphabétique
            l.sort(reverse=reverse)

        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)

        self.tree.heading(col, command=lambda: self.trier_colonne(col, not reverse))

    def afficher_menu_contextuel(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def show_suspendus(self):
        """Afficher la liste des étudiants suspendus dans la vue Gestion"""
        self.show_page("gestion")
        if hasattr(self, 'search_var'):
            self.search_var.set("Suspendu")
        else:
            self.etudiants_filtres = [
                e for e in self.etudiants if str(e.get("statut", "")).lower() == "suspendu"
            ]
            self.rafraichir()
            self.update_status()

    def rafraichir(self):
        """Rafraîchir la liste des étudiants"""
        # Protection : éviter les erreurs si le Treeview n'est pas encore prêt
        if not self.tree or not self.tree.winfo_exists():
            return
            
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for i, etudiant in enumerate(self.etudiants_filtres):
            notes = etudiant.get("note", [])
            moyenne = sum(notes) / len(notes) if notes else 0
            appreciation = self.get_appreciation(moyenne)
            
            # Colorer la ligne selon la moyenne
            tag = self.get_tag_for_moyenne(moyenne)
            row_tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            
            self.tree.insert("", tk.END, tags=(tag, row_tag), values=(
                etudiant["matricule"],
                etudiant["nom"],
                etudiant["prenom"],
                etudiant.get("filiere", ""),
                etudiant.get("niveau", ""),
                etudiant["age"],
                f"{moyenne:.2f}",
                appreciation
            ))
        
        # Configurer les tags pour la coloration
        # Couleurs de texte pour les moyennes
        self.tree.tag_configure('excellent', foreground=self.colors["success"])
        self.tree.tag_configure('bon', foreground=self.colors["accent"])
        self.tree.tag_configure('moyen', foreground=self.colors["warning"])
        self.tree.tag_configure('faible', foreground=self.colors["danger"])
        
        # Couleurs alternées pour les lignes
        self.tree.tag_configure('oddrow', background=self.colors["bg_panel"])
        self.tree.tag_configure('evenrow', background=self.colors["bg_main"]) # Alternance avec le fond principal
    
    def get_appreciation(self, moyenne):
        """Retourner l'appréciation en fonction de la moyenne"""
        if moyenne >= 18:
            return "⭐ Excellent"
        elif moyenne >= 16:
            return "✨ Très bien"
        elif moyenne >= 14:
            return "👍 Bien"
        elif moyenne >= 12:
            return "✓ Assez bien"
        elif moyenne >= 10:
            return "👌 Passable"
        else:
            return "❌ Insuffisant"
    
    def get_tag_for_moyenne(self, moyenne):
        """Retourner le tag pour la coloration de la ligne"""
        if moyenne >= 16:
            return 'excellent'
        elif moyenne >= 14:
            return 'bon'
        elif moyenne >= 10:
            return 'moyen'
        else:
            return 'faible'
    
    def update_status(self):
        """Mettre à jour la barre de statut"""
        total = len(self.etudiants)
        filtres = len(self.etudiants_filtres)
        
        if total > 0:
            moyennes = []
            for e in self.etudiants_filtres:
                notes = e.get("note", [])
                if notes:
                    moyennes.append(sum(notes) / len(notes))
            
            if moyennes:
                moyenne_generale = sum(moyennes) / len(moyennes)
                status_text = f"Total: {total} | Affichés: {filtres} | Moyenne générale: {moyenne_generale:.2f}"
            else:
                status_text = f"Total: {total} | Affichés: {filtres}"
        else:
            status_text = "Aucun étudiant enregistré"
        
        self.status_label.config(text=status_text)
    
    def create_users_view(self, parent):
        """Vue de gestion des utilisateurs réservée à l'Admin"""
        header = tk.Frame(parent, bg=self.colors["bg_main"])
        header.pack(fill=tk.X, pady=(0, 20))
        tk.Label(header, text="👤 Gestion des Utilisateurs", font=("Segoe UI", 22, "bold"),
                 bg=self.colors["bg_main"], fg=self.colors["accent"]).pack(anchor="w")

        paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Formulaire d'ajout (Gauche)
        left_frame = tk.Frame(paned, bg=self.colors["bg_panel"], relief=tk.RAISED, bd=1)
        left_frame.config(highlightthickness=1, highlightbackground=self.colors["border"])
        paned.add(left_frame, weight=1)

        tk.Label(left_frame, text="Ajouter un Utilisateur", font=("Segoe UI", 12, "bold"), 
                 bg=self.colors["bg_panel"], fg=self.colors["accent"], pady=15).pack()

        form_frame = tk.Frame(left_frame, bg=self.colors["bg_panel"], padx=20)
        form_frame.pack(fill=tk.BOTH)

        tk.Label(form_frame, text="Identifiant:", bg=self.colors["bg_panel"], fg=self.colors["fg_text"]).pack(anchor="w")
        self.new_user_entry = tk.Entry(form_frame, bg=self.colors["bg_input"], fg="white", relief=tk.FLAT, insertbackground=self.colors["accent"])
        self.new_user_entry.pack(fill=tk.X, pady=(5, 12), ipady=6)

        tk.Label(form_frame, text="Mot de passe:", bg=self.colors["bg_panel"], fg=self.colors["fg_text"]).pack(anchor="w")
        self.new_pass_entry = tk.Entry(form_frame, show="•", bg=self.colors["bg_input"], fg="white", relief=tk.FLAT, insertbackground=self.colors["accent"])
        self.new_pass_entry.pack(fill=tk.X, pady=(5, 12), ipady=6)

        tk.Label(form_frame, text="Rôle:", bg=self.colors["bg_panel"], fg=self.colors["fg_text"]).pack(anchor="w")
        self.new_role_var = tk.StringVar(value="Professeur")
        self.new_role_menu = ttk.Combobox(form_frame, textvariable=self.new_role_var, values=["Admin", "Secrétaire", "Professeur"], state="readonly")
        self.new_role_menu.pack(fill=tk.X, pady=(5, 25), ipady=4)

        self.btn_user_action = self.create_styled_button(form_frame, "➕ Créer le compte", self.ajouter_utilisateur, self.colors["success"])
        self.btn_user_action.pack(fill=tk.X, pady=(0, 5))
        
        self.create_styled_button(form_frame, "🔄 Réinitialiser", self.reinitialiser_form_utilisateur, "#95a5a6").pack(fill=tk.X)

        # Liste des comptes (Droite)
        right_frame = tk.Frame(paned, bg=self.colors["bg_panel"], relief=tk.RAISED, bd=1)
        right_frame.config(highlightthickness=1, highlightbackground=self.colors["border"])
        paned.add(right_frame, weight=2)

        tk.Label(right_frame, text="Liste des Comptes", font=("Segoe UI", 12, "bold"), 
                 bg=self.colors["bg_panel"], fg=self.colors["accent"], pady=15).pack()

        tree_frame = tk.Frame(right_frame, bg=self.colors["bg_panel"], padx=15, pady=15)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.users_tree = ttk.Treeview(tree_frame, columns=("User", "Role"), show="headings", height=10)
        self.users_tree.heading("User", text="Nom d'utilisateur")
        self.users_tree.heading("Role", text="Rôle")
        self.users_tree.pack(fill=tk.BOTH, expand=True)

        btn_manage = tk.Frame(right_frame, bg=self.colors["bg_panel"])
        btn_manage.pack(pady=20)
        self.create_styled_button(btn_manage, "✏️ Modifier le compte", self.preparer_modif_utilisateur, self.colors["warning"]).pack(side=tk.LEFT, padx=5)
        self.create_styled_button(btn_manage, "🗑️ Supprimer le compte", self.supprimer_utilisateur, self.colors["danger"]).pack(side=tk.LEFT, padx=5)

        self.charger_utilisateurs()

    def charger_utilisateurs(self):
        for i in self.users_tree.get_children():
            self.users_tree.delete(i)
        try:
            with db_session() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT username, role FROM users")
                for row in cursor.fetchall():
                    self.users_tree.insert("", tk.END, values=row)
        except Exception as e: self.notify(f"Erreur de chargement utilisateurs: {e}", "error")

    def reinitialiser_form_utilisateur(self):
        self.editing_username = None
        self.new_user_entry.delete(0, tk.END)
        self.new_pass_entry.delete(0, tk.END)
        self.new_role_var.set("Professeur")
        if hasattr(self, 'btn_user_action'):
            self.btn_user_action.config(text="➕ Créer le compte", bg=self.colors["success"])

    def preparer_modif_utilisateur(self):
        sel = self.users_tree.selection()
        if not sel: 
            self.notify("Sélectionnez un utilisateur à modifier", "warning")
            return
        u, r = self.users_tree.item(sel[0])['values']
        self.editing_username = u
        self.new_user_entry.delete(0, tk.END)
        self.new_user_entry.insert(0, u)
        self.new_pass_entry.delete(0, tk.END)
        self.new_role_var.set(r)
        if hasattr(self, 'btn_user_action'):
            self.btn_user_action.config(text="💾 Enregistrer les modifications", bg=self.colors["warning"])

    def ajouter_utilisateur(self):
        u, p, r = self.new_user_entry.get().strip(), self.new_pass_entry.get().strip(), self.new_role_var.get()
        if not u:
            self.notify("L'identifiant est obligatoire", "error")
            return
        try:
            with db_session() as conn:
                cursor = conn.cursor()
                if self.editing_username:
                    # Modification d'un compte existant
                    if p: # Si un nouveau mot de passe est saisi
                        query = f"UPDATE users SET username={DB_P}, password_hash={DB_P}, role={DB_P} WHERE username={DB_P}"
                        cursor.execute(query, (u, hash_password(p), r, self.editing_username))
                    else: # Conserver l'ancien mot de passe
                        query = f"UPDATE users SET username={DB_P}, role={DB_P} WHERE username={DB_P}"
                        cursor.execute(query, (u, r, self.editing_username))
                    
                    # Mettre à jour l'identité de la session si l'admin se modifie lui-même
                    if self.editing_username == self.username:
                        self.username = u
                        
                    self.notify(f"Compte '{u}' mis à jour", "success")
                else:
                    # Création d'un nouveau compte
                    if not p:
                        self.notify("Le mot de passe est obligatoire pour un nouveau compte", "error")
                        return
                    query = f"INSERT INTO users (username, password_hash, role) VALUES ({DB_P}, {DB_P}, {DB_P})"
                    cursor.execute(query, (u, hash_password(p), r))
                    self.notify(f"Nouveau compte '{u}' créé", "success")
            
            self.reinitialiser_form_utilisateur()
            self.charger_utilisateurs()
        except Exception as e:
            self.notify(f"Erreur (Identifiant peut-être déjà pris): {e}", "error")

    def supprimer_utilisateur(self):
        sel = self.users_tree.selection()
        if not sel: return
        u = self.users_tree.item(sel[0])['values'][0]
        if u == self.username:
            self.notify("Vous ne pouvez pas supprimer votre propre compte", "error")
            return
        if messagebox.askyesno("Confirmation", f"Supprimer définitivement le compte de {u} ?"):
            with db_session() as conn:
                query = f"DELETE FROM users WHERE username = {DB_P}"
                cursor = conn.cursor()
                cursor.execute(query, (u,))
            self.charger_utilisateurs()
            self.notify("Compte utilisateur supprimé", "warning")

    def create_paiements_view(self, parent):
        """Vue dédiée à la gestion financière"""
        self.charger_historique_paiements_data()

        header = tk.Frame(parent, bg=self.colors["bg_main"])
        header.pack(fill=tk.X, pady=(0, 20))
        tk.Label(header, text="💰 Gestion Financière", font=("Segoe UI", 22, "bold"),
                 bg=self.colors["bg_main"], fg=self.colors["accent"]).pack(anchor="w")

        stats_frame = tk.Frame(parent, bg=self.colors["bg_main"])
        stats_frame.pack(fill=tk.X, pady=(0, 20))

        total_scolarite = sum(e.get("frais_scolarite", 500000) for e in self.etudiants)
        total_encaisse = sum(p['montant'] for p in self.paiements)
        total_dettes = total_scolarite - total_encaisse

        self.create_stat_card(stats_frame, "Total Recettes", f"{total_encaisse:,} F", "💰").pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.create_stat_card(stats_frame, "Dettes Restantes", f"{total_dettes:,} F", "📉").pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(paned, bg=self.colors["bg_panel"], relief=tk.RAISED, bd=1)
        left_frame.config(highlightthickness=1, highlightbackground=self.colors["border"])
        paned.add(left_frame, weight=1)

        tk.Label(left_frame, text="Enregistrer un Paiement", font=("Segoe UI", 12, "bold"), 
                 bg=self.colors["bg_panel"], fg=self.colors["accent"], pady=15).pack()

        form = tk.Frame(left_frame, bg=self.colors["bg_panel"], padx=20)
        form.pack(fill=tk.BOTH)

        tk.Label(form, text="Étudiant:", bg=self.colors["bg_panel"], fg=self.colors["fg_text"]).pack(anchor="w")
        etudiants_list = [f"{e['matricule']} - {e['nom']} {e['prenom']}" for e in self.etudiants]
        self.pay_student_var = tk.StringVar()
        self.pay_combo = ttk.Combobox(form, textvariable=self.pay_student_var, values=etudiants_list, state="readonly")
        self.pay_combo.pack(fill=tk.X, pady=(5, 12), ipady=4)

        tk.Label(form, text="Montant (FCFA):", bg=self.colors["bg_panel"], fg=self.colors["fg_text"]).pack(anchor="w")
        self.pay_amount = tk.Entry(form, bg=self.colors["bg_input"], fg="white", relief=tk.FLAT, insertbackground=self.colors["accent"])
        self.pay_amount.pack(fill=tk.X, pady=(5, 12), ipady=6)

        tk.Label(form, text="Mode de paiement:", bg=self.colors["bg_panel"], fg=self.colors["fg_text"]).pack(anchor="w")
        self.pay_type = ttk.Combobox(form, values=["Espèces", "Virement", "Chèque"], state="readonly")
        self.pay_type.current(0)
        self.pay_type.pack(fill=tk.X, pady=(5, 12), ipady=4)

        self.create_styled_button(form, "✅ Valider le paiement", self.enregistrer_paiement, self.colors["success"]).pack(fill=tk.X, pady=10)

        right_frame = tk.Frame(paned, bg=self.colors["bg_panel"], relief=tk.RAISED, bd=1)
        right_frame.config(highlightthickness=1, highlightbackground=self.colors["border"])
        paned.add(right_frame, weight=2)

        tk.Label(right_frame, text="Historique des Paiements", font=("Segoe UI", 12, "bold"), 
                 bg=self.colors["bg_panel"], fg=self.colors["accent"], pady=15).pack()

        tree_frame = tk.Frame(right_frame, bg=self.colors["bg_panel"], padx=15, pady=15)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.pay_tree = ttk.Treeview(tree_frame, columns=("ID", "Mat", "Nom", "Montant", "Date", "Mode"), show="headings")
        for col, head in [("ID", "N°"), ("Mat", "Matricule"), ("Nom", "Étudiant"), ("Montant", "Montant"), ("Date", "Date"), ("Mode", "Mode")]:
            self.pay_tree.heading(col, text=head)
            self.pay_tree.column(col, width=80 if col != "Nom" else 150)
        self.pay_tree.pack(fill=tk.BOTH, expand=True)

        self.create_styled_button(right_frame, "🖨️ Générer Reçu PDF", self.imprimer_recu_paiement, self.colors["accent"]).pack(pady=20)
        self.rafraichir_tree_paiements()

    def charger_historique_paiements_data(self):
        self.paiements = []
        try:
            with db_session() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, matricule, montant FROM paiements")
                for row in cursor.fetchall():
                    self.paiements.append({'id': row[0], 'matricule': row[1], 'montant': row[2]})
        except Exception as e: print(f"Erreur chargement data paiements: {e}")

    def rafraichir_tree_paiements(self):
        for i in self.pay_tree.get_children(): self.pay_tree.delete(i)
        try:
            with db_session() as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    SELECT p.id, p.matricule, {NAME_CONCAT}, p.montant, p.date_paiement, p.type_paiement 
                    FROM paiements p JOIN etudiants e ON p.matricule = e.matricule
                    ORDER BY p.id DESC
                """)
                for row in cursor.fetchall():
                    self.pay_tree.insert("", tk.END, values=row)
        except Exception as e: print(f"Erreur chargement paiements: {e}")

    def enregistrer_paiement(self):
        sel_student = self.pay_student_var.get()
        montant_str = self.pay_amount.get()
        if not sel_student or not montant_str:
            self.notify("Veuillez remplir tous les champs", "error")
            return
        try:
            matricule = sel_student.split(" - ")[0]
            montant = float(montant_str)
            date_p = datetime.now().strftime("%d/%m/%Y %H:%M")
            mode = self.pay_type.get()
            with db_session() as conn:
                conn.execute(f"INSERT INTO paiements (matricule, montant, date_paiement, type_paiement) VALUES ({DB_P},{DB_P},{DB_P},{DB_P})",
                            (matricule, montant, date_p, mode))
            self.notify(f"Paiement de {montant} F enregistré", "success")
            self.pay_amount.delete(0, tk.END)
            self.show_page("paiements")
        except ValueError: self.notify("Montant invalide", "error")

    def imprimer_recu_paiement(self):
        sel = self.pay_tree.selection()
        if not sel:
            self.notify("Sélectionnez un paiement pour le reçu", "warning")
            return
        row = self.pay_tree.item(sel[0])['values']
        id_pay, matricule, nom_complet, montant, date_p, mode = row
        
        # Conversion de sécurité pour le formatage numérique
        montant_f = float(montant)

        etudiant = next((e for e in self.etudiants if str(e['matricule']) == str(matricule)), None)
        frais_totaux = float(etudiant.get('frais_scolarite', 500000)) if etudiant else 500000.0
        
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT SUM(montant) FROM paiements WHERE matricule = {DB_P}", (str(matricule),))
            res_sum = cursor.fetchone()[0]
            deja_paye = float(res_sum) if res_sum is not None else 0.0
            reste = frais_totaux - deja_paye
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf", 
            filetypes=[("Fichiers PDF", "*.pdf")],
            initialfile=f"Recu_Paiement_{id_pay}.pdf"
        )
        if not file_path: return
        try:
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()
            elements.append(Paragraph(f"<b>STUDENT MANAGER PRO - REÇU DE PAIEMENT</b>", styles['Title']))
            elements.append(Paragraph(f"Reçu N° : {id_pay} | Date : {date_p}", styles['Normal']))
            elements.append(Spacer(1, 20))
            data = [
                ["DÉSIGNATION", "DÉTAILS"],
                ["Étudiant", f"{nom_complet} (Matricule: {matricule})"],
                ["Mode de Paiement", str(mode)],
                ["Montant Versé", f"{float(montant_f):,.0f} FCFA"],
                ["-----------------------", "-----------------------"],
                ["Total Frais Scolarité", f"{float(frais_totaux):,.0f} FCFA"],
                ["Total déjà versé", f"{float(deja_paye):,.0f} FCFA"],
                ["RESTE À PAYER", f"<b>{reste:,.0f} FCFA</b>"]
            ]
            table = Table(data, colWidths=[5*cm, 10*cm])
            table.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 1, colors.grey),
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor(self.colors["accent"])),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('PADDING', (0,0), (-1,-1), 10),
                ('FONTSIZE', (0,0), (-1,-1), 11),
                ('ALIGN', (0,0), (0,-1), 'LEFT'),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 30))
            elements.append(Paragraph("Signature de l'administration : _______________________", styles['Normal']))
            doc.build(elements)
            self.notify("Reçu PDF généré !", "success")
            
            # Ouverture automatique pour confirmation visuelle
            try:
                os.startfile(file_path)
            except:
                pass
        except Exception as e: self.notify(f"Erreur PDF: {e}", "error")

    def menu_impression_pdf(self):
        """Génère un rapport PDF des étudiants actuellement affichés"""
        if not self.etudiants_filtres:
            self.notify("Aucune donnée à imprimer", "warning")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Fichiers PDF", "*.pdf")],
            initialfile=f"Rapport_Etudiants_{datetime.now().strftime('%d_%m_%Y')}.pdf"
        )
        
        if not file_path:
            return

        try:
            doc = SimpleDocTemplate(file_path, pagesize=landscape(A4))
            elements = []
            styles = getSampleStyleSheet()
            
            # Titre stylisé
            title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], alignment=1, spaceAfter=20)
            elements.append(Paragraph(f"Liste des Étudiants - Student Manager PRO", title_style))
            elements.append(Paragraph(f"Date de génération : {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
            elements.append(Spacer(1, 12))
            
            # Préparation des données pour le tableau
            data = [["Matricule", "Nom", "Prénom", "Filière", "Niveau", "Âge", "Moyenne"]]
            for e in self.etudiants_filtres:
                notes = e.get("note", [])
                moyenne = sum(notes) / len(notes) if notes else 0
                data.append([
                    e['matricule'],
                    e['nom'],
                    e['prenom'],
                    e.get('filiere', 'N/A'),
                    e.get('niveau', 'N/A'),
                    e['age'],
                    f"{moyenne:.2f}"
                ])
            
            # Application du style au tableau
            table = Table(data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.colors["accent"])),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            
            elements.append(table)
            doc.build(elements)
            self.notify(f"Rapport enregistré : {os.path.basename(file_path)}", "success")
            
            # Ouverture automatique du rapport
            try:
                os.startfile(file_path)
            except:
                pass
            
        except Exception as e:
            self.notify(f"Erreur PDF : {e}", "error")

    def afficher_liste(self):
        """Afficher la liste complète des étudiants"""
        if not self.etudiants:
            self.notify("Aucun étudiant enregistré", "info")
            return
        
        details = "📋 LISTE COMPLÈTE DES ÉTUDIANTS\n" + "="*100 + "\n\n"
        for i, etudiant in enumerate(self.etudiants, 1):
            notes = etudiant.get("note", [])
            moyenne = sum(notes) / len(notes) if notes else 0
            appreciation = self.get_appreciation(moyenne)
            
            details += f"{i}. Matricule: {etudiant['matricule']}\n"
            details += f"   Nom: {etudiant['nom']} | Prénom: {etudiant['prenom']}\n"
            details += f"   Email: {etudiant.get('email', 'N/A')} | Tél: {etudiant.get('telephone', 'N/A')}\n"
            details += f"   Âge: {etudiant['age']} ans\n"
            details += f"   Notes: {notes if notes else 'Aucune note'}\n"
            details += f"   Moyenne: {moyenne:.2f} | {appreciation}\n"
            details += f"   Ajout: {etudiant.get('date_ajout', 'N/A')}\n"
            details += "-" * 100 + "\n"
        
        self.show_text_window("📋 Liste des Étudiants", details)
    
    def exporter_csv(self):
        """Exporter les données en CSV"""
        if not self.etudiants:
            self.notify("Aucun étudiant à exporter", "info")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"etudiants_{datetime.now().strftime('%d_%m_%Y')}.csv"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Matricule', 'Nom', 'Prénom', 'Filière', 'Niveau', 'Email', 'Téléphone', 'Âge', 'Notes', 'Moyenne', 'Appréciation', 'Date d\'ajout']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for etudiant in self.etudiants:
                    notes = etudiant.get("note", [])
                    moyenne = sum(notes) / len(notes) if notes else 0
                    appreciation = self.get_appreciation(moyenne)
                    
                    writer.writerow({
                        'Matricule': etudiant['matricule'],
                        'Nom': etudiant['nom'],
                        'Prénom': etudiant['prenom'],
                        'Filière': etudiant.get('filiere', ''),
                        'Niveau': etudiant.get('niveau', ''),
                        'Email': etudiant.get('email', ''),
                        'Téléphone': etudiant.get('telephone', ''),
                        'Âge': etudiant['age'],
                        'Notes': '; '.join([str(n) for n in notes]),
                        'Moyenne': f"{moyenne:.2f}",
                        'Appréciation': appreciation,
                        'Date d\'ajout': etudiant.get('date_ajout', 'N/A')
                    })
            
            self.notify("Export CSV terminé avec succès", "success")
        except Exception as e:
            self.notify(f"Erreur lors de l'export: {e}", "error")
    
    def show_text_window(self, title, text):
        """Afficher une fenêtre avec texte scrollable"""
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("900x600")
        window.attributes('-alpha', 0.0)
        window.config(bg=self.colors["bg_main"])
        
        # En-tête
        title_frame = tk.Frame(window, bg=self.colors["bg_header"], height=40)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text=title, font=("Arial", 14, "bold"), 
                              bg=self.colors["bg_header"], fg=self.colors["accent"])
        title_label.pack(pady=8)
        
        # Contenu
        text_frame = tk.Frame(window, bg=self.colors["bg_main"])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, font=("Courier", 10), wrap=tk.WORD,
                             bg=self.colors["bg_panel"], fg=self.colors["fg_text"], insertbackground="white")
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_widget.insert("1.0", text)
        text_widget.config(state=tk.DISABLED)
        
        scrollbar = ttk.Scrollbar(text_frame, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        # Bouton fermer
        button_frame = tk.Frame(window, bg=self.colors["bg_main"])
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(button_frame, text="✕ Fermer", command=window.destroy,
                 bg=self.colors["danger"], fg="white", font=("Arial", 10), padx=20).pack(side=tk.RIGHT)
        self.animate_window(window)
    
    def reinitialiser_formulaire(self):
        """Réinitialiser tous les champs du formulaire"""
        self.matricule_entry.config(state=tk.NORMAL)
        self.matricule_entry.delete(0, tk.END)
        self.matricule_entry.insert(0, self.generer_matricule())
        self.nom_entry.delete(0, tk.END)
        self.prenom_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.telephone_entry.delete(0, tk.END)
        self.age_entry.delete(0, tk.END)
        self.filiere_entry.delete(0, tk.END)
        self.niveau_var.set("L1")
        self.statut_var.set("Actif")
        self.nb_notes_entry.delete(0, tk.END)
        self.notes_entry.delete("1.0", tk.END)
        self.photo_canvas.delete("all")
        self.photo_canvas.create_text(67, 67, text="Aucune\nPhoto", fill="gray", justify=tk.CENTER, font=("Segoe UI", 9))
        self.current_photo_path = None
        self.editing_matricule = None
        self.btn_valider.config(text="➕ Enregistrer", bg=self.colors["success"])
    
    def toggle_theme(self):
        """Ouvre une fenêtre pour choisir manuellement le thème de l'interface"""
        theme_win = tk.Toplevel(self.root)
        theme_win.title("⚙️ Paramètres d'apparence")
        theme_win.geometry("640x720")
        theme_win.resizable(True, True)
        theme_win.config(bg=self.colors["bg_main"])
        theme_win.transient(self.root)
        theme_win.grab_set()
        
        # Centrer la fenêtre par rapport à l'application
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 320
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 260
        theme_win.geometry(f"+{max(0, x)}+{max(0, y)}")

        tk.Label(theme_win, text="Personnalisation du thème", font=("Segoe UI", 14, "bold"),
                 bg=self.colors["bg_main"], fg=self.colors["accent"]).pack(pady=(30, 10))
        tk.Label(theme_win, text="Choisissez l'ambiance visuelle de votre gestionnaire", font=("Segoe UI", 9),
                 bg=self.colors["bg_main"], fg=self.colors["fg_text"]).pack(pady=(0, 10))
        tk.Label(theme_win, text="Faites défiler vers le bas pour voir tous les thèmes.", font=("Segoe UI", 8),
                 bg=self.colors["bg_main"], fg=self.colors["fg_text"]).pack(pady=(0, 20))

        theme_options = self.theme_options

        preview_container = tk.Frame(theme_win, bg=self.colors["bg_panel"], bd=1, relief=tk.SOLID)
        preview_container.pack(fill=tk.X, padx=30, pady=(0, 20))
        preview_title = tk.Label(preview_container, text="Aperçu du thème sélectionné", font=("Segoe UI", 10, "bold"),
                                 bg=self.colors["bg_panel"], fg=self.colors["accent"])
        preview_title.pack(anchor="w", pady=(10, 0), padx=10)
        preview_sample = tk.Label(preview_container, text="Manager PRO - Aperçu",
                                  bg=self.colors["bg_panel"], fg=self.colors["fg_head"],
                                  font=("Segoe UI", 12, "bold"), pady=12)
        preview_sample.pack(fill=tk.X, padx=10, pady=(10, 16))
        # Bouton de vérification des mises à jour toujours visible dans l'aperçu
        self.update_btn_preview = self.create_styled_button(preview_container, f"🔄 Vérifier les mises à jour ({APP_VERSION})", lambda: self.verifier_mises_a_jour(automatique=False), self.colors["accent"])
        self.update_btn_preview.pack(fill=tk.X, padx=10, pady=(0, 12))

        options_canvas = tk.Canvas(theme_win, bg=self.colors["bg_main"], highlightthickness=0, borderwidth=0, height=420)
        v_scrollbar = tk.Scrollbar(theme_win, orient=tk.VERTICAL, command=options_canvas.yview)
        h_scrollbar = tk.Scrollbar(theme_win, orient=tk.HORIZONTAL, command=options_canvas.xview)
        options_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        options_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(30, 0), pady=(0, 0))
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=(0, 10))
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X, padx=(30, 10), pady=(0, 10))

        options_inner = tk.Frame(options_canvas, bg=self.colors["bg_main"])
        window_id = options_canvas.create_window((0, 0), window=options_inner, anchor="nw")

        def _update_scroll_region(event=None):
            options_canvas.configure(scrollregion=options_canvas.bbox("all"))
            try:
                # Adapter la largeur du contenu à la largeur du canevas pour activer le scroll horizontal
                options_canvas.itemconfig(window_id, width=options_canvas.winfo_width())
            except Exception:
                pass

        options_inner.bind("<Configure>", _update_scroll_region)

        def _on_mousewheel(event):
            options_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        options_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        # Support du défilement horizontal via Shift + molette
        def _on_shift_mousewheel(event):
            if event.state & 0x0001:  # Shift appuyé
                options_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

        options_canvas.bind_all("<Shift-MouseWheel>", _on_shift_mousewheel)

        def appliquer_et_fermer(key):
            self.current_theme = key
            self.colors = self.themes[self.current_theme]
            theme_win.destroy()
            
            # Rafraîchir toute l'interface avec les nouvelles couleurs
            for widget in self.root.winfo_children():
                if not isinstance(widget, tk.Toplevel):
                    widget.destroy()
            self.create_widgets()
            # Enregistrer la préférence de thème pour l'utilisateur courant
            try:
                with db_session() as conn:
                    cursor = conn.cursor()
                    cursor.execute(f"UPDATE users SET theme = {DB_P} WHERE username = {DB_P}", (self.current_theme, self.username))
            except Exception:
                pass
            self.notify(f"Thème {key.capitalize()} appliqué !", "info")

        def preview_theme(key):
            preview_colors = self.themes.get(key, self.colors)
            preview_container.config(bg=preview_colors["bg_main"])
            preview_title.config(bg=preview_colors["bg_main"], fg=preview_colors["accent"])
            preview_sample.config(bg=preview_colors["bg_panel"], fg=preview_colors["fg_head"],
                                  text=f"Manager PRO - Aperçu ({key.replace('_', ' ').title()})")
            self.update_btn_preview.config(bg=preview_colors["accent"])

        for label, key, btn_color in theme_options:
            option_frame = tk.Frame(options_inner, bg=self.colors["bg_main"])
            option_frame.pack(fill=tk.X, padx=0, pady=8)

            # Aperçu visuel du thème
            preview_frame = tk.Frame(option_frame, bg=self.colors["bg_main"])
            preview_frame.pack(side=tk.LEFT, padx=(0, 12))
            if key in self.themes:
                preview_colors = self.themes[key]
                for color_key in ("bg_main", "bg_panel", "accent"):
                    swatch = tk.Frame(preview_frame, bg=preview_colors[color_key], width=28, height=28, bd=1, relief=tk.SOLID)
                    swatch.pack(side=tk.LEFT, padx=2)
                    swatch.pack_propagate(False)
                    swatch.bind("<Button-1>", lambda e, k=key: preview_theme(k))

                sample_label = tk.Label(option_frame, text="AaBb123 – Aperçu", 
                                        bg=preview_colors["bg_panel"], fg=preview_colors["fg_head"], 
                                        font=("Segoe UI", 8, "bold"), padx=8, pady=6, bd=1, relief=tk.SOLID,
                                        cursor="hand2")
                sample_label.pack(side=tk.LEFT, padx=(0, 12))
                sample_label.bind("<Button-1>", lambda e, k=key: preview_theme(k))

            btn = self.create_styled_button(option_frame, label, lambda k=key: appliquer_et_fermer(k), btn_color)
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

            if self.current_theme == key:
                tk.Label(option_frame, text="✓ Actuellement sélectionné", font=("Segoe UI", 8, "italic"), 
                         bg=self.colors["bg_main"], fg=self.colors["success"]).pack(side=tk.LEFT, padx=10)

    def verifier_mises_a_jour(self, automatique=True):
        """Vérifie si une nouvelle version est disponible sur le serveur"""
        def check():
            try:
                # Dans un environnement réel, on lirait un JSON distant
                # with urllib.request.urlopen(VERSION_URL, timeout=5) as response:
                #    data = json.loads(response.read().decode())
                #    latest_version = data.get("version", APP_VERSION)
                
                # Simulation pour la démonstration (décommentez les lignes ci-dessus en prod)
                latest_version = APP_VERSION 
                
                if latest_version > APP_VERSION:
                    self.root.after(0, lambda: self.proposer_mise_a_jour(latest_version))
                elif not automatique:
                    self.root.after(0, lambda: self.notify("Votre logiciel est à jour", "info"))
            except Exception as e:
                if not automatique:
                    self.root.after(0, lambda: self.notify("Serveur de mise à jour injoignable", "error"))

        thread = threading.Thread(target=check, daemon=True)
        thread.start()

    def proposer_mise_a_jour(self, nouvelle_version):
        """Affiche une boîte de dialogue pour confirmer le téléchargement"""
        msg = f"Une nouvelle version ({nouvelle_version}) est disponible.\nSouhaitez-vous l'installer maintenant ?"
        if messagebox.askyesno("🚀 Mise à jour disponible", msg):
            self.telecharger_et_installer()

    def telecharger_et_installer(self):
        """Télécharge le nouveau script et redémarre l'application"""
        self.show_loader_overlay("Téléchargement de la mise à jour...", duration=3000)
        
        def download():
            try:
                current_script = os.path.abspath(sys.argv[0])
                new_script = current_script + ".new"
                
                # Téléchargement du nouveau fichier
                urllib.request.urlretrieve(UPDATE_URL, new_script)
                
                # Création du script de remplacement (Windows Batch)
                # Ce script attend 2 secondes, remplace le fichier et relance
                updater_bat = os.path.join(BASE_DIR, "updater.bat")
                with open(updater_bat, "w") as f:
                    f.write(f'@echo off\n')
                    f.write(f'timeout /t 2 /nobreak > nul\n')
                    f.write(f'move /y "{new_script}" "{current_script}"\n')
                    f.write(f'start python "{current_script}"\n')
                    f.write(f'del "%~f0"\n')
                
                self.root.after(0, lambda: self.finaliser_installation(updater_bat))
            except Exception as e:
                self.root.after(0, lambda: self.notify(f"Erreur de téléchargement: {e}", "error"))

        threading.Thread(target=download, daemon=True).start()

    def finaliser_installation(self, bat_path):
        """Ferme l'app et lance le script de remplacement"""
        if messagebox.showinfo("Prêt", "Le téléchargement est terminé. L'application va redémarrer pour appliquer les changements."):
            subprocess.Popen([bat_path], shell=True)
            self.root.quit()

    def deconnexion(self, ask_confirm=True):
        """Déconnecter l'utilisateur et revenir à l'écran de connexion"""
        if not ask_confirm or messagebox.askyesno("Déconnexion", "Voulez-vous vraiment vous déconnecter ?"):
            if self.timeout_id:
                self.root.after_cancel(self.timeout_id)
            log_event(self.username, "LOGOUT", "Déconnexion de l'utilisateur")
            self.root.withdraw()
            # Nettoyer l'interface pour éviter les doublons lors de la reconnexion
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # Fonction de rappel pour recréer l'interface après reconnexion
            def relancer(user, role, theme='dark'):
                self.root.deiconify()
                GestionEtudiantsApp(self.root, user, role, theme)
            
            LoginWindow(self.root, relancer)

    def init_db(self):
        """Initialiser la base de données SQLite"""
        try:
            setup_database()
        except Exception as e:
            messagebox.showerror("Erreur BD", f"Impossible d'initialiser la base de données: {e}")
            self.notify(f"Impossible d'initialiser la base de données: {e}", "error")

    def charger_donnees(self):
        """Charger les données depuis la base de données SQLite ou MySQL distante"""
        self.etudiants = []
        try:
            with db_session() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM etudiants")
                rows = cursor.fetchall()
                
                # Migration: Si la BD est vide mais qu'un JSON existe, on importe le JSON
                if not rows and os.path.exists(JSON_PATH):
                    self.migrer_json_vers_sqlite(cursor, conn)
                    cursor.execute("SELECT * FROM etudiants")
                    rows = cursor.fetchall()

                for row in rows:
                    self.etudiants.append({
                        "matricule": row[0],
                        "nom": row[1],
                        "prenom": row[2],
                        "age": row[3],
                        "note": json.loads(row[4]) if row[4] else [],
                        "photo": row[5],
                        "date_ajout": row[6],
                        "email": row[7] if len(row) > 7 else "",
                        "telephone": row[8] if len(row) > 8 else "",
                        "statut": row[9] if len(row) > 9 else "Actif",
                        "filiere": row[10] if len(row) > 10 else "",
                        "niveau": row[11] if len(row) > 11 else "",
                        "frais_scolarite": row[12] if len(row) > 12 else 500000
                    })
            self.etudiants_filtres = self.etudiants.copy()
        except Exception as e:
            messagebox.showerror("❌ Erreur", f"Erreur lors du chargement: {e}")
            self.notify(f"Erreur lors du chargement des données: {e}", "error")
    
    def migrer_json_vers_sqlite(self, cursor, conn):
        """Importer les données JSON existantes dans la base de données active"""
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as fichier:
                data = json.load(fichier)
                insert_cmd = "REPLACE INTO etudiants VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)" if DB_TYPE == "mysql" else "INSERT OR IGNORE INTO etudiants VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)"
                for e in data:
                    cursor.execute(insert_cmd, 
                        (e['matricule'], e['nom'], e['prenom'], e['age'], 
                         json.dumps(e.get('note', [])), e.get('photo', ''), e.get('date_ajout', ''), e.get('email', ''), e.get('telephone', ''), e.get('statut', 'Actif'), e.get('filiere', ''), e.get('niveau', ''), e.get('frais_scolarite', 500000)))
                conn.commit()
                messagebox.showinfo("Migration", "Vos anciennes données JSON ont été importées dans la base de données.")
                self.notify("Vos anciennes données JSON ont été importées dans la base de données.", "info")
        except Exception as e:
            print(f"Erreur migration: {e}")
            self.notify(f"Erreur migration: {e}", "error")

    def sauvegarder_donnees(self):
        """Sauvegarder les données dans le fichier JSON (Backup)"""
        try:
            with open(JSON_PATH, "w", encoding="utf-8") as fichier:
                json.dump(self.etudiants, fichier, indent=4, ensure_ascii=False)
            self.notify("Sauvegarde JSON (Backup) réussie", "success")
        except Exception as e:
            messagebox.showerror("❌ Erreur", f"Erreur lors de la sauvegarde: {e}")
            self.notify(f"Erreur lors de la sauvegarde: {e}", "error")
            
    def sauvegarder_donnees_silencieux(self):
        """Version interne de sauvegarde sans notification visuelle"""
        try:
            with open(JSON_PATH, "w", encoding="utf-8") as fichier:
                json.dump(self.etudiants, fichier, indent=4, ensure_ascii=False)
        except Exception:
            pass

def compiler_en_exe():
    """Compile automatiquement le script en utilisant PyInstaller avec des chemins absolus."""
    print(f"\n📦 Préparation de la compilation de {APP_NAME} ({APP_VERSION})...")
    
    script_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(script_path)
    icon_path = os.path.join(current_dir, "app_icon.ico")
    logo_path = os.path.join(current_dir, "logo.png")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--clean",
        f"--name={APP_NAME.replace(' ', '_')}"
    ]
    
    # Ajout sécurisé des ressources
    if os.path.exists(logo_path):
        cmd.append(f"--add-data={logo_path};.")
    
    if os.path.exists(icon_path):
        cmd.append(f"--add-data={icon_path};.")
        cmd.append(f"--icon={icon_path}")
    else:
        print(f"⚠️  Attention: '{icon_path}' est introuvable. Compilation avec l'icône par défaut.")

    cmd.append(script_path)
    
    print(f"🚀 Exécution de la commande : {' '.join(cmd)}")
    try:
        import subprocess
        subprocess.run(cmd, check=True)
        print("\n✅ Compilation réussie !")
        print("📁 Retrouvez votre fichier '.exe' dans le dossier 'dist/'.")
    except Exception as e:
        print(f"\n❌ Erreur pendant la compilation: {e}")
        print("Assurez-vous que PyInstaller est installé : pip install pyinstaller")


if __name__ == "__main__":
    # Activer le support Haute Définition (High DPI) pour éviter le flou sur Windows
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    # Mode compilation automatique via l'argument --compile
    if "--compile" in sys.argv:
        compiler_en_exe()
        sys.exit()

    setup_database() # Initialiser la DB avant le login

    root = tk.Tk()
    root.withdraw() # Cacher la fenêtre principale au démarrage
    
    def lancer_application(user, role, theme='dark'):
        root.deiconify() # Réafficher la fenêtre principale
        GestionEtudiantsApp(root, user, role, theme)
    
    # Séquence de démarrage PRO : Splash Screen -> Login -> App
    def start_login():
        LoginWindow(root, lancer_application)
        
    SplashScreen(root, start_login)
    
    root.mainloop()
