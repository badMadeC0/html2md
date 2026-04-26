from unittest.mock import MagicMock

class MyException(Exception): pass

mock_module = MagicMock()
mock_module.MyException = MyException

try:
    raise MyException("test")
except mock_module.MyException as e:
    print("Caught!", e)
