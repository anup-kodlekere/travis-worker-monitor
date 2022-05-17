python3.8 script.py >> deploy_info.log
cat deploy_info.log | grep "Worker information" -A4 -B5
