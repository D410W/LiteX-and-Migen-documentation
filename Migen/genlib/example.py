from migen import *
from migen.genlib.fsm import FSM, NextState, NextValue

class BlinkerFSM(Module):
  def __init__(self):
    self.led = Signal()
    self.trigger = Signal()

    # Define FSM
    self.submodules.fsm = fsm = FSM(reset_state="IDLE")

    fsm.act("IDLE",
      self.led.eq(0),
      If(self.trigger,
        NextState("ACTIVE")
      )
    )

    fsm.act("ACTIVE",
      self.led.eq(1),
      If(~self.trigger,
        NextState("IDLE")
      )
    )

dut = BlinkerFSM()