import nbformat
import os
from nbconvert.preprocessors import ExecutePreprocessor
from tempfile import TemporaryDirectory

# This function is from https://www.blog.pythonlibrary.org/2018/10/16/testing-jupyter-notebooks/:
# and licensed under the wxWindows Library Licence.
def run_notebook(notebook_path):
    nb_name, _ = os.path.splitext(os.path.basename(notebook_path))
    dirname = os.path.dirname(notebook_path)

    with open(notebook_path) as f:
        nb = nbformat.read(f, as_version=4)

    proc = ExecutePreprocessor(timeout=600, kernel_name='python3')
    proc.allow_errors = True

    proc.preprocess(nb, {'metadata': {'path': '/'}})
    with TemporaryDirectory() as temp_dir:
        output_path = os.path.join(temp_dir, '{}_all_output.ipynb'.format(nb_name))

        with open(output_path, mode='wt') as f:
            nbformat.write(nb, f)
        errors = []
        for cell in nb.cells:
            if 'outputs' in cell:
                for output in cell['outputs']:
                    if output.output_type == 'error':
                        errors.append(output)
        return nb, errors
