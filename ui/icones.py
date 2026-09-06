"""
Petites icônes dessinées à la main (QPainter), pour ne dépendre d'aucun
fichier image ni police d'icônes externe.
"""

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QIcon, QPainter, QPen, QPixmap


def icone_boite_outils(couleur: str = "#152C4D", taille: int = 34) -> QPixmap:
    """Badge de l'écran de connexion : mallette à outils (poignée arquée,
    corps arrondi, ligne de couvercle, deux loquets) — repris du modèle
    HTML validé (voir #ecran-connexion .emblème svg)."""
    pixmap = QPixmap(taille, taille)
    pixmap.fill(Qt.GlobalColor.transparent)

    peintre = QPainter(pixmap)
    peintre.setRenderHint(QPainter.RenderHint.Antialiasing)
    s = taille / 64

    stylo = QPen(_vers_couleur(couleur), 3.2 * s)
    stylo.setCapStyle(Qt.PenCapStyle.RoundCap)
    stylo.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    peintre.setPen(stylo)
    peintre.setBrush(Qt.BrushStyle.NoBrush)

    # Poignée : deux montants reliés par un arc
    peintre.drawLine(QPointF(24 * s, 24 * s), QPointF(24 * s, 19 * s))
    peintre.drawLine(QPointF(40 * s, 24 * s), QPointF(40 * s, 19 * s))
    peintre.drawArc(QRectF(24 * s, 11 * s, 16 * s, 16 * s), 0, 180 * 16)

    # Corps de la mallette
    peintre.drawRoundedRect(QRectF(10 * s, 24 * s, 44 * s, 24 * s), 3 * s, 3 * s)
    peintre.drawLine(QPointF(10 * s, 36 * s), QPointF(54 * s, 36 * s))

    # Loquets
    peintre.setPen(Qt.PenStyle.NoPen)
    peintre.setBrush(_vers_couleur(couleur))
    peintre.drawRoundedRect(QRectF(27 * s, 32 * s, 4 * s, 8 * s), 1 * s, 1 * s)
    peintre.drawRoundedRect(QRectF(35 * s, 32 * s, 4 * s, 8 * s), 1 * s, 1 * s)

    peintre.end()
    return pixmap


def icone_oeil(ouvert: bool, couleur: str = "#6B6357", taille: int = 20) -> QIcon:
    """Œil ouvert (mot de passe visible) ou barré (mot de passe masqué)."""
    pixmap = QPixmap(taille, taille)
    pixmap.fill(Qt.GlobalColor.transparent)

    peintre = QPainter(pixmap)
    peintre.setRenderHint(QPainter.RenderHint.Antialiasing)
    stylo = QPen(Qt.GlobalColor.transparent)
    peintre.setPen(QPen(_vers_couleur(couleur), 1.6))
    peintre.setBrush(Qt.BrushStyle.NoBrush)

    marge = taille * 0.15
    rect_oeil = QRectF(marge, taille * 0.3, taille - 2 * marge, taille * 0.4)
    peintre.drawArc(rect_oeil, 0, 180 * 16)
    peintre.drawArc(rect_oeil, 180 * 16, 180 * 16)

    if ouvert:
        centre = rect_oeil.center()
        peintre.setBrush(_vers_couleur(couleur))
        peintre.drawEllipse(centre, taille * 0.09, taille * 0.09)
    else:
        peintre.drawLine(
            QPointF(marge, taille * 0.22),
            QPointF(taille - marge, taille * 0.78),
        )

    peintre.end()
    return QIcon(pixmap)


def _vers_couleur(code_hex: str):
    from PyQt6.QtGui import QColor
    return QColor(code_hex)
