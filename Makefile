## vim: foldmarker={{{,}}} foldlevel=0 foldmethod=marker spell:

## Variables {{{
PIP_OPTIONS = --user
RELEASE_OPENPGP_FINGERPRINT ?= C505B5C93B0DB3D338A1B6005FE92C12EE88E1F0
RELEASE_OPENPGP_CMD ?= $(shell git config --get gpg.program || echo 'gpg')
PYPI_REPO ?= pypi
NOSETESTS ?= $(shell command -v nosetests3 nosetests | head -n 1)
NOSE2 ?= $(shell command -v nose2-3 nose2-3.4 | head -n 1)
SHELL := /bin/bash
PYTHON_VERSION := $(shell python -c "import sys;t='{v[0]}.{v[1]}'.format(v=list(sys.version_info[:2]));sys.stdout.write(t)")
## }}}

.PHONY: FORCE_MAKE

.PHONY: default
default: list

## list targets (help) {{{
.PHONY: list
# https://stackoverflow.com/a/26339924/2239985
list:
	@echo "This Makefile has the following targets:"
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^(:?[^[:alnum:]]|FORCE_MAKE$$)' -e '^$@$$' | sed 's/^/    /'
## }}}

## Git hooks {{{
.PHONY: install-pre-commit-hook
install-pre-commit-hook: ./tests/hooks/pre-commit
	ln -srf "$<" "$(shell git rev-parse --git-dir)/hooks"

.PHONY: run-pre-commit-hook
run-pre-commit-hook: ./tests/hooks/pre-commit
	"$<"

.PHONY: remove-pre-commit-hook
remove-pre-commit-hook:
	rm -f "$(shell git rev-parse --git-dir)/hooks/pre-commit"
## }}}

## check {{{
.PHONY: check-quick
check-quick: check-unit-tests check-docs check-lint-quick

.PHONY: check
check: check-unit-tests-with-coverage check-docs check-lint

.PHONY: check-tox
check-tox:
	tox

.PHONY: check-docs
check-docs:
	$(MAKE) "docs" > /dev/null

.PHONY: check-lint-quick
check-lint-quick: check-flake8 check-travis.yml check-gitlab-ci.yml

.PHONY: check-lint
check-lint: check-lint-quick check-pylint

.PHONY: check-flake8
check-flake8:
	flake8 .

.PHONY: check-pylint
check-pylint: fdeunlock/
	if [[ "$(PYTHON_VERSION)" == "3.6" ]]; then \
		echo "Skip test as pylint had issues with this version"; \
	else \
		pylint "$<" --reports=n --rcfile .pylintrc --disable=missing-docstring,protected-access,too-many-instance-attributes; \
	fi

.PHONY: check-pylint-tests
check-pylint-tests: tests/
	pylint "$<" --reports=n --rcfile .pylintrc --disable=protected-access,missing-docstring,invalid-name,too-many-public-methods,too-many-lines

.PHONY: check-radon
check-radon: fdeunlock/
	radon cc "$<" --total-average

.PHONY: check-travis.yml
check-travis.yml: .travis.yml
	yamllint "$<"

.PHONY: check-gitlab-ci.yml
check-gitlab-ci.yml: .gitlab-ci.yml
	yamllint "$<"

.PHONY: check-nose
check-nose:
	$(NOSETESTS)

.PHONY: check-unit-tests
check-unit-tests: check-nose

.PHONY: check-unit-tests-with-coverage
check-unit-tests-with-coverage:
	$(NOSETESTS) --with-coverage --cover-package fdeunlock --cover-branches --cover-erase --cover-html --cover-html-dir tests/coverage-report

# Does not work on Travis, different versions. Using check-nose for now.
.PHONY: check-nose2
check-nose2:
	$(NOSE2) --start-dir tests

.PHONY: check-fixmes
check-fixmes:
	ag '(:?[F]IXME|[T]ODO|[n]ottest)' --ignore 'fdeunlock/defaults.py' && exit 1 || :

## }}}

## development {{{

.PHONY: clean
clean:
	$(MAKE) -C "docs" clean
	find . -name '*.py[co]' -delete
	rm -rf *.egg *.egg-info

.PHONY: distclean
distclean: clean
	rm -rf build dist dist_signed .coverage

.PHONY: build
build: setup.py
	"./$<" bdist_wheel sdist

.PHONY: install-dev
install-dev: setup.py
	pip3 install "$(PIP_OPTIONS)" --editable . --no-deps

.PHONY: docs
docs:
	if [[ "$(PYTHON_VERSION)" == "3.3" ]]; then \
		echo "Skip test as sphinx has dropped support for this version"; \
	else \
		$(MAKE) -C "docs" html; \
	fi

.PHONY: release-versionbump
release-versionbump: fdeunlock/_meta.py CHANGES.rst
	editor $?
	sh -c 'git commit --all --message="Release version $$(./setup.py --version)"'

.PHONY: release-sign
release-sign: distclean build
	rm -rf dist_signed
	mv dist dist_signed
	find dist_signed -type f -regextype posix-extended -regex '^.*(:?\.(:?tar\.gz|whl))$$' -print0 \
		| xargs --null --max-args=1 -I '{}' $(RELEASE_OPENPGP_CMD) --local-user "$(RELEASE_OPENPGP_FINGERPRINT)" --detach-sign --armor --output '{}.asc' '{}'
	git tag --sign --local-user "$(RELEASE_OPENPGP_FINGERPRINT)" --message "Released version $(shell ./setup.py --version)" "v$(shell ./setup.py --version)"

.PHONY: release-prepare
release-prepare: release-versionbump release-sign

.PHONY: pypi-register
pypi-register: build
	twine register -r "$(PYPI_REPO)" "$(shell find dist -type f -name '*.whl' | sort | head -n 1)"

.PHONY: pypi-register
pypi-upload: build
	twine upload -r "$(PYPI_REPO)" dist_signed/*

.PHONY: git-push
git-push:
	git push gitlab --follow-tags
	git push github --follow-tags

.PHONY: release-publish
release-publish: git-push pypi-register pypi-upload

.PHONY: release
release: release-prepare release-publish

## }}}
