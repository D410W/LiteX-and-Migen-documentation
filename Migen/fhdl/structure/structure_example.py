from migen import *

class StructureExample(Module):
  def __init__(self, platform): # Asking for a platform in order to get the custom clock domain.

    # - Signal
    # Represents hardware wires or registers (vectors of bits).
    self.counter = Signal(8, reset=0)       # 8-bit register, initial reset value = 0
    self.is_limit = Signal()                # 1-bit signal (default width is 1)
    self.clk_monitor = Signal()             # Signal to output clock state
    self.rst_monitor = Signal()             # Signal to output reset state

    # - Constant
    # Represents fixed bitvector values in hardware.
    # Syntax: Constant(value, width) or Constant(value, (width, signed))
    LIMIT = Constant(100, 8)                # 8-bit constant with value 100
    ZERO  = Constant(0, 8)                  # 8-bit constant with value 0

    # - ClockSignal & ResetSignal
    # Request the implicit clock and reset lines for a given domain ('sys' is default).
    current_clk = ClockSignal("sys")        # Wire representing the 'sys' clock
    current_rst = ResetSignal("sys")        # Wire representing the 'sys' reset

    # --- Combinatorial Logic (self.comb) ---
    self.comb += [
      # Compare a dynamic Signal against a Constant
      self.is_limit.eq(self.counter == LIMIT),

      # Set output signals directly from ClockSignal and ResetSignal
      self.clk_monitor.eq(current_clk),
      self.rst_monitor.eq(current_rst)
    ]

    # --- Synchronous Logic (self.sync) ---
    self.sync += [
      If(self.counter == LIMIT,
        self.counter.eq(ZERO)
      ).Else(
        self.counter.eq(self.counter + 1)
      )
    ]

    # - ClockDomain
    pixel_clock_from_pll = platform.request("clk50")   #
    system_reset_button = platform.request("key", 0)   # example pins

    # Creating a custom clock domain named "video"
    pix_domain = ClockDomain("video", reset_less=False)

    # Registering the domain in the module
    self.clock_domains += pix_domain

    # Connecting physical wires to the domain controls
    self.comb += [
        pix_domain.clk.eq(pixel_clock_from_pll),
        pix_domain.rst.eq(system_reset_button)
    ]

    h_sync = Signal(8)

    # Targeting the domain in synchronous logic
    self.sync.video += [
        h_sync.eq(h_sync + 1)
    ]

# Getting a specific platform
from migen.build.platforms import de0nano

StructureExample(de0nano.Platform())