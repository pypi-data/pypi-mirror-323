PYTHON_VERSION = 3.10

prepare:
	uvx --python $(PYTHON_VERSION) pip install build
	uvx --python $(PYTHON_VERSION) pip install twine

build: prepare
	uvx --python $(PYTHON_VERSION) --from build pyproject-build

upload:	clean build
	uvx --python $(PYTHON_VERSION) twine upload dist/* --verbose

install::
	uvx --python $(PYTHON_VERSION) pip install --upgrade hc-mcp-jira

all: clean prepare build upload install

clean::
	rm -rf dist
	rm -rf src/hc_mcp_jira.egg-info
	rm -rf src/hc_mcp_jira/__pycache__
	rm -rf .venv

help:
	@echo make targets:
	@grep '^[^#[:space:]].*:' Makefile | cut -f1 -d:
