from migen import *
from litex.soc.interconnect.csr import CSRStorage, AutoCSR
import math

from .helpermodules import build_sum_tree

class Conv2D(Module):
  """
  Symmetric Dyatic Quantizer accelerator.
  """
  def __init__(self, data_width=8, weight_width=8, kernel_size=3, has_bias=True, bias_width=32):
    kernel_area = kernel_size * kernel_size

    # Datapath dimensions
    prod_width = data_width + weight_width

    max_prod_sum_width = data_width + weight_width + math.ceil(math.log2(kernel_area)) # Worst case scenario
    out_width = max(max_prod_sum_width, bias_width if has_bias else 0) + 1
    products = [Signal((prod_width, True)) for _ in range(kernel_area)]

    # IO
    self.pixels  = [Signal((data_width, True), name=f"pix_{i}") for i in range(kernel_area)]
    self.weights = [Signal((weight_width, True), name=f"w_{i}") for i in range(kernel_area)]

    if has_bias:
      self.bias = Signal((bias_width, True))
    
    self.result = Signal((out_width, True))

    # Product
    for i in range(kernel_area):
      self.comb += [
        products[i].eq(self.pixels[i] * self.weights[i])
      ]

    # Sum
    operands = products + [self.bias] if has_bias else products
    final_sum = build_sum_tree(operands)
    self.comb += [
      self.result.eq(final_sum)
    ]

class StreamConv2D(Module, AutoCSR):
  def __init__(self, data_width=8, weight_width=8, kernel_size=3, max_width=512, max_height=512):
    kernel_area = kernel_size * kernel_size

    # CSRs
    self.csr_width  = CSRStorage(16, reset=8, description="Image Width")
    self.csr_height = CSRStorage(16, reset=8, description="Image Height")
    self.csr_bias   = CSRStorage(32, reset=0, description="Conv2D Bias")
    self.csr_weights = [
      CSRStorage(weight_width, name=f"w_{i}", description=f"Kernel Weight {i}")
      for i in range(kernel_area)
    ]