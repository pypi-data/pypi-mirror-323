from abc import ABC

from codegen.sdk.core.codebase import CodebaseType
from codegen.sdk.core.placeholder.placeholder import Placeholder
from codegen.sdk.enums import ProgrammingLanguage
from codegen.sdk.skills.core.skill import Skill
from codegen.sdk.skills.core.skill_test import SkillTestCase, SkillTestCasePyFile
from codegen.sdk.skills.core.utils import skill, skill_impl

CountUntypedReturnStatementsTest = SkillTestCase(
    files=[
        SkillTestCasePyFile(
            input="""
def add(a: int, b: int):
    return a + b

def subtract(a: int, b: int) -> int:
    return a - b

def multiply(a: int, b: int) -> int:
    return a * b

def divide(a: int, b: int) -> int:
    return a / b

def power(a: int, b: int) -> int:
    return a ** b
""",
            filepath="untyped_return_types.py",
        ),
    ],
    sanity=True,
)


@skill(
    prompt="""Generate a Python code snippet that counts the number of untyped return statements in all functions
    across all files in a codebase. The code should initialize a counter to zero, iterate through each file in the
    codebase, and for each file, iterate through its functions. For each function, check if the return type is None,
    and if so, count the number of return statements in that function. Finally, print the total count of untyped
    return statements.""",
    guide=True,
    uid="bef133a3-ebd9-484a-9b6d-bc1ca12f3a59",
)
class CountUntypedReturnStatements(Skill, ABC):
    """Counts the number of return statements in functions that do not have a specified return type across all files
    in the codebase. It iterates through each file and each function, checking for untyped return statements,
    and accumulates the total count, which is then printed.
    """

    @staticmethod
    @skill_impl(test_cases=[CountUntypedReturnStatementsTest], language=ProgrammingLanguage.PYTHON)
    def skill_func(codebase: CodebaseType):
        untitled_return_count = 0

        # Iterate through all files in the codebase
        for file in codebase.files:
            # Iterate through all functions in the file
            for function in file.functions:
                # Count the number of return statements that are not typed
                if isinstance(function.return_type, Placeholder):
                    untitled_return_count += len(function.return_statements)

        print(f"Number of untyped return statements: {untitled_return_count}")
