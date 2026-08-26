from migen import *

from .helpermodules import LineBuffer

class MaxPooling(Module):
  """
  Max Pooling datapath with coordinate tracking and spatial decimation.
  """
  def __init__(self, input_width=8, input_height=8, kernel_size=2):
    self.o = Signal(max=input_width)

    self.submodules.linebuffer = LineBuffer(depth=kernel_size)