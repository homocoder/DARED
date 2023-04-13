#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def usage():
	print("\nUsage: pkgPipe [options]") 
	print("\nDescription: This script packages an imaging ALMA pipeline execution, for approval/qa2.")
	print("\nOptions:")
	print("\t--dir=<path>            Absolute or relative path to the root of a pipeline execution to proceed with packaging.")
	print("\t--env=<path>            Path to file to 'source' environment variables.")
	print("\t-h, --help              Show this help.")
	
	print("\nExamples: ")
	print("\t* Do the qa2 package for a pipeline execution:")
	print("\t\tpkgPipe --dir=2012.1.00075.S_2014_09_11T16_17_10.661\n")

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
	from os.path import abspath, exists
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
	plrun_dir = abspath(argv[1])
	hostname = environ['HOSTNAME']
	username = environ['USER']
	casacmd = 'casa --nogui '
	envcmd = 'source ' + environ['SARADIR'] + '/etc/' + environ['SARA']
	scipipe_rootdir = environ['SCIPIPE_ROOTDIR']

	# Arguments and options detection.
	for o, a in opts:
		if o in ("--dir="):
			plrun_dir = abspath(a)

		if o in ("--env="):
			envcmd = 'source ' + a

		if o in ("-h", "--help"):
			usage()
			exit(0)

	plrun_rel_dir = plrun_dir.split('/')[-1]
	cmd = "grep OUSStatusRef " + plrun_dir + "/SOUS_uid___*/GOUS_uid___*/MOUS_uid___*/working/PPR_uid___*.xml"
	cmdoutput = getoutput(cmd)
	mous_uid = cmdoutput.split('"')[1]
	working_dir = glob(plrun_dir + '/SOUS_uid___*/GOUS_uid___*/MOUS_uid___*/working')[0]
	products_dir = glob(plrun_dir + '/SOUS_uid___*/GOUS_uid___*/MOUS_uid___*/products')[0]
	readme_file = products_dir + '/README'
	readme_jao_file = products_dir + '/README_JAO'
	stager_dir   = plrun_rel_dir + mous_uid.replace('uid://', '_uid___').replace('/', '_')
	project_code = plrun_rel_dir[:14]
	package_name = project_code  + mous_uid.replace('uid://', '_uid___').replace('/', '_') + '_001_of_001.tar' 

	# Now I have a directory, I can create the log file
	mylog = log(plrun_dir + "/pkgPipe." + mous_uid.replace("/", "_").replace(":", "_"), print_flag = True)
	l = mylog.log # l points to method "log"
	l(cmdoutput)

	# Log main info
	l("Running the stager+packager for MOUS " + mous_uid + " as " + username + "@" + hostname)
	l("Pipeline execution absolute directory is " + plrun_dir)

	# Readme files
	if not exists(readme_file):
		open(readme_file, 'w').close()
	if not exists(readme_jao_file):
		open(readme_jao_file, 'w').close()

	chdir(working_dir)

	# Get the latest version of analysis utils
	l('Get the latest version of analysis utils')
	cmd = envcmd + '; getAnalysisUtils'
	l('Starting to run the command "' + cmd + '"')
	mylog.run(cmd)
	
	# First, create the stager directory structure. Then, run the packager
	cmd = """def pkgPipe():
	from sys import path
	from os.path import exists
	path.append('""" + working_dir + """/AIV/science/qa2/')
	path.append('""" + working_dir + """/AIV/science/analysis_scripts/')
	import analysisUtils as aU
	# Create an "alias" for analysis utils
	es = aU.stuffForScienceDataReduction()
	# Import ALMA stuff
	from QA2_Packaging_module import QA_Pipeline_Stager, QA_Packager

	stager_dir = '""" + stager_dir + """'
	script_for_imaging = stager_dir + '/sg_ouss_id/group_ouss_id/member_ouss_id/script/scriptForImaging.py'
	readme_file = stager_dir + '/sg_ouss_id/group_ouss_id/member_ouss_id/README'

	QA_Pipeline_Stager('""" + plrun_dir + """', stager_dir, mode='copy',PIscript='""" + working_dir + """/AIV/science/qa2/scriptForPI.py',PIPE_README='""" + readme_jao_file + """')
	if not exists(script_for_imaging):
		open(script_for_imaging, 'w').close()

	if not exists(readme_file):
		open(readme_file, 'w').close()

	QA_Packager(origpath=stager_dir, readme=stager_dir + '/sg_ouss_id/group_ouss_id/member_ouss_id/README', packpath=stager_dir[:14], mode='copy', style='cycle4-pipe', PIscript='""" + working_dir + """/AIV/science/qa2/scriptForPI.py')"""
	fd = open('redtools_pkgPipe.casa.py', 'w')
	fd.write(cmd)
	fd.close()

	cmd = envcmd + ' ; ' + casacmd + ' -c "execfile(\'redtools_pkgPipe.casa.py\');pkgPipe();exit;"'
	l('Starting to run the command "' + cmd + '"')
	mylog.run(cmd)

	# daPermissions
	cmd = envcmd + ' ; daPermissions ' + stager_dir
	l('Starting to run the command "' + cmd + '"')
	mylog.run(cmd)
	
	# Create the tar package
	cmd = 'tar -cvf ' + package_name + ' ' + project_code
	l('Starting to run the command "' + cmd + '"')
	mylog.run(cmd)

	# Rename ticket.zip file 
	cmd = 'mv ' + project_code + '.ticket.zip ' + project_code + mous_uid.replace('uid://', '_uid___').replace('/', '_') + '.ticket.zip'
	l('Starting to run the command "' + cmd + '"')
	mylog.run(cmd)

	# MD5 hash to package file  
	cmd = 'md5sum ' + package_name + ' > ' + package_name + '.md5sum'
	l('Starting to run the command "' + cmd + '"')
	mylog.run(cmd)

	# Cross your fingers!
	l("pkgPipe has finished :)")
	mylog.close()

main()
