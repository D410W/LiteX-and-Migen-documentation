from migen import *

from litex.build.generic_platform import *
from litex.build.io import CRG
from litex.build.sim import SimPlatform
from litex.soc.interconnect import wishbone
from litex.soc.integration.soc import SoCCore, SoCRegion
from litex.soc.integration.soc_core import *

from kernel_implementations import ReLU


class Platform(SimPlatform):
  def __init__(self):
    # The simulator UART bridge expects a serial interface.
    io = [
      ("sys_clk", 0, Pins(1)),
      ("sys_rst", 0, Pins(1)),
      ("serial", 0,
        Subsignal("source_valid", Pins(1)),
        Subsignal("source_ready", Pins(1)),
        Subsignal("source_data",  Pins(8)),
        Subsignal("sink_valid",   Pins(1)),
        Subsignal("sink_ready",   Pins(1)),
        Subsignal("sink_data",    Pins(8)),
      ),
    ]
    SimPlatform.__init__(self, "SIM", io)


class AcceleratorSoC(SoCCore):
  def __init__(self, kernel=None, kernel_adr=0x40000000):
    # A very small SoC with integrated SRAM and UART.
    platform = Platform()
    sys_clk_freq = int(1e6)

    SoCCore.__init__(self, platform, clk_freq=sys_clk_freq,
      cpu_type="vexriscv",
      cpu_variant="minimal",
      ident="Minimal LiteX SoC",
      with_uart=True,
      uart_name="sim",
      integrated_rom_size=0x0,
      integrated_sram_size=0x2000,
      integrated_main_ram_size=0x2000,

      integrated_main_ram_init=get_mem_data(
        filename_or_regions=kernel,
        data_width=32,
        endianness="little",
      ),
      cpu_reset_address=int(str(kernel_adr), 0),
    )
    self.submodules.crg = CRG(platform.request("sys_clk"))

    # Memory with 1024 words, 32-bit width
    depth = 1024
    shared_mem = Memory(width=32, depth=depth)
    accel_port = shared_mem.get_port(write_capable=True)

    self.specials += shared_mem, accel_port

    # Create wishbone SRAM interface (CPU Port) and map to address space
    self.submodules.shared_ram = wishbone.SRAM(
      mem_or_size=shared_mem,
      bus=wishbone.Interface(data_width=32),
      read_only=False
    )
    self.bus.add_slave(
      name="shared_ram",
      slave=self.shared_ram.bus,
      region=SoCRegion(origin=0x80000000, size=depth * 4, cached=False)
    )

    # Connecting the accelerator modules
    self.relu = ReLU(width=32)
