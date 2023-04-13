# redTools: Reduction Tools

The redTools are a simple set of scripts to help Data Analysts to run the ALMA Pipeline.


## calPipeIF
```
[c4r2][fmorales@cvpost061 ~]$ calPipeIF --help

Usage: calPipeIF [options]

Description: This script assists in the execution of the ALMA interferometric calibration pipeline.

Options:
--mous=<mous_uid>       MOUS status uid to execute the pipeline.
--dir=<path>            Absolute or relative path to the root of a pipeline execution to look for a PPR.
--env=<path>            Path to file to 'source' environment variables.
-h, --help              Show this help.

Examples:
* Execute the pipeline for a FullyObserved MOUS:
calPipeIF --mous=uid://A002/X5ce05d/X6b

calPipeIF --mous=uid://A002/X5ce05d/X6b --env=/opt/sacm/etc/c4r2
```

## imgPipeIF

```
[c4r2][fmorales@cvpost061 ~]$ imgPipeIF --help

Usage: imgPipeIF [options]

Description: This script takes an already calibrated ALMA pipeline execution and continues to imaging steps.

Options:
--dir=<path>            Absolute or relative path to the root of a pipeline execution to proceed with imaging.
--env=<path>            Path to file to 'source' environment variables.
-h, --help              Show this help.

Examples:
* Do the imaging for a calibrated pipeline execution:
imgPipeIF --dir=2012.1.00075.S_2014_09_11T16_17_10.661

imgPipeIF --dir=/lustre/pipeline/2012.1.00075.S_2014_09_11T16_17_10.661 --env=/opt/etc/c4r2
```

## redPipeIF

```
[c4r2][fmorales@cvpost061 ~]$ redPipeIF --help

Usage: redPipeIF [options]

Description: This script assists in the execution of the ALMA interferometric reduction (cal+img) pipeline.

Options:
--mous=<mous_uid>       MOUS status uid to execute the pipeline.
--dir=<path>            Absolute or relative path to the root of a pipeline execution to look for a PPR.
--env=<path>            Path to file to 'source' environment variables.
-h, --help              Show this help.

Examples:
* Execute the pipeline for a FullyObserved MOUS:
redPipeIF --mous=uid://A002/X5ce05d/X6b

redPipeIF --mous=uid://A002/X5ce05d/X6b --env=/opt/sacm/etc/c4r2
```

## redPipeSD

```
[c4r2][fmorales@cvpost061 ~]$ redPipeSD --help

Usage: redPipeSD [options]

Description: This script assists in the execution of the ALMA Single Dish reduction (cal+img) pipeline.

Options:
--mous=<mous_uid>       MOUS status uid to execute the pipeline.
--dir=<path>            Absolute or relative path to the root of a pipeline execution to look for a PPR.
--env=<path>            Path to file to 'source' environment variables.
-h, --help              Show this help.

Examples:
* Execute the pipeline for a FullyObserved MOUS:
redPipeSD --mous=uid://A002/X5ce05d/X6b

redPipeSD --mous=uid://A002/X5ce05d/X6b --env=/opt/sacm/etc/c4r2
```

## pkgPipe

```
[c4r2][fmorales@cvpost061 ~]$ pkgPipe --help

Usage: pkgPipe [options]

Description: This script packages an imaging ALMA pipeline execution, for approval/qa2.

Options:
--dir=<path>            Absolute or relative path to the root of a pipeline execution to proceed with packaging.
--env=<path>            Path to file to 'source' environment variables.
-h, --help              Show this help.

Examples:
* Do the qa2 package for a pipeline execution:
pkgPipe --dir=2012.1.00075.S_2014_09_11T16_17_10.661
```
