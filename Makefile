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
	@lsof -ti :8000 | xargs kill -9 2>/dev/null || true
	@echo "Open http://localhost:8000/preview/preview.html"
	python3 -m http.server 8000 --directory cards_view

preview-stop:
	@lsof -ti :8000 | xargs kill -9 2>/dev/null || true
	@echo "Stopped preview server on port 8000"

help:
	@echo "Available targets:"
	@echo "  formater      Format code with ruff"
	@echo "  linter        Run ruff linter"
	@echo "  lint          Format and lint code"
	@echo "  commit        Run pre-commit hooks"
	@echo "  preview       Start preview server"
	@echo "  preview-stop  Stop preview server"
