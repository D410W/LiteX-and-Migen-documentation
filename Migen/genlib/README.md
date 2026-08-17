# migen.genlib

`migen.genlib` is Migen's standard component library. It provides reusable, parameterized hardware cores to avoid rewriting common digital design primitives from scratch.

## Core Modules

| Module | Primary Classes | Description |
| :--- | :--- | :--- |
| **fifo** | `SyncFIFO`, `AsyncFIFO`, `AsyncFIFOBuffered` | First-In-First-Out queues for data buffering across single or dual clock domains. |
| **fsm** | `FSM`, `NextState`, `NextValue` | Declarative Finite State Machine builder that abstracts state encodings and transitions. |
| **cdc** | `MultiReg`, `PulseSynchronizer`, `GrayCounter` | Clock Domain Crossing primitives to safely transfer signals and pulses between clock domains without metastability. |
| **record** | `Record` | Bundles multiple named `Signal` objects into structured hardware interfaces and bus protocols. |
| **resetsync** | `AsyncResetSynchronizer` | Asynchronously asserts and synchronously de-asserts resets to prevent timing violations during reset release. |
| **coding** | `Encoder`, `Decoder`, `PriorityEncoder` | Converts one-hot/active lines to binary values and vice versa. |
| **roundrobin** | `RoundRobin` | Fair-access arbiter with priority rotation among multiple requesting channels. |
| **divider** | `Divider` | Iterative multi-cycle integer division hardware with `start` and `ready` handshaking. |
| **misc** | `WaitTimer`, `BitSlip` | General utility blocks: low-level bit manipulation helpers, timing/sequencing utilities, and data alignment primitives. |
| **sort** | `BitonicSort` | Hardware sorting networks generated via recursive parallel comparator trees. |

---

## Quick Example: FSM with `genlib.fsm`

```Python
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
```