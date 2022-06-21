from cirq import Circuit, Gate, Operation

from icm.icm_operation_id import OperationId


def is_op_with_decomposed_flag(op: Operation, gate_type: Gate) -> bool:
    """Tests if op is a gate of the type gate_type and has the
    "decomposed" flag.

    Args:
        op (Operation): operation to test if it is of the required gate
            type and has an attribute called "decomposed"
        gate_type (Gate): The type of gate we testing to see if op is.

    Returns:
        bool: true if op is of the same type as gate_type and has the
            flag "decomposed" and false otherwise.
    """
    if op.gate == gate_type:
        return hasattr(op, "decomposed")
    return False


def reset_decomposition_flags(circuit: Circuit, gate_type: Gate) -> None:
    """For all operations in a circuit, set the decomposition flags with the
    type gate_type to false.

    Args:
        circuit (Circuit): circuit on which we change flags.
        gate_type (Gate): type of gate that we want to change the flag for.
    """
    for op in circuit.all_operations():
        if is_op_with_decomposed_flag(op, gate_type):
            op.decomposed = False


def add_decomposition_flags(circuit: Circuit, gate_type: Gate) -> None:
    """For all operations in a circuit, add the decomposition flags with the
    type gate_type with the value true.

    Args:
        circuit (Circuit): circuit on which we add flags.
        gate_type (Gate): type of gate that we want to add the flag for.
    """
    for op in circuit.all_operations():
        if not is_op_with_decomposed_flag(op, gate_type):
            setattr(op, "decomposed", True)


def remove_decomposition_flags(circuit: Circuit, gate_type: Gate) -> None:
    """For all operations in a circuit, remove the decomposition flags with the
    type gate_type.

    Args:
        circuit (Circuit): circuit on which we remove flags.
        gate_type (Gate): type of gate that we want to remove the flag for.
    """
    for op in circuit.all_operations():
        if is_op_with_decomposed_flag(op, gate_type):
            delattr(op, "decomposed")


def is_op_with_op_id(op: Operation, gate_types: Gate) -> bool:
    """Tests if op is a gate of the type gate_type and has the
    "icm_op_id" flag.

    Args:
        op (Operation): operation to test if it is of the required gate
            type and has an attribute called "icm_op_id"
        gate_type (Gate): The type of gate we testing to see if op is.

    Returns:
        bool: true if op is of the same type as gate_type and has the
            flag "icm_op_id" and false otherwise.
    """
    if op.gate in gate_types:
        return hasattr(op, "icm_op_id")
    return False


def reset_op_ids(circuit: Circuit, gate_types: Gate) -> None:
    remove_decomposition_flags(circuit, gate_types)
    add_decomposition_flags(circuit, gate_types)


def add_op_ids(circuit: Circuit, gate_types: Gate) -> None:
    """Tests if op is a gate of the type gate_type and if it
    is, give it an id. Increments the new ids by 1 for each
    gate of type gate_type the function finds in circuit.

    Args:
        op (Operation): operation to test if it is of the required gate
            type and, if yes, give it an OperationId.
        gate_type (Gate): The type of gate we testing to see if op is.
    """
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
    """For all operations in a circuit, remove the icm_op_id flags for gates
    with the type gate_type.

    Args:
        circuit (Circuit): circuit on which we remove flags.
        gate_type (Gate): type of gate that we want to remove the flag for.
    """
    for op in circuit.all_operations():
        if is_op_with_op_id(op, gate_types):
            delattr(op, "icm_op_id")
