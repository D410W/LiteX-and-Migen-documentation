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