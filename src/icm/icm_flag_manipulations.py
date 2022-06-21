from cirq import Circuit, Gate, Operation

from icm.icm_operation_id import OperationId

"""
    FLAG MANIPULATIONS
"""


def is_op_with_decomposed_flag(op: Operation, gate_type: Gate) -> bool:
    if op.gate == gate_type:
        return hasattr(op, "decomposed")
    return False


def reset_decomposition_flags(circuit: Circuit, gate_type: Gate) -> None:
    for op in circuit.all_operations():
        if is_op_with_decomposed_flag(op, gate_type):
            op.decomposed = False


def add_decomposition_flags(circuit: Circuit, gate_type: Gate) -> None:
    for op in circuit.all_operations():
        if not is_op_with_decomposed_flag(op, gate_type):
            setattr(op, "decomposed", True)


def remove_decomposition_flags(circuit: Circuit, gate_type: Gate) -> None:
    for op in circuit.all_operations():
        if is_op_with_decomposed_flag(op, gate_type):
            delattr(op, "decomposed")


"""
opid
"""


def is_op_with_op_id(op: Operation, gate_types: Gate) -> bool:
    if op.gate in gate_types:
        return hasattr(op, "icm_op_id")
    return False


def reset_op_ids(circuit: Circuit, gate_types: Gate) -> None:
    remove_decomposition_flags(circuit, gate_types)
    add_decomposition_flags(circuit, gate_types)


def add_op_ids(circuit: Circuit, gate_types: Gate) -> None:
    nr_op = 0
    for op in circuit.all_operations():
        if not is_op_with_op_id(op, gate_types):
            # # Condition to prevent opid being added to all ops
            # if op.gate in gate_types:
            setattr(op, "icm_op_id", OperationId(nr_op))
            # increase the id
            nr_op += 1
            # print(nr_op)


def remove_op_ids(circuit: Circuit, gate_types: Gate) -> None:
    for op in circuit.all_operations():
        if is_op_with_op_id(op, gate_types):
            delattr(op, "icm_op_id")
