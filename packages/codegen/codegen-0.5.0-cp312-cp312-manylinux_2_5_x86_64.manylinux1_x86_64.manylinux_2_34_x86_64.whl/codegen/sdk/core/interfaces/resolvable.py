from abc import abstractmethod
from typing import TYPE_CHECKING, Generic

from typing_extensions import TypeVar

from codegen.sdk.core.autocommit import writer
from codegen.sdk.core.interfaces.chainable import Chainable
from codegen.sdk.core.interfaces.editable import Editable
from codegen.shared.decorators.docs import noapidoc

if TYPE_CHECKING:
    pass
Parent = TypeVar("Parent", bound=Editable)


class Resolvable(Chainable[Parent], Generic[Parent]):
    """Represents a class resolved to another symbol during the compute dependencies step."""

    @abstractmethod
    @noapidoc
    @writer
    def rename_if_matching(self, old: str, new: str) -> None: ...
