#!/bin/bash

top_entities=("StreamConv2D" "StreamConvFusionLayer" "StreamMaxPooling" "StreamReLU" "StreamSymDyQuantizer")

for top_entity in "${top_entities[@]}"; do
  nextpnr-ecp5 --json "${top_entity}_ecp5.json" \
               --25k --package CABGA381 \
               --freq 100 \
               --textcfg /dev/null \
               --log "pnr_report_${top_entity}_ecp5.txt"
done