import os
from unittest.mock import MagicMock

import dao.db_connection
import pytest
from business_object.niveau_habilitation import NiveauHabilitation
from business_object.utilisateur import Utilisateur
from dao.utilisateur_dao import UtilisateurDao
from service.utilisateur_service import UtilisateurService

os.environ["JWT_SECRET_KEY"] = "fake_jwt_secret_key_for_tests"

dao.db_connection.DBConnection = MagicMock()


def test_creer_compte_succes():
    pseudo = "john_doe"
    mdp = "password123"
    utilisateur_cree = Utilisateur(1, pseudo, mdp, NiveauHabilitation.CLIENT)

    service = UtilisateurService()
    service.utilisateur_dao = MagicMock()
    service.utilisateur_dao.recherche_par_pseudo.return_value = None
    service.utilisateur_dao.creer.return_value = True
    service.utilisateur_dao.recherche_utilisateur.return_value = utilisateur_cree

    resultat = service.creer_compte(pseudo, mdp)

    assert resultat == utilisateur_cree
    service.utilisateur_dao.creer.assert_called_once()


def test_creer_compte_pseudo_vide():
    service = UtilisateurService()
    with pytest.raises(ValueError) as exc_info:
        service.creer_compte("", "password123")
    assert str(exc_info.value) == "Le pseudo ne peut pas être vide."


def test_creer_compte_mdp_trop_court():
    service = UtilisateurService()
    with pytest.raises(ValueError) as exc_info:
        service.creer_compte("john_doe", "court")
    assert str(exc_info.value) == "Le mot de passe doit contenir au moins 8 caractères."


def test_creer_compte_pseudo_deja_utilise():
    utilisateur_existant = Utilisateur(1, "john_doe", "hashed_pwd", NiveauHabilitation.CLIENT)
    UtilisateurDao.recherche_par_pseudo = MagicMock(return_value=utilisateur_existant)

    service = UtilisateurService()
    with pytest.raises(ValueError) as exc_info:
        service.creer_compte("john_doe", "password123")
    assert str(exc_info.value) == "Ce pseudo est déjà utilisé."


def test_connexion_succes():
    utilisateur = MagicMock(spec=Utilisateur)
    utilisateur.id_utilisateur = 1
    utilisateur.verifier_mdp.return_value = True
    UtilisateurDao.recherche_par_pseudo = MagicMock(return_value=utilisateur)

    service = UtilisateurService()
    resultat = service.connexion("john_doe", "password123")

    assert resultat is not None
    utilisateur.verifier_mdp.assert_called_once_with("password123")


def test_connexion_utilisateur_inconnu():
    UtilisateurDao.recherche_par_pseudo = MagicMock(return_value=None)

    service = UtilisateurService()
    resultat = service.connexion("inconnu", "password123")

    assert resultat is None


def test_connexion_mdp_incorrect():
    utilisateur = MagicMock(spec=Utilisateur)
    utilisateur.verifier_mdp.return_value = False
    UtilisateurDao.recherche_par_pseudo = MagicMock(return_value=utilisateur)

    service = UtilisateurService()
    resultat = service.connexion("john_doe", "mauvais_mdp")

    assert resultat is None


def test_rechercher_utilisateur_succes():
    utilisateur = Utilisateur(1, "john_doe", "hashed_pwd", NiveauHabilitation.CLIENT)
    UtilisateurDao.recherche_utilisateur = MagicMock(return_value=utilisateur)

    service = UtilisateurService()
    resultat = service.rechercher_utilisateur(1)

    assert resultat == utilisateur
    UtilisateurDao.recherche_utilisateur.assert_called_once_with(1)


def test_modifier_habilitation_succes():
    admin = Utilisateur(1, "admin_user", "hashed_pwd", NiveauHabilitation.ADMIN)
    admin_bdd = Utilisateur(1, "admin_user", "hashed_pwd", NiveauHabilitation.ADMIN)
    client_bdd = Utilisateur(2, "client_user", "hashed_pwd", NiveauHabilitation.CLIENT)

    UtilisateurDao.recherche_utilisateur = MagicMock(side_effect=[admin_bdd, client_bdd])
    UtilisateurDao.update = MagicMock(return_value=True)

    service = UtilisateurService()
    resultat = service.modifier_habilitation(admin, 2, NiveauHabilitation.ADMIN)

    assert resultat is True
    UtilisateurDao.update.assert_called_once_with(2, NiveauHabilitation.ADMIN)


def test_modifier_habilitation_non_admin():
    client = Utilisateur(2, "client_user", "hashed_pwd", NiveauHabilitation.CLIENT)
    client_bdd = Utilisateur(2, "client_user", "hashed_pwd", NiveauHabilitation.CLIENT)
    UtilisateurDao.recherche_utilisateur = MagicMock(return_value=client_bdd)

    service = UtilisateurService()
    with pytest.raises(PermissionError) as exc_info:
        service.modifier_habilitation(client, 3, NiveauHabilitation.ADMIN)
    assert str(exc_info.value) == "Seul un administrateur peut modifier les habilitations."
