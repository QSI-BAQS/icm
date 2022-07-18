import pytest
from cirq import CNOT, MeasurementGate, T, X

from icm.icm_circuit import ICMCircuit, ICMGateOperation
from icm.split_qubit import SplitQubit

TEST_GATES = [
    (
        ICMGateOperation(T, (SplitQubit("q0"),)),
        [
            ICMGateOperation(CNOT, (SplitQubit("q0"), SplitQubit("anc_0"))),
            ICMGateOperation(MeasurementGate(1), (SplitQubit("q0"),)),
        ],
    ),
    (
        ICMGateOperation(X, (SplitQubit("q0"),)),
        [
            ICMGateOperation(X, (SplitQubit("q0"),)),
        ],
    ),
    (
        ICMGateOperation(CNOT, (SplitQubit("q0"), SplitQubit("q1"))),
        [
            ICMGateOperation(CNOT, (SplitQubit("q0"), SplitQubit("q1"))),
        ],
    ),
]


@pytest.mark.parametrize("gate_operation,target_circuit_gates", TEST_GATES)
def test_compilation_of_individual_gates(gate_operation, target_circuit_gates):
    # if
    icm_circuit = ICMCircuit(gate_operation)
    target_circuit = ICMCircuit(*target_circuit_gates)

    # when
    icm_circuit.compile([gate_operation._gate])

    # then
    assert icm_circuit == target_circuit
