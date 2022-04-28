import sys, os

INTERP = "~/sidak-sv/env/bin/python"
if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)


from app import sisv as application