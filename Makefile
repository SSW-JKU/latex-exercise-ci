lint:
	pylint latex_build_action
	pylint tests

typecheck:
	mypy -p latex_build_action
	mypy -p tests

test:
	pytest -v tests

all: lint typecheck test