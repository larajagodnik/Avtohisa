#Uvoz bottla
from bottle import *


#Uvoz podatkov za povezavo
import auth_public as auth

#Uvoz psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import os
import binascii

# moras imet skupaj z reloader = true, da ne rabis usakic na novo
# poganjat pythona -- oboje izklopis ko oodajas aplikacijo profesorju
debug(True)

skrivnost = "SWiY1234"

#Privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
ROOT = os.environ.get('BOTTLE_ROOT', '/')
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)

#Funkcije
def rtemplate(*largs, **kwargs):
    """
    Izpis predloge s podajanjem spremenljivke ROOT z osnovnim URL-jem.
    """
    return template(ROOT=ROOT, *largs, **kwargs)

static_dir = "./static"
@route("/static/<filename:path>")
def static(filename):
    return static_file(filename, root=static_dir)


@get('/')
def index():
    uporabnik = request.get_cookie('account', secret=skrivnost)
    registracija = request.get_cookie('registracija', secret=skrivnost)
    napaka = request.get_cookie('napaka', secret=skrivnost)
    status = request.get_cookie('dovoljenje', secret=skrivnost)

    # kaj se pojavi v selectih, kjer lahko izbiras katere avte zelis videti
    cur.execute("SELECT DISTINCT leto_izdelave FROM avto ORDER BY leto_izdelave")
    leta = cur.fetchall()

    cur.execute("SELECT DISTINCT barva FROM avto")
    barve = cur.fetchall()

    cur.execute("SELECT DISTINCT tip FROM avto")
    tipi = cur.fetchall()

    cur.execute("SELECT DISTINCT znamka FROM avto")
    znamke = cur.fetchall()
   
    # avto ki je ze prodan se ne pokaze uporabnikom strani
    cur.execute("""SELECT avto.*, st_kilometrov, 1 as je_priljubljen FROM avto 
                    LEFT JOIN rabljeni on avto.id = rabljeni.id_avto 
                    WHERE id NOT IN (SELECT DISTINCT id_avto FROM prodaja) ORDER BY avto.id""")
    if(request.get_cookie('account', secret=skrivnost)):
        cur.execute("""SELECT avto.*, rabljeni.st_kilometrov, priljubljeni.id FROM avto
                        LEFT JOIN rabljeni on avto.id = rabljeni.id_avto 
                        LEFT JOIN priljubljeni ON
                        (avto.id = priljubljeni.id_avto AND priljubljeni.uporabnik LIKE %s )
                        WHERE avto.id NOT IN (SELECT DISTINCT id_avto FROM prodaja)
                        ORDER BY avto.id""", (uporabnik, ))
    
    #naslov domace strani
    naslov = 'Vsi avti'
    return rtemplate('avto_vsi.html', avto=cur, naslov=naslov, uporabnik=uporabnik, registracija=registracija, napaka=napaka, leta=leta, barve=barve, tipi=tipi, znamke=znamke, status=status)

@get('/avto/<x:re:[a-z]+>')
def avto(x):
    uporabnik = request.get_cookie('account', secret=skrivnost)
    registracija = request.get_cookie('registracija', secret=skrivnost)
    napaka = request.get_cookie('napaka', secret=skrivnost)
    status = request.get_cookie('dovoljenje', secret=skrivnost)

    if str(x) == 'vsi':
        redirect('{}'.format(ROOT))
    if str(x) == 'priljubljeni':
        pravice = ima_pravice()
        if (pravice != 3) or pravice is None:
            return
        cur.execute("SELECT avto.* FROM avto JOIN priljubljeni ON avto.id = priljubljeni.id_avto WHERE uporabnik LIKE %s", (uporabnik,))
        naslov = 'Priljubljeni avti'
        return rtemplate('priljubljeni.html', avto=cur, naslov=naslov, uporabnik=uporabnik, registracija=registracija, napaka=napaka, status=status)

###############################
###### avto prijavljen ########
###############################
# get zahtevek za tabelo avtov ko imas status 1 ali 2 (lastnik, zaposleni) in kliknes upravljaj avte
@get('/avto_prijavljen')
def avto_prijavljen():

    pravice = ima_pravice()
    if (pravice != 1 and pravice != 2) or pravice is None:
        return

    uporabnik = request.get_cookie('account', secret=skrivnost)
    napaka = request.get_cookie('napaka', secret=skrivnost)
    registracija = request.get_cookie('registracija', secret=skrivnost)
    status = request.get_cookie('dovoljenje', secret=skrivnost)
    
    cur.execute("""SELECT avto.*, TO_CHAR(priprava.datum, 'DD. MM. YYYY'), TO_CHAR(rabljeni.servis, 'DD. MM. YYYY') as servisiran,
                (SELECT id FROM prodaja WHERE prodaja.id_avto = avto.id) AS je_prodan 
                FROM avto 
                LEFT JOIN novi ON avto.id = novi.id_avto 
                LEFT JOIN priprava ON avto.id = priprava.id_avto
                LEFT JOIN servis ON avto.id = servis.id_avto
                LEFT JOIN rabljeni ON avto.id = rabljeni.id_avto
                ORDER BY avto.id""")
    return rtemplate('avto_prijavljen.html', avto=cur, uporabnik=uporabnik, registracija=registracija, napaka=napaka, status=status)


###############################
###### avto dodaj ########
###############################

## get in post zahtevka ko v navigaciji kliknes dodaj avto
# preusmeri te na formo kjer dodajas avto
@get('/avto_prijavljen/dodaj')
def avto_prijavljen_dodaj():

    pravice = ima_pravice()
    if pravice != 1 or pravice is None:
        return

    uporabnik = request.get_cookie('account', secret=skrivnost)
    napaka = request.get_cookie('napaka', secret=skrivnost)
    registracija = request.get_cookie('registracija', secret=skrivnost)
    status = request.get_cookie('dovoljenje', secret=skrivnost)
    return rtemplate('avto_prijavljen_dodaj.html', uporabnik=uporabnik, registracija=registracija, napaka=napaka, status=status)
    
# iz forme dobis podatke in jih vstavis v bazo
@post('/avto_prijavljen/dodaj')
def dodaj_avto():

    Id_avta = request.forms.Id_avta
    barva = request.forms.barva
    tip = request.forms.tip
    znamka = request.forms.znamka
    cena = request.forms.cena
    leto_izdelave = request.forms.leto_izdelave
    novi = request.forms.novi
    sql = "INSERT INTO avto (id, barva, tip, znamka, cena, leto_izdelave, novi) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    val = (Id_avta, barva, tip, znamka, cena, leto_izdelave, novi)
    cur.execute(sql,val)
 
    if novi == 'false':    
        st_kilometrov = request.forms.st_kilometrov
        servis = request.forms.datum_zadnjega_servisa
        if servis != "":
            sql = "INSERT INTO rabljeni (id_avto, st_kilometrov, servis) VALUES (%s, %s, %s)"
            val = (Id_avta, st_kilometrov, servis)
            cur.execute(sql,val)
        else:
            sql = "INSERT INTO rabljeni (id_avto, st_kilometrov, servis) VALUES (%s, %s, %s)"
            val = (Id_avta, st_kilometrov, None)
            cur.execute(sql,val)

    
    elif novi == 'true':   
        sql = "INSERT INTO novi VALUES (%s, %s)"
        val = (Id_avta, 'false')
        cur.execute(sql,val)      

    redirect('{}avto_prijavljen'.format(ROOT))

###############################
###### avto prodaja ########
###############################

# za gumb prodaja
@post('/avto_prijavljen/prodaja/<id>')
def prodaja(id):

    cur.execute("SELECT datum FROM servis WHERE id_avto = %s ORDER BY datum desc LIMIT 1", (id, ))
    datum_zadnjega_servisa1 = cur.fetchall()
    cur.execute("SELECT servis FROM rabljeni WHERE id_avto = %s", (id, ))
    datum_zadnjega_servisa2 = cur.fetchall()
    cur.execute("SELECT datum FROM priprava WHERE id_avto = %s", (id, ))
    datum_priprave = cur.fetchall()
    datum_omejim_min = max(datum_zadnjega_servisa1, datum_zadnjega_servisa2, datum_priprave)

    cur.execute("""SELECT id_zaposlenega, ime FROM zaposleni
        	    WHERE tip_zaposlenega LIKE 'Prodajalec' OR tip_zaposlenega LIKE 'Lastnik'  AND trenutno_zaposlen = 'True'""")
    zaposleni = cur.fetchall()

    cur.execute("SELECT id, id_avto, datum, nacin_placila, id_zaposlenega FROM prodaja")

    uporabnik = request.get_cookie('account', secret=skrivnost)
    napaka = request.get_cookie('napaka', secret=skrivnost)
    registracija = request.get_cookie('registracija', secret=skrivnost)
    status = request.get_cookie('dovoljenje', secret=skrivnost)
    return rtemplate('prodaja.html', id=id, prodaja=cur,zaposleni=zaposleni, datum_omejim_min=datum_omejim_min,
     uporabnik=uporabnik, registracija=registracija, napaka=napaka, status=status)

# avto ki je prodan se zapise v tabelo prodaja
@post('/avto_prijavljen/brisi')
def brisi_avto():

    id_avta = request.forms.id_avta
    datum = request.forms.datum
    nacin_placila = request.forms.nacin_placila
    id_zaposlenega = request.forms.Prodajalec
    sql = "INSERT INTO prodaja (id_avto, datum, nacin_placila, id_zaposlenega) VALUES (%s, %s, %s, %s)"  
    val = (id_avta, datum, nacin_placila, id_zaposlenega)
    cur.execute(sql,val)
    redirect('{}avto_prijavljen'.format(ROOT))

# tabela prodanih avtomobilov
@get('/prodaja_tabela')
def prodaja_tabela():

    pravice = ima_pravice()
    if (pravice != 1 and pravice != 2) or pravice is None:
        return

    cur.execute("SELECT * FROM prodaja ORDER BY datum")
    uporabnik = request.get_cookie('account', secret=skrivnost)
    registracija = request.get_cookie('registracija', secret=skrivnost)
    napaka = request.get_cookie('napaka', secret=skrivnost)
    status = request.get_cookie('dovoljenje', secret=skrivnost)
    return rtemplate('prodaja_tabela.html', prodaja_tabela=cur, uporabnik=uporabnik, registracija=registracija, napaka=napaka, status=status)

###############################
###### avto servis ########
###############################

# tabela servis podatkov
@get('/servis')
def servis():

    pravice = ima_pravice()
    if (pravice != 1 and pravice != 2) or pravice is None:
        return

    cur.execute("SELECT * FROM servis")
    uporabnik = request.get_cookie('account', secret=skrivnost)
    registracija = request.get_cookie('registracija', secret=skrivnost)
    napaka = request.get_cookie('napaka', secret=skrivnost)
    status = request.get_cookie('dovoljenje', secret=skrivnost)
    return rtemplate('servis.html', servis=cur, uporabnik=uporabnik, registracija=registracija, napaka=napaka, status=status)

# gumb dodaj servis, ki te preusmeri na formo za vstavljanje podatkov o servisu
@post('/avto_prijavljen/dodaj_servis_info/<id>')
def dodaj_servis_info(id):

    cur.execute("SELECT datum FROM servis WHERE id_avto = %s ORDER BY datum desc LIMIT 1", (id, ))
    datum_zadnjega_servisa1 = cur.fetchall()
    cur.execute("SELECT servis FROM rabljeni WHERE id_avto = %s", (id, ))
    datum_zadnjega_servisa2 = cur.fetchall()
    cur.execute("SELECT datum FROM priprava WHERE id_avto = %s", (id, ))
    datum_priprave = cur.fetchall()
    datum_zadnjega_servisa = max(datum_zadnjega_servisa1, datum_zadnjega_servisa2, datum_priprave)

    cur.execute("SELECT id_zaposlenega, ime FROM zaposleni WHERE tip_zaposlenega LIKE 'Serviser' AND trenutno_zaposlen = 'True'")
    zaposleni = cur.fetchall()
    cur.execute("SELECT id, id_avto, datum, tip_servisa, id_zaposlenega FROM servis")

    uporabnik = request.get_cookie('account', secret=skrivnost)
    napaka = request.get_cookie('napaka', secret=skrivnost)
    registracija = request.get_cookie('registracija', secret=skrivnost)
    status = request.get_cookie('dovoljenje', secret=skrivnost) 

    return rtemplate('dodaj_servis_info.html', id=id, servis=cur, zaposleni=zaposleni, datum_zadnjega_servisa=datum_zadnjega_servisa,
    uporabnik=uporabnik, registracija=registracija, napaka=napaka, status=status)

# dobi podatke o servisu in jih vpise v bazo
@post('/avto_prijavljen/dodaj_servis')
def dodaj_servis():

    id_avta = request.forms.id_avta
    datum = request.forms.datum
    tip_servisa = request.forms.tip_servisa
    id_zaposlenega = request.forms.Serviser

    sql = "INSERT INTO servis (id_avto, datum, tip_servisa, id_zaposlenega) VALUES (%s, %s, %s, %s)"
    val = (id_avta, datum, tip_servisa, id_zaposlenega)
    cur.execute(sql,val)

    cur.execute("UPDATE rabljeni SET servis = %s WHERE id_avto =  %s", (datum, id_avta, )) 
     
    redirect('{}avto_prijavljen'.format(ROOT))
   
###############################
###### avto priprava ########
###############################

# tabela priprava
@get('/priprava')
def priprava():

    pravice = ima_pravice()
    if (pravice != 1 and pravice != 2) or pravice is None:
        return

    cur.execute("SELECT * FROM priprava")
    uporabnik = request.get_cookie('account', secret=skrivnost)
    registracija = request.get_cookie('registracija', secret=skrivnost)
    napaka = request.get_cookie('napaka', secret=skrivnost)
    status = request.get_cookie('dovoljenje', secret=skrivnost)
    return rtemplate('priprava.html', priprava=cur, uporabnik=uporabnik, registracija=registracija, napaka=napaka, status=status)

# za gumb, ki zepreusmeri na formo za dodajanje podatkov o pripravi
@post('/avto_prijavljen/dodaj_pripravo_info/<id>')
def dodaj_pripravo_info(id):

    cur.execute("SELECT id_zaposlenega, ime FROM zaposleni WHERE tip_zaposlenega LIKE 'Serviser' AND trenutno_zaposlen = 'True'")
    zaposleni = cur.fetchall()
    cur.execute("SELECT * FROM priprava")

    uporabnik = request.get_cookie('account', secret=skrivnost)
    napaka = request.get_cookie('napaka', secret=skrivnost)
    registracija = request.get_cookie('registracija', secret=skrivnost)
    status = request.get_cookie('dovoljenje', secret=skrivnost) 

    return rtemplate('dodaj_pripravo_info.html', id=id, priprava=cur, zaposleni=zaposleni,
    uporabnik=uporabnik, registracija=registracija, napaka=napaka, status=status)

# dobi podatke o pripravi in jih vstavi v bazo
@post('/avto_prijavljen/dodaj_pripravo')
def dodaj_pripravo():

    id_avta = request.forms.id_avta
    datum = request.forms.datum
    id_zaposlenega = request.forms.Serviser

    cur.execute("UPDATE novi SET pripravljen = True WHERE id_avto =  %s", (id_avta, ))

    sql = "INSERT INTO priprava (id_avto, datum, id_zaposlenega) VALUES (%s, %s, %s)"
    val = (id_avta, datum, id_zaposlenega)
    cur.execute(sql,val)

    redirect('{}avto_prijavljen'.format(ROOT))

###############################
###### priljubljeni ########
###############################
   
# za gumb dodaj med priljubljene - vstavi v bazo
@get('/avto_vsi/dodaj_pod_priljubljene/<id>')
def priljubljeni_avto(id):
    uporabnik = request.get_cookie('account', secret=skrivnost)
    cur.execute("INSERT INTO priljubljeni (uporabnik, id_avto) VALUES (%s, %s)", (uporabnik, id))
    redirect('{}'.format(ROOT))

# za gumb odstrani (iz priljubljenih) - izbrise iz baze
@get('/avto/priljubljeni/<id>')
def odstrani_priljubljeni_avto(id):
    uporabnik = request.get_cookie('account', secret=skrivnost)
    cur.execute("DELETE FROM priljubljeni WHERE uporabnik = %s AND id_avto = %s", (uporabnik, id, ))
    redirect('{}avto/priljubljeni'.format(ROOT)) 

###############################
###### zaposleni ########
###############################

# tabela zaposlenih
@get('/zaposleni')
def zaposleni():

    pravice = ima_pravice()
    if pravice != 1 or pravice is None:
        return

    uporabnik = request.get_cookie('account', secret=skrivnost)
    registracija = request.get_cookie('registracija', secret=skrivnost)
    napaka = request.get_cookie('napaka', secret=skrivnost)
    status = request.get_cookie('dovoljenje', secret=skrivnost)
    cur.execute("SELECT * FROM zaposleni ORDER BY trenutno_zaposlen DESC, zaposleni.ime")
    return rtemplate('zaposleni.html', zaposleni=cur, uporabnik=uporabnik, registracija=registracija, napaka=napaka, status=status)

# klik na dodaj zaposlenega te preusmer na formo
@get('/zaposleni/dodaj')
def zaposleni_dodaj():

    pravice = ima_pravice()
    if pravice != 1 or pravice is None:
        return

    uporabnik = request.get_cookie('account', secret=skrivnost)
    napaka = request.get_cookie('napaka', secret=skrivnost)
    registracija = request.get_cookie('registracija', secret=skrivnost)
    status = request.get_cookie('dovoljenje', secret=skrivnost)
    return rtemplate('zaposleni_dodaj.html', uporabnik=uporabnik, registracija=registracija, napaka=napaka, status=status)

#dobi podatke o novem zaposlenem in jih vstavi v bazo   
@post('/zaposleni/dodaj')
def dodaj_zaposlenega():
    Id_zaposlenega = request.forms.Id_zaposlenega
    tip_zaposlenega = request.forms.tip_zaposlenega
    ime = request.forms.ime
    telefon = request.forms.telefon
    placa = request.forms.placa
    naslov = request.forms.naslov

    sql = """INSERT INTO zaposleni (id_zaposlenega, tip_zaposlenega, ime, telefon, placa, naslov, trenutno_zaposlen)
            VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    val = (Id_zaposlenega, tip_zaposlenega, ime, telefon, placa, naslov, "true")
    cur.execute(sql,val)

    redirect('{}zaposleni'.format(ROOT))

# za gumb odstrani zaposlenega
@get('/zaposleni/<id>')
def odstrani_zaposlenega(id):
    cur.execute("UPDATE zaposleni SET trenutno_zaposlen = false WHERE id_zaposlenega = %s", (id, ))  
    redirect('{}zaposleni'.format(ROOT))

################################################
###### ko nimas pravic za doloceno stran #######
################################################

@get('/ni_pravic')
def ni_pravic():
    uporabnik = request.get_cookie('account', secret=skrivnost)
    registracija = request.get_cookie('registracija', secret=skrivnost)
    napaka = request.get_cookie('napaka', secret=skrivnost)
    status = request.get_cookie('dovoljenje', secret=skrivnost)
    return rtemplate('ni_pravic.html', uporabnik=uporabnik, registracija=registracija, napaka=napaka, status=status)

#########################################################
#### Prijava
#########################################################
def preveri_uporabnika(uporabnik, password):
    try:
        cur.execute("SELECT * FROM prijava WHERE uporabnik = %s", (uporabnik, ))
        uporabnik,geslo,dovoljenje,ime,priimek = cur.fetchone()
        salt = geslo[:64]
        geslo = geslo[64:]
        pwdhash = hashlib.pbkdf2_hmac('sha512', 
                                  password.encode('utf-8'), 
                                  salt.encode('ascii'), 
                                  100000)
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')
        if pwdhash == geslo:
            return [ime, dovoljenje]
    except:
        return False

def preveri_za_uporabnika(uporabnik):
    try:
        cur.execute("SELECT uporabnik FROM prijava WHERE uporabnik = %s", (uporabnik, ))
        #uporabnik = cur.fetchone([0])
        uporabnik = cur.fetchone()
        if uporabnik==None:
            return True
        else:
            return False
    except:
        return False

def ima_pravice():
    username = request.get_cookie("username", secret=skrivnost)
    if username:
        pravice = None
        try:
            cur.execute("SELECT status FROM prijava WHERE uporabnik LIKE %s", (str(username), ))
            pravice = cur.fetchone()
        except:
            pravice = None
        if pravice:
            return pravice[0]
    redirect('/ni_pravic')


def dodaj_uporabnika(ime, priimek, uporabnik, geslo, dovoljenje):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', geslo.encode('utf-8'), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    geslo = (salt + pwdhash).decode('ascii')
    cur.execute("INSERT INTO prijava (uporabnik, geslo, status, ime, priimek) VALUES (%s, %s, %s, %s, %s)", (uporabnik, geslo, dovoljenje,ime, priimek, ))


@get('/registracija')
def registracija():
    response.set_cookie('registracija', 'DA', secret=skrivnost)
    response.delete_cookie('napaka')
    redirect('{}avto/vsi'.format(ROOT))

@get('/za_prijavo')
def za_prijavo():
    response.delete_cookie('registracija')
    response.delete_cookie('napaka')
    redirect('{}avto/vsi'.format(ROOT))

@post('/registracija')
def registriraj():
    ime = request.forms.username1
    priimek = request.forms.username2
    username = request.forms.username
    geslo1 = request.forms.password1
    geslo2 = request.forms.password2
    if geslo1 == geslo2:
        preveri = preveri_za_uporabnika(username)
        if preveri:
            dodaj_uporabnika(ime, priimek, username, geslo1, 3)
            response.delete_cookie('registracija')
            napaka = 'Registracija upešna!'
            response.set_cookie('napaka', napaka, secret=skrivnost)
        else:
            napaka = 'Uporabniško ime je že zasedeno'
            response.set_cookie('napaka', napaka, secret=skrivnost)
    else:
        napaka = 'Gesli se ne ujemata'
        response.set_cookie('napaka', napaka, secret=skrivnost)
    redirect('{}avto/vsi'.format(ROOT))

    

@post('/prijava')
def prijava_post():
    username = request.forms.username
    password = request.forms.password
    preveri = preveri_uporabnika(username, password)
    if preveri:
        ime, status = preveri
        response.set_cookie('account', ime, secret=skrivnost)
        response.set_cookie('username', username, secret=skrivnost)
        response.delete_cookie('napaka')
        response.set_cookie('dovoljenje', status, secret=skrivnost)
    else:
        napaka = 'Uporabniško ime in geslo se ne ujemata - Namig: jan asd, ali pa se registriraj'
        response.set_cookie('napaka', napaka, secret=skrivnost)
    redirect('{}avto/vsi'.format(ROOT))

@get('/odjava')
def odjava():
    response.delete_cookie('account')
    response.delete_cookie('dovoljenje')
    response.delete_cookie('username')
    redirect('{}avto/vsi'.format(ROOT))

    

#Povezava na bazo

conn = psycopg2.connect(database=auth.dbname, host=auth.host, user=auth.user, password=auth.password, port=DB_PORT)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) #Onemogočimo transakcije #### Za enkrat ne rabimo
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


#Poženemo strežnik na podani vratih, npr. http://localhost:8080/
run(host='localhost', port=SERVER_PORT, reloader=RELOADER)