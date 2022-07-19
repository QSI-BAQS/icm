import itertools
from typing import Iterator, List, Optional, Sequence, Tuple, TypeVar, Union

from cirq import (
    CNOT,
    OP_TREE,
    Circuit,
    Gate,
    GateOperation,
    H,
    InsertStrategy,
    MeasurementGate,
    Moment,
    NamedQubit,
    Operation,
    S,
    T,
)
from cirq.ops import EigenGate

from .operation_id import OperationId
from .split_qubit import SplitQubit

TSelf = TypeVar("TSelf", bound="ICMGateOperation")


class ICMGateOperation(GateOperation):
    """Operation with OperationId built in that only works on
    SplitQubits.
    """

    def __init__(
        self,
        gate: Gate,
        qubits: Sequence[Union[NamedQubit, SplitQubit]],
        icm_op_id: Optional[OperationId] = None,
    ) -> None:
        self.icm_op_id = icm_op_id
        # Recreation of __init__ of GateOperation
        self._gate: Gate = gate
        self._qubits: Tuple[SplitQubit, ...] = tuple(
            SplitQubit(qubit.name) for qubit in qubits
        )

    @property
    def qubits(self) -> Tuple[SplitQubit, ...]:
        """The qubits targeted by the operation."""
        return self._qubits

    def with_qubits(  # type: ignore
        self, *new_qubits: SplitQubit
    ) -> "ICMGateOperation":
        return ICMGateOperation(self.gate, new_qubits, self.icm_op_id)

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
        if self.gate in gate_types:
            return self.icm_op_id is not None
        return False


def _ensure_only_icm_gate_operations(operations: Union[Moment, OP_TREE]) -> None:
    """Checks that every Gate operation in an iterable is an ICMGateOperation.

    Args:
        operations (Union[Moment, OP_TREE]): Operations to check if they are
            ICMGateOperations.

    Raises:
        TypeError: If there is an operation in operations which is not a
            ICMGateOperation.
    """
    operations = itertools.chain.from_iterable(  # flatten iterable
        operations  # type: ignore
    )
    for op in operations:
        if not isinstance(op, ICMGateOperation):
            raise TypeError(
                f"Cannot append operation with type {type(op).__name__} "
                "to ICMCircuit. ICMCircuits consist only of ICMGateOperations."
            )


class ICMCircuit(Circuit):
    """Circuit which only has ICMGateOperations."""

    def __init__(
        self,
        *contents: OP_TREE,
        strategy: InsertStrategy = InsertStrategy.EARLIEST,
    ) -> None:
        self.t_meas_locs: Optional[List[SplitQubit]] = None
        super().__init__(contents, strategy=strategy)

    def all_operations(self) -> Iterator[ICMGateOperation]:
        all_ops = []
        for moment in self:
            for op in moment.operations:
                if isinstance(op, ICMGateOperation):
                    all_ops.append(op)
                else:
                    TypeError("ICMCircuit must only contain ICMGateOperations")
        return iter(all_ops)

    def insert(
        self,
        index: int,
        moment_or_operation_tree: Union[Moment, OP_TREE],
        strategy: InsertStrategy = InsertStrategy.EARLIEST,
    ) -> int:
        """Appends operations onto the end of the circuit.
        Moments within the operation tree are appended intact.
        Overridden here for typing purposes
        Args:
            moment_or_operation_tree: The moment or operation tree to append.
            strategy: How to pick/create the moment to put operations into.
        """
        _ensure_only_icm_gate_operations(moment_or_operation_tree)
        return super().insert(index, moment_or_operation_tree, strategy=strategy)

    def add_op_ids(self, gate_types: List[Gate]) -> None:
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
                op.icm_op_id = OperationId(nr_op)
                # increase the id for each new gate
                nr_op += 1

    def compile(self, raw_gates_to_decomp: List[EigenGate]) -> None:
        """
        Put self into inverse icm form. We implement Cliffords through initialization
        and CNOT, but T gates are implemented via non-clifford measurements
        (i.e. teleportation).

        The decomposition sweeps the circuit using the circuit.all_operations()
        generator method instead of using the intercepting decomposer.

        Input circuit is expected to be have gates [H, S, S^-1, CNOT] and
        Pauli gates. However H and S, S**-1 are skipped for decomposition.

        Parameters
        ----------
        gates_to_decomp: list
            list of gates that need to be decomposed in self.
        """
        SplitQubit.nr_ancilla = -1  # reset ancilla labels
        skip = ((H, 1), (S, 0.5), (S, -0.5))
        gates_to_decomp: List[Gate] = [
            gate for gate in raw_gates_to_decomp if not (gate, gate.exponent) in skip
        ]

        self.add_op_ids(gates_to_decomp)

        decomposed_circuit_ops: List[Operation] = []

        t_meas_locs = []

        for op in self.all_operations():

            decomp: List[Operation] = []
            if op.icm_op_id is None:
                TypeError("OperationID must be defined for all gates in ICM circuit.")
            else:
                new_op_id = op.icm_op_id.add_decomp_level()

            # If gate is not in gates_to_decomp, apply it to the latest reference.
            if op.gate not in gates_to_decomp:
                qubits = [q.get_latest_ref(new_op_id) for q in op.qubits]
                decomp.append(op.with_qubits(*qubits))

            # T and T^-1 decomp using measurement-based magic state injection
            if op.gate in (T**-1, T):
                wires = op.qubits[0].split(2, new_op_id)
                decomp.append(ICMGateOperation(CNOT, (wires[0], wires[1])))
                decomp.append(ICMGateOperation(MeasurementGate(1), (wires[0],)))
                t_meas_locs.append(wires[0])

            decomposed_circuit_ops += decomp

        self.__init__(*decomposed_circuit_ops)  # type: ignore
        self.t_meas_locs = t_meas_locs  # may or may not be needed
