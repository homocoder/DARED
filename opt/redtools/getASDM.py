#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def usage():
	print("\nUsage: getASDM [options]") 
	print("\nDescription: This script gets the ASDMs for a given PPR file.")
	print("\nOptions:")
	print('\t--dir=<path>            Absolute or relative path to the root of a pipeline execution to look for a PPR file.')
	print('\t--uid=<path>            ASDM uid to get from Archive. (Mutually exclusive with --dir parameter')
	print("\t--env=<path>            Path to file to 'source' environment variables.")
	print("\t-h, --help              Show this help.")
	
	print("\nExamples: ")
	print("\t\tgetASDM --uid=uid://A002/Xafb2c8/Xaeb")
	print("\t\tgetASDM --dir=2016.1.00455.S_2017_02_28T20_15_25.533\n")

class log:
	def __init__(self, filename, print_flag = False):
		from datetime import datetime
		now = datetime.now().isoformat().replace(":", "-")
		self.filename = filename + "." + now + ".log"
		self.print_flag = print_flag
		self.fd = open(self.filename, "w")

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
		
		from subprocess import Popen, PIPE, STDOUT
		from sys import exit

		self.log('Starting to run the shell command: "' + command + '"')

		try:
			proc = Popen(command, shell=True, bufsize=2, stdout=PIPE, stderr=STDOUT, universal_newlines=True)
		except:
			self.last_output = proc.read()
			self.log('STDOUT + STDERR' + self.last_output)

		for s in proc.stdout:
			self.log(s)
			self.last_output = s

		proc.poll()
		proc.terminate()
		proc.kill()
		self.log('Return code of shell command is: ' + str(proc.returncode))

		if proc.returncode:
			self.log('Exiting :(')
			self.close()
			exit(1)

	def close(self):
		self.fd.close()

def main():
	from sys import argv, stdout, exit
	from os import system, chdir, getcwd, environ
	from subprocess import getoutput
	from getopt import getopt, GetoptError
	from xml.dom.minidom import parse
	from glob import glob
	from os.path import abspath

	global logfile_fd

	# Arguments and options parsing.
	if len(argv) == 1:
		usage()
		exit()
	try:
		opts, args = getopt(argv[1:], "dueh", ["dir=", "uid=", "env=", "help"])
	except GetoptError as err: 
		print(err) 
		usage()
		exit(2)

	# Default variables
	asdm_uid = argv[1]
	pprmode = False
	hostname = environ['HOSTNAME']
	plrun_dir = abspath('.')
	username = environ['USER']
	envcmd = 'source ' + environ['DARED_ROOT'] + '/etc/default '
	scipipe_rootdir = environ['SCIPIPE_ROOTDIR']

	# Arguments and options detection.
	for o, a in opts:
		if o in ("--dir="):
			plrun_dir = abspath(a)
			pprmode = True

		if o in ("--uid="):
			asdm_uid = a

		if o in ("--env="):
			envcmd = 'source ' + abspath(a)

		if o in ("-h", "--help"):
			usage()
			exit(0)

	# Start logging
	mylog = log(plrun_dir + "/getASDM", print_flag = True)
	l = mylog.log # l points to method "log"
	l('Starting log. Logfile is ' + mylog.filename)

	# Search EBs on this execution
	if pprmode:
		ppr_file = glob(plrun_dir + '/SOUS_uid___*/GOUS_uid___*/MOUS_uid___*/working/PPR_uid___*.xml')
		if len(ppr_file) == 0:
			ppr_file = glob(plrun_dir + '/MOUS_uid___*/working/PPR_uid___*.xml')
		ppr_file = ppr_file[-1]
		cmd = "grep ExecBlockId " + ppr_file
		cmdoutput = getoutput(cmd)
		ebs = cmdoutput.replace("<ExecBlockId>", "").replace(" ", "").replace("</ExecBlockId>", "").replace('\t', '').replace(' ', '').split('\n')
		l("The Execution Blocks in PPR are:\n" + ebs.__repr__())
		rawdata_dir = glob(plrun_dir + '/SOUS_uid___*/GOUS_uid___*/MOUS_uid___*/rawdata')
		if len(rawdata_dir) == 0:
			rawdata_dir = glob(plrun_dir + '/MOUS_uid___*/rawdata')
		chdir(rawdata_dir[-1])
	else:
		ebs = [asdm_uid,]
	
	for e in ebs:
		mylog.run('asdmExportLight ' + e)
		mylog.run(envcmd + ' ; daPermissions ' + e.replace('uid://', 'uid___').replace('/', '_'))

	l("getASDM has finished :)")
	mylog.close()

main()
