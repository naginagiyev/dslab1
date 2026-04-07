import nbformat
from pathlib import Path
from jupyter_client import KernelManager
from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = PROJECT_ROOT / "workspace"

class Notebook:
    def __init__(self, filename):
        WORKSPACE_DIR.mkdir(exist_ok=True)
        self.outputPath = WORKSPACE_DIR / filename
        self.cells = []
        self.notebook = new_notebook()
        self.notebook['cells'] = self.cells

        self.km = KernelManager()
        self.km.start_kernel()

        self.kc = self.km.client()
        self.kc.start_channels()
        self.kc.wait_for_ready()

        self.lastCellID = -1

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.shutdown()

    def appendMarkdownCell(self, markdown):
        self.cells.append(new_markdown_cell(markdown))
        self.lastCellID = self.lastCellID + 1

    def appendCodeCell(self, code):
        self.cells.append(new_code_cell(code))
        self.lastCellID = self.lastCellID + 1

    def commitCodeCell(self, code):
        self.cells.append(new_code_cell(code))
        self.save()
        output = self.runLast()
        if output.startswith("Success"):
            self.lastCellID = self.lastCellID + 1
        return output

    def save(self):
        with open(self.outputPath, 'w', encoding='utf-8') as f:
            nbformat.write(self.notebook, f)

    def runLast(self):
        cell = self.cells[-1]
        if cell['cell_type'] != 'code':
            return

        cell['outputs'] = []
        
        self.kc.execute(cell['source'])
        
        outputs = []
        
        while True:
            msg = self.kc.get_iopub_msg()
            msgType = msg['msg_type']
            content = msg['content']

            if msgType == 'stream':
                outputs.append(nbformat.v4.new_output('stream',
                    name=content['name'], text=content['text']))
            elif msgType == 'execute_result':
                outputs.append(nbformat.v4.new_output('execute_result',
                    data=content['data'],
                    metadata=content['metadata'],
                    execution_count=content['execution_count']))
            elif msgType == 'error':
                outputs.append(nbformat.v4.new_output('error',
                    ename=content['ename'],
                    evalue=content['evalue'],
                    traceback=content['traceback']))
            elif msgType == 'status' and content['execution_state'] == 'idle':
                break

        cell['outputs'] = outputs

    def getLastOutput(self):
        lastCellType = self.cells[self.lastCellID]['cell_type']
        if lastCellType == "markdown":
            sourceContent = self.cells[self.lastCellID]['source']
            return f"Success:\nThe last cell is a Markdown cell with content \"{sourceContent}\""
        
        outputs = self.cells[self.lastCellID]['outputs']
        if not outputs:
            return "Success:\nNothing on the output!"
        
        allOutputParts = []
        hasError = False
        
        for out in outputs:
            if out['output_type'] == 'stream':
                allOutputParts.append(out.get('text', ''))
            elif out['output_type'] == 'error':
                hasError = True
                allOutputParts.append(f"{out.get('ename', 'Error')}: {out.get('evalue', '')}")
            elif out['output_type'] == 'execute_result':
                allOutputParts.append(str(out.get('data', {}).get('text/plain', '')))
        
        combinedOutput = "".join(allOutputParts).strip()
        
        if hasError:
            return f"Error:\n{combinedOutput}"
        else:
            return f"Success:\n{combinedOutput}"

    def shutdown(self):
        self.kc.stop_channels()
        del self.kc
        self.km.shutdown_kernel(now=True)