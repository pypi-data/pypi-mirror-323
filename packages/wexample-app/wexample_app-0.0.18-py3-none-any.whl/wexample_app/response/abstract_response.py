from abc import abstractmethod

from pydantic import BaseModel

from wexample_app.utils.abstract_kernel_child import AbstractKernelChild


class AbstractResponse(AbstractKernelChild, BaseModel):
    @abstractmethod
    def print(self) -> str:
        # For now, simple placeholder.
        pass
