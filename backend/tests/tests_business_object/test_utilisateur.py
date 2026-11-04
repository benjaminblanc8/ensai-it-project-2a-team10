from argon2 import PasswordHasher
from business_object.niveau_habilitation import NiveauHabilitation
from business_object.utilisateur import Utilisateur


def test_utilisateur_creation_et_getters():
    utilisateur = Utilisateur(1, "jeremie", "mdp", NiveauHabilitation.CLIENT)

    assert utilisateur.get_id_utilisateur() == 1
    assert utilisateur.get_pseudo() == "jeremie"
    assert utilisateur.get_niveau() == NiveauHabilitation.CLIENT


def test_verifier_role_client():
    utilisateur = Utilisateur(1, "jeremie", "mdp123", NiveauHabilitation.CLIENT)

    assert utilisateur.verifier_role(NiveauHabilitation.CLIENT) is True
    assert utilisateur.verifier_role(NiveauHabilitation.COLLAB) is False
    assert utilisateur.verifier_role(NiveauHabilitation.ADMIN) is False


def test_verifier_role_collab():
    utilisateur = Utilisateur(2, "benjamin", "mdp123", NiveauHabilitation.COLLAB)

    assert utilisateur.verifier_role(NiveauHabilitation.CLIENT) is False
    assert utilisateur.verifier_role(NiveauHabilitation.COLLAB) is True
    assert utilisateur.verifier_role(NiveauHabilitation.ADMIN) is False


def test_verifier_role_admin():
    utilisateur = Utilisateur(3, "hugo", "mdp123", NiveauHabilitation.ADMIN)

    assert utilisateur.verifier_role(NiveauHabilitation.CLIENT) is False
    assert utilisateur.verifier_role(NiveauHabilitation.COLLAB) is False
    assert utilisateur.verifier_role(NiveauHabilitation.ADMIN) is True


def test_verifier_mdp():
    ph = PasswordHasher()
    hash_reel = ph.hash("mot_de_passe_secret")
    # On passe le vrai hash à l'utilisateur
    utilisateur = Utilisateur(1, "alexandre", hash_reel, NiveauHabilitation.CLIENT)

    # On vérifie que le bon mot de passe passe, et le mauvais échoue
    assert utilisateur.verifier_mdp("mot_de_passe_secret") is True
    assert utilisateur.verifier_mdp("mauvais_mot_de_passe") is False
