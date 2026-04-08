.PHONY: install lint test

install:
	uv python install 3.12
	uv sync --python 3.12 --group dev

lint:
	uv run ruff format --check .
	uv run ruff check .

test:
	@uv run pytest || [ $$? -eq 5 ]
