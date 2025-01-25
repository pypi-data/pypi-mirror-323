import pytest
import os

from vellum import CodeExecutorResponse, NumberVellumValue, StringInput
from vellum.workflows.exceptions import NodeException
from vellum.workflows.inputs.base import BaseInputs
from vellum.workflows.nodes.displayable.code_execution_node import CodeExecutionNode
from vellum.workflows.references.vellum_secret import VellumSecretReference
from vellum.workflows.state.base import BaseState, StateMeta


def test_run_workflow__happy_path(vellum_client):
    """Confirm that CodeExecutionNodes output the expected text and results when run."""

    # GIVEN a node that subclasses CodeExecutionNode
    class Inputs(BaseInputs):
        word: str

    class State(BaseState):
        pass

    fixture = os.path.abspath(os.path.join(__file__, "../fixtures/main.py"))

    class ExampleCodeExecutionNode(CodeExecutionNode[State, int]):
        filepath = fixture
        runtime = "PYTHON_3_11_6"

        code_inputs = {
            "word": Inputs.word,
        }

    # AND we know what the Code Execution Node will respond with
    mock_code_execution = CodeExecutorResponse(
        log="hello",
        output=NumberVellumValue(value=5),
    )
    vellum_client.execute_code.return_value = mock_code_execution

    # WHEN we run the node
    node = ExampleCodeExecutionNode(
        state=State(
            meta=StateMeta(workflow_inputs=Inputs(word="hello")),
        )
    )
    outputs = node.run()

    # THEN the node should have produced the outputs we expect
    assert outputs == {"result": 5, "log": "hello"}

    # AND we should have invoked the Code with the expected inputs
    vellum_client.execute_code.assert_called_once_with(
        input_values=[
            StringInput(name="word", value="hello"),
        ],
        code="""\
def main(word: str) -> int:
    print(word)  # noqa: T201
    return len(word)
""",
        runtime="PYTHON_3_11_6",
        output_type="NUMBER",
        packages=[],
        request_options=None,
    )


def test_run_workflow__code_attribute(vellum_client):
    """Confirm that CodeExecutionNodes can use the `code` attribute to specify the code to execute."""

    # GIVEN a node that subclasses CodeExecutionNode
    class Inputs(BaseInputs):
        word: str

    class State(BaseState):
        pass

    class ExampleCodeExecutionNode(CodeExecutionNode[State, int]):
        code = """\
def main(word: str) -> int:
    print(word)  # noqa: T201
    return len(word)
"""
        runtime = "PYTHON_3_11_6"

        code_inputs = {
            "word": Inputs.word,
        }

    # AND we know what the Code Execution Node will respond with
    mock_code_execution = CodeExecutorResponse(
        log="hello",
        output=NumberVellumValue(value=5),
    )
    vellum_client.execute_code.return_value = mock_code_execution

    # WHEN we run the node
    node = ExampleCodeExecutionNode(
        state=State(
            meta=StateMeta(workflow_inputs=Inputs(word="hello")),
        )
    )
    outputs = node.run()

    # THEN the node should have produced the outputs we expect
    assert outputs == {"result": 5, "log": "hello"}

    # AND we should have invoked the Code with the expected inputs
    vellum_client.execute_code.assert_called_once_with(
        input_values=[
            StringInput(name="word", value="hello"),
        ],
        code="""\
def main(word: str) -> int:
    print(word)  # noqa: T201
    return len(word)
""",
        runtime="PYTHON_3_11_6",
        output_type="NUMBER",
        packages=[],
        request_options=None,
    )


def test_run_workflow__code_and_filepath_defined(vellum_client):
    """Confirm that CodeExecutionNodes raise an error if both `code` and `filepath` are defined."""

    # GIVEN a node that subclasses CodeExecutionNode
    class Inputs(BaseInputs):
        word: str

    class State(BaseState):
        pass

    fixture = os.path.abspath(os.path.join(__file__, "../fixtures/main.py"))

    class ExampleCodeExecutionNode(CodeExecutionNode[State, int]):
        filepath = fixture
        code = """\
def main(word: str) -> int:
    print(word)  # noqa: T201
    return len(word)
"""
        runtime = "PYTHON_3_11_6"

        code_inputs = {
            "word": Inputs.word,
        }

    # AND we know what the Code Execution Node will respond with
    mock_code_execution = CodeExecutorResponse(
        log="hello",
        output=NumberVellumValue(value=5),
    )
    vellum_client.execute_code.return_value = mock_code_execution

    # WHEN we run the node
    node = ExampleCodeExecutionNode(
        state=State(
            meta=StateMeta(workflow_inputs=Inputs(word="hello")),
        )
    )
    with pytest.raises(NodeException) as exc_info:
        node.run()

    # THEN the node should have produced the exception we expected
    assert exc_info.value.message == "Cannot specify both `code` and `filepath` for a CodeExecutionNode"


def test_run_workflow__code_and_filepath_not_defined(vellum_client):
    """Confirm that CodeExecutionNodes raise an error if neither `code` nor `filepath` are defined."""

    # GIVEN a node that subclasses CodeExecutionNode
    class Inputs(BaseInputs):
        word: str

    class State(BaseState):
        pass

    class ExampleCodeExecutionNode(CodeExecutionNode[State, int]):
        runtime = "PYTHON_3_11_6"

        code_inputs = {
            "word": Inputs.word,
        }

    # AND we know what the Code Execution Node will respond with
    mock_code_execution = CodeExecutorResponse(
        log="hello",
        output=NumberVellumValue(value=5),
    )
    vellum_client.execute_code.return_value = mock_code_execution

    # WHEN we run the node
    node = ExampleCodeExecutionNode(
        state=State(
            meta=StateMeta(workflow_inputs=Inputs(word="hello")),
        )
    )
    with pytest.raises(NodeException) as exc_info:
        node.run()

    # THEN the node should have produced the exception we expected
    assert exc_info.value.message == "Must specify either `code` or `filepath` for a CodeExecutionNode"


def test_run_workflow__vellum_secret(vellum_client):
    """Confirm that CodeExecutionNodes can use Vellum Secrets"""

    # GIVEN a node that subclasses CodeExecutionNode that references a Vellum Secret
    class State(BaseState):
        pass

    fixture = os.path.abspath(os.path.join(__file__, "../fixtures/main.py"))

    class ExampleCodeExecutionNode(CodeExecutionNode[State, int]):
        filepath = fixture
        runtime = "PYTHON_3_11_6"

        code_inputs = {
            "token": VellumSecretReference("OPENAI_API_KEY"),
        }

    # AND we know what the Code Execution Node will respond with
    mock_code_execution = CodeExecutorResponse(
        log="",
        output=NumberVellumValue(value=0),
    )
    vellum_client.execute_code.return_value = mock_code_execution

    # WHEN we run the node
    node = ExampleCodeExecutionNode(state=State())
    outputs = node.run()

    # THEN the node should have produced the outputs we expect
    assert outputs == {"result": 0, "log": ""}

    # AND we should have invoked the Code with the expected inputs
    vellum_client.execute_code.assert_called_once_with(
        input_values=[
            {"name": "token", "type": "SECRET", "value": "OPENAI_API_KEY"},
        ],
        code="""\
def main(word: str) -> int:
    print(word)  # noqa: T201
    return len(word)
""",
        runtime="PYTHON_3_11_6",
        output_type="NUMBER",
        packages=[],
        request_options=None,
    )
