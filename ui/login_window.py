"""
Écran d'accueil et de connexion.
Présentation façon page d'accueil : en-tête avec le nom de la boutique,
un grand titre d'accroche avec le formulaire de connexion intégré, une
illustration des outils en vitrine, des cartes de fonctionnalités et un
pied de page avec les coordonnées de contact. Le rôle et le site sont
déterminés automatiquement en base de données à partir de l'identifiant.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QFrame, QScrollArea
)

from modules.auth import authentifier
from ui.icones import icone_oeil
from ui.illustration_outils import IllustrationOutils
from ui.pictogrammes import pictogramme_stock, pictogramme_ventes, pictogramme_rapports

_COULEUR_OEIL = "#C7D3DD"


class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setWindowTitle("Ets Quincaillerie Franck — Connexion")
        self.resize(1080, 780)
        self.setMinimumSize(860, 600)
        self._construire_interface()

    def _construire_interface(self):
        layout_fenetre = QVBoxLayout()
        layout_fenetre.setContentsMargins(0, 0, 0, 0)
        layout_fenetre.setSpacing(0)

        zone_defilement = QScrollArea()
        zone_defilement.setWidgetResizable(True)
        zone_defilement.setFrameShape(QFrame.Shape.NoFrame)
        zone_defilement.setObjectName("defilementAccueil")

        contenu = QWidget()
        contenu.setObjectName("ecranAccueil")
        layout_contenu = QVBoxLayout()
        layout_contenu.setContentsMargins(0, 0, 0, 0)
        layout_contenu.setSpacing(0)

        layout_contenu.addWidget(self._construire_entete())
        layout_contenu.addWidget(self._construire_hero())
        layout_contenu.addWidget(self._construire_fonctionnalites())
        layout_contenu.addWidget(self._construire_pied_de_page())

        contenu.setLayout(layout_contenu)
        zone_defilement.setWidget(contenu)

        layout_fenetre.addWidget(zone_defilement)
        self.setLayout(layout_fenetre)

    def _construire_entete(self):
        entete = QWidget()
        entete.setObjectName("enteteAccueil")
        layout = QHBoxLayout()
        layout.setContentsMargins(40, 22, 40, 22)

        colonne_logo = QVBoxLayout()
        colonne_logo.setSpacing(0)
        logo = QLabel("🔨 Ets Quincaillerie Franck")
        logo.setObjectName("logoAccueil")
        slogan = QLabel("Quincaillerie générale — Batouri")
        slogan.setObjectName("sloganAccueil")
        colonne_logo.addWidget(logo)
        colonne_logo.addWidget(slogan)

        layout.addLayout(colonne_logo)
        layout.addStretch()

        entete.setLayout(layout)
        return entete

    def _construire_hero(self):
        hero = QWidget()
        hero.setObjectName("heroAccueil")
        layout = QHBoxLayout()
        layout.setContentsMargins(40, 10, 40, 34)
        layout.setSpacing(36)

        colonne_texte = QVBoxLayout()
        colonne_texte.setSpacing(14)

        titre = QLabel("La gestion de votre quincaillerie, simplifiée")
        titre.setObjectName("titreHero")
        titre.setWordWrap(True)

        sous_titre = QLabel(
            "Stock, commandes, caisse et rapports réunis dans une seule application, "
            "conçue pour Ets Quincaillerie Franck."
        )
        sous_titre.setObjectName("sousTitreHero")
        sous_titre.setWordWrap(True)

        colonne_texte.addWidget(titre)
        colonne_texte.addWidget(sous_titre)
        colonne_texte.addSpacing(8)
        colonne_texte.addWidget(self._construire_carte_connexion())
        colonne_texte.addStretch()

        conteneur_texte = QWidget()
        conteneur_texte.setObjectName("colonneTexteHero")
        conteneur_texte.setLayout(colonne_texte)

        illustration = IllustrationOutils(rayon_coins=18, afficher_titre=False)
        illustration.setMinimumSize(320, 320)

        cadre_photo = QFrame()
        cadre_photo.setObjectName("cadrePhoto")
        layout_photo = QVBoxLayout()
        layout_photo.setContentsMargins(0, 0, 0, 0)
        layout_photo.addWidget(illustration)
        cadre_photo.setLayout(layout_photo)

        layout.addWidget(conteneur_texte, stretch=3)
        layout.addWidget(cadre_photo, stretch=2)

        hero.setLayout(layout)
        return hero

    def _construire_carte_connexion(self):
        carte = QFrame()
        carte.setObjectName("carteConnexionHero")
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(10)

        invite = QLabel("Connexion")
        invite.setObjectName("titreCarteConnexion")

        self.champ_identifiant = QLineEdit()
        self.champ_identifiant.setPlaceholderText("Identifiant")

        ligne_mot_de_passe = QHBoxLayout()
        ligne_mot_de_passe.setSpacing(6)
        self.champ_mot_de_passe = QLineEdit()
        self.champ_mot_de_passe.setPlaceholderText("Mot de passe")
        self.champ_mot_de_passe.setEchoMode(QLineEdit.EchoMode.Password)
        self.champ_mot_de_passe.returnPressed.connect(self._tenter_connexion)

        self.bouton_oeil = QPushButton()
        self.bouton_oeil.setObjectName("boutonOeilHero")
        self.bouton_oeil.setCheckable(True)
        self.bouton_oeil.setIcon(icone_oeil(ouvert=False, couleur=_COULEUR_OEIL))
        self.bouton_oeil.setToolTip("Afficher le mot de passe")
        self.bouton_oeil.setFixedWidth(36)
        self.bouton_oeil.clicked.connect(self._basculer_visibilite_mot_de_passe)

        ligne_mot_de_passe.addWidget(self.champ_mot_de_passe)
        ligne_mot_de_passe.addWidget(self.bouton_oeil)

        bouton_connexion = QPushButton("Se connecter")
        bouton_connexion.setObjectName("boutonConnexionHero")
        bouton_connexion.clicked.connect(self._tenter_connexion)

        self.label_erreur = QLabel("")
        self.label_erreur.setObjectName("texteErreurHero")
        self.label_erreur.setWordWrap(True)

        aide = QLabel("Mot de passe oublié ? Contactez le responsable.")
        aide.setObjectName("texteAideHero")

        layout.addWidget(invite)
        layout.addWidget(self.champ_identifiant)
        layout.addLayout(ligne_mot_de_passe)
        layout.addSpacing(2)
        layout.addWidget(bouton_connexion)
        layout.addWidget(self.label_erreur)
        layout.addWidget(aide)

        carte.setLayout(layout)
        return carte

    def _construire_fonctionnalites(self):
        section = QWidget()
        section.setObjectName("sectionFonctionnalites")
        layout = QHBoxLayout()
        layout.setContentsMargins(40, 10, 40, 34)
        layout.setSpacing(20)

        cartes = [
            (pictogramme_stock(), "Gestion des stocks",
             "Suivez vos articles, vos quantités et vos seuils d'alerte en temps réel."),
            (pictogramme_ventes(), "Commandes & Caisse",
             "La comptabilité enregistre la commande, le responsable encaisse à la caisse."),
            (pictogramme_rapports(), "Rapports & Statistiques",
             "Visualisez vos ventes, vos recettes et vos produits les plus vendus."),
        ]

        for icone, titre_carte, description in cartes:
            layout.addWidget(self._construire_carte_fonctionnalite(icone, titre_carte, description))

        section.setLayout(layout)
        return section

    def _construire_carte_fonctionnalite(self, icone, titre_carte, description):
        carte = QFrame()
        carte.setObjectName("carteFonctionnalite")
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(8)

        pastille_icone = QLabel()
        pastille_icone.setPixmap(icone.pixmap(30, 30))

        titre = QLabel(titre_carte)
        titre.setObjectName("titreCarteFonctionnalite")
        titre.setWordWrap(True)

        texte = QLabel(description)
        texte.setObjectName("texteCarteFonctionnalite")
        texte.setWordWrap(True)

        layout.addWidget(pastille_icone)
        layout.addWidget(titre)
        layout.addWidget(texte)
        carte.setLayout(layout)
        return carte

    def _construire_pied_de_page(self):
        pied = QFrame()
        pied.setObjectName("piedAccueil")
        layout = QHBoxLayout()
        layout.setContentsMargins(40, 18, 40, 18)

        adresse = QLabel("Ets Quincaillerie Franck — Batouri, Région de l'Est, Cameroun")
        adresse.setObjectName("texteFooterAccueil")

        contact = QLabel("Contact : 699 861217 / 654 226348")
        contact.setObjectName("contactAccueil")

        layout.addWidget(adresse)
        layout.addStretch()
        layout.addWidget(contact)

        pied.setLayout(layout)
        return pied

    def _basculer_visibilite_mot_de_passe(self):
        visible = self.bouton_oeil.isChecked()
        self.champ_mot_de_passe.setEchoMode(
            QLineEdit.EchoMode.Normal if visible else QLineEdit.EchoMode.Password
        )
        self.bouton_oeil.setIcon(icone_oeil(ouvert=visible, couleur=_COULEUR_OEIL))
        self.bouton_oeil.setToolTip("Masquer le mot de passe" if visible else "Afficher le mot de passe")

    def _tenter_connexion(self):
        identifiant = self.champ_identifiant.text().strip()
        mot_de_passe = self.champ_mot_de_passe.text()

        if not identifiant or not mot_de_passe:
            self.label_erreur.setText("Veuillez remplir l'identifiant et le mot de passe.")
            return

        try:
            utilisateur = authentifier(identifiant, mot_de_passe)
        except ConnectionError as erreur:
            QMessageBox.critical(self, "Connexion au serveur impossible", str(erreur))
            return
        except ValueError as erreur:
            self.label_erreur.setText(str(erreur))
            self.champ_mot_de_passe.clear()
            return

        self.label_erreur.setText("")
        self.on_login_success(utilisateur)
