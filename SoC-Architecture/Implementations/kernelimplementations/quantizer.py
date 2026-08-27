from migen import *
from litex.soc.interconnect import stream
from litex.soc.interconnect.csr import CSRStorage, AutoCSR

class SymDyQuantizer(Module):
  """
  Symmetric Dyatic Quantizer accelerator.
  """
  def __init__(self, in_width=32, out_width=8, mult_width=16):
    # IO
    self.input_data = Signal((in_width, True))
    self.multiplier = Signal((mult_width, True))
    self.shift = Signal((5, True))
    self.output_data = Signal((out_width, True))

    # Datapath dimensions
    prod_width  = in_width + mult_width + 1
    quant_min = -(1 << (out_width - 1))      # -128 for INT8
    quant_max =  (1 << (out_width - 1)) - 1  # +127 for INT8

    # Datapath signals
    product      = Signal((prod_width, True))
    bias         = Signal((prod_width, True))
    biased_prod  = Signal((prod_width, True))
    shifted_val  = Signal((prod_width, True))
    clamped_val  = Signal((out_width, True))

    # Product
    self.comb += [
      product.eq(self.input_data * self.multiplier)
    ]

    # Shifted and rounded intermediate signal
    self.comb += [
      If(self.shift > 0,
        bias.eq(1 << (self.shift - 1))
      ).Else(
        bias.eq(0)
      ),
      biased_prod.eq(product + bias)
    ]

    self.comb += [
      shifted_val.eq(biased_prod >> self.shift)
    ]

    # Clamped output
    self.comb += [
      If(shifted_val > quant_max,
        clamped_val.eq(quant_max)
      ).Elif(shifted_val < quant_min,
        clamped_val.eq(quant_min)
      ).Else(
        clamped_val.eq(shifted_val[:out_width])
      )
    ]

    # Output
    self.comb += [
      self.output_data.eq(clamped_val)
    ]

class StreamSymDyQuantizer(Module, AutoCSR):
  """
  Symmetric Dyatic Quantizer single accelerator for testing.

  DMA reader -> SDQ -> DMA writer
  """
  def __init__(self, in_width=32, out_width=8, mult_width=16, vector_size=1):
    assert (in_width % vector_size) == 0
    assert vector_size >= 1
    lane_width = in_width // vector_size

    # Stream endpoints
    self.sink   = stream.Endpoint([("data", (in_width, True))])
    self.source = stream.Endpoint([("data", (out_width, True))])

    # CSRs for runtime scale tuning
    self.csr_mult  = CSRStorage(mult_width, description="Quantization multiplier (M)")
    self.csr_shift = CSRStorage(5,          description="Dyadic right-shift exponent (n)")

    self.submodules.quantizers = [
      SymDyQuantizer(in_width=in_width, out_width=out_width, mult_width=mult_width)
      for _ in range(vector_size)
    ]

    # Quantizer submodules input connections
    for i in range(vector_size):
      start_bit = i * lane_width
      end_bit = (i+1) * lane_width
      self.comb += [
        self.quantizers[i].multiplier.eq(self.csr_mult.storage),
        self.quantizers[i].shift.eq(self.csr_shift.storage),
        self.quantizers[i].input_data.eq(self.sink.data[start_bit:end_bit])
      ]

    # Connecting quantizers output data to streams and CSRs
    self.comb += self.source.data.eq(
      Cat( *[quantizer.output_data for quantizer in self.quantizers] )
    )

    # Stream handshake
    self.comb += [
      self.source.valid.eq(self.sink.valid),
      self.sink.ready.eq(self.source.ready),
    ]

dut = StreamSymDyQuantizer()