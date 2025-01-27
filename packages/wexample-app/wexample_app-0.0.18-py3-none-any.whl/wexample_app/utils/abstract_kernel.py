from typing import Any, Optional, Dict, Type, cast, TYPE_CHECKING

from pydantic import BaseModel, Field

from wexample_app.exception.kernel_exception import KernelException
from wexample_app.utils.command_request import CommandRequest
from wexample_app.utils.runner.abstract_command_runner import AbstractCommandRunner
from wexample_filestate.file_state_manager import FileStateManager
from wexample_helpers.const.types import StringsList
from wexample_helpers.service.mixins.service_container_mixin import ServiceContainerMixin
from wexample_prompt.common.io_manager import IoManager
from wexample_prompt.responses.base_prompt_response import BasePromptResponse

if TYPE_CHECKING:
    from wexample_app.utils.abstract_command_resolver import AbstractCommandResolver


class AbstractKernel(
    ServiceContainerMixin,
    BaseModel
):
    io: Optional[IoManager] = None
    entrypoint_path: str = Field(description="The main file placed at application root directory")
    runners: Dict[str, "AbstractCommandRunner"] = None
    env_config: Dict[str, Optional[str]] = None
    expected_env_items: Optional[StringsList] = [
        "APP_ENV"
    ]
    workdir: FileStateManager = None

    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)

        self.io = IoManager()

        self._init_workdir()
        self._init_env_values()
        self._init_resolvers()
        self._init_runners()

        # Validate configuration.
        self._check_env_values()

    def _init_env_values(self):
        from dotenv import dotenv_values

        self.env_config = dotenv_values(f"{self.workdir.get_resolved()}{self._get_dotenv_file_name()}")

    def _get_dotenv_file_name(self) -> str:
        from wexample_helpers.const.globals import FILE_NAME_ENV
        return FILE_NAME_ENV

    def _init_workdir(self):
        self.workdir = (self._get_workdir_state_manager_class()).create_from_path(
            path=self.entrypoint_path,
            config={},
            io_manager=self.io
        )

    def _init_resolvers(self):
        self.register_services(
            'resolvers',
            self._get_command_resolvers()
        )

    def _init_runners(self):
        self.runners = {
            class_definition.get_runner_name(): class_definition(kernel=self)
            for class_definition in self._get_command_runners()
        }

    def _get_workdir_state_manager_class(self) -> Type[FileStateManager]:
        return FileStateManager

    def _get_command_request_class(self) -> Type["CommandRequest"]:
        from wexample_app.utils.command_request import CommandRequest

        return CommandRequest

    def _check_env_values(self):
        from wexample_helpers.helpers.dict import dict_get_first_missing_key
        first_missing_key = dict_get_first_missing_key(self.env_config, self.expected_env_items)
        if first_missing_key:
            raise KernelException(f"Missing {self._get_dotenv_file_name()} configuration {first_missing_key}")

    def _get_command_resolvers(self) -> list[Type["AbstractCommandResolver"]]:
        return cast(
            list[Type["AbstractCommandResolver"]],
            self.get_service_registry('command_resolvers').all_classes())

    def _get_command_runners(self) -> list[Type["AbstractCommandRunner"]]:
        from wexample_app.utils.runner.python_command_runner import PythonCommandRunner

        return [
            # Default runner.
            PythonCommandRunner
        ]

    def execute_kernel_command(self, request: "CommandRequest") -> BasePromptResponse:
        return request.execute()

