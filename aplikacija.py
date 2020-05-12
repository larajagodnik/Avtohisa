#Uvoz bottla
from bottle import *



#Uvoz podatkov za povezavo
import auth_public as auth

#Uvoz psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import os

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
    cur.execute("SELECT * FROM avto")
    naslov = 'Vsi avti'
    #response.set_cookie("kaj", 'blalba', secret='skrivnost')
    uporabnik = request.get_cookie('account', secret=skrivnost)
    #print(uporabnik)
    return rtemplate('avto.html', avto=cur, naslov=naslov, uporabnik=uporabnik)
    #redirect('/avto/vsi') #To ni to kar sem hotu, ampak sedaj usaj prižge stran
    #return rtemplate('zacetna.html')

@get('/avto/<x:re:[a-z]+>')
def avto(x):
    if str(x) == 'novi':
        cur.execute("SELECT * FROM avto WHERE novi = 'true'")
        naslov = 'Novi avti'
    if str(x) == 'rabljeni':
        cur.execute("SELECT * FROM avto WHERE novi = 'false'")
        naslov = 'Rabljeni avti'
    if str(x) == 'vsi':
        redirect('/')
    uporabnik = request.get_cookie('account', secret=skrivnost)
    return rtemplate('avto.html', avto=cur, naslov=naslov, uporabnik=uporabnik)

@get('/avto_prijavljen')
def avto_prijavljen():
    cur.execute("SELECT * FROM avto")
    return rtemplate('avto_prijavljen.html', avto=cur)

@post('/avto_prijavljen/dodaj')
def dodaj_avto():
    Id = request.forms.id
    barva = request.forms.barva
    tip = request.forms.tip
    znamka = request.forms.znamka
    cena = request.forms.cena
    novi = request.forms.novi
    #try:
    sql = "INSERT INTO avto (id, barva, tip, znamka, cena, novi) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (Id, barva, tip, znamka, cena, novi)
    cur.execute(sql,val)
    # except Exception as ex:
    #     conn.rollback()
    #     return rtemplate('avto_prijavljen/dodaj.html', Id=id, barva=barva, tip=tip, znamka=znamka, cena=cena, novi=novi,
    #                     napaka='Dodajanje ni bilo uspešno: %s' % ex)   
    redirect('/avto_prijavljen')

@get('/manjse/<x:int>')
def razvrsti(x):
    cur.execute("SELECT * FROM avto WHERE cena < %s", x)
    return rtemplate('avto.html', avto=cur)
    
@get('/zaposleni')
def zaposleni():
    cur.execute("""
        SELECT * FROM zaposleni
        ORDER BY zaposleni.ime""")
    return rtemplate('zaposleni.html', zaposleni=cur)

#########################################################
#### Prijava
#########################################################

@post('/prijava')
def prijava_post():
    username = request.forms.username
    password = request.forms.password
    print(username, password)
    #if username is None or password is None:
    #
    #else:
    response.set_cookie('account', username, secret=skrivnost)
    redirect('/avto/vsi')


@get('/odjava')
def odjava():
    response.delete_cookie('account')
    redirect('/avto/vsi')

    

#Povezava na bazo
conn = psycopg2.connect(database=auth.dbname, host=auth.host, user=auth.user, password=auth.password, port=DB_PORT)
#conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)) #Onemogočimo transakcije #### Za enkrat ne rabimo
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


#Poženemo strežnik na podani vratih, npr. http://localhost:8080/
run(host='localhost', port=SERVER_PORT, reloader=RELOADER)