from typing import List

from cirq import Circuit, Gate, Operation

from .icm_operation_id import OperationId
from .split_qubit import SplitQubit


class ICMOperation(Operation):
    """Operation with OperationId built in that only works on
    SplitQubits.
    """

    def __init__(self, operation: Operation) -> None:
        self.icm_op_id = None
        self.decomposed = None

        # replace qubits with SplitQubits
        new_qubits = [SplitQubit(str(qubit_id)) for qubit_id in list(operation.qubits)]
        self.operation = operation.gate.on(*new_qubits)

    def has_decomposed_flag(self, gate_type: Gate) -> bool:
        """Returns true op is a gate of the type gate_type and has the
        "decomposed" flag.

        Args:
            op (Operation): operation to test if it is of the required gate
                type and has an attribute called "decomposed"
            gate_type (Gate): The type of gate we testing to see if op is.

        Returns:
            bool: true if op is of the same type as gate_type and has the
                flag "decomposed" and false otherwise.
        """
        if self.operation.gate == gate_type:
            return self.decomposed != None
        return False

    def has_op_id(self, gate_types: List[Gate]) -> bool:
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
        if self.operation.gate in gate_types:
            return self.icm_op_id != None
        return False


class ICMCircuit(Circuit):
    def __init__(self, operations: List[Operation]) -> None:
        super().__init__([ICMOperation(op) for op in operations])

    def reset_decomposition_flags(self, gate_type: Gate) -> None:
        """For all operations in a circuit, set the decomposition flags with the
        type gate_type to false.

        Args:
            circuit (Circuit): circuit on which we change flags.
            gate_type (Gate): type of gate that we want to change the flag for.
        """
        for op in self.all_operations():
            if self.decomposed_flag(op, gate_type):
                op.decomposed = False

    def add_decomposition_flags(self, gate_type: Gate) -> None:
        """For all operations in a circuit, add the decomposition flags with the
        type gate_type with the value true.

        Args:
            circuit (Circuit): circuit on which we add flags.
            gate_type (Gate): type of gate that we want to add the flag for.
        """
        for op in self.all_operations():
            if not op.decomposed != None:
                op.decomposed = True

    def remove_decomposition_flags(self, gate_type: Gate) -> None:
        """For all operations in a circuit, remove the decomposition flags with the
        type gate_type.

        Args:
            circuit (Circuit): circuit on which we remove flags.
            gate_type (Gate): type of gate that we want to remove the flag for.
        """
        for op in self.all_operations():
            op.decomposed = None

    def reset_op_ids(self, gate_types: Gate) -> None:
        self.remove_decomposition_flags(gate_types)
        self.add_decomposition_flags(gate_types)

    def add_op_ids(self, gate_types: Gate) -> None:
        """Tests if op is a gate of the type gate_type and if it
        is, give it an id. Increments the new ids by 1 for each
        gate of type gate_type the function finds in circuit.

        Args:
            op (Operation): operation to test if it is of the required gate
                type and, if yes, give it an OperationId.
            gate_type (Gate): The type of gate we testing to see if op is.
        """
        nr_op = 0
        for op in self.all_operations():
            if not op.has_op_id(gate_types):
                # # Condition to prevent opid being added to all ops
                # if op.gate in gate_types:
                op.icm_op_id = OperationId(nr_op)
                # increase the id
                nr_op += 1
                # print(nr_op)

    def remove_op_ids(self, gate_types: Gate) -> None:
        """For all operations in a circuit, remove the icm_op_id flags for gates
        with the type gate_type.

        Args:
            circuit (Circuit): circuit on which we remove flags.
            gate_type (Gate): type of gate that we want to remove the flag for.
        """
        for op in self.all_operations():
            if op.has_op_id(gate_types):
                op.icm_op_id = None
