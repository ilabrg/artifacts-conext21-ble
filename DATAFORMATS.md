# Description of used raw data formats
This document describes the data formats used to store the raw experiment data (`*.dump`-files in the `results/logs` subfolder) as well as the intermediate plot data (`*.json` in the `results/plots/` subfolder).

## Experiment raw data
The result of each experiment run is a single raw data file which located in `/results/logs/EXP_NAME/EXP_NAME_TIMESTAMP.dump`. These files use a custom data format.

The raw result files are split into two sections, which are separated by a newline, four dashes, and another newline character (`\n----\n\n`). The first part of the result file contains the information on the experiment configuration, such as used nodes, software versions and build parameters, topology configuration, and experiment command sequence. To allow for easy parsing, each line is prepended by `exp: `.

The second part of a result file contains the actual experiment raw data. This data is the output of the iotlab `serial-aggregator` tool. The `serial-aggregator` collects the STDIO of each iotlab node used in an experiment and joins the output on a line-by-line base. Each output line has the following structure:
```
TIME_S.TIME.MS;NODE_ID;STDIO output
```
e.g.
```
1606818574.051906;nrf52dk-2;buf40
```
With this, each raw file contains the complete STDIO output over the experiment runtime of all nodes used in that experiment.

In order to track network traffic and the state of each node, we use custom RIOT modules that output defined events to a nodes STDIO (see `lib/riot/`).


## Intermediate data
Once raw data is parsed and processed using the `tools/results.py` script, a number of intermediate plots and data files are created. These plots are used for detailed analysis of a single experiment run and to verify an experiments validity to rule out e.g. testbed issues and firmware errors (like crashing nodes). Each plot is saves as `*.pdf` as well as `*.png` file into the `results/plots/EXP_NAME/` folder. It is important to note, that these intermediate plots are not used in our paper directly.

Additionally to the plot files, the raw data for each plot is saved as `*.json` file. These JSON file contain all data needed by Matplotlib to create the corresponding plots. These file contain two objects: the `info` object containing all meta information such as type of the plot, axes and tick labels, etc., while the `data` object contains the actual raw data used in the corresponding plots. Both, the `info` and the `data` objects are structured in a way, so that these can be passed directly to the plotting functions of our custom Matplotlib-wrapper in `tools/exputil/plotter.py`.

These intermediate JSON files are used as input for the scripts that create the actual figures as printed in our paper (see `tools/fig_x.py`).
