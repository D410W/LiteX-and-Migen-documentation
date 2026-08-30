#!/bin/bash

top_entities=("StreamConv2D" "StreamConvFusionLayer" "StreamMaxPooling" "StreamReLU" "StreamSymDyQuantizer")

for top_entity in "${top_entities[@]}"; do
  echo "Running 'nextpnr-ecp5' with entity ${top_entity}"
  nextpnr-ecp5 --json "${top_entity}_ecp5.json" \
               --25k --package CABGA381 \
               --freq 50 \
               --textcfg /dev/null \
               --log "pnr_report_${top_entity}_ecp5.txt" &> /dev/null
  echo "Finished 'nextpnr-ecp5' with entity ${top_entity}. Program result: ${?}"
done

for top_entity in "${top_entities[@]}"; do
  echo "Running 'nextpnr-ice40' with entity ${top_entity}."
  nextpnr-ice40 --json "${top_entity}_ice40.json" \
                --hx8k \
                --package ct256 \
                --freq 50 \
                --asc /dev/null \
                --log "pnr_report_${top_entity}_ice40.txt" &> /dev/null
  echo "Program result: ${?}"
done