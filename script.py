import requests
import json
from time import sleep, time
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

print("Starting the polllll.....")

start = time()
flag = False

# wait for the job to finish since sometimes the logs aren't streamed back
# to travis-ui immediately

print("Waiting for all jobs to finish")
#state = requests.get("https://api.travis-ci.com/build/"+str(build_number), headers=headers).json()["state"]
state = "queued"
while(state != "passed" and state != "failed" and state != "errored"):
   sleep(30)
   state = requests.get("https://api.travis-ci.com/build/"+str(build_id), headers=headers).json()["state"]

if state=="errored":
   print("Travis build errored, cannot proceed further")
   exit()

flag = True
print("All jobs have finished")

build_started_at = requests.get("https://api.travis-ci.com/build/"+str(build_id), headers=headers).json()["started_at"]
build_finished_at = requests.get("https://api.travis-ci.com/build/"+str(build_id), headers=headers).json()["finished_at"]
build_duration = requests.get("https://api.travis-ci.com/build/"+str(build_id), headers=headers).json()["duration"]

# collect all job-ids in the build
response = requests.get("https://api.travis-ci.com/build/" + str(build_id) + "/jobs", headers=headers)
job_ids_jobj = response.json()["jobs"][0:]

jids = []
for obj in job_ids_jobj:
   jids.append(obj["id"])


# the worker startup data will be written to a file
# TODO: Find ways to connect jenkins to a db to store this data there
dep_file = open("deploy_info.log", "a")

for id in jids:
   endpoint = "https://api.travis-ci.com/job/" + str(id) + "/log"
   response = requests.get(endpoint, headers=log_headers)
   logs = response.text

   endpoint = "https://api.travis-ci.com/job/" + str(id)
   response = requests.get(endpoint, headers=headers)

   job_started_at = response.json()["started_at"]
   jobs_duration = response.json()["duration"]

   dep_file.write("Logs for Job \n")
   dep_file.write("{}".format(id))
   dep_file.write("\n")

   dep_file.write("Started At: \n")
   dep_file.write("{}".format(job_started_at))
   dep_file.write("\n")

   dep_file.write(logs)

dep_file.close()

# If build didn't start
if not flag:
   try:
      response = requests.post("https://api.travis-ci.com/build/" + str(build_id) + "/cancel", headers=headers)
      print("Time limit exceeded, Build Cancelled!")
   except Exception as e:
      print("Error while canceliing the build")
      print(e)
