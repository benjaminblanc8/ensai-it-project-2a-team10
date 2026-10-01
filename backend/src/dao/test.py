from backend.src.business_object.gare import Gare
from backend.src.dao.gare_dao import GareDao


gare_dao = GareDao()

# 1. Création d'un objet Gare
gare = Gare(
    None,
    "Test",
    "ville_test",
    0,
    0
)

print("Avant insertion :", gare)

# 2. INSERT dans la BDD
resultat = gare_dao.create_gare(gare)

print("Insertion réussie :", resultat)
print("ID donné par PostgreSQL :", gare.id_gare)


# 3. Recherche de la gare créée
gare_trouvee = gare_dao.recherche_gare(gare.id_gare)

print("Gare trouvée :", gare_trouvee)
