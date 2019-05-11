import os
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
    def __init__(self, message, name, code, desc):
        super().__init__(message)
        self.name = name
        self.code = code
        self.desc = desc


def send_cmd(fiware_servicepath, entity_type, entity_id, data):
    headers = {
        'Content-Type': 'application/json',
        'Fiware-Service': FIWARE_SERVICE,
    }
    headers['Fiware-Servicepath'] = fiware_servicepath

    url = ORION_PATH_TPL.replace('<<ID>>', entity_id).replace('<<TYPE>>', entity_type)

    response = requests.patch(url, headers=headers, data=data)
    if 200 <= response.status_code and response.status_code < 300:
        logger.debug(f'sent data to orion, url={url}, fiware_servicepath={fiware_servicepath}, data={data}')
    else:
        raise OrionError(response.text, f'OrionError({response.reason})', 500, response.json()['description'])
