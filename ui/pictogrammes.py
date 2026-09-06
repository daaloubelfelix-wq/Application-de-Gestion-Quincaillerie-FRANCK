"""
Petits pictogrammes dessinés (QPainter) pour les cartes de fonctionnalités
de l'écran d'accueil — aucune dépendance à une police d'icônes ou un
fichier image externe.
"""

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap


def _nouveau_pixmap(taille):
    pixmap = QPixmap(taille, taille)
    pixmap.fill(Qt.GlobalColor.transparent)
    peintre = QPainter(pixmap)
    peintre.setRenderHint(QPainter.RenderHint.Antialiasing)
    return pixmap, peintre


def pictogramme_stock(couleur="#E8A23A", taille=28) -> QIcon:
    """Boîtes empilées — gestion des stocks."""
    pixmap, peintre = _nouveau_pixmap(taille)
    peintre.setPen(QPen(QColor(couleur), taille * 0.08))
    peintre.setBrush(Qt.BrushStyle.NoBrush)
    m = taille * 0.16
    peintre.drawRoundedRect(QRectF(m, taille * 0.42, taille * 0.36, taille * 0.36), 2, 2)
    peintre.drawRoundedRect(QRectF(taille * 0.48, taille * 0.42, taille * 0.36, taille * 0.36), 2, 2)
    peintre.drawRoundedRect(QRectF(taille * 0.32, taille * 0.12, taille * 0.36, taille * 0.36), 2, 2)
    peintre.end()
    return QIcon(pixmap)


def pictogramme_ventes(couleur="#E8A23A", taille=28) -> QIcon:
    """Reçu / ticket — facturation et ventes."""
    pixmap, peintre = _nouveau_pixmap(taille)
    peintre.setPen(QPen(QColor(couleur), taille * 0.07))
    peintre.setBrush(Qt.BrushStyle.NoBrush)
    rect = QRectF(taille * 0.22, taille * 0.1, taille * 0.56, taille * 0.8)
    peintre.drawRoundedRect(rect, taille * 0.04, taille * 0.04)
    for i in range(3):
        y = taille * (0.32 + i * 0.16)
        peintre.drawLine(QPointF(taille * 0.32, y), QPointF(taille * 0.7, y))
    peintre.end()
    return QIcon(pixmap)


def pictogramme_rapports(couleur="#E8A23A", taille=28) -> QIcon:
    """Barres ascendantes — rapports et statistiques."""
    pixmap, peintre = _nouveau_pixmap(taille)
    peintre.setPen(Qt.PenStyle.NoPen)
    peintre.setBrush(QColor(couleur))
    largeurs_barres = [0.4, 0.65, 0.85]
    for i, hauteur_relative in enumerate(largeurs_barres):
        x = taille * (0.16 + i * 0.28)
        h = taille * 0.72 * hauteur_relative
        peintre.drawRoundedRect(QRectF(x, taille * 0.86 - h, taille * 0.18, h), 2, 2)
    peintre.end()
    return QIcon(pixmap)
