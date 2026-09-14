cd ~/ai-auction-experts/backend
pkill -f 'python app.py' || true
sleep 1
bash -c 'nohup ../venv/bin/python app.py > server.log 2>&1 < /dev/null & disown -a; sleep 3'
echo "Server started successfully."
