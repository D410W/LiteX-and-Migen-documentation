# migen.fhdl.specials

Migen's 'specials' term usually refers to hardware that cannot be modeled as standard logic gates. It is frequently used to communicate with the FPGA architecture and components.

Some examples of 'specials' are:

- Memory - Interacts directly with the synthesis tool (Vivado, Quartus, etc.) to communicate direclty with dedicated BRAM instead of flip-flops;

- Instance - Describes a module 'unknown' to Migen. This is used to link Migen designs with external verilog/vhdl code;

- Tristate - Maps to an IOBUF (Input/Output Buffer) at the physical pad level, allowing a single board pin to act as both an input and an output.

Usage example:

```Python
from migen import *
from migen.fhdl.specials import Tristate

class SpecialsExample(Module):
  def __init__(self):

    # - Memory (Infers Block RAM on FPGAs)
    # 1024 entries, 32 bits wide
    self.specials.ram = Memory(width=32, depth=1024)
    
    # Generate a port (supports write capabilities and address/data signals)
    self.specials.ram_port = self.ram.get_port(write_capable=True)

    # Connect signals to the RAM port combinatorially
    self.comb += [
      self.ram_port.adr.eq(0x0F),         # Read/Write address
      self.ram_port.dat_w.eq(0xDEADBEEF), # Data to write
      self.ram_port.we.eq(1)              # Write Enable
    ]


    # - Tristate (Bidirectional Pin Control)
    self.external_pin = Signal() # Physical IO pin bound in build system
    self.data_in      = Signal() # Read value
    self.data_out     = Signal() # Value to drive
    self.oe           = Signal() # Output Enable flag

    self.specials += Tristate(
      target=self.external_pin,
      o=self.data_out,
      oe=self.oe,
      i=self.data_in
    )

    # - Instance (Black-Box External Verilog Core)
    clk = ClockSignal() # Gets the default system clock
    a   = Signal(16)
    b   = Signal(16)
    res = Signal(32)

    # Instantiates an external Verilog module named "fast_multiplier"
    self.specials += Instance("fast_multiplier",
      # Verilog Parameters or Generics (p_NAME)
      p_WIDTH=16,

      # Inputs (i_PORTNAME)
      i_clk=clk,
      i_a_in=a,
      i_b_in=b,

      # Outputs (o_PORTNAME)
      o_result=res
    )

# We can't simulate with Migen's run_simulation since it doesn't support Instance nor Tristate.
# One solution is to export the design to Verilog and use an external simulator.
```