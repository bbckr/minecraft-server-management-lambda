MODULES=src/backup
VENV_NAME=venv
VENV_ACTIVATE=. $(VENV_NAME)/bin/activate
PYTHON=$(VENV_NAME)/bin/python2.7
TERRAFORM_VERSION=0.11.8

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
	npm list | grep serverless-python-requirements || sls plugin install -n serverless-python-requirements
	npm list | grep serverless-iam-roles-per-function || sls plugin install -n serverless-iam-roles-per-function
	serverless package

plan:
	terraform init terraform/output
	terraform plan terraform/output

deploy:
	terraform init terraform/output
	terraform apply --auto-approve terraform/output

destroy:
	terraform destroy --auto-approve terraform/output

all:
	make build
	make package
	make deploy
