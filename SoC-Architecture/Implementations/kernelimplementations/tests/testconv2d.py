from migen import *

from .. import StreamConv2D

def conv2d_reference(elements, width, height, weights, kernel_size, bias=0):
  output = []

  for y in range(kernel_size - 1, height):
    for x in range(kernel_size - 1, width):
      acc = bias
      for r in range(kernel_size):
        for c in range(kernel_size):
          pix_idx = (y - (kernel_size - 1) + r) * width + (x - (kernel_size - 1) + c)
          weight_idx = r * kernel_size + c
          acc += elements[pix_idx] * weights[weight_idx]
      output.append(acc)
  return output

def conv2d_testbench(dut, test):
  elements    = test['elements']
  width       = test['width']
  height      = test['height']
  weights     = test['weights']
  bias        = test.get('bias', 0)
  kernel_size = test['kernel_size']

  yield dut.csr_width.storage.eq(width)
  yield dut.csr_height.storage.eq(height)
  yield dut.csr_bias.storage.eq(bias)
  for i, w in enumerate(weights):
    yield dut.csr_weights[i].storage.eq(w)

  yield dut.source.ready.eq(1)
  yield

  output = []
  expected = conv2d_reference(elements, width, height, weights, kernel_size, bias)

  for element in elements:
    print(f'Input: {element}')
    yield dut.sink.data.eq(element)
    yield dut.sink.valid.eq(1)
    yield

    while not (yield dut.sink.ready):
      yield

    if (yield dut.source.valid):
      raw_out = (yield dut.source.data)
      output.append(raw_out)
      print(f"Output: Expected: {expected[len(output)-1]} | Actual: {raw_out}")

  yield dut.sink.valid.eq(0)
  yield

  assert len(output) == len(expected), (
    f"Length mismatch: got {len(output)}, expected {len(expected)}"
  )
  for exp, act in zip(expected, output):
    assert act == exp, f"Mismatch: expected {exp}, got {act}"

def test_conv2d():
  print("Testing modules from 'conv2d'...")

  tests = [
    {
      'width': 4,
      'height': 4,
      'kernel_size': 2,
      'data_width': 8,
      'weight_width': 8,
      'bias': 0,
      'weights': [
          1, 0,
          0, 1,
      ],
      'elements': [
        10, 20, 30, 40,
        50, 60, 70, 80,
        90, 10, 20, 30,
        40, 50, 60, 70
      ],
      'testbench': conv2d_testbench,
    },
    {
      'width': 4,
      'height': 4,
      'kernel_size': 3,
      'data_width': 8,
      'weight_width': 8,
      'bias': 0,
      'weights': [
          0, 0, 0,
          0, 1, 0,
          0, 0, 0
      ],
      'elements': [
        10, 20, 30, 40,
        50, 60, 70, 80,
        90, 10, 20, 30,
        40, 50, 60, 70
      ],
      'testbench': conv2d_testbench,
    },
    {
      'width': 4,
      'height': 4,
      'kernel_size': 3,
      'data_width': 8,
      'weight_width': 8,
      'bias': 5,
      'weights': [
        -1, -2, -1,
        0,  0,  0,
        1,  2,  1
      ],
      'elements': list(range(1, 17)),
      'testbench': conv2d_testbench,
    }
  ]

  passed = 0
  print("Testing 'StreamConv2D'...")
  for idx, test in enumerate(tests):
    print(f"[TEST {idx+1}]")
    dut = StreamConv2D(
      data_width=test['data_width'],
      weight_width=test['weight_width'],
      kernel_size=test['kernel_size'],
      max_width=64,
      max_height=64
    )

    try:
      run_simulation(dut, test['testbench'](dut, test))
      print("[PASS]")
      passed += 1
    except AssertionError as e:
      print(f"[FAIL] {e}")

  print(f"Finished testing 'StreamConv2D': {passed} out of {len(tests)} tests passed.")