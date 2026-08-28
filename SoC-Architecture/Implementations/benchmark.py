from migen.fhdl import verilog
from kernelimplementations import StreamReLU

duts = [
  StreamReLU(data_width=32, vector_size=4)
]

ios = {
  dut.sink.data, dut.sink.valid, dut.sink.ready,
  dut.source.data, dut.source.valid, dut.source.ready,
}

for dut in duts:
  verilog_text = verilog.convert(dut, ios=ios, name="top_module")
  with open("benchmarks/streamrelu.v", "w") as f:
    f.write(str(verilog_text))
