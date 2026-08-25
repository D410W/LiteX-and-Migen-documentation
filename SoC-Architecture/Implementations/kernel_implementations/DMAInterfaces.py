from migen import *
from litex.soc.interconnect.csr import AutoCSR, CSRStorage, CSRStatus

from LightInference import ReLU

"""
Fused convolution layer for better data flow between each kernel.

DMA reader -> Con2D -> Quantizer -> ReLU -> MaxPooling -> Output
"""
class DMAConvFusionLayer(Module, AutoCSR):
  def __init__(self):
    self.o = Signal() # TODO


class DMAReLU(Module):
  def __init__(self):
    self.submodules.relu = ReLU(width=32)
