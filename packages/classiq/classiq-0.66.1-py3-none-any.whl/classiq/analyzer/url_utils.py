import urllib
from urllib.parse import urljoin

from classiq.interface.server import routes

import classiq

QUERY_START_MARK = "?"
VERSION_QUERY_PARAM = "version"


def client_ide_base_url() -> str:
    client = classiq._internals.client.client()
    return str(client.config.ide)


def versioned_url_params(circuit_version: str) -> str:
    return QUERY_START_MARK + urllib.parse.urlencode(
        {VERSION_QUERY_PARAM: circuit_version}
    )


def circuit_page_uri(circuit_id: str, circuit_version: str) -> str:
    url = urljoin(f"{routes.ANALYZER_CIRCUIT_PAGE}/", circuit_id)
    url += versioned_url_params(circuit_version=circuit_version)
    return url
