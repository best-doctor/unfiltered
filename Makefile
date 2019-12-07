check:
	flake8 src
	mypy src/pinhead
	PYTHONPATH=./src:$PYTHONPATH python -m pytest --cov=src --cov-report=xml -p no:warnings --disable-socket
