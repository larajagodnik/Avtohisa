CREATE TABLE zaposleni(
  emso TEXT PRIMARY KEY,
  ime TEXT NOT NULL,
  telefon INTEGER,
  placa INTEGER NOT NULL,
  naslov TEXT NOT NULL,
  serviser BOOL NOT NULL,
  prodajalec BOOL NOT NULL
);
CREATE TABLE avto(
  id INTEGER PRIMARY KEY,
  barva TEXT,
  tip TEXT NOT NULL,
  znamka TEXT NOT NULL,
  cena INTEGER NOT NULL
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
