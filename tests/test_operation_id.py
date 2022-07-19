from icm.operation_id import OperationId


def test_add_decomp_level():
    op_id = OperationId((0,))
    op_id_target = OperationId(
        (
            0,
            0,
        )
    )
    op_id = op_id.add_decomp_level()

    assert op_id.numbers == op_id_target.numbers


def test_advance_decomp():
    op_id = OperationId((0,))
    op_id = op_id.advance_decomp()

    op_id_target = OperationId((1,))

    assert op_id.numbers == op_id_target.numbers
