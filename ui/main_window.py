"""
ui/main_window.py
Fenêtre principale de l'application Solitaire Crypto.

Fonctionnalités :
  - Visualisation et réordonnement du jeu (clé)
  - Génération aléatoire de clé
  - Chiffrage / déchiffrage de texte saisi
  - Import de fichier .txt à chiffrer ou déchiffrer
"""

import os
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from src.solitaire import *
from ui.card_area import CardArea
from src.mapper import get_cartes


# thread à part 

class CryptoWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, mode: str, text: str, deck: list[int]):
        super().__init__()
        self.mode = mode      # "encrypt" ou "decrypt"
        self.text = text
        self.deck = deck

    def run(self):
        try:
            s = Solitaire(self.deck)
            if self.mode == "encrypt":
                resultat = s.chiffrage_final(self.text)
            else:
                resultat = s.dechiffrage_final(self.text)
            self.finished.emit(resultat)
        except Exception as e:
            self.error.emit(str(e))

# fenêtre principale

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Solitaire Crypto")
        self.setMinimumSize(1100, 700)

        self.deck = get_cartes()   # jeu courant
        self.worker: CryptoWorker | None = None

        self.init_ui()
        self.style_application()

    # UI principale

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 8)
        root.setSpacing(8)

        # Barre d'outils haut
        root.addLayout(self.init_toolbar())

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Panneau gauche
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)

        deck_label = QLabel("Jeu de cartes (clé de chiffrement)")
        deck_label.setObjectName("sectionTitle")
        left_layout.addWidget(deck_label)

        self.affichage_cartes = CardArea(self.deck)
        self.affichage_cartes.changement_ordre.connect(self.on_changement_deck)
        left_layout.addWidget(self.affichage_cartes)

        splitter.addWidget(left)

        # Panneau droit
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)

        crypto_label = QLabel("Chiffrement / Déchiffrement")
        crypto_label.setObjectName("sectionTitle")
        right_layout.addWidget(crypto_label)
        right_layout.addWidget(self.init_panneau_cryptage())

        splitter.addWidget(right)
        splitter.setSizes([1000, 300])

        root.addWidget(splitter, stretch=1)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Prêt : Jeu par défaut chargé (ordre 1-54)")

    # UI localisées

    def init_toolbar(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        btn_reset = QPushButton("Réinitialiser le jeu")
        btn_reset.setObjectName("toolBtn")
        btn_reset.clicked.connect(self.reset_deck)

        btn_shuffle = QPushButton("Clé aléatoire")
        btn_shuffle.setObjectName("toolBtn")
        btn_shuffle.setObjectName("primaryBtn")
        btn_shuffle.clicked.connect(self.melange_deck)

        layout.addWidget(btn_reset)
        layout.addWidget(btn_shuffle)
        layout.addStretch()

        return layout

    def init_panneau_cryptage(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # Mode encrypt / decrypt
        mode_group = QGroupBox("Mode")
        mode_layout = QHBoxLayout(mode_group)
        self.radio_encrypt = QRadioButton("Chiffrer")
        self.radio_decrypt = QRadioButton("Déchiffrer")
        self.radio_encrypt.setChecked(True)
        btn_group = QButtonGroup(self)
        btn_group.addButton(self.radio_encrypt)
        btn_group.addButton(self.radio_decrypt)
        mode_layout.addWidget(self.radio_encrypt)
        mode_layout.addWidget(self.radio_decrypt)
        layout.addWidget(mode_group)

        # Tabs : texte direct / fichier
        tabs = QTabWidget()

        # Tab texte
        text_tab = QWidget()
        text_layout = QVBoxLayout(text_tab)
        text_layout.addWidget(QLabel("Texte d'entrée :"))
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Saisir le texte ici…")
        self.input_text.setMaximumHeight(120)
        text_layout.addWidget(self.input_text)

        btn_run_text = QPushButton("Lancer")
        btn_run_text.setObjectName("primaryBtn")
        btn_run_text.clicked.connect(self.run_text_crypto)
        text_layout.addWidget(btn_run_text)
        tabs.addTab(text_tab, "Texte")

        # Tab fichier
        file_tab = QWidget()
        file_layout = QVBoxLayout(file_tab)
        self.file_label = QLabel("Aucun fichier sélectionné")
        self.file_label.setObjectName("filePath")
        btn_browse = QPushButton("Parcourir…")
        btn_browse.clicked.connect(self.browse_file)
        btn_run_file = QPushButton("Lancer sur le fichier")
        btn_run_file.setObjectName("primaryBtn")
        btn_run_file.clicked.connect(self.run_file_crypto)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(btn_browse)
        file_layout.addStretch()
        file_layout.addWidget(btn_run_file)
        tabs.addTab(file_tab, "Fichier")

        layout.addWidget(tabs)

        # Bouton copier
        btn_copy = QPushButton("Copier le résultat")
        btn_copy.clicked.connect(self.copier_resultat)
        layout.addWidget(btn_copy)

        # Résultat
        layout.addWidget(QLabel("Résultat :"))
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("Le résultat apparaîtra ici…")
        layout.addWidget(self.output_text, stretch=1)

        return widget

    # Deck

    def on_changement_deck(self, deck: list[int]):
        self.deck = deck
        self.status.showMessage(f"Jeu réordonné : Nouvelle clé définie ({len(deck)} cartes)")

    def reset_deck(self):
        self.deck = get_cartes()
        self.affichage_cartes.set_deck(self.deck)
        self.status.showMessage("Jeu réinitialisé (ordre 1-54)")

    def melange_deck(self):
        self.affichage_cartes.melanger_deck()
        self.status.showMessage("Clé aléatoire générée ✓")
        
    # Crypter texte

    def run_text_crypto(self):
        text = self.input_text.toPlainText().strip()
        if not text:
            self.status.showMessage("Texte vide !")
            return
        mode = "encrypt" if self.radio_encrypt.isChecked() else "decrypt"
        self.launch_worker(mode, text)

    # Crypter fichier

    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Choisir un fichier texte", "",
            "Fichiers texte (*.txt *.crypt *.decrypt);;Tous les fichiers (*)"
        )
        if path:
            self.selected_file = path
            self.file_label.setText(os.path.basename(path))
            self.status.showMessage(f"Fichier sélectionné : {path}")

    def run_file_crypto(self):
        if not hasattr(self, "selected_file"):
            self.status.showMessage("Aucun fichier sélectionné !")
            return

        mode = "encrypt" if self.radio_encrypt.isChecked() else "decrypt"
        path = self.selected_file

        try:
            if mode == "encrypt":
                result = chiffrage_fichier(path, self.deck)
            else:
                result = dechiffrage_fichier(path, self.deck)

            if result is not None:
                self.output_text.setPlainText(result)
                ext = ".crypt" if mode == "encrypt" else ".decrypt"
                self.status.showMessage("Fichier sauvegardé !")
            else:
                self.status.showMessage("Erreur : fichier illisible ou vide.")

        except Exception as e:
            self.status.showMessage(f"Erreur lecture : {e}")
            return

    # Worker

    def launch_worker(self, mode: str, text: str, save_to_file: bool = False):
        self.output_text.setPlainText("Traitement en cours…")
        self.save_to_file = save_to_file

        self.worker = CryptoWorker(mode, text, list(self.deck))
        self.worker.finished.connect(self.on_crypter_fini)
        self.worker.error.connect(self.on_crypter_erreur)
        self.worker.start()

    def on_crypter_fini(self, result: str):
        self.output_text.setPlainText(result)
        self.status.showMessage("Traitement terminé")

        if self.save_to_file and hasattr(self, "selected_file"):
            mode = "encrypt" if self.radio_encrypt.isChecked() else "decrypt"
            ext = ".crypt" if mode == "encrypt" else ".decrypt"
            out_path = self.selected_file + ext
            try:
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(result)
                self.status.showMessage(f"Fichier sauvegardé : {out_path}")
            except Exception as e:
                self.status.showMessage(f"Erreur écriture : {e}")

    def on_crypter_erreur(self, msg: str):
        self.output_text.setPlainText(f"Erreur : {msg}")
        self.status.showMessage(f"Erreur : {msg}")

    def copier_resultat(self):
        from PyQt6.QtWidgets import QApplication
        QApplication.clipboard().setText(self.output_text.toPlainText())
        self.status.showMessage("Résultat copié dans le presse-papiers")

    # ------------------------------------------------------------------
    # Style
    # ------------------------------------------------------------------

    def style_application(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #0f1117;
                color: #e0e0e0;
                font-family: "Segoe UI", "Ubuntu", sans-serif;
                font-size: 13px;
            }
            #sectionTitle {
                font-size: 14px;
                font-weight: bold;
                color: #7eb8f7;
                padding: 4px 0px;
            }
            QPushButton {
                background-color: #1e2130;
                color: #c8d0e0;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 6px 14px;
            }
            QPushButton:hover {
                background-color: #2a2f45;
                border-color: #555;
            }
            QPushButton#primaryBtn {
                background-color: #1a4a8a;
                color: #ffffff;
                border: 1px solid #2d6abf;
                font-weight: bold;
            }
            QPushButton#primaryBtn:hover {
                background-color: #2060b0;
            }
            QTextEdit {
                background-color: #161b27;
                border: 1px solid #2a2f45;
                border-radius: 6px;
                padding: 6px;
                color: #e0e0e0;
                font-family: "Consolas", "Courier New", monospace;
            }
            QGroupBox {
                border: 1px solid #2a2f45;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 6px;
                color: #a0b0c8;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
            }
            QTabWidget::pane {
                border: 1px solid #2a2f45;
                border-radius: 6px;
            }
            QTabBar::tab {
                background: #161b27;
                color: #888;
                padding: 6px 18px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background: #1e2130;
                color: #7eb8f7;
            }
            QComboBox {
                background: #1e2130;
                border: 1px solid #333;
                border-radius: 5px;
                padding: 4px 10px;
                color: #c8d0e0;
            }
            QScrollArea {
                background: #0f1117;
            }
            QStatusBar {
                color: #666;
                font-size: 11px;
            }
            #filePath {
                color: #7eb8f7;
                font-style: italic;
            }
            QRadioButton {
                spacing: 6px;
            }
            QRadioButton::indicator {
                width: 14px;
                height: 14px;
            }
        """)