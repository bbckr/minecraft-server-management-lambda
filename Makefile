MODULES=src/backup-service
VENV_NAME=venv
VENV_ACTIVATE=. $(VENV_NAME)/bin/activate
PYTHON=$(VENV_NAME)/bin/python2.7

pre:
	sudo apt-get -y install python3.5 python3-pip
	python3 -m pip install virtualenv
	make venv

venv: $(VENV_NAME)/bin/activate
$(VENV_NAME)/bin/activate: requirements-dev.txt
	test -d $(VENV_NAME) || virtualenv --no-wheel $(VENV_NAME)
	$(PYTHON) -m pip install -r requirements-dev.txt
	touch $(VENV_NAME)/bin/activate

lint:
	$(VENV_ACTIVATE)
	$(PYTHON) -m flake8 $(MODULES)
	