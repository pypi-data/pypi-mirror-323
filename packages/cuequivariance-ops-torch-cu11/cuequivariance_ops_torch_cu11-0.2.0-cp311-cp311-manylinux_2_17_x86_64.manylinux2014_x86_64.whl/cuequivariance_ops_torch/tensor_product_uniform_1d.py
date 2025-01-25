# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.


import torch
import torch.nn as nn
from typing import Optional
import cuequivariance_ops_torch._ext as ext
import logging

logger = logging.getLogger(__name__)


def _get_batch_size(ins: list[torch.Tensor]):
    result = None
    for i in ins:
        if i is None:
            continue
        if _is_empty(i):
            continue
        torch._assert(
            len(i.shape) == 3,
            "at the torch.ops level, this kernel expects three-dimensional tensors",
        )
        if i.shape[0] != 1:
            torch._assert(
                result is None or i.shape[0] == result, "mismatch in batch size"
            )
            result = i.shape[0]
    if result is None:
        result = 1
    return result


def _fwd_fake(
    ins: list[torch.Tensor],
    number_of_output_segments: int,
) -> torch.Tensor:

    return torch.empty(
        _get_batch_size(ins),
        number_of_output_segments,
        max(i.shape[2] for i in ins if not _is_empty(i)),
        dtype=ins[0].dtype,
        device=ins[0].device,
    )


def _is_empty(t: torch.Tensor) -> bool:
    return len(t.shape) == 1 and t.shape[0] == 0


def _fwd_impl(
    ins: list[torch.Tensor],
    number_of_output_segments: int,
    number_of_paths: int,
    data: torch.Tensor,
    math_code: int,
) -> torch.Tensor:
    out = _fwd_fake(ins, number_of_output_segments)
    ext.tensor_product_uniform_1d_fwd(
        number_of_paths,
        data.detach().contiguous(),
        math_code,
        [i.detach().contiguous() for i in ins if not _is_empty(i)],
        out,
        torch.cuda.current_stream().cuda_stream,
    )
    return out


def _bwd_fake(ins: list[torch.Tensor], ngs: list[bool]) -> list[torch.Tensor]:
    return tuple(
        [
            torch.empty_like(i) if ng and not _is_empty(i) else None
            for i, ng in zip(ins, ngs)
        ]
    )


def _bwd_impl(
    ins: list[torch.Tensor],
    ngs: list[bool],
    number_of_paths: int,
    data: torch.Tensor,
    math_code: int,
) -> list[torch.Tensor]:
    outs = _bwd_fake(ins, ngs)
    for out in outs:
        if out is not None and out.shape[0] == 1:
            out.zero_()

    if _is_empty(ins[2]):
        ext.tensor_product_uniform_1d_bwd(
            number_of_paths,
            data.detach().contiguous(),
            math_code,
            [ins[i].detach().contiguous() for i in [0, 1, 3]],
            [outs[i] for i in [0, 1]],
            torch.cuda.current_stream().cuda_stream,
        )
    else:
        ext.tensor_product_uniform_1d_bwd(
            number_of_paths,
            data.detach().contiguous(),
            math_code,
            [ins[i].detach().contiguous() for i in [0, 1, 2, 3]],
            [outs[i] for i in [0, 1, 2]],
            torch.cuda.current_stream().cuda_stream,
        )
    return outs


def _bwd_bwd_impl(
    ins: list[torch.Tensor],
    dins: list[torch.Tensor],
    ngs: list[torch.Tensor],
    number_of_paths: int,
    data: torch.Tensor,
    math_code: int,
):
    outs = _bwd_fake(ins, ngs)
    for out in outs:
        if out is not None and out.shape[0] == 1:
            out.zero_()

    if _is_empty(ins[2]):
        ext.tensor_product_uniform_1d_bwd_bwd(
            number_of_paths,
            data.detach().contiguous(),
            math_code,
            [ins[i].detach().contiguous() for i in [0, 1, 3]],
            [dins[i].detach().contiguous() for i in [0, 1]],
            [outs[i] for i in [0, 1, 3]],
            torch.cuda.current_stream().cuda_stream,
        )
    else:
        ext.tensor_product_uniform_1d_bwd_bwd(
            number_of_paths,
            data.detach().contiguous(),
            math_code,
            [ins[i].detach().contiguous() for i in [0, 1, 2, 3]],
            [dins[i].detach().contiguous() for i in [0, 1, 2]],
            [outs[i] for i in [0, 1, 2, 3]],
            torch.cuda.current_stream().cuda_stream,
        )
    return outs


def _fwd_primitive_setup_context(ctx, inputs, output):
    *ins, _, num_paths, data, math_code = inputs
    ctx.num_paths = num_paths
    ctx.math_code = math_code
    ctx.save_for_backward(*ins, data)


def _fwd_primitive_backward(ctx, in3):
    *ins, data = ctx.saved_tensors
    ngs = ctx.needs_input_grad[: len(ins)]
    args = []
    for i, n in zip(ins, ngs):
        args.append(i)
        args.append(n)
    outs = torch.ops.cuequivariance_ops_torch.tensor_product_uniform_4x1d_bwd_primitive(
        *args, in3, ctx.num_paths, data, ctx.math_code
    )
    result = list(outs) + [None, None, None, None, None]
    return tuple(result)


def _bwd_primitive_setup_context(ctx, inputs, output):
    *ins, num_paths, data, math_code = inputs
    ctx.num_paths = num_paths
    ctx.math_code = math_code
    ctx.save_for_backward(*ins[::2], data)


def _bwd_primitive_backward(ctx, *grads):
    *ins, data = ctx.saved_tensors
    ngs = ctx.needs_input_grad[::2][: len(ins)]
    assert len(ins) == len(grads) + 1
    assert len(ngs) == len(grads) + 1
    args = []
    for i, g, n in zip(ins, grads, ngs):
        args.append(i)
        args.append(g)
        args.append(n)
    args.append(ins[-1])
    args.append(ngs[-1])
    outs = torch.ops.cuequivariance_ops_torch.tensor_product_uniform_4x1d_bwd_bwd_primitive(
        *args,
        ctx.num_paths,
        data,
        ctx.math_code,
    )
    result = []
    for o in outs:
        result.append(o)
        result.append(None)
    return *result, None, None


torch.library.define(
    "cuequivariance_ops_torch::tensor_product_uniform_4x1d_fwd_primitive",
    (
        "(Tensor in0, Tensor in1, Tensor in2, int noos, int nop,"
        "Tensor data, int math_code)"
        " -> Tensor"
    ),
)

torch.library.define(
    "cuequivariance_ops_torch::tensor_product_uniform_4x1d_bwd_primitive",
    (
        "(Tensor in0, bool ng0, Tensor in1, bool ng1,"
        "Tensor in2, bool ng2, Tensor in3, int nop, Tensor data, int math_code)"
        " -> "
        "(Tensor? out0, Tensor? out1, Tensor? out2)"
    ),
)

torch.library.define(
    "cuequivariance_ops_torch::tensor_product_uniform_4x1d_bwd_bwd_primitive",
    (
        "(Tensor in0, Tensor din0, bool ng0, Tensor in1, Tensor din1, bool ng1,"
        "Tensor in2, Tensor din2, bool ng2, Tensor in3, bool ng3,"
        "int nop, Tensor data, int math_code)"
        " -> "
        "(Tensor? out0, Tensor? out1, Tensor? out2, Tensor? out3)"
    ),
)


@torch.library.impl(
    "cuequivariance_ops_torch::tensor_product_uniform_4x1d_fwd_primitive", "cuda"
)
def _(
    in0: torch.Tensor,
    in1: torch.Tensor,
    in2: torch.Tensor,
    number_of_output_segments: int,
    number_of_paths: int,
    data: torch.Tensor,
    math_code: int,
) -> torch.Tensor:
    return _fwd_impl(
        [in0, in1, in2], number_of_output_segments, number_of_paths, data, math_code
    )


@torch.library.impl(
    "cuequivariance_ops_torch::tensor_product_uniform_4x1d_bwd_primitive", "cuda"
)
def _(
    in0: torch.Tensor,
    ng0: bool,
    in1: torch.Tensor,
    ng1: bool,
    in2: torch.Tensor,
    ng2: bool,
    in3: torch.Tensor,
    number_of_paths: int,
    data: torch.Tensor,
    math_code: int,
) -> (torch.Tensor, torch.Tensor, torch.Tensor):
    return _bwd_impl(
        [in0, in1, in2, in3], [ng0, ng1, ng2], number_of_paths, data, math_code
    )


@torch.library.impl(
    "cuequivariance_ops_torch::tensor_product_uniform_4x1d_bwd_bwd_primitive", "cuda"
)
def _(
    in0: torch.Tensor,
    din0: torch.Tensor,
    ng0: bool,
    in1: torch.Tensor,
    din1: torch.Tensor,
    ng1: bool,
    in2: torch.Tensor,
    din2: torch.Tensor,
    ng2: bool,
    in3: torch.Tensor,
    ng3: bool,
    number_of_paths: int,
    data: torch.Tensor,
    math_code: int,
) -> (torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor):
    return _bwd_bwd_impl(
        [in0, in1, in2, in3],
        [din0, din1, din2],
        [ng0, ng1, ng2, ng3],
        number_of_paths,
        data,
        math_code,
    )


@torch.library.register_fake(
    "cuequivariance_ops_torch::tensor_product_uniform_4x1d_fwd_primitive"
)
def _(
    in0: torch.Tensor,
    in1: torch.Tensor,
    in2: torch.Tensor,
    number_of_output_segments: int,
    number_of_paths: int,
    data: torch.Tensor,
    math_code: int,
) -> torch.Tensor:
    return _fwd_fake([in0, in1, in2], number_of_output_segments)


@torch.library.register_fake(
    "cuequivariance_ops_torch::tensor_product_uniform_4x1d_bwd_primitive"
)
def _(
    in0: torch.Tensor,
    ng0: bool,
    in1: torch.Tensor,
    ng1: bool,
    in2: torch.Tensor,
    ng2: bool,
    in3: torch.Tensor,
    number_of_paths: int,
    data: torch.Tensor,
    math_code: int,
) -> (torch.Tensor, torch.Tensor, torch.Tensor):
    return _bwd_fake([in0, in1, in2, in3], [ng0, ng1, ng2])


@torch.library.register_fake(
    "cuequivariance_ops_torch::tensor_product_uniform_4x1d_bwd_bwd_primitive"
)
def _(
    in0: torch.Tensor,
    din0: torch.Tensor,
    ng0: bool,
    in1: torch.Tensor,
    din1: torch.Tensor,
    ng1: bool,
    in2: torch.Tensor,
    din2: torch.Tensor,
    ng2: bool,
    in3: torch.Tensor,
    ng3: bool,
    number_of_paths: int,
    data: torch.Tensor,
    math_code: int,
) -> (torch.Tensor, torch.Tensor, torch.Tensor):
    return _bwd_fake([in0, in1, in2, in3], [ng0, ng1, ng2, ng3])


torch.library.register_autograd(
    "cuequivariance_ops_torch::tensor_product_uniform_4x1d_fwd_primitive",
    _fwd_primitive_backward,
    setup_context=_fwd_primitive_setup_context,
)

torch.library.register_autograd(
    "cuequivariance_ops_torch::tensor_product_uniform_4x1d_bwd_primitive",
    _bwd_primitive_backward,
    setup_context=_bwd_primitive_setup_context,
)


class TensorProductUniform1d(nn.Module):
    SUPPORTED_DIMS = [3, 4]
    SUPPORTED_EXTENT_MULTIPLE = 32
    SUPPORTED_TOTAL_SEGMENTS = 256

    @classmethod
    def is_supported(
        cls,
        operand_dim: list[int],
        operand_extent: int,
        operand_num_segments: list[int],
    ):
        """
        Check if the kernel supports operations with the given parameters.

        See ``__init__`` for a description of the paramters.
        """
        num_operands = len(operand_num_segments)
        try:
            assert num_operands in cls.SUPPORTED_DIMS
            assert len(operand_dim) == num_operands
            assert (
                operand_extent % TensorProductUniform1d.SUPPORTED_EXTENT_MULTIPLE == 0
            )
            assert (
                sum(operand_num_segments)
                <= TensorProductUniform1d.SUPPORTED_TOTAL_SEGMENTS
            )
        except AssertionError:
            return False
        return True

    def __init__(
        self,
        operand_dim: list[int],
        operand_extent: int,
        operand_num_segments: list[int],
        path_indices: list[list[int]],
        path_coefficients: list[float],
        math_dtype: torch.dtype = torch.float32,
    ):
        """
        A tensor product implementation for scalar and vector operands where
        all vectors have the same length.

        Parameters
        ----------
        operand_dim: list[int]
            ``operand_dim[i]`` may be either 0 or 1, and indicates whether that
            operand ``i`` has scalar (0-dimensional) or vector (1-dimensional)
            segments.
        operand_extent: int
            The extent (number of elements) of each vector operand segment. Must
            be a multiple of ``SUPPORTED_EXTENT_MULTIPLE``.
        operand_num_segments: list[int]
            The number of segments for each operand.
        path_indices: list[list[int]]
            Each element of this list is a single computation, i.e. which input
            operands get multiplied together and then and added to which output
            segment.
        path_coefficients: list[float]
            The scaling factor for each entry in ``path_indices``.
        math_dtype: torch.dtype
            The data type used for internal computation. May be FP32 or FP64.
            All inputs will be cast to this type, and all multiplications and
            additions will be performed at this precision (except for atomic
            output accumulation, which occurs at input precision).

        Example
        -------
        For this example, let's say that we use this kernel to implement
        complex-complex multiplication, i.e. two inputs, one output
        (three operands total) and two segments each (real and imaginary).
        Then, this would encode the multiplication rule:

        >>> m = TensorProductUniform1d(
        ...        [1, 1, 1], 32, [2, 2, 2],
        ...        [[0, 0, 0], [1, 1, 0], [1, 0, 1], [0, 1, 1]],
        ...        [1.0, -1.0, 1.0, 1.0])

        This encodes the following operation with plain torch:

        >>> input_0_segment_0 = torch.randn((batch, 32,))
        >>> input_0_segment_1 = torch.randn((batch, 32,))
        >>> input_1_segment_0 = torch.randn((batch, 32,))
        >>> input_1_segment_1 = torch.randn((batch, 32,))
        >>> output_segment_0 = input_0_segment_0 * input_1_segment_0 - \
        ...     input_0_segment_1 * input_1_segment_1
        >>> output_segment_1 = input_0_segment_0 * input_1_segment_1 + \
        ...     input_0_segment_1 * input_1_segment_0

        Or, using our kernel:

        >>> input_0 = torch.randn((batch, 2*32), device='cuda')
        >>> input_1 = torch.randn((batch, 2*32), device='cuda')
        >>> m = m.to('cuda')
        >>> output = m(input_0, input_1)

        """
        assert TensorProductUniform1d.is_supported(
            operand_dim, operand_extent, operand_num_segments
        )
        assert len(path_indices) == len(path_coefficients)
        assert len(path_coefficients) > 0
        self.num_operands = len(operand_num_segments)
        assert len(path_indices[0]) == self.num_operands
        logger.debug(
            "TensorProductUniform4x1d.__init__("
            + f"operand_dim={operand_dim}, operand_extent={operand_extent}, "
            + f"operand_num_segments={operand_num_segments}, path_indices=..., "
            + f"path_coefficients=..., math_dtype={math_dtype})"
        )
        logger.debug(
            f"TensorProductUniform4x1d.__init__(path_indices={path_indices}, "
            + f"path_coefficients={path_coefficients})"
        )

        super().__init__()

        self.number_of_output_segments = operand_num_segments[-1]
        self.number_of_paths = len(path_indices)
        self.math_dtype = math_dtype

        self.operand_dim = operand_dim
        self.operand_extent = operand_extent
        self.operand_num_segments = operand_num_segments
        self.path_indices = path_indices
        self.path_coefficients = path_coefficients

        data, math_code = ext.tensor_product_uniform_1d_get_data(
            torch.empty((), dtype=math_dtype),
            operand_extent,
            operand_num_segments,
            self.number_of_paths,
            path_indices,
            path_coefficients,
        )
        data = torch.tensor(data, dtype=torch.uint8).view(dtype=torch.int32)
        self.register_buffer("data", data, persistent=True)
        self.math_code = math_code
        self.segment_len = [
            max(1, self.operand_dim[idx] * self.operand_extent)
            for idx in range(len(self.operand_dim) - 1)
        ]
        self.out_last_dim = self.operand_num_segments[-1] * max(
            1, self.operand_dim[-1] * self.operand_extent
        )

    def forward(
        self, in0: torch.Tensor, in1: torch.Tensor, in2: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Execute the TensorProductUniform1d kernel.

        For an example, see ``__init__``.

        Each operand is a torch tensor with one or two dimensions. If it is two-
        dimensional, the first dimension is the batch dimension and must match
        across all input tensors that have a batch dimension. It will also be
        the first dimension of the returned tensor.
        Generally, a sufficiently large batch dimension is required for good
        performance. The last tensor dimension contains all the segments of the
        operand packed together, so it is of size
        ``operand_num_segments[i] * operand_extent`` for vector operands (i.e.,
        where ``operand_dim[i] == 1``) or just ``operand_num_segments[i]`` for
        scalar operands.

        Parameters
        ----------
        in0: torch.Tensor
            The first operand of the tensor product.
        in1: torch.Tensor
            The second operand of the tensor product.
        in2: torch.Tensor
            The third operand of the tensor product. Required for 4-dimensional
            tensor products, ignored for 3-dimensional tensor products.

        Returns
        -------
        torch.Tensor
            The last (output) operand of the tensor product.
        """

        if in2 is None:
            in2 = torch.empty((0,), dtype=in0.dtype, device=in0.device)

        ins = [
            in0,
            in1,
            in2,
        ]

        for i in range(len(self.operand_dim) - 1):
            ins[i] = ins[i].reshape(
                ins[i].shape[0], self.operand_num_segments[i], self.segment_len[i]
            )

        for i in ins:
            torch._assert(ins[0].dtype == i.dtype, "tensors must have same type")
        out = torch.ops.cuequivariance_ops_torch.tensor_product_uniform_4x1d_fwd_primitive(
            ins[0],
            ins[1],
            ins[2],
            self.number_of_output_segments,
            self.number_of_paths,
            self.data,
            self.math_code,
        )
        if not torch.jit.is_scripting() and not torch.compiler.is_compiling():
            logger.debug(
                "TensorProductUniform4x1d.forward("
                + f"in0.shape={in0.shape}, in0.dtype={in0.dtype}, "
                + f"in1.shape={in1.shape}, in1.dtype={in1.dtype}, "
                + f"in2.shape={in2.shape if len(self.operand_dim) == 4 else ''}, "
                + f"in2.dtype={in2.dtype if len(self.operand_dim) == 4 else ''}, "
                + f"out.shape={out.shape}, out.dtype={out.dtype})"
            )
        return out.reshape(out.shape[0], self.out_last_dim)


TensorProductUniform4x1d = TensorProductUniform1d

__all__ = ["TensorProductUniform4x1d", "TensorProductUniform1d"]
