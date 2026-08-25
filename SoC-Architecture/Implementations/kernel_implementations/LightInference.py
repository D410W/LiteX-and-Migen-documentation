from migen import *

# Works with IEEE 754 floats as well

class ReLU(Module):
  def __init__(self, width=8):
    self.i = Signal((width, True))
    self.o = Signal((width, True))

    self.comb += [
      If(self.i[-1],
        self.o.eq(0)
      ).Else(
        self.o.eq(self.i)
      )
    ]

class ReLUVector(Module):
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