-- ============================================================
-- Trajecto — Initialisation de la base de données
-- Usage : psql -h <host> -U <user> -d <database> -f data/init_db.sql
-- ============================================================

-- ------------------------------------------------------------
-- Tables
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS Gare (
    id_gare       SERIAL PRIMARY KEY,
    nom           VARCHAR(255) NOT NULL,
    ville         VARCHAR(255) NOT NULL,
    id_gare_sncf  VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS Utilisateur (
    id_utilisateur  SERIAL PRIMARY KEY,
    pseudo          VARCHAR(100) NOT NULL UNIQUE,
    mdp             TEXT NOT NULL,
    niveau          VARCHAR(20) NOT NULL DEFAULT 'CLIENT'
);

CREATE TABLE IF NOT EXISTS Ligne (
    id_ligne          SERIAL PRIMARY KEY,
    id_gare_depart    INTEGER NOT NULL REFERENCES Gare(id_gare),
    id_gare_arrivee   INTEGER NOT NULL REFERENCES Gare(id_gare),
    date_creation     DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS Trajet (
    id_trajet         SERIAL PRIMARY KEY,
    id_ligne          INTEGER NOT NULL REFERENCES Ligne(id_ligne),
    date_heure_depart TIMESTAMP NOT NULL,
    duree_minutes     INTEGER NOT NULL,
    nb_places         INTEGER NOT NULL CHECK (nb_places >= 0),
    tarif             NUMERIC(10, 2) NOT NULL,
    places_reservees  INTEGER NOT NULL DEFAULT 0 CHECK (places_reservees >= 0 AND places_reservees <= nb_places)
);

CREATE TABLE IF NOT EXISTS Reservation (
    id_reservation  SERIAL PRIMARY KEY,
    id_utilisateur  INTEGER NOT NULL REFERENCES Utilisateur(id_utilisateur),
    id_trajet       INTEGER NOT NULL REFERENCES Trajet(id_trajet)
);

-- ------------------------------------------------------------
-- Données de démonstration
-- ------------------------------------------------------------

-- Gares (id_gare_sncf : identifiants Navitia/SNCF réels)
INSERT INTO Gare (nom, ville, id_gare_sncf) VALUES
    ('Paris Gare de Lyon',    'Paris',    'stop_area:SNCF:87471003'),
    ('Lyon Part-Dieu',        'Lyon',     'stop_area:SNCF:87672241'),
    ('Marseille Saint-Charles','Marseille','stop_area:SNCF:87879058'),
    ('Bordeaux Saint-Jean',   'Bordeaux', 'stop_area:SNCF:87204196'),
    ('Strasbourg',            'Strasbourg','stop_area:SNCF:87603042')
ON CONFLICT DO NOTHING;

-- Utilisateurs
-- admin123  → ADMIN
-- collab123 → COLLAB
-- client123 → CLIENT
INSERT INTO Utilisateur (pseudo, mdp, niveau) VALUES
    ('admin',  '$argon2id$v=19$m=65536,t=3,p=4$SM1WTkX/H77LCDVdFLkN5g$v/nuII99KD6N/F36aJejKtK1ELUFHVEEcFjrnolk3UU', 'ADMIN'),
    ('collab', '$argon2id$v=19$m=65536,t=3,p=4$k0+J/ZmqWw7thoN6vn5K4g$3HwjEjS03JfgCKrvrQs33tUwjv7JzlFkLE/KygwV/n8', 'COLLAB'),
    ('client', '$argon2id$v=19$m=65536,t=3,p=4$1XT6FCu24mMTJi34yoAciw$BG8i/lJk0kDvuux2hnFOwd4YWS2T+QsQ5v+XQE+/lFY', 'CLIENT')
ON CONFLICT (pseudo) DO NOTHING;

-- Lignes
-- 1: Paris Gare de Lyon ↔ Lyon Part-Dieu
-- 2: Paris Gare de Lyon ↔ Marseille Saint-Charles
-- 3: Lyon Part-Dieu ↔ Strasbourg
INSERT INTO Ligne (id_gare_depart, id_gare_arrivee, date_creation) VALUES
    (1, 2, CURRENT_DATE),
    (1, 3, CURRENT_DATE),
    (2, 5, CURRENT_DATE)
ON CONFLICT DO NOTHING;

-- Trajets
INSERT INTO Trajet (id_ligne, date_heure_depart, duree_minutes, nb_places, tarif, places_reservees) VALUES
    (1, '2026-01-15 08:00:00', 155, 20, 39.50, 0),
    (1, '2026-01-15 14:30:00', 155, 20, 42.00, 0),
    (2, '2026-01-16 07:45:00', 300, 15, 55.90, 0),
    (3, '2026-01-16 10:15:00', 190, 18, 32.00, 0)
ON CONFLICT DO NOTHING;

-- Réservations (client réserve le trajet 1, collab réserve le trajet 3)
INSERT INTO Reservation (id_utilisateur, id_trajet) VALUES
    (3, 1),
    (2, 3)
ON CONFLICT DO NOTHING;

-- Mise à jour des compteurs de places après les réservations
UPDATE Trajet SET places_reservees = places_reservees + 1
WHERE id_trajet IN (SELECT id_trajet FROM Reservation WHERE id_utilisateur = 3);

UPDATE Trajet SET places_reservees = places_reservees + 1
WHERE id_trajet IN (SELECT id_trajet FROM Reservation WHERE id_utilisateur = 2);

-- ------------------------------------------------------------
-- Réinitialisation des séquences (évite les conflits si re-exécuté)
-- ------------------------------------------------------------

SELECT setval(pg_get_serial_sequence('Gare', 'id_gare'), COALESCE(MAX(id_gare), 0) + 1, false) FROM Gare;
SELECT setval(pg_get_serial_sequence('Utilisateur', 'id_utilisateur'), COALESCE(MAX(id_utilisateur), 0) + 1, false) FROM Utilisateur;
SELECT setval(pg_get_serial_sequence('Ligne', 'id_ligne'), COALESCE(MAX(id_ligne), 0) + 1, false) FROM Ligne;
SELECT setval(pg_get_serial_sequence('Trajet', 'id_trajet'), COALESCE(MAX(id_trajet), 0) + 1, false) FROM Trajet;
SELECT setval(pg_get_serial_sequence('Reservation', 'id_reservation'), COALESCE(MAX(id_reservation), 0) + 1, false) FROM Reservation;