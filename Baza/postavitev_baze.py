import psycopg2
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki
import csv

from conf_baza import *

conn_string = "host='{0}' dbname='{1}' user='{2}' password='{3}'".format(host, dbname, user, password)

def izbrisi():
    with psycopg2.connect(conn_string) as con:
        cur = con.cursor()
        cur.execute("DROP TABLE IF EXISTS priprava CASCADE")
        cur.execute("DROP TABLE IF EXISTS prodaja CASCADE")
        cur.execute("DROP TABLE IF EXISTS servis CASCADE")
        cur.execute("DROP TABLE IF EXISTS rabljeni CASCADE")
        cur.execute("DROP TABLE IF EXISTS novi CASCADE")
        cur.execute("DROP TABLE IF EXISTS avto CASCADE")
        cur.execute("DROP TABLE IF EXISTS zaposleni CASCADE")
    print("Baza je izbrisana!")

#id_zaposlenega spremenimo v emso?
def ustvari_tabelo_zaposleni():
    with psycopg2.connect(conn_string) as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS zaposleni(
              id_zaposlenega TEXT PRIMARY KEY,
              tip_zaposlenega VARCHAR(255) NOT NULL,
              ime TEXT NOT NULL,
              telefon TEXT,
              placa INTEGER NOT NULL,
              naslov TEXT NOT NULL,
              UNIQUE (id_zaposlenega, tip_zaposlenega),
              CHECK (tip_zaposlenega = 'Prodajalec' OR tip_zaposlenega = 'Serviser' OR tip_zaposlenega = 'Lastnik')
            );
        """)
    print("Tabela zaposleni ustvarjena!")

def ustvari_tabelo_avto():
    with psycopg2.connect(conn_string) as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS avto(
              id INTEGER PRIMARY KEY,
              barva TEXT,
              tip TEXT NOT NULL,
              znamka TEXT NOT NULL,
              cena INTEGER NOT NULL,
              novi BOOL NOT NULL
            );
        """)
    print("Tabela avtov ustvarjena!")

def ustvari_tabelo_prodaja():
    with psycopg2.connect(conn_string) as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS prodaja(
              id INTEGER PRIMARY KEY,
              id_avto INTEGER REFERENCES avto(id),
              datum DATE,
              nacim_placila TEXT NOT NULL,
              id_zaposlenega TEXT NOT NULL,
              tip_zaposlenega VARCHAR(255) NOT NULL,
              FOREIGN KEY (id_zaposlenega, tip_zaposlenega)
                REFERENCES zaposleni(id_zaposlenega, tip_zaposlenega)
                ON DELETE NO ACTION
                ON UPDATE CASCADE,
              CHECK (tip_zaposlenega = 'Prodajalec')
            );
        """)
    print("Tabela prodanih avtov ustvarjena!")

def ustvari_tabelo_rabljeni():
    with psycopg2.connect(conn_string) as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS rabljeni(
              id INTEGER PRIMARY KEY REFERENCES avto(id)
                ON DELETE NO ACTION
                ON UPDATE CASCADE,
              st_kilometrov INTEGER,
              leto_izdelave DATE
            );
        """)
    print("Tabela rabljenih avtov ustvarjena!")

def ustvari_tabelo_novi():
    with psycopg2.connect(conn_string) as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS novi(
              id INTEGER PRIMARY KEY REFERENCES avto(id)
                ON DELETE NO ACTION
                ON UPDATE CASCADE
            );
        """)
    print("Tabela novih avtov ustvarjena!")   

def ustvari_tabelo_servis():
    with psycopg2.connect(conn_string) as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS servis(
              id INTEGER PRIMARY KEY,
              id_avto INTEGER NOT NULL REFERENCES avto(id),
              datum DATE,
              tip_servisa TEXT,
              id_zaposlenega TEXT NOT NULL,
              tip_zaposlenega VARCHAR(255) NOT NULL,
              FOREIGN KEY (id_zaposlenega, tip_zaposlenega)
                REFERENCES zaposleni(id_zaposlenega, tip_zaposlenega)
                ON DELETE NO ACTION
                ON UPDATE CASCADE,
              CHECK (tip_zaposlenega = 'Serviser')
            );
        """)  
    print("Tabela servisiranih avtov ustvarjena!")  

def ustvari_tabelo_priprava():
    with psycopg2.connect(conn_string) as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS priprava(
              id INTEGER PRIMARY KEY,
              id_avto INTEGER NOT NULL REFERENCES avto(id),
              id_zaposlenega TEXT NOT NULL,
              tip_zaposlenega VARCHAR(255) NOT NULL,
              FOREIGN KEY (id_zaposlenega, tip_zaposlenega)
                REFERENCES zaposleni(id_zaposlenega, tip_zaposlenega)
                ON DELETE NO ACTION
                ON UPDATE CASCADE,
              CHECK (tip_zaposlenega = 'Serviser')
            );
        """) 
    print("Tabela pripravljenih avtov ustvarjena!") 


#Urejanje pravic

def pravice():
    with psycopg2.connect(conn_string) as con:
        cur = con.cursor()
        cur.execute("""
            GRANT ALL ON DATABASE sem2020_jansi TO laraj;
            GRANT ALL ON SCHEMA public TO laraj;
            GRANT ALL ON ALL TABLES IN SCHEMA public TO laraj;
            GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO laraj; 
        """)
    print("Pravice dodane osebi: laraj!")

#Klicanje funkcij


#izbrisi() #če želimo zbrisati celo bazo! NOT GOOD IDEA ;)!!

ustvari_tabelo_zaposleni()
ustvari_tabelo_avto()
ustvari_tabelo_prodaja()
ustvari_tabelo_rabljeni()
ustvari_tabelo_novi()
ustvari_tabelo_servis()
ustvari_tabelo_priprava()

pravice()

#Uvoz podatkov
def uvoziCSV(cur, tabela):
    with open('podatki/{0}.csv'.format(tabela)) as csvfile:
        podatki = csv.reader(csvfile)
        vsiPodatki = [vrstica for vrstica in podatki]
        glava = vsiPodatki[0]
        vrstice = vsiPodatki[1:]
        cur.executemany("INSERT INTO {0} ({1}) VALUES ({2})".format(
            tabela, ",".join(glava), ",".join(['%s']*len(glava))), vrstice)

# ne dela dokler v bazi ne postavimo na decimalke ne integer, bazo lahko brise samo jan
with psycopg2.connect(conn_string) as con:
    cur = con.cursor()
    #uvoziCSV(cur, 'avto')
    #uvoziCSV(cur, 'rabljeni')
    #uvoziCSV(cur, 'zaposleni')