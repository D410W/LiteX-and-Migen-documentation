# record

This module provides structured data containers (`Record`) and layout schemas (`Layout`) to group multiple related `Signal` objects into a single object (similar to a C `struct` or SystemVerilog `interface`).

It is used across LiteX to define bus standards (Wishbone, AXI, UART, SPI) and features automatic directional wiring between master and slave endpoints.

Key features and methods:
* **Layout Definitions:** Lists of tuples defining fields: `(name, size)` or `(name, size, direction)`.
* **Direction Constants:** `DIR_M_TO_S` (Master-to-Slave) and `DIR_S_TO_M` (Slave-to-Master) for directional buses.
* **master.connect(slave):** Automatically connects matching fields in `self.comb` according to their defined directions (`DIR_M_TO_S` -> `slave.eq(master)`, `DIR_S_TO_M` -> `master.eq(slave)`).
* **record.raw_bits()**: Returns a `Cat` concatenation of all signals in the record, allowing entire structures to be stored in FIFOs or memory blocks.
* **record.eq(other)**: Assigns all matching named fields from `other` to `self`.

```python
from migen import *
from migen.genlib.record import Record, DIR_M_TO_S, DIR_S_TO_M

# - Defining a structured bus layout
bus_layout = [
    ("adr",   30, DIR_M_TO_S),  # Master drives address
    ("dat_w", 32, DIR_M_TO_S),  # Master drives write data
    ("dat_r", 32, DIR_S_TO_M),  # Slave drives read data
    ("cyc",    1, DIR_M_TO_S),  # Bus cycle active
    ("ack",    1, DIR_S_TO_M),  # Slave acknowledge
]

class BusInterconnectDemo(Module):
  def __init__(self):
    # - Instantiating master and slave records
    self.master = Record(bus_layout, name="wb_master")
    self.slave  = Record(bus_layout, name="wb_slave")

    # Accessing individual fields directly
    self.comb += self.master.adr.eq(0x1000)

    # - Automatic directional connection
    # Connects adr, dat_w, cyc from master -> slave,
    # and dat_r, ack from slave -> master
    self.comb += self.master.connect(self.slave)

    # - Packing entire bus into a single wire vector (for example, for FIFO buffering)
    self.packed_bus = Signal(len(self.master))
    self.comb += self.packed_bus.eq(self.master.raw_bits())

dut = BusInterconnectDemo()
```