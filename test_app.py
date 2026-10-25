
import ast
from pathlib import Path
import unittest

class ApplicationTests(unittest.TestCase):
    def test_app_compiles(self):
        source = Path("app.py").read_text(encoding="utf-8")
        ast.parse(source)

    def test_workflow_functions_exist(self):
        source = Path("app.py").read_text(encoding="utf-8")
        tree = ast.parse(source)

        functions = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

        self.assertIn("search_web", functions)
        self.assertIn("summarize_results", functions)
        self.assertIn("research_workflow", functions)

if __name__ == "__main__":
    unittest.main()
