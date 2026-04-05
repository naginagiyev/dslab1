import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.notebook import StatefulNotebookRunner

runner = StatefulNotebookRunner("test_notebook")
cell = runner.addCell(code="print('hello world')")
result = runner.runCell(cell)
print(result)
runner.shutdown()