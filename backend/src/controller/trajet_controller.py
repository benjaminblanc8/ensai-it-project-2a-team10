
from fastapi import APIRouter, Depends, HTTPException
from schema.trajet_model import TrajetModel, TrajetReadModel
from service.ligne_service import LigneService
from service.trajet_service import TrajetService
from utils.log_utils import get_logger

router = APIRouter()
logger = get_logger(__name__)


def get_trajet_service():
    return TrajetService()


def get_ligne_service():
    return LigneService()


def convertir_trajet(trajet) -> TrajetReadModel:
    """Convertit un objet Trajet en modèle de réponse."""
    places_reservees = trajet.get_places_reservees()

    return TrajetReadModel(
        id_trajet=trajet.id_trajet,
        id_ligne=trajet.ligne.id_ligne,
        date_heure_depart=trajet.date_heure_depart,
        duree_minutes=trajet.duree_minutes,
        nb_places=trajet.get_nb_places_disponibles() + places_reservees,
        tarif=trajet.get_tarif(),
        places_reservees=places_reservees,
    )


@router.get("/{id_trajet}", response_model=TrajetReadModel, tags=["Trajets"])
def recherche_trajet(
    id_trajet: int,
    service: TrajetService = Depends(get_trajet_service), # noqa: B008
):
    """Recherche un trajet par son identifiant."""
    trajet = service.recherche_trajet(id_trajet)

    if trajet is None:
        raise HTTPException(status_code=404, detail="Trajet introuvable")

    return convertir_trajet(trajet)


@router.post("/", response_model=TrajetReadModel, tags=["Trajets"])
def creer_trajet(
    informations: TrajetModel,
    service: TrajetService = Depends(get_trajet_service), # noqa: B008
    ligne_service: LigneService = Depends(get_ligne_service), # noqa: B008
):
    """Crée un trajet sur une ligne existante."""
    ligne = ligne_service.rechercher_ligne(informations.id_ligne)

    if ligne is None:
        raise HTTPException(status_code=404, detail="Ligne introuvable")

    trajet = service.creer_trajet(
        ligne=ligne,
        date_heure_depart=informations.date_heure_depart,
        duree_minutes=informations.duree_minutes,
        nb_places=informations.nb_places,
        tarif=informations.tarif,
    )

    if trajet is None:
        raise HTTPException(
            status_code=400,
            detail="Échec de la création du trajet",
        )

    logger.info("Trajet créé : %s", trajet.id_trajet)
    return convertir_trajet(trajet)


@router.put("/{id_trajet}", response_model=TrajetReadModel, tags=["Trajets"])
def modifier_trajet(
    id_trajet: int,
    informations: TrajetModel,
    service: TrajetService = Depends(get_trajet_service), # noqa: B008
    ligne_service: LigneService = Depends(get_ligne_service), # noqa: B008
):
    """Modifie un trajet existant."""
    trajet_existant = service.recherche_trajet(id_trajet)

    if trajet_existant is None:
        raise HTTPException(status_code=404, detail="Trajet introuvable")

    ligne = ligne_service.rechercher_ligne(informations.id_ligne)

    if ligne is None:
        raise HTTPException(status_code=404, detail="Ligne introuvable")

    succes = service.modifier_trajet(
        id_trajet=id_trajet,
        ligne=ligne,
        date_heure_depart=informations.date_heure_depart,
        duree_minutes=informations.duree_minutes,
        nb_places=informations.nb_places,
        tarif=informations.tarif,
        places_reservees=trajet_existant.get_places_reservees(),
    )

    if not succes:
        raise HTTPException(
            status_code=400,
            detail="Échec de la modification du trajet",
        )

    trajet = service.recherche_trajet(id_trajet)
    logger.info("Trajet modifié : %s", id_trajet)
    return convertir_trajet(trajet)


@router.delete("/{id_trajet}", tags=["Trajets"])
def supprimer_trajet(
    id_trajet: int,
    service: TrajetService = Depends(get_trajet_service), # noqa: B008
):
    """Supprime un trajet existant."""
    trajet = service.recherche_trajet(id_trajet)

    if trajet is None:
        raise HTTPException(status_code=404, detail="Trajet introuvable")

    succes = service.supprimer_trajet(id_trajet)

    if not succes:
        raise HTTPException(
            status_code=400,
            detail="Échec de la suppression du trajet",
        )

    logger.info("Trajet supprimé : %s", id_trajet)
    return {"message": "Trajet supprimé avec succès"}
