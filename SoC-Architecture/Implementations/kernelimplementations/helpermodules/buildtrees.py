from migen import *

def build_tree(operands, operation):
  current_level = operands
  while len(current_level) > 1:
    next_level = []
    for i in range(0, len(current_level), 2):
      if i + 1 < len(current_level):
        next_level.append(operation(current_level[i], current_level[i + 1]))
      else: # odd element
        next_level.append(current_level[i])
    current_level = next_level
  return current_level[0]

def signed_max(a, b):
  return Mux(a > b, a, b)

def build_max_tree(operands):
  return build_tree(operands, signed_max)

def signed_sum(a, b):
  return a + b

def build_sum_tree(operands):
  return build_tree(operands, signed_sum)
