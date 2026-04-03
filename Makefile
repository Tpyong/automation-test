.PHONY: install test lint format coverage clean docker security allure

install:
	pip install -r requirements.lock
	playwright install

install-dev:
	pip install -r requirements-dev.txt

update-deps:
	pip-compile requirements.in -o requirements.lock

update-dev-deps:
	pip-compile requirements-dev.in -o requirements-dev.lock

test:
	pytest -v

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

test-api:
	pytest tests/api/ -v

test-e2e:
	pytest tests/e2e/ -v

lint:
	pylint core/ tests/
	flake8 core/ tests/

format:
	black core/ tests/
	isort core/ tests/

mypy:
	mypy core/

coverage:
	pytest --cov=core --cov-report=html:reports/coverage-html --cov-fail-under=80

coverage-report:
	pytest --cov=core --cov-report=term-missing

security:
	python scripts/security_scan.py

docker-build:
	docker build -t automation-test:latest .

docker-test:
	docker-compose up test

docker-test-unit:
	docker-compose up test-unit

docker-test-integration:
	docker-compose up test-integration

docker-test-api:
	docker-compose up test-api

docker-test-e2e:
	docker-compose up test-e2e

docker-allure:
	docker-compose up allure

docker-clean:
	docker-compose down -v

docker-security:
	docker-compose up security-scan

allure:
	@echo "生成 Allure 报告..."
	python scripts/prepare_allure.py
	allure generate reports/allure-results -o reports/allure-report --clean
	allure open reports/allure-report

clean:
	rm -rf .pytest_cache __pycache__ allure-results allure-report reports/* logs/*
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
