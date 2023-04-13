# DARED: Data Analysis Reduction Environment Distribution

# DARED directories hierarchy
```
dared
├── bin
├── etc
├── mnt
│   ├── dataproc
│   │   ├── xuser
│   │   │   ├── Deliver
│   │   │   ├── Fix
│   │   │   ├── Pack
│   │   │   ├── Run
│   │   │   ├── Used
│   │   │   └── Work
│   │   ├── yuser
│   │   │   ├── Deliver
│   │   │   ├── Fix
│   │   │   ├── Pack
│   │   │   ├── Run
│   │   │   ├── Used
│   │   │   └── Work
│   │   └── zuser
│   │       ├── Deliver
│   │       ├── Fix
│   │       ├── Pack
│   │       ├── Run
│   │       ├── Used
│   │       └── Work
│   ├── log
│   ├── tmp
│   └── trash
└── opt
    ├── acs
    ├── casa
    ├── java
    ├── oracle
    ├── python
    └── redtools
```

* `dared`: Portable root directory of the self-contained installation
* `bin`: The only directory where the exposed commands and script resides
* `etc`: All the site-settings are here. Each pre-defined environment has its own mnemonic name
* `mnt`: Directory containing locations for users processing
* `opt`: Third-party software. The wrapper scripts and all its dependencies
* `mnt/dataproc`: This is the location where the cluster-aware storage is available for users

# Requirements
* `RHEL 6/7`
* `CentOS 6/7` (\*)
* Regular user account with restricted permissions (no root/admin needed)

(\*) `CentOS 6/7` have also been tested under Docker containers (http://docker.io)

# Usage

The only step to use a pre-defined environment is to "source" the corresponding configuration file. Example:

```sh
$ source /opt/dared/etc/c4r2
```

Once the environment is loaded, the shell prompt will show the environment, user and node names:

```sh
[c4r2][fmorales@cvpost061 ~]$
```

Now, the user have the reduction tools available from the command line:

* `calPipeIF`: Tool to do the calibration for a Interferometric dataset
* `imgPipeIF`: Tool to do the imaging for an already calibrated dataset
* `redPipeIF`: Tool to perform a complete Interferometric pipeline reduction (cal+img) for a given MOUS
* `redPipeSD`: Tool to perform a complete Single Dish pipeline reduction for a given MOUS
* `pkgPipe`: Tool to automatize the stager and packaging process after a qa2 Pass
* `getPPR`: Standalone script to create the directory structure before running the pipeline
* `getASDM`: Wrapper for dataPacker that can read a PPR file
* `daPermissions`: Sets permissions to share pipeline runs between users
* `getAnalysisUtils`: Gets the latest analysis utils from CVS
