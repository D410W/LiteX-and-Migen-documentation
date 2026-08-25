from migen import *
from litex.soc.interconnect.csr import AutoCSR, CSRStorage, CSRStatus

# Works with IEEE 754 floats as well

class ReLU(Module, AutoCSR):
  def __init__(self, width=8):
    # self.i = Signal((width, True))
    # self.o = Signal((width, True))

    self.i = CSRStorage(size=width, reset=0, description="ReLU signed input")
    self.o = CSRStatus(size=width, description="ReLU rectified output")

    self.comb += [
      If(self.i.storage[-1],
        self.o.status.eq(0)
      ).Else(
        self.o.status.eq(self.i.storage)
      )
    ]

class ReLUVector(Module, AutoCSR):
  def __init__(self, width=8, vec_size=4):
    self.i = [Signal(width, True) for idx in range(vec_size)]
    self.o = [Signal(width, True) for idx in range(vec_size)]

    for idx in range(vec_size):
      self.comb += [
        If(self.i[idx][-1],
          self.o[idx].eq(0)
        ).Else(
          self.o[idx].eq(self.i)
        )
      ]