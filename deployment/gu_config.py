import multiprocessing

# workers = multiprocessing.cpu_count() * 2 + 1
workers = 5
bind = 'unix:sisv.sock'
umask = 0o007
reload = True

accesslog = '/var/log/sisv/sisv.access.log'
errorlog = '/var/log/sisv/sisv.error.log'
capture_output = True
loglevel = "info"