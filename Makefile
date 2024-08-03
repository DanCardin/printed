.PHONY: install test lint format
.DEFAULT_GOAL := help

VERSION=$(shell python -c 'from importlib import metadata; print(metadata.version("printed"))')

install:
	poetry install

test:
	coverage run -m pytest -vv src tests
	coverage report -i
	coverage xml

lint:
	ruff --fix src tests || exit 1
	ruff format -q src tests || exit 1
	mypy src tests || exit 1
	ruff format --check src tests

format:
	ruff src tests --fix
	ruff format src tests

.PHONY: docker-tag docker-build docker-watch docker-publish
docker-build:
	docker build \
	--target final \
	-t printed \
	.

docker-watch:
	docker run -it --rm -v $(PWD):/app printed

docker-tag:
	docker tag printed dancardin/printed:latest
	docker tag printed dancardin/printed:$(VERSION)

docker-publish: docker-build docker-tag
	docker push dancardin/printed:latest
	docker push dancardin/printed:$(VERSION)


.PHONY: run run-web init-css watch-css

run:
	printed watch

run-web:
	printed web
