import requests
import json
from time import sleep
from datetime import datetime
import os

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
   dep_file = open("deploy_info.log", "a")
   endpoint = "https://api.travis-ci.com/job/" + str(job_id) + "/log.txt"
   response = requests.get(endpoint, headers=log_headers)
   logs = response.text

   endpoint = "https://api.travis-ci.com/job/" + str(job_id)
   response = requests.get(endpoint, headers=headers)

   job_started_at = response.json()["started_at"]

   dep_file.write("{}".format(job_id))
   dep_file.write("\n")

   dep_file.write("{}".format(job_queue_waiting_time))
   dep_file.write("\n")

   dep_file.write("passed")
   dep_file.write("\n")

   dep_file.write("{}".format(job_started_at))
   dep_file.write("\n")
   
   dep_file.write(logs)
   dep_file.write("\n")

   print("[LOG]: {}".format(job_id))
   print("[LOG]: {}".format(job_queue_waiting_time))
   print("[LOG]: {}".format(job_started_at))
   print("[LOG]: passed")
   print("[LOG]: {}".format(logs))

   dep_file.close()

def write_failure_log(job_id, job_queue_waiting_time):
   dep_file = open("deploy_info.log", "a")

   dep_file.write("{}".format(job_id))
   dep_file.write("\n")

   dep_file.write("{}".format(job_queue_waiting_time))
   dep_file.write("\n")

   dep_file.write("failed")
   
   for _ in range(6):
      dep_file.write('NULL')
      dep_file.write('\n')

   dep_file.close()

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

print("Waiting for all jobs to finish")

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