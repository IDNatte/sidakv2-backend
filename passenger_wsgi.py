from app import app as application
import sys
import os

workdir = os.path.dirname(os.getcwd())
envdir = os.path.join(workdir, 'env/bin/python')


INTERP = envdir
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)
