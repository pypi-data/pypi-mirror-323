import unittest
from unittest.mock import patch
import pandas as pd

from grynn_pylib import utils


class TestUtils(unittest.TestCase):
    @patch("grynn_pylib.utils.subprocess.run")
    def test_compare(self, mock_subprocess_run):
        # Create sample data
        a = pd.Series([1, 2, 3], name="a")
        b = pd.Series([4, 5, 6], name="b")

        # Call the function
        utils.bcompare(a, b)

        # Assert subprocess.run was called
        self.assertTrue(mock_subprocess_run.called)
        args, kwargs = mock_subprocess_run.call_args
        self.assertIn("bcomp", args[0])


if __name__ == "__main__":
    unittest.main()
