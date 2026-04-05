import nbformat
from path import workspaceDir
from nbclient import NotebookClient
from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell

class StatefulNotebookRunner:
    def __init__(self, notebookName: str):
        if not notebookName.endswith(".ipynb"):
            notebookName += ".ipynb"

        workspaceDir.mkdir(parents=True, exist_ok=True)
        self.notebookPath = workspaceDir / notebookName

        if self.notebookPath.exists():
            with open(self.notebookPath, "r", encoding="utf-8") as f:
                self.nb = nbformat.read(f, as_version=4)
        else:
            self.nb = new_notebook()
            self.save()

        self.client = NotebookClient(self.nb, timeout=60, kernel_name="python3")
        self.client.km = self.client.create_kernel_manager()
        self.client.kc = self.client.km.client()
        self.client.km.start_kernel()
        self.client.kc.start_channels()

    def save(self):
        with open(self.notebookPath, "w", encoding="utf-8") as f:
            nbformat.write(self.nb, f)

    def addCell(self, markdown=None, code=None):
        if markdown:
            self.nb.cells.append(new_markdown_cell(markdown))
            self.save()

        if code:
            cell = new_code_cell(code)
            self.nb.cells.append(cell)
            self.save()
            return cell

    def runCell(self, cell):
        try:
            self.client.execute_cell(cell, cell_index=len(self.nb.cells) - 1)

            outputs = []
            for output in cell.get("outputs", []):
                if "text" in output:
                    outputs.append(output["text"])
                elif "data" in output and "text/plain" in output["data"]:
                    outputs.append(output["data"]["text/plain"])

            self.save()
            return "\n".join(outputs) if outputs else "success"

        except Exception as e:
            self.save()
            return f"error: {str(e)}"

    def shutdown(self):
        self.client.kc.stop_channels()
        self.client.km.shutdown_kernel()

    def reset(self):
        self.shutdown()
        self.nb = new_notebook()
        self.save()

        self.client = NotebookClient(self.nb, timeout=60, kernel_name="python3")
        self.client.km = self.client.create_kernel_manager()
        self.client.kc = self.client.km.client()
        self.client.km.start_kernel()
        self.client.kc.start_channels()