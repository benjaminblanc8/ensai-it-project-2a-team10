from math import ceil

from business_object.niveau_habilitation import NiveauHabilitation
from fastapi import APIRouter, Depends, HTTPException
from schema.trajet_model import TrajetCreationModel, TrajetModel, TrajetReadModel
from service.api_sncf_service import ApiSncfError, ApiSncfService
from service.ligne_service import LigneService
from service.trajet_service import TrajetService
from utils.log_utils import get_logger
from utils.verification_habilitation import require_niveau

router = APIRouter()
logger = get_logger(__name__)


def get_trajet_service():
    return TrajetService()


def get_ligne_service():
    return LigneService()


def convertir_trajet(trajet) -> TrajetReadModel:
    """Convertit un objet Trajet en modèle de réponse."""
    places_reservees = trajet.get_places_reservees

    return TrajetReadModel(
        id_trajet=trajet.id_trajet,
        id_ligne=trajet.ligne.id_ligne,
        date_heure_depart=trajet.date_heure_depart,
        duree_minutes=trajet.duree_minutes,
        nb_places=trajet.get_nb_places_disponibles + places_reservees,
        tarif=trajet.get_tarif,
        places_reservees=places_reservees,
        places_disponibles=trajet.get_nb_places_disponibles,
    )


@router.post("/", response_model=TrajetReadModel, tags=["Trajets"])
def creer_trajet(
    informations: TrajetCreationModel,
    utilisateur=Depends(require_niveau(NiveauHabilitation.COLLAB)),  # ruff: ignore[function-call-in-default-argument]
    service: TrajetService = Depends(get_trajet_service),  # noqa: B008  # ruff: ignore[fast-api-non-annotated-dependency]
    ligne_service: LigneService = Depends(get_ligne_service),  # noqa: B008  # ruff: ignore[fast-api-non-annotated-dependency]
):
    """Crée un trajet et estime sa durée à partir d'un itinéraire SNCF."""
    ligne = ligne_service.rechercher_ligne_par_gares(
        informations.nom_gare_depart,
        informations.nom_gare_arrivee,
    )

    if ligne is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Aucune ligne de « {informations.nom_gare_depart} » "
                f"vers « {informations.nom_gare_arrivee} »."
            ),
        )

    id_depart = ligne.gare_depart.id_gare_sncf
    id_arrivee = ligne.gare_arrivee.id_gare_sncf

    if not id_depart or not id_arrivee:
        raise HTTPException(
            status_code=422,
            detail="Une des gares n'a pas d'identifiant SNCF.",
        )

    try:
        itineraire = ApiSncfService().calculer_duree_trajet(
            id_depart,
            id_arrivee,
            informations.date_heure_depart,
        )
    except ApiSncfError as exc:
        logger.error("Erreur API SNCF : %s", exc)
        raise HTTPException(
            status_code=502,
            detail="Impossible de récupérer la durée auprès de l'API SNCF.",
        ) from exc

    if itineraire is None:
        raise HTTPException(
            status_code=422,
            detail="Aucun itinéraire SNCF trouvé pour ces gares à la date demandée.",
        )

    duree_minutes = ceil(itineraire["duree"].total_seconds() / 60)

    trajet = service.creer_trajet(
        ligne=ligne,
        date_heure_depart=informations.date_heure_depart,
        duree_minutes=duree_minutes,
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


@router.get("/", response_model=list[TrajetReadModel], tags=["Trajets"])
def rechercher_trajets_par_gares(
    nom_gare_depart: str,
    nom_gare_arrivee: str,
    service: TrajetService = Depends(get_trajet_service),  # noqa: B008  # ruff: ignore[fast-api-non-annotated-dependency]
    ligne_service: LigneService = Depends(get_ligne_service),  # noqa: B008  # ruff: ignore[fast-api-non-annotated-dependency]
):
    """Liste les trajets entre deux gares, dans le sens demandé."""
    ligne = ligne_service.rechercher_ligne_par_gares(
        nom_gare_depart,
        nom_gare_arrivee,
    )

    if ligne is None:
        return []

    trajets = service.rechercher_trajets_par_ligne(ligne)
    return [convertir_trajet(trajet) for trajet in trajets]


@router.get("/{id_trajet}", response_model=TrajetReadModel, tags=["Trajets"])
def recherche_trajet(
    id_trajet: int,
    service: TrajetService = Depends(get_trajet_service),  # noqa: B008  # ruff: ignore[fast-api-non-annotated-dependency]
):
    """Recherche un trajet par son identifiant."""
    trajet = service.recherche_trajet(id_trajet)

    if trajet is None:
        raise HTTPException(status_code=404, detail="Trajet introuvable")

    return convertir_trajet(trajet)


@router.put("/{id_trajet}", response_model=TrajetReadModel, tags=["Trajets"])
def modifier_trajet(
    id_trajet: int,
    informations: TrajetModel,
    utilisateur=Depends(require_niveau(NiveauHabilitation.COLLAB)),  # noqa: B008
    service: TrajetService = Depends(get_trajet_service),  # noqa: B008  # ruff: ignore[fast-api-non-annotated-dependency]
    ligne_service: LigneService = Depends(get_ligne_service),  # noqa: B008  # ruff: ignore[fast-api-non-annotated-dependency]
):
    """Modifie un trajet et recalcule sa durée si nécessaire."""
    trajet_existant = service.recherche_trajet(id_trajet)

    if trajet_existant is None:
        raise HTTPException(status_code=404, detail="Trajet introuvable")

    ligne = ligne_service.rechercher_ligne(informations.id_ligne)

    if ligne is None:
        raise HTTPException(status_code=404, detail="Ligne introuvable")

    duree_minutes = trajet_existant.duree_minutes

    if (
        informations.date_heure_depart != trajet_existant.date_heure_depart
        or ligne.id_ligne != trajet_existant.ligne.id_ligne
    ):
        id_depart = ligne.gare_depart.id_gare_sncf
        id_arrivee = ligne.gare_arrivee.id_gare_sncf

        if not id_depart or not id_arrivee:
            raise HTTPException(
                status_code=422,
                detail="Une des gares n'a pas d'identifiant SNCF.",
            )

        try:
            itineraire = ApiSncfService().calculer_duree_trajet(
                id_depart,
                id_arrivee,
                informations.date_heure_depart,
            )

        except ApiSncfError as exc:
            logger.error("Erreur API SNCF : %s", exc)
            raise HTTPException(
                status_code=502,
                detail="Impossible de récupérer la durée auprès de l'API SNCF.",
            ) from exc

        if itineraire is None:
            raise HTTPException(
                status_code=422,
                detail=(
                    "Aucun itinéraire SNCF trouvé pour ces gares "
                    "à la date demandée."
                ),
            )

        duree_minutes = ceil(itineraire["duree"].total_seconds() / 60)

    try:
        succes = service.modifier_trajet(
            id_trajet=id_trajet,
            ligne=ligne,
            date_heure_depart=informations.date_heure_depart,
            duree_minutes=duree_minutes,
            nb_places=informations.nb_places,
            tarif=informations.tarif,
            places_reservees=trajet_existant.get_places_reservees,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

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
    utilisateur=Depends(require_niveau(NiveauHabilitation.COLLAB)),  # ruff: ignore[function-call-in-default-argument]
    service: TrajetService = Depends(get_trajet_service),  # noqa: B008  # ruff: ignore[fast-api-non-annotated-dependency]
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
