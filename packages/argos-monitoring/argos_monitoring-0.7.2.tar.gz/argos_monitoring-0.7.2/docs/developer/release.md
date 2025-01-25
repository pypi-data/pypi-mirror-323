---
description: Once in a while, we release this package. Here is how.
---
# Releasing guide

Once in a while, we release this package. Here is how.

## Pre-requesites

You need to be in a working environment, with the dev dependencies installed. You can check it's the case by typing:

```bash
pip install -e ".[dev]"
```

You'll need to get an account on [PyPI](https://pypi.org), where the packages will be uploaded.

## The steps

Here is the quick version. If you need more details, some parts are explained in more details in the next sections.

```bash
# Be sure you are on the good branch
git checkout main

# Ensure the tests run correctly
make test

# Check static typing
make mypy

# Bump the version, according to semantic versionning
hatch version minor # or `hatch version major`, or `hatch version fix`

# Update the changelog
sed -e "s/## .Unreleased./&\n\n## $(hatch version)\n\nDate: $(date +%F)/" \
    -i CHANGELOG.md

# Commit the change
git add argos/__init__.py CHANGELOG.md
git commit -m "🏷 — Bump version ($(hatch version))"

# Create a tag on the git repository and push it
git tag "$(hatch version)" -m "$(hatch version)" &&
  git push --follow-tags

# Build the project
hatch build --clean

# Upload the project to PyPI
hatch publish
```

Aditionnaly, ensure it works well in a new environment.

## Bumping the version number

We follow semantic versionning conventions, and the version is specified in the `argos.__init__.py` file.
`hatch` provide commands to help with this:

```bash
hatch version minor
hatch version major
```

## Publishing

`hatch` will ask you for some credentials. Don't provide them the full credentials to you account, but instead you can [create a (scoped) token](https://pypi.org/manage/account/token/).

When asked for credentials, enter:

- `__token__` as the login
- the token as the value.

## Verifying it worked

Once published, you can test it works properly, by using pip, ideally in a new venv. Here's how:

```bash
python -m venv /tmp/argos
source /tmp/argos/bin/activate
pip install argos-monitoring
argos version # should output the proper version
```

## Using the test server

When running `hatch publish` the main PyPI instance will be used, which is not ideal for testing that it's doing what you want.

If you're still experimenting, you can use the [Test PyPI](https://test.pypi.org) server.

```bash
# Publishing on test PyPI
hatch publish -r test

# Installing from test PyPI
pip install --index-url https://test.pypi.org/simple/ argos-monitoring

```
