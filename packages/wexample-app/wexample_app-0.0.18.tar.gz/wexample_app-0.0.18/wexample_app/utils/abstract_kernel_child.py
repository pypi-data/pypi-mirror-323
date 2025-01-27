from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wexample_app.utils.abstract_kernel import AbstractKernel

class AbstractKernelChild:
    kernel: "AbstractKernel"
