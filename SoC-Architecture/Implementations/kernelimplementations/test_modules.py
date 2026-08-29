from migen import *
import argparse

from .streaminterfaces import *
from .tests.testlightinf import test_ligh_inference
from .tests.testpooling import test_pooling
from .tests.testquantizer import test_quantizer
from .tests.testconv2d import test_conv2d


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

  if test_all or modules_to_test['pooling']:
    test_pooling()

  if test_all or modules_to_test['quantizer']:
    test_quantizer()

  if test_all or modules_to_test['conv_2d']:
    test_conv2d()

if __name__ == '__main__':
  main()