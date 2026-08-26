from migen import *
from migen.genlib.fifo import SyncFIFO
from litex.soc.interconnect import stream


class LineBuffer(Module):
  """
  FIFO-based line buffer encapsulating row storage and stream handshakes.
  """
  def __init__(self, depth, data_width=16):
    self.sink   = stream.Endpoint([("data", data_width)])
    self.source = stream.Endpoint([("data", data_width)])

    self.submodules.fifo = fifo = SyncFIFO(width=data_width, depth=depth)

    self.comb += [
      fifo.sink.valid.eq(self.sink.valid),
      self.sink.ready.eq(fifo.sink.ready),
      fifo.sink.data.eq(self.sink.data),

      self.source.valid.eq(fifo.source.valid),
      fifo.source.ready.eq(self.source.ready),
      self.source.data.eq(fifo.source.data),
    ]