import os
import json
from logging import getLogger
from urllib.parse import urljoin

import requests

from src.utils import const

logger = getLogger(__name__)

ORION_PATH = '/v2/entities/<<ID>>/attrs?type=<<TYPE>>'
FIWARE_SERVICE = os.environ.get(const.FIWARE_SERVICE, '')
ORION_ENDPOINT = os.environ.get(const.ORION_ENDPOINT, const.DEFAULT_ORION_ENDPOINT)
ORION_PATH_TPL = urljoin(ORION_ENDPOINT, ORION_PATH)


class OrionError(Exception):
    def __init__(self, message, name, desc, code=500):
        super().__init__(message)
        self.name = name
        self.desc = desc
        self.code = code


def patch_attr(fiware_servicepath, entity_type, entity_id, data):
    headers = {
        'Content-Type': 'application/json',
        'Fiware-Service': FIWARE_SERVICE,
    }
    headers['Fiware-Servicepath'] = fiware_servicepath

    url = ORION_PATH_TPL.replace('<<ID>>', entity_id).replace('<<TYPE>>', entity_type)

    response = requests.patch(url, headers=headers, data=data)
    if 200 <= response.status_code and response.status_code < 300:
        logger.debug(f'patch attr, url={url}, fiware_servicepath={fiware_servicepath}, data={data}')
    else:
        raise OrionError(response.text, f'OrionError({response.reason})', response.json()['description'])


def get_attrs(fiware_servicepath, entity_type, entity_id, attrs):
    headers = {
        'Fiware-Service': FIWARE_SERVICE,
    }
    headers['Fiware-Servicepath'] = fiware_servicepath

    url = ORION_PATH_TPL.replace('<<ID>>', entity_id).replace('<<TYPE>>', entity_type)

    params = {
        'attrs': attrs
    }
    response = requests.get(url, headers=headers, params=params)
    if 200 <= response.status_code and response.status_code < 300:
        try:
            data = response.json()
            logger.debug(f'get attrs, url={url}, fiware_servicepath={fiware_servicepath}, data={data}')
            return data
        except json.JSONDecodeError as e:
            raise OrionError(str(e), 'OrionError(JSONDecodeError)', str(e))
    else:
        raise OrionError(response.text, f'OrionError({response.reason})', response.json()['description'])


def parse_attr_value(data, attr):
    data = __extract_attr_from_NGSI(data, attr)
    return data['value']


def __extract_attr_from_NGSI(data, attr):
    for data in __extract_data_from_NGSI(data):
        if (isinstance(data, dict) and attr in data and
                isinstance(data[attr], dict) and 'value' in data[attr]):
            return data[attr]

    raise OrionError('AttrDoesNotExist', 'OrionError(AttrDoesNotExist)', f'this attribute ({attr}) does not exist')


def __extract_data_from_NGSI(data):
    if data is None or len(data.strip()) == 0:
        raise OrionError('NSGIError', 'OrionError(NGSIError)', f'empty data')

    try:
        payload = json.loads(data)
    except json.decoder.JSONDecodeError:
        raise OrionError('NSGIError', 'OrionError(NGSIError)', f'json parse error')

    if (payload is None or not isinstance(payload, dict) or
            'data' not in payload or not isinstance(payload['data'], list)):
        raise OrionError('NSGIError', 'OrionError(NGSIError)', f'invalid NGSI format')
    return payload['data']
