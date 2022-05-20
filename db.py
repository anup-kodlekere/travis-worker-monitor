import psycopg2
from datetime import date

def insert(ids, rep, wrkr, qwt, bttm, dt, tm, st):

    #establishing the connection
    conn = psycopg2.connect(
        database="worker_usage", user='postgres', password='76482687', host='169.48.22.246', port='6443'
    )

    print("[LOG]: Connected to remote postgres db")
    #Creating a cursor object using the cursor() method
    cursor = conn.cursor()

    ids, rep = str(ids), str(rep)
    wrkr, qwt = str(wrkr), str(qwt)
    bttm, dt = str(bttm), str(dt)
    tm, st = str(tm), str(st)

    if st == 'passed':
        query = "INSERT INTO lxd_usage_details values(" + ids + ", '" + rep + "', '" + wrkr + "'," + qwt + "," + bttm + ", '" + dt + "', '" + dt + "', '" + tm + "', '" + st + "');"
    else:
        query = "INSERT INTO lxd_usage_details(job_id, repo, queue_wait_time_m, logged_after, logged_before, job_state) values(" + \
            ids + ", '" + rep + "', " + qwt + ", '" + dt + "', '" + dt + "', '" + st + "');"

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

def parse_log_input(jid, worker_name, job_bootup, job_started_at, queue_wait_time, job_state):

    today = date.today()
    repo = 'anup-kodlekere/travis-sample-job'

    if job_state == 'queued':
        insert(jid, repo, 'NULL', queue_wait_time, 'NULL', today, 'NULL', job_state)
    else:
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