# sort

This module provides a fully combinational parallel sorting network (`BitonicSort`) based on Batcher's bitonic sorting algorithm. It sorts a fixed-size array of inputs purely in combinational logic using a network of comparators and multiplexers with O(n log²(n)) complexity, requiring zero clock cycles of latency.

Key parameters and attributes:
* **`n`**: Number of input and output elements to sort.
* **`m`**: Bit-width of each element, or a `(width, signed)` tuple.
* **`ascending`**: Sort direction (`True` for ascending order, `False` for descending order; defaults to `True`).
* **`i`**: List of 'n' input `Signal(m)` items to be sorted.
* **`o`**: List of 'n' output `Signal(m)` items containing the sorted results.

```python
from migen import *
from migen.genlib.sort import BitonicSort
from migen.sim import run_simulation

class SorterDemo(Module):
  def __init__(self, n=4, width=8):
    # Instantiate 4-element, 8-bit combinational bitonic sorter
    self.submodules.sorter = BitonicSort(n=n, m=width, ascending=True)


# Simulation Testbench
def testbench(dut):
  # Provide unsorted inputs: [45, 12, 89, 3]
  unsorted_data = [45, 12, 89, 3]
  for sig, val in zip(dut.sorter.i, unsorted_data):
      yield sig.eq(val)

  yield  # Allow combinational logic to settle

  # Read sorted outputs
  sorted_data = []
  for sig in dut.sorter.o:
    sorted_data.append((yield sig))
  
  print(f"Unsorted: {unsorted_data}")
  print(f"Sorted:   {sorted_data}")  # Output: [3, 12, 45, 89]

if __name__ == "__main__":
  dut = SorterDemo(n=4, width=8)
  run_simulation(dut, testbench(dut))
```