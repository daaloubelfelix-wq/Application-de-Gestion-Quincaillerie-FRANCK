"""
Illustration de fond pour l'écran d'accueil : outils de quincaillerie
dessinés directement (QPainter), pour ne dépendre d'aucune image externe.
Remplacer par de vraies photos de la boutique est possible plus tard —
voir README.
"""

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen, QPolygonF
from PyQt6.QtWidgets import QWidget


class IllustrationOutils(QWidget):
    def __init__(self, parent=None, rayon_coins=0, afficher_titre=True):
        super().__init__(parent)
        self.setMinimumWidth(360)
        self.rayon_coins = rayon_coins
        self.afficher_titre = afficher_titre

    def paintEvent(self, event):
        peintre = QPainter(self)
        peintre.setRenderHint(QPainter.RenderHint.Antialiasing)

        largeur = self.width()
        hauteur = self.height()

        if self.rayon_coins:
            chemin = QPainterPath()
            chemin.addRoundedRect(QRectF(self.rect()), self.rayon_coins, self.rayon_coins)
            peintre.setClipPath(chemin)

        degrade = QLinearGradient(0, 0, largeur, hauteur)
        degrade.setColorAt(0.0, QColor("#3D5066"))
        degrade.setColorAt(1.0, QColor("#22303F"))
        peintre.fillRect(self.rect(), degrade)

        self._dessiner_marteau(peintre, largeur * 0.20, hauteur * 0.30, largeur * 0.16)
        self._dessiner_cle(peintre, largeur * 0.68, hauteur * 0.22, largeur * 0.15)
        self._dessiner_pot_peinture(peintre, largeur * 0.62, hauteur * 0.62, largeur * 0.14)
        self._dessiner_vis(peintre, largeur * 0.22, hauteur * 0.68, largeur * 0.05)
        self._dessiner_vis(peintre, largeur * 0.32, hauteur * 0.74, largeur * 0.035)
        self._dessiner_vis(peintre, largeur * 0.14, hauteur * 0.55, largeur * 0.03)

        if self.afficher_titre:
            self._dessiner_titre(peintre, largeur, hauteur)
        peintre.end()

    def _dessiner_titre(self, peintre, largeur, hauteur):
        zone_titre = QRectF(largeur * 0.08, hauteur * 0.74, largeur * 0.84, hauteur * 0.16)

        taille_police = min(26, max(14, int(largeur * 0.034)))
        police_titre = QFont("Segoe UI", taille_police, QFont.Weight.Bold)
        peintre.setFont(police_titre)
        peintre.setPen(QPen(QColor("#FFFFFF")))
        peintre.drawText(
            zone_titre,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom | Qt.TextFlag.TextWordWrap,
            "Ets Quincaillerie Franck",
        )

        peintre.setPen(QPen(QColor("#C7D3DD")))
        police_sous_titre = QFont("Segoe UI", max(9, int(largeur * 0.018)))
        peintre.setFont(police_sous_titre)
        zone_sous_titre = QRectF(largeur * 0.08, hauteur * 0.90, largeur * 0.84, hauteur * 0.07)
        peintre.drawText(zone_sous_titre, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                          "Batouri, Région de l'Est, Cameroun")

    def _dessiner_marteau(self, peintre, x, y, taille):
        peintre.save()
        peintre.translate(x, y)
        peintre.rotate(-35)

        peintre.setPen(Qt.PenStyle.NoPen)
        peintre.setBrush(QColor("#B8710F"))
        manche = QRectF(-taille * 0.06, 0, taille * 0.12, taille * 0.9)
        peintre.drawRoundedRect(manche, taille * 0.03, taille * 0.03)

        peintre.setBrush(QColor("#EAE5D7"))
        tete = QRectF(-taille * 0.32, -taille * 0.16, taille * 0.64, taille * 0.28)
        peintre.drawRoundedRect(tete, taille * 0.05, taille * 0.05)
        peintre.restore()

    def _dessiner_cle(self, peintre, x, y, taille):
        """Clé à anneau : manche + anneau ouvert à une extrémité."""
        peintre.save()
        peintre.translate(x, y)
        peintre.rotate(-15)

        peintre.setPen(Qt.PenStyle.NoPen)
        peintre.setBrush(QColor("#EAE5D7"))

        manche = QRectF(-taille * 0.09, -taille * 0.05, taille * 0.75, taille * 0.10)
        peintre.drawRoundedRect(manche, taille * 0.05, taille * 0.05)

        centre_anneau = QPointF(-taille * 0.12, 0)
        peintre.drawEllipse(centre_anneau, taille * 0.30, taille * 0.30)
        peintre.setBrush(QColor("#22303F"))
        peintre.drawEllipse(centre_anneau, taille * 0.15, taille * 0.15)
        peintre.restore()

    def _dessiner_pot_peinture(self, peintre, x, y, taille):
        peintre.save()
        peintre.translate(x, y)

        peintre.setPen(Qt.PenStyle.NoPen)
        peintre.setBrush(QColor("#EAE5D7"))
        corps = QPolygonF([
            QPointF(-taille * 0.4, -taille * 0.35),
            QPointF(taille * 0.4, -taille * 0.35),
            QPointF(taille * 0.32, taille * 0.4),
            QPointF(-taille * 0.32, taille * 0.4),
        ])
        peintre.drawPolygon(corps)

        peintre.setBrush(QColor("#B8710F"))
        couvercle = QRectF(-taille * 0.46, -taille * 0.48, taille * 0.92, taille * 0.16)
        peintre.drawRoundedRect(couvercle, taille * 0.04, taille * 0.04)

        peintre.setPen(QPen(QColor("#3D5066"), taille * 0.05))
        peintre.drawArc(
            QRectF(-taille * 0.3, -taille * 0.75, taille * 0.6, taille * 0.6),
            20 * 16, 140 * 16,
        )
        peintre.restore()

    def _dessiner_vis(self, peintre, x, y, taille):
        """Tête de boulon hexagonale."""
        peintre.save()
        peintre.translate(x, y)
        peintre.setPen(Qt.PenStyle.NoPen)
        peintre.setBrush(QColor(234, 229, 215, 190))

        hexagone = QPolygonF([
            QPointF(taille * 1.0, 0),
            QPointF(taille * 0.5, taille * 0.87),
            QPointF(-taille * 0.5, taille * 0.87),
            QPointF(-taille * 1.0, 0),
            QPointF(-taille * 0.5, -taille * 0.87),
            QPointF(taille * 0.5, -taille * 0.87),
        ])
        peintre.drawPolygon(hexagone)

        peintre.setBrush(QColor("#22303F"))
        peintre.drawEllipse(QPointF(0, 0), taille * 0.32, taille * 0.32)
        peintre.restore()
