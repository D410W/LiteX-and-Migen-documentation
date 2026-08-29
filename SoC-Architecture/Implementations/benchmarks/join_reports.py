modules = ["StreamConv2D", "StreamConvFusionLayer", "StreamMaxPooling", "StreamReLU", "StreamSymDyQuantizer"]
families = ["synth_xilinx", "synth_ecp5", "synth_ice40"]

total_report = ''

for module in modules:
  combined = f'## Report for module \'{module}\'\n\n'

  for family in families[1:3]:
    pnr_filename = f'pnr_report_{module}_{family.removeprefix('synth_')}.txt'
    with open(pnr_filename) as pnr_file:
      print(pnr_filename)
      pnr_report = pnr_file.read()

      report_lines = pnr_report.split('\n')
      frequency_lines = [line for line in report_lines if line.find("Max frequency for clock") != -1]

      if len(frequency_lines) > 0:
        frequency_report = frequency_lines[-1]
        frequency_report = "\n\n```\n" + frequency_report + "\n```\n\n"

        combined += f"### Frequency report from 'nextpnr-{family.removeprefix('synth_')}'"
        combined += frequency_report

  for family in families:
    filename = f'report_{module}_{family}.txt'
    with open(filename) as file:
      content = file.read()

      upper = '3. Printing statistics.'
      lower = 'Warnings'

      top_module = content.split(upper, 1)[1].split(lower, 1)[0]
      top_module = top_module[3:-2]
      top_module = "\n\n```\n" + top_module + "\n```\n\n"

      combined += f'### Synthesis of \'{module}\' for family \'{family.removeprefix('synth_')}\''
      combined += top_module

  total_report += combined + '\n'

with open("full_report.md", "w", encoding="utf-8") as file:
  file.write(total_report)