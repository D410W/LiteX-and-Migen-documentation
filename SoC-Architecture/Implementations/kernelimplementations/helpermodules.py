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
      fifo.we.eq(self.sink.valid), # tells the fifo there's input i have input
      self.sink.ready.eq(fifo.writable), # im ready to receive input only when the fifo is ready to receive input
      fifo.din.eq(self.sink.data), # data in

      self.source.valid.eq(fifo.readable), # i only have output when the fifo has output
      fifo.re.eq(self.source.ready), # tells the fifo it can output only when i can output
      self.source.data.eq(fifo.dout), # data out
    ]


class PoolingPositionCounter(Module):
  """
  A counter for the pixel's positions x and y, as well as kernel's positions.
  """
  def __init__(self, max_input_width, max_input_height, kernel_size):
    assert max_input_width % kernel_size == 0
    assert max_input_height % kernel_size == 0

    self.x = Signal(max=max_input_width)
    self.y = Signal(max=max_input_height)

    self.width  = Signal(16) # CSR-customizable counter dimensions
    self.height = Signal(16)

    if max_input_width // kernel_size == 1:
      self.kx = Signal()
    else:
      self.kx = Signal(max=kernel_size)

    if max_input_height // kernel_size == 1:
      self.ky = Signal()
    else: 
      self.ky = Signal(max=kernel_size)

    self.kx_last = Signal()
    self.ky_last = Signal()
    self.kx_first = Signal()
    self.ky_first = Signal()

    self.enable = Signal()

    # Pixel position update
    self.sync += [
      If(self.enable,
        If(self.x == self.width - 1,
          self.x.eq(0),
          If(self.y == self.height - 1,
            self.y.eq(0)
          ).Else(
            self.y.eq(self.y + 1)
          )
        ).Else(
          self.x.eq(self.x + 1)
        )
      )
    ]

    # Kernel position update
    self.sync += [
      If(self.enable,
        If(self.kx == kernel_size - 1,
          self.kx.eq(0),

          If(self.x == self.width - 1,
            If(self.ky == kernel_size - 1,
              self.ky.eq(0)
            ).Else(
              self.ky.eq(self.ky + 1)
            )
          )
        ).Else(
          self.kx.eq(self.kx + 1)
        )
      )
    ]

    # Helper signals that indicate row or column start
    self.comb += [
      If(self.kx == 0,
        self.kx_first.eq(1)
      ).Else(
        self.kx_first.eq(0)
      ),
      If(self.ky == 0,
        self.ky_first.eq(1)
      ).Else(
        self.ky_first.eq(0)
      )
    ]

    # Helper signals that indicate row or column end
    self.comb += [
      If(self.kx == kernel_size - 1,
        self.kx_last.eq(1)
      ).Else(
        self.kx_last.eq(0)
      ),
      If(self.ky == kernel_size - 1,
        self.ky_last.eq(1)
      ).Else(
        self.ky_last.eq(0)
      )
    ]


class SlidingWindow2D(Module):
  def __init__(self, data_width=8, kernel_size=3, max_width=512, max_height=512, signed=True):
    self.kernel_area = kernel_size * kernel_size

    # Stream input (pixels)
    self.sink = stream.Endpoint([("data", (data_width, signed))])

    # Dynamic dimensions
    self.width  = Signal(16)
    self.height = Signal(16)

    # Downstream flow control
    self.ready_out = Signal() # Output ready (from conv2d)
    self.valid_out = Signal() # Output valid (when full KxK window is ready)

    # Flat parallel outputs exposed to compute cores (Conv2D, etc.)
    # self.pixels = [
    #   Signal((data_width, signed), name=f"win_pix_{i}") 
    #   for i in range(self.kernel_area)
    # ]
    self.pixels = [
      [
        Signal((data_width, signed), name=f'win_pix_{i}_{j}')
        for i in range(kernel_size)
      ]
      for j in range(kernel_size)
    ]

    # Line buffers
    self.submodules.line_buffers = [LineBuffer(depth=kernel_size-1, data_width=data_width, signed=signed) for _ in range(kernel_size - 1)]

    # Shift registers (KxK 2D array)
    
    
    # Raster coordinate counter (x, y)

    # IO logic
    

def build_tree(operands, operation):
  current_level = operands
  while len(current_level) > 1:
    next_level = []
    for i in range(0, len(current_level), 2):
      if i + 1 < len(current_level):
        next_level.append(operation(current_level[i], current_level[i + 1]))
      else: # odd element
        next_level.append(current_level[i])
    current_level = next_level
  return current_level[0]

def signed_max(a, b):
  return Mux(a > b, a, b)

def build_max_tree(operands):
  return build_tree(operands, signed_max)

def signed_sum(a, b):
  return a + b

def build_sum_tree(operands):
  return build_tree(operands, signed_sum)