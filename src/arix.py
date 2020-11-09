# ┏━┓┏━┓╻╻ ╻ ┏━┓╻ ╻
# ┣━┫┣┳┛┃┏╋┛ ┣━┛┗┳┛
# ╹ ╹╹┗╸╹╹ ╹╹╹   ╹

# SPDX-License-Identifier: MIT

# Author: Shane R. Spencer <spencersr@gmail.com>

from sys import exc_info
from pathlib import Path
from typing import Optional, Union

import tornado.autoreload

from tornado.httpclient import AsyncHTTPClient, HTTPClientError
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.log import gen_log
from tornado.options import define, options, parse_command_line, parse_config_file
from tornado.websocket import websocket_connect
from tornado.escape import json_decode

APP_OPTIONS_GROUP = "Application Parameters"
ARI_OPTIONS_GROUP = "ARI Parameters"
CALLBACK_OPTIONS_GROUP = "Callback Parameters"

DEFAULT_DEBUG = False

DEFAULT_ARI_APPLICATION = "arix"
DEFAULT_ARI_USERNAME = "arix"
DEFAULT_ARI_PASSWORD = "arix"

DEFAULT_ARI_WEBSOCKET_URL = "ws://localhost:8088/ari/events?api_key=arix:arix&app=arix"
DEFAULT_ARI_PING_URL = (
    "http://arix:arix@localhost:8088/ari/events/user/arixPing?application=arix"
)

DEFAULT_CALLBACK_URL = "http://localhost:8080/arix/callback"

define("debug", type=bool, group=APP_OPTIONS_GROUP, default=DEFAULT_DEBUG)

define(
    name="config",
    type=Path,
    group=APP_OPTIONS_GROUP,
    callback=lambda path: parse_config_file(path, final=False),
)

define("ping-interval", default=0, group=APP_OPTIONS_GROUP)

define("websocket-url", group=ARI_OPTIONS_GROUP, default=DEFAULT_ARI_WEBSOCKET_URL)
define("ping-url", group=ARI_OPTIONS_GROUP, default=DEFAULT_ARI_PING_URL)

define("callback-url", group=CALLBACK_OPTIONS_GROUP, default=DEFAULT_CALLBACK_URL)


class AriClient:
    def __init__(self) -> None:
        self._running = False

    async def run(self) -> None:

        io_loop = IOLoop.current()

        try:
            websocket_client = await websocket_connect(options.websocket_url)
        except HTTPClientError:
            gen_log.error("Error connecting to ARI WebSocket", exc_info=True)
            io_loop.stop()
            return

        http_client = AsyncHTTPClient()

        self._running = True

        while self._running:

            message = await websocket_client.read_message()

            if not message:
                self._running = False

            message_obj = json_decode(message)

            if message_type := message_obj.get("type"):
                if message_timestamp := message_obj.get("timestamp"):
                    if message_eventname := message_obj.get("eventname"):
                        gen_log.debug(
                            f"{message_type}: {message_timestamp}: {message_eventname}"
                        )

            await http_client.fetch(options.callback_url, method="POST", body=message)


async def do_ping():
    http_client = AsyncHTTPClient()
    await http_client.fetch(options.ping_url, method="POST", body="")


def main() -> None:

    parse_command_line()

    io_loop = IOLoop.instance()

    if options.debug:

        tornado.autoreload.start()

        for option, value in sorted(options.as_dict().items()):
            gen_log.debug(f"Option: {option}: {value}")

    ari_client = AriClient()

    io_loop.add_callback(ari_client.run)

    if options.ping_interval:
        ping_periodic_callback = PeriodicCallback(do_ping, options.ping_interval * 1000)
        ping_periodic_callback.start()

    io_loop.start()


if __name__ == "__main__":
    main()
