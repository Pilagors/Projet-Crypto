
import random

from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

from ui.card_widget import CardWidget

# grille d'affichage des cartes
class CardArea(QScrollArea):

    changement_ordre = pyqtSignal(list)

    COLUMNS = 13

    def __init__(self, deck: list[int], parent=None):
        super().__init__(parent)

        self.deck = list(deck)
        self._drag_source_index : int | None = None

        self.container = QWidget()
        self.layout = QGridLayout(self.container)
        self.layout.setSpacing(6)
        self.layout.setContentsMargins(10, 10, 10, 10)

        self.setWidget(self.container)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.container.setAcceptDrops(True)
        self.container.dragEnterEvent = self._on_drag_enter
        self.container.dropEvent = self._on_drop

        self.afficher_cartes()

    def afficher_cartes(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for i, valeur in enumerate(self.deck):
            carte = CardWidget(valeur)
            carte.setProperty("index", i)
            row, col = divmod(i, self.COLUMNS)
            self.layout.addWidget(carte, row, col)

    def set_deck(self, deck: list[int]):
        self.deck = list(deck)
        self.afficher_cartes()

    def melanger_deck(self):
        random.shuffle(self.deck)
        self.afficher_cartes()
        self.changement_ordre.emit(self.deck)

    # drag et drop
    def _on_drag_enter(self, event: QDragEnterEvent):
        if event.mimeData().hasFormat('application/x-carte-valeur'):
            event.acceptProposedAction()

    def _on_drop(self, event: QDropEvent):
        if not event.mimeData().hasFormat('application/x-carte-valeur'):
            return
        
        carte_drag = int(event.mimeData().data('application/x-carte-valeur').data())

        position = event.position().toPoint()
        cible = self.container.childAt(position)

        if isinstance(cible, CardWidget) and cible.valeur != carte_drag:
            index = self.deck.index(carte_drag)
            cible_index = self.deck.index(cible.valeur)

            self.deck[index], self.deck[cible_index] = self.deck[cible_index], self.deck[index]
            self.afficher_cartes()
            self.changement_ordre.emit(self.deck)

        event.acceptProposedAction()