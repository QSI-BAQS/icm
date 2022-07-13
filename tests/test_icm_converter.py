import cirq
import pytest
from cirq import CNOT, Circuit, H, I, Moment, NamedQubit, T, Z, approx_eq, measure
from cirq.testing import assert_same_circuits

from icm.icm_converter import icm_circuit, keep_icm
from icm.split_qubit import SplitQubit

TEST_GATES = [
    (
        T,
        [
            Moment(
                CNOT(NamedQubit("q0"), NamedQubit("anc_0")),
            ),
            Moment(
                measure(NamedQubit("q0")),
            ),
        ],
    ),
]


@pytest.mark.parametrize("gate, target_circuit_moments", TEST_GATES)
def test_icm_converter(gate, target_circuit_moments):
    # if
    qubits = [SplitQubit(f"q{i}") for i in range(3)]
    circuit = Circuit()
    circuit.append(gate(*qubits[0 : gate._num_qubits_()]))
    target_circuit = Circuit()
    target_circuit.append(target_circuit_moments)

    # when
    compiled_circuit = icm_circuit(circuit, [gate])

    # then
    for moment1, moment2 in zip(compiled_circuit, target_circuit):
        breakpoint()
        assert moment1 == moment2


q = [SplitQubit(f"q{i}") for i in range(3)]
[
    Moment([(T**-1).on(q[0]), H(q[1])]),
    Moment([CNOT(q[1], q[0])]),
    Moment([T(q[0]), (T**-1)(q[1])]),
    Moment([CNOT(q[1], q[0])]),
    Moment([H(q[1])]),
],
