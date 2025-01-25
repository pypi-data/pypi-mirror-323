#!/usr/bin/env python
# ******************************************************************************
# Copyright 2024 Brainchip Holdings Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ******************************************************************************
__all__ = ["Conv2DTranposeOnnxConverter"]

import akida

from .activation import set_activation_variables
from .base_converter import OnnxConverter
from .check_compatibility import check_attributes, check_if_squared, check_weight_types
from .padding import compute_conv_transpose_same_pads
from .register import register_onnx_converter_target
from .scale_out import set_output_scale_variables
from .weights import set_weight_variables


def _get_conv_transpose_params(layer):
    # Parse common information
    layer_params = {
        "name": layer.name,
        "filters": layer.weights["W"].shape[1],
        "kernel_size": layer.weights["W"].shape[-1],
        "activation": layer.activation,
        "output_bits": 8,
    }

    return layer_params


@register_onnx_converter_target("QuantizedConv2DTranspose")
class Conv2DTranposeOnnxConverter(OnnxConverter):
    """Convert QuantizedConv2DTranspose type node into an akida.Conv2DTranspose.

    Args:
        node (NodeProto): the node to convert.
        model (ModelProto): the model that the node is.
    """

    def load_attributes(self, node):
        # Load default attributes
        super().load_attributes(node)

        # Some attributes should infer from node.op_type
        n_op = node.op_type
        self.activation = "ReLU" in n_op
        self.use_bias = "Biased" in n_op

    def _additional_checks(self):
        _check_transpose_convolution_compatibility(self)

    def _parse_akida_layer(self):
        layer_params = _get_conv_transpose_params(self)
        return akida.Conv2DTranspose(**layer_params)

    def _set_akida_variables(self, ak_layer):
        _set_tranpose_convolutional_variables(self, ak_layer)


def _set_tranpose_convolutional_variables(converter, ak_layer):
    assert isinstance(converter, OnnxConverter)

    # Get kernels and transpose them (C,F,Kx,Ky) -> (Kx,Ky,C,F)
    kernel = converter.weights["W"].transpose((2, 3, 0, 1))
    bias = converter.weights.get("bias", None)
    set_weight_variables(ak_layer, [kernel], bias)

    # Activation
    if converter.activation:
        set_activation_variables(ak_layer, converter.weights.get("max_value", None))

    # Scale out
    set_output_scale_variables(ak_layer, converter.weights["Scale"], converter.weights["Shift"])


def _check_transpose_convolution_compatibility(converter):
    # Weights constrains
    check_weight_types(converter,
                       weight_names=["W", "Scale", "Shift"],
                       expect_types=["int8", "uint8", "float32"])

    # Bias constrains
    if converter.use_bias:
        check_weight_types(converter=converter, weight_names=["bias"], expect_types=["int32"])

    # Max value constrains
    if "max_value" in converter.weights:
        check_weight_types(converter=converter, weight_names=["max_value"], expect_types=["int32"])

    # Attributes checks
    check_attributes(converter, ["strides"])

    # Other checks
    kernel_shapes = converter.weights["W"].shape[-2:]
    check_if_squared(kernel_shapes, name_val="kernels")
    check_if_squared(converter.strides, name_val="strides")

    # Check padding is SAME
    expected_padding = compute_conv_transpose_same_pads(kernel_shapes, converter.strides)
    if converter.pads != expected_padding:
        raise ValueError(f"{converter.name} expects to have '{expected_padding}' pads, "
                         f"found '{converter.pads}'.")
