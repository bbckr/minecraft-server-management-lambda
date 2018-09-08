MODULES=src/backup
VENV_NAME=venv
VENV_ACTIVATE=. $(VENV_NAME)/bin/activate
PYTHON=$(VENV_NAME)/bin/python2.7
TERRAFORM_VERSION=0.11.8

pre:
	sudo apt-get -y install python3.5 python3-pip nodejs npm unzip
	wget https://releases.hashicorp.com/terraform/$(TERRAFORM_VERSION)/terraform_$(TERRAFORM_VERSION)_linux_amd64.zip
	sudo mv terraform /usr/local/bin/
	terraform init terraform/output/
	sudo npm install -g serverless
	serverless plugin install -n serverless-python-requirements
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

build:
	$(VENV_ACTIVATE)
	test -d terraform/output || mkdir terraform/output
	jinja2 terraform/main.j2 serverless.yml > terraform/output/main.tf

package:
	$(VENV_ACTIVATE)
	serverless package

plan:
	terraform plan terraform/output/

deploy:
	terraform apply --auto-approve terraform/output/
