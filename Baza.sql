CREATE TABLE zaposleni (
  emso TEXT PRIMARY KEY,
  telefon TEXT,
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
  id TEXT PRIMARY KEY,
  barva TEXT,
  tip TEXT,
  znamka TEXT,
  cena INTEGER
);
CREATE TABLE priprava(
  id TEXT PRIMARY KEY,
  serviser TEXT NOT NULL REFERENCES serviser(emso)
);
CREATE TABLE servis(
  id TEXT PRIMARY KEY,
  datum DATE,
  tip TEXT,
  serviser TEXT NOT NULL REFERENCES serviser(emso)
);
CREATE TABLE rabljen(
  id TEXT PRIMARY KEY REFERENCES avto(id),
  st_kilometrov INTEGER,
  leto_izdelave DATE,
  priprava TEXT REFERENCES priprava(id)
);
CREATE TABLE novi(
  id TEXT PRIMARY KEY REFERENCES avto(id),
  priprava TEXT REFERENCES priprava(id)
);
CREATE TABLE prodaja(
  id TEXT PRIMARY KEY,
  avto TEXT REFERENCES avto(id),
  cena INTEGER,
  datum DATE,
  nacim_placila TEXT,
  prodajalec TEXT NOT NULL REFERENCES prodajalec(emso)
);
