import cirq
import pytest

from icm.icm_flag_manipulations import (
    add_decomposition_flags,
    add_op_ids,
    is_op_with_decomposed_flag,
    is_op_with_op_id,
    remove_op_ids,
    reset_decomposition_flags,
    reset_op_ids,
)
