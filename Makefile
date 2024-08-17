.PHONY: help

help:
	@echo "HPChat Commands"
	@echo "---------------------"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

setup: ## Sets up the project from a fresh clone
	pip install -e .

chat: ## Starts a new chat session
	python -m hpchat.cli

ask: ## Builds the C++ library
	echo 'python -m hpchat.runtime --question="What is best in life?"'
	python -m hpchat.runtime --question="What is the significance of the 'Space Jockey'?"

clean: ## remove build artifacts
	rm -rf venv/
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	rm -fr notebooks/.ipynb_checkpoints/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
