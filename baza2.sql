CREATE TABLE zaposleni(
  emso TEXT PRIMARY KEY,
  ime TEXT NOT NULL,
  telefon TEXT,
  placa INTEGER NOT NULL,
  naslov TEXT NOT NULL,
  prodajalec BOOL NOT NULL
);
CREATE TABLE avto(
  id INTEGER PRIMARY KEY,
  barva TEXT,
  tip TEXT NOT NULL,
  znamka TEXT NOT NULL,
  cena INTEGER NOT NULL,
  rabljeni BOOL NOT NULL
);
CREATE TABLE prodaja(
  id INTEGER PRIMARY KEY,
  id_avto INTEGER REFERENCES avto(id),
  datum DATE,
  nacim_placila TEXT NOT NULL,
  prodajalec TEXT NOT NULL REFERENCES zaposleni(emso)
);
CREATE TABLE rabljeni(
  id INTEGER PRIMARY KEY REFERENCES avto(id),
  st_kilometrov INTEGER,
  leto_izdelave DATE
);
CREATE TABLE novi(
  id INTEGER PRIMARY KEY REFERENCES avto(id)
);
CREATE TABLE servis(
  id INTEGER PRIMARY KEY,
  datum DATE,
  tip_servisa TEXT,
  id_serviser TEXT NOT NULL REFERENCES zaposleni(emso),
  id_avto INTEGER NOT NULL REFERENCES avto(id)
);
CREATE TABLE priprava(
  id INTEGER PRIMARY KEY,
  id_avto INTEGER NOT NULL REFERENCES avto(id),
  id_serviser TEXT NOT NULL REFERENCES zaposleni(emso)
);





CREATE TABLE zaposleni2(
  id_zaposlenega TEXT PRIMARY KEY,
  tip_zaposlenega VARCHAR(255) NOT NULL,
  ime TEXT NOT NULL,
  telefon TEXT,
  placa INTEGER NOT NULL,
  naslov TEXT NOT NULL,
  UNIQUE (id_zaposlenega, tip_zaposlenega),
  CHECK (tip_zaposlenega = 'Prodajalec' OR tip_zaposlenega = 'Serviser' OR tip_zaposlenega = 'Lastnik')
);


CREATE TABLE prodaja2 (
  id INTEGER PRIMARY KEY,
  id_avto INTEGER REFERENCES avto(id),
  datum DATE,
  nacim_placila TEXT NOT NULL,
  id_zaposlenega TEXT NOT NULL,
  tip_zaposlenega VARCHAR(255) NOT NULL,
  FOREIGN KEY (id_zaposlenega, tip_zaposlenega)
    REFERENCES zaposleni2(id_zaposlenega, tip_zaposlenega)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CHECK (tip_zaposlenega = 'Prodajalec')
);

CREATE TABLE servis2(
  id INTEGER PRIMARY KEY,
  id_avto INTEGER NOT NULL REFERENCES avto(id),
  datum DATE,
  tip_servisa TEXT,
  id_zaposlenega TEXT NOT NULL,
  tip_zaposlenega VARCHAR(255) NOT NULL,
  FOREIGN KEY (id_zaposlenega, tip_zaposlenega)
    REFERENCES zaposleni2(id_zaposlenega, tip_zaposlenega)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CHECK (tip_zaposlenega = 'Serviser')
);

CREATE TABLE priprava2(
  id INTEGER PRIMARY KEY,
  id_avto INTEGER NOT NULL REFERENCES avto(id),
  id_zaposlenega TEXT NOT NULL,
  tip_zaposlenega VARCHAR(255) NOT NULL,
  FOREIGN KEY (id_zaposlenega, tip_zaposlenega)
    REFERENCES zaposleni2(id_zaposlenega, tip_zaposlenega)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CHECK (tip_zaposlenega = 'Serviser')
);