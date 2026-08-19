from migen.sim import run_simulation

def testbench(dut):
  # Feed 100 continuous sample values
  for i in range(100):
    yield dut.sample_in.eq(i + 1)
    if i == 20:
      yield dut.trigger.eq(1)
    else:
      yield dut.trigger.eq(0)
    yield

  # Wait until buffer halts
  while not (yield dut.halted):
    yield

  final_addr = (yield dut.halt_address)
  print(f"Capture halted at address: {final_addr}")
  print("Exercise 2 Passed!")

if __name__ == "__main__":
  dut = TraceBuffer(depth=256, sample_width=16, post_trigger_cycles=10)
  run_simulation(dut, testbench(dut))