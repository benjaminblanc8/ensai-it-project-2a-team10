from fastapi import APIRouter, Depends, HTTPException

from business_object.utilisateur import Utilisateur
from dao.reservation_dao import ReservationDao
from dao.trajet_dao import TrajetDao
from utils.authentication import get_current_user
from utils.verification_habilitation import require_niveau
from schema.utilisateur_model import NiveauHabilitation
from schema.reservation_model import (
    ReservationUtilisateurReadModel,
    ReservationTrajetReadModel,
    ReservationResponseModel,
    ReservationCreateModel,
    ReservationReadModel
)
from service.reservation_service import ReservationService
from utils.log_utils import get_logger

router = APIRouter()
logger = get_logger(__name__)


def get_reservation_service():
    """Injecte les DAO dans le service réservation."""

    return ReservationService(
        ReservationDao(),
        TrajetDao(),
    )


@router.post("/", response_model=ReservationResponseModel, tags=["Réservations"])
def creer_reservation(
    informations: ReservationCreateModel,
    utilisateur=Depends(require_niveau(NiveauHabilitation.CLIENT)),
    service=Depends(get_reservation_service),
):
    try:
        reservation = service.creer_reservation(
            utilisateur,
            informations.id_trajet,
        )

        return ReservationResponseModel(
            message="Réservation effectuée avec succès.",
            id_reservation=reservation.id_reservation,
        )

    except LookupError as erreur:
        raise HTTPException(status_code=404, detail=str(erreur)) from erreur

    except ValueError as erreur:
        raise HTTPException(status_code=409, detail=str(erreur)) from erreur


@router.get(
    "/mes-reservations",
    response_model=list[ReservationReadModel],
    tags=["Réservations"],
)
def rechercher_mes_reservations(
    utilisateur=Depends(require_niveau(NiveauHabilitation.CLIENT)),
    service=Depends(get_reservation_service),
):
    logger.info(
    "Utilisateur connecté : %s", utilisateur.id_utilisateur,
    )

    reservations = service.rechercher_reservations(utilisateur)

    for reservation in reservations:
        print("Utilisateur :", vars(reservation.utilisateur))
        print("Trajet :", vars(reservation.trajet))

        print(
            "Utilisateur converti :",
            ReservationUtilisateurReadModel.model_validate(
                reservation.utilisateur
            )
        )

        print(
            "Trajet converti :",
            ReservationTrajetReadModel.model_validate(
                reservation.trajet
            )
        )

    return reservations


@router.delete(
    "/{id_reservation}",
    response_model=ReservationResponseModel,
    tags=["Réservations"],
)
def annuler_reservation(
    id_reservation: int,
    utilisateur=Depends(require_niveau(NiveauHabilitation.CLIENT)),
    service=Depends(get_reservation_service),
):
    try:
        service.annuler_reservation(utilisateur, id_reservation)

        return ReservationResponseModel(
            message="Réservation annulée avec succès.",
            id_reservation=id_reservation,
        )

    except LookupError as erreur:
        raise HTTPException(status_code=404, detail=str(erreur)) from erreur

    except PermissionError as erreur:
        raise HTTPException(status_code=403, detail=str(erreur)) from erreur