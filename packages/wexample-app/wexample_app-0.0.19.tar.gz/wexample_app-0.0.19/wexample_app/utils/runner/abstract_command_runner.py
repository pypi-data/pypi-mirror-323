from abc import abstractmethod
from typing import Optional
from typing import TYPE_CHECKING

from pydantic import BaseModel

from wexample_app.utils.abstract_kernel_child import AbstractKernelChild

if TYPE_CHECKING:
    from wexample_app.utils.command import Command
    from wexample_app.utils.command_request import CommandRequest


class AbstractCommandRunner(AbstractKernelChild, BaseModel):
    @classmethod
    @abstractmethod
    def get_runner_name(cls) -> str:
        pass

    @abstractmethod
    def build_command(self, request: "CommandRequest") -> Optional["Command"]:
        pass

    def will_run(self, request: "CommandRequest") -> bool:
        return False
