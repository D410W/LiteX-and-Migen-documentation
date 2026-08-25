import argparse
from migen import Memory
from litex.build.sim.config import SimConfig
from litex.soc.integration.builder import Builder

from soc import AcceleratorSoC

def main():
  parser = argparse.ArgumentParser(description="Minimal LiteX SoC example")
  parser.add_argument("--output-dir", default="build")
  
  parser.add_argument("--kernel", default=None,
    help="Bare-metal firmware image to load via serialboot")
  
  parser.add_argument("--kernel-adr", default="0x40000000")

  parser.add_argument("--no-build", action="store_true",
    help="Construct the SoC and stop before running the builder")
  
  args = parser.parse_args()

  soc = AcceleratorSoC(
    kernel=args.kernel,
    kernel_adr=args.kernel_adr
  )
  
  if args.no_build:
    print(f"SoC constructed successfully. Output dir would be: {args.output_dir}")
    return

  sim_config = SimConfig()
  sim_config.add_clocker("sys_clk", freq_hz=int(1e6))
  sim_config.add_module("serial2console", "serial")

  builder = Builder(soc, output_dir=args.output_dir)
  builder.build(sim_config=sim_config, interactive=False, run=True)

if __name__ == "__main__":
  main()