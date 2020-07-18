#Uvoz bottla
from bottle import *


#Uvoz podatkov za povezavo
import conf_baza as auth


#Uvoz psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import os
import binascii

# moras imet skupaj z reloader = true, da ne rabis usakic na novo
# poganjat pythona -- oboje izklopis ko oodajas aplikacijo profesorju
debug(True)

#skrivnost ='1'
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

    #dodamo se select po vseh, rabljenih, novih da ne rabimo 3 tabel tm met
    #izbor se ne dela

    cur.execute("SELECT DISTINCT leto_izdelave FROM avto ORDER BY leto_izdelave")
    leta = cur.fetchall()

    cur.execute("SELECT DISTINCT barva FROM avto")
    barve = cur.fetchall()

    cur.execute("SELECT DISTINCT tip FROM avto")
    tipi = cur.fetchall()

    cur.execute("SELECT DISTINCT znamka FROM avto")
    znamke = cur.fetchall()
   
    cur.execute("SELECT * FROM avto WHERE id NOT IN (SELECT DISTINCT id_avto FROM prodaja)")
    #leta = cur.execute("SELECT DISTINCT leto_izdelave from avto")
    naslov = 'Vsi avti'
    
    #response.set_cookie("kaj", 'blalba', secret='skrivnost')
    uporabnik = request.get_cookie('account', secret=skrivnost)
    registracija = request.get_cookie('registracija', secret=skrivnost)
    napaka = request.get_cookie('napaka', secret    =skrivnost)
    #print(uporabnik)
    return rtemplate('avto_vsi.html', avto=cur, naslov=naslov, uporabnik=uporabnik, registracija=registracija, napaka=napaka, leta=leta, barve=barve, tipi=tipi, znamke=znamke)
    #redirect('/avto/vsi') #To ni to kar sem hotu, ampak sedaj ussaj prižge stran
    #return rtemplate('zacetna.html')

@get('/avto/<x:re:[a-z]+>')
def avto(x):
    uporabnik = request.get_cookie('account', secret=skrivnost)
    registracija = request.get_cookie('registracija', secret=skrivnost)
    napaka = request.get_cookie('napaka', secret=skrivnost)
    if str(x) == 'novi':
        cur.execute("SELECT * FROM novi INNER JOIN avto ON novi.id_avto = avto.id")
        naslov = 'Novi avti'
        return rtemplate('avto_novi.html', avto=cur, naslov=naslov, uporabnik=uporabnik, registracija=registracija, napaka=napaka)
    if str(x) == 'rabljeni':
        cur.execute("""SELECT id_avto,st_kilometrov,servis,barva,tip,znamka,cena,leto_izdelave
                         FROM rabljeni INNER JOIN avto ON avto.id=rabljeni.id_avto""")
        naslov = 'Rabljeni avti'
        return rtemplate('avto_rabljeni.html', avto=cur, naslov=naslov, uporabnik=uporabnik, registracija=registracija, napaka=napaka)
    if str(x) == 'vsi':
        redirect('/')
        return rtemplate('avto_vsi.html', avto=cur, naslov=naslov, uporabnik=uporabnik, registracija=registracija, napaka=napaka)

@get('/avto_prijavljen')
def avto_prijavljen():
    #cur.execute("SELECT * FROM avto")
    
    cur.execute("SELECT avto.*, novi.pripravljen, rabljeni.servis,(SELECT id FROM prodaja WHERE prodaja.id_avto = avto.id) AS je_prodan FROM avto LEFT JOIN novi ON avto.id = novi.id_avto LEFT JOIN rabljeni ON avto.id = rabljeni.id_avto")
    uporabnik = request.get_cookie('account', secret=skrivnost)
    napaka = request.get_cookie('napaka', secret=skrivnost)
    registracija = request.get_cookie('registracija', secret=skrivnost)
    return rtemplate('avto_prijavljen.html', avto=cur, uporabnik=uporabnik, registracija=registracija, napaka=napaka)

# @post('/avto_prijavljen/filtriraj_po_barvah')
# def filtriraj_po_barvah():
#     cur.execute("SELECT avto.* FROM avto WHERE barva LIKE 'Rdeča'")
#     rows = cur.fetchall()
#     row_dict = [{k:v for k, v in record.items()} for record in rows]
    
#     return "{}".format(row_dict)

    
@post('/avto_prijavljen/dodaj')
def dodaj_avto():
    
    Id_avta = request.forms.Id_avta
    barva = request.forms.barva
    tip = request.forms.tip
    znamka = request.forms.znamka
    cena = request.forms.cena
    leto_izdelave = request.forms.leto_izdelave
    novi = request.forms.novi
    #try:
    sql = "INSERT INTO avto (id, barva, tip, znamka, cena, leto_izdelave, novi) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    val = (Id_avta, barva, tip, znamka, cena, leto_izdelave, novi)
    cur.execute(sql,val)
    # except Exception as ex:
    #     conn.rollback()
    #     return rtemplate('avto_prijavljen/dodaj.html', Id=id, barva=barva, tip=tip, znamka=znamka, cena=cena, novi=novi,
    #                     napaka='Dodajanje ni bilSo uspešno: %s' % ex)   
    #if request.forms.izberi_starost == False:  
    if novi == 'false':    
        st_kilometrov = request.forms.st_kilometrov
        servis = request.forms.servis
        sql = "INSERT INTO rabljeni (id_avto, st_kilometrov, servis) VALUES (%s, %s, %s)"
        val = (Id_avta, st_kilometrov, servis)
        cur.execute(sql,val)
    #elif request.forms.izberi_starost == True: 
    elif novi == 'true':   
        sql = "INSERT INTO novi VALUES (%s, %s)"
        val = (Id_avta, 'false')
        cur.execute(sql,val)             
    redirect('/avto_prijavljen')


#
# Ne dela pravilno! vedno da po vrsti id_avta notri namesto tistega k kliknes
#
@post('/avto_prijavljen/prodaja/<id>')
def prodaja(id):
    cur.execute("SELECT id_zaposlenega,ime FROM zaposleni WHERE tip_zaposlenega LIKE 'Prodajalec'")
    zaposleni = cur.fetchall()
    # spodnaj izberes vse (*), ko bomo dali ven tip zaposlenega
    cur.execute("SELECT id, id_avto, datum, nacin_placila, id_zaposlenega FROM prodaja")
    return rtemplate('prodaja.html', id=id, prodaja=cur,zaposleni=zaposleni)

# prej morem se zbrisat avto iz rabljen oziroma novi
@post('/avto_prijavljen/brisi')
def brisi_avto():
    
    id_avta = request.forms.id_avta
    datum = request.forms.datum
    nacin_placila = request.forms.nacin_placila
    id_zaposlenega = request.forms.Prodajalec
    sql = "INSERT INTO prodaja (id, id_avto, datum, nacin_placila, id_zaposlenega) VALUES (%s, %s, %s, %s, %s)"  
    val = (1, id_avta, datum, nacin_placila, id_zaposlenega)
    cur.execute(sql,val)

    cur.execute("DELETE FROM novi WHERE id_avto = %s", (id, ))
    cur.execute("DELETE FROM rabljeni WHERE id_avto = %s", (id, ))
    cur.execute("DELETE FROM avto WHERE id = %s", (id, ))
    redirect('/avto_prijavljen')

#
# Naceloma dela, preveri s SERIAL ce dela samodejno id-je
#
@post('/avto_prijavljen/dodaj_servis_info/<id>')
def dodaj_servis_info(id):
    cur.execute("SELECT id_zaposlenega, ime FROM zaposleni WHERE tip_zaposlenega LIKE 'Serviser'")
    zaposleni = cur.fetchall()
     # spodnaj izberes vse (*), ko bomo dali ven tip zaposlenega
    cur.execute("SELECT id, id_avto, datum, tip_servisa, id_zaposlenega FROM servis")
    return rtemplate('dodaj_servis_info.html', id=id, servis=cur, zaposleni=zaposleni)

@post('/avto_prijavljen/dodaj_servis')
def dodaj_servis():

    id_avta = request.forms.id_avta
    datum = request.forms.datum
    tip_servisa = request.forms.tip_servisa
    id_zaposlenega = request.forms.Serviser

    #try:
    sql = "INSERT INTO servis (id, id_avto, datum, tip_servisa, id_zaposlenega) VALUES (%s, %s, %s, %s, %s)"
    val = (2, id_avta, datum, tip_servisa, id_zaposlenega)
    cur.execute(sql,val)

    cur.execute("UPDATE rabljeni SET servis = True WHERE id_avto =  %s", (id_avta, ))

    # except Exception as ex:
    #     conn.rollback()
    #     return rtemplate('avto_prijavljen/dodaj.html', Id=id, barva=barva, tip=tip, znamka=znamka, cena=cena, novi=novi,
    #                     napaka='Dodajanje ni bilSo uspešno: %s' % ex)   
    #if request.forms.izberi_starost == False:        
    redirect('/avto_prijavljen')
   
@post('/avto_prijavljen/dodaj_pripravo_info/<id>')
def dodaj_pripravo_info(id):
    cur.execute("SELECT id_zaposlenega, ime FROM zaposleni WHERE tip_zaposlenega LIKE 'Serviser'")
    zaposleni = cur.fetchall()
    cur.execute("SELECT * FROM priprava")
    return rtemplate('dodaj_pripravo_info.html', id=id, priprava=cur, zaposleni=zaposleni)

@post('/avto_prijavljen/dodaj_pripravo')
def dodaj_pripravo():

    id_avta = request.forms.id_avta
    datum = request.forms.datum
    id_zaposlenega = request.forms.Serviser

    #try:
    sql = "INSERT INTO priprava (id, id_avto, id_zaposlenega) VALUES (%s, %s, %s)"
    val = (2, id_avta, id_zaposlenega)
    cur.execute(sql,val)

    cur.execute("UPDATE novi SET pripravljen = True WHERE id_avto =  %s", (id_avta, ))

    # except Exception as ex:
    #     conn.rollback()
    #     return rtemplate('avto_prijavljen/dodaj.html', Id=id, barva=barva, tip=tip, znamka=znamka, cena=cena, novi=novi,
    #                     napaka='Dodajanje ni bilSo uspešno: %s' % ex)   
    #if request.forms.izberi_starost == False:        
    redirect('/avto_prijavljen')
   
#
#
#

@get('/novi_zacasna')
def novi_zacasna():
    cur.execute("SELECT * FROM novi")
    return rtemplate('novi_zacasna.html', novi=cur)



@get('/manjse/<x:int>')
def razvrsti(x):    
    cur.execute("SELECT * FROM avto WHERE cena < %s", x)
    return rtemplate('avto_vsi.html', avto=cur)
    
@get('/zaposleni')
def zaposleni():
    cur.execute("""
        SELECT * FROM zaposleni
        ORDER BY zaposleni.ime""")
    return rtemplate('zaposleni.html', zaposleni=cur)


#########################################################
#### Prijava
#########################################################
def preveri_uporabnika(uporabnik, password):
    try:
        cur.execute("SELECT * FROM prijava WHERE uporabnik = %s", (uporabnik, ))
        uporabnik,geslo,dovoljenje = cur.fetchone()
        salt = geslo[:64]
        geslo = geslo[64:]
        pwdhash = hashlib.pbkdf2_hmac('sha512', 
                                  password.encode('utf-8'), 
                                  salt.encode('ascii'), 
                                  100000)
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')
        return pwdhash == geslo
    except:
        return False

def preveri_za_uporabnika(uporabnik):
    try:
        cur.execute("SELECT * FROM prijava WHERE uporabnik = %s", (uporabnik, ))
        uporabnik = cur.fetchone([0])
        print (uporabnik)
        if len(uporabnik)==0:
            return True
    except:
        return True

def dodaj_uporabnika(uporabnik, geslo, dovoljenje):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', geslo.encode('utf-8'), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    geslo = (salt + pwdhash).decode('ascii')
    cur.execute("INSERT INTO prijava (uporabnik, geslo, status) VALUES (%s, %s, %s)", (uporabnik, geslo, dovoljenje, ))


@get('/registracija')
def registracija():
    response.set_cookie('registracija', 'DA', secret=skrivnost)
    redirect('/avto/vsi')

@get('/za_prijavo')
def za_prijavo():
    response.delete_cookie('registracija')
    response.delete_cookie('napaka')
    redirect('/avto/vsi')

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
            dodaj_uporabnika(username, geslo1, 1)
            response.delete_cookie('registracija')
            response.delete_cookie('napaka')
            response.set_cookie('account', username, secret=skrivnost)
        else:
            napaka = 'Uporabniško ime je že zasedeno'
            response.set_cookie('napaka', napaka, secret=skrivnost)
    else:
        napaka = 'Gesli se ne ujemata'
        response.set_cookie('napaka', napaka, secret=skrivnost)
    redirect('/avto/vsi')

    

@post('/prijava')
def prijava_post():
    username = request.forms.username
    password = request.forms.password
    print(username, password)
    preverjam = preveri_uporabnika(username, password)
    #if preverjam:
    response.set_cookie('account', username, secret=skrivnost)
    response.delete_cookie('napaka')
    #else:
    #    napaka = 'Uporabniško ime in geslo se ne ujemata - Namig: jan asd, ali pa se registriraj'
    #    response.set_cookie('napaka', napaka, secret=skrivnost)
    #response.set_cookie('dovoljenje', preverjam, secret=skrivnost)
    redirect('/avto/vsi')

@get('/odjava')
def odjava():
    response.delete_cookie('account')
    response.delete_cookie('dovoljenje')
    redirect('/avto/vsi')

    

#Povezava na bazo

conn = psycopg2.connect(database=auth.dbname, host=auth.host, user=auth.user, password=auth.password, port=DB_PORT)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) #Onemogočimo transakcije #### Za enkrat ne rabimo
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


#Poženemo strežnik na podani vratih, npr. http://localhost:8080/
run(host='localhost', port=SERVER_PORT, reloader=RELOADER)