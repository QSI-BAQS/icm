"""
For this the ICM form of circuits is being implemented. As described in

"Faster manipulation of large quantum circuits using wire label reference
diagrams" https://arxiv.org/abs/1811.06011
"""
from typing import List

import cirq
from cirq import CNOT, Circuit, Gate, H, Operation, S, T, measure

from .icm_operation import add_op_ids, is_op_with_op_id
from .icm_operation_id import RIGHT_MOST_OP
from .wire_manipulation import initialise_circuit, split_wires


def icm_circuit(circuit: Circuit, gates_to_decomp: List[Gate]) -> Circuit:
    """
    Function that converts an input circuit into inverse icm form. We implement
    Cliffords through initialization and CNOT, but T gates are implemented via
    non-clifford measurements (teleportation).

    The decomposition sweeps the circuit using the circuit.all_operations()
    generator method instead of using the intercepting decomposer.

    Input circuit is expected to be have gates [H, S, S^-1, CNOT] and
    Pauli gates.

    Parameters
    ----------
    circuit : Circuit
        circuit to be put in icm form

    gates_to_decomp: list
        list of gates that need to be decomposed

    Returns
    -------
    icm_circuit : Circuit
        The decomposed circuit
    """
    # skips decomposing H and S, S**-1
    skip = ((H, 1), (S, 0.5), (S, -0.5))
    gates_to_decomp = [
        gate for gate in gates_to_decomp if not (gate, gate.exponent) in skip
    ]

    circuit = initialise_circuit(circuit)
    add_op_ids(circuit, gates_to_decomp)

    decomposed_list = []
    queue = list(circuit.all_operations())

    t_meas_locs = []

    while queue:
        op = queue.pop(0)

        decomp = []
        new_op_id = op.icm_op_id.add_decomp_level()

        # If gate is not in the to be decomposed list, apply it to
        # the latest reference.
        if op.gate not in gates_to_decomp:
            qubits = [q.get_latest_ref(new_op_id) for q in op.qubits]
            decomp = op.gate.on(*qubits)
            decomposed_list.append(decomp)
            continue

        # T and T^-1 decomp
        if op.gate in (T**-1, T):
            wires = split_wires(op.qubits[0], 2, new_op_id)

            # Add CNOTS
            decomp.append(CNOT(wires[0], wires[1]))

            # Add measurement gate
            decomp.append(measure(wires[0]))

            # Track qubits which are measured to implement T gates
            t_meas_locs.append(wires[0])

        decomposed_list.append(decomp)

    circuit = Circuit(decomposed_list)
    setattr(circuit, "meas_seq", t_meas_locs)  # may or may not be needed
    return circuit


def keep_icm(cirq_operation: Operation) -> bool:
    """
    Determine if an operation should be decomposed into an ICM circuit.

    Decompose if the operation is not from the set of the ones to keep

    Keep the operation if:
        * this operation that should be decomposed
        AND
        * is not marked for decomposition

    Parameters
    ----------
    cirq_operation :
        Operation which we may want to decompose.

    Returns
    -------
    keep :
        Boolean value which is true if the gate should not be decomposed
        false if the gate should be decomposed.
    """
    keep = False

    if isinstance(cirq_operation.gate, (cirq.CNOTPowGate, cirq.measurementGate)):
        keep = True

    if not is_op_with_op_id(cirq_operation, [cirq_operation.gate]):
        keep = True

    if keep:
        # Update the reference to the latest
        nqubits = []
        for i in range(len(cirq_operation.qubits)):
            nqubits.append(cirq_operation.qubits[i].get_latest_ref(RIGHT_MOST_OP))
        cirq_operation._qubits = tuple(nqubits)

    return keep


def keep_clifford(op: Operation) -> bool:
    """_summary_

    Args:
        op (Operation): _description_

    Returns:
        Optional[bool]: _description_
    """
    if isinstance(
        op.gate,
        (
            cirq.XPowGate,
            cirq.YPowGate,
            cirq.ZPowGate,
            cirq.HPowGate,
            cirq.CNotPowGate,
            cirq.SwapPowGate,
        ),
    ):
        return True
    return False
