from unittest.mock import MagicMock

# Neutralisation totale de la base de données
import dao.db_connection
import pytest
from business_object.niveau_habilitation import NiveauHabilitation
from business_object.utilisateur import Utilisateur
from dao.utilisateur_dao import UtilisateurDao
from service.utilisateur_service import UtilisateurService

dao.db_connection.DBConnection = MagicMock()


def test_creer_compte_succes():
    # GIVEN
    pseudo = "john_doe"
    mdp = "password123"
    utilisateur_cree = Utilisateur(1, pseudo, mdp, NiveauHabilitation.CLIENT)
    # Le pseudo n'existe pas encore
    UtilisateurDao.recherche_par_pseudo = MagicMock(return_value=None)
    UtilisateurDao.create = MagicMock(return_value=True)
    # On recharge l'utilisateur après insertion
    UtilisateurDao.recherche_utilisateur = MagicMock(return_value=utilisateur_cree)

    # WHEN
    service = UtilisateurService()
    resultat = service.creer_compte(pseudo, mdp)

    # THEN
    assert resultat == utilisateur_cree
    UtilisateurDao.create.assert_called_once()


def test_creer_compte_pseudo_vide():
    # GIVEN / WHEN / THEN
    service = UtilisateurService()
    with pytest.raises(ValueError) as exc_info:
        service.creer_compte("", "password123")
    assert str(exc_info.value) == "Le pseudo ne peut pas être vide."


def test_creer_compte_mdp_trop_court():
    # GIVEN / WHEN / THEN
    service = UtilisateurService()
    with pytest.raises(ValueError) as exc_info:
        service.creer_compte("john_doe", "court")
    assert str(exc_info.value) == "Le mot de passe doit contenir au moins 8 caractères."


def test_creer_compte_pseudo_deja_utilise():
    # GIVEN
    utilisateur_existant = Utilisateur(1, "john_doe", "hashed_pwd", NiveauHabilitation.CLIENT)
    # Le DAO renvoie un utilisateur existant
    UtilisateurDao.recherche_par_pseudo = MagicMock(return_value=utilisateur_existant)

    # WHEN / THEN
    service = UtilisateurService()
    with pytest.raises(ValueError) as exc_info:
        service.creer_compte("john_doe", "password123")
    assert str(exc_info.value) == "Ce pseudo est déjà utilisé."


def test_connexion_succes():
    # GIVEN
    utilisateur = MagicMock(spec=Utilisateur)
    utilisateur.verifier_mdp.return_value = True
    UtilisateurDao.recherche_par_pseudo = MagicMock(return_value=utilisateur)

    # WHEN
    service = UtilisateurService()
    resultat = service.connexion("john_doe", "password123")

    # THEN
    assert resultat == utilisateur
    utilisateur.verifier_mdp.assert_called_once_with("password123")


def test_connexion_utilisateur_inconnu():
    # GIVEN
    UtilisateurDao.recherche_par_pseudo = MagicMock(return_value=None)

    # WHEN
    service = UtilisateurService()
    resultat = service.connexion("inconnu", "password123")

    # THEN
    assert resultat is None


def test_connexion_mdp_incorrect():
    # GIVEN
    utilisateur = MagicMock(spec=Utilisateur)
    utilisateur.verifier_mdp.return_value = False
    UtilisateurDao.recherche_par_pseudo = MagicMock(return_value=utilisateur)

    # WHEN
    service = UtilisateurService()
    resultat = service.connexion("john_doe", "mauvais_mdp")

    # THEN
    assert resultat is None


def test_rechercher_utilisateur_succes():
    # GIVEN
    utilisateur = Utilisateur(1, "john_doe", "hashed_pwd", NiveauHabilitation.CLIENT)
    UtilisateurDao.recherche_utilisateur = MagicMock(return_value=utilisateur)

    # WHEN
    service = UtilisateurService()
    resultat = service.rechercher_utilisateur(1)

    # THEN
    assert resultat == utilisateur
    UtilisateurDao.recherche_utilisateur.assert_called_once_with(1)


def test_modifier_habilitation_succes():
    # GIVEN
    admin = Utilisateur(1, "admin_user", "hashed_pwd", NiveauHabilitation.ADMIN)
    admin_bdd = Utilisateur(1, "admin_user", "hashed_pwd", NiveauHabilitation.ADMIN)
    UtilisateurDao.recherche_utilisateur = MagicMock(return_value=admin_bdd)
    UtilisateurDao.update = MagicMock(return_value=True)

    # WHEN
    service = UtilisateurService()
    resultat = service.modifier_habilitation(admin, 2, NiveauHabilitation.ADMIN)

    # THEN
    assert resultat is True
    UtilisateurDao.update.assert_called_once_with(2, NiveauHabilitation.ADMIN)


def test_modifier_habilitation_non_admin():
    # GIVEN
    client = Utilisateur(2, "client_user", "hashed_pwd", NiveauHabilitation.CLIENT)
    client_bdd = Utilisateur(2, "client_user", "hashed_pwd", NiveauHabilitation.CLIENT)
    UtilisateurDao.recherche_utilisateur = MagicMock(return_value=client_bdd)

    # WHEN / THEN
    service = UtilisateurService()
    with pytest.raises(PermissionError) as exc_info:
        service.modifier_habilitation(client, 3, NiveauHabilitation.ADMIN)
    assert str(exc_info.value) == "Seul un administrateur peut modifier les habilitations."
