#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def usage():
	print("\nUsage: redPipeCS [options]") 
	print("\nDescription: This script assists in the execution of the ALMA Pipeline for CalSurvey data.")
	print("\nOptions:")
	print("\t--mous=<mous_uid>       MOUS status uid to execute the pipeline. (mandatory)")
	print("\t--eb=<mous_uid>         Comma-separated EBs uid to use. (mandatory)")
	print("\t--dir=<path>            Absolute or relative path to the root of a pipeline execution to look for a PPR.")
	print("\t--env=<path>            Path to file to 'source' environment variables. Usage of this flag is not supported.")
	print("\t-h, --help              Show this help.")
	
	print("\nExample: ")
	print("\t* Execute the pipeline given a MOUS uid and a EB uid:")
	print("\t\tredPipeCS --mous=uid://A002/X845868/X2d --eb=uid://A002/Xc2ec9c/X1279\n")

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
	from os.path import abspath
	from subprocess import getoutput
	from getopt import getopt, GetoptError
	from xml.dom.minidom import parse
	from glob import glob

	global logfile_fd

	# Arguments and options parsing.
	if len(argv) == 1:
		usage()
		exit()
	try:
		opts, args = getopt(argv[1:], "medeh", ["mous=", "eb=", "dir=", "env=", "help"])	
	except GetoptError as err: 
		print(err) 
		usage()
		exit(2)

	# Default variables
	mous_uid = argv[1]
	ebs_uid = ''
	plrun_dir = ''
	pprmode = False
	hostname = environ['HOSTNAME']
	username = environ['USER']
	casacmd = 'casa --pipeline --nogui '
	unsupported = False
	envcmd = 'source /opt/dared/etc/default '
	scipipe_rootdir = '/opt/dared/mnt/dataproc '

	# Arguments and options detection.
	if 'DARED_ROOT' in environ:
		envcmd = 'source ' + environ['DARED_ROOT'] + '/etc/default '
	if 'SCIPIPE_ROOTDIR' in environ:		
		scipipe_rootdir = environ['SCIPIPE_ROOTDIR']

	for o, a in opts:
		if o in ("--mous="):
			mous_uid = a

		if o in ("--eb="):
			ebs_uid = a

		if o in ("--dir="):
			plrun_dir = abspath(a)
			pprmode = True

		if o in ("--env="):
			envcmd = 'source ' + a
			unsupported = True

		if o in ("-h", "--help"):
			usage()
			exit(0)

	# Execute PipelineMakeRequest
	if pprmode:
		ppmr_rel_dir = plrun_dir.split('/')[-1]
		ppmr_dir = plrun_dir
		cmd = "grep OUSStatusRef " + plrun_dir + "/MOUS_uid___*/working/PPR_uid___*.xml"
		cmdoutput = getoutput(cmd)
		mous_uid = cmdoutput.split('"')[1]
	else:
		cmd = envcmd + ' ; getPPR ' + mous_uid + ' intents_hifa.xml procedure_hifa_calsurvey.xml '
		# Detect execution directory
		cmdoutput = getoutput(cmd)
		print(cmdoutput)
		for i in cmdoutput.split("\n"):
			if 'Project root directory is' in i:
				ppmr_rel_dir = i.split()[-1]
				ppmr_dir = scipipe_rootdir + '/' + ppmr_rel_dir

	# Now I have a directory, I can create the log file
	mylog = log(ppmr_dir + "/redPipeCS." + ppmr_rel_dir + "." + mous_uid.replace("/", "_").replace(":", "_"), print_flag = True)
	l = mylog.log # l points to method "log"
	l(cmdoutput)

	# Log the environment
	l('Environment variables:')
	cmd = 'envcmd + ' + '; env '
	mylog.run(cmd)

	## Log main info
	l("Running the pipeline for MOUS " + mous_uid + " as " + username + "@" + hostname)
	l("Pipeline execution absolute directory is " + ppmr_dir)
	l("Pipeline execution relative directory is " + ppmr_rel_dir)

	obsproject_code = ppmr_rel_dir[:14]
	l("Project code is " + obsproject_code)

	## Find MOUS directory
	dir_mous = glob(ppmr_dir + '/MOUS_uid___*')[0]
	l('MOUS directory is ' + dir_mous)
	chdir(dir_mous)

	## Identifying the valid SB for this execution. TODO: Make this again for the God's sake!!!!!!
	cmd = 'grep --after-context=2 "' + ebs_uid.split(',')[0] + '" ./rawdata/MOUS_uid___*.xml'
	l('Running ' + cmd)
	sbs_uid = getoutput(cmd + ' ./rawdata/MOUS_uid___*.xml').split('"')[1].replace('uid://', 'uid___').replace('/', '_')
	l('SB Status UID is ' + sbs_uid)	

	mylog.run('mv SBS_' + sbs_uid + '/rawdata/* ./rawdata')
	mylog.run('mv SBS_' + sbs_uid + '/working .')

	## Find working directory and PPR
	dir_working = glob(ppmr_dir + '/MOUS_uid___*/working/')[0]
	chdir(dir_working)
	pprfile = glob('PPR*xml')[0]

	## Change EBs to be included on this execution
	if ebs_uid != '':
		ebs_lines = list()
		ebs_uid = ebs_uid.split(',')
		for e in ebs_uid:
			ebs_lines.append('                        <AsdmIdentifier>\n')
			ebs_lines.append('                            <AsdmRef>\n')
			ebs_lines.append('                                <ExecBlockId>' + e + '</ExecBlockId>\n')
			ebs_lines.append('                            </AsdmRef>\n')
			ebs_lines.append('                            <AsdmDiskName>' + e.replace('uid://', 'uid___').replace('/', '_') + '</AsdmDiskName>\n')
			ebs_lines.append('                        </AsdmIdentifier>\n')

		fd = open(pprfile, "r")
		lines = fd.readlines()
		fd.close()

		newlines = list()
		for line in lines:
			if not (('<ExecBlockId>' in line and '</ExecBlockId>' in line) or ('<AsdmRef>' in line or '</AsdmRef>' in line) or ('<AsdmIdentifier>' in line or '</AsdmIdentifier>' in line) or ('<AsdmDiskName>' in line and '</AsdmDiskName>' in line) ):
				newlines.append(line)
			if '<SBTitle>Undefined</SBTitle>' in line:
				newlines = newlines + ebs_lines
				
		fd = open(pprfile, "w")
		fd.writelines(newlines)
		fd.close()

	## log EBs on this execution
	cmd = "grep ExecBlockId " + ppmr_dir + "/MOUS_uid___*/working/PPR_uid___*.xml"
	cmdoutput = getoutput(cmd)
	ebs = cmdoutput.replace("<ExecBlockId>", "").replace(" ", "").replace("</ExecBlockId>", "")
	
	l("The Execution Blocks in PPR are:\n" + ebs)

	## Fetching the data from Archive
	mylog.run('getASDM --dir=' + ppmr_dir)

	## Checking the rawdata
	rawdata = glob(ppmr_dir + '/MOUS_uid___*/rawdata/uid___*')
	l('EBs in rawdata directory are: ')
	for r in rawdata:
		l(r)

	## Get the flagtemplates from JAO
#	l('Downloading flagtemplates from JAO')

#	for r in rawdata:
#		rawdata_uid = r.split('/')[-1]
		#cmd = 'curl --silent ' + environ['DARED_URL']+ '/redtools/execblock/uid/' + rawdata_uid.replace('___', '://').replace('_', '/')
		#cmd += ' > ' + dir_working + '/' + rawdata_uid + '.flagtemplate.txt'
		#l('Starting to run ' + cmd)
		#mylog.run(cmd)
		
	# Store the RelativePath of this execution in the variable relative_path
	fd = open(pprfile, "r")
	pprXML = parse(fd)
	nodeList = pprXML.getElementsByTagName('RelativePath')
	s = nodeList[0] # There should be only 1 RelativePath node
	relative_path = s.firstChild.data # read
	fd.close()
	
	## If this execution is multi SB, edit RelativePath in PPR
	l('Warning, this execution contains multiple SBs.')
	fd = open(pprfile, "r")
	pprXML = parse(fd)
	relative_path = pprXML.getElementsByTagName('RelativePath')[0].firstChild.data
	pprXML.getElementsByTagName('RelativePath')[0].firstChild.replaceWholeText('/'.join(relative_path.split('/')[:-1]))
	fd.close()
	fd = open(pprfile,"w")
	fd.write(pprXML.toxml())
	fd.close()

	cmd = """def redtools_importonly():
	import pipeline.infrastructure.executeppr
	pipeline.infrastructure.executeppr.executeppr('""" + pprfile+ """', importonly=True)"""
	
	fd = open('redtools_importonly.casa.py', 'w')
	fd.write(cmd)
	fd.close()

	cmd = envcmd + ' ; xvfb-run -d ' + casacmd + ' -c "execfile(\'redtools_importonly.casa.py\');redtools_importonly();exit;"'
	l('Starting to run the command "' + cmd + '"')
	mylog.run(cmd)

	# daPermissions
	cmd = envcmd + ' ; daPermissions pipeline*'
	l('Starting to run the command "' + cmd + '"')
	mylog.run(cmd)
	
	# Get the latest version of analysis utils
	l('Get the latest version of analysis utils')
	cmd = envcmd + '; getAnalysisUtils'
	l('Starting to run the command "' + cmd + '"')
	if not unsupported:
		mylog.run(cmd)

	# Starting Legacy Fixes
	legacy_fixes_script = """def redtools_legacy_fixesCS():
	import glob
	from sys import path
	path.append('""" + dir_working + """AIV/science/analysis_scripts/')
	# Import ALMA stuff
	import analysisUtils as aU
	# Create an "alias" for analysis utils
	es = aU.stuffForScienceDataReduction()
	from recipes.almahelpers import fixsyscaltimes

	es = aU.stuffForScienceDataReduction()
	mslist = glob.glob('uid___A00*_X*_X*.ms')
	fd = open("casa_pipescript.py.txt", "w")
	
	for thisvis in mslist:
		print('Running fixes for ASDM ' + thisvis + '...')
		print('Running fixForCSV255...')
		es.fixForCSV2555(thisvis)
		print('Running fixsyscaltimes...')
		fixsyscaltimes(vis = thisvis)
		fd.write("    fixsyscaltimes(vis = '" + thisvis + "')")
		fd.write('# SACM/JAO - Fixes' + chr(10))
		SSOforfix = es.getFieldsForFixPlanets(thisvis)
		if (len(SSOforfix) > 0):
			print('Running fixplanets...')
			for ssofield in SSOforfix:
				fd.write("    fixplanets(vis = '" + thisvis + "', field = '" + str(ssofield) + "', fixuvw = T)")
				fd.write('# SACM/JAO - Fixes' + chr(10))
				fixplanets(vis = thisvis, field = str(ssofield), fixuvw = T)
	
		
	fd.close()"""

	fd = open("redtools_legacy_fixesCS.casa.py", "w")
	fd.write(legacy_fixes_script)
	fd.close()

	cmd = envcmd + ' ; ' + casacmd + ' -c "execfile(\'redtools_legacy_fixesCS.casa.py\');redtools_legacy_fixesCS();exit;"'
	l('Starting to run the command "' + cmd + '"')
	if not unsupported:
		mylog.run(cmd)

	# Starting routine to correct antenna positions
	correct_antenna_positions_script = """def redtools_correct_antenna_positions():
	import glob
	from sys import path
	path.append('""" + dir_working + """AIV/science/analysis_scripts/')
	# Import ALMA stuff
	import analysisUtils as aU
	# Create an "alias" for analysis utils
	es = aU.stuffForScienceDataReduction()
	mslist = glob.glob('uid___A00*_X*_X*.ms')
	print('Running es.correctMyAntennaPositions')
	es.correctMyAntennaPositions(mslist)"""

	fd = open('redtools_correct_antenna_positions.casa.py', 'w')
	fd.write(correct_antenna_positions_script)
	fd.close()

	cmd = envcmd + ' ; ' + casacmd + ' -c "execfile(\'redtools_correct_antenna_positions.casa.py\');redtools_correct_antenna_positions();exit;"'
	l('Starting to run the command "' + cmd + '"')
	if not unsupported:
		mylog.run(cmd)

	# Starting routine to update flux measurements on asdm-provided flux.csv file
	correct_flux_measurements_script = """def redtools_correct_flux_measurements():
	from sys import path
	path.append('""" + dir_working + """AIV/science/analysis_scripts/')
	# Import ALMA stuff
	import analysisUtils as aU
	# Create an "alias" for analysis utils
	es = aU.stuffForScienceDataReduction()
	print('Running aU.getALMAFluxcsv')
	aU.getALMAFluxcsv('flux.csv')"""

	fd = open('redtools_correct_flux_measurements.casa.py', 'w')
	fd.write(correct_flux_measurements_script)
	fd.close()

	cmd = envcmd + ' ; ' + casacmd + ' -c "execfile(\'redtools_correct_flux_measurements.casa.py\');redtools_correct_flux_measurements();exit;"'
	l('Starting to run the command "' + cmd + '"')
	if not unsupported:
		mylog.run(cmd)

	# Run the pipeline!!!!
	cmd = """def redtools_redPipeCS_PPR():
	import pipeline.infrastructure.executeppr
	pipeline.infrastructure.executeppr.executeppr('""" + pprfile+ """', importonly=False);exit;"""
	
	fd = open('redtools_redPipeCS_PPR.casa.py', 'w')
	fd.write(cmd)
	fd.close()

	cmd = envcmd + ' ; xvfb-run -d ' + casacmd + ' -c "execfile(\'redtools_redPipeCS_PPR.casa.py\');redtools_redPipeCS_PPR();exit;"'

	l('Starting to run the command "' + cmd + '"')
	mylog.run(cmd)

	# daPermissions
	cmd = envcmd + ' ; daPermissions pipeline*'
	l('Starting to run the command "' + cmd + '"')
	mylog.run(cmd)
	

	# Procedure to include fixes in casa_pipescript
	restore_script = glob(ppmr_dir + "/MOUS_uid___*/products/uid___*.casa_pipescript.py")[0]
	l("Starting the routine to add fixes to casa_pipescript file " + restore_script)

	fd = open(restore_script, "r")
	lines = fd.readlines()
	fd.close()
	
	fd = open("casa_pipescript.py.txt", "r")
	fixeslines = fd.readlines()
	fd.close()

	l("Fixes to be applied are: ")
	for f in fixeslines:
		l(f)

	newlines = list()
	newlines.append('from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes\n')
	for line in lines:
		newlines.append(line)
		if 'hifa_importdata' in line:
			newlines = newlines + fixeslines
			newlines.append("    h_save() # SACM/JAO - Finish weblog after fixes\n")
			newlines.append("    h_init() # SACM/JAO - Restart weblog after fixes\n")
			newlines.append(line)	
	fd = open(restore_script, "w")
	fd.writelines(newlines)
	fd.close()

	# Procedure to include fixes in casa_piperestorescript
	restore_script = glob(ppmr_dir + "/MOUS_uid___*/products/uid___*.casa_piperestorescript.py")[0]
	l("Starting the routine to add fixes to casa_piperestorescript file " + restore_script)

	fd = open(restore_script, "r")
	lines = fd.readlines()
	fd.close()
	
	fd = open("casa_pipescript.py.txt", "r")
	fixeslines = fd.readlines()
	fd.close()

	newlines = list()
	newlines.append('from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes\n')
	for line in lines:
		if 'hif_restoredata' in line:
			newlines.append(line.replace("hif_restoredata", "hifa_importdata").replace("'uid___", "'../rawdata/uid___").replace('vis=[', 'dbservice=False, bdfflags=False, vis=['))
			newlines = newlines + fixeslines
			newlines.append("    h_save() # SACM/JAO - Finish weblog after fixes\n")
			newlines.append("    h_init() # SACM/JAO - Restart weblog after fixes\n")
		newlines.append(line)

	# Perform the actual modification of casa_piperestorescript
	fd = open(restore_script, "w")
	fd.writelines(newlines)
	fd.close()

	## Rename the root plRun directory in case of a E2E project code
	if ('E2E' in ppmr_rel_dir):
		ppmr_rel_dir = ppmr_rel_dir.replace('E2E', '200')
		cmd = 'mv ' + scipipe_rootdir + '/' + ppmr_rel_dir + ' ' + scipipe_rootdir + '/' + ppmr_rel_dir.replace('E2E', '200')

	l("redPipeCS has finished :)")
	mylog.close()

main()
