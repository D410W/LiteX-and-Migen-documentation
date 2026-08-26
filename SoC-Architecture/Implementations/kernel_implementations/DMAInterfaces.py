from migen import *
from litex.soc.interconnect.csr import AutoCSR, CSRStorage, CSRStatus
from litex.soc.interconnect import stream

from .LightInference import ReLU

"""
Fused convolution layer for better data flow between each kernel.

DMA reader -> Con2D -> Quantizer -> ReLU -> MaxPooling -> DMA writer
"""
class DMAConvFusionLayer(Module, AutoCSR):
  def __init__(self):
    self.o = Signal() # TODO

"""
ReLU single accelerator for testing.

DMA reader -> ReLU -> DMA writer
"""
class DMAReLU(Module):
  def __init__(self, width=32):
    self.sink   = stream.Endpoint([("data", width)])
    self.source = stream.Endpoint([("data", width)])

    self.submodules.relu = ReLU(width=width)

    # ReLU handshake as a combinational pass-through
    self.comb += self.source.valid.eq(self.sink.valid)
    self.comb += self.sink.ready.eq(self.source.ready)

    # ReLU input and output connections
    self.comb += self.relu.i.eq(self.sink.data)
    self.comb += self.source.data.eq(self.relu.o)
