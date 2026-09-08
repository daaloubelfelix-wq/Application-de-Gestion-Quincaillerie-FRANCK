"""
Modes de paiement acceptés à l'encaissement.
Liste volontairement centralisée pour que l'écran de caisse et les
rapports affichent toujours les mêmes libellés.
"""

MODES_PAIEMENT = [
    ("especes", "Espèces"),
    ("orange_money", "Orange Money"),
    ("mtn_momo", "MTN Mobile Money"),
    ("credit_client", "Crédit client"),
    ("autre", "Autre"),
]

LIBELLES_MODES_PAIEMENT = dict(MODES_PAIEMENT)


def libelle_mode_paiement(code):
    return LIBELLES_MODES_PAIEMENT.get(code, code or "—")
