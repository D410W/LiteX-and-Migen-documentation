# cdc

This module provides Clock Domain Crossing (CDC) primitives designed to safely pass signals, single-cycle pulses, and multi-bit data buses across asynchronous clock domains without metastability or data loss.

Key primitives provided:
* **MultiReg(i, o, odomain, n=2)**: Multi-stage flip-flop synchronizer chain (default $N=2$) with `no_retiming` synthesis attributes to synchronize quasi-static or single-bit level signals.
* **PulseSynchronizer(idomain, odomain)**: Safely transfers a single-clock pulse from an input domain to an output domain using toggle registers.
* **BusSynchronizer(width, idomain, odomain)**: Transfers coherent multi-bit data buses using a ping-pong handshake mechanism to avoid bus skew issues.
* **BlindTransfer(idomain, odomain, data_width)**: Pulse/data transfer with input back-pressure (blinding) to prevent lost pulses when pulses occur close together.
* **GrayCounter(width) / GrayDecoder(width)**: Counters and decoders where only 1 bit transitions per increment, ideal for asynchronous pointer comparison (used in `AsyncFIFO`).
* **ElasticBuffer & Gearbox**: Dual-clock FIFO buffers and width-converting data alignment pipelines between related clock trees.

```python
from migen import *
from migen.genlib.cdc import MultiReg, PulseSynchronizer, BusSynchronizer

class CDCDemo(Module):
  def __init__(self):
    # Asynchronous external input button
    self.btn_async = Signal()
    self.btn_sys = Signal()

    # - Level Synchronizer, 2-stage register chain into "sys" domain
    self.specials += MultiReg(self.btn_async, self.btn_sys, odomain="sys", n=2)

    # - Pulse Synchronizer, transfer 1-cycle strobe from "sys" to "video"
    self.trigger_sys = Signal()
    self.trigger_pix = Signal()
    self.submodules.ps = PulseSynchronizer(idomain="sys", odomain="video")
    self.comb += [
      self.ps.i.eq(self.trigger_sys),
      self.trigger_pix.eq(self.ps.o)
    ]

    # - Coherent Bus Synchronizer, safe 32-bit transfer from "sys" to "video"
    self.data_sys = Signal(32)
    self.data_pix = Signal(32)
    self.submodules.bus_sync = BusSynchronizer(
      width=32, idomain="sys", odomain="video"
    )
    self.comb += [
      self.bus_sync.i.eq(self.data_sys),
      self.data_pix.eq(self.bus_sync.o)
    ]

dut = CDCDemo()
```