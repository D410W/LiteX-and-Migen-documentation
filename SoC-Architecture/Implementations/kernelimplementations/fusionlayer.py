from migen import *
from litex.soc.interconnect import stream
from litex.soc.interconnect.csr import CSRStorage, AutoCSR

from .conv2d import StreamConv2D
from .quantizer import StreamSymDyQuantizer
from .pooling import StreamMaxPooling
from .lightinference import StreamReLU


class StreamConvFusionLayer(Module, AutoCSR):
  """
  Fused Vision Layer:
  DMA In -> StreamConv2D -> StreamSymDyQuantizer -> ReLU -> StreamMaxPooling -> DMA Out
  """
  def __init__(self, data_width=8, weight_width=8, conv_kernel=3, pool_kernel=2,
               max_width=512, max_height=512, bias_width=32, signed=True):

    # Endpoints
    self.sink   = stream.Endpoint([("data", (data_width, signed))])
    self.source = stream.Endpoint([("data", (data_width, signed))])

    # Frame dims CSRs
    self.csr_width  = CSRStorage(16, reset=max_width, description="Input Frame Width")
    self.csr_height = CSRStorage(16, reset=max_height, description="Input Frame Height")

    # Conv2D
    self.submodules.conv = StreamConv2D(
        data_width=data_width,
        weight_width=weight_width,
        kernel_size=conv_kernel,
        max_width=max_width,
        max_height=max_height,
        has_bias=True,
        bias_width=bias_width,
        signed=signed
    )

    # Quantizer
    conv_out_width = len(self.conv.source.data)
    self.submodules.quant = StreamSymDyQuantizer(
        in_width=conv_out_width,
        out_width=data_width,
        vector_size=1
    )

    # ReLU
    self.submodules.relu = StreamReLU(
      data_width=data_width,
      vector_size=1
    )

    # Max pooling
    self.submodules.pool = StreamMaxPooling(
        data_width=data_width,
        kernel_size=pool_kernel,
        max_input_width=max_width,
        max_input_height=max_height,
        signed=signed
    )

    # Submodules dimensions config
    self.comb += [
        self.conv.csr_width.storage.eq(self.csr_width.storage),
        self.conv.csr_height.storage.eq(self.csr_height.storage),

        self.pool.csr_width.storage.eq(self.csr_width.storage - (conv_kernel - 1)),
        self.pool.csr_height.storage.eq(self.csr_height.storage - (conv_kernel - 1)),
    ]


    # Sink -> Conv2D
    self.comb += self.sink.connect(self.conv.sink)

    # Conv2D -> Quantizer
    self.comb += self.conv.source.connect(self.quant.sink)

    # Quantizer -> ReLU
    self.comb += self.quant.source.connect(self.relu.sink)

    # ReLU -> MaxPooling
    self.comb += self.relu.source.connect(self.pool.sink)

    # MaxPooling -> Source
    self.comb += self.pool.source.connect(self.source)