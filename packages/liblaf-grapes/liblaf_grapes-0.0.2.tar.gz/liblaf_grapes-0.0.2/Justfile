default: gen-init lint


build:
    pyproject-build
    check-wheel-contents dist/*.whl
    twine check --strict dist/*

docs-assets:
    ./scripts/docs/download-assets.sh

docs-build: docs-assets
    mkdocs build

docs-serve: docs-assets
    mkdocs serve

docs-deploy: docs-assets
    mkdocs gh-deploy --force --no-history

gen-init:
    ./scripts/gen-init.sh

lint: lint-python lint-toml

lint-python:
    ruff check --fix

lint-toml:
    sort-toml .ruff.toml pyproject.toml

upgrade:
    pixi upgrade
    just
