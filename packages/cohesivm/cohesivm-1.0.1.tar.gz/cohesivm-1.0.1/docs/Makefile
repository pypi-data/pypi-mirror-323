# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Target for generating the README.md
readme:
	python "$(SOURCEDIR)/generate_readme.py" "$(SOURCEDIR)/_templates/readme.md" "../README.md"

# Target for generating the CONTRIBUTING.md
contributing:
    python "$(SOURCEDIR)/generate_readme.py" "$(SOURCEDIR)/getting_involved/contributing.md" "../CONTRIBUTING.md"

# Custom target for building HTML documentation and generating the README
all: html readme contributing

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
