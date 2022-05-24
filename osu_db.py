import psycopg2
import os, sys
from datetime import date, timedelta

def insert(hn, la, lb, tj, pj, fj, cj, ej):

    #establishing the connection
    conn = psycopg2.connect(
        database="worker_usage", user='postgres', password=os.environ['DB_PASS'], host=os.environ['DB_IP'], port='6443'
    )

    print("[LOG]: Connected to remote postgres db")
    #Creating a cursor object using the cursor() method
    cursor = conn.cursor()

    la, lb = str(la), str(lb)
    tj, pj = str(tj), str(pj)
    fj, cj = str(fj), str(cj)
    hn, ej = str(hn), str(ej)

    query = "INSERT INTO osu_usage_aggregate values(" + "'" + hn + "', '" + la + "', '" + lb + "', " + tj + ", " + pj + ", " + fj + ", " + cj + ", " + ej + ");"

    print(query)
    cursor.execute(query)
    conn.commit()

    conn.close()

    print("[LOG]: DB Connection closed")

def parse(deploy):

    usage = open(deploy, 'r')
    lines = usage.readlines()
    lines = [line.rstrip() for line in lines]

    hostname = lines[1].split(' ', 1)[0]
    lb = date.today()
    la = lb - timedelta(1)

    tj = int(lines[4].split(':', 1)[1][1:])
    pj = int(lines[5].split(':', 1)[1][1:])
    fj = int(lines[6].split(':', 1)[1][1:])
    cj = int(lines[7].split(':', 1)[1][1:])
    ej = int(lines[8].split(':', 1)[1][1:])
    print(hostname, tj, pj, fj, cj, ej)

    usage.close()

    insert(hostname, la, lb, tj, pj, fj, cj, ej)

parse(sys.argv[1])