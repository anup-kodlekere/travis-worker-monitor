python3.8 script.py >> full_log.log
cat full_log.log | grep "Worker information" -A4 -B5 | tee deploy_info.log