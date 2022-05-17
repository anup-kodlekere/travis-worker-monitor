python3.8 script.py
cat deploy_info.log | grep "Worker information" -A4 -B5 | tee db_input