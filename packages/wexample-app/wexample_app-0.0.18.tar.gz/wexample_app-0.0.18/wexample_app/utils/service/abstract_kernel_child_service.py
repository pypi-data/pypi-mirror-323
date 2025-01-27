from pydantic import BaseModel

from wexample_app.utils.abstract_kernel_child import AbstractKernelChild
from wexample_app.utils.service.service_mixin import ServiceMixin


class AbstractKernelChildService(ServiceMixin, AbstractKernelChild, BaseModel):
    pass
