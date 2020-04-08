CREATE TABLE zaposleni (
  emso TEXT PRIMARY KEY,
  telefon INTEGER,
  naslov TEXT,
  placa INTEGER
);
CREATE TABLE serviser(
  emso TEXT PRIMARY KEY REFERENCES zaposleni(emso)
);
CREATE TABLE prodajalec(
  emso TEXT PRIMARY KEY REFERENCES zaposleni(emso)
);
CREATE TABLE avto(
  id INTEGER PRIMARY KEY,
  barva TEXT,
  tip TEXT,
  znamka TEXT,
  cena INTEGER
);
CREATE TABLE priprava(
  id INTEGER PRIMARY KEY,
  id_avto INTEGER NOT NULL REFERENCES avto(id)
  id_serviser TEXT NOT NULL REFERENCES serviser(emso)
);
CREATE TABLE servis(
  id INTEGER PRIMARY KEY,
  datum DATE,
  tip_servisa TEXT,
  id_serviser INTEGER NOT NULL REFERENCES serviser(emso)
  id_avto INTEGER NOT NULL REFERENCES avto(id)
);
CREATE TABLE rabljeni(
  id INTEGER PRIMARY KEY REFERENCES avto(id),
  st_kilometrov INTEGER,
  leto_izdelave DATE
);
CREATE TABLE novi(
  id INTEGER PRIMARY KEY REFERENCES avto(id),
);
CREATE TABLE prodaja(
  id INTEGER PRIMARY KEY,
  id_avto TEXT REFERENCES avto(id),
  cena INTEGER,
  datum DATE,
  nacim_placila TEXT,
  prodajalec TEXT NOT NULL REFERENCES prodajalec(emso)
);
