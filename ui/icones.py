"""
Petites icônes dessinées à la main (QPainter), pour ne dépendre d'aucun
fichier image ni police d'icônes externe.
"""

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QIcon, QPainter, QPen, QPixmap


def icone_oeil(ouvert: bool, couleur: str = "#5B6169", taille: int = 20) -> QIcon:
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
