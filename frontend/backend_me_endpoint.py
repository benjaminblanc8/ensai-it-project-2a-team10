# À ajouter dans utilisateur_controller.py (backend), à côté des autres routes.
# Le frontend l'appelle après la connexion pour connaître le pseudo et le rôle.

@router.get("/me", tags=["Utilisateurs"])
def moi(
    utilisateur=Depends(require_niveau(NiveauHabilitation.CLIENT)),  # noqa: B008
):
    """Retourne les informations de l'utilisateur connecté."""
    habilitation = getattr(utilisateur, "habilitation", None)
    return {
        "id_utilisateur": utilisateur.id_utilisateur,
        "pseudo": utilisateur.pseudo,
        # adapte l'attribut "habilitation" au nom réel dans ton business object
        "niveau": getattr(habilitation, "name", str(habilitation)),
    }
