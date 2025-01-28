import ast
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from typing import (
    Optional,
)

from classiq.interface.exceptions import ClassiqSemanticError
from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.function_params import PortDirection
from classiq.interface.generator.functions.classical_type import CLASSICAL_ATTRIBUTES
from classiq.interface.generator.functions.concrete_types import ConcreteQuantumType
from classiq.interface.generator.functions.port_declaration import (
    PortDeclarationDirection,
)
from classiq.interface.model.handle_binding import (
    FieldHandleBinding,
    HandleBinding,
    SlicedHandleBinding,
    SubscriptHandleBinding,
)
from classiq.interface.model.inplace_binary_operation import InplaceBinaryOperation
from classiq.interface.model.model import Model
from classiq.interface.model.model_visitor import ModelVisitor
from classiq.interface.model.native_function_definition import NativeFunctionDefinition
from classiq.interface.model.port_declaration import PortDeclaration
from classiq.interface.model.quantum_expressions.quantum_expression import (
    QuantumExpressionOperation,
)
from classiq.interface.model.quantum_function_call import QuantumFunctionCall
from classiq.interface.model.quantum_function_declaration import (
    QuantumFunctionDeclaration,
    QuantumOperandDeclaration,
)
from classiq.interface.model.quantum_lambda_function import (
    QuantumLambdaFunction,
)
from classiq.interface.model.quantum_statement import HandleMetadata, QuantumOperation
from classiq.interface.model.validation_handle import HandleState
from classiq.interface.model.variable_declaration_statement import (
    VariableDeclarationStatement,
)
from classiq.interface.model.within_apply_operation import WithinApply

from classiq.model_expansions.visitors.variable_references import VarRefCollector
from classiq.qmod.builtins.functions import (
    BUILTIN_FUNCTION_DECLARATIONS,
)
from classiq.qmod.semantics.annotation.call_annotation import resolve_function_calls
from classiq.qmod.semantics.annotation.qstruct_annotator import QStructAnnotator
from classiq.qmod.semantics.error_manager import ErrorManager
from classiq.qmod.semantics.lambdas import get_renamed_parameters
from classiq.qmod.semantics.validation.func_call_validation import (
    check_no_overlapping_quantum_args,
    validate_call_arguments,
)
from classiq.qmod.semantics.validation.handle_validation import resolve_handle

HANDLE_BINDING_PART_MESSAGE = {
    SubscriptHandleBinding: "array subscript",
    SlicedHandleBinding: "array slice",
    FieldHandleBinding: "field access",
}


class StaticScope:
    def __init__(
        self,
        parameters: list[str],
        operands: dict[str, QuantumOperandDeclaration],
        variables_to_states: dict[str, HandleState],
        variables_to_types: dict[str, ConcreteQuantumType],
    ) -> None:
        self.parameters = parameters
        self.operands = operands
        self.variable_states = variables_to_states
        self.variables_to_types = variables_to_types


class StaticSemanticsVisitor(ModelVisitor):
    def __init__(
        self,
        functions_dict: Mapping[str, QuantumFunctionDeclaration],
        constants: list[str],
    ) -> None:
        self._scope: list[StaticScope] = []
        self._error_manager = ErrorManager()
        self._functions_dict = functions_dict
        self._constants = constants

    @property
    def current_scope(self) -> StaticScope:
        return self._scope[-1]

    @contextmanager
    def scoped_visit(self, scope: StaticScope) -> Iterator[None]:
        self._scope.append(scope)
        yield
        self._scope.pop()

    def visit_Model(self, model: Model) -> None:
        self.visit_BaseModel(model)

    def visit_NativeFunctionDefinition(
        self, func_def: NativeFunctionDefinition
    ) -> None:
        scope = StaticScope(
            parameters=list(func_def.param_names) + self._constants,
            operands=dict(func_def.operand_declarations_dict),
            variables_to_states=initialize_variables_to_state(
                func_def.port_declarations
            ),
            variables_to_types={
                port.name: port.quantum_type for port in func_def.port_declarations
            },
        )
        with self.scoped_visit(scope), self._error_manager.call(func_def.name):
            if len(func_def.body) == 0:
                return
            self.visit(func_def.body)
            with self._error_manager.node_context(func_def.body[-1]):
                for port_decl in func_def.port_declarations:
                    handle_state = self.current_scope.variable_states[port_decl.name]
                    expected_terminal_state = EXPECTED_TERMINAL_STATES.get(
                        port_decl.direction
                    )
                    if (
                        expected_terminal_state is not None
                        and handle_state is not expected_terminal_state
                    ):
                        self._error_manager.add_error(
                            f"At the end of the function, variable {port_decl.name!r} is expected to be {expected_terminal_state.name.lower()} but it isn't"
                        )

    def visit_WithinApply(self, within_apply: WithinApply) -> None:
        initial_variables_to_state = self.current_scope.variable_states.copy()
        scope = StaticScope(
            parameters=self.current_scope.parameters,
            operands=self.current_scope.operands,
            variables_to_states=self.current_scope.variable_states.copy(),
            variables_to_types=self.current_scope.variables_to_types.copy(),
        )
        with self.scoped_visit(scope):
            self.visit(within_apply.compute)
            compute_captured_variables = {
                var
                for var, state in self.current_scope.variable_states.items()
                if var in initial_variables_to_state
                and state != initial_variables_to_state[var]
            }
            self.visit(within_apply.action)
            variables_to_state = self.current_scope.variable_states.copy()
        self.current_scope.variable_states.update(
            {
                var: state
                for var, state in variables_to_state.items()
                if var in self.current_scope.variable_states
                and var not in compute_captured_variables
            }
        )

    def visit_QuantumOperation(self, op: QuantumOperation) -> None:
        with self._error_manager.node_context(op):
            if isinstance(op, QuantumFunctionCall):
                validate_call_arguments(
                    op,
                    {
                        **self._functions_dict,
                        **self.current_scope.operands,
                    },
                )
            elif isinstance(op, InplaceBinaryOperation) and isinstance(
                op.value, HandleBinding
            ):
                check_no_overlapping_quantum_args(
                    [op.target, op.value], op.operation.value
                )
            self._handle_inputs(op.readable_inputs)
            self._handle_outputs(op.readable_outputs)
            self._handle_inouts(op.readable_inouts)
            self.generic_visit(op)

    def visit_VariableDeclarationStatement(
        self, declaration: VariableDeclarationStatement
    ) -> None:
        handle_wiring_state = self.current_scope.variable_states.get(declaration.name)
        if handle_wiring_state is not None:
            self._error_manager.add_error(
                f"Trying to declare a variable of the same name as previously declared variable {declaration.name}"
            )
            return

        self.current_scope.variable_states[declaration.name] = HandleState.UNINITIALIZED
        self.current_scope.variables_to_types[declaration.name] = (
            declaration.quantum_type
        )

    def visit_QuantumLambdaFunction(self, lambda_func: QuantumLambdaFunction) -> None:
        renamed_parameters, renamed_operands, renamed_ports = get_renamed_parameters(
            lambda_func
        )
        scope = StaticScope(
            parameters=self.current_scope.parameters + renamed_parameters,
            operands={**self.current_scope.operands, **renamed_operands},
            variables_to_states={
                **self.current_scope.variable_states.copy(),
                **initialize_variables_to_state(renamed_ports),
            },
            variables_to_types=self.current_scope.variables_to_types
            | {port.name: port.quantum_type for port in renamed_ports},
        )
        with self.scoped_visit(scope):
            self.generic_visit(lambda_func)

    def visit_HandleBinding(self, handle: HandleBinding) -> None:
        resolve_handle(self.current_scope, handle)

    def visit_Expression(self, expr: Expression) -> None:
        if len(self._scope) == 0:
            return
        vrc = VarRefCollector(ignore_duplicated_handles=True, unevaluated=True)
        vrc.visit(ast.parse(expr.expr))
        handles = [
            HandleMetadata(handle=handle)
            for handle in vrc.var_handles
            if handle.name in self.current_scope.variable_states
            and (
                not isinstance(handle, FieldHandleBinding)
                or handle.field not in CLASSICAL_ATTRIBUTES
            )
        ]
        self._handle_inouts(handles)

    def visit_QuantumExpressionOperation(self, op: QuantumExpressionOperation) -> None:
        self.visit_Expression(op.expression)
        self.visit_QuantumOperation(op)

    def _handle_state_changing_ios(
        self,
        ios: Sequence[HandleMetadata],
        state: HandleState,
        state_change_verb: str,
    ) -> None:
        for handle_metadata in ios:
            handle_binding = handle_metadata.handle
            if isinstance(
                handle_binding,
                (SubscriptHandleBinding, SlicedHandleBinding, FieldHandleBinding),
            ):
                self._error_manager.add_error(
                    f"Cannot use {HANDLE_BINDING_PART_MESSAGE[type(handle_binding)]} of variable {handle_binding.name!r} in {state_change_verb} context"
                )
                continue
            handle_wiring_state = self.current_scope.variable_states.get(
                handle_binding.name
            )
            if handle_wiring_state is not state:
                state_prefix = (
                    ""
                    if handle_wiring_state is None
                    else f"{handle_wiring_state.name.lower()} "
                )
                location = (
                    f" {handle_metadata.readable_location}"
                    if handle_metadata.readable_location is not None
                    else ""
                )
                self._error_manager.add_error(
                    f"Cannot use {state_prefix}quantum variable {handle_binding.name!r}"
                    f"{location}"
                )

            self.current_scope.variable_states[handle_binding.name] = ~state

    def _handle_inputs(self, inputs: Sequence[HandleMetadata]) -> None:
        self._handle_state_changing_ios(
            inputs, HandleState.INITIALIZED, "uninitialization"
        )

    def _handle_outputs(self, outputs: Sequence[HandleMetadata]) -> None:
        self._handle_state_changing_ios(
            outputs, HandleState.UNINITIALIZED, "initialization"
        )

    def _handle_inouts(self, inouts: Sequence[HandleMetadata]) -> None:
        for handle_metadata in inouts:
            handle_binding = handle_metadata.handle

            if handle_binding.name not in self.current_scope.variable_states:
                ErrorManager().add_error(
                    f"Variable {handle_binding.name!r} is not defined"
                )
                return
            handle_wiring_state = self.current_scope.variable_states[
                handle_binding.name
            ]

            if handle_wiring_state is not HandleState.INITIALIZED:
                state_prefix = (
                    ""
                    if handle_wiring_state is None
                    else f"{handle_wiring_state.name.lower()} "
                )
                location = (
                    f" {handle_metadata.readable_location}"
                    if handle_metadata.readable_location is not None
                    else ""
                )
                self._error_manager.add_error(
                    f"Cannot use {state_prefix}quantum variable {handle_binding.name!r}"
                    f"{location}"
                )


def static_semantics_analysis_pass(
    model: Model, error_type: Optional[type[Exception]] = ClassiqSemanticError
) -> None:
    QStructAnnotator().visit(model)
    functions = {**BUILTIN_FUNCTION_DECLARATIONS, **model.function_dict}
    resolve_function_calls(model, functions)
    StaticSemanticsVisitor(
        functions,
        [const.name for const in model.constants],
    ).visit(model)
    if error_type is not None:
        ErrorManager().report_errors(error_type)


EXPECTED_TERMINAL_STATES: dict[PortDeclarationDirection, HandleState] = {
    PortDeclarationDirection.Output: HandleState.INITIALIZED,
    PortDeclarationDirection.Inout: HandleState.INITIALIZED,
}


def initialize_variables_to_state(
    port_declarations: Sequence[PortDeclaration],
) -> dict[str, HandleState]:
    variables_to_state: dict[str, HandleState] = dict()

    for port_decl in port_declarations:
        variables_to_state[port_decl.name] = (
            HandleState.INITIALIZED
            if port_decl.direction.includes_port_direction(PortDirection.Input)
            else HandleState.UNINITIALIZED
        )

    return variables_to_state
