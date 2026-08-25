# divider

This module provides an iterative, multi-cycle integer division hardware core (`Divider`) based on a shift-and-subtract algorithm. It computes both the quotient and the remainder without requiring dedicated DSP blocks or generating large combinational delay paths.

Key signals and operational characteristics:
* **`w`**: Bit-width parameter for operands and results.
* **Latency**: Takes exactly 'w' clock cycles after `start_i` is pulsed to complete the computation.
* **Inputs:**
  * `start_i`: 1-cycle pulse that latches `dividend_i` and `divisor_i` and begins the iterative division.
  * `dividend_i`: Numerator input (`Signal(w)`).
  * `divisor_i`: Denominator input (`Signal(w)`).
* **Outputs:**
  * `ready_o`: High when the core is idle and available for a new operation, or when calculation is complete.
  * `quotient_o`: Division result $\lfloor \text{dividend} / \text{divisor} \rfloor$ (`Signal(w)`).
  * `remainder_o`: Remainder result (dividend mod divisor) (`Signal(w)`).

```python
from migen import *
from migen.genlib.divider import Divider
from migen.sim import run_simulation

class DividerDemo(Module):
  def __init__(self, width=16):
    # Instantiate 16-bit divider (takes 16 cycles per division)
    self.submodules.div = Divider(w=width)


# Simulation Testbench
def testbench(dut):
  # Set inputs: 100 / 7
  yield dut.div.dividend_i.eq(100)
  yield dut.div.divisor_i.eq(7)

  yield dut.div.start_i.eq(1) # Start division
  yield # Let the module recognize 'start_i' as active
  yield dut.div.start_i.eq(0) # Stop asking for divisions
  yield # Let the division module start it's computation

  # Wait for completion (ready_o asserts after 16 cycles)
  while not (yield dut.div.ready_o):
    yield

  quotient = (yield dut.div.quotient_o)   # 14
  remainder = (yield dut.div.remainder_o) # 2
  print(f"Result: {quotient} R {remainder}")

if __name__ == "__main__":
  dut = DividerDemo(width=16)
  run_simulation(dut, testbench(dut))
```