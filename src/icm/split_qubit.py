from typing import List, Optional, Tuple
from warnings import warn

from cirq import NamedQubit

from .icm_operation_id import OperationId


class SplitQubit(NamedQubit):
    """

    Attributes:
        children Tuple[Optional[SplitQubit], Optional[SplitQubit]]:
            This qubits that the qubit are split into by the ICM algorithm.
        threshold (OperationId) : If the children have higher OperationId's
            than this threshold, then the wire is split.

    """

    # Static nr_ancilla
    nr_ancilla = -1

    def __init__(self, name: str):
        super().__init__(name)
        self.children: Tuple[Optional["SplitQubit"], Optional["SplitQubit"]]
        self.children = (None, None)
        self.threshold = OperationId()

    def get_latest_ref(self, operation_id: OperationId) -> "SplitQubit":
        """Update the last id corresponding to the latest child added.

        Args:
            operation_id (OperationId): Operation of the

        Returns:
            SplitQubit: Updated children's OperationId's.
        """
        # this wire has not been split
        if self.children == (None, None):
            return self

        n_ref = self
        for stuck in range(1000):
            # Decide based on the threshold
            if (
                isinstance(n_ref.children[0], OperationId)
                and n_ref.threshold >= operation_id
            ):
                n_ref = n_ref.children[0]
            elif (
                isinstance(n_ref.children[1], OperationId)
                and n_ref.threshold < operation_id
            ):
                n_ref = n_ref.children[1]
            elif n_ref.children == (None, None):
                break
            else:
                TypeError(
                    "Children of SplitQubit up to threshold"
                    " must be defined to split wire."
                )

        if stuck == 999:
            warn(
                f"Error: Got stuck updating reference for qubit {self.name} "
                f"with operation with id : {operation_id.numbers}."
            )

        return n_ref

    def split_this_wire(
        self, operation_id: OperationId
    ) -> Tuple["SplitQubit", "SplitQubit"]:
        """Decompose qubit into it's children.

        Args:
            operation_id (OperationId) : Threshold at which to split qubit.

        Returns:
            Tuple[SplitQubit, SplitQubit]: 2 qubits on which the equivalent operations
                are performed in the ICM format.
        """
        # It can happen that the reference is too old
        current_wire = self.get_latest_ref(operation_id)

        # The wire receives a threshold for latter updates
        current_wire.threshold = operation_id

        # It is a new wire, but keep the old name
        n_child_0 = SplitQubit(current_wire.name)

        # It is a new wire, that is introduced and gets a new name
        SplitQubit.nr_ancilla += 1
        n_child_1 = SplitQubit("anc_{0}".format(SplitQubit.nr_ancilla))

        current_wire.children = (n_child_0, n_child_1)

        # Return the children as a tuple
        return current_wire.children

    def split(self, n: int, opid: OperationId) -> List["SplitQubit"]:
        """
        Split a qubit n times

        This will return a list of qubits [q, anc_0, anc_1,...,anc_n-2],
        where q is split into q and anc_0, anc_0 is split into anc_0 and anc_1
        and so on.

        Args:
            qubit (SplitQubit): Qubit to be split n times.
            n (int): number of times to split qubit.
            opid (OperationId): OperationId at which to split the qubit.

        Returns:
            List[SplitQubit]: List of qubits that qubit was split into.
        """
        wires = [self]

        for i in range(n - 1):
            new_wires = wires[-1].split_this_wire(opid)
            wires[-1] = new_wires[0]
            wires.append(new_wires[1])

        return wires
