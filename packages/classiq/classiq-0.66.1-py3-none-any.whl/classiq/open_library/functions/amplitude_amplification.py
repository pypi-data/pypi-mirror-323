from classiq.open_library.functions.grover import grover_operator
from classiq.qmod.builtins.functions.standard_gates import RY
from classiq.qmod.builtins.operations import (
    allocate,
    bind,
    control,
    repeat,
    within_apply,
)
from classiq.qmod.cparam import CInt, CReal
from classiq.qmod.qfunc import qfunc
from classiq.qmod.qmod_variable import QArray, QBit
from classiq.qmod.quantum_callable import QCallable
from classiq.qmod.symbolic import acos, asin, ceiling, pi, sin


@qfunc
def amplitude_amplification(
    reps: CInt,
    oracle: QCallable[QArray[QBit]],
    space_transform: QCallable[QArray[QBit]],
    packed_qvars: QArray[QBit],
) -> None:
    """
    [Qmod Classiq-library function]

    Applies the Amplitude Amplification algorithm (QAE); Prepares a state using the given `space_transform` function, and applies `reps` repetititions
    of the grover operator, using the given `oracle` functions which marks the "good" states.

    Args:
        reps: Number of repetitions to apply the grover operator on the initial state. Should be determined by the user, according to the calculated amplification.
        oracle: The oracle operator that marks the "good" states. This operator should flip the sign of the amplitude of the "good" state.
        space_transform: The space transform operator (which is known also the state preparation operator). First applied to prepare the state before the amplification, then used inside the Grover operator.
        packed_vars: The variable that holds the state to be amplified. Assumed to be in the zero state at the beginning of the algorithm.
    """
    space_transform(packed_qvars)
    repeat(reps, lambda index: grover_operator(oracle, space_transform, packed_qvars))


@qfunc
def exact_amplitude_amplification(
    amplitude: CReal,
    oracle: QCallable[QArray[QBit]],
    space_transform: QCallable[QArray[QBit]],
    packed_qvars: QArray[QBit],
) -> None:
    """
    [Qmod Classiq-library function]

    Applies an exact version of the Amplitude Amplification algorithm (QAE), assuming knowledge of the amplitude of the marked state.
    The function should be applied on the zero state, and it takes care for preparing the initial state before amplification using the `space_transform`.

    Based on the algorithm in [Quantum state preparation without coherent arithmetic](https://arxiv.org/abs/2210.14892).

    Assuming the `space_transform` creates a state $|\\psi\rangle = a|\\psi_good\rangle + \\sqrt(1-a)|\\psi_bad\rangle$, given `a` as the `amplitude`
    argument, the function will load exactly the state $|\\psi_good\rangle$.

    Note: if the `amplitude` argument is not exact, the resulting state will not be exactly $|\\psi_good\rangle$, and there will be additional internal auxilliary of the function that is not released correctly.

    Args:
        amplitude: The amplitude of the state $|\\psi_good\rangle$ with regards to the initial state prepared by.
        oracle: The oracle operator that marks the "good" states. This operator should flip the sign of the amplitude of the "good" state.
        space_transform: The space transform operator (which is known also the state preparation operator). First applied to prepare the state before the amplification, then used inside the Grover operator.
        packed_vars: The variable that holds the state to be amplified. Assumed to be in the zero state at the beginning of the algorithm.
    """
    aux = QBit()
    k = ceiling((pi / (4 * asin(amplitude))) - 0.5)
    theta = pi / (4 * k + 2)
    rot_phase = 2 * acos(sin(theta) / amplitude)

    extended_qvars: QArray = QArray("extended_qvars")
    within_apply(
        lambda: [  # type:ignore[arg-type]
            allocate(aux),
            bind(
                [aux, packed_qvars], extended_qvars
            ),  # type:ignore[func-returns-value]
        ],
        lambda: amplitude_amplification(
            k,
            lambda qvars_: control(
                qvars_[0] == 0, lambda: oracle(qvars_[1 : qvars_.size])
            ),
            lambda qvars_: [
                space_transform(  # type:ignore[func-returns-value]
                    qvars_[1 : qvars_.size]
                ),
                RY(rot_phase, qvars_[0]),
            ],
            extended_qvars,
        ),
    )
