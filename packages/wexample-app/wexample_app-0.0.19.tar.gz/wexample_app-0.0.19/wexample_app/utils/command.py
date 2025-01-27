from typing import Callable, Any

from pydantic import BaseModel

from wexample_app.utils.abstract_kernel_child import AbstractKernelChild


class Command(AbstractKernelChild, BaseModel):
    function: Callable[..., Any] = None

    def execute(self, arguments):
        return self.function(
            kernel=self.kernel,
            arguments=arguments
        )
