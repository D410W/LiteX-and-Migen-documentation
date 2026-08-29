from migen import *
from .. import StreamSymDyQuantizer


def quantizer_reference(elements, multiplier, shift, out_width):
  quant_min = -(1 << (out_width - 1))      # -128 for INT8
  quant_max =  (1 << (out_width - 1)) - 1  # +127 for INT8

  output = []

  for element in elements:
    prod = element * multiplier
    bias = (1 << (shift - 1)) if shift >= 1 else 0
    
    val = (prod + bias) >> shift

    # Saturation clamping
    if val > quant_max:
        output.append(quant_max)
    elif val < quant_min:
        output.append(quant_min)
    else:
      output.append(val)

  return output

def quantizer_testbench(dut, test):
  elements = test['elements']
  multiplier = test['multiplier']
  shift      = test['shift']
  in_width   = test['in_width']
  out_width  = test['out_width']

  yield dut.csr_mult.storage.eq(multiplier)
  yield dut.csr_shift.storage.eq(shift)
  yield dut.source.ready.eq(1)
  yield

  output = []
  expected = quantizer_reference(elements, multiplier, shift, out_width)

  for element in elements:
    print(f'Input: {element}')
    yield dut.sink.data.eq(element)
    yield dut.sink.valid.eq(1)
    yield

    # Wait for sink to be accepted if DUT stalls
    while not (yield dut.sink.ready):
      yield

    # If 0-cycle combinational datapath: sample source data
    if (yield dut.source.valid):
      raw_out = (yield dut.source.data)
      output.append(raw_out)
      print(f"Output: Expected: {expected[len(output)-1]} | Actual: {raw_out}")

  assert len(output) == len(expected), "Amount of expected output elements differ"
  for exp, act in zip(expected, output):
    assert act == exp, f"Mismatch: expected {exp}, got {act}"

  # Disabling stream
  yield dut.sink.valid.eq(0)
  yield

def test_quantizer():
  print("Testing modules from 'quantizer'...")

  tests = [
    {
      'in_width': 32,
      'out_width': 8,
      'elements': [1, -2, 3, -4, 500, -500, 0, -1],
      'multiplier': 10,
      'shift': 2,
      'testbench': quantizer_testbench,
    },
    {
      'in_width': 32,
      'out_width': 8,
      'elements': [10, -20, 30, -40],
      'multiplier': 1,
      'shift': 0,
      'testbench': quantizer_testbench,
    },
  ]

  passed = 0

  print("Testing 'StreamSymDyQuantizer'...")
  for idx, test in enumerate(tests):
    print(f'[TEST {idx+1}]')

    dut = StreamSymDyQuantizer(in_width=test['in_width'], out_width=test['out_width'], vector_size=1)

    try:
      run_simulation(
        dut,
        test['testbench'](
          dut,
          test
        )
      )
      print(f"[PASS]")
      passed += 1
    except AssertionError as e:
      print(f"[FAIL] {e}")

  print(f"Finished testing 'StreamSymDyQuantizer, {passed} out of {len(tests)} tests passed.")