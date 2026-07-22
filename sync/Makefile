.PHONY: formater linter lint

formater:
	@echo "Formatting code with ruff..."
	ruff format .

linter:
	@echo "Running ruff linter..."
	ruff check --fix

lint: linter formater
	@echo "Code formatted and linted with ruff"
