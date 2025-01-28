from typing import TYPE_CHECKING

from classiq.interface.exceptions import ClassiqValueError
from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.model.allocate import Allocate
from classiq.interface.model.handle_binding import HandleBinding
from classiq.interface.model.quantum_function_call import QuantumFunctionCall

from classiq.model_expansions.closure import FunctionClosure
from classiq.model_expansions.quantum_operations.call_emitter import CallEmitter
from classiq.model_expansions.quantum_operations.declarative_call_emitter import (
    DeclarativeCallEmitter,
)
from classiq.qmod.semantics.error_manager import ErrorManager

if TYPE_CHECKING:
    from classiq.model_expansions.interpreters.base_interpreter import BaseInterpreter


ALLOCATE_COMPATIBILITY_ERROR_MESSAGE = (
    "'allocate' expects two argument: The number of qubits to allocate (integer) and "
    "the variable to be allocated (quantum variable)"
)


class QuantumFunctionCallEmitter(CallEmitter[QuantumFunctionCall]):
    def __init__(self, interpreter: "BaseInterpreter") -> None:
        super().__init__(interpreter)
        self._model = self._interpreter._model

    def emit(self, call: QuantumFunctionCall, /) -> None:
        if call.function == "allocate":  # FIXME: Remove compatibility (CAD-25935)
            self._allocate_compatibility(call)
            return
        function = self._interpreter.evaluate(call.function).as_type(FunctionClosure)
        args = call.positional_args
        with ErrorManager().call(function.name):
            self._emit_quantum_function_call(
                function, args, self._debug_info.get(call.uuid)
            )

    def _allocate_compatibility(self, call: QuantumFunctionCall) -> None:
        if len(call.positional_args) != 2:
            raise ClassiqValueError(ALLOCATE_COMPATIBILITY_ERROR_MESSAGE)
        size, target = call.positional_args
        if not isinstance(size, Expression) or not isinstance(target, HandleBinding):
            raise ClassiqValueError(ALLOCATE_COMPATIBILITY_ERROR_MESSAGE)
        allocate = Allocate(size=size, target=target, source_ref=call.source_ref)
        self._interpreter.emit_statement(allocate)


class DeclarativeQuantumFunctionCallEmitter(
    QuantumFunctionCallEmitter, DeclarativeCallEmitter
):
    pass
