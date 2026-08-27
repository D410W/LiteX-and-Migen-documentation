from migen import *
from .. import StreamMaxPooling

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

def get_max_pool(elements, width, height, kernel_size):
  kwidth = width // kernel_size
  kheight = height // kernel_size

  output = []

  for y in range(kheight):
    for x in range(kwidth):
      max = elements[(y * kernel_size * width) + x * kernel_size]

      for j in range(kernel_size):
        for i in range(kernel_size):
          element = elements[((y * kernel_size + j) * width) + x * kernel_size + i]
          if element > max:
            max = element

      output.append(max)

  return output

def pooling_testbench(dut, test):
  elements = test['elements']
  data_width = test['data_width']

  yield dut.csr_width.storage.eq(test['width'])
  yield dut.csr_height.storage.eq(test['height'])
  yield dut.source.ready.eq(1)

  output = []
  expected = get_max_pool(elements, test['width'], test['height'], test['kernel_size'])

  for element in elements:
    # packing element into a data word (LSB to MSB)
    packet_in = to_unsigned(element, data_width)

    # Input stream
    yield dut.sink.data.eq(packet_in)
    yield dut.sink.valid.eq(1)

    print(f'Input: {element}')

    yield

    out_packet = (yield dut.source.data)
    out_valid  = (yield dut.source.valid)

    actual = to_signed(out_packet, data_width)

    if out_valid == 1:
      output.append(actual)
      print(f"Output: Expected: {expected[len(output)-1]} | Actual: {actual}")

  assert len(output) == len(expected), "Amount of expected output elements differ"
  for exp, act in zip(expected, output):
    print('Data out: ', output)
    assert act == exp, f"Mismatch: expected {exp}, got {act}"

  # Disabling stream
  yield dut.sink.valid.eq(0)
  yield

def test_pooling():
  print("Testing modules from 'pooling'...")

  tests = [
    {
      'data_width': 32,
      'elements': [1, -2, 3, -4],
      'width': 2,
      'height': 2,
      'kernel_size': 2,
      'testbench': pooling_testbench,
    },
    {
      'data_width': 32,
      'elements': [131, -132, -133, -134, 245, 566, 1, 2],
      'width': 4,
      'height': 2,
      'kernel_size': 2,
      'testbench': pooling_testbench,
    },
    {
      'data_width': 32,
      'elements': [131, -132, -133, -134, 245, 566, 1, 2],
      'width': 2,
      'height': 4,
      'kernel_size': 2,
      'testbench': pooling_testbench,
    },
  ]

  passed = 0

  print("Testing 'MaxPooling'...")
  for idx, test in enumerate(tests):
    print(f'[TEST {idx+1}]')

    dut = StreamMaxPooling(data_width=test['data_width'], kernel_size=test['kernel_size'], signed=True)

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

  print(f"Finished testing 'StreamReLU, {passed} out of {len(tests)} tests passed.")