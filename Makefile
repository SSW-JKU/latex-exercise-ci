lint:
	pylint latex_build_action
	pylint tests
	pylint action_tests

typecheck:
	mypy -p latex_build_action
	mypy -p tests
	mypy -p action_tests

test:
	pytest -v tests

all: lint typecheck test
