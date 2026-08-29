from migen import *
from litex.soc.interconnect import stream
from litex.soc.interconnect.csr import CSRStorage, AutoCSR
import math

from .helpermodules import build_sum_tree, SlidingWindow2D

class Conv2D(Module):
  """

  """
  def __init__(self, data_width=8, weight_width=8, kernel_size=3, has_bias=True, bias_width=32):
    # Datapath dimensions
    kernel_area = kernel_size * kernel_size
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
  def __init__(self, data_width=8, weight_width=8, kernel_size=3,
               max_width=512, max_height=512, has_bias=True, bias_width=32, signed=True):
    kernel_area = kernel_size * kernel_size

    # CSR registers
    self.csr_width   = CSRStorage(16, reset=8, description="Image Width")
    self.csr_height  = CSRStorage(16, reset=8, description="Image Height")
    self.csr_bias  = CSRStorage(bias_width, reset=0, description="Conv2D Bias")
    self.csr_weights = [
      CSRStorage(weight_width, name=f"w_{i}", description=f"Kernel Weight {i}")
      for i in range(kernel_area)
    ]

    # Sliding window buffer and arithmetic core
    self.submodules.window = SlidingWindow2D(
      data_width=data_width,
      kernel_size=kernel_size,
      max_width=max_width,
      max_height=max_height,
      signed=signed
    )

    self.submodules.core = Conv2D(
      data_width=data_width,
      weight_width=weight_width,
      kernel_size=kernel_size,
      has_bias=has_bias,
      bias_width=bias_width
    )

    # Stream endpoints
    out_width = len(self.core.result)
    self.sink   = stream.Endpoint([("data", (data_width, signed))])
    self.source = stream.Endpoint([("data", (out_width, signed))])

    self.comb += self.sink.connect(self.window.sink)

    # CSR and datapath configuration
    self.comb += [
      self.window.width.eq(self.csr_width.storage),
      self.window.height.eq(self.csr_height.storage),
    ]

    # Input weights and bias into the compute core
    if has_bias:
      self.comb += self.core.bias.eq(self.csr_bias.storage)

    for i in range(kernel_area):
      self.comb += self.core.weights[i].eq(self.csr_weights[i].storage)

    # Flatten 2D window taps into 1D Conv2D input array (row-major order)
    for r in range(kernel_size):
      for c in range(kernel_size):
        tap_idx = r * kernel_size + c
        self.comb += self.core.pixels[tap_idx].eq(self.window.pixels[r][c])

    # Output stream
    self.comb += [
      self.source.data.eq(self.core.result),
      self.source.valid.eq(self.window.valid_out),
      self.window.ready_out.eq(self.source.ready)
    ]