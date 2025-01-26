import time
import requests

from sandboxai.api.v1 import (
    Sandbox,
    RunIPythonCellRequest,
    RunIPythonCellResponse,
    RunShellCommandRequest,
    RunShellCommandResponse,
)


def _validate_response(response: requests.Response, expected_status: int) -> None:
    """
    Validates that the response's status code matches the expected status.
    Raises an exception if there's a mismatch.
    """
    if response.status_code != expected_status:
        raise RuntimeError(
            f"Expected status {expected_status}, got {response.status_code}: {response.text}"
        )


class SandboxNotFoundError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class HttpClient:
    """
    A Python client for interacting with the SandboxAI API, using typed models from v1.py.
    Provides CRUD operations on sandbox resources and runs IPython cells.
    """

    def __init__(self, base_url: str) -> None:
        """
        Initialize the Python client.

        Args:
            base_url (str): The base URL for the SandboxAI API
                            (for example, "http://localhost:5000/v1").
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def check_health(self) -> bool:
        """
        Checks if the sandbox service is running by verifying the health endpoint.

        Returns:
            bool: True if the service is reachable, False otherwise
        """
        endpoint = f"{self.base_url}/healthz"
        try:
            response = self.session.get(endpoint)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def wait_until_healthy(self, timeout: int = 10) -> None:
        """
        Waits until the sandbox service is running for a specified timeout.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.check_health():
                return
            time.sleep(1)
        raise TimeoutError(
            "Sandbox service did not start within the specified timeout."
        )

    def create_sandbox(self, sandbox: Sandbox) -> Sandbox:
        """
        Create a new sandbox. Issues a POST to /sandboxes.

        Args:
            sandbox (Sandbox): Sandbox object to create on the remote server.

        Returns:
            Sandbox: The newly created sandbox, as returned by the API.
        """
        endpoint = f"{self.base_url}/sandboxes"
        response = self.session.post(endpoint, json=sandbox.model_dump())
        _validate_response(response, 201)
        return Sandbox.model_validate(response.json())

    def get_sandbox(self, sandbox_id: str) -> Sandbox:
        """
        Retrieve an existing sandbox by its ID. Issues a GET to /sandboxes/{sandbox_id}.

        Args:
            sandbox_id (str): ID of the sandbox to retrieve.

        Returns:
            Sandbox: The retrieved sandbox.

        Raises:
            SandboxNotFoundError: If the sandbox with the given ID does not exist.
        """
        endpoint = f"{self.base_url}/sandboxes/{sandbox_id}"
        response = self.session.get(endpoint)
        if response.status_code == 404:
            raise SandboxNotFoundError(f"Sandbox with ID '{sandbox_id}' not found.")
        _validate_response(response, 200)
        return Sandbox.model_validate(response.json())

    def delete_sandbox(self, sandbox_id: str) -> None:
        """
        Delete an existing sandbox by its ID. Issues a DELETE to /sandboxes/{sandbox_id}.

        Args:
            sandbox_id (str): ID of the sandbox to delete.
        """
        endpoint = f"{self.base_url}/sandboxes/{sandbox_id}"
        response = self.session.delete(endpoint)
        _validate_response(response, 204)

    def run_ipython_cell(
        self, sandbox_id: str, request: RunIPythonCellRequest
    ) -> RunIPythonCellResponse:
        """
        Run an IPython cell in the specified sandbox. Issues a POST to
        /sandboxes/{sandbox_id}/tools:run_ipython_cell.

        Args:
            sandbox_id (str): The ID of the sandbox where the cell should run.
            request (RunIPythonCellRequest): The cell execution request details.

        Returns:
            RunIPythonCellResponse: The result of running the cell.
        """
        endpoint = f"{self.base_url}/sandboxes/{sandbox_id}/tools:run_ipython_cell"
        response = self.session.post(endpoint, json=request.model_dump())
        _validate_response(response, 200)
        return RunIPythonCellResponse.model_validate(response.json())

    def run_shell_command(
        self, sandbox_id: str, request: RunShellCommandRequest
    ) -> RunShellCommandResponse:
        """
        Run a shell command in the specified sandbox. Issues a POST to
        /sandboxes/{sandbox_id}/tools:run_shell_command.

        Args:
            sandbox_id (str): The ID of the sandbox where the command should run.
            request (RunShellCommandRequest): The shell command execution request details.

        Returns:
            RunShellCommandResponse: The result of running the shell command.
        """
        endpoint = f"{self.base_url}/sandboxes/{sandbox_id}/tools:run_shell_command"
        response = self.session.post(endpoint, json=request.model_dump())
        _validate_response(response, 200)
        return RunShellCommandResponse.model_validate(response.json())
