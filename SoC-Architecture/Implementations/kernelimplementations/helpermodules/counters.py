from migen import *
from migen.genlib.fifo import SyncFIFO
from litex.soc.interconnect import stream

from .linebuffer import LineBuffer


class PositionCounter(Module):
  """
  A counter for the pixel's positions x and y.
  """
  def __init__(self, max_input_width, max_input_height):
    self.x = Signal(max=max_input_width)
    self.y = Signal(max=max_input_height)

    self.width  = Signal(16) # CSR-customizable counter dimensions
    self.height = Signal(16)

    self.x_last = Signal()
    self.y_last = Signal()
    self.x_first = Signal()
    self.y_first = Signal()

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

    # Helper signals that indicate row or column start
    self.comb += [
      If(self.x == 0,
        self.x_first.eq(1)
      ).Else(
        self.x_first.eq(0)
      ),
      If(self.y == 0,
        self.y_first.eq(1)
      ).Else(
        self.y_first.eq(0)
      )
    ]

    # Helper signals that indicate row or column end
    self.comb += [
      If(self.x == self.width - 1,
        self.x_last.eq(1)
      ).Else(
        self.x_last.eq(0)
      ),
      If(self.y == self.height - 1,
        self.y_last.eq(1)
      ).Else(
        self.y_last.eq(0)
      )
    ]


class PoolingPositionCounter(Module):
  """
  A counter for the pixel's positions x and y, as well as intra-kernel's positions.
  """
  def __init__(self, max_input_width, max_input_height, kernel_size):
    assert max_input_width % kernel_size == 0
    assert max_input_height % kernel_size == 0
    
    self.submodules.pos_counter = PositionCounter(max_input_width, max_input_width)

    # Exposing submodule CSRs
    self.x = self.pos_counter.x
    self.y = self.pos_counter.y
    
    self.width = self.pos_counter.width
    self.height = self.pos_counter.height
    
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

    self.enable = self.pos_counter.enable

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
