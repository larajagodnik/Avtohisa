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
    return rtemplate('avto_vsi.html', avto=cur, naslov=naslov, uporabnik=uporabnik)
    #redirect('/avto/vsi') #To ni to kar sem hotu, ampak sedaj usaj prižge stran
    #return rtemplate('zacetna.html')

@get('/avto/<x:re:[a-z]+>')
def avto(x):
    uporabnik = request.get_cookie('account', secret=skrivnost)
    if str(x) == 'novi':
        cur.execute("SELECT * FROM novi INNER JOIN avto USING(id)")
        naslov = 'Novi avti'
        return rtemplate('avto_novi.html', avto=cur, naslov=naslov, uporabnik=uporabnik)
    if str(x) == 'rabljeni':
        cur.execute("""SELECT id_avto,st_kilometrov,servis,barva,tip,znamka,cena,leto_izdelave
                         FROM rabljeni INNER JOIN avto ON avto.id=rabljeni.id_avto""")
        naslov = 'Rabljeni avti'
        return rtemplate('avto_rabljeni.html', avto=cur, naslov=naslov, uporabnik=uporabnik)
    if str(x) == 'vsi':
        redirect('/')
        return rtemplate('avto_vsi.html', avto=cur, naslov=naslov, uporabnik=uporabnik)

@get('/avto_prijavljen')
def avto_prijavljen():
    #cur.execute("SELECT * FROM avto")
    cur.execute("SELECT avto.*, novi.pripravljen FROM avto LEFT JOIN novi ON avto.id = novi.id_avto")
    
    return rtemplate('avto_prijavljen.html', avto=cur)

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
    if request.forms.izberi_starost == False:    
        st_kilometrov = request.forms.st_kilometrov
        servis = request.forms.servis
        sql = "INSERT INTO rabljeni (id_avto, st_kilometrov, servis) VALUES (%s, %s, %s)"
        val = (Id_avta, st_kilometrov, servis)
        cur.execute(sql,val)
    elif request.forms.izberi_starost == True:   
        sql = "INSERT INTO novi VALUES (%s)"
        val = (Id_avta)
        cur.execute(sql,val)             
    redirect('/avto_prijavljen')

# prej morem se zbrisat avto iz rabljen oziroma novi
@post('/avto_prijavljen/brisi/<id>')
def brisi_avto(id):
    cur.execute("DELETE FROM avto WHERE id = %s", (id, ))
    redirect('/avto_prijavljen')

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