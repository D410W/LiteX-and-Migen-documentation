from migen import *
from migen.genlib.misc import WaitTimer
from migen.fhdl.specials import Memory

class TraceBuffer(Module):
  def __init__(self, depth=256, sample_width=16, post_trigger_cycles=32):
    self.sample_in = Signal(sample_width)
    self.trigger = Signal()
    self.halted = Signal()
    self.halt_address = Signal(max=depth)

    # Internal Signals
    wr_ptr = Signal(max=depth)
    capturing_post = Signal()

    # BRAM Memory & Port
    self.specials.mem = Memory(width=sample_width, depth=depth)
    self.specials.wrport = self.mem.get_port(write_capable=True)

    # Timer for post-trigger capture
    self.submodules.timer = WaitTimer(post_trigger_cycles)

    self.comb += [
      self.wrport.adr.eq(wr_ptr),
      self.wrport.dat_w.eq(self.sample_in),
      self.wrport.we.eq(~self.halted),
      self.timer.wait.eq(capturing_post),
      self.halt_address.eq(wr_ptr)
    ]

    self.sync += [
      If(~self.halted,
        wr_ptr.eq(wr_ptr + 1),
        If(self.trigger & ~capturing_post,
          capturing_post.eq(1)
        ),
        If(self.timer.done,
          self.halted.eq(1),
          capturing_post.eq(0)
        )
      )
    ]