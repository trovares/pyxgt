# -*- coding: utf-8 -*- --------------------------------------------------===#
#
#  Copyright 2022-2024 Trovares Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#===----------------------------------------------------------------------===#

import os
import unittest
from util.util import run_notebook

class TestJupyterNotebook(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        real_path = os.path.realpath(__file__)
        dir_path = os.path.dirname(real_path)
        notebook = 'netflow_ctu13_enriched.ipynb'
        notebook_loc = dir_path + '/../demos/cyber_netflow/'
        cls.nb, errors = run_notebook(notebook_loc + notebook)
        if errors != []:
            raise Exception(str(errors))

    def test_notebook_runs(self):
        # For now, just test the notebook runs.
        self.assertEqual(True, True)

if __name__ == '__main__':
    unittest.main()
