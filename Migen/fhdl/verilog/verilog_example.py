from migen import *
from migen.fhdl import verilog

class Blinker(Module):
    def __init__(self):
        self.a = Signal(1)
        self.b = Signal(1)
        self.res = Signal(1)

        self.comb += self.res.eq(self.a ^ self.b)

dut = Blinker()

# Export Migen design to Verilog
verilog_code = verilog.convert(dut, ios={dut.a, dut.b, dut.res})
with open("output.v", "w") as f:
    f.write(str(verilog_code))