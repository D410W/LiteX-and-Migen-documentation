from migen import *
from .. import StreamReLU

def to_unsigned(val, bits):
  """
  Encodes a signed integer into an unsigned two's complement bitfield.
  """
  return val & ((1 << bits) - 1)


def to_signed(val, bits):
  """
  Decodes an unsigned two's complement bitfield into a signed integer.
  """
  if val & (1 << (bits - 1)):
      return val - (1 << bits)
  return val


def light_inf_testbench(dut, width, vector_size, elements):
  lane_width  = width // vector_size

  yield dut.source.ready.eq(1)

  # slicing test vectors into vector_size chunks. ex: [1, -2], [3, -4], [5, -6]
  chunks = [elements[i:i + vector_size] for i in range(0, len(elements), vector_size)]

  for chunk in chunks:
    # packing vector elements into a single data word (LSB to MSB)
    packed_in = 0
    expected = []
    for i, val in enumerate(chunk):
      packed_in |= to_unsigned(val, lane_width) << (i * lane_width)
      expected.append(max(0, val))

    # Input stream
    yield dut.sink.data.eq(packed_in)
    yield dut.sink.valid.eq(1)
    yield

    # Sampling output from combinational stream
    out_packed = (yield dut.source.data)
    out_valid  = (yield dut.source.valid)

    # Unpacking output lanes and decode signed integers
    actual = []
    for i in range(vector_size):
      raw = (out_packed >> (i * lane_width)) & ((1 << lane_width) - 1)
      actual.append(to_signed(raw, lane_width))

    print(f"Input: {chunk} -> Expected: {expected} | Actual: {actual}")

    assert out_valid == 1, "Expected source.valid to be asserted"
    for exp, act in zip(expected, actual):
      assert act == exp, f"Mismatch: expected {exp}, got {act}"

  # Disabling stream
  yield dut.sink.valid.eq(0)
  yield

def test_ligh_inference():
  print("Testing modules from 'light_inference'...")

  tests = [
    {
      'data_width': 32,
      'vector_size': 2,
      'elements': [1, -2, 3, -4, 5, -6],
      'testbench': light_inf_testbench,
    },
    {
      'data_width': 32,
      'vector_size': 2,
      'elements': [131, -132, -133, -134, 245, 566],
      'testbench': light_inf_testbench,
    },
  ]

  passed = 0

  print("Testing 'StreamReLU'...")
  for idx, test in enumerate(tests):
    print(f'[TEST {idx+1}]')

    dut = StreamReLU(data_width=test['data_width'], vector_size=test['vector_size'])

    try:
      run_simulation(
        dut,
        test['testbench'](
          dut, 
          test['data_width'], 
          test['vector_size'], 
          test['elements']
        )
      )
      print(f"[PASS]")
      passed += 1
    except AssertionError as e:
      print(f"[FAIL] {e}")

  print(f"Finished testing 'StreamReLU, {passed} out of {len(tests)} tests passed.")
