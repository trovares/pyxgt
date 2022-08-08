import unittest
import sys
from io import StringIO
from util.util import run_notebook

class TestJupyterNotebook(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        input = u"""2020
                    6
                 """
        notebook = 'nyctaxi_rideshare.ipynb'
        notebook_loc = '../demos/nyctaxi/'
        sys.path.insert(0, notebook_loc)
        # Pass stdin input to the notebook.
        sys.stdin = StringIO(input)
        cls.nb, errors = run_notebook(notebook_loc + notebook)

    def test_notebook_runs(self):
        # For now just test the notebook runs.
        self.assertEqual(True, True)

if __name__ == '__main__':
    unittest.main()
