from migen import *

def to_unsigned(val, bits):
  """Encodes a signed integer into an unsigned two's complement bitfield."""
  return val & ((1 << bits) - 1)


def to_signed(val, bits):
  """Decodes an unsigned two's complement bitfield into a signed integer."""
  if val & (1 << (bits - 1)):
      return val - (1 << bits)
  return val


def light_inf_testbench(dut, width, vector_size, elements):
  lane_width  = width // vector_size

  # 1. Downstream consumer (DMA writer) is ready
  yield dut.source.ready.eq(1)

  # 2. Slice test vectors into vector_size chunks: [1, -2], [3, -4], [5, -6]
  chunks = [elements[i:i + vector_size] for i in range(0, len(elements), vector_size)]

  for chunk in chunks:
    # Pack SIMD lanes into a single data word (LSB to MSB)
    packed_in = 0
    expected = []
    for i, val in enumerate(chunk):
      packed_in |= to_unsigned(val, lane_width) << (i * lane_width)
      expected.append(max(0, val))

    # Drive the input stream
    yield dut.sink.data.eq(packed_in)
    yield dut.sink.valid.eq(1)
    yield

    # Sample output from combinational stream
    out_packed = (yield dut.source.data)
    out_valid  = (yield dut.source.valid)

    # Unpack output lanes and decode signed integers
    actual = []
    for i in range(vector_size):
      raw = (out_packed >> (i * lane_width)) & ((1 << lane_width) - 1)
      actual.append(to_signed(raw, lane_width))

    print(f"Input: {chunk} -> Expected: {expected} | Actual: {actual}")

    assert out_valid == 1, "Expected source.valid to be asserted"
    for exp, act in zip(expected, actual):
      assert act == exp, f"Mismatch: expected {exp}, got {act}"

  # Deassert stream
  yield dut.sink.valid.eq(0)
  yield