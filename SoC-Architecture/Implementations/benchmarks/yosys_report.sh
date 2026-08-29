#!/bin/bash

verilogs=("conv2d" "convfusionlayer" "maxpooling" "relu" "symdyquantizer")
top_entities=("StreamConv2D" "StreamConvFusionLayer" "StreamMaxPooling" "StreamReLU" "StreamSymDyQuantizer")
families=("synth_xilinx" "synth_ecp5" "synth_ice40")

for i in "${!verilogs[@]}"; do
  verilog="${verilogs[i]}.v"
  top_entity="${top_entities[i]}"

  yosys -p "read_verilog ${verilog}; synth_ecp5 -top top_module; write_json ${top_entity}_ecp5.json"
  for family in "${families[@]}"; do
    yosys -p "read_verilog ${verilog}; ${family} -top top_module; stat" > "report_${top_entity}_${family}.txt"
  done
done