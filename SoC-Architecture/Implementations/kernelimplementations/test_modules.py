from migen import *
import argparse

from .dma_nterfaces import *
from .tests.testlightinf import light_inf_testbench

def test_ligh_inference():
  print("Testing modules from 'light_inference'...")

  tests = [
    {
      'width': 32,
      'vector_size': 2,
      'elements': [1, -2, 3, -4, 5, -6],
      'testbench': light_inf_testbench,
    },
    {
      'width': 32,
      'vector_size': 2,
      'elements': [131, -132, -133, -134, 245, 566],
      'testbench': light_inf_testbench,
    },

  ]

  passed = 0

  print("Testing 'StreamReLU'...")
  for idx, test in enumerate(tests):
    print(f'[TEST {idx+1}]')

    dut = StreamReLU(width=test['width'], vector_size=test['vector_size'])

    try:
      run_simulation(
        dut,
        test['testbench'](
          dut, 
          test['width'], 
          test['vector_size'], 
          test['elements']
        )
      )
      print(f"[PASS]")
      passed += 1
    except AssertionError as e:
      print(f"[FAIL] {e}")

  print(f"Finished testing 'StreamReLU, {passed} out of {len(tests)} tests passed.")

def main():
  parser = argparse.ArgumentParser(description="Accelerator modules tester and correctude validator")

  module_categories = [
    'conv_2d',
    'light_inference',
    'quantizer',
    'pooling',
  ]

  for category in module_categories:
    parser.add_argument(f'--{category}', action='store_true',
      help=f"Test only '{category}' category of modules")
  
  args = parser.parse_args()

  modules_to_test = {category: getattr(args, category) for category in module_categories}

  test_all = not any(modules_to_test.values())

  if test_all or modules_to_test['light_inference']:
    test_ligh_inference()

if __name__ == '__main__':
  main()