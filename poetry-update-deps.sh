#!/bin/bash

python3.8 -m pip install --upgrade poetry

poetry add \
    appdirs@latest \
    tornado@latest \
    # ...

poetry add --dev black@latest --allow-prereleases
poetry add --dev isort==5.5.3

poetry add --dev \
    autoflake@latest \
    bandit@latest \
    flake8@latest \
    hypothesis@latest \
    mypy@latest \
    pytest@latest \
    # ...

