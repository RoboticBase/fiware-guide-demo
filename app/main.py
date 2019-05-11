#!/usr/bin/env python
import json
import os
import logging.config
from logging import getLogger

from flask import Flask

from src.utils import error_handler
from src.utils import const
from src.api import StartGuidanceAPI, UpdateMobileRobotStateAPI, UpdateMobileRobotPosAPI


try:
    with open(const.LOGGING_JSON, "r") as f:
        logging.config.dictConfig(json.load(f))
        if (const.LOG_LEVEL in os.environ and
                os.environ[const.LOG_LEVEL].upper() in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']):
            for handler in getLogger().handlers:
                if handler.get_name() in const.TARGET_HANDLERS:
                    handler.setLevel(getattr(logging, os.environ[const.LOG_LEVEL].upper()))
except FileNotFoundError:
    print(f'can not open {const.LOGGING_JSON}')
    pass


app = Flask(__name__)
app.config.from_pyfile(const.CONFIG_CFG)
app.add_url_rule('/notify/start-guidance/',
                 view_func=StartGuidanceAPI.as_view(StartGuidanceAPI.NAME))
app.add_url_rule('/notify/update-mobilerobot-state/',
                 view_func=UpdateMobileRobotStateAPI.as_view(UpdateMobileRobotStateAPI.NAME))
app.add_url_rule('/notify/update-mobilerobot-pos/',
                 view_func=UpdateMobileRobotPosAPI.as_view(UpdateMobileRobotPosAPI.NAME))
app.register_blueprint(error_handler.blueprint)


if __name__ == '__main__':
    default_port = app.config[const.DEFAULT_PORT]
    try:
        port = int(os.environ.get(const.LISTEN_PORT, str(default_port)))
        if port < 1 or 65535 < port:
            port = default_port
    except ValueError:
        port = default_port

    app.run(host="0.0.0.0", port=port)
