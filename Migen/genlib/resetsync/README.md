# resetsync

This module provides the `AsyncResetSynchronizer` hardware primitive, which protects clock domains against reset metastability and timing violations during reset recovery and removal.

It implements an **Asynchronous Assert, Synchronous De-assert** strategy:
* **Immediate Reset (Asynchronous):** When `async_reset` goes high, the target `ClockDomain` enters reset immediately without waiting for a clock edge.
* **Safe Release (Synchronous):** When `async_reset` goes low, the reset signal is de-asserted synchronously through a 2-stage flip-flop chain clocked by the target domain, preventing flip-flops from entering metastable states.

Key properties:
* **Target:** Connects directly to a `ClockDomain` object (`cd`) and an active-high reset source (`async_reset`).
* **Registration:** Because it represents a specialized hardware primitive lowered by platform backends, it must be added to `self.specials`.

```python
from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

class SafeClockDomain(Module):
  def __init__(self, platform):
    # - Physical clock and reset button inputs from platform
    raw_clk = platform.request("clk50")
    rst_btn = platform.request("key", 0)

    # - Declare a custom clock domain
    self.clock_domains.cd_sys = cd_sys = ClockDomain("sys")

    # Drive clock wire directly
    self.comb += cd_sys.clk.eq(raw_clk)

    # - Synchronize the raw button reset into the "sys" domain
    self.specials += AsyncResetSynchronizer(cd_sys, rst_btn)

# Example platform
from migen.build.platforms import de0nano

dut = SafeClockDomain(de0nano.Platform())
```