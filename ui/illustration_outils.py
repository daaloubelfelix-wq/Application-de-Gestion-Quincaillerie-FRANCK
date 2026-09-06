"""
Illustration de fond pour l'écran d'accueil : un mur à outils façon
quincaillerie (pegboard perforé, rail, outils accrochés), dessiné
directement (QPainter), pour ne dépendre d'aucune image externe.
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
        degrade.setColorAt(0.0, QColor("#2A2A2A"))
        degrade.setColorAt(1.0, QColor("#141414"))
        peintre.fillRect(self.rect(), degrade)

        self._dessiner_texture_pegboard(peintre, largeur, hauteur)

        y_rail = hauteur * 0.30
        self._dessiner_rail(peintre, largeur, y_rail)

        taille_outil = min(largeur, hauteur) * 0.20
        positions = [0.14, 0.32, 0.5, 0.68, 0.86]
        dessinateurs = [
            self._dessiner_marteau,
            self._dessiner_cle,
            self._dessiner_tournevis,
            self._dessiner_metre_ruban,
            self._dessiner_pot_peinture,
        ]
        for fraction_x, dessiner in zip(positions, dessinateurs):
            x = largeur * fraction_x
            self._dessiner_crochet(peintre, x, y_rail)
            dessiner(peintre, x, y_rail + 16, taille_outil)

        if self.afficher_titre:
            self._dessiner_titre(peintre, largeur, hauteur)
        peintre.end()

    def _dessiner_texture_pegboard(self, peintre, largeur, hauteur):
        """Petits trous perforés en grille, comme un panneau à outils."""
        peintre.save()
        peintre.setPen(Qt.PenStyle.NoPen)
        peintre.setBrush(QColor(255, 255, 255, 16))
        pas = max(22, int(largeur * 0.055))
        y = pas
        while y < hauteur:
            x = pas
            while x < largeur:
                peintre.drawEllipse(QPointF(x, y), 1.6, 1.6)
                x += pas
            y += pas
        peintre.restore()

    def _dessiner_rail(self, peintre, largeur, y_rail):
        """Rail horizontal sur lequel les outils sont accrochés."""
        peintre.save()
        peintre.setPen(Qt.PenStyle.NoPen)
        peintre.setBrush(QColor("#0F0F0F"))
        rail = QRectF(largeur * 0.06, y_rail - 5, largeur * 0.88, 9)
        peintre.drawRoundedRect(rail, 3, 3)
        peintre.setPen(QPen(QColor(255, 255, 255, 45), 1))
        peintre.drawLine(QPointF(largeur * 0.06, y_rail - 5), QPointF(largeur * 0.94, y_rail - 5))
        peintre.restore()

    def _dessiner_crochet(self, peintre, x, y_rail):
        """Petit crochet reliant le rail à l'outil suspendu."""
        peintre.save()
        peintre.setPen(QPen(QColor("#5A5A5A"), 2))
        peintre.drawLine(QPointF(x, y_rail + 4), QPointF(x, y_rail + 16))
        peintre.restore()

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

        peintre.setPen(QPen(QColor("#E5E5E5")))
        police_sous_titre = QFont("Segoe UI", max(9, int(largeur * 0.018)))
        peintre.setFont(police_sous_titre)
        zone_sous_titre = QRectF(largeur * 0.08, hauteur * 0.90, largeur * 0.84, hauteur * 0.07)
        peintre.drawText(zone_sous_titre, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                          "Batouri, Région de l'Est, Cameroun")

    def _dessiner_marteau(self, peintre, x, y, taille):
        peintre.save()
        peintre.translate(x, y)
        peintre.setPen(Qt.PenStyle.NoPen)

        peintre.setBrush(QColor("#E5E5E5"))
        tete = QRectF(-taille * 0.32, 0, taille * 0.64, taille * 0.24)
        peintre.drawRoundedRect(tete, taille * 0.05, taille * 0.05)

        peintre.setBrush(QColor("#FF7A18"))
        manche = QRectF(-taille * 0.06, taille * 0.2, taille * 0.12, taille * 0.62)
        peintre.drawRoundedRect(manche, taille * 0.03, taille * 0.03)
        peintre.restore()

    def _dessiner_cle(self, peintre, x, y, taille):
        """Clé à anneau : anneau en haut, manche vers le bas."""
        peintre.save()
        peintre.translate(x, y)
        peintre.setPen(Qt.PenStyle.NoPen)
        peintre.setBrush(QColor("#E5E5E5"))

        centre_anneau = QPointF(0, taille * 0.18)
        peintre.drawEllipse(centre_anneau, taille * 0.24, taille * 0.24)
        peintre.setBrush(QColor("#141414"))
        peintre.drawEllipse(centre_anneau, taille * 0.12, taille * 0.12)

        peintre.setBrush(QColor("#E5E5E5"))
        manche = QRectF(-taille * 0.07, taille * 0.36, taille * 0.14, taille * 0.48)
        peintre.drawRoundedRect(manche, taille * 0.04, taille * 0.04)
        peintre.restore()

    def _dessiner_tournevis(self, peintre, x, y, taille):
        """Manche en haut, tige plate vers le bas."""
        peintre.save()
        peintre.translate(x, y)
        peintre.setPen(Qt.PenStyle.NoPen)

        peintre.setBrush(QColor("#FF7A18"))
        manche = QRectF(-taille * 0.15, 0, taille * 0.3, taille * 0.32)
        peintre.drawRoundedRect(manche, taille * 0.08, taille * 0.08)

        peintre.setBrush(QColor("#E5E5E5"))
        tige = QRectF(-taille * 0.045, taille * 0.28, taille * 0.09, taille * 0.5)
        peintre.drawRoundedRect(tige, taille * 0.02, taille * 0.02)
        peintre.restore()

    def _dessiner_metre_ruban(self, peintre, x, y, taille):
        """Mètre ruban : boîtier rond avec une languette."""
        peintre.save()
        peintre.translate(x, y)
        peintre.setPen(Qt.PenStyle.NoPen)

        centre = QPointF(0, taille * 0.24)
        peintre.setBrush(QColor("#E5E5E5"))
        peintre.drawEllipse(centre, taille * 0.26, taille * 0.26)
        peintre.setBrush(QColor("#FF7A18"))
        peintre.drawEllipse(centre, taille * 0.1, taille * 0.1)

        peintre.setBrush(QColor("#E5E5E5"))
        languette = QRectF(taille * 0.16, taille * 0.16, taille * 0.18, taille * 0.1)
        peintre.drawRoundedRect(languette, taille * 0.02, taille * 0.02)
        peintre.restore()

    def _dessiner_pot_peinture(self, peintre, x, y, taille):
        peintre.save()
        peintre.translate(x, y + taille * 0.5)

        peintre.setPen(Qt.PenStyle.NoPen)
        peintre.setBrush(QColor("#E5E5E5"))
        corps = QPolygonF([
            QPointF(-taille * 0.36, -taille * 0.28),
            QPointF(taille * 0.36, -taille * 0.28),
            QPointF(taille * 0.3, taille * 0.34),
            QPointF(-taille * 0.3, taille * 0.34),
        ])
        peintre.drawPolygon(corps)

        peintre.setBrush(QColor("#FF7A18"))
        couvercle = QRectF(-taille * 0.42, -taille * 0.4, taille * 0.84, taille * 0.14)
        peintre.drawRoundedRect(couvercle, taille * 0.04, taille * 0.04)

        peintre.setPen(QPen(QColor("#E5E5E5"), taille * 0.05))
        peintre.drawArc(
            QRectF(-taille * 0.26, -taille * 0.62, taille * 0.52, taille * 0.5),
            20 * 16, 140 * 16,
        )
        peintre.restore()
