import psycopg2
from datetime import date, time
import os

def parse_log_input():

    today = date.today()

    repo = 'anup-kodlekere/travis-sample-job'

    with open("raw_db_input") as deploy:
        lines = deploy.readlines()
        lines = [line.rstrip() for line in lines]

        jid = int(lines[0])
        queue_wait_time = int(lines[1])
        job_state = lines[2]
        job_started_at = lines[3].split('T', 1)[1][:-1]
        worker_name = lines[6].split('.', 1)[1]
        job_bootup = lines[9].split(':', 1)[1]

        worker_bootup = 0

        minute_j1 = job_bootup.find('m')

        if minute_j1 != -1:
            m = int(job_bootup[1:minute_j1])
            s = round(float(job_bootup[minute_j1+1:-1]))
            worker_bootup = m * 60 + s
        else:
            j1s = round(float(job_bootup[1:-1]))
            worker_bootup = j1s

    deploy.close()

    return jid, repo, worker_name, queue_wait_time, worker_bootup, today, job_started_at, job_state

def insert():

    #establishing the connection
    conn = psycopg2.connect(
        database="worker_usage", user='postgres', password='76482687', host='169.48.22.246', port='6443'
    )

    print("[LOG]: Connected to remote postgres db")
    #Creating a cursor object using the cursor() method
    cursor = conn.cursor()

    tbl_row = parse_log_input()

    ids = str(tbl_row[0])
    rep = str(tbl_row[1])
    wrkr = str(tbl_row[2])
    qwt = str(tbl_row[3])
    bttm = str(tbl_row[4])
    dt = str(tbl_row[5])
    tm = str(tbl_row[6])
    st = str(tbl_row[7])

    query = "INSERT INTO lxd_usage_details values(" + ids + ", '" + rep + "', '" + wrkr + "'," + qwt + "," + bttm + ", '" + dt + "', '" + dt + "', '" + tm + "', '" + st + "');"

    print(query)
    cursor.execute(query)
    conn.commit()

    #Executing an MYSQL function using the execute() method
    cursor.execute("select * from lxd_usage_details")

    # Fetch a single row using fetchone() method.
    data = cursor.fetchall()
    print(data)

    conn.close()

    print("[LOG]: DB Connection closed")

insert()