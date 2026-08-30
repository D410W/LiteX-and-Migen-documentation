from migen import *
from migen.genlib.fifo import SyncFIFO
from litex.soc.interconnect import stream

class LineBuffer(Module):
  """
  FIFO-based line buffer encapsulating row storage and stream handshakes.
  """
  def __init__(self, depth, data_width=32, signed=False):
    fifo_depth = max(2, depth)

    self.sink   = stream.Endpoint([("data", (data_width, signed))])
    self.source = stream.Endpoint([("data", (data_width, signed))])

    self.submodules.fifo = fifo = SyncFIFO(width=data_width, depth=fifo_depth)

    self.comb += [
      fifo.we.eq(self.sink.valid), # tells the fifo theres input i have input
      self.sink.ready.eq(fifo.writable), # im ready to receive input only when the fifo is ready to receive input
      fifo.din.eq(self.sink.data), # data in

      self.source.valid.eq(fifo.readable), # i only have output when the fifo has output
      fifo.re.eq(self.source.ready), # tells the fifo it can output only when i can output
      self.source.data.eq(fifo.dout), # data out
    ]
