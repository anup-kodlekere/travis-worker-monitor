python3.8 script.py
cat deploy_info.log | grep "Worker information" -A4 -B4 | tee raw_db_input