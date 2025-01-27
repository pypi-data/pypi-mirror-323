from .mock_db import MockDB
#from mock import patch
from . import utils
import pytest

class TestUtils(MockDB):

    @pytest.mark.skip(reason="need to change to pytest conftest")
    def test_db_write(self):
        with self.mock_db_config:
            self.assertEqual(utils.db_write("""INSERT INTO `test_table` (`id`, `text`, `int`) VALUES ('3', 'test_text_3', 3)"""), True)
            self.assertEqual(utils.db_write("""INSERT INTO `test_table` (`id`, `text`, `int`) VALUES ('1', 'test_text_3', 3)"""), False)
            self.assertEqual(utils.db_write("""DELETE FROM `test_table` WHERE id='1' """), True)
            self.assertEqual(utils.db_write("""DELETE FROM `test_table` WHERE id='4' """), True)
