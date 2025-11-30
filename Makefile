.PHONY: test lint format format-check typecheck build

all: test lint format typecheck

test:
	$(info ****************** running tests ******************)
	uv run pytest tests

lint:
	$(info ****************** running pre-commit ******************)
	uv run pre-commit run -a
	$(info ****************** running ruff check ******************)
	uv run ruff check

format:
	$(info ****************** formatting ******************)
	uv run ruff format

format-check:
	$(info ****************** checking formatting ******************)
	uv run ruff format --check

typecheck:
	$(info ****************** type checking ******************)
	uv run ty check src/pdfitdown/

build:
	$(info ****************** building ******************)
	uv build