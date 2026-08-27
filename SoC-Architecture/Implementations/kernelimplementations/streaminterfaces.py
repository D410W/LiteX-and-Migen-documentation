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