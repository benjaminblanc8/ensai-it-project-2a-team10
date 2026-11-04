from business_object.niveau_habilitation import NiveauHabilitation
from business_object.utilisateur import Utilisateur
from fastapi import Depends, HTTPException
from utils.authentication import get_current_user


def require_niveau(niveau_minimal: NiveauHabilitation):
    """
    Retourne une dépendance FastAPI qui vérifie que l'utilisateur
    connecté possède au minimum le niveau d'habilitation requis.

    Utilisation dans un contrôleur :
        @router.post("/admin/", dependencies=[Depends(require_niveau(NiveauHabilitation.ADMIN))])
        def action_admin():
            ...

    Ou en paramètre :
        def action(user: Utilisateur = Depends(require_niveau(NiveauHabilitation.COLLAB))):
            ...
    """

    def verifieur(user: Utilisateur = Depends(get_current_user)):  # ruff: ignore[function-call-in-default-argument]
        if user.get_niveau().value < niveau_minimal.value:
            raise HTTPException(
                status_code=403,
                detail=(
                    f"Niveau d'habilitation insuffisant. "
                    f"Requis : {niveau_minimal.name}, "
                    f"actuel : {user.get_niveau().name}"
                ),
            )
        return user

    return verifieur