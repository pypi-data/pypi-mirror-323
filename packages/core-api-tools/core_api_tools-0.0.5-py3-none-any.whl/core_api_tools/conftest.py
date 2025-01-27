from _pytest.config import Config
from pytest import Parser

BASE_URL = None

def pytest_addoption(parser: Parser):
    parser.addoption("--base_url", action="store", help="Ссылка на api")


def pytest_configure(config: Config):
    global BASE_URL
    BASE_URL = config.getoption("--base_url")
