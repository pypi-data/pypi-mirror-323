"""
This is a utility to format the coverage report in markdown format - useful for working with LLMs.

To use:
```console
pytest --junitxml=- --cov=./ --cov-report=xml | python tests/show_coverage.py
coverage run --source=pytest_evals -m pytest tests/ && coverage xml && python tests/show_coverage.py
```
"""

import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class CoverageCase:
    """Represents a continuous block of uncovered code"""

    start_line: int
    end_line: int
    code_lines: List[str]
    context: str = ""  # Can be used to store function/class name


class CoverageReport:
    def __init__(self, coverage_xml: str = "coverage.xml"):
        self.coverage_xml = coverage_xml
        self.files_with_uncovered = 0
        self.total_uncovered_lines = 0

    def _group_continuous_lines(
        self, lines: List[Tuple[int, str]]
    ) -> List[CoverageCase]:
        """Group continuous line numbers into cases"""
        if not lines:
            return []

        cases = []
        current_case = None

        for line_num, code in lines:
            if current_case is None:
                current_case = CoverageCase(line_num, line_num, [code])
            elif line_num == current_case.end_line + 1:
                current_case.end_line = line_num
                current_case.code_lines.append(code)
            else:
                cases.append(current_case)
                current_case = CoverageCase(line_num, line_num, [code])

        if current_case:
            cases.append(current_case)

        return cases

    def _detect_context(self, lines: List[str], start_line: int) -> str:
        """Try to detect the context (function/class) for a block of code"""
        # Look up to 5 lines before the uncovered block for context
        context_range = range(max(0, start_line - 5), start_line)
        for i in reversed(context_range):
            line = lines[i].strip()
            if line.startswith("def ") or line.startswith("class "):
                return line.split("(")[0].strip()
        return ""

    def format_markdown(self) -> str:
        """Format the coverage report in markdown with grouped cases"""
        try:
            root = ET.parse(self.coverage_xml).getroot()
            output = ["# Coverage Report\n"]

            files_report = defaultdict(list)

            for class_elem in root.findall(".//class"):
                filename = class_elem.attrib["filename"]

                try:
                    with open(filename, "r") as f:
                        file_lines = f.readlines()

                    # Get uncovered lines with their code
                    uncovered_lines = [
                        (
                            int(line.attrib["number"]),
                            file_lines[int(line.attrib["number"]) - 1].rstrip(),
                        )
                        for line in class_elem.findall('./lines/line[@hits="0"]')
                        if file_lines[int(line.attrib["number"]) - 1].strip()
                    ]

                    if uncovered_lines:
                        self.files_with_uncovered += 1
                        self.total_uncovered_lines += len(uncovered_lines)

                        # Group into cases
                        cases = self._group_continuous_lines(uncovered_lines)

                        # Add context to each case
                        for case in cases:
                            case.context = self._detect_context(
                                file_lines, case.start_line
                            )

                        files_report[filename].extend(cases)

                except FileNotFoundError:
                    output.append(f"⚠️ Could not find source file: {filename}\n")

            # Format the report
            for filename, cases in files_report.items():
                output.append(f"## {filename}\n")

                for i, case in enumerate(cases, 1):
                    context = f" ({case.context})" if case.context else ""
                    output.append(f"### Case {i}{context}\n")

                    if case.start_line == case.end_line:
                        output.append(f"Line {case.start_line}:\n")
                    else:
                        output.append(f"Lines {case.start_line}-{case.end_line}:\n")

                    output.append("```python")
                    for line_num, code in zip(
                        range(case.start_line, case.end_line + 1), case.code_lines
                    ):
                        output.append(f"{line_num}: {code}")
                    output.append("```\n")

            # Add summary
            output.extend(
                [
                    "## Summary\n",
                    f"- Files with uncovered lines: {self.files_with_uncovered}",
                    f"- Total uncovered lines: {self.total_uncovered_lines}",
                    f"- Total cases: {sum(len(cases) for cases in files_report.values())}",
                ]
            )

            return "\n".join(output)

        except FileNotFoundError:
            return "❌ Error: coverage.xml not found. Run coverage xml first."
        except Exception as e:
            return f"❌ Error: {str(e)}"


def main():
    report = CoverageReport()
    print(report.format_markdown())


if __name__ == "__main__":
    main()
