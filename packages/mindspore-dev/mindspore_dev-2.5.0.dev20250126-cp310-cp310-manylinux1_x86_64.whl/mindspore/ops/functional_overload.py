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
"""Holding mint APIs"""
from mindspore._c_expression import _all_gather_matmul_instance
from mindspore._c_expression import _bitwise_not_instance
from mindspore._c_expression import _clamp_instance
from mindspore._c_expression import _div_instance
from mindspore._c_expression import _empty_instance
from mindspore._c_expression import _fmod_instance
from mindspore._c_expression import _lerp_instance
from mindspore._c_expression import _matmul_reduce_scatter_instance
from mindspore._c_expression import _max_instance
from mindspore._c_expression import _min_instance
from mindspore._c_expression import _nansum_instance
from mindspore._c_expression import _remainder_instance
from mindspore._c_expression import _repeat_interleave_instance
from mindspore._c_expression import _where_instance

def all_gather_matmul(*args, **kwargs):
    r"""
    all_gather_matmul(input, x2, group, world_size, *, bias=None, gather_index=0, gather_output=True, comm_turn=0, trans_input=False, trans_x2=False) -> Tensor

    In the TP segmentation scenario, allgather and matmul are fused, and communication and computational pipelines
    are parallelized within the fusion operator.

    .. math::
        output = allgather(input)@x2

        gather\_out = allgather(input)

    .. warning::
        This is an experimental API that is subject to change or deletion.

    Args:
        input (Tensor): The left matrix of matmul, the dtype supports float16 and bfloat16, the shape supports 2
            dimensions, and the data format supports ND.
        x2 (Tensor): The right matrix of matmul, the dtype needs to be consistent with ``input`` , the shape
            supports 2 dimensions, and the data format supports ND.
        group (str): Communication group name, can be created by ``create_group`` method, or use the default group
            ``mindspore.communication.GlobalComm.WORLD_COMM_GROUP``.
        world_size (int): The total number of ranks in the communication group, should be consistent with the number
            of devices actually running, supporting ``2`` , ``4`` , and ``8`` .

    Keyword Args:
        bias (Tensor, optional): Currently only ``None`` is supported. Default: ``None`` .
        gather_index (int, optional): Indicates the allgather operation object, ``0`` means gather ``input`` ,
            ``1`` means gather ``x2`` . Currently only ``0`` is supported. Default: ``0`` .
        gather_output (bool, optional): Indicates whether gather output is required. Default: ``True`` .
        comm_turn (int, optional): Indicates the granularity of communication between ranks. Currently only ``0``
            is supported. Default: ``0`` .
        trans_input (bool, optional): Indicates whether ``input`` is transposed. Currently only ``False`` is
            supported. Default: ``False`` .
        trans_x2 (bool, optional): Indicates whether ``x2`` is transposed. Default: ``False`` .

    Returns:
        - output (Tensor) - The result of allgather and matmul fusion calculations.
        - gather_out (Tensor) - The result of allgather. If gather_output is ``False`` , ``gather_out`` returns a
          tensor with shape 0.

    Note:
        - When using this interface, please ensure that the driver firmware package and CANN package are both the
          matching 8.0.RC2 version or a higher version, otherwise an error will be reported, such as BUS ERROR.
        - The shape of ``input`` is (m, k), the shape of ``x2`` is (k, n), k is required to be equal, and the value
          range of k is [256, 65535). The shape of ``output`` is (m * world_size, n), and the shape of
          ``gather_out`` is (m * world_size, k).
        - The common fusion operators in a model only support the same communication group.

    Raises:
        TypeError: Any arg is of wrong type.
        RuntimeError: The dtype of ``input`` or ``x2`` is neither float16 nor bfloat16.
        RuntimeError: The dtypes of ``input`` and ``x2`` are different.
        RuntimeError: The shape of ``input`` or ``x2`` is not two-dimensional.
        RuntimeError: The k axis of ``input`` shape and ``x2`` shape are not equal.
        RuntimeError: k is less than ``256`` or greater than or equal to ``65535`` .
        RuntimeError: ``bias`` is not None.
        RuntimeError: ``group`` does not exist.
        RuntimeError: ``world_size`` is inconsistent with the actual number of running cards.
        RuntimeError: ``world_size`` is not equal to ``2`` , ``4`` , or ``8`` .
        RuntimeError: ``gather_index`` is not ``0`` .
        RuntimeError: ``trans_input`` is ``True`` .

    Supported Platforms:
        ``Ascend``

    Examples:
        .. note::
            Before running the following examples, you need to configure the communication environment variables.

            For Ascend/GPU/CPU devices, it is recommended to use the msrun startup method without any third-party or
            configuration file dependencies. Please see the `msrun start up <https://www.mindspore.cn/docs/en/master/model_train/parallel/msrun_launcher.html>`_
            for more details.

            This example should be run with 2 devices.

        >>> import mindspore as ms
        >>> import numpy as np
        >>> from mindspore import ops
        >>> ms.communication.init()
        >>> rank = ms.communication.get_rank()
        >>> np.random.seed(rank)
        >>> input = ms.Tensor(np.random.randn(128, 256).astype(np.float32), dtype=ms.float16)
        >>> x2 = ms.Tensor(np.random.randn(256, 512).astype(np.float32), dtype=ms.float16)
        >>> group = ms.communication.GlobalComm.WORLD_COMM_GROUP
        >>> world_size = ms.communication.get_group_size()
        >>> output, gather_out = ops.all_gather_matmul(
        ...    input,
        ...    x2,
        ...    group,
        ...    world_size,
        ...    bias=None,
        ...    gather_index=0,
        ...    gather_output=True,
        ...    comm_turn=0,
        ...    trans_input=False,
        ...    trans_x2=False,
        ... )
        >>> print(output.shape)
        (256, 512)
        >>> print(gather_out.shape)
        (256, 256)
    """
    return _all_gather_matmul_instance(*args, **kwargs)


def bitwise_not(*args, **kwargs):
    r"""
    bitwise_not(input) -> Tensor

    Returns bitwise `not` of the input tensor.

    .. warning::
        This is an experimental API that is subject to change or deletion.

    Args:
        input (Tensor): The input tensor must be of integral or Boolean types.

    Returns:
        Tensor, has the same shape and type as `input`.

    Raises:
        TypeError: If `input` is not a Tensor.
        RuntimeError: If dtype of `input` is not int or bool.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, mint
        >>> x = Tensor(np.array([True, False, True, False]))
        >>> y = mint.bitwise_not(x)
        >>> print(y)
        [False True False True]
    """
    return _bitwise_not_instance(*args, **kwargs)


def clamp(*args, **kwargs):
    r"""
    clamp(input, min=None, max=None) -> Tensor

    Clamps tensor values between the specified minimum value and maximum value.

    Limits the value of :math:`input` to a range, whose lower limit is `min` and upper limit is `max` .

    .. math::

        out_i= \left\{
        \begin{array}{align}
            max & \text{ if } input_i\ge max \\
            input_i & \text{ if } min \lt input_i \lt max \\
            min & \text{ if } input_i \le min \\
        \end{array}\right.

    Note:
        - `min` and `max` cannot be None at the same time;
        - When `min` is None and `max` is not None, the elements in Tensor larger than `max` will become `max`;
        - When `min` is not None and `max` is None, the elements in Tensor smaller than `min` will become `min`;
        - If `min` is greater than `max`, the value of all elements in Tensor will be set to `max`;
        - The data type of `input`, `min` and `max` should support implicit type conversion and cannot be bool type.

    Args:
        input (Tensor): Input data, which type is Tensor. Tensors of arbitrary dimensions are supported.
        min (Union(Tensor, float, int), optional): The minimum value. Default: ``None`` .
        max (Union(Tensor, float, int), optional): The maximum value. Default: ``None`` .

    Returns:
        Tensor, a clipped Tensor.
        The data type and shape are the same as input.

    Raises:
        ValueError: If both `min` and `max` are None.
        TypeError: If the type of `input` is not Tensor.
        TypeError: If the type of `min` is not in None, Tensor, float or int.
        TypeError: If the type of `max` is not in None, Tensor, float or int.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> # case 1: the data type of input is Tensor
        >>> import mindspore
        >>> from mindspore import Tensor, mint
        >>> import numpy as np
        >>> min_value = Tensor(5, mindspore.float32)
        >>> max_value = Tensor(20, mindspore.float32)
        >>> input = Tensor(np.array([[1., 25., 5., 7.], [4., 11., 6., 21.]]), mindspore.float32)
        >>> output = mint.clamp(input, min_value, max_value)
        >>> print(output)
        [[ 5. 20.  5.  7.]
         [ 5. 11.  6. 20.]]
        >>> # case 2: the data type of input is number
        >>> import mindspore
        >>> from mindspore import Tensor, mint
        >>> import numpy as np
        >>> min_value = 5
        >>> max_value = 20
        >>> input = Tensor(np.array([[1., 25., 5., 7.], [4., 11., 6., 21.]]), mindspore.float32)
        >>> output = mint.clamp(input, min_value, max_value)
        >>> print(output)
        [[ 5. 20.  5.  7.]
         [ 5. 11.  6. 20.]]
    """
    return _clamp_instance(*args, **kwargs)


def clip(*args, **kwargs):
    r"""
    clip(input, min=None, max=None) -> Tensor

    Alias for :func:`mindspore.mint.clamp`.
    """
    return _clamp_instance(*args, **kwargs)


def div(*args, **kwargs):
    r"""
    div(input, other, *, rounding_mode=None) -> Tensor

    Divides each element of the `input` by the corresponding element of the `other` .

    .. math::

        out_{i} = input_{i} / other_{i}

    .. note::
        - When the two inputs have different shapes, they must be able to broadcast to a common shape.
        - The two inputs can not be bool type at the same time,
          [True, Tensor(True, bool\_), Tensor(np.array([True]), bool\_)] are all considered bool type.
        - The two inputs comply with the implicit type conversion rules to make the data types
          consistent.

    Args:
        input (Union[Tensor, Number, bool]): The dividend.
        other (Union[Tensor, Number, bool]): The divisor.

    Keyword Args:
        rounding_mode (str, optional): Type of rounding applied to the result. Default: ``None`` .
            Three types are defined as,

            - None: Default behavior, which is the same as true division in Python or `true_divide` in NumPy.

            - "floor": Rounds the division of the inputs down, which is the same as floor division in Python
              or `floor_divide` in NumPy.

            - "trunc": Rounds the division of the inputs towards zero, which is the same as C-style integer division.

    Returns:
        Tensor, the shape is the same as the one after broadcasting,
        and the data type is the one with higher precision or higher digits among the two inputs.

    Raises:
        TypeError: If `input` and `other` is not one of the following: Tensor, Number, bool.
        ValueError: If `rounding_mode` value is not None, "floor" or "trunc".

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, mint
        >>> x = Tensor(np.array([1.0, 2.0, 3.0]), mindspore.float32)
        >>> y = Tensor(np.array([4.0, 5.0, 6.0]), mindspore.float32)
        >>> output = mint.div(x, y)
        >>> print(output)
        [0.25 0.4 0.5]
    """
    return _div_instance(*args, **kwargs)


def divide(*args, **kwargs):
    r"""
    divide(input, other, *, rounding_mode=None) -> Tensor

    Alias for :func:`mindspore.mint.div`.
    """
    return _div_instance(*args, **kwargs)


def empty(*args, **kwargs):
    r"""
    empty(*size, dtype=None, device=None) -> Tensor

    Creates a tensor with uninitialized data, whose shape, dtype and device are described by the argument `size`,
    `dtype` and `device` respectively.

    .. warning::
        This is an experimental API that is subject to change or deletion.

    Args:
        size (Union[tuple[int], list[int], int]): The specified shape of output tensor. Can be variable numbers of
            positive integers or tupled or list containing positive integers.

    Keyword Args:
        dtype (:class:`mindspore.dtype`, optional): The specified type of output tensor. If `dtype` is ``None`` ,
            `mindspore.float32` will be used. Default: ``None`` .
        device (string, optional): The specified device of the output tensor. Support ``CPU`` and ``Ascend``. If
            `device = None`, `mindspore.context.device_target` will be used. Default ``None``.

    Returns:
        Tensor, whose dtype and size are defined by input.

    Raises:
        TypeError:  If `size` is neither an int nor a tuple or list of int.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore
        >>> from mindspore import ops
        >>> output = ops.empty((2, 3), dtype=mindspore.float32)
        >>> print(output)
        [[0. 0. 0.]
         [0. 0. 0.]]
    """
    return _empty_instance(*args, **kwargs)


def fmod(*args, **kwargs):
    r"""
    fmod(input, other) -> Tensor

    Computes the floating-point remainder of the division operation input/other.

    .. math::

        out = input - n * other

    Where :math:`n` is :math:`input/other` with its fractional part truncated.
    The returned value has the same sign as `input` and is less than `other` in magnitude.

    .. warning::
        This is an experimental API that is subject to change or deletion.

    Args:
        input (Tensor): the dividend.
        other (Union[Tensor, Number]): the divisor.

    Returns:
        Tensor, the shape is the same as the one after broadcasting,
        and the data type is the one with higher precision or higher digits among the two inputs.

    Raises:
        TypeError: If `input` is not a Tensor.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, mint
        >>> input = Tensor(np.array([-4., -3.5, 0, 3.5, 4]), mindspore.float32)
        >>> output = mint.fmod(input, 2.5)
        >>> print(output)
        [-1.5 -1.   0.   1.   1.5]
    """
    return _fmod_instance(*args, **kwargs)


def lerp(*args, **kwargs):
    r"""
    lerp(input, end, weight) -> Tensor

    Perform a linear interpolation of two tensors input and end based on a float or tensor weight.

    If `weight` is a tensor, the shapes of three inputs need to be broadcast;
    If `weight` is a float, the shapes of `input` and `end` need to be broadcast.
    If `weight` is a float and platform is Ascend, the types of `input` and `end` need to be float32.

    .. warning::
        This is an experimental API that is subject to change or deletion.

    .. math::
        output_{i} = input_{i} + weight_{i} * (end_{i} - input_{i})

    Args:
        input (Tensor): The tensor with the starting points. Data type must be float16 or float32.
        end (Tensor): The tensor with the ending points. Data type must be the same as `input`.
        weight (Union[float, Tensor]): The weight for the interpolation formula. Must be a float scalar
            or a tensor with float16 or float32 data type.

    Returns:
        Tensor, has the same type and shape as input `input`.

    Raises:
        TypeError: If `input` or `end` is not a tensor.
        TypeError: If `weight` is neither scalar(float) nor tensor.
        TypeError: If dtype of `input` or `end` is neither float16 nor float32.
        TypeError: If dtype of `weight` is neither float16 nor float32 when it is a tensor.
        TypeError: If `input` and `end` have different data types.
        TypeError: If `input`, `end` and `weight` have different data types when `weight` is a tensor.
        ValueError: If `end` could not be broadcast to a tensor with shape of `input`.
        ValueError: If `weight` could not be broadcast to tensors with shapes of `input` and `end` when it is a tensor.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, mint
        >>> start = Tensor(np.array([1., 2., 3., 4.]), mindspore.float32)
        >>> end = Tensor(np.array([10., 10., 10., 10.]), mindspore.float32)
        >>> output = mint.lerp(start, end, 0.5)
        >>> print(output)
        [5.5 6. 6.5 7. ]
    """
    return _lerp_instance(*args, **kwargs)


def matmul_reduce_scatter(*args, **kwargs):
    r"""
    matmul_reduce_scatter(input, x2, group, world_size, *, reduce_op='sum', bias=None, comm_turn=0, trans_input=False, trans_x2=False) -> Tensor

    In the TP segmentation scenario, matmul and reducescatter are fused, and communication and computational
    pipelines are parallelized within the fusion operator.

    .. math::
        output = reducescatter(input@x2)

    .. warning::
        This is an experimental API that is subject to change or deletion.

    Args:
        input (Tensor): The left matrix of matmul, the dtype supports float16 and bfloat16, the shape supports 2
            dimensions, and the data format supports ND.
        x2 (Tensor): The right matrix of matmul, the dtype needs to be consistent with ``input`` , the shape
            supports 2 dimensions, and the data format supports ND.
        group (str): Communication group name, can be created by ``create_group`` method, or use the default group
            ``mindspore.communication.GlobalComm.WORLD_COMM_GROUP``.
        world_size (int): The total number of ranks in the communication group, should be consistent with the number
            of devices actually running, supporting ``2`` , ``4`` , and ``8`` .

    Keyword Args:
        reduce_op (str, optional) The reduce operation type. Currently only ``'sum'`` is supported. Default:
            ``'sum'`` .
        bias (Tensor, optional): Currently only ``None`` is supported. Default: ``None`` .
        comm_turn (int, optional): Indicates the granularity of communication between ranks. Currently only ``0``
            is supported. Default: ``0`` .
        trans_input (bool, optional): Indicates whether ``input`` is transposed. Currently only ``False`` is
            supported. Default: ``False`` .
        trans_x2 (bool, optional): Indicates whether ``x2`` is transposed. Default: ``False`` .

    Returns:
        - output (Tensor) - The result of allgather and matmul fusion calculations.

    Note:
        - When using this interface, please ensure that the driver firmware package and CANN package are both the
          matching 8.0.RC2 version or a higher version, otherwise an error will be reported, such as BUS ERROR.
        - The shape of ``input`` is (m, k), the shape of ``x2`` is (k, n), k is required to be equal, and the value
          range of k is [256, 65535), and m is required to be an integer multiple of ``world_size`` . The shape of
          ``output`` is (m * world_size, n).
        - The common fusion operators in a model only support the same communication group.

    Raises:
        TypeError: Any arg is of wrong type.
        RuntimeError: The dtype of ``input`` or ``x2`` is neither float16 nor bfloat16.
        RuntimeError: The dtypes of ``input`` and ``x2`` are different.
        RuntimeError: The shape of ``input`` or ``x2`` is not two-dimensional.
        RuntimeError: The k axis of ``input`` shape and ``x2`` shape are not equal.
        RuntimeError: k is less than ``256`` or greater than or equal to ``65535`` .
        RuntimeError: ``bias`` is not None.
        RuntimeError: ``group`` does not exist.
        RuntimeError: ``world_size`` is inconsistent with the actual number of running cards.
        RuntimeError: ``world_size`` is not equal to ``2`` , ``4`` , or ``8`` .
        RuntimeError: ``reduce_op`` is not ``'sum'`` .
        RuntimeError: ``trans_input`` is ``True`` .

    Supported Platforms:
        ``Ascend``

    Examples:
        .. note::
            Before running the following examples, you need to configure the communication environment variables.

            For Ascend/GPU/CPU devices, it is recommended to use the msrun startup method without any third-party or
            configuration file dependencies. Please see the `msrun start up <https://www.mindspore.cn/docs/en/master/model_train/parallel/msrun_launcher.html>`_
            for more details.

            This example should be run with 2 devices.

        >>> import mindspore as ms
        >>> from mindspore import ops
        >>> import numpy as np
        >>> ms.communication.init()
        >>> rank = ms.communication.get_rank()
        >>> np.random.seed(rank)
        >>> input = ms.Tensor(np.random.randn(1024, 256).astype(np.float32), dtype=ms.float16)
        >>> x2 = ms.Tensor(np.random.randn(256, 512).astype(np.float32), dtype=ms.float16)
        >>> group = ms.communication.GlobalComm.WORLD_COMM_GROUP
        >>> world_size = ms.communication.get_group_size()
        >>> reduce_op = ops.ReduceOp.SUM
        >>> output = ops.matmul_reduce_scatter(
        ...    input,
        ...    x2,
        ...    group,
        ...    world_size,
        ...    reduce_op=reduce_op,
        ...    bias=None,
        ...    comm_turn=0,
        ...    trans_input=False,
        ...    trans_x2=False,
        ... )
        >>> print(output.shape)
        (512, 512)
    """
    return _matmul_reduce_scatter_instance(*args, **kwargs)


def max(*args, **kwargs):
    r"""
    max(input) -> Tensor

    Returns the maximum value of the input tensor.

    Args:
        input (Tensor): The input tensor.

    Returns:
        Scalar Tensor with the same dtype as `input`, the maximum value of the input.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, mint
        >>> x = Tensor(np.array([0.0, 0.4, 0.6, 0.7, 0.1]), mindspore.float32)
        >>> output = mint.max(x)
        >>> print(output)
        0.7

    .. function:: max(input, dim, keepdim=False) -> tuple(Tensor)
        :noindex:

    Calculates the maximum value along with the given dim for the input tensor, and returns the maximum values and
    indices.

    Args:
        input (Tensor): The input tensor, can be any dimension. Set the shape of input tensor as
            :math:`(input_1, input_2, ..., input_N)` , Complex tensor is not supported.
        dim (int): The dimension to reduce.
        keepdim (bool, optional): Whether to reduce dimension, if ``True`` the output will keep the same dimension as the
            `input` , the output will reduce dimension if ``false``. Default: ``False``.

    Returns:
        tuple (Tensor), tuple of 2 tensors, containing the maximum value of the self tensor along the given
        dimension `dim` and the corresponding index.

        - **values** (Tensor) - The maximum value of input tensor, with the same shape as `index`, and same dtype as `input`.
        - **index** (Tensor) - The index for the maximum value of the input tensor, with dtype int64. If `keepdim`
          is ``True`` , the shape of output tensors is :math:`(input_1, input_2, ..., input_{dim-1}, 1, input_{dim+1}, ..., input_N)`.
          Otherwise, the shape is :math:`(input_1, input_2, ..., input_{dim-1}, input_{dim+1}, ..., input_N)` .

    Raises:
        TypeError: If `input` is not Tensor.
        TypeError: If `keepdim` is not a bool.
        TypeError: If `dim` is not an int.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, mint
        >>> x = Tensor(np.array([0.0, 0.4, 0.6, 0.7, 0.1]), mindspore.float32)
        >>> output, index = mint.max(x, 0, keepdim=True)
        >>> print(output, index)
        [0.7] [3]

    .. function:: max(input, other) -> Tensor
        :noindex:

    For details, please refer to :func:`mindspore.mint.maximum`.
    """
    return _max_instance(*args, **kwargs)


def min(*args, **kwargs):
    r"""
    min(input) -> Tensor

    Returns the minimum value of the input tensor.

    Args:
        input (Tensor): The input tensor.

    Returns:
        Scalar Tensor with the same dtype as `input`, the minimum value of the input.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, mint
        >>> x = Tensor(np.array([0.0, 0.4, 0.6, 0.7, 0.1]), mindspore.float32)
        >>> output = mint.min(x)
        >>> print(output)
        0.0

    .. function:: min(input, dim, keepdim=False) -> Tensor
        :noindex:

    Calculates the minimum value along with the given dim for the input tensor, and returns the minimum values and
    indices.

    Args:
        input (Tensor) - The input tensor, can be any dimension. Set the shape of input tensor as
            :math:`(input_1, input_2, ..., input_N)` , Complex tensor is not supported.
        dim (int): The dimension to reduce.
        keepdim (bool, optional): Whether to reduce dimension, if ``True`` the output will keep the same dimension as the
            input, the output will reduce dimension if ``false``. Default: ``False``.

    Returns:
        tuple (Tensor), tuple of 2 tensors, containing the minimum value of the self tensor along the given
        dimension `dim` and the corresponding index.

        - **values** (Tensor) - The minimum value of input tensor, with the same shape as `index`, and same dtype as `input`.
        - **index** (Tensor) - The index for the minimum value of the input tensor, with dtype int64. If `keepdim`
          is ``True`` , the shape of output tensors is :math:`(input_1, input_2, ..., input_{dim-1}, 1, input_{dim+1}, ..., input_N)`.
          Otherwise, the shape is :math:`(input_1, input_2, ..., input_{dim-1}, input_{dim+1}, ..., input_N)` .

    Raises:
        TypeError: If `input` is not Tensor.
        TypeError: If `keepdim` is not a bool.
        TypeError: If `dim` is not an int.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, mint
        >>> x = Tensor(np.array([0.0, 0.4, 0.6, 0.7, 0.1]), mindspore.float32)
        >>> output, index = mint.min(x, 0, keepdim=True)
        >>> print(output, index)
        [0.0] [0]

    .. function:: min(input, other) -> Tensor
        :noindex:

    For details, please refer to :func:`mindspore.mint.minimum`.
    """
    return _min_instance(*args, **kwargs)


def nansum(*args, **kwargs):
    r"""
    nansum(input, dim=None, keepdim=False, *, dtype=None) -> Tensor

    Computes sum of `input` over a given dimension, treating NaNs as zero.

    .. warning::
        It is only supported on Atlas A2 Training Series Products.
        This is an experimental API that is subject to change or deletion.

    Args:
        input (Tensor): The input Tensor.
        dim (Union[int, tuple(int)], optional): The dimensions to sum.
            Dim must be in the range [-rank(input), rank(input)). Default: ``None``, which indicates the sum of all
            elements in a tensor.
        keepdim (bool, optional): Whether the output Tensor keeps dimensions or not. Default: ``False``, indicating that no dimension is kept.

    Keyword Args:
        dtype (:class:`mindspore.dtype`, optional): The dtype of output Tensor. Default: ``None``.

    Returns:
        Tensor, the sum of input `input` in the given dimension dim, treating NaNs as zero.

        - If dim is None, keepdim is False,
          the output is a 0-D Tensor representing the sum of all elements in the input Tensor.
        - If dim is int, set as 2, and keepdim is False,
          the shape of output is :math:`(input_1, input_3, ..., input_R)`.
        - If dim is tuple(int) or list(int), set as (2, 3), and keepdim is False,
          the shape of output is :math:`(input_1, input_4, ..., input_R)`.

    Raises:
        TypeError: If `input` is not Tensor.
        TypeError: If `keepdim` is not a bool.
        TypeError: If the dtype of `input` or `dtype` is complex type.
        ValueError: If `dim` is not in [-rank(input), rank(input)).

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, mint
        >>> x = Tensor(np.array([[float("nan"), 2, 3], [1, 2, float("nan")]]), mindspore.float32)
        >>> output1 = mint.nansum(x, dim=0, keepdim=False, dtype=mindspore.float32)
        >>> output2 = mint.nansum(x, dim=0, keepdim=True, dtype=mindspore.float32)
        >>> print(output1)
        [1. 4. 3.]
        >>> print(output2)
        [[1. 4. 3.]]
    """
    return _nansum_instance(*args, **kwargs)


def remainder(*args, **kwargs):
    r"""
    remainder(input, other) -> Tensor

    Computes the remainder of `input` divided by `other` element-wise. The result has the same sign as the divisor and
    its absolute value is less than that of `other`.

    Supports broadcasting to a common shape and implicit type promotion.

    .. code:: python

        remainder(input, other) == input - input.div(other, rounding_mode="floor") * other

    Note:
        Complex inputs are not supported. At least one input need to be tensor, but not both are bool tensors.

    Args:
        input (Union[Tensor, numbers.Number, bool]): The dividend is a numbers.Number or
            a bool or a tensor whose data type is
            `number <https://www.mindspore.cn/docs/en/master/api_python/mindspore/mindspore.dtype.html>`_ or
            `bool_ <https://www.mindspore.cn/docs/en/master/api_python/mindspore/mindspore.dtype.html>`_.
        other (Union[Tensor, numbers.Number, bool]): The divisor is a numbers.Number or
            a bool or a tensor whose data type is number or bool\_ when the dividend is a tensor.
            When the dividend is Scalar, the divisor must be a Tensor whose data type is number or bool\_.

    Returns:
        Tensor, with dtype promoted and shape broadcasted.

    Raises:
        TypeError: If `input` and `other` are not of types: (tensor, tensor), (tensor, number), (tensor, bool),
            (number, tensor) or (bool, tensor).
        ValueError: If `input` and `other` are not broadcastable.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import numpy as np
        >>> from mindspore import Tensor, mint
        >>> x = Tensor(np.array([-4.0, 5.0, 6.0]).astype(np.float32))
        >>> y = Tensor(np.array([3.0, 2.0, 3.0]).astype(np.float64))
        >>> output = mint.remainder(x, y)
        >>> print(output)
        [2.  1.  0.]
    """
    return _remainder_instance(*args, **kwargs)


def repeat_interleave(*args, **kwargs):
    r"""
    repeat_interleave(input, repeats, dim=None, *, output_size=None) -> Tensor

    Repeat elements of a tensor along an axis, like :func:`mindspore.numpy.repeat`.

    .. warning::
        Only support on Atlas A2 training series.

    Args:
        input (Tensor): The tensor to repeat values for. Must be of types: float16,
            float32, int8, uint8, int16, int32, or int64.
        repeats (Union[int, tuple, list, Tensor]): The number of times to repeat, must be positive.
        dim (int, optional): The dim along which to repeat, Default: ``None``. If dims is None,
            the input Tensor will be flattened and the output will alse be flattened.

    Keyword Args:
        output_size (int, optional): Total output size for the given axis (e.g. sum of repeats),
            Default: ``None``.

    Returns:
        One tensor with values repeated along the specified dim. If input has shape
        :math:`(s1, s2, ..., sn)` and dim is i, the output will have shape :math:`(s1, s2, ...,
        si * repeats, ..., sn)`. The output type will be the same as the type of `input`.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, mint
        >>> input = Tensor(np.array([[0, 1, 2], [3, 4, 5]]), mindspore.int32)
        >>> output = mint.repeat_interleave(input, repeats=2, dim=0)
        >>> print(output)
        [[0 1 2]
         [0 1 2]
         [3 4 5]
         [3 4 5]]
    """
    return _repeat_interleave_instance(*args, **kwargs)


def where(*args, **kwargs):
    r"""
    where(condition, input, other) -> Tensor

    Selects elements from `input` or `other` based on `condition` and returns a tensor.

    .. math::
        output_i = \begin{cases} input_i,\quad &if\ condition_i \\ other_i,\quad &otherwise \end{cases}

    Args:
        condition (Tensor[bool]): If true, yield `input`, otherwise yield `other`.
        input (Union[Tensor, Scalar]): When `condition` is true, values to select from.
        other (Union[Tensor, Scalar]): When `condition` is false, values to select from.

    Returns:
        Tensor, elements are selected from `input` and `other`.

    Raises:
        TypeError: If `condition` is not a tensor.
        TypeError: If both `input` and `other` are scalars.
        ValueError: If `condition`, `input` and `other` can not broadcast to each other.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import numpy as np
        >>> from mindspore import tensor, ops
        >>> from mindspore import dtype as mstype
        >>> a = tensor(np.arange(4).reshape((2, 2)), mstype.float32)
        >>> b = tensor(np.ones((2, 2)), mstype.float32)
        >>> condition = a < 3
        >>> output = ops.where(condition, a, b)
        >>> print(output)
        [[0. 1.]
         [2. 1.]]
    
    .. function:: where(condition) -> Tensor
        :noindex:

    Identical to :func:`mindspore.ops.nonzero` with input `condition` and `as_tuple` being True.

    Supported Platforms:
        ``Ascend``
    """
    return _where_instance(*args, **kwargs)

__all__ = [
    "all_gather_matmul",
    "bitwise_not",
    "clamp",
    "clip",
    "div",
    "divide",
    "empty",
    "fmod",
    "lerp",
    "matmul_reduce_scatter",
    "max",
    "min",
    "nansum",
    "remainder",
    "repeat_interleave",
    "where",
]
