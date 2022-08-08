import unittest
from util.util import run_notebook

class TestJupyterNotebook(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        notebook = 'netflow_ctu13_enriched.ipynb'
        notebook_loc = '../demos/cyber_netflow/'
        cls.nb, errors = run_notebook(notebook_loc + notebook)
        if errors != []:
            raise Exception(str(errors))

    def test_notebook_runs(self):
        # For now, just test the notebook runs.
        self.assertEqual(True, True)

if __name__ == '__main__':
    unittest.main()
