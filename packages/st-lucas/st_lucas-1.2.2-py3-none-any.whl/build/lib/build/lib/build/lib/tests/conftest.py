def pytest_addoption(parser):
    parser.addoption("--url", action="store", default=None)
