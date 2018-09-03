MODULES=src/backup-service

lint:
	flake8 $(MODULES)
	