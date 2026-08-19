# Migen

**Migen** is a Python-based toolbox for designing, simulating, and generating complex digital hardware (FHDL - Functional Hardware Description Language). Rather than acting as an interpreter or high-level synthesizer, Migen uses Python as an 'elaboration language' to construct and optimize abstract syntax trees (AST) that translate into synthesizable Verilog or run directly inside a simulator.

Migen powers the digital logic foundation of the [LiteX](https://github.com/enjoy-digital/litex) ecosystem for building complete Systems-on-Chip (SoCs).

* **Official Website:** [m-labs.hk/misc/migen](https://m-labs.hk/misc/migen/)
* **Upstream Repository:** [github.com/m-labs/migen](https://github.com/m-labs/migen) or [git.m-labs.hk/M-Labs/migen](https://git.m-labs.hk/M-Labs/migen)

## Migen workflow

In Migen, Python code executes only once during elaboration to build the hardware:
* Statements inside `__init__` do not execute at runtime on the FPGA; they register hardware connections.
* Statements assigned with `+=` to `self.comb` define combinational wires and gates with continuous evaluation.
* Statements assigned with `+=` to `self.sync` define synchronous operations.

## Repository Structure & Documentation

migen/\
├── fhdl/\
├── sim/\
├── genlib/\
├── build/\
├── interconnect/\
└── actor/


### 1. `fhdl` (Core Language)
The foundation of Migen. It defines the AST primitives, data structures, and compiler transformations.

### 2. `sim` (Simulation Engine)
A cycle-accurate, event-driven hardware simulator written in pure Python.

### 3. `genlib` (Generic Core Library)
A collection of pre-built, parameterized hardware modules.

### 4. `build` (Platform & Synthesis Backends)
Bridges abstract designs with physical FPGA hardware.

### 5. `interconnect` (System Interconnects)
Standards for connecting complex modules and memories together.

## Quick Start Example

A simple synchronous 8-bit counter and Python testbench:

```Python
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
```