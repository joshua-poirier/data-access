.PHONY: init
init:
	pip install pipenv
	pipenv install --dev

.PHONY: lint
lint:
	pipenv run pylint data_access
	pipenv run python -m flake8 data_access

.PHONY: check_format
check_format:
	pipenv run python -m isort data_access --check-only
	pipenv run python -m black data_access --diff

.PHONY: check_type
check_type:
	pipenv run python -m mypy data_access

.PHONY: format
format:
	pipenv run python -m isort data_access
	pipenv run python -m black data_access --preview

.PHONY: test
test:
	pipenv run pytest tests
