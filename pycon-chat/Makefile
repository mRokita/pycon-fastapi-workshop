.PHONY: format
format:
	- poetry run isort -i pycon_chat/ tests/
	- poetry run black pycon_chat/ tests/

.PHONY: test
test:
	- poetry run pytest --cov pycon_chat/

.PHONY: lint
lint:
	- poetry run mypy --config-file pyproject.toml pycon_chat
	- poetry run flake8 --config flake8.ini $(shell pwd)/pycon_chat