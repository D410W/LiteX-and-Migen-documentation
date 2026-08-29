from migen import *
from litex.soc.interconnect import stream

from .counters import PositionCounter
from .linebuffer import LineBuffer

class SlidingWindow2D(Module):
  def __init__(self, data_width=8, kernel_size=3, max_width=512, max_height=512, signed=True):
    self.kernel_area = kernel_size * kernel_size

    # Stream input (pixels)
    self.sink = stream.Endpoint([("data", (data_width, signed))])

    # Dynamic dimensions
    self.width  = Signal(16)
    self.height = Signal(16)

    # Output flow control
    self.ready_out = Signal() # Output ready (from conv2d)
    self.valid_out = Signal() # Output valid (when full KxK window is ready)
    
    data_moving = Signal() # If this module is actually processing values

    # Exposed pixel outputs (for Conv2D, etc.)
    self.pixels = [
      [
        Signal((data_width, signed), name=f'win_pix_{r}_{c}')
        for c in range(kernel_size)
      ]
      for r in range(kernel_size)
    ]

    # Line buffers
    self.submodules.line_buffers = [
      LineBuffer(depth=max_width, data_width=data_width, signed=signed)
      for _ in range(kernel_size - 1)
    ]

    # Pixel coordinate counter (x, y)
    self.submodules.pos_counter = PositionCounter(
      max_input_width=max_width, max_input_height=max_height
    )
    self.comb += [
      self.pos_counter.width.eq(self.width),
      self.pos_counter.height.eq(self.height),
      self.pos_counter.enable.eq(data_moving),
    ]

    
    # Shift registers
    row_inputs = []
    for r in range(kernel_size):
      if r == kernel_size - 1:
        row_inputs.append(self.sink.data)
      else:
        kernel_idx = kernel_size - r - 2
        row_inputs.append(self.line_buffers[kernel_idx].source.data)
    
    # History registers (2D)
    self.hist_pixels = [
      [
        Signal((data_width, signed), name=f'hist_pix_{r}_{c}')
        for c in range(kernel_size - 1)
      ]
      for r in range(kernel_size)
    ]

    self.sync += [
      If(data_moving,
        *[
          [
            self.hist_pixels[r][c].eq(self.hist_pixels[r][c + 1])
            for c in range(kernel_size - 2)
          ] + [
            self.hist_pixels[r][kernel_size - 2].eq(row_inputs[r])
          ]
          for r in range(kernel_size)
        ]
      )
    ]

    for r in range(kernel_size):
      for c in range(kernel_size):
        if c == kernel_size - 1:
          self.comb += self.pixels[r][c].eq(row_inputs[r])
        else:
          self.comb += self.pixels[r][c].eq(self.hist_pixels[r][c])
        
    # Internal data flow
    for idx, lb in enumerate(self.line_buffers):
      # Only pop once enough lines have entered the pipeline
      can_pop = Signal()
      self.comb += [
        can_pop.eq(self.pos_counter.y >= (idx + 1)),
        lb.source.ready.eq(data_moving & can_pop)
      ]
      
      if idx == 0:
        self.comb += [
          lb.sink.valid.eq(data_moving),
          lb.sink.data.eq(self.sink.data),
        ]
      else:
        prev_lb = self.line_buffers[idx - 1]
        self.comb += [
          lb.sink.valid.eq(data_moving & (self.pos_counter.y >= idx)),
          lb.sink.data.eq(prev_lb.source.data),
        ]

    # IO and handshake logic
    is_valid_window = Signal()
    self.comb += [
      is_valid_window.eq((self.pos_counter.x >= (kernel_size - 1)) & (self.pos_counter.y >= (kernel_size - 1))),
      self.valid_out.eq(self.sink.valid & is_valid_window),

      # Stream ready backpressure
      If(is_valid_window,
        self.sink.ready.eq(self.ready_out)
      ).Else(
        self.sink.ready.eq(1) # Fast-fill during startup warm-up
      ),

      data_moving.eq(self.sink.valid & self.sink.ready)
    ]
