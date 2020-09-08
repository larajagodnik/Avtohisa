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
        cur.execute("DROP TABLE IF EXISTS priljubljeni CASCADE")
        cur.execute("DROP TABLE IF EXISTS prijava CASCADE")
    print("Baza je izbrisana!")

#id_zaposlenega spremenimo v emso?
# LIKE
def ustvari_tabelo_zaposleni():
    with psycopg2.connect(conn_string) as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS zaposleni(
              id_zaposlenega TEXT PRIMARY KEY,
              tip_zaposlenega VARCHAR(255) NOT NULL,
              ime TEXT NOT NULL,
              telefon TEXT,
              placa FLOAT(2) NOT NULL,
              naslov TEXT NOT NULL,
              UNIQUE (id_zaposlenega, tip_zaposlenega),
              CHECK (tip_zaposlenega LIKE 'Prodajalec' OR tip_zaposlenega LIKE 'Serviser' OR tip_zaposlenega LIKE 'Lastnik')
            );
        """)
    print("Tabela zaposleni ustvarjena!")

def ustvari_tabelo_avto():
    with psycopg2.connect(conn_string) as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS avto(
              id TEXT PRIMARY KEY,
              barva TEXT,
              tip TEXT NOT NULL,
              znamka TEXT NOT NULL,
              cena FLOAT(2) NOT NULL,
              leto_izdelave INTEGER NOT NULL,
              novi BOOL NOT NULL
            );
        """)
    print("Tabela avtov ustvarjena!")

def ustvari_tabelo_prodaja():
    with psycopg2.connect(conn_string) as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS prodaja(
              id SERIAL PRIMARY KEY,
              id_avto TEXT REFERENCES avto(id),
              datum DATE,
              nacin_placila TEXT NOT NULL,
              id_zaposlenega TEXT NOT NULL,
              FOREIGN KEY (id_zaposlenega)
                REFERENCES zaposleni(id_zaposlenega)
                ON DELETE NO ACTION
                ON UPDATE CASCADE
            );
        """)
    print("Tabela prodanih avtov ustvarjena!")

def ustvari_tabelo_rabljeni(): 
    with psycopg2.connect(conn_string) as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS rabljeni(
              id_avto TEXT PRIMARY KEY REFERENCES avto(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
              st_kilometrov INTEGER NOT NULL,
              servis DATE      
            );
        """)
    print("Tabela rabljenih avtov ustvarjena!")

def ustvari_tabelo_novi():
    with psycopg2.connect(conn_string) as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS novi(
              id_avto TEXT PRIMARY KEY REFERENCES avto(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
              pripravljen BOOL DEFAULT false
            );
        """)
    print("Tabela novih avtov ustvarjena!")   

def ustvari_tabelo_servis():
    with psycopg2.connect(conn_string) as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS servis(
              id SERIAL PRIMARY KEY,
              id_avto TEXT NOT NULL REFERENCES avto(id),
              datum DATE,
              tip_servisa TEXT,
              id_zaposlenega TEXT NOT NULL,
              FOREIGN KEY (id_zaposlenega)
                REFERENCES zaposleni(id_zaposlenega)
                ON DELETE NO ACTION
                ON UPDATE CASCADE
            );
        """)  
    print("Tabela servisiranih avtov ustvarjena!")  

def ustvari_tabelo_priprava():
    # datum??
    with psycopg2.connect(conn_string) as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS priprava(
              id SERIAL PRIMARY KEY,
              id_avto TEXT NOT NULL REFERENCES avto(id),
              datum DATE,
              id_zaposlenega TEXT NOT NULL,
              FOREIGN KEY (id_zaposlenega)
                REFERENCES zaposleni(id_zaposlenega)
                ON DELETE NO ACTION
                ON UPDATE CASCADE
            );
        """) 
    print("Tabela pripravljenih avtov ustvarjena!") 

def ustvari_tabelo_priljubljeni():
    with psycopg2.connect(conn_string) as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS priljubljeni(
              id SERIAL PRIMARY KEY,
              uporabnik TEXT NOT NULL,
              id_avto TEXT NOT NULL REFERENCES avto(id)
                  ON DELETE NO ACTION
                  ON UPDATE CASCADE
            );
        """) 
    print("Tabela priljubljenih avtov ustvarjena!") 

def ustvari_tabelo_prijava():
    with psycopg2.connect(conn_string) as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS prijava(
              uporabnik TEXT PRIMARY KEY,
              geslo TEXT NOT NULL,
              status INTEGER DEFAULT 3,
              ime TEXT NOT NULL,
              priimek TEXT NOT NULL
            );
        """) 
    print("Tabela priljubljenih avtov ustvarjena!") 

#Urejanje pravic

def pravice():
    with psycopg2.connect(conn_string) as con:
        cur = con.cursor()
        cur.execute("""
            GRANT ALL ON DATABASE sem2020_jansi TO laraj;
            GRANT ALL ON SCHEMA public TO laraj;
            GRANT ALL ON ALL TABLES IN SCHEMA public TO laraj;
            GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO laraj; 

            GRANT ALL ON DATABASE sem2020_jansi TO javnost;
            GRANT SELECT ON ALL TABLES IN SCHEMA public TO javnost;
            GRANT INSERT ON ALL TABLES IN SCHEMA public TO javnost;
            GRANT DELETE ON ALL TABLES IN SCHEMA public TO javnost;
            GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO javnost;
        """)
    print("Pravice dodane osebi: laraj in javnosti!")

#Funkcija za uvoz podatkov
def uvoziCSV(cur, tabela):
    with open('podatki/{0}.csv'.format(tabela), encoding='utf-8') as csvfile:
        podatki = csv.reader(csvfile)
        vsiPodatki = [vrstica for vrstica in podatki]
        glava = vsiPodatki[0]
        vrstice = vsiPodatki[1:]
        cur.executemany("INSERT INTO {0} ({1}) VALUES ({2})".format(
            tabela, ",".join(glava), ",".join(['%s']*len(glava))), vrstice)
    print("Dodal podatke o {0}!".format(tabela))

#Dejanski uvoz podatkov
def uvozi():
    try:
        with psycopg2.connect(conn_string) as con:
            cur = con.cursor()
            uvoziCSV(cur, 'avto')
    except:
        print("Neka napaka, podatki verjetno že obstajajo!")
    try:
        with psycopg2.connect(conn_string) as con:
            cur = con.cursor()
            uvoziCSV(cur, 'zaposleni')
    except:
        print("Neka napaka, podatki verjetno že obstajajo!")
    try:
        with psycopg2.connect(conn_string) as con:
            cur = con.cursor()
            uvoziCSV(cur, 'novi')
    except:
        print("Neka napaka, podatki verjetno že obstajajo!") 
    
    try:
        with psycopg2.connect(conn_string) as con:
            cur = con.cursor()
            uvoziCSV(cur, 'rabljeni')
    except:
        print("Neka napaka, podatki verjetno že obstajajo!")   
    

#Klicanje funkcij


izbrisi() #če želimo zbrisati celo bazo! NOT GOOD IDEA ;)!!
ustvari_tabelo_zaposleni()
ustvari_tabelo_avto()
ustvari_tabelo_prodaja()
ustvari_tabelo_rabljeni()
ustvari_tabelo_novi()
ustvari_tabelo_servis()
ustvari_tabelo_priprava()
ustvari_tabelo_priljubljeni()

pravice()

uvozi()
