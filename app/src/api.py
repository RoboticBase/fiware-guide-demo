import os
from datetime import datetime
from logging import getLogger

from flask import request, jsonify, current_app
from flask.views import MethodView
from werkzeug.exceptions import BadRequest

from src.utils import const
from src.libs import orion


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
        orion.patch_attr(MOBILE_ROBOT_SERVICEPATH, MOBILE_ROBOT_TYPE, MOBILE_ROBOT_ID, data)

        return jsonify({'result': 'ok'})


class UpdateMobileRobotStateAPI(MethodView):
    NAME = 'update-mobilerobot-state'

    def post(self):
        data = request.data.decode('utf-8')
        logger.info(f'reqest data={data}')

        if data is None or len(data.strip()) == 0:
            raise BadRequest()

        r_mode = orion.parse_attr_value(data, 'r_mode')

        current_state = orion.get_attrs(MOBILE_ROBOT_SERVICEPATH,
                                        MOBILE_ROBOT_TYPE,
                                        MOBILE_ROBOT_ID, 'r_state')['r_state']['value']

        next_state = ' '
        if current_state in (' ', const.STATE_WAITING) and r_mode == const.MODE_NAVI:
            next_state = const.STATE_GUIDING
        elif current_state == const.STATE_GUIDING and r_mode == const.MODE_STANDBY:
            next_state = const.STATE_SUSPENDING
        elif current_state == const.STATE_SUSPENDING and r_mode == const.MODE_NAVI:
            next_state = const.STATE_RETURNING
        elif current_state == const.STATE_RETURNING and r_mode == const.MODE_STANDBY:
            next_state = const.STATE_WAITING
        else:
            logger.debug(f'ignore this process: r_mode={r_mode}, current_state={current_state}, ')
            return jsonify({'result': 'ignore'})

        now = datetime.utcnow()
        tpl = current_app.jinja_env.get_template('mobile_robot_update_state.json.j2')
        data = tpl.render({'value': next_state, 'datetime': now.strftime('%Y-%m-%dT%H:%M:%SZ')})
        orion.patch_attr(MOBILE_ROBOT_SERVICEPATH, MOBILE_ROBOT_TYPE, MOBILE_ROBOT_ID, data)
        logger.debug(f'update mobile robot state: r_mode={r_mode}, prev_state={current_state}, current_state={next_state}')
        return jsonify({'result': 'ok'})
