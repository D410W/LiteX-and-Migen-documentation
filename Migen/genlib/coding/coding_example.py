from migen import *
from migen.genlib.coding import Encoder, PriorityEncoder, Decoder

class CodingDemo(Module):
  def __init__(self):
    # - Strict One-Hot Encoder (8-bit one-hot -> 3-bit binary)
    self.submodules.enc = Encoder(width=8)
    # self.enc.i : One-hot input (e.g., 0b0000_0100)
    # self.enc.o : Binary output (e.g., 2)
    # self.enc.n : Asserts 1 if input is invalid (0 or >1 bits active)

    # - Priority Encoder (4-bit requests -> 2-bit binary index)
    self.requests = Signal(4)
    self.submodules.penc = PriorityEncoder(width=4)
    self.comb += [
        self.penc.i.eq(self.requests)
        # self.penc.o : Contains index of lowest active request bit (LSB priority)
        # self.penc.n : Asserts 1 if no requests are active (requests == 0)
    ]

    # - Binary to One-Hot Decoder (3-bit binary -> 8-bit one-hot enable mask)
    self.sel = Signal(3)
    self.submodules.dec = Decoder(width=8)
    self.comb += [
        self.dec.i.eq(self.sel)
        # self.dec.o : Drives only the bit (1 << sel) high
    ]

dut = CodingDemo()