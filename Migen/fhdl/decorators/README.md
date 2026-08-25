# decorators

This module provides high-level function/class decorators that allow you to dynamically transform a module's behavior from the outside
without having to edit the module's internal Python code.

```Python 
@CEInserter({"sys": ce_signal})
```

- Wraps all synchronous logic (self.sync) inside an If(ce_signal, ...) check, adding a Clock Enable line to the entire module.

```Python
@ResetInserter({"sys": rst_signal})
```

- Forces an additional Reset signal onto all synchronous logic in the module.

```Python
@ClockDomainRenamer("domain_name")
```

- Re-routes all synchronous statements in a module from the default "sys" domain to a specified clock domain (e.g., "pix" or "eth").

Examples:

```Python
from migen import *
from migen.fhdl.decorators import CEInserter, ResetInserter, ClockDomainsRenamer

# Standard module, always counts on every clock cycle.
class BasicCounter(Module):
    def __init__(self):
        self.count = Signal(8)
        self.sync += self.count.eq(self.count + 1)

enable_wire = Signal()
rst_signal = Signal()

# The counter now only increments when enable_wire == 1
GatedCounter = CEInserter({"sys": enable_wire})(BasicCounter)

ResettableCounter = ResetInserter({"sys": rst_signal})(BasicCounter)

PixelCounter = ClockDomainsRenamer("pix")(BasicCounter)
# Can also be used in the format {old: new}:
# PixelCounter = ClockDomainsRenamer({"sys": "pix"})(BasicCounter)

# Instantiating the newly transformed modules
dut1 = GatedCounter()
dut1 = ResettableCounter()
dut1 = PixelCounter()
```