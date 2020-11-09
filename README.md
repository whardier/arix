# ARIx
Asterisk ARI WebSocket/Callback Service

# Installation

After cloning simply run `poetry install` and then execute via `poetry run arix --help` to see all options.  You can use the form `arix` as long as the virtualenv associated with the poetry installation is activated.

Alternatively you can run `poetry build` and then run `pip install --user dist/arix-{versionnumber}.tar.gz`

# What's it do?

ARIx acts as an ARI Application WebSocket client and connects to an Asterisk ARI endpoint on behalf of another application.  When messages are received on the ARI WebSocket connection it is then forwarded to configurable HTTP callback as the JSON payload.

# Lots of room to grow

Eventually I would like to allow for templated callback paths, filtering, better username/password management.. and more than a single file ;)

