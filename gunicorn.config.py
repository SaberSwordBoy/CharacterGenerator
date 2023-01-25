bind = "0.0.0.0:443"
workers = 3

access_logfile = "/root/AiGeneratedWebsite/logs/gunicorn.access.log"
error_logfile = "/root/AiGeneratedWebsite/logs/gunicorn.access.log"

certfile = '/etc/letsencrypt/live/sab3r.ml/fullchain.pem'
keyfile = '/etc/letsencrypt/live/sab3r.ml/privkey.pem'
