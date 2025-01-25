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
from functools import cmp_to_key
from typing import List

from cuequivariance_ops_torch.utils import (
    maybe_detach,
    get_operator_from_module,
)

import cuequivariance_ops_torch._ext as ops


def _cmp_indices_tuples(a, b):
    if a[1][0] > b[1][0]:
        return 1
    elif a[1][0] == b[1][0]:
        if len(a[1]) < len(b[1]):
            return -1
        elif len(a[1]) == len(b[1]):
            return 0
        else:
            return 1
    else:
        return -1


def _matricization(path_vals, path_indices, num_out_segments, correlation, alignment):
    path_padded_vals = torch.tensor([], dtype=torch.float64)
    path_padded_indices = torch.tensor([], dtype=torch.int32)

    path_offsets = torch.zeros(2 * num_out_segments, dtype=torch.int32)

    sorted_vals_indices = sorted(
        zip(path_vals, path_indices), key=cmp_to_key(_cmp_indices_tuples)
    )

    curr_output = -1
    path_start, path_end, path_num = 0, 0, 0

    for path_val, path_index in sorted_vals_indices:

        if len(path_index) > correlation + 2:
            raise AssertionError("Invalid length of index tuple")

        if curr_output == -1:

            curr_output = path_index[0]
            path_num = 1

        elif curr_output == path_index[0]:

            path_num = path_num + 1

        elif curr_output != path_index[0]:

            path_end = path_start + path_num
            path_offsets[2 * curr_output + 0] = path_start
            path_offsets[2 * curr_output + 1] = path_end

            num_padded = (
                (path_num + alignment - 1) // alignment
            ) * alignment - path_num

            for i in range(0, num_padded):
                path_padded_vals = torch.cat(
                    (path_padded_vals, torch.tensor([0], dtype=torch.float64))
                )
                path_padded_indices = torch.cat(
                    (
                        path_padded_indices,
                        torch.tensor([0] * (correlation + 1), dtype=torch.int32),
                    )
                )

            path_num = 1
            path_start = path_end + num_padded
            path_end = path_start

            curr_output = path_index[0]

        else:
            raise AssertionError(
                "Unexpected value of curr_output and path index",
                curr_output,
                path_index,
            )

        path_padded_vals = torch.cat(
            (path_padded_vals, torch.tensor([path_val], dtype=torch.float64))
        )

        index = (
            path_index[1:-1]
            + [-1] * (correlation - len(path_index[1:-1]))
            + [path_index[-1]]
        )

        path_padded_indices = torch.cat(
            (path_padded_indices, torch.tensor(index, dtype=torch.int32))
        )

    if curr_output != -1:
        num_padded = ((path_num + alignment - 1) // alignment) * alignment - path_num

        for i in range(0, num_padded):
            path_padded_vals = torch.cat(
                (path_padded_vals, torch.tensor([0], dtype=torch.float64))
            )
            path_padded_indices = torch.cat(
                (
                    path_padded_indices,
                    torch.tensor([0] * (correlation + 1), dtype=torch.int32),
                )
            )

        path_end = path_start + path_num
        path_offsets[2 * curr_output + 0] = path_start
        path_offsets[2 * curr_output + 1] = path_end

    return path_padded_vals, path_padded_indices, path_offsets


def _register_path_tensor_buffer(
    symmetric_contraction_info,
    path_vals,
    path_indices,
    num_out_segments,
    correlation,
    math_dtype,
    suffix="",
):

    size_of_math_dtype = torch.tensor([], dtype=math_dtype).element_size()
    alignment = 16 // size_of_math_dtype

    if size_of_math_dtype == 1:
        int_type = torch.int8
    elif size_of_math_dtype == 2:
        int_type = torch.int16
    elif size_of_math_dtype == 4:
        int_type = torch.int32
    elif size_of_math_dtype == 8:
        int_type = torch.int64
    else:
        raise AssertionError("Non supported data size.")

    path_padded_vals, path_padded_indices, path_padded_offsets = _matricization(
        path_vals, path_indices, num_out_segments, correlation, alignment
    )

    path_vals_buffer = path_padded_vals.detach().to(math_dtype).contiguous()

    symmetric_contraction_info.register_buffer(
        "path_vals" + suffix, path_vals_buffer.view(int_type)
    )

    path_indices_buffer = (
        path_padded_indices.detach()
        .to(torch.int16)
        .contiguous()
        .view(dtype=torch.int32)
    )
    symmetric_contraction_info.register_buffer(
        "path_indices" + suffix, path_indices_buffer
    )

    path_offsets_buffer = (
        path_padded_offsets.detach().to(torch.int32).flatten().contiguous()
    )
    symmetric_contraction_info.register_buffer(
        "path_offsets" + suffix, path_offsets_buffer
    )


# index format [output_index, in1_index, in2_index, A_index,..., W_index]
def _diff_index_tuple_list_tensor_a(path_vals, path_indices, num_in_segments):

    new_path_vals, new_path_indices = [], []

    for path_val, path_index in zip(path_vals, path_indices):

        for i_segment in range(0, num_in_segments):

            tmp = path_index[1:-1]
            num = tmp.count(i_segment)

            if num == 0:
                continue

            tmp.pop(tmp.index(i_segment))
            new_path_index = [i_segment] + [path_index[0]] + tmp + [path_index[-1]]
            new_path_val = num * path_val

            new_path_vals.append(new_path_val)
            new_path_indices.append(new_path_index)

    return new_path_vals, new_path_indices


def _diff_diff_index_tuple_list_tensor_a(path_vals, path_indices, num_in_segments):

    d_path_vals, d_path_indices = _diff_index_tuple_list_tensor_a(
        path_vals, path_indices, num_in_segments
    )

    d_d_path_vals_a, d_d_path_indices_a = [], []
    d_d_path_indices_b, d_d_path_indices_w = [], []

    for path_val, path_index in zip(d_path_vals, d_path_indices):
        for i_segment in range(0, num_in_segments):
            tmp = path_index[2:-1]
            if len(tmp) == 0:
                continue
            num = tmp.count(i_segment)

            if num == 0:
                continue

            tmp.pop(tmp.index(i_segment))
            new_path_index = [i_segment] + path_index[0:2] + tmp + [path_index[-1]]
            new_path_val = num * path_val

            d_d_path_vals_a.append(new_path_val)
            d_d_path_indices_a.append(new_path_index)

    for path_index in d_path_indices:
        index = [path_index[1], path_index[0]] + path_index[2:]
        d_d_path_indices_b.append(index)

        index = [path_index[-1]] + path_index[1:-1] + [path_index[0]]
        d_d_path_indices_w.append(index)

    d_d_path_vals_b, d_d_path_vals_w = d_path_vals[:], d_path_vals[:]

    return (
        (d_d_path_vals_a, d_d_path_indices_a),
        (d_d_path_vals_b, d_d_path_indices_b),
        (d_d_path_vals_w, d_d_path_indices_w),
    )


def _diff_index_tuple_list_tensor_w(path_vals, path_indices):

    new_path_indices = []
    for path_index in path_indices:
        index = [path_index[-1]] + path_index[1:-1] + [path_index[0]]
        new_path_indices.append(index)

    return path_vals, new_path_indices


def _diff_diff_index_tuple_list_tensor_w(path_vals, path_indices, num_in_segments):

    d_path_vals, d_path_indices = _diff_index_tuple_list_tensor_w(
        path_vals, path_indices
    )

    d_path_vals_a, d_path_indices_a = _diff_index_tuple_list_tensor_a(
        d_path_vals, d_path_indices, num_in_segments
    )
    d_path_vals_b, d_path_indices_b = _diff_index_tuple_list_tensor_w(
        d_path_vals, d_path_indices
    )

    return (d_path_vals_a, d_path_indices_a), (d_path_vals_b, d_path_indices_b)


def make_clebsch_gordan_tensor(path_vals, path_indices, path_offsets, num_out_segments):
    math_dtype = path_vals.dtype
    op = get_operator_from_module(
        ops,
        "make_clebsch_gordan_tensor",
        (math_dtype,),
    )
    return op(
        path_vals, path_indices.view(dtype=torch.int16), path_offsets, num_out_segments
    )


class SymmetricContractionFwdInfo(nn.Module):
    def __init__(
        self, path_vals, path_indices, num_out_segments, correlation, math_dtype
    ):
        super().__init__()

        self.num_out_segments = num_out_segments
        self.math_dtype = math_dtype

        _register_path_tensor_buffer(
            self, path_vals, path_indices, num_out_segments, correlation, math_dtype
        )

    def forward(self):
        raise NotImplementedError(
            "SymmetricContractionFwdInfo module is not intended to be called."
        )


class SymmetricContractionBwdInfo(nn.Module):
    def __init__(
        self,
        path_vals,
        path_indices,
        num_in_segments,
        num_coupling_paths,
        correlation,
        math_dtype,
    ):
        super().__init__()

        self.num_in_segments = num_in_segments
        self.num_coupling_paths = num_coupling_paths
        self.math_dtype = math_dtype

        # for input tensor derivatives
        new_path_vals, new_path_indices = _diff_index_tuple_list_tensor_a(
            path_vals, path_indices, num_in_segments
        )
        _register_path_tensor_buffer(
            self,
            new_path_vals,
            new_path_indices,
            num_in_segments,
            correlation,
            math_dtype,
            "_da",
        )

        # for weight derivatives
        new_path_vals, new_path_indices = _diff_index_tuple_list_tensor_w(
            path_vals, path_indices
        )
        _register_path_tensor_buffer(
            self,
            new_path_vals,
            new_path_indices,
            num_coupling_paths,
            correlation,
            math_dtype,
            "_dw",
        )

    def forward(self):
        raise NotImplementedError(
            "SymmetricContractionBwdInfo module is not intended to be called."
        )


class SymmetricContractionBwdBwdInfo(nn.Module):
    def __init__(
        self,
        path_vals,
        path_indices,
        num_in_segments,
        num_coupling_paths,
        num_out_segments,
        correlation,
        math_dtype,
    ):
        super().__init__()

        self.num_in_segments = num_in_segments
        self.num_coupling_paths = num_coupling_paths
        self.num_out_segments = num_out_segments
        self.math_dtype = math_dtype

        # for second derivative with respect to input tensor
        (
            sparse_tensor_da_da,
            sparse_tensor_da_db,
            sparse_tensor_da_dw,
        ) = _diff_diff_index_tuple_list_tensor_a(
            path_vals, path_indices, num_in_segments
        )

        _register_path_tensor_buffer(
            self,
            sparse_tensor_da_da[0],
            sparse_tensor_da_da[1],
            num_in_segments,
            correlation,
            math_dtype,
            "_da_da",
        )
        _register_path_tensor_buffer(
            self,
            sparse_tensor_da_db[0],
            sparse_tensor_da_db[1],
            num_out_segments,
            correlation,
            math_dtype,
            "_da_db",
        )
        _register_path_tensor_buffer(
            self,
            sparse_tensor_da_dw[0],
            sparse_tensor_da_dw[1],
            num_coupling_paths,
            correlation,
            math_dtype,
            "_da_dw",
        )

        sparse_tensor_dw_da, sparse_tensor_dw_db = _diff_diff_index_tuple_list_tensor_w(
            path_vals, path_indices, num_in_segments
        )

        _register_path_tensor_buffer(
            self,
            sparse_tensor_dw_da[0],
            sparse_tensor_dw_da[1],
            num_in_segments,
            correlation,
            math_dtype,
            "_dw_da",
        )
        _register_path_tensor_buffer(
            self,
            sparse_tensor_dw_db[0],
            sparse_tensor_dw_db[1],
            num_out_segments,
            correlation,
            math_dtype,
            "_dw_db",
        )


@torch.library.custom_op(
    "cuequivariance_ops_torch::symmetric_tensor_contraction_bwd_primitive",
    mutates_args=(),
    device_types="cuda",
)
def _(
    grad_tensor_b: torch.Tensor,
    tensor_a: torch.Tensor,
    tensor_w: torch.Tensor,
    tensor_w_id: torch.Tensor,
    path_vals_da: torch.Tensor,
    path_indices_da: torch.Tensor,
    path_offsets_da: torch.Tensor,
    path_vals_dw: torch.Tensor,
    path_indices_dw: torch.Tensor,
    path_offsets_dw: torch.Tensor,
    path_vals_da_da: torch.Tensor,
    path_indices_da_da: torch.Tensor,
    path_offsets_da_da: torch.Tensor,
    path_vals_da_db: torch.Tensor,
    path_indices_da_db: torch.Tensor,
    path_offsets_da_db: torch.Tensor,
    path_vals_da_dw: torch.Tensor,
    path_indices_da_dw: torch.Tensor,
    path_offsets_da_dw: torch.Tensor,
    path_vals_dw_da: torch.Tensor,
    path_indices_dw_da: torch.Tensor,
    path_offsets_dw_da: torch.Tensor,
    path_vals_dw_db: torch.Tensor,
    path_indices_dw_db: torch.Tensor,
    path_offsets_dw_db: torch.Tensor,
    num_in_segments: int,
    num_out_segments: int,
    num_coupling_paths: int,
    correlation: int,
) -> List[torch.Tensor]:
    math_dtype = torch.float64 if path_vals_da.dtype == torch.int64 else torch.float32

    bwd_fun = get_operator_from_module(
        ops,
        "symmetric_tensor_contraction_bwd",
        (
            grad_tensor_b.dtype,
            tensor_a.dtype,
            tensor_w.dtype,
            math_dtype,
        ),
    )

    stream = torch.cuda.current_stream().cuda_stream

    grad_tensor_a = torch.empty_like(
        tensor_a, dtype=tensor_a.dtype, device=tensor_a.device
    )

    grad_tensor_w = torch.empty(
        tensor_w.shape, dtype=math_dtype, device=tensor_w.device
    )

    cg_da = make_clebsch_gordan_tensor(
        path_vals_da.view(math_dtype),
        path_indices_da,
        path_offsets_da,
        num_in_segments,
    )

    cg_dw = make_clebsch_gordan_tensor(
        path_vals_dw.view(math_dtype),
        path_indices_dw,
        path_offsets_dw,
        num_coupling_paths,
    )

    bwd_fun(
        grad_tensor_a,
        grad_tensor_w,
        maybe_detach(grad_tensor_b),
        maybe_detach(tensor_a),
        maybe_detach(tensor_w),
        maybe_detach(tensor_w_id),
        cg_da,
        cg_dw,
        correlation,
        stream,
    )

    if grad_tensor_w.dtype != tensor_w.dtype:
        grad_tensor_w = grad_tensor_w.to(tensor_w.dtype)

    ret = [grad_tensor_a, grad_tensor_w]
    return ret


@torch.library.register_fake(
    "cuequivariance_ops_torch::symmetric_tensor_contraction_bwd_primitive"
)
def _(
    grad_tensor_b: torch.Tensor,
    tensor_a: torch.Tensor,
    tensor_w: torch.Tensor,
    tensor_w_id: torch.Tensor,
    path_vals_da: torch.Tensor,
    path_indices_da: torch.Tensor,
    path_offsets_da: torch.Tensor,
    path_vals_dw: torch.Tensor,
    path_indices_dw: torch.Tensor,
    path_offsets_dw: torch.Tensor,
    path_vals_da_da: torch.Tensor,
    path_indices_da_da: torch.Tensor,
    path_offsets_da_da: torch.Tensor,
    path_vals_da_db: torch.Tensor,
    path_indices_da_db: torch.Tensor,
    path_offsets_da_db: torch.Tensor,
    path_vals_da_dw: torch.Tensor,
    path_indices_da_dw: torch.Tensor,
    path_offsets_da_dw: torch.Tensor,
    path_vals_dw_da: torch.Tensor,
    path_indices_dw_da: torch.Tensor,
    path_offsets_dw_da: torch.Tensor,
    path_vals_dw_db: torch.Tensor,
    path_indices_dw_db: torch.Tensor,
    path_offsets_dw_db: torch.Tensor,
    num_in_segments: int,
    num_out_segments: int,
    num_coupling_paths: int,
    correlation: int,
) -> List[torch.Tensor]:  # (torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor):
    grad_tensor_a = torch.empty_like(
        tensor_a, dtype=tensor_a.dtype, device=tensor_a.device
    )

    accum_type = torch.float32 if tensor_a.element_size() <= 4 else torch.float64

    grad_tensor_w = torch.empty_like(tensor_w, dtype=accum_type, device=tensor_w.device)
    return [grad_tensor_a, grad_tensor_w]


@torch.library.custom_op(
    "cuequivariance_ops_torch::symmetric_tensor_contraction_bwd_bwd_primitive",
    mutates_args=(),
    device_types="cuda",
)
def _(
    grad_grad_tensor_a: torch.Tensor,
    grad_grad_tensor_w: torch.Tensor,
    grad_tensor_b: torch.Tensor,
    tensor_a: torch.Tensor,
    tensor_w: torch.Tensor,
    tensor_w_id: torch.Tensor,
    path_vals_da_da: torch.Tensor,
    path_indices_da_da: torch.Tensor,
    path_offsets_da_da: torch.Tensor,
    path_vals_da_db: torch.Tensor,
    path_indices_da_db: torch.Tensor,
    path_offsets_da_db: torch.Tensor,
    path_vals_da_dw: torch.Tensor,
    path_indices_da_dw: torch.Tensor,
    path_offsets_da_dw: torch.Tensor,
    path_vals_dw_da: torch.Tensor,
    path_indices_dw_da: torch.Tensor,
    path_offsets_dw_da: torch.Tensor,
    path_vals_dw_db: torch.Tensor,
    path_indices_dw_db: torch.Tensor,
    path_offsets_dw_db: torch.Tensor,
    num_in_segments: int,
    num_out_segments: int,
    num_coupling_paths: int,
    correlation: int,
) -> List[
    torch.Tensor
]:  # (torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor): # List[torch.Tensor]:
    math_dtype = (
        torch.float64 if path_vals_da_da.dtype == torch.int64 else torch.float32
    )

    bwd_bwd_fun = get_operator_from_module(
        ops,
        "symmetric_tensor_contraction_bwd_bwd",
        (
            grad_tensor_b.dtype,
            tensor_a.dtype,
            tensor_w.dtype,
            math_dtype,
        ),
    )

    stream = torch.cuda.current_stream().cuda_stream

    grad_grad_tensor_b = torch.empty_like(
        grad_tensor_b,
        dtype=grad_tensor_b.dtype,
        device=grad_tensor_b.device,
    )

    grad_tensor_a = torch.empty_like(
        tensor_a, dtype=tensor_a.dtype, device=tensor_a.device
    )

    grad_tensor_w = torch.empty(
        tensor_w.shape,
        dtype=math_dtype,
        device=tensor_w.device,
    )

    cg_da_da = make_clebsch_gordan_tensor(
        path_vals_da_da.view(math_dtype),
        path_indices_da_da,
        path_offsets_da_da,
        num_in_segments,
    )
    cg_da_db = make_clebsch_gordan_tensor(
        path_vals_da_db.view(math_dtype),
        path_indices_da_db,
        path_offsets_da_db,
        num_out_segments,
    )
    cg_da_dw = make_clebsch_gordan_tensor(
        path_vals_da_dw.view(math_dtype),
        path_indices_da_dw,
        path_offsets_da_dw,
        num_coupling_paths,
    )
    cg_dw_da = make_clebsch_gordan_tensor(
        path_vals_dw_da.view(math_dtype),
        path_indices_dw_da,
        path_offsets_dw_da,
        num_in_segments,
    )
    cg_dw_db = make_clebsch_gordan_tensor(
        path_vals_dw_db.view(math_dtype),
        path_indices_dw_db,
        path_offsets_dw_db,
        num_out_segments,
    )

    bwd_bwd_fun(
        grad_grad_tensor_b,
        grad_tensor_a,
        grad_tensor_w,
        maybe_detach(grad_grad_tensor_a),
        maybe_detach(grad_grad_tensor_w),
        maybe_detach(grad_tensor_b),
        maybe_detach(tensor_a),
        maybe_detach(tensor_w),
        maybe_detach(tensor_w_id),
        cg_da_da,
        cg_da_db,
        cg_da_dw,
        cg_dw_da,
        cg_dw_db,
        correlation,
        stream,
    )

    if grad_tensor_w.dtype != tensor_w.dtype:
        grad_tensor_w = grad_tensor_w.to(tensor_w.dtype)

    return [grad_grad_tensor_b, grad_tensor_a, grad_tensor_w]


@torch.library.register_fake(
    "cuequivariance_ops_torch::symmetric_tensor_contraction_bwd_bwd_primitive"
)
def _(
    grad_grad_tensor_a: torch.Tensor,
    grad_grad_tensor_w: torch.Tensor,
    grad_tensor_b: torch.Tensor,
    tensor_a: torch.Tensor,
    tensor_w: torch.Tensor,
    tensor_w_id: torch.Tensor,
    path_vals_da_da: torch.Tensor,
    path_indices_da_da: torch.Tensor,
    path_offsets_da_da: torch.Tensor,
    path_vals_da_db: torch.Tensor,
    path_indices_da_db: torch.Tensor,
    path_offsets_da_db: torch.Tensor,
    path_vals_da_dw: torch.Tensor,
    path_indices_da_dw: torch.Tensor,
    path_offsets_da_dw: torch.Tensor,
    path_vals_dw_da: torch.Tensor,
    path_indices_dw_da: torch.Tensor,
    path_offsets_dw_da: torch.Tensor,
    path_vals_dw_db: torch.Tensor,
    path_indices_dw_db: torch.Tensor,
    path_offsets_dw_db: torch.Tensor,
    num_in_segments: int,
    num_out_segments: int,
    num_coupling_paths: int,
    correlation: int,
) -> List[torch.Tensor]:

    grad_grad_tensor_b = torch.empty_like(
        grad_tensor_b,
        dtype=grad_tensor_b.dtype,
        device=grad_tensor_b.device,
    )

    grad_tensor_a = torch.empty_like(
        tensor_a, dtype=tensor_a.dtype, device=tensor_a.device
    )

    accum_type = torch.float32 if tensor_a.element_size() <= 4 else torch.float64

    grad_tensor_w = torch.empty_like(tensor_w, dtype=accum_type, device=tensor_w.device)

    return [grad_grad_tensor_b, grad_tensor_a, grad_tensor_w]


def _symmetric_tensor_contraction_fwd(
    ret: torch.Tensor,
    tensor_a: torch.Tensor,
    tensor_w: torch.Tensor,
    tensor_w_id: torch.Tensor,
    path_vals: torch.Tensor,
    path_indices: torch.Tensor,
    path_offsets: torch.Tensor,
    num_out_segments: int,
    correlation: int,
    stream: int = -1,
) -> torch.Tensor:
    math_dtype = torch.float64 if path_vals.dtype == torch.int64 else torch.float32

    if ret is None:
        ret = torch.empty(
            [tensor_a.shape[0], num_out_segments, tensor_a.shape[-1]],
            dtype=tensor_a.dtype,
            device=tensor_a.device,
        )

    fwd_fun = get_operator_from_module(
        ops,
        "symmetric_tensor_contraction_fwd",
        (tensor_a.dtype, tensor_a.dtype, tensor_w.dtype, math_dtype),
    )

    cg = make_clebsch_gordan_tensor(
        path_vals.view(math_dtype), path_indices, path_offsets, num_out_segments
    )

    if stream == -1:
        stream = torch.cuda.current_stream().cuda_stream

    fwd_fun(
        ret,
        maybe_detach(tensor_a),
        maybe_detach(tensor_w),
        maybe_detach(tensor_w_id),
        cg,
        correlation,
        stream_id=stream,
    )
    return ret


@torch.library.custom_op(
    "cuequivariance_ops_torch::symmetric_tensor_contraction_fwd_primitive",
    mutates_args=(),
    device_types="cuda",
)
def _(
    tensor_a: torch.Tensor,
    tensor_w: torch.Tensor,
    tensor_w_id: torch.Tensor,
    path_vals: torch.Tensor,
    path_indices: torch.Tensor,
    path_offsets: torch.Tensor,
    path_vals_da: torch.Tensor,
    path_indices_da: torch.Tensor,
    path_offsets_da: torch.Tensor,
    path_vals_dw: torch.Tensor,
    path_indices_dw: torch.Tensor,
    path_offsets_dw: torch.Tensor,
    path_vals_da_da: torch.Tensor,
    path_indices_da_da: torch.Tensor,
    path_offsets_da_da: torch.Tensor,
    path_vals_da_db: torch.Tensor,
    path_indices_da_db: torch.Tensor,
    path_offsets_da_db: torch.Tensor,
    path_vals_da_dw: torch.Tensor,
    path_indices_da_dw: torch.Tensor,
    path_offsets_da_dw: torch.Tensor,
    path_vals_dw_da: torch.Tensor,
    path_indices_dw_da: torch.Tensor,
    path_offsets_dw_da: torch.Tensor,
    path_vals_dw_db: torch.Tensor,
    path_indices_dw_db: torch.Tensor,
    path_offsets_dw_db: torch.Tensor,
    num_in_segments: int,
    num_out_segments: int,
    num_coupling_paths: int,
    correlation: int,
) -> torch.Tensor:

    return _symmetric_tensor_contraction_fwd(
        None,
        tensor_a,
        tensor_w,
        tensor_w_id,
        path_vals,
        path_indices,
        path_offsets,
        num_out_segments,
        correlation,
    )


@torch.library.register_fake(
    "cuequivariance_ops_torch::symmetric_tensor_contraction_fwd_primitive"
)
def _(
    tensor_a: torch.Tensor,
    tensor_w: torch.Tensor,
    tensor_w_id: torch.Tensor,
    path_vals: torch.Tensor,
    path_indices: torch.Tensor,
    path_offsets: torch.Tensor,
    path_vals_da: torch.Tensor,
    path_indices_da: torch.Tensor,
    path_offsets_da: torch.Tensor,
    path_vals_dw: torch.Tensor,
    path_indices_dw: torch.Tensor,
    path_offsets_dw: torch.Tensor,
    path_vals_da_da: torch.Tensor,
    path_indices_da_da: torch.Tensor,
    path_offsets_da_da: torch.Tensor,
    path_vals_da_db: torch.Tensor,
    path_indices_da_db: torch.Tensor,
    path_offsets_da_db: torch.Tensor,
    path_vals_da_dw: torch.Tensor,
    path_indices_da_dw: torch.Tensor,
    path_offsets_da_dw: torch.Tensor,
    path_vals_dw_da: torch.Tensor,
    path_indices_dw_da: torch.Tensor,
    path_offsets_dw_da: torch.Tensor,
    path_vals_dw_db: torch.Tensor,
    path_indices_dw_db: torch.Tensor,
    path_offsets_dw_db: torch.Tensor,
    num_in_segments: int,
    num_out_segments: int,
    num_coupling_paths: int,
    correlation: int,
) -> torch.Tensor:
    tensor_b = torch.empty(
        [tensor_a.shape[0], num_out_segments, tensor_a.shape[-1]],
        dtype=tensor_a.dtype,
        device=tensor_a.device,
    )
    return tensor_b


def symmetric_tensor_contraction_fwd(
    tensor_a,
    tensor_w,
    tensor_w_id,
    correlation: int,
    fwd_info: SymmetricContractionFwdInfo,
    bwd_info: SymmetricContractionBwdInfo,
    bwd_bwd_info: SymmetricContractionBwdBwdInfo,
):
    return (
        torch.ops.cuequivariance_ops_torch.symmetric_tensor_contraction_fwd_primitive(
            tensor_a,
            tensor_w,
            tensor_w_id,
            fwd_info.path_vals,
            fwd_info.path_indices,
            fwd_info.path_offsets,
            bwd_info.path_vals_da,
            bwd_info.path_indices_da,
            bwd_info.path_offsets_da,
            bwd_info.path_vals_dw,
            bwd_info.path_indices_dw,
            bwd_info.path_offsets_dw,
            bwd_bwd_info.path_vals_da_da,
            bwd_bwd_info.path_indices_da_da,
            bwd_bwd_info.path_offsets_da_da,
            bwd_bwd_info.path_vals_da_db,
            bwd_bwd_info.path_indices_da_db,
            bwd_bwd_info.path_offsets_da_db,
            bwd_bwd_info.path_vals_da_dw,
            bwd_bwd_info.path_indices_da_dw,
            bwd_bwd_info.path_offsets_da_dw,
            bwd_bwd_info.path_vals_dw_da,
            bwd_bwd_info.path_indices_dw_da,
            bwd_bwd_info.path_offsets_dw_da,
            bwd_bwd_info.path_vals_dw_db,
            bwd_bwd_info.path_indices_dw_db,
            bwd_bwd_info.path_offsets_dw_db,
            bwd_info.num_in_segments,
            fwd_info.num_out_segments,
            bwd_info.num_coupling_paths,
            correlation,
        )
    )


def symmetric_tensor_contraction_setup_fwd_context(ctx, inputs, output):
    ctx.save_for_backward(*inputs[:3])
    ctx.saved_constants = inputs[6:]


def symmetric_tensor_contraction_setup_bwd_context(ctx, inputs, output):
    ctx.save_for_backward(*inputs[:4])
    ctx.saved_constants = inputs[10:]


def symmetric_tensor_contraction_primitive_backward(ctx, grad_output):
    ret = torch.ops.cuequivariance_ops_torch.symmetric_tensor_contraction_bwd_primitive(
        grad_output,
        *ctx.saved_tensors,
        *ctx.saved_constants,
    )
    return (
        *ret,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    )


def symmetric_tensor_contraction_primitive_backward_backward(ctx, grad_output):
    ret = torch.ops.cuequivariance_ops_torch.symmetric_tensor_contraction_bwd_bwd_primitive(
        *grad_output,
        *ctx.saved_tensors,
        *ctx.saved_constants,
    )
    return (
        *ret,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    )


torch.library.register_autograd(
    "cuequivariance_ops_torch::symmetric_tensor_contraction_fwd_primitive",
    symmetric_tensor_contraction_primitive_backward,
    setup_context=symmetric_tensor_contraction_setup_fwd_context,
)

torch.library.register_autograd(
    "cuequivariance_ops_torch::symmetric_tensor_contraction_bwd_primitive",
    symmetric_tensor_contraction_primitive_backward_backward,
    setup_context=symmetric_tensor_contraction_setup_bwd_context,
)


def _map_to_path_indices(path_segment_indices):
    path_indices = [[index[-1]] + index[0:-1] for index in path_segment_indices]
    return path_indices


class SymmetricTensorContraction(nn.Module):
    """
    A class to perform the symmetric tensor contraction in the Mace model.
    For more detail, see Eq(10) and Eq(11) in https://arxiv.org/pdf/2206.07697.

    Attributes
    ---------------------------
    num_in_segments : int
        number of segments in the fist input tensor
    num_couplings : int
        number of segments in the second input tensor
    num_out_segments : int
        number of segments in the output tensor
    correlation: int
        correlation length
    fwd_info: SymmetricContractionFwdInfo
        object to store precomputed data for the forward
    bwd_info: SymmetricContractionBwdInfo
        object to store precompute data for the backward
    bwd_bwd_info: SymmetricContractionBwdBwdInfo
        object to store precompute data for the double-backward

    Methods
    ---------------------------
    forward(tensor_a, tensor_w, tensor_w_id):
        forward function for the symmetric tensor contraction in the Mace model
    get_segments_dims():
        get the numbers of the segments for the input, the weight and the output tensors
    """

    def __init__(
        self,
        path_segment_indices: list[list[int]],
        path_coefficients: list[float],
        num_in_segments: int,
        num_couplings: int,
        num_out_segments: int,
        correlation: int,
        math_dtype: torch.dtype,
    ):
        """
        Construct all the necessary attributes

        Parameters
        ---------------------------
        path_segment_indices: list[list[int]]
            list of integer lists to represent each path
        path_coefficients: list[float]
            list of scaling factors for each path
        num_in_segments: int
            number of segments in the first input tensor,
            the repeated operand with the maximum repetition, correlation
        num_couplings: int
            number of segments in the second input tensor,
            the weight tensor
        num_out_segments: int
            number of segments in the output tensor
        correlation: int
            correlation length for the symmetric tensor contraction
        math_dtype: torch.dtype
            data type for computation

        Example
        ---------------------------
        # path_segment_indices[i][-1] < num_out_segments
        # path_segment_indices[i][-2] < num_couplings
        # path_segment_indices[i][0:-2] < num_in_segments
        path_segment_indices = [[0, 1, 1], [0, 1, 1, 2], [1, 1, 16, 8]]
        path_coefficients = [0.1, 0.2, -0.1]
        batch_size = 100
        num_in_segments = 9
        num_couplings = 17
        num_out_segments = 9
        num_embeddings = 3
        correlation = 2
        math_dtype = torch.float32
        sym_tc = SymmetricTensorContraction(path_segment_indices, path_coefficients, \
        num_in_segments, num_couplings, num_out_segments, correlation, math_dtype)

        sym_tc.to('cuda')

        # Number of repetition for segments of tensors.
        # tensor_a, tensor_w and tensor_out must have the same num_features.
        num_features = 128

        dtype = torch.float32

        tensor_a = torch.randn(
        (batch_size, num_in_segments, num_features),
        dtype=dtype,
        requires_grad=True,
        device='cuda',
        )
        tensor_w = torch.randn(
        (num_embeddings, num_couplings, num_features),
        dtype=dtype,
        requires_grad=True,
        device='cuda',
        )
        y = (
        torch.nn.functional.one_hot(
            torch.arange(0, batch_size) % num_embeddings, num_classes=num_embeddings
        )
        )
        tensor_w_id = (
        torch.nonzero(y)[:, 1]
        .contiguous()
        .to(dtype=torch.int32, device='cuda')
        .requires_grad_(False)
        )

        tensor_out = sym_tc.forward(tensor_a, tensor_w, tensor_w_id)
        """
        super().__init__()

        if not torch.cuda.is_available():
            raise AssertionError("No Nvidia GPU is detected")

        if len(path_segment_indices) != len(path_coefficients):
            raise AssertionError(
                "Number of the path coefficients and of the path segment indices \
                 are different."
            )

        self.num_in_segments = num_in_segments
        self.num_couplings = num_couplings
        self.num_out_segments = num_out_segments

        self.correlation = correlation

        path_indices = _map_to_path_indices(path_segment_indices)

        self.fwd_info = SymmetricContractionFwdInfo(
            path_coefficients,
            path_indices,
            self.num_out_segments,
            correlation,
            math_dtype,
        )
        self.bwd_info = SymmetricContractionBwdInfo(
            path_coefficients,
            path_indices,
            self.num_in_segments,
            self.num_couplings,
            correlation,
            math_dtype,
        )
        self.bwd_bwd_info = SymmetricContractionBwdBwdInfo(
            path_coefficients,
            path_indices,
            self.num_in_segments,
            self.num_couplings,
            self.num_out_segments,
            correlation,
            math_dtype,
        )

    def forward(self, tensor_a, tensor_w, tensor_w_id):
        """
        Forward funciton call

        Parameters
        ---------------------------
        tensor_a: torch.Tensor
            The input tensor with shape [num_batches, num_in_segments, num_features]
        tensor_w: torch.Tensor
            The input tensor with shape [num_embeddings, num_couplings, num_features]
        tensor_w_id:
            The weight ID with shape [num_batches] with 0-base, i.e. each element has the
            value smaller than num_embeddings

        Return
        ---------------------------
        Torch.tensor with shape [num_batches, num_out_segments, num_features]
        """

        return symmetric_tensor_contraction_fwd(
            tensor_a,
            tensor_w,
            tensor_w_id,
            self.correlation,
            self.fwd_info,
            self.bwd_info,
            self.bwd_bwd_info,
        )

    def get_segments_dims(self):
        """
        Get the numbers of the segments for the input, the weight and the output tensors
        """
        return (
            self.num_in_segments,
            self.num_coupling_paths,
            self.num_out_segments,
        )


__all__ = ["SymmetricTensorContraction"]
