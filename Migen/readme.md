# Migen

Migen is a Python library for describing and simulating complex digital hardware. It is used by LiteX to describe it's digital logic.\
More information can be found in the [official Migen website](https://m-labs.hk/misc/migen/) and in the [Migen repository](https://git.m-labs.hk/M-Labs/migen).

This documentation will be split into Migen's modules:

fhdl          <-- Description of the DSL used to actually describe hardware.\
sim           <-- Simulation of digital hardware.\
genlib        <-- Component library given by Migen.\
build         <-- Translates Migen designs into hardware platforms (FGPA).\
interconnect  <-- Implementations of standard bus protocols.
