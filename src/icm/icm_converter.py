"""
For this the ICM form of circuits is being implemented. As described in

"Faster manipulation of large quantum circuits using wire label reference
diagrams" https://arxiv.org/abs/1811.06011
"""
from typing import List, Tuple, Union

import cirq
from cirq import CNOT, Circuit, Gate, H, Operation, S, T, Z, measure
from pyparsing import Optional

from . import SplitQubit, icm_flag_manipulations
from . import icm_operation_id as op
from .wire_manipulation import correction_seq, initialise_circuit, split_wires


def icm_circuit(
    circuit: Circuit, gates_to_decomp: List[Gate], inverse=False
) -> Circuit:
    """
    Function that converts an input circuit into icm form

    The decomposition sweeps the circuit using the circuit.all_operations()
    generator method instead of using the intercepting decomposer.

    Input circuit is expected to be have gates [T, T^-1, H, S, S^-1, CNOT] and
    Pauli gates.

    Parameters
    ----------
    circuit : Circuit

    gates_to_decomp: list
        list of gates that need to be decomposed

    inverse : Bool, optional
        If true will produce an inverse icm decomposition
    Returns
    -------
    icm_circuit : Circuit
        The decomposed circuit
    """
    # skips decomposing H and S, S**-1 for inverse icm
    skip = ((H, 1), (S, 0.5), (S, -0.5))
    if inverse:
        gates_to_decomp = [
            gate for gate in gates_to_decomp if not (gate, gate.exponent) in skip
        ]

    circuit = initialise_circuit(circuit)
    icm_flag_manipulations.add_op_ids(circuit, gates_to_decomp)

    decomposed_list = []
    queue = list(circuit.all_operations())

    t_meas_locs = []

    while queue:
        op = queue.pop(0)

        decomp = []
        new_op_id = op.icm_op_id.add_decomp_level()

        # If gate is not in the to be decomposed list, will apply it to
        # the latest reference. For inverse icm, it will apply H to latest
        # without decomposing
        if op.gate not in gates_to_decomp:
            qubits = [q.get_latest_ref(new_op_id) for q in op.qubits]
            decomp = op.gate.on(*qubits)
            decomposed_list.append(decomp)
            continue

        # T and T^-1 decomp
        if op.gate in (T**-1, T):
            #         decomposed_list.append(op)
            #         continue
            # list that holds all wires
            #         new_op_id = op.icm_op_id.add_decomp_level()
            wires = split_wires(op.qubits[0], 6, new_op_id)

            had_locs: Tuple[int, ...]
            t_locs: Tuple[int, ...]
            s_locs: Tuple[int, ...]
            cnot_locs: Tuple[Tuple[int, int], ...]
            meas_locs: Tuple[int, ...]

            # gate locations for icm and inverse icm
            if not inverse:
                had_locs = (1, 3, 4)
                t_locs = (1,)
                s_locs = (3,)
                cnot_locs = ((1, 0), (1, 2), (3, 1), (4, 2), (3, 5), (4, 5))
                meas_locs = tuple(i for i in range(5))
            else:
                had_locs = (3, 4)
                t_locs = ()
                cnot_locs = ((0, 1), (1, 2), (3, 1), (4, 2), (3, 5), (4, 5))
                z_locs = (3,)
                meas_locs = tuple(i for i in range(5))

                # add phase correction for T gates
                if op.gate == T:
                    s_locs = (3, 4)
                else:
                    s_locs = ()

            # Initialise Block
            decomp.append([H(wires[i]) for i in had_locs])
            decomp.append([T(wires[i]) for i in t_locs])
            decomp.append([S(wires[i]) for i in s_locs])

            # CNOT Block
            decomp.append([CNOT(wires[i], wires[j]) for i, j in cnot_locs])

            if inverse:
                # Z correction
                decomp.append([Z(wires[i]) for i in z_locs])

            # Measurement Block
            decomp.append([measure(wires[i]) for i in meas_locs])

            t_meas_locs.append(wires[0])

        # decomp for Hadamard
        if not inverse:
            if op.gate == H:

                # initialise
                wires = [op.qubits[0]]
                #         new_op_id = op.icm_op_id.add_decomp_level()

                # gate locations
                cnot_locs = ((1, 0), (2, 0), (3, 0))
                had_locs = (1, 2, 3)
                s_locs = had_locs
                meas_locs = had_locs

                # split the qubit
                for i in range(3):
                    SplitQubit.nr_ancilla += 1
                    child = SplitQubit("anc_{0}".format(SplitQubit.nr_ancilla))
                    print(child)
                    wires.append(child)
                #             new_wires = wires[0].split_this_wire(new_op_id)
                #             wires[0] = new_wires[0]
                #             wires.append(new_wires[1])

                # Initialise Block
                decomp.append([H(wires[i]) for i in had_locs])
                decomp.append([S(wires[i]) for i in s_locs])
                #         print(decomp[-1])

                # CNOT Block
                decomp.append(
                    [
                        CNOT(wires[i], wires[j].get_latest_ref(new_op_id))
                        for i, j in cnot_locs
                    ]
                )

                # Measurement Block
                decomp.append([measure(wires[i]) for i in meas_locs])

        # Decomp for Phase gate
        if (op.gate == S) and not inverse:

            # initialise
            wires = [op.qubits[0]]
            #         new_op_id = op.icm_op_id.add_decomp_level()

            # gate locations for icm
            cnot_locs = ((1, 0),)
            had_locs = (1,)
            s_locs = had_locs
            meas_locs = had_locs

            # split the qubit
            SplitQubit.nr_ancilla += 1
            child = SplitQubit("anc_{0}".format(SplitQubit.nr_ancilla))
            print(child)
            wires.append(child)

            # Initialise Block
            decomp.append([H(wires[i]) for i in had_locs])
            decomp.append([S(wires[i]) for i in s_locs])

            # CNOT Block
            decomp.append(
                [
                    CNOT(wires[i], wires[j].get_latest_ref(new_op_id))
                    for i, j in cnot_locs
                ]
            )

            # Measurement Block
            decomp.append([measure(wires[i]) for i in meas_locs])

        # if decomp == []:
        #     qubits = [q.get_latest_ref(new_op_id) for q in op.qubits]
        #     decomp = op.gate.on(*qubits)

        decomposed_list.append(decomp)

    circuit = Circuit(decomposed_list)
    setattr(circuit, "meas_seq", (t_meas_locs, correction_seq))
    return circuit


def iicm_circuit(circuit: Circuit, gates_to_decomp: List[Gate]) -> Circuit:
    """
    Function that converts an input circuit into inverse icm form

    The decomposition sweeps the circuit using the circuit.all_operations()
    generator method instead of using the intercepting decomposer.

    Input circuit is expected to be have gates [T, T^-1, H, S, S^-1, CNOT] and
    Pauli gates.

    Parameters
    ----------
    circuit : Circuit

    gates_to_decomp: list
        list of gates that need to be decomposed

    Returns
    -------
    iicm_circuit : Circuit
        The decomposed circuit
    """
    # skips decomposing H and S, S**-1
    skip = ((H, 1), (S, 0.5), (S, -0.5))
    gates_to_decomp = [
        gate for gate in gates_to_decomp if not (gate, gate.exponent) in skip
    ]

    circuit = initialise_circuit(circuit)
    icm_flag_manipulations.add_op_ids(circuit, gates_to_decomp)

    decomposed_list = []
    queue = list(circuit.all_operations())

    t_meas_locs = []

    while queue:
        op = queue.pop(0)

        decomp = []
        new_op_id = op.icm_op_id.add_decomp_level()

        # If gate is not in the to be decomposed list, will apply it to
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

            # if op.gate in (T, ):
            #     #decomp.append(S(wires[1]))

            # Add measurement gate
            decomp.append(measure(wires[0]))

            # Track measured qubits
            t_meas_locs.append(wires[0])

        decomposed_list.append(decomp)

    circuit = Circuit(decomposed_list)
    setattr(circuit, "meas_seq", t_meas_locs)
    return circuit


def decomp_to_icm(cirq_operation: Gate) -> List[Union[CNOT, Operation]]:
    """

    :param cirq_operation:
    :return:
    """

    new_op_id = cirq_operation.icm_op_id.add_decomp_level()

    # Assume for the moment that these are only single qubit operations
    new_wires = cirq_operation.qubits[0].split_this_wire(new_op_id)

    """
        In this version the type of the gate, and the initialisation
        of the qubits is not considered.
    """

    # Create the cnot
    cnot = CNOT(new_wires[0], new_wires[1])
    # Assign a decomposition id, like [old].1
    cnot.icm_op_id = new_op_id.advance_decomp()

    # Create the measurement
    meas = measure(new_wires[0])
    # Because this operation follows the CNOT, has ID from the previous
    # results into something like  [oldid].2
    meas.icm_op_id = cnot.icm_op_id.advance_decomp()

    # new_wires = new_wires[1].split_this_wire(new_op_id)
    #
    # # Create the cnot
    # cnot2 = CNOT(new_wires[1], new_wires[0])
    # # Assign a decomposition id, like [old].1
    # cnot2.icm_op_id = meas.icm_op_id.advance_decomp()
    #
    # return [cnot, meas, cnot2]

    return [cnot, meas]


def keep_icm(cirq_operation: Operation) -> bool:
    """

    :param cirq_operation:
    :return:
    """
    """
        Decompose if the operation is not from the set of the ones to keep
    """
    keep = False

    if isinstance(cirq_operation.gate, (cirq.CNOTPowGate, cirq.measurementGate)):
        keep = True

    """
        Keep the operation if:
        * this is an operation that should be decomposed
        AND
        * is not marked for decomposition
    """
    if not icm_flag_manipulations.is_op_with_op_id(
        cirq_operation, [cirq_operation.gate]
    ):
        keep = True

    if keep:
        # Update the reference to the latest
        nqubits = []
        for i in range(len(cirq_operation.qubits)):
            nqubits.append(cirq_operation.qubits[i].get_latest_ref(op.RIGHT_MOST_OP))
        cirq_operation._qubits = tuple(nqubits)

    return keep


def keep_clifford(op: Operation) -> Optional[bool]:
    """
    ops to keep (clifford + T)
    """
    # if isinstance(op.gate, (HPowGate,
    #                S,
    #                T,
    #                T**-1,
    #                CNOT,
    #                SWAP,
    #                X,
    #                Y,
    #                ZPowGate)):

    if isinstance(
        op.gate,
        (
            cirq.XPowGate,
            cirq.YPowGate,
            cirq.ZPowGate,
            cirq.HPowGate,
            cirq.CNOTPowGate,
            cirq.SwapPowGate,
        ),
    ):
        return True
