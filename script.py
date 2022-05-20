from ast import parse
import requests
import json
from time import sleep
from datetime import datetime
import os

from db import parse_log_input

#TODO: Document how to get job.id and repository.id
# you can find your travis api token in your profile
TRAVIS_API_TOKEN=os.environ['TRAVIS_API_TOKEN']
GITHUB_USERNAME="anup-kodlekere"
# repo where the travis build is taking place
GITHUB_REPOSITORY_NAME="travis-sample-job"
REPOSITORY_ID=478089076

# Reqeust headers
headers={
  "Content-Type": "application/json",
  "Accept": "application/json",
  "Travis-API-Version": "3",
  "Authorization": "token " + TRAVIS_API_TOKEN
}

# plaintext logs specifically for getting logs
log_headers={
  "Accept": "text/plain",
  "Travis-API-Version": "3",
  "Authorization": "token " + TRAVIS_API_TOKEN
}

# Request body
body={
  "request": {
  "message": "Override the commit message: this is an api request",
  "branch":"main"
  }
}

def write_passed_log(job_id, job_queue_waiting_time):

   endpoint = "https://api.travis-ci.com/job/" + str(job_id) + "/log"
   content = requests.get(endpoint, headers=headers).json()["content"]

   hostname = content.splitlines()[2:6][0]
   hostname = hostname.split('.', 1)[1]

   startup_time = content.splitlines()[2:6][3]
   startup_time = startup_time.split(':', 1)[1]

   endpoint = "https://api.travis-ci.com/job/" + str(job_id)
   job_started_at = requests.get(endpoint, headers=headers).json()["started_at"]
   job_started_at = job_started_at.split('T', 1)[1]

   parse_log_input(job_id, hostname, startup_time, job_started_at, job_queue_waiting_time, 'passed')


def write_failure_log(job_id, job_queue_waiting_time):
   parse_log_input(job_id, 'NULL', 'NULL', 'NULL', 60, 'queued')

build_request_made = datetime.now()
print("[LOG]: Build request made at {}".format(build_request_made))
request_made_hour = build_request_made.hour
request_made_min = build_request_made.minute

# Make a build request
response = requests.post("https://api.travis-ci.com/repo/"+ GITHUB_USERNAME + "%2F" + GITHUB_REPOSITORY_NAME + "/requests", data=json.dumps(body), headers=headers)
data = response.json()

# Get the request number to get the build info
request_no = data["request"]["id"]


# Get the response body
# Make a request to get the build numbers wait some time to spin up the build
sleep(10)

response = requests.get("https://api.travis-ci.com/repo/" + str(REPOSITORY_ID) + "/request/"+ str(request_no),headers=headers)
sleep(1)
# Get the build number from the request number
build_id = response.json()["builds"][0]["id"]

# wait for the job to finish since sometimes the logs aren't streamed back
# to travis-ui immediately

print("[LOG]: Waiting for all jobs to finish")

orig = requests.get("https://api.travis-ci.com/build/"+str(build_id), headers=headers).json()
build_state = orig["state"]

job_id = orig["jobs"][0]["id"]
queue_wait_time = 0 # in minutes


while(build_state != "passed" and build_state != "failed" and build_state != "errored"):
   sleep(30)
   build_state = requests.get("https://api.travis-ci.com/build/"+str(build_id), headers=headers).json()["state"]

   # make a reuest to job and check if state is queued and time elsped is one hour,
   # if true then exit the loop and send NULL data to db
   job_state = requests.get("https://api.travis-ci.com/job/"+str(job_id), headers=headers).json()["state"]
   queue_wait_time = datetime.now()
   qwt_h = queue_wait_time.hour
   qwt_m = queue_wait_time.minute

   wait_time = (qwt_h - request_made_hour) * 60 + (qwt_m - request_made_min)
   queue_wait_time = wait_time

   if job_state == "queued" and wait_time >= 60:
      #TODO: Send a request to cancel the build
      print("[LOG]: Job waiting in queue for over an hour.")
      sleep(10)
      write_failure_log(job_id, 60)
      sleep(10)
      exit()


if build_state =="errored":
   print("Travis build errored, cannot proceed further")
   exit()

sleep(180)

print("[LOG]: Build has finished")

write_passed_log(job_id, queue_wait_time)

build_started_at = requests.get("https://api.travis-ci.com/build/"+str(build_id), headers=headers).json()["started_at"]
build_finished_at = requests.get("https://api.travis-ci.com/build/"+str(build_id), headers=headers).json()["finished_at"]
build_duration = requests.get("https://api.travis-ci.com/build/"+str(build_id), headers=headers).json()["duration"]