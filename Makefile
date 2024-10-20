.PHONY: help

help:
	@echo "HPChat Commands"
	@echo "---------------------"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

server: ## Starts the webserver
	python hpchat/server.py

process: ## Preprocesses the video data in videos and the sermon listing
	python hpchat/preprocess.py

setup: ## Sets up the project from a fresh clone
	pip install -e .

chat: ## Starts a new chat session
	python -m hpchat.cli

transcribe: ## Transcribes all videos
	python transcribe.py
	
clean: ## remove build artifacts
	find output -type f ! -name "*.txt" -delete
