.PHONY: test lint lint-check format format-check typecheck build

all: test lint format typecheck

test:
	$(info ****************** running tests ******************)
	uv run --all-groups pytest tests

lint-check:
	$(info ****************** running ruff check ******************)
	uv run --all-groups ruff check

lint:
	$(info ****************** running ruff check ******************)
	uv run --all-groups ruff check --fix

format:
	$(info ****************** formatting ******************)
	uv run --all-groups ruff format

format-check:
	$(info ****************** checking formatting ******************)
	uv run --all-groups ruff format --check

typecheck:
	$(info ****************** type checking ******************)
	uv run --all-groups ty check src/mcp_server/

build:
	$(info ****************** building ******************)
	uv build
