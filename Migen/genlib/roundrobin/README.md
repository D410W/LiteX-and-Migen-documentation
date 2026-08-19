# roundrobin

This module provides a fair round-robin arbiter (`RoundRobin`) to share a common resource among N requesting channels, guaranteeing that no channel is starved.

Key parameters, signals, and policies:
* **`n`**: Number of requesting channels.
* **`request`**: Input `Signal(n)` where bit `i` represents an active request from master `i`.
* **`grant`**: Output `Signal(max=n)` indicating the binary index of the currently granted master.
* **Switch Policies (`switch_policy`):**
* **`SP_WITHDRAW` (default):** The active master retains the grant until it lowers its `request` bit (`~request[grant]`), at which point the arbiter grants the next requesting master in circular order.
* **`SP_CE`:** Arbitration evaluation occurs only when the clock enable signal `ce` is asserted, allowing external controllers to trigger priority rotation explicitly (e.g., after a packet transfer completes).

```python
from migen import *
from migen.genlib.roundrobin import RoundRobin, SP_WITHDRAW, SP_CE

class ArbiterDemo(Module):
  def __init__(self):
    # 4 requesting masters
    self.requests = Signal(4)
    self.grant_index = Signal(2)

    # - Standard Round-Robin (Master keeps grant until request drops)
    self.submodules.arbiter = arbiter = RoundRobin(n=4, switch_policy=SP_WITHDRAW)
    self.comb += [
        arbiter.request.eq(self.requests),
        self.grant_index.eq(arbiter.grant)
    ]

    # - Clock-Enabled Round-Robin (Rotates on each cycle 'ce' is pulsed)
    self.submodules.arb_ce = arb_ce = RoundRobin(n=4, switch_policy=SP_CE)
    self.next_grant = Signal()
    self.comb += [
        arb_ce.request.eq(self.requests),
        arb_ce.ce.eq(self.next_grant)
    ]

dut = ArbiterDemo()
```