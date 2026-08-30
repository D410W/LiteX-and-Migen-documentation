from migen import *
from migen.genlib.misc import split, chooser, WaitTimer, timeline

class MiscDemo(Module):
  def __init__(self):
    # - Bus splitting helper (e.g. 32-bit word -> byte0, word16, byte3)
    bus = Signal(32)
    b0, w1, b3 = split(bus, 8, 16, 8)  # b0: 8-bit, w1: 16-bit, b3: 8-bit

    # - Dynamic sub-word chooser (Mux 4-byte bus to 1-byte output)
    byte_out = Signal(8)
    byte_sel = Signal(2)
    self.comb += chooser(signal=bus, shift=byte_sel, output=byte_out)

    # - Wait timer (counts down 100 cycles)
    self.submodules.timer = WaitTimer(t=100)
    # self.timer.wait : Assert 1 to count down, 0 to reset counter
    # self.timer.done : Asserts 1 when counter reaches 0

    # - Cycle-accurate timeline sequencer
    start_pulse = Signal()
    led = Signal()
    pulse_out = Signal()

    # Schedule synchronous actions at specific cycle delays after start_pulse
    self.sync += timeline(start_pulse, [
      (0,  [led.eq(1)]),            # Cycle 0: Turn LED on immediately
      (10, [pulse_out.eq(1)]),      # Cycle 10: Assert pulse_out
      (11, [pulse_out.eq(0)]),      # Cycle 11: De-assert pulse_out
      (50, [led.eq(0)])             # Cycle 50: Turn LED off
    ])

dut = MiscDemo()