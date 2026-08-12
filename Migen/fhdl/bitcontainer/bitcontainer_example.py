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