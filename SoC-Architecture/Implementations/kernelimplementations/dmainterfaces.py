from migen import *
from litex.soc.interconnect.csr import AutoCSR, CSRStorage, CSRStatus
from litex.soc.interconnect import stream

from .lightinference import ReLU


class StreamConvFusionLayer(Module, AutoCSR):
  """
  Fused convolution layer for better data flow between each kernel.

  DMA reader -> Con2D -> Quantizer -> ReLU -> MaxPooling -> DMA writer
  """
  def __init__(self):
    self.o = Signal() # TODO


class StreamReLU(Module):
  """
  ReLU single accelerator for testing.

  DMA reader -> ReLU -> DMA writer
  """
  def __init__(self, width=32, vector_size=1):
    assert (width % vector_size) == 0
    lane_width = width // vector_size

    self.sink   = stream.Endpoint([("data", width)])
    self.source = stream.Endpoint([("data", width)])

    self.submodules.relus = [ReLU(width=lane_width) for _ in range(vector_size)]

    # ReLU handshake as a combinational pass-through
    self.comb += [
      self.source.valid.eq(self.sink.valid),
      self.sink.ready.eq(self.source.ready),
    ]

    # ReLU input connections
    for i in range(vector_size):
      start_bit = i * lane_width
      end_bit = (i+1) * lane_width
      self.comb += self.relus[i].i.eq(self.sink.data[start_bit:end_bit])
    
    # ReLU output connections
    self.comb += self.source.data.eq(
      Cat( *[relu.o for relu in self.relus] )
    )


"""
ReLU single accelerator for testing.

DMA reader -> ReLU -> DMA writer
"""
class StreamMaxPooling(Module):
  def __init__(self, width=32, vector_size=1):