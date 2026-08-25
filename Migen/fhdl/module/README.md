# migen.fhdl.module

Modules in Migen are containers for hardware objects and circuits. Every single design involves subclassing 'Module' in order to be able to run.

self.comb += ... and self.sync += ... append operations that define the behavior of the module.\
Combinational hardware is re-evaluated when any of their entries changes, and Syncronous hardware is re-evaluated every clock cycle.

Usage example:

```Python
from migen import *

# Sub-module: simple 8-bit Counter
class Counter(Module):
  def __init__(self, width=8):
    # Declare hardware signals
    self.count = Signal(width)
    self.enable = Signal()

    # Synchronous logic: evaluated on the rising edge of the default clock
    self.sync += [
      If(self.enable,
        self.count.eq(self.count + 1)
      )
    ]


# Parent Module: uses the Counter submodule and multiple clock domains
class TopModuleExample(Module):
  def __init__(self):
    self.led = Signal()
    self.slow_signal = Signal()

    # - Registering submodules
    # Migen needs 'self.submodules' registration to build the child hardware
    self.submodules.my_counter = Counter(width=8)

    # - Combinatorial Logic (self.comb)
    # Evaluates immediately whenever inputs change (like gates/wires)
    self.comb += [
      self.my_counter.enable.eq(1),             # Enable the counter continuously
      self.led.eq(self.my_counter.count > 128)  # Turn on LED when count > 128
    ]

    # - Synchronous kogic in a 'named clock domain' (self.sync.<domain>)
    # Runs on the 'pix' (pixel clock) domain instead of default 'sys'
    # since we didn't create this 'pix' clock, this piece of code will fail.
    #
    # self.sync.pix += [
    #   self.slow_signal.eq(~self.slow_signal)
    # ]

from migen.sim import run_simulation

def testbench(dut):
  yield # Each yield advances time by 1 cycle.
  yield 
  # Asserts are a good way of testing or debugging simpler designs.
  assert (yield dut.led) == 0, f"Error: Expected 0, got {(yield dut.led)}"

# Instancing the module and testing it
dut = TopModuleExample()
run_simulation(dut, testbench(dut))
```