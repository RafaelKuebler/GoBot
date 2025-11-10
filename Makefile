default: help

.PHONY: help
help: # Show help for each of the Makefile recipes.
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

.PHONY: setup
setup: # Setup the local development environment
	python3 -m venv .venv && \
	. .venv/bin/activate && \
	pip install --upgrade pip && \
	pip install -r requirements.txt && \
	pip install -r requirements-dev.txt && \
	pip install pre-commit && \
	pre-commit install && \
	pre-commit autoupdate

.PHONY: gui
gui: # Run gui locally
	@. .venv/bin/activate && \
	PYTHONPATH=. python gobot/gui.py

.PHONY: run
run: # Run bot locally (with Docker DynamoDB)
	docker-compose up dynamodb --detach && \
	. .venv/bin/activate && \
	PYTHONPATH=. python main.py ; \
	docker-compose down

.PHONY: test
test: # Run tests
	docker-compose up --detach && \
	. .venv/bin/activate && \
	PYTHONPATH=. python -m pytest tests ; \
	docker-compose down

.PHONY: deploy
deploy: # Deploy bot to AWS and set up webhook
	. .venv/bin/activate && \
	cd infrastructure && \
	PYTHONPATH=.. cdk deploy --outputs-file outputs.json && \
	GATEWAY_URL=$$(jq -r '.GoBotStack.ApiGatewayEndpoint' outputs.json) && \
	echo "Loading TOKEN from '.env' file..." && \
	. ../.env && \
	echo "Setting Telegram bot webhook to API gateway URL: $${GATEWAY_URL}..." && \
	curl -X POST https://api.telegram.org/bot$${TOKEN}/setWebhook?url=$${GATEWAY_URL} && \
	echo "\nDeployment SUCCESS"

.PHONY: pre-commit
pre-commit: # Run pre-commit hooks on all files
	@. .venv/bin/activate && \
	pre-commit run --all-files
