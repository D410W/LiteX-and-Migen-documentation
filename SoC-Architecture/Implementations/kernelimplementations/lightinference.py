from migen import *
from litex.soc.interconnect import stream

# Works with IEEE 754 floats as well

class ReLU(Module):
  def __init__(self, width=8):
    self.i = Signal((width, True))
    self.o = Signal((width, True))

    self.comb += [
      If(self.i[width - 1],
        self.o.eq(0)
      ).Else(
        self.o.eq(self.i)
      )
    ]

class StreamReLU(Module):
  """
  ReLU single accelerator for testing.

  DMA reader -> ReLU -> DMA writer
  """
  def __init__(self, data_width=32, vector_size=1):
    assert (data_width % vector_size) == 0
    lane_width = data_width // vector_size

    self.sink   = stream.Endpoint([("data", (data_width, True))])
    self.source = stream.Endpoint([("data", (data_width, True))])

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