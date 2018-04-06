.PHONY: test setup clean clean-pyc clean-test build dist

TESTS=tests/unit

install:
	python -m pip install -e .

setup:
	python -m pip install -e .[dev]

clean: clean-pyc

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

documents:
	echo "Removing old Docs and regenerating"
	rm -f ./docs/source/*.rst
	sphinx-apidoc -f -e -M --implicit-namespaces -o docs/source/ eventmagic
	sphinx-apidoc -f -e -M --implicit-namespaces -o docs/source/ tests
	sphinx-build -c docs/ docs/source/ docs/build/

test:
	# Slack token does not need to be set to real value
	pytest -v $(TESTS) --duration=10

test-lint:
	flake8 --count

test-coverage:
	py.test --cov-report term-missing --cov-fail-under=85 --cov=eventmagic tests/

build:
	find ./dist/ -name '*.whl' -exec rm -f {} +
	find ./dist/ -name '*.tar.gz' -exec rm -f {} +
	python setup.py sdist
	python setup.py bdist_wheel

dist:
	twine upload dist/*
