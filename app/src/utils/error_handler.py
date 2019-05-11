# -*- coding: utf-8 -*-

from flask import Blueprint, make_response, jsonify

blueprint = Blueprint('app', __name__)


@blueprint.app_errorhandler(400)
@blueprint.app_errorhandler(404)
@blueprint.app_errorhandler(405)
@blueprint.app_errorhandler(500)
def error_handler(error):
    name = error.name if hasattr(error, 'name') else 'Internal Server Error'
    code = error.code if hasattr(error, 'code') else 500
    return make_response(jsonify({'error': name}), code)
