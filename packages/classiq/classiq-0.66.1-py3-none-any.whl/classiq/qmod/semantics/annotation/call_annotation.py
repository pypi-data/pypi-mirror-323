from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from typing import Any

from classiq.interface.exceptions import ClassiqError
from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.functions.classical_type import Integer
from classiq.interface.generator.functions.port_declaration import (
    PortDeclarationDirection,
)
from classiq.interface.model.classical_parameter_declaration import (
    ClassicalParameterDeclaration,
)
from classiq.interface.model.model_visitor import ModelVisitor
from classiq.interface.model.native_function_definition import NativeFunctionDefinition
from classiq.interface.model.port_declaration import PortDeclaration
from classiq.interface.model.quantum_function_call import QuantumFunctionCall
from classiq.interface.model.quantum_function_declaration import (
    AnonQuantumOperandDeclaration,
    QuantumFunctionDeclaration,
    QuantumOperandDeclaration,
)
from classiq.interface.model.quantum_lambda_function import (
    QuantumLambdaFunction,
)
from classiq.interface.model.quantum_type import QuantumBitvector

from classiq.qmod.builtins.functions import BUILTIN_FUNCTION_DECLARATIONS
from classiq.qmod.semantics.annotation.qstruct_annotator import QStructAnnotator
from classiq.qmod.semantics.error_manager import ErrorManager
from classiq.qmod.semantics.lambdas import get_renamed_parameters

ALLOCATE_DECL_FOR_COMPATIBILITY = QuantumFunctionDeclaration(
    name="allocate",
    positional_arg_declarations=[
        ClassicalParameterDeclaration(
            name="num_qubits",
            classical_type=Integer(),
        ),
        PortDeclaration(
            name="out",
            quantum_type=QuantumBitvector(length=Expression(expr="num_qubits")),
            direction=PortDeclarationDirection.Output,
        ),
    ],
)


def _annotate_function_call_decl(
    fc: QuantumFunctionCall,
    function_dict: Mapping[str, QuantumFunctionDeclaration],
) -> None:
    if fc.function == "allocate":  # FIXME: Remove compatibility (CAD-25935)
        fc.set_func_decl(ALLOCATE_DECL_FOR_COMPATIBILITY)
        return
    if fc._func_decl is None:
        func_decl = function_dict.get(fc.func_name)
        if func_decl is None:
            raise ClassiqError(
                f"Error resolving function {fc.func_name}, the function is not found in included library."
            )
        fc.set_func_decl(func_decl)

    for arg, param in zip(fc.positional_args, fc.func_decl.positional_arg_declarations):
        if not isinstance(param, AnonQuantumOperandDeclaration):
            continue
        args: list
        if isinstance(arg, list):
            args = arg
        else:
            args = [arg]
        for qlambda in args:
            if isinstance(qlambda, QuantumLambdaFunction):
                qlambda.set_op_decl(param)


class _CallLambdaAnnotator(ModelVisitor):
    def __init__(
        self, quantum_functions: Mapping[str, QuantumFunctionDeclaration]
    ) -> None:
        self._quantum_functions = dict(quantum_functions)
        self._current_operands: dict[str, QuantumOperandDeclaration] = {}

    @contextmanager
    def set_operands(
        self, operands: dict[str, QuantumOperandDeclaration]
    ) -> Iterator[None]:
        previous_operands = self._current_operands
        self._current_operands = operands
        yield
        self._current_operands = previous_operands

    def visit_NativeFunctionDefinition(self, func: NativeFunctionDefinition) -> None:
        with self.set_operands(func.operand_declarations_dict):
            self.generic_visit(func)

    def visit_QuantumLambdaFunction(self, lambda_func: QuantumLambdaFunction) -> None:
        lambda_operands = get_renamed_parameters(lambda_func)[1]
        with self.set_operands(self._current_operands | lambda_operands):
            self.generic_visit(lambda_func)

    def visit_QuantumFunctionCall(self, call: QuantumFunctionCall) -> None:
        _annotate_function_call_decl(
            call, self._quantum_functions | self._current_operands
        )
        self.generic_visit(call)


def resolve_function_calls(
    root: Any,
    quantum_function_dict: Mapping[str, QuantumFunctionDeclaration],
) -> None:
    all_functions: Mapping[str, QuantumFunctionDeclaration] = {
        **BUILTIN_FUNCTION_DECLARATIONS,
        **quantum_function_dict,
    }
    with ErrorManager().ignore_errors_context():
        QStructAnnotator().visit(quantum_function_dict)
        QStructAnnotator().visit(root)
        _CallLambdaAnnotator(all_functions).visit(root)
