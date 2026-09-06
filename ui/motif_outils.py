"""
Fond en filigrane façon "atelier" pour l'écran de connexion : un motif
d'outils (marteau, vis, écrou, clé) répété en mosaïque légèrement pivotée,
peint en très faible opacité derrière le formulaire — repris du modèle
HTML validé (voir #ecran-connexion .fond-outils).
"""

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QWidget


class MotifOutilsFond(QWidget):
    def __init__(self, couleur="#152C4D", opacite=0.12, taille_tuile=100, parent=None):
        super().__init__(parent)
        self._couleur = QColor(couleur)
        self._couleur.setAlphaF(opacite)
        self._taille_tuile = taille_tuile
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def paintEvent(self, event):
        peintre = QPainter(self)
        peintre.setRenderHint(QPainter.RenderHint.Antialiasing)

        peintre.translate(self.width() / 2, self.height() / 2)
        peintre.rotate(6)
        peintre.translate(-self.width() / 2, -self.height() / 2)

        diagonale = int((self.width() ** 2 + self.height() ** 2) ** 0.5) + self._taille_tuile
        t = self._taille_tuile
        for gx in range(-t, diagonale, t):
            for gy in range(-t, diagonale, t):
                peintre.save()
                peintre.translate(gx, gy)
                self._dessiner_tuile(peintre, t)
                peintre.restore()

        peintre.end()

    def _dessiner_tuile(self, peintre, t):
        s = t / 110.0

        # Marteau
        peintre.save()
        peintre.translate(8 * s, 12 * s)
        peintre.rotate(-10)
        peintre.setPen(Qt.PenStyle.NoPen)
        peintre.setBrush(self._couleur)
        peintre.drawRoundedRect(QRectF(0, 0, 24 * s, 10 * s), 2 * s, 2 * s)
        peintre.drawRoundedRect(QRectF(9 * s, 8 * s, 6 * s, 32 * s), 2 * s, 2 * s)
        peintre.restore()

        # Vis
        peintre.save()
        peintre.translate(70 * s, 8 * s)
        peintre.rotate(25)
        peintre.setPen(Qt.PenStyle.NoPen)
        peintre.setBrush(self._couleur)
        peintre.drawRoundedRect(QRectF(0, 0, 11 * s, 4.5 * s), 1 * s, 1 * s)
        peintre.drawRect(QRectF(4 * s, 3.5 * s, 2.5 * s, 24 * s))
        peintre.restore()

        # Écrou (cercle + fente)
        peintre.save()
        stylo = QPen(self._couleur, 3 * s)
        peintre.setPen(stylo)
        peintre.setBrush(Qt.BrushStyle.NoBrush)
        peintre.drawEllipse(QPointF(24 * s, 82 * s), 7 * s, 7 * s)
        peintre.drawLine(QPointF(19 * s, 82 * s), QPointF(29 * s, 82 * s))
        peintre.restore()

        # Clé plate
        peintre.save()
        peintre.translate(58 * s, 60 * s)
        peintre.rotate(18)
        stylo_cle = QPen(self._couleur, 4 * s)
        stylo_cle.setCapStyle(Qt.PenCapStyle.RoundCap)
        peintre.setPen(stylo_cle)
        peintre.drawLine(QPointF(0, 0), QPointF(24 * s, 0))
        peintre.drawEllipse(QPointF(0, 0), 6 * s, 6 * s)
        peintre.drawEllipse(QPointF(24 * s, 0), 6 * s, 6 * s)
        peintre.restore()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update()
