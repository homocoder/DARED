#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def usage():
	print("\nUsage: imgPipeIF [options]") 
	print("\nDescription: This script takes an already calibrated ALMA pipeline execution and continues to imaging steps.")
	print("\nOptions:")
	print("\t--dir=<path>            Absolute or relative path to the root of a pipeline execution to proceed with imaging.")
	print("\t--env=<path>            Path to file to 'source' environment variables.")
	print("\t-h, --help              Show this help.")
	
	print("\nExamples: ")
	print("\t* Do the imaging for a calibrated pipeline execution:")
	print("\t\timgPipeIF --dir=2012.1.00075.S_2014_09_11T16_17_10.661\n")
	print("\t\timgPipeIF --dir=/lustre/pipeline/2012.1.00075.S_2014_09_11T16_17_10.661 --env=/opt/etc/c4r2\n")

class log:
	def __init__(self, filename, print_flag = False):
		from datetime import datetime
		now = datetime.now().isoformat().replace(":", "-")
		self.filename = filename
		self.print_flag = print_flag
		self.fd = open(filename + "." + now + ".log", "w")

	def log(self, str):
		from datetime import datetime
		now = datetime.now().isoformat()
		str = str.split("\n")
	
		for s in str:			
			self.fd.write(now + ": " + s + "\n")
			if self.print_flag:
				print(now + ": " + s)
			self.fd.flush()

	def run(self, command):
		"""This procedure runs a command in background and logs the output line by line in real-time

		command: String containing the command to run."""
		
		from subprocess import Popen, PIPE
		proc = Popen(command, shell=True, bufsize=0, stdout=PIPE)
		for l in proc.stdout:
			self.log(l.decode()[:-1]) # type(l) is bytes

	def close(self):
		self.fd.close()

def main():
	from sys import argv, stdout, exit
	from os import system, chdir, getcwd, environ
	from subprocess import getoutput
	from getopt import getopt, GetoptError
	from glob import glob

	global logfile_fd

	# Arguments and options parsing.
	if len(argv) == 1:
		usage()
		exit()

	try:
		opts, args = getopt(argv[1:], "deh", ["dir=", "env=", "help"])
	except GetoptError as err: 
		print(err) 
		usage()
		exit(2)

	# Default variables
	img_dir = argv[1]
	hostname = environ['HOSTNAME']
	username = environ['USER']
	casacmd = 'casa --pipeline --nogui '
	envcmd = 'source ' + environ['SARADIR'] + '/etc/' + environ['SARA']
	scipipe_rootdir = environ['SCIPIPE_ROOTDIR']

	# Arguments and options detection.
	for o, a in opts:
		if o in ("--dir="):
			img_dir = a

		if o in ("--env="):
			envcmd = 'source ' + a

		if o in ("-h", "--help"):
			usage()
			exit(0)

	if img_dir[0] != "/":
		img_dir = getcwd() + "/" + img_dir
	if img_dir[-1] != "/":
		img_dir += "/"

	pldir = img_dir.split('/')[-2]
	cmd = envcmd + ' && rm -rf ' + img_dir + 'SOUS*/GOUS*/MOUS*/rawdata/uid___*/ASDMBinary/* '
	cmd += ' ; (cd ' + img_dir + '.. '
	cmd += ' ; cp --verbose --no-dereference --recursive --verbose --preserve=mode,timestamps --no-preserve=ownership ' + img_dir + ' ' + scipipe_rootdir + ' & '
	cmd += ' tar -cvf ' + img_dir[:-1] + '.tar ' + pldir + ') && mv ' + img_dir + ' ' + scipipe_rootdir + environ['SARADIR'] + '/mnt/trash ' 
	print('Copying original execution to $SCIPIPE_ROOTDIR and making a tar file in the original location ...\n')

	print(cmd)	
	print(getoutput(cmd))

	img_dir = scipipe_rootdir + '/' + pldir
	chdir(img_dir)

	cmd = "grep OUSStatusRef " + img_dir + "/SOUS_uid___*/GOUS_uid___*/MOUS_uid___*/working/PPR_uid___*.xml"
	cmdoutput = getoutput(cmd)
	print(cmdoutput)
	mous_uid = cmdoutput.split('"')[1]

	# Now I have a directory, I can create the log file
	mylog = log(img_dir + "/imgPipeIF." + mous_uid.replace("/", "_").replace(":", "_"), print_flag = True)
	l = mylog.log # l points to method "log"
	l(cmdoutput)

	# Log the environment
	l('Environment variables:')
	cmd = 'envcmd + ' + '; env '
	mylog.run(cmd)

	# Log main info
	l("Running the pipeline for MOUS " + mous_uid + " as " + username + "@" + hostname)
	l("Pipeline execution absolute directory is " + img_dir)

	## Find working directory and PPR
	dir_working = glob(img_dir + '/SOUS_uid___*/GOUS_uid___*/MOUS_uid___*/working/')[0]
	chdir(dir_working)

	context_file = glob(dir_working + "/pipeline-201*context")
	context_file.sort()
	context_file = context_file[0]
	
	cmd = 'mv ' + context_file[:-8] + '* ' + dir_working + '/..' 
	l('Moving first execution 1 level up.')
	mylog.run(cmd)

	cmd = "ls -1 ../working/PPR*xml"
	pprfile = getoutput(cmd)

	# Run the IMAGING pipeline!!!!
	cmd = envcmd + ' ; xvfb-run -a ' + casacmd + ' -c "eppr.executeppr(\'' + pprfile + '\',importonly=False,bpaction=\'resume\');exit;"'

	l('Starting to run the command "' + cmd + '"')
	mylog.run(cmd)

	# daPermissions
	cmd = envcmd + ' ; daPermissions pipeline*'
	l('Starting to run the command "' + cmd + '"')
	mylog.run(cmd)

	l("imgPipeIF has finished :)")
	mylog.close()

main()
