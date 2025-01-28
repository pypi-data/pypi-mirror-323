import dataclasses
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from classiq.interface.enum_utils import StrEnum
from classiq.interface.exceptions import (
    ClassiqExpansionError,
    ClassiqInternalExpansionError,
)
from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.functions.port_declaration import (
    PortDeclarationDirection,
)
from classiq.interface.model.handle_binding import (
    HandleBinding,
    NestedHandleBinding,
    SlicedHandleBinding,
)
from classiq.interface.model.port_declaration import PortDeclaration
from classiq.interface.model.quantum_function_call import ArgValue
from classiq.interface.model.quantum_type import QuantumBitvector, QuantumType
from classiq.interface.model.variable_declaration_statement import (
    VariableDeclarationStatement,
)

from classiq.model_expansions.capturing.mangling_utils import (
    demangle_handle,
    mangle_captured_var_name,
)
from classiq.model_expansions.transformers.var_splitter import SymbolPart, SymbolParts

if TYPE_CHECKING:
    from classiq.model_expansions.closure import FunctionClosure


ALREADY_ALLOCATED_MESSAGE = "Cannot allocate variable '{}', it is already initialized"
ALREADY_FREED_MESSAGE = "Cannot free variable '{}', it is already uninitialized"


class PortDirection(StrEnum):
    Input = "input"
    Inout = "inout"
    Output = "output"
    Outin = "outin"

    def negate(self) -> "PortDirection":
        if self == PortDirection.Input:
            return PortDirection.Output
        if self == PortDirection.Output:
            return PortDirection.Input
        return self

    @staticmethod
    def load(direction: PortDeclarationDirection) -> "PortDirection":
        if direction == PortDeclarationDirection.Input:
            return PortDirection.Input
        if direction == PortDeclarationDirection.Output:
            return PortDirection.Output
        if direction == PortDeclarationDirection.Inout:
            return PortDirection.Inout
        raise ClassiqInternalExpansionError

    def dump(self) -> PortDeclarationDirection:
        if self == PortDirection.Input:
            return PortDeclarationDirection.Input
        if self == PortDirection.Output:
            return PortDeclarationDirection.Output
        if self == PortDirection.Inout:
            return PortDeclarationDirection.Inout
        raise ClassiqInternalExpansionError


@dataclass(frozen=True)
class _CapturedHandle:
    handle: HandleBinding
    quantum_type: QuantumType
    defining_function: "FunctionClosure"
    direction: PortDirection
    is_propagated: bool

    @property
    def mangled_name(self) -> str:
        return mangle_captured_var_name(
            self.handle.identifier,
            self.defining_function.name,
            self.defining_function.depth,
        )

    @property
    def port(self) -> PortDeclaration:
        return PortDeclaration(
            name=self.mangled_name,
            quantum_type=self.quantum_type,
            direction=self.direction.dump(),
        )

    def is_same_var(self, other: "_CapturedHandle") -> bool:
        return self.handle.name == other.handle.name and _same_closure(
            self.defining_function, other.defining_function
        )

    def change_direction(self, new_direction: PortDirection) -> "_CapturedHandle":
        return dataclasses.replace(self, direction=new_direction)

    def set_propagated(self) -> "_CapturedHandle":
        return dataclasses.replace(self, is_propagated=True)

    def update_propagation(
        self, other_captured_handle: "_CapturedHandle"
    ) -> "_CapturedHandle":
        if self.is_propagated and not other_captured_handle.is_propagated:
            return dataclasses.replace(self, is_propagated=False)
        return self

    def set_symbol(
        self, handle: HandleBinding, quantum_type: QuantumType
    ) -> "_CapturedHandle":
        return dataclasses.replace(self, handle=handle, quantum_type=quantum_type)


@dataclass
class CapturedVars:
    _captured_handles: list[_CapturedHandle] = field(default_factory=list)

    def capture_handle(
        self,
        handle: HandleBinding,
        quantum_type: QuantumType,
        defining_function: "FunctionClosure",
        direction: PortDeclarationDirection,
    ) -> None:
        self._capture_handle(
            _CapturedHandle(
                handle=handle,
                quantum_type=quantum_type,
                defining_function=defining_function,
                direction=PortDirection.load(direction),
                is_propagated=False,
            )
        )

    def _capture_handle(self, captured_handle: _CapturedHandle) -> None:
        if (
            isinstance(captured_handle.handle, NestedHandleBinding)
            and captured_handle.direction != PortDirection.Inout
        ):
            verb = (
                "free"
                if captured_handle.direction == PortDirection.Input
                else "allocate"
            )
            raise ClassiqExpansionError(
                f"Cannot partially {verb} variable {captured_handle.handle.name}"
            )

        new_captured_handles = []
        for existing_captured_handle in self._captured_handles:
            if not existing_captured_handle.is_same_var(captured_handle):
                new_captured_handles.append(existing_captured_handle)
                continue
            captured_handle = captured_handle.update_propagation(
                existing_captured_handle
            )
            if existing_captured_handle.handle == captured_handle.handle:
                captured_handle = self._conjugate_direction(
                    existing_captured_handle, captured_handle
                )
            elif captured_handle.handle.overlaps(existing_captured_handle.handle):
                captured_handle = self._intersect_handles(
                    existing_captured_handle, captured_handle
                )
            else:
                new_captured_handles.append(existing_captured_handle)
        new_captured_handles.append(captured_handle)
        self._captured_handles = new_captured_handles

    def _conjugate_direction(
        self,
        existing_captured_handle: _CapturedHandle,
        captured_handle: _CapturedHandle,
    ) -> _CapturedHandle:
        if existing_captured_handle.direction == PortDirection.Input:
            if captured_handle.direction == PortDirection.Output:
                return captured_handle.change_direction(PortDirection.Inout)
            if captured_handle.direction == PortDirection.Outin:
                return captured_handle.change_direction(PortDirection.Input)
            raise ClassiqExpansionError(
                ALREADY_FREED_MESSAGE.format(captured_handle.handle)
            )
        if existing_captured_handle.direction == PortDirection.Output:
            if captured_handle.direction == PortDirection.Input:
                return captured_handle.change_direction(PortDirection.Outin)
            if captured_handle.direction in (
                PortDirection.Output,
                PortDirection.Outin,
            ):
                raise ClassiqExpansionError(
                    ALREADY_ALLOCATED_MESSAGE.format(captured_handle.handle)
                )
            return captured_handle.change_direction(PortDirection.Output)
        if existing_captured_handle.direction == PortDirection.Inout:
            if captured_handle.direction in (
                PortDirection.Output,
                PortDirection.Outin,
            ):
                raise ClassiqExpansionError(
                    ALREADY_ALLOCATED_MESSAGE.format(captured_handle.handle)
                )
        elif captured_handle.direction in (
            PortDirection.Input,
            PortDirection.Inout,
        ):
            raise ClassiqExpansionError(
                ALREADY_FREED_MESSAGE.format(captured_handle.handle)
            )
        return captured_handle

    def _intersect_handles(
        self,
        existing_captured_handle: _CapturedHandle,
        captured_handle: _CapturedHandle,
    ) -> _CapturedHandle:
        if captured_handle.handle in existing_captured_handle.handle:
            if existing_captured_handle.direction in (
                PortDirection.Input,
                PortDirection.Outin,
            ):
                raise ClassiqExpansionError(
                    ALREADY_FREED_MESSAGE.format(captured_handle.handle)
                )
            return existing_captured_handle

        if existing_captured_handle.handle in captured_handle.handle:
            if captured_handle.direction in (
                PortDirection.Output,
                PortDirection.Outin,
            ):
                raise ClassiqExpansionError(
                    ALREADY_ALLOCATED_MESSAGE.format(captured_handle.handle)
                )
            return captured_handle

        sliced_handle, quantum_type, other_handle = self._get_sliced_handle(
            existing_captured_handle, captured_handle
        )
        if not isinstance(other_handle, SlicedHandleBinding):
            return captured_handle.set_symbol(sliced_handle, quantum_type)

        merged_handle, merged_quantum_type = self._merge_sliced_handles(
            sliced_handle, other_handle, quantum_type
        )
        return captured_handle.set_symbol(merged_handle, merged_quantum_type)

    @staticmethod
    def _get_sliced_handle(
        existing_captured_handle: _CapturedHandle,
        captured_handle: _CapturedHandle,
    ) -> tuple[SlicedHandleBinding, QuantumBitvector, HandleBinding]:
        handle_1 = existing_captured_handle.handle
        quantum_type_1 = existing_captured_handle.quantum_type
        handle_2 = captured_handle.handle
        quantum_type_2 = captured_handle.quantum_type
        if isinstance(handle_1, SlicedHandleBinding):
            sliced_handle = handle_1
            other_handle = handle_2
            quantum_type = quantum_type_1
        elif isinstance(handle_2, SlicedHandleBinding):
            sliced_handle = handle_2
            other_handle = handle_1
            quantum_type = quantum_type_2
        else:
            raise ClassiqInternalExpansionError(
                f"Unexpected overlapping handles {handle_1} and {handle_2}"
            )
        if not isinstance(quantum_type, QuantumBitvector):
            raise ClassiqInternalExpansionError
        return sliced_handle, quantum_type, other_handle

    @staticmethod
    def _merge_sliced_handles(
        handle_1: SlicedHandleBinding,
        handle_2: SlicedHandleBinding,
        quantum_type: QuantumBitvector,
    ) -> tuple[HandleBinding, QuantumBitvector]:
        if (
            not handle_1.start.is_evaluated()
            or not handle_1.end.is_evaluated()
            or not handle_2.start.is_evaluated()
            or not handle_2.end.is_evaluated()
        ):
            raise ClassiqInternalExpansionError

        new_start = min(handle_1.start.to_int_value(), handle_2.start.to_int_value())
        new_end = max(handle_1.end.to_int_value(), handle_2.end.to_int_value())
        merged_handle = SlicedHandleBinding(
            base_handle=handle_1.base_handle,
            start=Expression(expr=str(new_start)),
            end=Expression(expr=str(new_end)),
        )
        merged_quantum_type = QuantumBitvector(
            element_type=quantum_type.element_type,
            length=Expression(expr=str(new_end - new_start)),
        )
        return merged_handle, merged_quantum_type

    def update(self, other_captured_vars: "CapturedVars") -> None:
        for captured_handle in other_captured_vars._captured_handles:
            self._capture_handle(captured_handle)

    def negate(self) -> "CapturedVars":
        return CapturedVars(
            _captured_handles=[
                captured_handle.change_direction(captured_handle.direction.negate())
                for captured_handle in self._captured_handles
            ]
        )

    def filter_vars(
        self,
        current_function: "FunctionClosure",
        current_declarations: Optional[list[VariableDeclarationStatement]] = None,
    ) -> "CapturedVars":
        current_declared_vars = (
            None
            if current_declarations is None
            else {decl.name for decl in current_declarations}
        )
        return CapturedVars(
            _captured_handles=[
                captured_handle
                for captured_handle in self._captured_handles
                if not _same_closure(
                    captured_handle.defining_function, current_function
                )
                or (
                    current_declared_vars is not None
                    and captured_handle.handle.name not in current_declared_vars
                )
            ]
        )

    def set_propagated(self) -> "CapturedVars":
        return CapturedVars(
            _captured_handles=[
                captured_handle.set_propagated()
                for captured_handle in self._captured_handles
            ]
        )

    def get_captured_ports(self) -> list[PortDeclaration]:
        return [captured_handle.port for captured_handle in self._captured_handles]

    def get_captured_args(
        self, current_function: "FunctionClosure"
    ) -> list[HandleBinding]:
        return [
            (
                captured_handle.handle
                if _same_closure(current_function, captured_handle.defining_function)
                else HandleBinding(name=captured_handle.mangled_name)
            )
            for captured_handle in self._captured_handles
        ]

    def get_captured_mapping(self) -> SymbolParts:
        return {
            captured_handle.handle: [
                SymbolPart(
                    source_handle=captured_handle.handle,
                    target_var_name=captured_handle.mangled_name,
                    target_var_type=captured_handle.quantum_type,
                )
            ]
            for captured_handle in self._captured_handles
            if not captured_handle.is_propagated
        }

    def clone(self) -> "CapturedVars":
        return CapturedVars(_captured_handles=list(self._captured_handles))


def _same_closure(closure_1: "FunctionClosure", closure_2: "FunctionClosure") -> bool:
    return closure_1.depth == closure_2.depth


def validate_args_are_not_propagated(
    args: Sequence[ArgValue], captured_vars: Sequence[HandleBinding]
) -> None:
    if not captured_vars:
        return
    captured_handles = {demangle_handle(handle) for handle in captured_vars}
    arg_handles = {
        demangle_handle(arg) for arg in args if isinstance(arg, HandleBinding)
    }
    if any(
        arg_handle.overlaps(captured_handle)
        for arg_handle in arg_handles
        for captured_handle in captured_handles
    ):
        captured_handles_str = {str(handle) for handle in captured_handles}
        arg_handles_str = {str(handle) for handle in arg_handles}
        vars_msg = f"Explicitly passed variables: {arg_handles_str}, captured variables: {captured_handles_str}"
        raise ClassiqExpansionError(
            f"Cannot capture variables that are explicitly passed as arguments. "
            f"{vars_msg}"
        )


def validate_captured_directions(
    captured_vars: CapturedVars, report_outin: bool = True
) -> None:
    captured_inputs = [
        captured_handle.handle.name
        for captured_handle in captured_vars._captured_handles
        if captured_handle.direction == PortDirection.Input
    ]
    captured_outputs = [
        captured_handle.handle.name
        for captured_handle in captured_vars._captured_handles
        if captured_handle.direction
        in (
            (PortDirection.Output, PortDirection.Outin)
            if report_outin
            else (PortDirection.Output,)
        )
    ]
    if len(captured_inputs) > 0:
        raise ClassiqExpansionError(
            f"Captured quantum variables {captured_inputs!r} cannot be used as inputs"
        )
    if len(captured_outputs) > 0:
        raise ClassiqExpansionError(
            f"Captured quantum variables {captured_outputs!r} cannot be used as outputs"
        )
