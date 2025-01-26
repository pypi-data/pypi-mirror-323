from typing import Optional
from pydantic import BaseModel


class Sandbox(BaseModel):
    """
    Represents a sandbox for running AI-generated code and commands,
    as defined in the API spec.

    Attributes:
        id: The unique identifier of the sandbox.
        image: The container image the sandbox will run with.
    """

    id: Optional[str] = None
    image: str = ""


class RunIPythonCellRequest(BaseModel):
    """
    Represents the cell to run in a stateful IPython (Jupyter) kernel,
    as defined in the API spec.

    Attributes:
        code: The code to run in the IPython kernel.
        split_output: Whether to split output into stdout and stderr.
    """

    code: str
    split_output: Optional[bool] = None


class RunIPythonCellResponse(BaseModel):
    """
    Represents the response from a stateful IPython (Jupyter) kernel,
    as defined in the API spec.

    Attributes:
        output: The combined stdout and stderr from the IPython kernel.
        stdout: The stdout stream from the IPython kernel.
        stderr: The stderr stream from the IPython kernel.
    """

    output: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None


class RunShellCommandRequest(BaseModel):
    """
    Represents a shell command to run in the sandbox,
    as defined in the API spec.

    Attributes:
        command: The command to execute. Will be passed to 'bash -c'.
        split_output: Whether to split output into stdout and stderr.
                     If True, the output field in the response will be empty and
                     stdout/stderr fields will be populated.
    """

    command: str
    split_output: Optional[bool] = None


class RunShellCommandResponse(BaseModel):
    """
    Represents the response from a shell command execution,
    as defined in the API spec.

    Attributes:
        output: The combined stdout and stderr from the shell command.
        stdout: The stdout stream from the shell command.
        stderr: The stderr stream from the shell command.
    """

    output: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None


class Error(BaseModel):
    """
    Represents an API error response, as defined in the API spec.

    Attributes:
        message: The error message describing what went wrong.
    """

    message: str
