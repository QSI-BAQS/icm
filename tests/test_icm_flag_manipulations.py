import cirq
import pytest
from ..src.icm.icm_flag_manipulations import (
    is_op_with_decomposed_flag,
    reset_decomposition_flags,
    add_decomposition_flags,
    is_op_with_op_id,
    reset_op_ids,
    add_op_ids,
    remove_op_ids,
)
