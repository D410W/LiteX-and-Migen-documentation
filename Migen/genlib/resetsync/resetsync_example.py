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

from migen.build.platforms import de0nano

dut = SafeClockDomain(de0nano.Platform())