.PHONY: help clean test lint format check docs build env all
.DEFAULT_GOAL := help

help:  ## Display this help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} \
	/^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } \
	/^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) }' $(MAKEFILE_LIST)

##@ Primary Commands
all: clean check test docs build  ## Run all checks and tests

##@ Development
env:  ## Create the development environment (with all extras)
	pip install -e '.[dev,test,docs]'
	pip install tox tox-gh-actions

clean: ## Clean up build artifacts and caches
	tox -e clean

##@ Testing
test: ## Run tests
	tox

test-coverage: ## Run tests with coverage report
	tox -e coverage_report

##@ Code Quality
lint: ## Run linting
	tox -e lint

format: ## Format code and sort imports
	tox -e format

type: ## Run type checking
	tox -e type_check

check: lint type ## Run all code quality checks

##@ Documentation
docs: ## Build documentation
	mkdir -p docs/_build
	tox -e docs

docs-serve: ## Serve documentation locally
	python -m http.server --directory docs/_build/html

docs-clean: ## Clean documentation build
	tox -e clean

##@ Building
build: clean ## Build the package
	pip install build
	python -m build
