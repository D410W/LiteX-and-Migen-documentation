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