formater:
	@echo "Formatting code with ruff..."
	ruff format .

linter:
	@echo "Running ruff linter..."
	ruff check --fix

lint: linter formater
	@echo "Code formatted and linted with ruff"

commit:
	pre-commit run --all-files

preview:  # to correctly stop it: Ctrl+C (not command + C)
	@echo "Open http://localhost:8000/preview/preview.html"
	python3 -m http.server 8000 --directory cards_view
