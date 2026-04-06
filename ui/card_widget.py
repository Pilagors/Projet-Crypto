from PyQt6.QtWidgets import QLabel, QSizePolicy
from PyQt6.QtCore import Qt, QMimeData, QByteArray
from PyQt6.QtGui import QDrag, QPixmap, QPainter, QColor, QFont
from src.mapper import *

class CardWidget(QLabel):

    CARD_W = 80
    CARD_H = 112

    def __init__(self, valeur, parent=None):
        super().__init__(parent)
        self.valeur = valeur

        self.setFixedSize(self.CARD_W, self.CARD_H)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.charger_carte()
        self.style_carte()

    def charger_carte(self):
        chemin = carte_vers_chemin(self.valeur)
        pixmap = QPixmap(chemin)

        if pixmap.isNull():
            pixmap = self.image_manquante()

        else:
            pixmap = pixmap.scaled(
                self.CARD_W, self.CARD_H,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

        self.setPixmap(pixmap)
        self.setToolTip(carte_vers_label(self.valeur))

    def image_manquante(self):
        pixmap = QPixmap(self.CARD_W, self.CARD_H)
        pixmap.fill(Qt.GlobalColor.gray)

        painter = QPainter(pixmap)
        painter.setPen(QColor('red'))
        painter.setFont(QFont('Arial', 10))
        
        label = carte_vers_label(self.valeur)
        parts = label.split(" de ")

        if len(parts) == 2:
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, f"{parts[0]}\n {parts[1]}")
        else:
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, label)

        painter.end()

        return pixmap

    def style_carte(self):
        self.setStyleSheet("""
            QLabel {
                border: 1px solid black;
                border-radius: 5px;
                background: transparent;
                padding: 0px;
            }
            QLabel:hover {
                border: 2px solid blue;
                border-radius: 6px;
            }          
        """)

    # Override
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_position = event.position().toPoint()
        return super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        
        if not hasattr(self, "_drag_start_position"):
            return
        
        drag = QDrag(self)
        mime = QMimeData()

        mime.setData("application/x-carte-valeur", QByteArray(str(self.valeur).encode()))
        drag.setMimeData(mime)

        # aperçu pendant le drag
        pixmap = self.grab()
        drag.setPixmap(pixmap)
        drag.setHotSpot(self._drag_start_position)

        self.setOpacity(0.4)
        drag.exec(Qt.DropAction.MoveAction)
        self.setOpacity(1.0)

    def setOpacity(self, valeur):
        self.setStyleSheet(f"""

            QLabel {{
                border: 1px solid black;
                border-radius: 6px;
                background: transparent;
                opacity: {valeur};
            }}
        """)

    def refresh(self):
        self.charger_carte()