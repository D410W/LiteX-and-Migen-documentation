from migen import *
from litex.soc.interconnect import stream
from litex.soc.interconnect.csr import CSRStorage, AutoCSR

from .helpermodules import LineBuffer, PoolingPositionCounter, build_max_tree

class StreamMaxPooling(Module, AutoCSR):
  """
  MaxPooling single accelerator for testing.

  DMA reader -> MaxPooling -> DMA writer
  """
  def __init__(self, data_width=32, max_input_width=32, max_input_height=32,
               default_width=8, default_height=8, kernel_size=2, signed=False):
    assert max_input_width % kernel_size == 0
    assert max_input_height % kernel_size == 0
    assert max_input_width >= kernel_size, "'input_width' must be at least 'kernel_size'"

    self.sink   = stream.Endpoint([("data", (data_width, signed))])
    self.source = stream.Endpoint([("data", (data_width, signed))])
    sink_data = Signal((data_width, signed))
    self.comb += sink_data.eq(self.sink.data)

    self.csr_width  = CSRStorage(16, reset=default_width,  description="Input image width in pixels")
    self.csr_height = CSRStorage(16, reset=default_height, description="Input image height in pixels")

    max_kernels_width = max_input_width // kernel_size
    
    data_moving = Signal()

    # Horizontal reduction
    h_accumulator = Signal((data_width, signed)) # Updated on the next clock cycle
    h_max = Signal((data_width, signed)) # Updated combinationally (available this cycle)

    self.line_buffers = [LineBuffer(depth=max_kernels_width, data_width=data_width, signed=signed) for _ in range(kernel_size - 1)]
    self.submodules += self.line_buffers

    # Coordinate tracking
    self.submodules.pooling_counter = PoolingPositionCounter(
      max_input_width=max_input_width, max_input_height=max_input_height, kernel_size=kernel_size
    )
    # Coordinate counting enabling
    self.comb += [
      self.pooling_counter.width.eq(self.csr_width.storage),
      self.pooling_counter.height.eq(self.csr_height.storage),
      self.pooling_counter.enable.eq(data_moving),
    ]

    # Handshake setup
    lb_readies = Array([lb.sink.ready for lb in self.line_buffers])

    self.comb += [
      If(self.pooling_counter.kx_last,
        If(self.pooling_counter.ky_last,
          self.sink.ready.eq(self.source.ready)
        ).Else(
          self.sink.ready.eq(lb_readies[self.pooling_counter.ky])
        )
      ).Else(
        self.sink.ready.eq(1)
      ),
      data_moving.eq(self.sink.valid & self.sink.ready)
    ]

    # Horizontal reduction logic
    self.comb += [
      If(self.pooling_counter.kx_first,
        h_max.eq(sink_data)
      ).Else(
        If(sink_data > h_accumulator,
          h_max.eq(sink_data)
        ).Else(
          h_max.eq(h_accumulator)
        )
      )
    ]
    self.sync += [
      If(data_moving,
        h_accumulator.eq(h_max)
      )
    ]

    # Line buffers popping logic
    pop_line_buffers = Signal()
    self.comb += [
      pop_line_buffers.eq(data_moving & self.pooling_counter.kx_last & (self.pooling_counter.ky_last)),

      *[lb.source.ready.eq(pop_line_buffers & self.source.ready) for lb in self.line_buffers] # Pop line buffers on completion of each kernel
    ]

    # Vertical logic
    for y_idx in range(kernel_size):
      if y_idx == (kernel_size - 1):
        operands = [lb.source.data for lb in self.line_buffers] + [h_max]
        final_max = build_max_tree(operands)

        self.comb += [
          self.source.data.eq(final_max)
        ]

        self.comb += [
          self.source.valid.eq( # If there's data moving, AND it's the kx_last 'pixel', AND it's at the k-1 kernel layer:
            self.sink.valid & self.pooling_counter.kx_last & (self.pooling_counter.ky == y_idx)
          ),
        ]
      else:
        lb = self.line_buffers[y_idx]
        
        self.comb += [
          lb.sink.valid.eq( # If there's data moving, AND it's at the kx_last pixel, AND is at this layer
            self.sink.valid & self.pooling_counter.kx_last & (self.pooling_counter.ky == y_idx)
          ),
          lb.sink.data.eq(h_max)
        ]