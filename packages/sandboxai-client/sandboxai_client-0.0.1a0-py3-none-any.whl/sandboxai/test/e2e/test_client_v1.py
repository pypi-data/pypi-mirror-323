import os
import pytest

from sandboxai.api.v1 import Sandbox, RunIPythonCellRequest, RunShellCommandRequest
from sandboxai.client.v1 import HttpClient


@pytest.fixture
def client():
    # Adjust the base_url as needed for your environment
    base_url = os.environ.get("SANDBOXAI_BASE_URL", "")
    return HttpClient(base_url=base_url)


def test_http_client_v1(client):
    """
    Run IPython tool end-to-end test for the Client.

    This test verifies that the client can create a sandbox, retrieve it,
    and run multiple IPython cells and shell command with the expected outputs.
    """
    box_image = os.environ.get("BOX_IMAGE", "")
    # Create a new sandbox (adjust the image as needed for your tests)
    sandbox = client.create_sandbox(Sandbox(image=box_image))

    # Ensure sandbox retrieval works
    retrieved = client.get_sandbox(sandbox.id)
    assert retrieved.id == sandbox.id

    ipy_test_cases = [
        {
            "name": "simple print",
            "code": "print(123)",
            "split": False,
            "expectedOutput": "123\n",
        },
        {
            "name": "simple split print",
            "code": "print(123)",
            "split": True,
            "expectedStdout": "123\n",
        },
        {
            "name": "import sys",
            "code": "import sys",
            # No expected output
        },
        {
            "name": "stderr print",
            "code": "import sys\nprint(123, file=sys.stderr)",
            "split": False,
            "expectedOutput": "123\n",
        },
        {
            "name": "stderr split print",
            "code": "import sys\nprint(123, file=sys.stderr)",
            "split": True,
            "expectedStderr": "123\n",
        },
        {
            "name": "unknown var",
            "code": "foo",
            "expectedOutputContains": "name 'foo' is not defined",
        },
        {
            "name": "set var",
            "code": "foo = 123",
        },
        {
            "name": "evaluate var",
            "code": "foo",
            "expectedOutput": "Out[1]: 123\n",
        },
    ]

    shell_test_cases = [
        {
            "name": "basic echo",
            "command": "echo 'hello'",
            "expectedOutput": "hello\n",
        },
        {
            "name": "echo to stderr",
            "command": ">&2 echo 'error'",
            "expectedOutput": "error\n",
        },
        {
            "name": "echo to stderr with split output",
            "command": ">&2 echo 'error'",
            "split": True,
            "expectedStderr": "error\n",
        },
    ]

    try:
        for tc in ipy_test_cases:
            req = RunIPythonCellRequest(
                code=tc["code"], split_output=tc.get("split", False)
            )
            resp = client.run_ipython_cell(sandbox.id, req)

            # If we expect the output to contain a substring
            if "expectedOutputContains" in tc:
                assert tc["expectedOutputContains"] in (resp.output or "")
                # This check ensures there's no conflicting expectations
                assert (
                    "expectedOutput" not in tc
                ), "Invalid assertion combo: both 'output' and 'outputContains' set."
            else:
                # Must match exact output if 'expectedOutput' is defined
                expected_output = tc.get("expectedOutput", "")
                assert expected_output == (resp.output or "")

                # Check stdout if provided
                if "expectedStdout" in tc:
                    assert tc["expectedStdout"] == (resp.stdout or "")

                # Check stderr if provided
                if "expectedStderr" in tc:
                    assert tc["expectedStderr"] == (resp.stderr or "")
        for tc in shell_test_cases:
            req = RunShellCommandRequest(
                command=tc["command"], split_output=tc.get("split", False)
            )
            resp = client.run_shell_command(sandbox.id, req)

            if "expectedOutput" in tc:
                assert tc["expectedOutput"] == (resp.output or "")
            if "expectedStdout" in tc:
                assert tc["expectedStdout"] == (resp.stdout or "")
            if "expectedStderr" in tc:
                assert tc["expectedStderr"] == (resp.stderr or "")

    finally:
        # Cleanup: delete the sandbox
        client.delete_sandbox(sandbox.id)
