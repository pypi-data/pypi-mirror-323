from typing import TYPE_CHECKING, Optional, Any, List, Union

from pydantic import BaseModel

from wexample_app.utils.abstract_kernel_child import AbstractKernelChild

if TYPE_CHECKING:
    from wexample_app.utils.abstract_command_resolver import AbstractCommandResolver
    from wexample_app.utils.runner.abstract_command_runner import AbstractCommandRunner


class CommandRequest(AbstractKernelChild, BaseModel):
    name: str
    arguments: List[Union[str | int]] = []
    path: Optional[str] = None
    type: Optional[str] = None
    resolver: Optional["AbstractCommandResolver"] = None
    runner: Optional["AbstractCommandRunner"] = None

    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)

        self.type = self.guess_type()
        self.path = self.get_resolver().build_command_path(self)
        self.resolver = self.get_resolver()
        self.runner = self.guess_runner()

    def execute(self) -> Any:
        command = self.runner.build_command(request=self)

        return command.execute(self.arguments)

    def get_resolver(self) -> Optional["AbstractCommandResolver"]:
        return self.kernel.resolvers[self.type]

    def guess_runner(self) -> Optional["AbstractCommandRunner"]:
        for runner_type in self.kernel.runners:
            if self.kernel.runners[runner_type].will_run(self):
                return self.kernel.runners[runner_type]
        return None

    def guess_type(self) -> Optional[str]:
        for resolver_type in self.kernel.resolvers:
            if self.kernel.resolvers[resolver_type].supports(self):
                return resolver_type
        return None
