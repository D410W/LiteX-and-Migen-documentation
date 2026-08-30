from migen.sim import run_simulation

def testbench(dut):
  # Packet layout:
  # valid=1 (1b) | prio=5 (3b) -> 0b101 | flags=0b0100 (4b) -> bit 2 active
  # payload = 0xAA_BB_CC (24b)
  # Binary: [payload: 24b][flags: 4b][prio: 3b][valid: 1b]
  # LSB -> 1 | (5 << 1) | (4 << 4) | (0xAABBCC << 8)
  packet_val = 1 | (5 << 1) | (4 << 4) | (0xAABBCC << 8)

  yield dut.raw_packet.eq(packet_val)
  yield dut.byte_sel.eq(1) # Should select 0xBB
  yield

  assert (yield dut.valid) == 1
  assert (yield dut.prio) == 5
  assert (yield dut.highest_flag_idx) == 2
  assert (yield dut.flags_empty) == 0
  assert (yield dut.selected_byte) == 0xBB
  print("Exercise 1 Passed!")

if __name__ == "__main__":
  dut = HeaderParser()
  run_simulation(dut, testbench(dut))