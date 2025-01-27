# fernet-encrypt

A [Fernet](https://cryptography.io/en/latest/fernet/) encryption CLI tool

## Install

Use [pipx](https://pypa.github.io/pipx/) to install globally in an isolated python environment.

```bash
pipx install fernet-encrypt
```

## Usage

```
Usage: fernet-encrypt [OPTIONS] COMMAND [ARGS]...

Options:
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.

Commands:
  create-fernet-key
  decrypt-file
  encrypt-file
```

### create-fernet-key

Create a new fernet key to sign with. Keys will be stored in fernet-encrypt install location. When decrypting, all available keys will be tried until one succeeds or they are all exhasted.

```
Usage: fernet-encrypt create-fernet-key [OPTIONS]

Options:
  --help  Show this message and exit.
```

### encrypt-file

Encrypt provided `INPUT_FILE` with the newest fernet key (see `create-fernet-key`). The encrypted output will be directed to `OUTPUT_FILE` if provided. Otherwise output will be directed to stdout.

```
Usage: fernet-encrypt encrypt-file [OPTIONS] INPUT_FILE
                                   [OUTPUT_FILE]

Arguments:
  INPUT_FILE     [required]
  [OUTPUT_FILE]

Options:
  --help  Show this message and exit.
```

### decrypt-file

Decrypt provided `INPUT_FILE`. All existing fernet keys will be used for decryption until one succeeds or they are all exhasted. The decrypted output will be directed to `OUTPUT_FILE` if provided. Otherwise output will be directed to stdout.

```
fernet-encrypt decrypt-file [OPTIONS] INPUT_FILE
                            [OUTPUT_FILE]

Arguments:
  INPUT_FILE     [required]
  [OUTPUT_FILE]

Options:
  --help  Show this message and exit.
```

## Dev Prerequisites

-   python 3.12
-   [pipx](https://pypa.github.io/pipx/), an optional tool for prerequisite installs
-   [poetry](https://github.com/python-poetry/poetry) (install globally with `pipx install poetry`)
-   [flake8](https://github.com/PyCQA/flake8) (install globally with `pipx install flake8`)
    -   [flake8-bugbear](https://github.com/PyCQA/flake8-bugbear) extension (install with `pipx inject flake8 flake8-bugbear`)
    -   [flake8-naming](https://github.com/PyCQA/pep8-naming) extension (install with `pipx inject flake8 pep8-naming`)
-   [black](https://github.com/psf/black) (install globally with `pipx install black`)
-   [pre-commit](https://github.com/pre-commit/pre-commit) (install globally with `pipx install pre-commit`)
-   [just](https://github.com/casey/just), a Justfile command runner

### Windows

Justfile support for Windows requires [cygwin](https://www.cygwin.com/). Once installed your `PATH` will need to be updated to resolve `cygpath.exe` (probably `C:\cygwin64\bin`). Justfile will forward any targets with shebangs starting with `/` to cygwin for execution.

## Updating python version:

-   Update python version in `Dev Prerequisites` above
-   Update \[tool.poetry.dependencies\] section of `pyproject.toml`
-   Update pyupgrade hook in `.pre-commit-config.yaml`

## Justfile Targets

-   `install`: installs poetry dependencies and pre-commit git hooks
-   `update_boilerplate`: fetches and applies updates from the boilerplate remote
-   `test`: runs pytest with test coverage report

## Boilerplate

To support pulling updates from the [pyplate](git@github.com:tysonholub/pyplate.git) python boilerplate, add the `boilerplate` git remote:

```bash
git remote add boilerplate git@github.com:tysonholub/pyplate.git
```

Then moving forward, run `just update_boilerplate` to pull latest changes from the `boilerplate` remote. **NOTE**: you must keep the boilerplate remote history intact to successfully merge updates from the boilerplate remote.
