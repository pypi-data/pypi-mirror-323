import json
import logging
from httpx import Client, Response
import logging
import pytest
from conftest import BASE_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if BASE_URL is None:
    raise Exception('You should set variable BASE_URL to use core.tests')

class ApiClient(Client):
    """
    Расширение стандартного клиента httpx.
    """

    def __init__(self):
        super().__init__(base_url=BASE_URL)

    def request(self, method, url, **kwargs) -> Response:
        """
        расширение логики метода httpx request с добавлением логирования типа запроса и его url,
        логировать или нет задается в файле .env
        :param method: метод, который мы используем (POST, GET и.т.д)
        :param url: путь на домене, по которому отправляем запрос
        """
        logger.info(f'{method} {url}')
        
        return super().request(method, url, **kwargs)
    
    def log(self, obj, indent = 4):
        if is_json_serializable(obj):
            return logger.info(json.dumps(obj, indent=indent, ensure_ascii=False ))
        logger.info(obj)

def is_json_serializable(obj):
    try:
        json.dumps(obj)
        return True
    except (TypeError, OverflowError):
        return False
    

class TestApiClient:
    @pytest.fixture(scope='class')
    def client(self) -> ApiClient:
        return ApiClient()