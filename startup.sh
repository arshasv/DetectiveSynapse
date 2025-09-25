apt-get update
apt-get install -y uvicorn
pip install -r requirements.txt
gunicorn -w 4 -k uvicorn.workers.UvicornWorker synapse.src.synapse.api:app