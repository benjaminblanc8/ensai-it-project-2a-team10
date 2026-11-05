from business_object.niveau_habilitation import NiveauHabilitation
from fastapi import APIRouter, Depends, HTTPException
from schema.ligne_model import (
    LigneModel,
    LigneReadModel,
    LigneReadUpdateModel,
    LigneUpdateModel,
)
from service.gare_service import GareService
from service.ligne_service import LigneService
from utils.log_utils import get_logger
from utils.verification_habilitation import require_niveau

router = APIRouter()

logger = get_logger(__name__)


def get_ligne_service():
    """Injecte la dépendance au service ligne."""
    return LigneService()


def get_gare_service():
    """Injecte la dépendance au service gare."""
    return GareService()


@router.post("/", response_model=LigneReadModel, tags=["Lignes"])
def creer_ligne(
    informations: LigneModel,
    utilisateur=Depends(require_niveau(NiveauHabilitation.COLLAB)),  # noqa: B008
    ligne_service=Depends(get_ligne_service),  # noqa: B008
):
    """Crée une ligne à partir des noms des deux gares."""
    gares = []

    for nom in (
        informations.nom_gare_depart,
        informations.nom_gare_arrivee,
    ):
        nom_normalise = nom.strip().casefold()

        if not nom_normalise:
            raise HTTPException(
                status_code=422,
                detail="Le nom de gare est vide.",
            )

        resultats = ligne_service.gare_service.recherche_gare_par_nom(
            nom.strip()
        )

        correspondances = [
            gare
            for gare in resultats
            if gare.nom.strip().casefold() == nom_normalise
        ]

        if not correspondances:
            raise HTTPException(
                status_code=404,
                detail=f"La gare « {nom} » est introuvable en base.",
            )

        if len(correspondances) > 1:
            raise HTTPException(
                status_code=409,
                detail=f"Plusieurs gares portent le nom « {nom} ».",
            )

        gares.append(correspondances[0])

    return ligne_service.creer(gares[0], gares[1])

    
@router.get("/{id_ligne}", response_model=LigneReadModel, tags=["Lignes"])
def rechercher_ligne(
    id_ligne: int,
    service=Depends(get_ligne_service),  # noqa: B008
):
    """Recherche une ligne par son identifiant."""

    logger.info("Recherche d'une ligne")

    ligne = service.rechercher_ligne(id_ligne)

    if not ligne:
        raise HTTPException(status_code=404, detail="Ligne introuvable")

    return ligne

@router.put("/{id_ligne}", response_model=LigneReadUpdateModel, tags=["Lignes"])
def modifier_ligne(
    informations: LigneUpdateModel,
    utilisateur=Depends(require_niveau(NiveauHabilitation.COLLAB)),  # ruff: ignore[function-call-in-default-argument]
    service=Depends(get_ligne_service),  # ruff: ignore[function-call-in-default-argument]
):
    """ Modifie une ligne """

    logger.info("Modification d'une ligne")

    gare_depart = service.gare_service.recherche_gare(informations.id_gare_depart)

    gare_arrivee = service.gare_service.recherche_gare(
        informations.id_gare_arrivee
    )

    return service.modifier_ligne(informations.id_ligne, gare_depart, gare_arrivee)


@router.delete("/{id_ligne}", tags=["Lignes"])
def supprimer_ligne(
    id_ligne: int,
    utilisateur=Depends(require_niveau(NiveauHabilitation.COLLAB)),  # ruff: ignore[function-call-in-default-argument]
    service=Depends(get_ligne_service),  # ruff: ignore[function-call-in-default-argument]
):
    """Supprime une ligne."""

    logger.info("Suppression d'une ligne")

    ligne = service.rechercher_ligne(id_ligne)

    if not ligne:
        raise HTTPException(status_code=404, detail="Ligne introuvable")

    try:
        suppression_effectuee = service.supprimer_ligne(id_ligne)

        if not suppression_effectuee:
            raise HTTPException(
                status_code=500,
                detail="La suppression de la ligne a échoué.",
            )

        return {"message": "La ligne a été supprimée avec succès."}

    except PermissionError as erreur:
        raise HTTPException(
            status_code=409,
            detail=str(erreur),
        ) from erreur