import os
from logging import getLogger

from flask import request, jsonify, current_app
from flask.views import MethodView
from werkzeug.exceptions import BadRequest

from src.utils import const
from src.libs.orion import send_cmd


logger = getLogger(__name__)

MOBILE_ROBOT_SERVICEPATH = os.environ.get(const.MOBILE_ROBOT_SERVICEPATH, '')
MOBILE_ROBOT_TYPE = os.environ.get(const.MOBILE_ROBOT_TYPE, '')
MOBILE_ROBOT_ID = os.environ.get(const.MOBILE_ROBOT_ID, '')


class StartGuidanceAPI(MethodView):
    NAME = 'start-guidance'

    def post(self):
        data = request.data.decode('utf-8')
        logger.info(f'reqest data={data}')

        if data is None or len(data.strip()) == 0:
            raise BadRequest()

        tpl = current_app.jinja_env.get_template('mobile_robot_move_cmd.json.j2')
        data = tpl.render({'value': 'up'})
        send_cmd(MOBILE_ROBOT_SERVICEPATH, MOBILE_ROBOT_TYPE, MOBILE_ROBOT_ID, data)
        result = {'result': 'ok', 'requested': False}

        return jsonify(result)
