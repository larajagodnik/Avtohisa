import psycopg2

from conf_baza import *

conn_string = "host='{0}' dbname='{1}' user='{2}' password='{3}'".format(host, dbname, user, password)

with psycopg2.connect(conn_string) as con:
    cur = con.cursor()
    #cur.execute("INSERT INTO avto VALUES(101, 'rumena', 'karavan', 'peguot', 200, TRUE)")
    #cur.execute("INSERT INTO avto VALUES(102, 'rumena', 'karavan', 'peguot', 200, True)")
    #cur.execute("INSERT INTO avto VALUES(103, 'rumena', 'karavan', 'peguot', 200, true)")
    #cur.execute("INSERT INTO avto VALUES(104, 'rumena', 'karavan', 'peguot', 200, true)")
    #cur.execute("INSERT INTO avto VALUES(1, 'rumena', 'karavan', 'ford', 200, false)")
    #cur.execute("INSERT INTO avto VALUES(20, 'rumena', 'karavan', 'ford', 200.2, false)")
    #con.commit()