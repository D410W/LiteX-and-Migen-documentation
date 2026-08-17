from migen import *
from migen.sim import run_simulation

# Defining the Hardware Module
class Counter(Module):
  def __init__(self, width=8):
    self.count = Signal(width)
    self.enable = Signal()

    # Synchronous logic, increments on rising clock edge
    self.sync += [
      If(self.enable,
        self.count.eq(self.count + 1)
      )
    ]

# Defining the Python Testbench
# Each yield advances time by 1 clock cycle
def testbench(dut):
  # Enable counting
  yield dut.enable.eq(1)
  for _ in range(5):
    yield
    print(f"Count: {(yield dut.count)}")

  # Pause counting
  yield dut.enable.eq(0)
  yield
  yield
  print(f"Final Paused Count: {(yield dut.count)}")

# 3. Simulate or Convert
if __name__ == "__main__":
  dut = Counter(width=8)
  
  # Running simulation
  run_simulation(dut, testbench(dut), vcd_name="counter.vcd")
  
  # Or exporting to Verilog:
  # from migen.fhdl import verilog
  # print(verilog.convert(dut, ios={dut.count, dut.enable}))