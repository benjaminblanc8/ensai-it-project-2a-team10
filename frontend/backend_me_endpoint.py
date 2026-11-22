# À ajouter dans utilisateur_controller.py (backend), à côté des autres routes.
# Le frontend l'appelle après la connexion pour connaître le pseudo et le rôle.
# Déclare-la AVANT toute route GET dynamique du même routeur (il n'y en a pas ici).

@router.get("/me", tags=["Utilisateurs"])
def moi(
    utilisateur=Depends(require_niveau(NiveauHabilitation.CLIENT)),  # noqa: B008
):
    """Retourne les informations de l'utilisateur connecté."""
    habilitation = getattr(utilisateur, "habilitation", None)
    return {
        "id_utilisateur": utilisateur.id_utilisateur,
        "pseudo": utilisateur.pseudo,
        # adapte "habilitation" au nom réel de l'attribut dans ton business object
        "niveau": getattr(habilitation, "name", str(habilitation)),
    }
