class VariableRegistry:
    def __init__(self):
        self.namespace = {}

    def runCode(self, codeStr: str) -> dict:
        exec(codeStr, self.namespace)
        return self.getRegistry()

    def getRegistry(self) -> dict:
        skip = {"__builtins__"}
        return {
            name: self.describe(val)
            for name, val in self.namespace.items()
            if not name.startswith("_") and name not in skip
        }

    def describe(self, val) -> dict:
        typeName = type(val).__name__
        moduleNme = type(val).__module__

        if typeName == "DataFrame":
            return {"type": "DataFrame", "shape": val.shape, "columns": list(val.columns)}
        if typeName == "ndarray":
            return {"type": "ndarray", "shape": val.shape, "dtype": str(val.dtype)}
        if typeName == "Tensor":
            return {"type": "Tensor", "shape": list(val.shape), "dtype": str(val.dtype)}
        if typeName == "Image":
            return {"type": "Image", "size": val.size, "mode": val.mode}
        if isinstance(val, (int, float, str, bool)):
            return {"type": typeName, "value": val}
        if isinstance(val, (list, dict, tuple)):
            return {"type": typeName, "length": len(val)}

        return {"type": typeName, "module": moduleNme}

    def toPromptString(self) -> str:
        lines = ["Available variables:"]
        for name, meta in self.getRegistry().items():
            lines.append(f"  - `{name}`: {meta}")
        return "\n".join(lines)