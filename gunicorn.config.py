bind = "0.0.0.0:443"
workers = 3

errorlog = '/root/AiGeneratedWebsite/logs/gunicorn.log'

certfile = '/etc/letsencrypt/live/sab3r.ml/fullchain.pem'
keyfile = '/etc/letsencrypt/live/sab3r.ml/privkey.pem'
