#!/bin/bash
source venv/bin/activate
if ps up `cat /tmp/TCECache.pid` >/dev/null
then
	echo "Cache already running."
else
	python3 cache.py &
fi
gunicorn -w 2 tcefind:app
