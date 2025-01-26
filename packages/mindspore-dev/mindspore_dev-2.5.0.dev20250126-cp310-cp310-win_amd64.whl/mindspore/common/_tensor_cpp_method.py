# Copyright 2024 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""Add tensor cpp methods for stub tensor"""

tensor_cpp_methods = ['_to', 'abs', '__abs__', 'absolute', 'acos', 'arccos', 'acosh', 'arccosh', 'add', '__add__', 'add_', '__iadd__', 'addbmm', 'addmm', 'addmv', 'all', 'allclose', 'any', 'argmax', 'argmin', 'argsort', 'asin', 'arcsin', 'asinh', 'arcsinh', 'atan', 'arctan', 'atan2', 'arctan2', 'atanh', 'arctanh', 'bincount', 'bitwise_not', 'ceil', 'chunk', 'clamp', 'clip', 'clone', 'cos', 'cosh', 'cumsum', 'div', 'divide', 'div_', '__itruediv__', 'dot', 'eq', 'erf', 'erfc', 'exp', 'exp_', 'expand_as', 'expm1', 'fill_', 'flatten', 'floor', 'fmod', 'frac', 'gather', 'gcd', 'greater', 'gt', 'greater_equal', 'hardshrink', 'histc', 'index_select', 'inverse', 'isclose', 'isfinite', 'isinf', 'isneginf', 'lerp', 'less', 'lt', 'less_equal', 'le', 'log', 'log10', 'log1p', 'log2', 'logical_and', 'logical_not', 'logical_or', 'masked_fill', 'masked_fill_', 'masked_select', 'matmul', 'max', 'maximum', 'mean', 'median', 'min', 'minimum', 'mm', 'mul', 'mul_', '__imul__', 'nan_to_num', 'nansum', 'narrow', 'neg', 'negative', 'new_ones', 'new_zeros', 'not_equal', 'ne', 'outer', 'pow', '__pow__', 'prod', 'reciprocal', 'remainder', 'repeat_interleave', 'reshape', 'round', 'rsqrt', 'scatter', 'scatter_', 'scatter_add', 'select', 'sigmoid', 'sin', 'sinc', 'sinh', 'sort', 'split', 'sqrt', 'square', 'std', 'sub', '__sub__', 'sub_', '__isub__', 'subtract', 'sum', 't', 'tan', 'tanh', 'tile', 'topk', 'transpose', 'tril', 'triu', 'true_divide', 'trunc', 'type_as', 'unbind', 'unique', 'unsqueeze', 'var', 'view_as', 'where']
