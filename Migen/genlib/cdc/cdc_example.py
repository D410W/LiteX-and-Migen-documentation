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