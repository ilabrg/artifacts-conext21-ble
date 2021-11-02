# Framework for running multi-hop IP over BLE Experiments

## About
This repository contains all the artifacts necessary to reproduce the results of our paper **'Mind the Gap: Multi-hop IPv6 over BLE in the IoT'**.

## Repository Structure
The following list gives a high-level rundown on the purpose of each folder in this repository:

- `exp`: this folder contains all the experiment descriptions, as well as the corresponding RIOT applications
- `expvars`: generic experiment configuration parameter sets like topology descriptions, NimBLE and RIOT buffer configurations, connection parameter sets, ...
- `lib`:  The `lib/riot` subdirectory contains custom RIOT libraries that are build into the RIOT applications and used for logging network events as well as collecting statistical information on a nodes state.
- `results`: contains the experiment results. The results are structured in three subdirectories:
  - `results/logs`: the log files of successful experiment runs are stored here. See [DATAFORMATS.md](DATAFORMATS.md) for a description on the files formatting.
  - `results/tmp`: while experiments are running the log will be created here. Once an experiment successfully completes, the according logfile is moved to `results/logs`
  - `results/plots`: figures and intermediate data created during the analysis of logfiles.
  - `results/figs`: figures created from the aggregated data of 1 to N experiment runs as outputted by the scripts located in `tools`. These are the figures printed in our paper.
- `suites`: put yml files with lists of single experiments into this folder, so runs of more than a single experiment can be automated.
- `tools`: this folder contains the actual Python code of our experiment framework as well as the specific scripts used to create the figures printed in the paper.

Each experiment run has a unique name as deducted by the filename of the experiment description file in the `exp` folder. For example, the experiment described in `exp/exp_foobar.yml` has the name `exp_foobar`. The experiment log will be put into the `results/logs/exp_foobar/exp_foobar_YYYYMMDD-hhmmss.dump`, while all analysis result files will be created in `results/plots/foobar/exp_foobar_YYYYMMDD-hhmmss_xxx.yyy`. This way all log and result files can always be traced back to the specific experiment configuration used.


## How-to use this experiment framework

### Get the raw experiment data as used in the paper
All raw experiment data used in our paper is available via zenodo: https://zenodo.org/record/5635607

To make this data accessible to our experiment framework and tooling located in this repository, we included a script that will automatically download the raw data from the zenodo into the `results/logs` and `results/plots` subfolders. Simply run the
```bash
./download_experiment_data.sh
```

script located in the root of this repository.

**Note:** the download my take a while as the script is downloading roughly 4Gb of data and the extracted files will take roughly 20Gb of local storage.


### Reproduce the figures printed in the paper
Once the raw data has been downloaded, all figures from the paper can be reproduced from the raw data by running the plotting scripts provided in the `tools/` directory of this repository. Each individual result plot in the paper is created by its dedicated plotting script. To maintain reproducibility, the specific raw results used for each plot are hard coded into the scripts source code, hence the scripts are run without any additional parameters.

The following table shows the mapping between figures in the paper and the script used to produce it:

| Figure      | creator script |
| :--         | :-- |
| Fig. 7 (a)  | `tools/fig_app_pdr.py` |
| Fig. 7 (b)  | `tools/fig_app_cdf_linetree.py` |
| Fig. 8 (a)  | `tools/fig_app_cdf_itvlcmp.py` |
| Fig. 8 (b)  | `tools/fig_app_cdf_prodcmp_75ms.py` |
| Fig. 9 (a)  | `tools/fig_app_pdr_load_100ms.py` |
| Fig. 9 (b)  | `tools/fig_app_pdr_load_i2s.py` |
| Fig. 10 (a) | `tools/fig_app_pdr_154.py` |
| Fig. 10 (b) | `tools/fig_app_cdf_154.py` |
| Fig. 12     | `tools/fig_shading.py` |
| Fig. 13 (a) | `tools/fig_app_pdr_rand24.py` |
| Fig. 13 (b) | `tools/fig_ll_pdr_rand24.py` |
| Fig. 13 (c) | `tools/fig_app_cdf_rand24.py` |
| Fig. 14     | `tools/fig_overview_connloss_1saggr.py` |
| Fig. 15     | `tools/fig_stats.py' |`


### Howto setup your host system for running experiments
The following list describes all preparation necessary to (re)run the IP over BLE experiments presented in our paper using our experimentation framework and the [FIT Iotlab](https://www.iot-lab.info/).

**1. Create an `iotlab` account.**

Go to to [https://www.iot-lab.info/](https://www.iot-lab.info/) and sign up for a free account to get access to the `iotlab`

**2. Boot into your favorite Linux environment**

We expect our framework to be run under Linux. It might work under OSX or Windows as well, but this is untested.

**3. Make sure you have `python3`, `pip3`, and `tmux` installed**

Under Debian/Ubuntu these are installed by calling
```bash
sudo apt-get install python3 python3-pip tmux
```

**4. Install the required Python packages**

The needed packages are specified in the included `requirements.txt` file. 
Run 
```bash
pip3 install --user -r requirements.txt
```

 to let the Python package manager take care of this.

**5. Create the authentication token for the iotlab.**

This needs to be done on the local host as well as the front-end server for every site that is used for experiments. 
To create the token on the local host, run
```bash
iotlab-auth -u USERNAME
```

To create the token on the remote iotlab front-end servers, you have to ssh into each of them once and execute the same command there as well, e.g.
```bash
ssh USERNAME@saclay.iot-lab.info
> iotlab-auth -u USERNAME
```

This has to be done only once and the tokens are valid as long as the users password does not change.

**6. Initialize and update git submodules for `RIOT` and `NimBLE`**

Both RIOT and NimBLE are configured in this repository as git submodules. The git submodule configuration takes care of downloading both projects and switching to the actual branches that contain the necessary logging hooks used in our experiments.

To initialize the submodules run the following in the root of the repository:
```bash
git submodule init
git submodule update
```

Alternatively, clone these repositories directly:
```bash
git clone --branch conext21 https://github.com/haukepetersen/RIOT lib/RIOT
git clone --branch conext21 https://github.com/haukepetersen/mynewt-nimble lib/NIMBLE
```

**7. Install the needed toolchain for building RIOT**

Our experimentation framework creates the needed RIOT binaries locally for each experiment run. In order to build these binaries, your host system must be able to build RIOT. For this, the `arm-none-eabi-gcc` toolchain must be available on the host system.

All results used in our work were created with `arm-none-eabi-gcc 9.3.1`.

To check if this is the case, simply try to build RIOTs `hello-world` example application for the `nrf52dk` board:
```bash
# make sure the RIOT submodule is initialized and checked out...
cd lib/RIOT/examples/hello-world
BOARD=nrf52dk make all
```

Once this succeeds, the toolchain related setup is complete. If you are not able to build RIOT locally, please take a look at [RIOTs getting started guide](https://doc.riot-os.org/getting-started.html).


### Run an experiment
To run a single experiment in the iotlab simply run the included `exp.py` tool and pass the target experiment configuration file as command line argument, e.g.:
```
./exp.py exp/exp_putnon_statconn-static_1s1h39b_i75.yml
```

This will trigger the following:

- the `exp.py` script will collect the full experiment configuration as specified in the given experiment file and its linked files
- all needed RIOT binaries are compiled for each target platform used in the experiment
- the needed nodes in the iotlab are allocated
- each iotlab node is flashed with the corresponding firmware
- a new `tmux` session is started in the background, which will take care of communicating with the nodes through the iotlab's `serial_aggregator`
- while the experiment is running, the commands as specified in the experiment description are passed to the corresponding nodes. At the same time, the aggregated STDIO output of all nodes is logged into a common logfile created in the `/results/tmp` direcctory
- once the experiment successfully completes, the temporary logfile is move to `results/logs` and the iotlab session is terminated

Each successful experiment run will create a single logfile in the `results/logs` directory. See below in the `Analyze the results of a single experiment` section on how to proceed with these logfiles.

### Run a set of experiments
Running multiple experiments in a sequence is possible by specifying a list of experiment files in a experiment suite file. For example, running experiments `a`, `b`, and `c` would require a suite file in the `suites` directory as follows, e.g. `suites/expset_abc.suite`:
```
- exp/a.yml
- exp/b.yml
- exp/c.yml
```

Then running this suite is as simple as running a single experiment as described in the section above:
```
./exp.py suites/expset_abc.suite
```

### Analyze the results of a single experiment
To create the default analysis output for any given single experiment the script provided in `tools/results.py` is used.

E.g. to analyze the results of the latest run for the experiment `exp_foo` do the following:
- get the specific name of the experiment run, containing the timestamp, from the experiments logfile in `results/logs/foo/foo_X.dump`, e.g. `results/logs/exp_foo/exp_foo_20210901-201512.dump`
- run the experiment analysis script passing the experiment by passing the experiments logfile as parameter, e.g.:
```bash
tools/results.py results/logs/foo/foo_20210901-201500.dump
```
This will parse the experiment logfile (this may take a while) and output the following:
- in the shell window a dump of the most interesting experiment analysis raw data is printed
- there will be a number matplotlib windows popping up displaying the created result graphs. Simple close each window to continue with the analysis and see the next graph
- all graphs and the corresponding intermediate data are also written to `results/plots/exp_foo/exp_foo_20210901-201500-XXX.yyy`

**Note:** The purpose of these intermediate graphs created by the `results.py` script is mainly to preprocess and validate single experiment runs. The actual plots used in the paper are then build from these intermediate data sets by running the scripts located in the `tools/` folder.


### Create aggregate results of multiple experiments
Each aggregation plot is scripted by its own python script located in the `tools` directory. All scripts are structured the same way: on top the specific experiment runs are specified by linking the corresponding raw data in `results/plots/` while the plot itself is coded using matplotlib in the remainder of each script.

**NOTE**: for each experiment run used in an aggregate script, the experiment run has to be manually analyzed using the steps described in the section above once.
