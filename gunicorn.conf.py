# Um unico processo com threads.
#
# Dois pontos dependem estado no processo: o contador do rate limit do login
# (Flask-Limiter, storage em memoria) e o SQLite. Com mais de um worker, cada
# um teria o proprio contador e o limite de 5 tentativas viraria 5 por worker,
# alem de multiplos escritores disputando o mesmo arquivo. Um processo com
# threads atende com folga uma oficina e mantem os dois controles corretos.
bind = "0.0.0.0:8080"
worker_class = "gthread"
workers = 1
threads = 4
accesslog = "-"
errorlog = "-"
timeout = 120
preload_app = True