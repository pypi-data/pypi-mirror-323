# repo-launcher

[![PyPI version](https://badge.fury.io/py/repo-launcher.svg)](https://badge.fury.io/py/repo-launcher)
[![Apache 2.0 License](https://img.shields.io/badge/License-APACHEv2-brightgreen.svg)](https://github.com/tschm/cradle/blob/master/LICENSE)
[![Coverage Status](https://coveralls.io/repos/github/tschm/cradle/badge.png?branch=main)](https://coveralls.io/github/tschm/cradle?branch=main)
[![ci](https://github.com/tschm/cradle/actions/workflows/ci.yml/badge.svg)](https://github.com/tschm/cradle/actions/workflows/ci.yml)

cradle is a command line tool to create repos based on a group of templates.

![Creating a repository from the command line](demo.png)

The tool is very similar to the popular
[Cookiecutter](https://cookiecutter.readthedocs.io/en/stable/#) project.

## Install gh

Please install GitHub's official command line tool [gh](https://github.com/cli/cli).
This tool is used to create GitHub repos from the command line.

Verify the existence of the tool and a valid SSH connection with

```bash
ssh -T git@github.com
gh --version
```

A new SSH connection could be established [here](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent).

## Install uv and uvx

uv is a modern, high-performance Python package manager and installer
written in Rust.
It serves as a drop-in replacement for traditional tools like pip and pipx.
For macOS and Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

For Windows follow the instructions [here](https://docs.astral.sh/uv/getting-started/installation/)

## Understanding uvx

uvx is a command provided by uv to run tools published as Python packages
without installing them permanently. It creates temporary,
isolated environments for these tools:

```bash
uvx repo-launcher
```

This command will:

* Resolve and install the repo-launcher package in a temporary environment.
* Execute the repo-launcher command.

**Note**: If you plan to use a tool frequently, consider installing
it permanently using uv:

```bash
uv tool install repo-launcher
````

Once the tool is permanently installed it is enough to start it with

```bash
repo-launcher
```

### Templates

You could create your own templates and standardize project structures
across your team or organization.
It's essentially a project scaffolding tool that helps maintain consistency
in Python projects.

We currently offer $4$ standard templates out of the box

* The document template
* The experiments template
* The package template
* The R template

#### Standard Templates

We follow the one template, one repository policy.
You are encouraged to create your own templates and we give $3$ examples that
may serve as inspiration

##### [The document template](https://github.com/tschm/paper)

The template supports the fast creation of repositories of LaTeX documents.
Out of the box you get

* curated pre-commit-hooks (e.g. for spelling)
* github ci/cd workflows
* Makefile
* Example *.tex and bib file.

##### [The experiments template](https://github.com/tschm/experiments)

Here we support the creation of notebooks without the ambition to release software.
The repo is not minimalistic but comes with a curated set of pre-commit hooks and
follows modern and established guidelines.

* uv support
* curated pre-commit-hooks
* DevContainer
* github ci/cd workflows
* Makefile
* marimo support

##### [The package template](https://github.com/tschm/package)

The package template is most useful when the final
goal is the release of software to a registry, e.g. pypi.
It features include

* uv support
* curated set of pre-commit hooks
* DevContainer
* Makefile
* github ci/cd workflows
* marimo support
* JupyterBook
* pdoc documentation

##### [The R template](https://github.com/tschm/cradle_r)

Here we expose R Studio in a devcontainer.

#### Proprietary templates

##### Creation

You can create your very own templates and we recommend to start with
forking the
[dedicated repo](https://github.com/tschm/template/blob/main/README.md)
for the job.

Templates rely on [Jinja](https://jinja.palletsprojects.com/en/stable/).
At the root level the repo needs a 'copier.yml' file and a 'template' folder.

Each template is tested using [act](https://github.com/nektos/act), e.g.
we render the project template and test the workflows of the created project.
This helps to avoid creating projects starting their life in a broken state.

##### Usage

We essentially expose the copier interface directly with
minor modifications, e.g. if the user is not submitting a source template
we offer to choose one of the standard templates.

Any cradle template could be used directly as the first 'template'
argument

```bash
uvx repo-launcher --template=git@github.com:tschm/paper.git
```

By default, Copier (and hence the repo-launcher) will copy from the last
release found in template Git tags, sorted as
[PEP 440](https://peps.python.org/pep-0440/).

## :warning: Private repositories

Using workflows in private repos will eat into your monthly GitHub bill.
You may want to restrict the workflow to operate only when merging on the main branch
while operating on a different branch or deactivate the flow.
