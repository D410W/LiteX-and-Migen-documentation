# fhdl (Core of the library)

FHDL: Fragmented Hardware Description Language

The repo's 'migen/fhdl' folder contains the Python description for FHDL, the low-level description language used by Migen to generate hardware.

Taking a look at this folder's most commonly used packages:

migen.fhdl.structure,\
migen.fhdl.module,\
migen.fhdl.specials,\
migen.fhdl.bitcontainer,\
migen.fhdl.decorators,\
migen.fhdl.simplify,

<!-- All of these are further explored in their respective folders. -->

## migen.fhdl.structure:

Has the basic components for building complex digital structures.

Some examples are:

Signal,\
Constant,\
ClockSignal,\
ResetSignal,\
If,\
Mux,\
Case,\
Array,

Each of these classes have their in-code description which explain their usage.

Examples:

```Python
from migen import *

class ClockAndResetExample(Module):
  def __init__(self):
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
```

# TODO: mux case and array examples

## migen.fhdl.module:

Modules in Migen are containers for hardware objects and circuits. Every single design involves subclassing 'Module' in order to be able to run.

self.comb += ... and self.sync += ... append operations that define the behavior of the hardware.\
Combinational hardware is re-evaluated when any of their entries changes, and Syncronous hardware is re-evaluated every clock cycle.

Usage example:

```Python
from migen import *

# Sub-module: Simple 8-bit Counter
class Counter(Module):
  def __init__(self, width=8):
    # Declare hardware signals
    self.count = Signal(width)
    self.enable = Signal()

    # Synchronous logic: evaluated on the rising edge of the default clock
    self.sync += [
      If(self.enable,
        self.count.eq(self.count + 1)
      )
    ]


# Parent Module: Uses the Counter submodule and multiple clock domains
class TopModuleExample(Module):
  def __init__(self):
    self.led = Signal()
    self.slow_signal = Signal()

    # - Registering Submodules
    # Migen needs 'self.submodules' registration to build the child hardware
    self.submodules.my_counter = Counter(width=8)

    # - Combinatorial Logic (self.comb)
    # Evaluates immediately whenever inputs change (like gates/wires)
    self.comb += [
      self.my_counter.enable.eq(1),             # Enable the counter continuously
      self.led.eq(self.my_counter.count > 128)  # Turn on LED when count > 128
    ]

    # - Synchronous Logic in a Named Clock Domain (self.sync.<domain>)
    # Runs on the 'pix' (pixel clock) domain instead of default 'sys'
    self.sync.pix += [
      self.slow_signal.eq(~self.slow_signal)
    ]
```

## migen.fhdl.specials:

Usage example:

```Python
from migen import *
from migen.fhdl.specials import Tristate

class HardwarePrimitivesExample(Module):
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
      # Verilog Parameters (Generics)
      p_WIDTH=16,

      # Inputs (i_PORTNAME)
      i_clk=clk,
      i_a_in=a,
      i_b_in=b,

      # Outputs (o_PORTNAME)
      o_result=res
    )
```