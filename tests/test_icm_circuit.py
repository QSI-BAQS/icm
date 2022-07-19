import pytest
from cirq import CNOT, MeasurementGate, T, X

from icm.icm_circuit import ICMCircuit, ICMGateOperation
from icm.split_qubit import SplitQubit

TEST_CIRCUITS = [
    (
        ICMCircuit(ICMGateOperation(T, (SplitQubit("q0"),))),
        ICMCircuit(
            ICMGateOperation(CNOT, (SplitQubit("q0"), SplitQubit("anc_0"))),
            ICMGateOperation(MeasurementGate(1), (SplitQubit("q0"),)),
        ),
    ),
    (
        ICMCircuit(ICMGateOperation(X, (SplitQubit("q0"),))),
        ICMCircuit(
            ICMGateOperation(X, (SplitQubit("q0"),)),
        ),
    ),
    (
        ICMCircuit(ICMGateOperation(CNOT, (SplitQubit("q0"), SplitQubit("q1")))),
        ICMCircuit(
            ICMGateOperation(CNOT, (SplitQubit("q0"), SplitQubit("q1"))),
        ),
    ),
    (
        # This test is probably wrong...
        ICMCircuit(
            ICMGateOperation(T, (SplitQubit("q0"),)),
            ICMGateOperation(T, (SplitQubit("q0"),)),
        ),
        ICMCircuit(
            ICMGateOperation(CNOT, (SplitQubit("q0"), SplitQubit("anc_0"))),
            ICMGateOperation(MeasurementGate(1), (SplitQubit("q0"),)),
            ICMGateOperation(CNOT, (SplitQubit("q0"), SplitQubit("anc_1"))),
            ICMGateOperation(MeasurementGate(1), (SplitQubit("q0"),)),
        ),
    ),
    (
        ICMCircuit(
            ICMGateOperation(T, (SplitQubit("q0"),)),
            ICMGateOperation(T, (SplitQubit("q1"),)),
        ),
        ICMCircuit(
            ICMGateOperation(CNOT, (SplitQubit("q0"), SplitQubit("anc_0"))),
            ICMGateOperation(CNOT, (SplitQubit("q1"), SplitQubit("anc_1"))),
            ICMGateOperation(MeasurementGate(1), (SplitQubit("q0"),)),
            ICMGateOperation(MeasurementGate(1), (SplitQubit("q1"),)),
        ),
    ),
    (
        ICMCircuit(
            ICMGateOperation(T, (SplitQubit("q0"),)),
            ICMGateOperation(CNOT, (SplitQubit("q0"), SplitQubit("q1"))),
        ),
        ICMCircuit(
            ICMGateOperation(CNOT, (SplitQubit("q0"), SplitQubit("anc_0"))),
            ICMGateOperation(MeasurementGate(1), (SplitQubit("q0"),)),
            ICMGateOperation(CNOT, (SplitQubit("q0"), SplitQubit("q1"))),
        ),
    ),
]


@pytest.mark.parametrize("circuit, target_circuit", TEST_CIRCUITS)
def test_circuit_compilation(circuit, target_circuit):
    # if
    circuit.compile([T])

    # then
    assert circuit == target_circuit
