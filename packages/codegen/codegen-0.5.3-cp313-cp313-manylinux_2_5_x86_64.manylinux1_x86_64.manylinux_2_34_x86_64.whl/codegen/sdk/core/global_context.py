from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from codegen.sdk.codebase.config import DefaultConfig, GraphSitterConfig
from codegen.sdk.codebase.multigraph import MultiGraph
from codegen.sdk.core.plugins import PLUGINS

if TYPE_CHECKING:
    from codegen.sdk.core.codebase import Codebase
    from codegen.sdk.core.function import Function


@dataclass
class GlobalContext[TFunction: Function]:
    multigraph: MultiGraph[TFunction] = field(default_factory=MultiGraph)
    config: GraphSitterConfig = DefaultConfig

    def execute_plugins(self, codebase: "Codebase"):
        for plugin in PLUGINS:
            plugin.execute(codebase)
