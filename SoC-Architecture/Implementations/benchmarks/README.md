This folder's purpose is to generate resource consumption data (LUTs, max frequency, etc) for each of the implemented accelerator modules.

```bash
# In 'Implementations/' or '..'
python benchmark.py

cd benchmarks/

./yosys_report.sh
./pnr_report.sh
python join_reports.py

# Output in 'full_report.md'
```