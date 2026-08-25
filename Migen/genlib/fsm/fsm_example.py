from migen import *
from migen.genlib.fsm import FSM, NextState, NextValue

class TxController(Module):
  def __init__(self):
    self.start = Signal()
    self.tx_ready = Signal()
    self.bit_count = Signal(3)

    # - Instantiate the FSM (defaults to first defined state if reset_state is omitted)
    self.submodules.fsm = fsm = FSM(reset_state="IDLE")

    # - Define state behaviors and transitions with .act()
    fsm.act("IDLE",
      self.tx_ready.eq(1),
      If(self.start,
        NextValue(self.bit_count, 0),
        NextState("TRANSMIT")
      )
    )

    fsm.act("TRANSMIT",
      self.tx_ready.eq(0),
      NextValue(self.bit_count, self.bit_count + 1),
      If(self.bit_count == 7,
        NextState("DONE")
      )
    )

    fsm.act("DONE",
      self.tx_ready.eq(1),
      NextState("IDLE")
    )

dut = TxController()