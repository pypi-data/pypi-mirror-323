.PHONY: patch minor major build clean publish

# Default version bump is patch
bump-version:
	python patch.py $(TYPE)

patch:
	$(MAKE) bump-version TYPE=patch

minor:
	$(MAKE) bump-version TYPE=minor

major:
	$(MAKE) bump-version TYPE=major

# Build the package
build: clean
	python -m build

# Clean build artifacts
clean:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/

# Publish to PyPI (you'll need credentials configured)
publish: build
	python -m twine upload dist/*

# Install development dependencies
dev-deps:
	pip install build twine 