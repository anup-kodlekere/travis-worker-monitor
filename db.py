import psycopg2
from datetime import date, time
import os

def insert(ids, rep, wrkr, qwt, bttm, dt, tm, st):

    #establishing the connection
    conn = psycopg2.connect(
        database="worker_usage", user='postgres', password='76482687', host='169.48.22.246', port='6443'
    )

    print("[LOG]: Connected to remote postgres db")
    #Creating a cursor object using the cursor() method
    cursor = conn.cursor()

    ids = str(ids)
    rep = str(rep)
    wrkr = str(wrkr)
    qwt = str(qwt)
    bttm = str(bttm)
    dt = str(dt)
    tm = str(tm)
    st = str(st)

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

def parse_log_input():

    with open("raw_db_input") as deploy:
        lines = deploy.readlines()
        lines = [line.rstrip() for line in lines]

        jid = int(lines[0])
        queue_wait_time = int(lines[1])
        job_state = lines[2]

        if job_state == 'queued':
            insert(jid, queue_wait_time, job_state, 'NULL', 'NULL', 'NULL', 'NULL', 'NULL')
        else:
            job_started_at = lines[3].split('T', 1)[1][:-1]
            worker_name = lines[6].split('.', 1)[1]
            job_bootup = lines[9].split(':', 1)[1]
            today = date.today()
            repo = 'anup-kodlekere/travis-sample-job'

            worker_bootup = 0
            minute_j1 = job_bootup.find('m')
            if minute_j1 != -1:
                m = int(job_bootup[1:minute_j1])
                s = round(float(job_bootup[minute_j1+1:-1]))
                worker_bootup = m * 60 + s
            else:
                j1s = round(float(job_bootup[1:-1]))
                worker_bootup = j1s

            insert(jid, repo, worker_name, queue_wait_time, worker_bootup, today, job_started_at, job_state)

    deploy.close()

parse_log_input()