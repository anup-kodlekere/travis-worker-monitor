python3.8 script.py >> log.log
cat log.log | grep "Worker information" -A4 -B5 > deploy_info.log 