from migen import *
from migen.genlib.fifo import SyncFIFO, AsyncFIFO
from migen.fhdl.decorators import ClockDomainsRenamer

# 1. Synchronous FIFO (Single clock domain)
# Buffers up to 16 elements of 32-bit data
sync_fifo = SyncFIFO(width=32, depth=16)

# Writing to the FIFO
we = Signal()
data_in = Signal(32)
can_write = sync_fifo.writable
sync_fifo.din.eq(data_in)
sync_fifo.we.eq(we & can_write)

# Reading from the FIFO
re = Signal()
data_out = sync_fifo.dout
has_data = sync_fifo.readable
sync_fifo.re.eq(re & has_data)


# 2. Asynchronous FIFO (Dual clock domain crossing)
# Transfers data from the "sys" domain to the "pix" domain
async_fifo = ClockDomainsRenamer({"write": "sys", "read": "pix"})(
    AsyncFIFO(width=16, depth=8)
)