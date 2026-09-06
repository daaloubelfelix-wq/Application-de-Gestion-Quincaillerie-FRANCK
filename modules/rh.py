"""
Ressources humaines — réservé au responsable.
Fiche employé (nom, poste, salaire), absences/congés, avances sur
salaire. Le paiement du salaire lui-même est une dépense normale (voir
modules/comptabilite.py::saisir_transaction), simplement rattachée à
l'employé pour la traçabilité.
"""

from database import Database


TYPES_CONTRAT = [("permanent", "Permanent"), ("temporaire", "Temporaire")]


def lister_employes(actifs_seulement=False):
    condition = "WHERE e.actif = TRUE" if actifs_seulement else ""
    return Database.fetch_all(
        f"""
        SELECT e.id, e.nom_complet, e.poste, e.telephone, e.type_contrat, e.salaire_mensuel,
               e.date_embauche, e.actif, e.site_id, s.nom AS site_nom
        FROM employes e
        LEFT JOIN sites s ON s.id = e.site_id
        {condition}
        ORDER BY e.nom_complet
        """
    )


def creer_employe(nom_complet, poste, telephone, type_contrat, salaire_mensuel, site_id, date_embauche):
    if not nom_complet.strip():
        raise ValueError("Le nom de l'employé est obligatoire.")
    if type_contrat not in ("permanent", "temporaire"):
        raise ValueError("Type de contrat invalide.")
    if salaire_mensuel < 0:
        raise ValueError("Le salaire ne peut pas être négatif.")

    employe = Database.fetch_one(
        """
        INSERT INTO employes (nom_complet, poste, telephone, type_contrat, salaire_mensuel, site_id, date_embauche)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (nom_complet.strip(), poste or None, telephone or None, type_contrat,
         salaire_mensuel, site_id, date_embauche),
    )
    return employe["id"]


def modifier_employe(employe_id, nom_complet, poste, telephone, type_contrat, salaire_mensuel, site_id, date_embauche):
    if not nom_complet.strip():
        raise ValueError("Le nom de l'employé est obligatoire.")
    if type_contrat not in ("permanent", "temporaire"):
        raise ValueError("Type de contrat invalide.")
    if salaire_mensuel < 0:
        raise ValueError("Le salaire ne peut pas être négatif.")

    Database.execute(
        """
        UPDATE employes
        SET nom_complet = %s, poste = %s, telephone = %s, type_contrat = %s,
            salaire_mensuel = %s, site_id = %s, date_embauche = %s
        WHERE id = %s
        """,
        (nom_complet.strip(), poste or None, telephone or None, type_contrat,
         salaire_mensuel, site_id, date_embauche, employe_id),
    )


def activer_desactiver_employe(employe_id, actif):
    Database.execute("UPDATE employes SET actif = %s WHERE id = %s", (actif, employe_id))


def enregistrer_absence_conge(employe_id, type_evenement, date_debut, date_fin, motif, utilisateur_id):
    if type_evenement not in ("absence", "conge"):
        raise ValueError("Type invalide (absence ou congé).")
    if date_fin < date_debut:
        raise ValueError("La date de fin ne peut pas être avant la date de début.")

    Database.execute(
        """
        INSERT INTO absences_conges (employe_id, type, date_debut, date_fin, motif, utilisateur_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (employe_id, type_evenement, date_debut, date_fin, motif or None, utilisateur_id),
    )


def lister_absences_conges(employe_id=None, limite=50):
    condition = "WHERE ac.employe_id = %s" if employe_id is not None else ""
    params = [employe_id] if employe_id is not None else []
    params.append(limite)
    return Database.fetch_all(
        f"""
        SELECT ac.id, ac.type, ac.date_debut, ac.date_fin, ac.motif, ac.date_creation,
               e.nom_complet AS employe_nom, u.nom_complet AS enregistre_par
        FROM absences_conges ac
        JOIN employes e ON e.id = ac.employe_id
        JOIN utilisateurs u ON u.id = ac.utilisateur_id
        {condition}
        ORDER BY ac.date_debut DESC
        LIMIT %s
        """,
        params,
    )


def enregistrer_avance(employe_id, montant, motif, utilisateur_id):
    if montant <= 0:
        raise ValueError("Le montant de l'avance doit être supérieur à 0.")

    Database.execute(
        """
        INSERT INTO avances_salaire (employe_id, montant, motif, utilisateur_id)
        VALUES (%s, %s, %s, %s)
        """,
        (employe_id, montant, motif or None, utilisateur_id),
    )


def lister_avances(employe_id=None, limite=50):
    condition = "WHERE av.employe_id = %s" if employe_id is not None else ""
    params = [employe_id] if employe_id is not None else []
    params.append(limite)
    return Database.fetch_all(
        f"""
        SELECT av.id, av.montant, av.motif, av.remboursee, av.date_avance,
               e.nom_complet AS employe_nom
        FROM avances_salaire av
        JOIN employes e ON e.id = av.employe_id
        {condition}
        ORDER BY av.date_avance DESC
        LIMIT %s
        """,
        params,
    )


def marquer_avance_remboursee(avance_id):
    Database.execute("UPDATE avances_salaire SET remboursee = TRUE WHERE id = %s", (avance_id,))


def solde_avances_non_remboursees(employe_id):
    resultat = Database.fetch_one(
        "SELECT COALESCE(SUM(montant), 0) AS total FROM avances_salaire WHERE employe_id = %s AND remboursee = FALSE",
        (employe_id,),
    )
    return float(resultat["total"])
