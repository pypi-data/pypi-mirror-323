from abc import abstractmethod
from typing import TYPE_CHECKING, Optional

from wexample_app.utils.service.service_mixin import ServiceMixin

if TYPE_CHECKING:
    from wexample_app.utils.command_request import CommandRequest


class AbstractCommandResolver(ServiceMixin):
    @classmethod
    @abstractmethod
    def get_type(cls) -> str:
        pass

    def supports(self, request: "CommandRequest") -> bool:
        # By default, resolver match with every command.
        return True

    def build_command_path(self, request: "CommandRequest") -> Optional[str]:
        return None

    def build_command_function_name(self, request: "CommandRequest") -> None:
        return None
