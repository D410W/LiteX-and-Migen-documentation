# fsm

This module provides a high-level, declarative framework for building Finite State Machines (FSMs) in hardware without manually declaring state register signals, calculating binary encodings, or writing verbose `Case` trees.

Key operations and methods used when describing states:
* **a.eq(b)**: Combinational statement active only while in that state (equivalent to `self.comb`).
* **NextState("NAME")**: Schedules a transition to the designated state on the next clock edge.
* **NextValue(target, value)**: Schedules a synchronous register update on the next clock edge only when executing from that specific state.
* **fsm.ongoing("NAME")**: Returns a 1-bit `Signal` that evaluates to `1` whenever the FSM is currently in the specified state.
* **fsm.before_entering("NAME") / after_entering("NAME")**: Edge-detection pulse signals triggered immediately before or after entering a state.

```python
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
```