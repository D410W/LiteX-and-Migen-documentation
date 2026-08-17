# bitcontainer

This module contains 3 helper functions that make 'bandwidth' calculation between signals easier.

For example, if you have some signal(s) with defined width in bits, and want to make the rest of the design automatically
adjust while correctly holding values without width mismatches, or want to fit the maximum possible value your design is intended to process:

```Python
from migen import *
from migen.fhdl.bitcontainer import *

w1 = bits_for(255) # Returns 8 bits
w2 = bits_for(256) # Returns 9 bits
w3 = bits_for(256, require_sign_bit=True) # Returns 10 bits

a = Signal(8)
b = Signal(8)

product_shape = value_bits_sign(a * b)
print(product_shape[0])  # Output: 16
print(product_shape[1])  # Output: False
```