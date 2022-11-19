# install:
# 	poetry check
# 	poetry lock
# 	poetry update
# 	poetry install

# test:
# 	poetry run pytest --disable-pytest-warnings

# build:
# 	make install
# 	make test
# 	poetry build

# all:
# 	make build
# 	poetry run python -m pip install --upgrade pip

install:
	@echo Installing Microservice
	poetry check
	poetry lock
	poetry update
	poetry install
	poetry run pre-commit install

activate:
	@echo Activating Microservice
	poetry run pre-commit autoupdate

test:
	echo Unit Testing Microservice
	poetry run pytest --disable-pytest-warnings

build:
	@echo Building Microservice
	make install
	make test
	poetry build

linters:
	@echo "Running Linters"
	poetry run pre-commit run --all-files
	poetry run flakeheaven lint

freeze:
	@echo "Freezing Requirements"
	poetry run pip freeze > requirements.txt
	poetry run python -m pip install --upgrade pip

all:
	make build
	make linters
	make pyc
	make freeze
