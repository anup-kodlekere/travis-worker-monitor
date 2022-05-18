from sshtunnel import SSHTunnelForwarder
import psycopg2
from datetime import date, time
import os

def parse_log_input():

    today = date.today()

    repo = 'anup-kodlekere/travis-sample-job'
    state = 'passed'

    with open("raw_db_input") as deploy:
        lines = deploy.readlines()
        lines = [line.rstrip() for line in lines]

        j1_started_at = lines[3].split('T', 1)[1][:-1]
        j2_started_at = lines[14].split('T', 1)[1][:-1]

        jid = [int(lines[1]), int(lines[12])]

        worker_name = [lines[6].split('.', 1)[1], lines[17].split('.', 1)[1]]

        job1_bootup = lines[9].split(':', 1)[1]
        job2_bootup = lines[20].split(':', 1)[1]

        j1_triggered, j2_triggered = 0, 0

        minute_j1 = job1_bootup.find('m')
        minute_j2 = job2_bootup.find('m')

        if minute_j1 != -1:
            m = int(job1_bootup[1:minute_j1])
            s = round(float(job1_bootup[minute_j1+1:-1]))
            j1_triggered = m * 60 + s
        else:
            j1s = round(float(job1_bootup[1:-1]))
            j1_triggered = j1s

        if minute_j2 != -1:
            m = int(job1_bootup[1:minute_j1])
            s = round(float(job2_bootup[minute_j1+1:-1]))
            j2_triggered = m * 60 + s
        else :
            j2s = round(float(job2_bootup[1:-1]))
            j2_triggered = j2s

        worker_bootup_time = [j1_triggered, j2_triggered]
        job_started_at = [j1_started_at, j2_started_at]

    deploy.close()

    return [jid, [repo,repo],  worker_name, worker_bootup_time, [state, state], [today, today], job_started_at]

def insert():
    tunnel = SSHTunnelForwarder(
        (os.environ['DB_IP'], 22),
        ssh_username='root',
        ssh_private_key='key',
        remote_bind_address=('localhost', 6443),
        local_bind_address=('localhost', 6443),
    )

    tunnel.start()
    #establishing the connection
    conn = psycopg2.connect(
        database="worker_usage", user='postgres', password='76482687', host=tunnel.local_bind_host, port=tunnel.local_bind_port
    )

    #Creating a cursor object using the cursor() method
    cursor = conn.cursor()

    tbl_row = parse_log_input()

    #orig = "INSERT INTO usage_details values(570271173,  'anup-kodlekere/check', 'lxd-ppc64le-travis-ci-production-worker1-com', 4, 'passed', '2022-05-16', '2022-05-16', '14:59:17');"
    #print(orig)

    for i in range(2):
        ids = str(tbl_row[0][i])
        rep = str(tbl_row[1][i])
        wrkr = str(tbl_row[2][i])
        bttm = str(tbl_row[3][i])
        st = str(tbl_row[4][i])
        dt = str(tbl_row[5][i])
        tm = str(tbl_row[6][i])

        query = "INSERT INTO usage_details values(" + ids + ", '" + rep + "', '" + wrkr + "'," + bttm + ", '" + st + "', '" + dt + "', '" + dt + "', '" + tm + "');"

        print(query)
        cursor.execute(query)
        conn.commit()

    #Executing an MYSQL function using the execute() method
    cursor.execute("select * from usage_details")

    # Fetch a single row using fetchone() method.
    data = cursor.fetchall()
    print(data)

    conn.close()
    tunnel.stop()

insert()