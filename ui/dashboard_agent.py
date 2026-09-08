"""
Tableau de bord affiché aux agents (stock ou comptabilité).
Vue restreinte à leur site et leur module, conformément à la maquette validée.
Le contenu (statistiques, alertes, actions rapides) dépend du rôle exact :
un agent comptabilité n'a pas de raison de voir des actions de stock, et
inversement.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt

from database import Database
from modules.comptabilite import totaux_du_jour
from modules.inventaire import statut_inventaire_jour


class TableauBordAgent(QWidget):
    def __init__(self, utilisateur):
        super().__init__()
        self.utilisateur = utilisateur
        self._construire_interface()

    def _construire_interface(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # En-tête
        entete = QHBoxLayout()
        infos = QVBoxLayout()
        nom = QLabel(f"Bonjour, {self.utilisateur['nom_complet']}")
        nom.setStyleSheet("font-size: 16px; font-weight: bold;")
        site_role = QLabel(
            f"{self.utilisateur['site_nom']} · "
            f"{'Agent stock' if self.utilisateur['role'] == 'agent_stock' else 'Agent comptabilité'}"
        )
        site_role.setStyleSheet("color: #6B6357; font-size: 12px;")
        infos.addWidget(nom)
        infos.addWidget(site_role)
        entete.addLayout(infos)
        entete.addStretch()
        layout.addLayout(entete)

        # Zone reconstruite à chaque rafraîchissement (après ajout d'article
        # ou mouvement de stock), comme dans TableauBordResponsable.
        self.zone_contenu = QVBoxLayout()
        layout.addLayout(self.zone_contenu)

        if self.utilisateur["role"] == "agent_stock":
            self._rafraichir_stock()
        else:
            self._rafraichir_comptabilite()

        layout.addStretch()
        self.setLayout(layout)

    def _vider_zone_contenu(self):
        while self.zone_contenu.count():
            item = self.zone_contenu.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._vider_layout(item.layout())

    def _vider_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    # ------------------------------------------------------------
    # Contenu spécifique : agent stock
    # ------------------------------------------------------------
    def _rafraichir_stock(self):
        self._vider_zone_contenu()

        cartes = QHBoxLayout()
        cartes.addWidget(self._carte_stat("Articles en stock", self._compter_articles()))
        cartes.addWidget(self._carte_stat("Seuils atteints", self._compter_alertes(), alerte=True))
        self.zone_contenu.addLayout(cartes)

        titre_inventaire = QLabel("Comptage d'inventaire du jour")
        titre_inventaire.setStyleSheet("font-size: 13px; font-weight: bold;")
        self.zone_contenu.addWidget(titre_inventaire)
        self.zone_contenu.addWidget(self._construire_statut_inventaire())

        titre_alertes = QLabel("Alertes stock faible")
        titre_alertes.setStyleSheet("font-size: 13px; font-weight: bold;")
        self.zone_contenu.addWidget(titre_alertes)

        self.zone_contenu.addWidget(self._construire_liste_alertes())

        actions = QHBoxLayout()
        bouton_ajout = QPushButton("Ajouter article")
        bouton_ajout.clicked.connect(self._ouvrir_formulaire_ajout_article)
        bouton_mouvement = QPushButton("Mouvement stock")
        bouton_mouvement.clicked.connect(self._ouvrir_formulaire_mouvement_stock)
        bouton_comptage = QPushButton("Faire le comptage")
        bouton_comptage.clicked.connect(self._ouvrir_comptage)
        actions.addWidget(bouton_ajout)
        actions.addWidget(bouton_mouvement)
        actions.addWidget(bouton_comptage)
        self.zone_contenu.addLayout(actions)

    def _construire_statut_inventaire(self):
        statut = statut_inventaire_jour(self.utilisateur["site_id"])
        cadre = QFrame()

        if statut["nombre_comptages"] == 0:
            cadre.setStyleSheet("background-color: #E7DFC9; border-radius: 8px; padding: 12px;")
            texte = "Pas encore comptabilisé aujourd'hui — pensez au comptage du matin et du soir."
            couleur = "#6B6357"
        elif statut["en_ordre"]:
            cadre.setStyleSheet("background-color: #DDE8DD; border-radius: 8px; padding: 12px;")
            texte = "✔ Tout est en ordre — aucun écart détecté sur le comptage du jour."
            couleur = "#3F6B46"
        else:
            cadre.setStyleSheet("background-color: #F0DDD0; border-radius: 8px; padding: 12px;")
            detail = ", ".join(
                f"{e['nom']} ({'manque ' + str(abs(e['ecart'])) if e['ecart'] < 0 else '+' + str(e['ecart'])})"
                for e in statut["ecarts"]
            )
            texte = f"✘ Écart détecté : {detail}"
            couleur = "#9C3D1F"

        vlayout = QVBoxLayout()
        label = QLabel(texte)
        label.setWordWrap(True)
        label.setStyleSheet(f"color: {couleur}; font-weight: 600;")
        vlayout.addWidget(label)
        cadre.setLayout(vlayout)
        return cadre

    def _ouvrir_comptage(self):
        from ui.comptage_stock import ComptageStock
        ComptageStock(self.utilisateur, parent=self).exec()
        self._rafraichir_stock()

    def _ouvrir_formulaire_ajout_article(self):
        from ui.formulaire_article import FormulaireArticle
        dialogue = FormulaireArticle(self.utilisateur, article=None, parent=self)
        if dialogue.exec():
            self._rafraichir_stock()

    def _ouvrir_formulaire_mouvement_stock(self):
        from ui.formulaire_mouvement_stock import FormulaireMouvementStock
        dialogue = FormulaireMouvementStock(self.utilisateur, parent=self)
        if dialogue.exec():
            self._rafraichir_stock()

    # ------------------------------------------------------------
    # Contenu spécifique : agent comptabilité
    # ------------------------------------------------------------
    def _rafraichir_comptabilite(self):
        self._vider_zone_contenu()
        totaux = totaux_du_jour(self.utilisateur["site_id"])

        cartes = QHBoxLayout()
        cartes.addWidget(self._carte_stat(
            "Recettes du jour", f"{totaux['recettes']:,.0f} FCFA".replace(",", " ")
        ))
        cartes.addWidget(self._carte_stat(
            "Dépenses du jour", f"{totaux['depenses']:,.0f} FCFA".replace(",", " "), alerte=True
        ))
        self.zone_contenu.addLayout(cartes)

        info = QLabel("Pour saisir une recette ou une dépense, ouvrez l'onglet « Comptabilité ».")
        info.setStyleSheet("color: #6B6357; font-size: 12px;")
        self.zone_contenu.addWidget(info)

    # ------------------------------------------------------------
    # Composants communs
    # ------------------------------------------------------------
    def _carte_stat(self, titre, valeur, alerte=False):
        cadre = QFrame()
        cadre.setStyleSheet(
            f"background-color: {'#F2E0BE' if alerte else '#E7DFC9'}; "
            "border-radius: 8px; padding: 12px;"
        )
        vlayout = QVBoxLayout()
        label_titre = QLabel(titre)
        label_titre.setStyleSheet("font-size: 12px; color: #6B6357;")
        label_valeur = QLabel(str(valeur))
        label_valeur.setStyleSheet("font-size: 22px; font-weight: bold;")
        vlayout.addWidget(label_titre)
        vlayout.addWidget(label_valeur)
        cadre.setLayout(vlayout)
        return cadre

    def _construire_liste_alertes(self):
        cadre = QFrame()
        cadre.setStyleSheet("border: 1px solid #D8CFB7; border-radius: 8px;")
        vlayout = QVBoxLayout()
        vlayout.setSpacing(0)

        articles_alerte = Database.fetch_all(
            """
            SELECT nom, quantite_stock
            FROM articles
            WHERE site_id = %s AND quantite_stock <= seuil_alerte
            ORDER BY quantite_stock ASC
            """,
            (self.utilisateur["site_id"],),
        )

        if not articles_alerte:
            label_vide = QLabel("Aucune alerte de stock pour le moment.")
            label_vide.setStyleSheet("padding: 10px; color: #6B6357; font-size: 13px;")
            vlayout.addWidget(label_vide)
        else:
            for article in articles_alerte:
                ligne = QHBoxLayout()
                ligne.addWidget(QLabel(article["nom"]))
                quantite_label = QLabel(f"{article['quantite_stock']} restants")
                quantite_label.setStyleSheet("color: #9C3D1F;")
                quantite_label.setAlignment(Qt.AlignmentFlag.AlignRight)
                ligne.addWidget(quantite_label)
                conteneur_ligne = QWidget()
                conteneur_ligne.setLayout(ligne)
                conteneur_ligne.setStyleSheet("padding: 8px;")
                vlayout.addWidget(conteneur_ligne)

        cadre.setLayout(vlayout)
        return cadre

    def _compter_articles(self):
        resultat = Database.fetch_one(
            "SELECT COUNT(*) AS total FROM articles WHERE site_id = %s",
            (self.utilisateur["site_id"],),
        )
        return resultat["total"] if resultat else 0

    def _compter_alertes(self):
        resultat = Database.fetch_one(
            "SELECT COUNT(*) AS total FROM articles WHERE site_id = %s AND quantite_stock <= seuil_alerte",
            (self.utilisateur["site_id"],),
        )
        return resultat["total"] if resultat else 0
