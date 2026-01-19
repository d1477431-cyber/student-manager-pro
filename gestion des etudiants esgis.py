import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import sqlite3
import json
import webbrowser
import os
from datetime import datetime
import csv
import shutil
from PIL import Image, ImageTk  # pip install pillow
import matplotlib.pyplot as plt # pip install matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class LoginWindow:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success
        
        self.window = tk.Toplevel(root)
        self.window.title("Connexion")
        self.window.geometry("400x480")
        self.window.attributes('-alpha', 0.0)
        
        # Palette de couleurs moderne (Thème Nord)
        self.colors = {
            "bg": "#2E3542",      # Fond sombre
            "card": "#3B4252",    # Fond carte
            "input": "#434C5E",   # Champs saisie
            "fg": "#D8DEE9",      # Texte
            "accent": "#88C0D0",  # Bleu glacé
            "white": "#ECEFF4"    # Blanc
        }
        self.window.config(bg=self.colors["bg"])
        
        # Icône de la fenêtre de connexion
        try:
            base_folder = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(base_folder, "logo.png")
            ico_path = os.path.join(base_folder, "logo.ico")
            
            if os.path.exists(logo_path):
                self.icon_img = tk.PhotoImage(file=logo_path)
                self.window.iconphoto(False, self.icon_img)
            elif os.path.exists(ico_path):
                self.window.iconbitmap(ico_path)
        except Exception: pass
        
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
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
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
        
        # Identifiants par défaut (admin / admin)
        if user == "donatien" and password == "dodo":
            self.window.destroy()
            self.on_success()
        else:
            messagebox.showerror("Erreur", "Identifiants incorrects\n", parent=self.window)

    def on_closing(self):
        self.root.destroy()

class GestionEtudiantsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion des Étudiants - ESGIS")
        self.root.geometry("1400x800")
        self.root.attributes('-alpha', 0.0)
        
        # Palettes de couleurs (Thèmes Nord)
        self.themes = {
            "dark": {
                "bg_main": "#2E3440", "bg_panel": "#3B4252", "bg_input": "#434C5E",
                "bg_header": "#2E3440", "fg_text": "#D8DEE9", "fg_head": "#ECEFF4",
                "accent": "#88C0D0", "success": "#A3BE8C", "warning": "#EBCB8B",
                "danger": "#BF616A", "border": "#4C566A"
            },
            "light": {
                "bg_main": "#ECEFF4", "bg_panel": "#FFFFFF", "bg_input": "#E5E9F0",
                "bg_header": "#D8DEE9", "fg_text": "#2E3440", "fg_head": "#3B4252",
                "accent": "#5E81AC", "success": "#8FBCBB", "warning": "#D08770",
                "danger": "#BF616A", "border": "#D8DEE9"
            }
        }
        self.current_theme = "dark"
        self.colors = self.themes[self.current_theme]
        self.root.config(bg=self.colors["bg_main"])
        
        # Icône de la fenêtre principale
        try:
            base_folder = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(base_folder, "logo.png")
            ico_path = os.path.join(base_folder, "logo.ico")

            if os.path.exists(logo_path):
                self.icon_img = tk.PhotoImage(file=logo_path)
                self.root.iconphoto(True, self.icon_img)
            elif os.path.exists(ico_path):
                self.root.iconbitmap(ico_path)
        except Exception: pass
        
        # Configurer le style
        self.setup_styles()
        
        self.etudiants = []
        self.etudiants_filtres = []
        self.editing_matricule = None
        self.current_photo_path = None
        
        # Créer le dossier pour les photos s'il n'existe pas
        if not os.path.exists("photos"):
            os.makedirs("photos")
            
        self.init_db()
        self.charger_donnees()
        
        self.create_widgets()
        self.root.minsize(1000, 600)
        self.animate_window(self.root)
    
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

        # Logo/Titre
        app_title = tk.Label(sidebar, text="🎓 ESGIS\nManager", font=("Segoe UI", 22, "bold"),
                             bg=sidebar_bg, fg=self.colors["accent"], justify=tk.CENTER)
        app_title.pack(pady=(40, 50))
        
        self.sidebar_btns = {}

        # Menu Navigation
        self.create_sidebar_btn(sidebar, "dashboard", "📊  Tableau de bord", lambda: self.show_page("dashboard"))
        self.create_sidebar_btn(sidebar, "gestion", "👥  Gestion Étudiants", lambda: self.show_page("gestion"))
        self.create_sidebar_btn(sidebar, "export", "📁  Exporter CSV", self.exporter_csv)
        self.create_sidebar_btn(sidebar, "save", "💾  Sauvegarder", self.sauvegarder_donnees)
        
        # Spacer
        tk.Frame(sidebar, bg=sidebar_bg).pack(fill=tk.Y, expand=True)
        
        # Bas de sidebar
        self.create_sidebar_btn(sidebar, "theme", "🌓  Thème", self.toggle_theme)
        self.create_sidebar_btn(sidebar, "logout", "🚪  Déconnexion", self.deconnexion, is_danger=True)

        # --- CONTENU PRINCIPAL (Droite) ---
        self.content_area = tk.Frame(main_container, bg=self.colors["bg_main"])
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Afficher la page par défaut
        self.current_page = ""
        self.show_page("dashboard")
        
    def create_gestion_view(self, parent):
        # En-tête de la vue
        header = tk.Frame(parent, bg=self.colors["bg_main"])
        header.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(header, text="Gestion des Étudiants", font=("Segoe UI", 20, "bold"),
                 bg=self.colors["bg_main"], fg=self.colors["fg_head"]).pack(side=tk.LEFT)

        # Barre de recherche intégrée
        search_frame = tk.Frame(header, bg=self.colors["bg_input"], padx=15, pady=8)
        search_frame.pack(side=tk.RIGHT)
        
        tk.Label(search_frame, text="🔍", bg=self.colors["bg_input"], fg=self.colors["fg_text"]).pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filtrer_etudiants)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                               font=("Segoe UI", 10), bg=self.colors["bg_input"], fg=self.colors["fg_text"], width=25, relief=tk.FLAT, insertbackground=self.colors["accent"])
        search_entry.pack(side=tk.LEFT, padx=5)

        # PanedWindow
        self.paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)
        
        # Colonne gauche - Formulaire
        left_frame = tk.Frame(self.paned, bg=self.colors["bg_panel"])
        self.paned.add(left_frame, weight=1)
        
        # En-tête du panneau gauche
        tk.Label(left_frame, text="➕ Ajouter/Modifier", font=("Segoe UI", 12, "bold"), 
                 bg=self.colors["bg_panel"], fg=self.colors["accent"]).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Wrapper pour le formulaire
        form_wrapper = tk.Frame(left_frame, bg=self.colors["bg_panel"], padx=20)
        form_wrapper.pack(fill=tk.BOTH, expand=True)
        
        self.create_form(form_wrapper)
        
        # Colonne droite - Liste
        right_frame = tk.Frame(self.paned, bg=self.colors["bg_main"])
        self.paned.add(right_frame, weight=3)

        # Barre d'état inférieure (Déplacée ici pour garantir la visibilité en bas)
        status_frame = tk.Frame(right_frame, bg=self.colors["bg_main"])
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tk.Label(status_frame, text="", bg=self.colors["bg_main"], fg=self.colors["accent"], 
                                    font=("Segoe UI", 9))
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Boutons de gestion de la sélection
        manage_frame = tk.Frame(status_frame, bg=self.colors["bg_main"])
        manage_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        
        self.create_styled_button(manage_frame, "📧 Email", self.envoyer_email, "#9b59b6").pack(side=tk.LEFT, padx=3)
        self.create_styled_button(manage_frame, "✏️ Modifier", self.modifier_etudiant, self.colors["warning"]).pack(side=tk.LEFT, padx=3)
        self.create_styled_button(manage_frame, "🗑️ Supprimer", self.supprimer_etudiant, self.colors["danger"]).pack(side=tk.LEFT, padx=3)

        # Liste des étudiants
        list_frame = tk.Frame(right_frame, bg=self.colors["bg_panel"]) # Panel pour la liste
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # En-tête de la liste
        header_list = tk.Frame(list_frame, bg=self.colors["bg_panel"])
        header_list.pack(fill=tk.X, padx=20, pady=(15, 10))
        tk.Label(header_list, text="📋 Étudiants Enregistrés", font=("Segoe UI", 12, "bold"), 
                 bg=self.colors["bg_panel"], fg=self.colors["accent"]).pack(side=tk.LEFT)
        
        # Conteneur du tableau
        tree_container = tk.Frame(list_frame, bg=self.colors["bg_panel"], padx=20)
        tree_container.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview avec plus de colonnes
        self.tree = ttk.Treeview(tree_container, columns=("Matricule", "Nom", "Prénom", "Âge", "Moyenne", "Appréciation"), 
                                 height=15, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("Matricule", anchor=tk.CENTER, width=90)
        self.tree.column("Nom", anchor=tk.W, width=100)
        self.tree.column("Prénom", anchor=tk.W, width=100)
        self.tree.column("Âge", anchor=tk.CENTER, width=50)
        self.tree.column("Moyenne", anchor=tk.CENTER, width=80)
        self.tree.column("Appréciation", anchor=tk.CENTER, width=120)
        
        self.tree.heading("#0", text="", anchor=tk.W)
        for col in ["Matricule", "Nom", "Prénom", "Âge", "Moyenne", "Appréciation"]:
            self.tree.heading(col, text=col, anchor=tk.CENTER, 
                            command=lambda c=col: self.trier_colonne(c, False))
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Menu contextuel (Clic Droit)
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="✏️ Modifier", command=self.modifier_etudiant)
        self.context_menu.add_command(label="📧 Envoyer Email", command=self.envoyer_email)
        self.context_menu.add_command(label="️ Supprimer", command=self.supprimer_etudiant)
        self.tree.bind("<Button-3>", self.afficher_menu_contextuel)
        
        self.rafraichir()

    def show_page(self, page_name):
        """Changer de page dans la zone principale"""
        if self.current_page == page_name:
            return
            
        self.current_page = page_name
        
        # Mettre à jour l'apparence des boutons
        for name, btn in self.sidebar_btns.items():
            if name == page_name:
                btn.config(bg=self.colors["bg_main"], fg=self.colors["accent"], font=("Segoe UI", 11, "bold"))
            elif name not in ["export", "save", "theme", "logout"]: # Ne pas changer le style des boutons d'action
                btn.config(bg=self.colors["bg_panel"], fg=self.colors["fg_text"], font=("Segoe UI", 11))

        # Vider la zone de contenu
        for widget in self.content_area.winfo_children():
            widget.destroy()
            
        # Construire la nouvelle page
        if page_name == "dashboard":
            self.create_dashboard_view(self.content_area)
        elif page_name == "gestion":
            self.create_gestion_view(self.content_area)

    def create_dashboard_view(self, parent):
        """Créer la vue Tableau de Bord"""
        # En-tête
        tk.Label(parent, text="Tableau de Bord", font=("Segoe UI", 24, "bold"),
                 bg=self.colors["bg_main"], fg=self.colors["fg_head"]).pack(anchor="w", pady=(0, 20))

        # Calcul des stats
        total = len(self.etudiants)
        moyennes = [sum(e.get("note", []))/len(e.get("note", [])) for e in self.etudiants if e.get("note")]
        moy_gen = sum(moyennes)/len(moyennes) if moyennes else 0
        meilleur = max(moyennes) if moyennes else 0
        
        # Cartes de statistiques (Grid layout)
        cards_frame = tk.Frame(parent, bg=self.colors["bg_main"])
        cards_frame.pack(fill=tk.X, pady=(0, 30))
        
        self.create_stat_card(cards_frame, "Total Étudiants", str(total), "👥").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.create_stat_card(cards_frame, "Moyenne Générale", f"{moy_gen:.2f}/20", "📊").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.create_stat_card(cards_frame, "Meilleure Note", f"{meilleur:.2f}/20", "🏆").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        # Graphiques
        charts_frame = tk.Frame(parent, bg=self.colors["bg_main"])
        charts_frame.pack(fill=tk.BOTH, expand=True)
        
        # Graphique Circulaire (Répartition)
        left_chart = tk.Frame(charts_frame, bg=self.colors["bg_panel"], padx=10, pady=10)
        left_chart.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(left_chart, text="Répartition par Mention", font=("Segoe UI", 12, "bold"), 
                bg=self.colors["bg_panel"], fg=self.colors["fg_text"]).pack(pady=(0, 10))
        
        # Données pour le pie chart
        mentions = {"Excellent": 0, "Très bien": 0, "Bien": 0, "Assez bien": 0, "Passable": 0, "Insuffisant": 0}
        for m in moyennes:
            if m >= 18: mentions["Excellent"] += 1
            elif m >= 16: mentions["Très bien"] += 1
            elif m >= 14: mentions["Bien"] += 1
            elif m >= 12: mentions["Assez bien"] += 1
            elif m >= 10: mentions["Passable"] += 1
            else: mentions["Insuffisant"] += 1
            
        labels = [k for k, v in mentions.items() if v > 0]
        sizes = [v for v in mentions.values() if v > 0]
        colors = ["#2ecc71", "#27ae60", "#3498db", "#2980b9", "#f1c40f", "#e74c3c"]
        
        if sizes:
            fig = plt.Figure(figsize=(4, 3), dpi=100)
            fig.patch.set_facecolor(self.colors["bg_panel"])
            ax = fig.add_subplot(111)
            ax.set_facecolor(self.colors["bg_panel"])
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, textprops={'color': self.colors["fg_text"]})
            canvas = FigureCanvasTkAgg(fig, master=left_chart)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            tk.Label(left_chart, text="Pas assez de données", bg=self.colors["bg_panel"], fg=self.colors["fg_text"]).pack(expand=True)

        # Graphique Barres (Top 5)
        right_chart = tk.Frame(charts_frame, bg=self.colors["bg_panel"], padx=10, pady=10)
        right_chart.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        tk.Label(right_chart, text="Top 5 Étudiants", font=("Segoe UI", 12, "bold"), 
                bg=self.colors["bg_panel"], fg=self.colors["fg_text"]).pack(pady=(0, 10))
                
        top_students = sorted(self.etudiants, key=lambda x: sum(x.get("note", []))/len(x.get("note", [])) if x.get("note") else 0, reverse=True)[:5]
        
        if top_students:
            names = [s['prenom'] for s in top_students]
            vals = [sum(s.get("note", []))/len(s.get("note", [])) for s in top_students]
            
            fig2 = plt.Figure(figsize=(4, 3), dpi=100)
            fig2.patch.set_facecolor(self.colors["bg_panel"])
            ax2 = fig2.add_subplot(111)
            ax2.set_facecolor(self.colors["bg_panel"])
            bars = ax2.bar(names, vals, color=self.colors["accent"])
            ax2.tick_params(axis='x', colors=self.colors["fg_text"])
            ax2.tick_params(axis='y', colors=self.colors["fg_text"])
            ax2.spines['bottom'].set_color(self.colors["fg_text"])
            ax2.spines['left'].set_color(self.colors["fg_text"])
            ax2.spines['top'].set_visible(False)
            ax2.spines['right'].set_visible(False)
            
            canvas2 = FigureCanvasTkAgg(fig2, master=right_chart)
            canvas2.draw()
            canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            tk.Label(right_chart, text="Pas assez de données", bg=self.colors["bg_panel"], fg=self.colors["fg_text"]).pack(expand=True)

    def create_stat_card(self, parent, title, value, icon):
        frame = tk.Frame(parent, bg=self.colors["bg_panel"], padx=20, pady=20)
        tk.Label(frame, text=icon, font=("Segoe UI", 24), bg=self.colors["bg_panel"], fg=self.colors["accent"]).pack(side=tk.LEFT, padx=(0, 15))
        content = tk.Frame(frame, bg=self.colors["bg_panel"])
        content.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(content, text=title, font=("Segoe UI", 10), bg=self.colors["bg_panel"], fg=self.colors["fg_text"]).pack(anchor="w")
        tk.Label(content, text=value, font=("Segoe UI", 16, "bold"), bg=self.colors["bg_panel"], fg=self.colors["fg_head"]).pack(anchor="w")
        return frame

    def create_sidebar_btn(self, parent, name, text, command, is_danger=False):
        bg_color = self.colors["bg_panel"]
        fg_color = self.colors["fg_text"]
        
        if is_danger:
            fg_color = self.colors["danger"]

        btn = tk.Button(parent, text=text, command=command,
                       bg=bg_color, fg=fg_color, font=("Segoe UI", 11),
                       relief=tk.FLAT, activebackground=self.colors["bg_main"], 
                       activeforeground=fg_color,
                       anchor="w", padx=30, pady=12, cursor="hand2", borderwidth=0)
        btn.pack(fill=tk.X, pady=2)
        self.sidebar_btns[name] = btn
        
        if not is_danger:
            def on_enter(e): btn['bg'] = self.colors["bg_main"]
            def on_leave(e): 
                if self.current_page != name:
                    btn['bg'] = bg_color
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            
    def show_toast(self, message, is_error=False):
        """Afficher une notification flottante (Toast)"""
        color = self.colors["danger"] if is_error else self.colors["success"]
        toast = tk.Label(self.root, text=message, bg=color, fg="white", padx=20, pady=10, font=("Segoe UI", 10, "bold"))
        
        # Positionner en bas au centre
        toast.place(relx=0.5, rely=0.9, anchor="center")
        
        # Animation de disparition
        def fade_out():
            toast.destroy()
        self.root.after(3000, fade_out)

    def create_form(self, parent):
        """Créer le formulaire avec meilleure présentation"""
        # Conteneur principal du formulaire pour diviser en 2 colonnes
        form_container = tk.Frame(parent, bg=self.colors["bg_panel"])
        form_container.pack(fill=tk.BOTH, expand=True)
        
        # --- Colonne Gauche : Champs de saisie ---
        inputs_frame = tk.Frame(form_container, bg=self.colors["bg_panel"])
        inputs_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Matricule
        tk.Label(inputs_frame, text="Matricule:", font=("Segoe UI", 10), bg=self.colors["bg_panel"], 
                fg=self.colors["fg_text"]).pack(anchor=tk.W)
        self.matricule_entry = tk.Entry(inputs_frame, width=30, font=("Segoe UI", 10), 
                                        bg=self.colors["bg_input"], fg="white", insertbackground=self.colors["accent"], relief=tk.FLAT)
        self.matricule_entry.pack(anchor=tk.W, pady=(0, 12))
        
        # Nom
        tk.Label(inputs_frame, text="Nom:", font=("Segoe UI", 10), bg=self.colors["bg_panel"], 
                fg=self.colors["fg_text"]).pack(anchor=tk.W)
        self.nom_entry = tk.Entry(inputs_frame, width=30, font=("Segoe UI", 10), 
                                  bg=self.colors["bg_input"], fg="white", insertbackground=self.colors["accent"], relief=tk.FLAT)
        self.nom_entry.pack(anchor=tk.W, pady=(0, 12))
        
        # Prénom
        tk.Label(inputs_frame, text="Prénom:", font=("Segoe UI", 10), bg=self.colors["bg_panel"], 
                fg=self.colors["fg_text"]).pack(anchor=tk.W)
        self.prenom_entry = tk.Entry(inputs_frame, width=30, font=("Segoe UI", 10), 
                                     bg=self.colors["bg_input"], fg="white", insertbackground=self.colors["accent"], relief=tk.FLAT)
        self.prenom_entry.pack(anchor=tk.W, pady=(0, 12))
        
        # Email
        tk.Label(inputs_frame, text="Email:", font=("Segoe UI", 10), bg=self.colors["bg_panel"], 
                fg=self.colors["fg_text"]).pack(anchor=tk.W)
        self.email_entry = tk.Entry(inputs_frame, width=30, font=("Segoe UI", 10), 
                                     bg=self.colors["bg_input"], fg="white", insertbackground=self.colors["accent"], relief=tk.FLAT)
        self.email_entry.pack(anchor=tk.W, pady=(0, 12))
        
        # Téléphone
        tk.Label(inputs_frame, text="Téléphone:", font=("Segoe UI", 10), bg=self.colors["bg_panel"], 
                fg=self.colors["fg_text"]).pack(anchor=tk.W)
        self.telephone_entry = tk.Entry(inputs_frame, width=30, font=("Segoe UI", 10), 
                                     bg=self.colors["bg_input"], fg="white", insertbackground=self.colors["accent"], relief=tk.FLAT)
        self.telephone_entry.pack(anchor=tk.W, pady=(0, 12))
        
        # Âge
        tk.Label(inputs_frame, text="Âge:", font=("Segoe UI", 10), bg=self.colors["bg_panel"], 
                fg=self.colors["fg_text"]).pack(anchor=tk.W)
        self.age_entry = tk.Entry(inputs_frame, width=30, font=("Segoe UI", 10), 
                                  bg=self.colors["bg_input"], fg="white", insertbackground=self.colors["accent"], relief=tk.FLAT)
        self.age_entry.pack(anchor=tk.W, pady=(0, 12))
        
        # --- Colonne Droite : Photo ---
        photo_frame = tk.Frame(form_container, bg=self.colors["bg_panel"])
        photo_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        
        tk.Label(photo_frame, text="Photo de profil:", font=("Segoe UI", 10, "bold"), 
                bg=self.colors["bg_panel"], fg=self.colors["fg_text"]).pack(pady=(0, 5))
        
        # Canvas pour afficher la photo
        self.photo_canvas = tk.Canvas(photo_frame, width=120, height=120, bg=self.colors["bg_input"], highlightthickness=0)
        self.photo_canvas.pack(pady=(0, 10))
        # Texte par défaut dans le canvas
        self.photo_canvas.create_text(60, 60, text="Aucune\nPhoto", fill="gray", justify=tk.CENTER)
        
        # Bouton choisir photo
        self.create_styled_button(photo_frame, "📷 Choisir...", self.choisir_photo, self.colors["accent"]).pack(fill=tk.X, padx=0)
        
        # --- Suite des champs (Notes) en dessous ---
        
        # Nombre de notes
        tk.Label(parent, text="Nombre de notes:", font=("Segoe UI", 10), bg=self.colors["bg_panel"], 
                fg=self.colors["fg_text"]).pack(anchor=tk.W)
        self.nb_notes_entry = tk.Entry(parent, width=30, font=("Segoe UI", 10), 
                                       bg=self.colors["bg_input"], fg="white", insertbackground=self.colors["accent"], relief=tk.FLAT)
        self.nb_notes_entry.pack(anchor=tk.W, pady=(0, 12))
        
        # Notes
        tk.Label(parent, text="Notes (séparées par des virgules):", font=("Segoe UI", 10), 
                bg=self.colors["bg_panel"], fg=self.colors["fg_text"]).pack(anchor=tk.W)
        self.notes_entry = tk.Text(parent, width=28, height=4, font=("Segoe UI", 10), 
                                   bg=self.colors["bg_input"], fg="white", insertbackground=self.colors["accent"], relief=tk.FLAT)
        self.notes_entry.pack(anchor=tk.W, pady=(0, 12))
        
        # Boutons du formulaire
        button_frame = tk.Frame(parent, bg=self.colors["bg_panel"])
        button_frame.pack(anchor=tk.W, pady=15, fill=tk.X)
        
        self.btn_valider = self.create_styled_button(button_frame, "➕ Ajouter", self.gerer_validation, self.colors["success"])
        self.btn_valider.pack(side=tk.LEFT, padx=3)
        self.create_styled_button(button_frame, "🔄 Réinitialiser", self.reinitialiser_formulaire, "#95a5a6").pack(side=tk.LEFT, padx=3)
        
    def create_styled_button(self, parent, text, command, bg_color):
        """Créer un bouton stylisé avec effet de survol"""
        btn = tk.Button(parent, text=text, command=command,
                       bg=bg_color, fg="white", font=("Segoe UI", 9, "bold"),
                       relief=tk.FLAT, activebackground=bg_color, activeforeground="white",
                       padx=15, pady=8, cursor="hand2", borderwidth=0)
        
        # Effet de survol simple (éclaircissement simulé)
        def on_enter(e):
            # On éclaircit légèrement en changeant la couleur (mapping simple)
            colors = {
                "#27ae60": "#2ecc71", "#95a5a6": "#bdc3c7", "#3498db": "#5dade2",
                "#9b59b6": "#af7ac5", "#16a085": "#1abc9c", "#e74c3c": "#ec7063",
                "#f39c12": "#f1c40f", "#c0392b": "#e74c3c"
            }
            btn['bg'] = colors.get(bg_color, bg_color)
            
        def on_leave(e):
            btn['bg'] = bg_color
            
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

    def gerer_validation(self):
        """Diriger vers ajout ou modification selon le mode"""
        if self.editing_matricule is not None:
            self.sauvegarder_modification()
        else:
            self.ajouter_etudiant()
            
    def ajouter_etudiant(self):
        """Ajouter un nouvel étudiant avec validation améliorée"""
        try:
            matricule_str = self.matricule_entry.get().strip()
            if not matricule_str:
                messagebox.showerror("❌ Erreur", "Le matricule est obligatoire")
                return
                
            matricule = int(matricule_str)
            nom = self.nom_entry.get().strip().capitalize()
            prenom = self.prenom_entry.get().strip().capitalize()
            email = self.email_entry.get().strip()
            telephone = self.telephone_entry.get().strip()
            
            age_str = self.age_entry.get().strip()
            if not age_str:
                messagebox.showerror("❌ Erreur", "L'âge est obligatoire")
                return
            age = int(age_str)
            
            if not nom or not prenom:
                messagebox.showerror("❌ Erreur", "Le nom et le prénom sont obligatoires")
                return
                
            if age < 15 or age > 40:
                messagebox.showerror("❌ Erreur", "L'âge doit être entre 15 et 40 ans")
                return
            
            # Vérifier si le matricule existe déjà
            for etudiant in self.etudiants:
                if etudiant["matricule"] == matricule:
                    messagebox.showerror("❌ Erreur", "Ce matricule existe déjà")
                    return
            
            # Traiter les notes
            notes_text = self.notes_entry.get("1.0", tk.END).strip()
            notes = []
            if notes_text:
                try:
                    notes = [float(n.strip()) for n in notes_text.split(",") if n.strip()]
                    for note in notes:
                        if note < 0 or note > 20:
                            messagebox.showerror("❌ Erreur", "Les notes doivent être entre 0 et 20")
                            return
                except ValueError:
                    messagebox.showerror("❌ Erreur", "Veuillez entrer des nombres valides pour les notes")
                    return
            
            # Sauvegarde de la photo
            photo_dest = ""
            if self.current_photo_path:
                ext = os.path.splitext(self.current_photo_path)[1]
                filename = f"{matricule}{ext}"
                photo_dest = os.path.join("photos", filename)
                shutil.copy(self.current_photo_path, photo_dest)

            # Sauvegarde en Base de Données
            with sqlite3.connect("etudiants.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO etudiants VALUES (?,?,?,?,?,?,?,?,?)", 
                    (matricule, nom, prenom, age, json.dumps(notes), 
                     photo_dest, datetime.now().strftime("%d/%m/%Y %H:%M"), email, telephone))
                conn.commit()

            etudiant = {
                "matricule": matricule,
                "nom": nom,
                "prenom": prenom,
                "email": email,
                "telephone": telephone,
                "age": age,
                "note": notes,
                "photo": photo_dest,
                "date_ajout": datetime.now().strftime("%d/%m/%Y %H:%M")
            }
            
            self.etudiants.append(etudiant)
            self.etudiants_filtres = self.etudiants.copy()
            self.show_toast(f"✅ {nom} {prenom} ajouté(e) avec succès")
            self.reinitialiser_formulaire()
            self.rafraichir()
            self.update_status()
            
        except ValueError:
            messagebox.showerror("❌ Erreur", "Veuillez entrer des nombres valides pour le matricule et l'âge")
        except sqlite3.IntegrityError:
            messagebox.showerror("❌ Erreur", "Ce matricule existe déjà dans la base de données")
    
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
            age_str = self.age_entry.get().strip()
            
            if not nom or not prenom or not age_str:
                messagebox.showerror("❌ Erreur", "Tous les champs sont obligatoires")
                return
                
            age = int(age_str)
            if age < 15 or age > 40:
                messagebox.showerror("❌ Erreur", "L'âge doit être entre 15 et 40 ans")
                return

            # Traiter les notes
            notes_text = self.notes_entry.get("1.0", tk.END).strip()
            notes = []
            if notes_text:
                try:
                    notes = [float(n.strip()) for n in notes_text.split(",") if n.strip()]
                    for note in notes:
                        if note < 0 or note > 20:
                            messagebox.showerror("❌ Erreur", "Les notes doivent être entre 0 et 20")
                            return
                except ValueError:
                    messagebox.showerror("❌ Erreur", "Notes invalides")
                    return

            # Gestion de la photo lors de la modification
            photo_dest = etudiant.get("photo", "")
            if self.current_photo_path and self.current_photo_path != photo_dest:
                ext = os.path.splitext(self.current_photo_path)[1]
                filename = f"{etudiant['matricule']}{ext}"
                photo_dest = os.path.join("photos", filename)
                shutil.copy(self.current_photo_path, photo_dest)

            # Mise à jour Base de Données
            with sqlite3.connect("etudiants.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE etudiants SET nom=?, prenom=?, age=?, note=?, photo=?, email=?, telephone=? 
                    WHERE matricule=?
                """, (nom, prenom, age, json.dumps(notes), photo_dest, email, telephone, etudiant['matricule']))
                conn.commit()

            # Mise à jour
            etudiant.update({"nom": nom, "prenom": prenom, "age": age, "note": notes, "photo": photo_dest, "email": email, "telephone": telephone})
            self.show_toast("✅ Modifications enregistrées")
            self.reinitialiser_formulaire()
            self.rafraichir()
            self.update_status()
        except ValueError:
            messagebox.showerror("❌ Erreur", "Valeurs invalides")

    def modifier_etudiant(self):
        """Modifier un étudiant sélectionné"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("⚠️  Avertissement", "Veuillez sélectionner un étudiant à modifier")
            return
        
        item = self.tree.item(selected[0])
        matricule = int(item['values'][0])
        
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
                self.email_entry.insert(0, etudiant.get("email", ""))
                self.telephone_entry.delete(0, tk.END)
                self.telephone_entry.insert(0, etudiant.get("telephone", ""))
                self.age_entry.delete(0, tk.END)
                self.age_entry.insert(0, str(etudiant["age"]))
                self.notes_entry.delete("1.0", tk.END)
                notes_str = ", ".join([str(n) for n in etudiant.get("note", [])])
                self.notes_entry.insert("1.0", notes_str)
                
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
            messagebox.showwarning("⚠️  Avertissement", "Veuillez sélectionner un étudiant à supprimer")
            return
        
        item = self.tree.item(selected[0])
        nom = item['values'][1]
        prenom = item['values'][2]
        
        if messagebox.askyesno("🗑️  Confirmation", f"Êtes-vous sûr de vouloir supprimer {prenom} {nom} ?"):
            matricule = int(item['values'][0])
           
            # Suppression Base de Données
            with sqlite3.connect("etudiants.db") as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM etudiants WHERE matricule=?", (matricule,))
                conn.commit()

            self.etudiants = [e for e in self.etudiants if e["matricule"] != matricule]
                
                # Optionnel : Supprimer le fichier photo
                # for f in os.listdir("photos"):
                #     if f.startswith(str(matricule)):
                #         os.remove(os.path.join("photos", f))
                
            self.etudiants_filtres = self.etudiants.copy()
            self.rafraichir()
            self.update_status()
            self.show_toast("🗑️ Étudiant supprimé")
        
    def envoyer_email(self):
        """Ouvrir le client mail par défaut pour l'étudiant sélectionné"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("⚠️  Avertissement", "Veuillez sélectionner un étudiant")
            return
        
        item = self.tree.item(selected[0])
        matricule = int(item['values'][0])
        
        etudiant = next((e for e in self.etudiants if e["matricule"] == matricule), None)
        
        if etudiant and etudiant.get("email"):
            email = etudiant["email"]
            subject = f"Information Étudiant - {etudiant['prenom']} {etudiant['nom']}"
            webbrowser.open(f"mailto:{email}?subject={subject}")
        else:
            messagebox.showinfo("ℹ️ Information", "Cet étudiant n'a pas d'adresse email enregistrée.")
    
    def filtrer_etudiants(self, *args):
        """Filtrer les étudiants en temps réel"""
        search_term = self.search_var.get().lower().strip()
        
        if not search_term:
            self.etudiants_filtres = self.etudiants.copy()
        else:
            self.etudiants_filtres = [e for e in self.etudiants if 
                                     search_term in e["nom"].lower() or 
                                     search_term in e["prenom"].lower() or 
                                     search_term in str(e["matricule"])]
        
        self.rafraichir()
        self.update_status()
    
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

    def rafraichir(self):
        """Rafraîchir la liste des étudiants"""
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
    
    def afficher_liste(self):
        """Afficher la liste complète des étudiants"""
        if not self.etudiants:
            messagebox.showinfo("ℹ️  Information", "Aucun étudiant enregistré")
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
            messagebox.showinfo("ℹ️  Information", "Aucun étudiant à exporter")
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
                fieldnames = ['Matricule', 'Nom', 'Prénom', 'Email', 'Téléphone', 'Âge', 'Notes', 'Moyenne', 'Appréciation', 'Date d\'ajout']
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
                        'Email': etudiant.get('email', ''),
                        'Téléphone': etudiant.get('telephone', ''),
                        'Âge': etudiant['age'],
                        'Notes': '; '.join([str(n) for n in notes]),
                        'Moyenne': f"{moyenne:.2f}",
                        'Appréciation': appreciation,
                        'Date d\'ajout': etudiant.get('date_ajout', 'N/A')
                    })
            
            self.show_toast(f"✅ Export réussi: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("❌ Erreur", f"Erreur lors de l'export: {e}")
    
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
        self.matricule_entry.delete(0, tk.END)
        self.nom_entry.delete(0, tk.END)
        self.prenom_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.telephone_entry.delete(0, tk.END)
        self.age_entry.delete(0, tk.END)
        self.nb_notes_entry.delete(0, tk.END)
        self.notes_entry.delete("1.0", tk.END)
        self.photo_canvas.delete("all")
        self.photo_canvas.create_text(60, 60, text="Aucune\nPhoto", fill="gray", justify=tk.CENTER)
        self.current_photo_path = None
        self.editing_matricule = None
        self.matricule_entry.config(state=tk.NORMAL)
        self.btn_valider.config(text="➕ Ajouter", bg=self.colors["success"])
    
    def toggle_theme(self):
        """Basculer entre le mode clair et sombre"""
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.colors = self.themes[self.current_theme]
        self.root.config(bg=self.colors["bg_main"])
        self.setup_styles()
        
        # Recréer l'interface
        for widget in self.root.winfo_children():
            if not isinstance(widget, tk.Toplevel):
                widget.destroy()
        self.create_widgets()

    def deconnexion(self):
        """Déconnecter l'utilisateur et revenir à l'écran de connexion"""
        if messagebox.askyesno("Déconnexion", "Voulez-vous vraiment vous déconnecter ?"):
            self.root.withdraw()
            # Nettoyer l'interface pour éviter les doublons lors de la reconnexion
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # Fonction de rappel pour recréer l'interface après reconnexion
            def relancer():
                self.root.deiconify()
                GestionEtudiantsApp(self.root)
            
            LoginWindow(self.root, relancer)

    def init_db(self):
        """Initialiser la base de données SQLite"""
        try:
            with sqlite3.connect("etudiants.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS etudiants (
                        matricule INTEGER PRIMARY KEY,
                        nom TEXT,
                        prenom TEXT,
                        age INTEGER,
                        note TEXT,
                        photo TEXT,
                        date_ajout TEXT,
                        email TEXT,
                        telephone TEXT
                    )
                """)
                
                # Migration : Ajouter la colonne email si elle n'existe pas (pour les anciennes BD)
                try:
                    cursor.execute("ALTER TABLE etudiants ADD COLUMN email TEXT")
                except sqlite3.OperationalError:
                    pass # La colonne existe déjà
                
                try:
                    cursor.execute("ALTER TABLE etudiants ADD COLUMN telephone TEXT")
                except sqlite3.OperationalError:
                    pass 
                    
                conn.commit()
        except Exception as e:
            messagebox.showerror("Erreur BD", f"Impossible d'initialiser la base de données: {e}")

    def charger_donnees(self):
        """Charger les données depuis la base de données SQLite"""
        self.etudiants = []
        try:
            with sqlite3.connect("etudiants.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM etudiants")
                rows = cursor.fetchall()
                
                # Migration: Si la BD est vide mais qu'un JSON existe, on importe le JSON
                if not rows and os.path.exists("etudiants.json"):
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
                        "telephone": row[8] if len(row) > 8 else ""
                    })
            self.etudiants_filtres = self.etudiants.copy()
        except Exception as e:
            messagebox.showerror("❌ Erreur", f"Erreur lors du chargement: {e}")
    
    def migrer_json_vers_sqlite(self, cursor, conn):
        """Importer les données JSON existantes dans SQLite"""
        try:
            with open("etudiants.json", "r", encoding="utf-8") as fichier:
                data = json.load(fichier)
                for e in data:
                    cursor.execute("INSERT OR IGNORE INTO etudiants VALUES (?,?,?,?,?,?,?,?,?)", 
                        (e['matricule'], e['nom'], e['prenom'], e['age'], 
                         json.dumps(e.get('note', [])), e.get('photo', ''), e.get('date_ajout', ''), e.get('email', ''), e.get('telephone', '')))
                conn.commit()
                messagebox.showinfo("Migration", "Vos anciennes données JSON ont été importées dans la base de données SQLite.")
        except Exception as e:
            print(f"Erreur migration: {e}")

    def sauvegarder_donnees(self):
        """Sauvegarder les données dans le fichier JSON (Backup)"""
        try:
            with open("etudiants.json", "w", encoding="utf-8") as fichier:
                json.dump(self.etudiants, fichier, indent=4, ensure_ascii=False)
            self.show_toast("✅ Sauvegarde JSON effectuée")
        except Exception as e:
            messagebox.showerror("❌ Erreur", f"Erreur lors de la sauvegarde: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw() # Cacher la fenêtre principale au démarrage
    
    def lancer_application():
        root.deiconify() # Afficher la fenêtre principale
        app = GestionEtudiantsApp(root)
    
    # Lancer l'écran de connexion
    LoginWindow(root, lancer_application)
    
    root.mainloop()