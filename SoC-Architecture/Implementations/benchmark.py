from migen.fhdl import verilog
from kernelimplementations import StreamReLU, StreamMaxPooling, StreamSymDyQuantizer, StreamConv2D, StreamConvFusionLayer

duts = [
  StreamReLU(data_width=32, vector_size=4),
  StreamMaxPooling(data_width=32, kernel_size=2, signed=True),
  StreamSymDyQuantizer(in_width=32, out_width=8, vector_size=1),
  StreamConv2D(
    data_width=32,
    weight_width=8,
    kernel_size=3,
    max_width=64,
    max_height=64
  ),
  StreamConvFusionLayer(),
]


for idx, dut in enumerate(duts):
  ios = {
    dut.sink.data, dut.sink.valid, dut.sink.ready,
    dut.source.data, dut.source.valid, dut.source.ready,
    *([csr.storage for csr in dut.get_csrs()] if hasattr(dut, 'get_csrs') else [])
  }

  verilog_text = verilog.convert(dut, ios=ios, name="top_module")
  filename = f"benchmarks/{type(dut).__name__.lower().removeprefix("stream")}.v"
  with open(filename, "w") as f:
    f.write(str(verilog_text))
