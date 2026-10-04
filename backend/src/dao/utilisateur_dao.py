from dao.db_connection import DBConnection


class UtilisateurDao:

  def __init__(self):
    self.db = DBConnection()
    self.connection = self.db.connection

  def creer_utilisateur(self, nom: str, email: str, mot_de_passe_hache: str):
    """Insère un nouvel utilisateur dans la base de données de façon sécurisée."""

    requete = """
            INSERT INTO utilisateur (nom, email, mot_de_passe)
            VALUES (%s, %s, %s)
            RETURNING id, nom, email;
        """

    try:
      with self.connection.cursor() as cursor:
        cursor.execute(requete, (nom, email, mot_de_passe_hache))
        utilisateur_cree = cursor.fetchone()
     
      self.connection.commit()
      return utilisateur_cree

    except Exception:
      self.connection.rollback()
      raise

  def trouver_par_email(self, email: str):
    """Cherche un utilisateur par son email, car celui-ci est unique."""

    requete = "SELECT * FROM utilisateur WHERE email = %s"

    try:
      with self.connection.cursor() as cursor:
        cursor.execute(requete, (email,))
        return cursor.fetchone()

    except Exception:
      self.connection.rollback()
      raise
