from migen import *
from migen.genlib.misc import split, chooser
from migen.genlib.coding import PriorityEncoder

class HeaderParser(Module):
  def __init__(self):
    # Inputs
    self.raw_packet = Signal(32)
    self.byte_sel = Signal(2)

    # Outputs
    self.valid = Signal()
    self.prio = Signal(3)
    self.flags = Signal(4)
    self.payload = Signal(24)
    
    self.highest_flag_idx = Signal(2)
    self.flags_empty = Signal()
    self.selected_byte = Signal(8)

    # - Split fields
    valid_s, prio_s, flags_s, payload_s = split(self.raw_packet, 1, 3, 4, 24)
    self.comb += [
      self.valid.eq(valid_s),
      self.prio.eq(prio_s),
      self.flags.eq(flags_s),
      self.payload.eq(payload_s),
    ]

    # - Priority Encoder for flags
    self.submodules.penc = PriorityEncoder(width=4)
    self.comb += [
      self.penc.i.eq(self.flags),
      self.highest_flag_idx.eq(self.penc.o),
      self.flags_empty.eq(self.penc.n)
    ]

    # - Dynamic byte extractor from 24-bit payload
    self.comb += chooser(signal=self.payload, shift=self.byte_sel, output=self.selected_byte)