from sandboxai.client.v1 import HttpClient
from sandboxai.api import v1 as v1Api
from sandboxai.utils import launch_sandboxd


DEFAULT_BACKEND = "http://localhost:5266/v1"
DEFAULT_IMAGE = "substratusai/sandboxai-box:v0.1.0"


class Sandbox:
    def __init__(
        self,
        backend: str = DEFAULT_BACKEND,
        image: str = DEFAULT_IMAGE,
        lazy_start: bool = False,
    ):
        """
        Initialize a Sandbox instance.
        """
        self.id = ""
        self.image = image
        self.backend = backend
        self.client = HttpClient(self.backend)
        if not self.client.check_health():
            if backend == DEFAULT_BACKEND:
                launch_sandboxd()
                self.client.wait_until_healthy(timeout=10)
            else:
                raise RuntimeError(
                    f"Sandbox service {backend}/v1/healthz is not responding with 200 OK."
                )
        if lazy_start == False:
            self.start()

    def __enter__(self):
        """
        Enter the context manager. Ensures the sandbox is started.
        """
        if not self.id:
            self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the context manager. Stops the sandbox.
        """
        self.stop()
        return False  # Don't suppress any exceptions

    def start(self) -> None:
        response = self.client.create_sandbox(v1Api.Sandbox(image=self.image))
        self.id = response.id
        self.image = response.image

    def run_python_code(self, code: str) -> str:
        """
        Runs Python code in the sandbox.
        """
        if not self.id:
            self.start()

        response = self.client.run_ipython_cell(self.id, v1Api.RunIPythonCellRequest(code=code, split_output=False))  # type: ignore
        return response.output or ""

    def run_shell_command(self, command: str) -> str:
        """
        Runs a shell command in the sandbox (uses 'bash -c <command>').
        """
        if not self.id:
            self.start()

        response = self.client.run_shell_command(self.id, v1Api.RunShellCommandRequest(command=command, split_output=False))  # type: ignore
        return response.output or ""

    def stop(self) -> None:
        if self.id:
            self.client.delete_sandbox(self.id)
            self.id = ""
            self.image = ""
