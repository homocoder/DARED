#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class plrun:
	def __init__(self):
		# Intrinsec to class
		self.is_multi_sbs = False
		self.supported = True
		self.mous_uid = ''
		self.mous_fuid = ''
		self.eb_uid = list()
		self.eb_fuid = list()
		self.directory = '' # only directory name
		self.root_dir = '' # abspath
		self.identifier = '' # directory+mous_fuid+tstamp
		self.ppr_mode = False
		self.ppr_file = ''
		self.working_path  = ''
		self.products_path = ''
		self.rawdata_path  = ''
		self.cwd = ''
		self.mous_state = ''
		self.mous_substate = ''
		self.mous_state_transition_msg = ''

		#
		self.wrapper = None
		self.l = None # Just a convenient alias
		
		# Environment configuration
		self.user_id      = None
		self.node_id      = None
		self.log_dir      = None
		self.trash_dir    = None
		self.dataproc_dir = None
		self.products_dir = None
		self.spool_dir    = None
		self.env_cmd      = None
		self.casa_cmd     = None
		self.calPipeIF_intents   = None
		self.redPipeIF_intents   = None
		self.redPipeSD_intents   = None
		self.redPipeCS_intents   = None
		self.calPipeIF_procedure = None
		self.redPipeIF_procedure = None
		self.redPipeSD_procedure = None
		self.redPipeCS_procedure = None

	def chdir(self, cwd):
		from os import chdir
		chdir(cwd)
		self.cwd = cwd

	def run(self, step_name):
		from os import environ
		from datetime import datetime
		from pprint import pformat
		self.wrapper.log_buffer.append('Checking if step ' + step_name + ' is enabled.')
		env_key = 'REDTOOLS_FLAG_' + step_name
		if env_key in environ:
			self.l(env_key + '=' + "'" + environ[env_key] + "'")

			if 'True' in environ[env_key]:

				self.l('Step "' + step_name + '" is enabled.')
				self.l('Starting to run step "' + step_name + '".')
				try:
					eval('self.' + step_name + '()')
				except Exception as e:
					v = [(i, globals()[i]).__str__() + '\n' for i in globals()]
					v.sort()
					for j in v:
						self.l(j)

					self.mous_state = 'ProcessingProblem'
					self.mous_state_transition_msg = dict()
					self.mous_state_transition_msg['tstamp'] = datetime.now().isoformat()
					self.mous_state_transition_msg['step'] = step_name
					self.mous_state_transition_msg['hint'] = repr(e)
					if self.mous_substate == '':
						self.l('WARNING: XTSS MOUS Substate (PT label) is not set. Will not change State.')
					else:
						self.run('step_put_xtss_mous_state')

					self.l('Exception at step "' + step_name + '".')
					self.l('Exception is ' + repr(e))
					self.l('Dumping plrun object: ')
					self.l(pformat(self.__dict__, depth=2))

					self.l('Finished with errors :(')
					self.wrapper.close()
					raise
				self.l('Finished step "' + step_name + '".')
		else:
			self.l('Step "' + step_name + '" not enabled.')

	def step_environ_config(self):
		from os import environ 
		
		self.user_id      = environ['USER']
		self.node_id      = environ['HOSTNAME']
		self.log_dir      = environ['REDTOOLS_CONFIG_log_dir']
		self.trash_dir    = environ['REDTOOLS_CONFIG_trash_dir']
		self.dataproc_dir = environ['REDTOOLS_CONFIG_dataproc_dir']
		self.products_dir = environ['REDTOOLS_CONFIG_products_dir']
		self.spool_dir    = environ['REDTOOLS_CONFIG_spool_dir']
		self.env_cmd      = environ['REDTOOLS_CONFIG_env_cmd']
		self.casa_cmd     = environ['REDTOOLS_CONFIG_casa_cmd']
		self.asa_api      = environ['REDTOOLS_CONFIG_asa_api']
		self.calPipeIF_intents   = environ['REDTOOLS_CONFIG_calPipeIF_intents']
		self.redPipeIF_intents   = environ['REDTOOLS_CONFIG_redPipeIF_intents']
		self.redPipeSD_intents   = environ['REDTOOLS_CONFIG_redPipeSD_intents']
		self.redPipeCS_intents   = environ['REDTOOLS_CONFIG_redPipeCS_intents']
		self.calPipeIF_procedure = environ['REDTOOLS_CONFIG_calPipeIF_procedure']
		self.redPipeIF_procedure = environ['REDTOOLS_CONFIG_redPipeIF_procedure']
		self.redPipeSD_procedure = environ['REDTOOLS_CONFIG_redPipeSD_procedure']
		self.redPipeCS_procedure = environ['REDTOOLS_CONFIG_redPipeCS_procedure']

	def step_get_ppr(self):
		from subprocess import getoutput
		from glob import glob

		## Execute PipelineMakeRequest
		if self.ppr_mode: #TODO:test ppr_mode procedure
			self.directory = self.root_dir.split('/')[-1]
			cmd = 'grep OUSStatusRef ' + self.root_dir + self.ous_path + '/PPR_uid___*.xml'
			cmdoutput = getoutput(cmd)
			self.mous_uid = cmdoutput.split('"')[1]
			self.mous_fuid = self.mous_uid.replace('://', '___').replace('/', '_')
		else:
			cmd = self.env_cmd + ' ; getPPR ' + self.mous_uid + ' ' + self.intents + ' ' + self.procedure
			# Detect execution directory
			self.wrapper.run_shell(cmd)
			for i in self.wrapper.log_buffer:
				if 'Project root directory is' in i:
					self.directory     = i.split()[-1]
					self.root_dir      = self.dataproc_dir + '/' + self.directory
					self.ous_path      = glob(self.root_dir + self.ous_path)[-1]
					self.ous_path      = '/' + '/'.join(self.ous_path.split('/')[-3:])
					self.working_path  = self.root_dir + self.ous_path + '/working'
					self.rawdata_path  = self.root_dir + self.ous_path + '/rawdata'
					self.products_path = self.root_dir + self.ous_path + '/products'
					self.ppr_file      = glob(self.working_path + '/PPR_uid___*.xml')[-1]
						
		self.l('Project root directory is ' + self.root_dir)
		
	def step_get_ppr_rawdata(self):
		pass

	def step_get_asdm(self):
		cmd = 'getASDM --dir=' + self.root_dir
		self.wrapper.run_shell(cmd)
		
	def step_log_os_specs(self):
		pass

	def step_log_hw_specs(self):
		pass

	def step_log_shell_environment(self):
		cmd = self.env_cmd + '; env | sort '
		self.wrapper.run_shell(cmd)
	
	def step_log_os_environ(self):
		from os import environ
		for j in [(i, environ[i]).__str__() + '\n' for i in environ]:
			self.l(j) # los juimos

	def step_log_casa_environment(self):
		for j in [(i, globals()[i]).__str__() + '\n' for i in globals()]:
			self.l(j)

	def step_log_plrun_attributes(self):
		self.l("Running the pipeline for MOUS " + self.mous_uid + " as " + self.user_id + "@" + self.node_id)
		self.l("Pipeline execution absolute directory is " + self.root_dir)
		self.l("Pipeline execution relative directory is " + self.directory)
		self.l("Project code is " + self.directory[:14])
		
	def step_log_dependencies_specs(self):
		pass

	def step_rc_init_user_files(self):
		pass

	def step_self_test(self):
		#Based on information on specs, set self.supported accordingly
		pass
	
	def step_edit_ppr_eb(self):
		if len(self.eb_uid) == 0:
			self.l('No EBs were specified on command line. Assuming al EBs on PPR for this execution.')
			return(0)
		ebs_lines = list()
		for e in self.eb_uid:
			ebs_lines.append('                        <AsdmIdentifier>\n')
			ebs_lines.append('                            <AsdmRef>\n')
			ebs_lines.append('                                <ExecBlockId>' + e + '</ExecBlockId>\n')
			ebs_lines.append('                            </AsdmRef>\n')
			ebs_lines.append('                            <AsdmDiskName>' + e.replace('uid://', 'uid___').replace('/', '_') + '</AsdmDiskName>\n')
			ebs_lines.append('                        </AsdmIdentifier>\n')

		fd = open(self.ppr_file, 'r')
		lines = fd.readlines()
		fd.close()

		newlines = list()
		for line in lines:
			if not (('<ExecBlockId>' in line and '</ExecBlockId>' in line) or ('<AsdmRef>' in line or '</AsdmRef>' in line) or ('<AsdmIdentifier>' in line or '</AsdmIdentifier>' in line) or ('<AsdmDiskName>' in line and '</AsdmDiskName>' in line) ):
				newlines.append(line)
			if '<SBTitle>Undefined</SBTitle>' in line:
				newlines = newlines + ebs_lines
				
		fd = open(self.ppr_file, 'w')
		fd.writelines(newlines)
		fd.close()

	def step_edit_ppr_relative_path(self):
		pass

	def step_get_sacm_flagtemplate(self):
		pass

	def step_get_apa_qa0_flags(self):
		from requests.auth import HTTPBasicAuth
		from requests import get
		auth = HTTPBasicAuth('pipelineuser', 'P1p3Line')

		for e in self.eb_fuid:
			qa0_url  = self.asa_api + '/apa/service/api/qa0-cal-flags/'
			qa0_url += e
			self.l('qa0 flags URL is: ' + qa0_url)
			qa0_get = get(qa0_url, auth=auth)
			if qa0_get.status_code == 200 and qa0_get.ok:
				fd = open(e + '.flagtemplate.txt', 'a')
				fd.write(qa0_get.text)
				fd.close()
				qa0_get.close()
			else:
				self.l('Error when getting flagtemplates for EB ' + e)
				self.l('Error code is ', str(qa0_get.status_code))
				self.l('Reason is ', str(qa0_get.reason))				
				qa0_get.raise_for_status()
				qa0_get.close()
			
	def step_get_apa_qa2_flags(self):
		from requests.auth import HTTPBasicAuth
		from requests import get
		auth = HTTPBasicAuth('pipelineuser', 'P1p3Line')

		for e in self.eb_fuid:
			qa2_url  = self.asa_api + '/apa/service/api/qa2-cal-flags/'
			qa2_url += e
			qa2_get = get(qa2_url, auth=auth)
			if qa2_get.status_code == 200 and qa2_get.ok:
				fd = open(e + '.flagtemplate.txt', 'a')
				fd.write(qa2_get.text)
				fd.close()
				qa2_get.close()
			else:
				self.l('Error when getting flagtemplates for EB ' + e)
				self.l('Error code is ', str(qa2_get.status_code))
				self.l('Reason is ', str(qa2_get.reason))				
				qa2_get.raise_for_status()
				qa2_get.close()
				
	def step_legacy_fix_fixplanets(self):
		legacy_fixes_script = """def redtools_legacy_fix_fixplanets():
		import glob
		from sys import path
		path.append('""" + self.working_path + """/AIV/science/analysis_scripts/')
		# Import ALMA stuff
		import analysisUtils as aU
		# Create an "alias" for analysis utils

		es = aU.stuffForScienceDataReduction()
		mslist = glob.glob('uid___A00*_X*_X*.ms')
		fd = open("casa_pipescript.py.txt", "a")

		for thisvis in mslist:
			print('Running legacy_fix_fixplanets for EB ' + thisvis + '...')
			SSOforfix = es.getFieldsForFixPlanets(thisvis)
			if (len(SSOforfix) > 0):
				print('Running fixplanets...')
				for ssofield in SSOforfix:
					fd.write("    fixplanets(vis = '" + thisvis + "', field = '" + str(ssofield) + "', fixuvw = T)")
					fd.write('# SACM/JAO - Fixes' + chr(10))
					fixplanets(vis = thisvis, field = str(ssofield), fixuvw = T)		
		fd.close()"""

		fd = open("redtools_legacy_fix_fixplanets.casa.py", "w")
		fd.write(legacy_fixes_script)
		fd.close()

		cmd = self.env_cmd + ' ; ' + self.casa_cmd + ' -c "execfile(\'redtools_legacy_fix_fixplanets.casa.py\');redtools_legacy_fix_fixplanets();exit;"'
		self.wrapper.run_shell(cmd)

	def step_legacy_fix_fixsyscaltimes(self):
		legacy_fixes_script = """def redtools_legacy_fix_fixsyscaltimes():
		import glob
		from sys import path
		path.append('""" + self.working_path + """/AIV/science/analysis_scripts/')
		# Import ALMA stuff
		import analysisUtils as aU
		# Create an "alias" for analysis utils
		es = aU.stuffForScienceDataReduction()
		from recipes.almahelpers import fixsyscaltimes
		
		mslist = glob.glob('uid___A00*_X*_X*.ms')
		fd = open("casa_pipescript.py.txt", "a")

		for thisvis in mslist:
			print('Running fixsyscaltimes...')
			fixsyscaltimes(vis = thisvis)
			fd.write("    fixsyscaltimes(vis = '" + thisvis + "')")
			fd.write('# SACM/JAO - Fixes' + chr(10))
			
		fd.close()"""

		fd = open("redtools_legacy_fix_fixsyscaltimes.casa.py", "w")
		fd.write(legacy_fixes_script)
		fd.close()

		cmd = self.env_cmd + ' ; ' + self.casa_cmd + ' -c "execfile(\'redtools_legacy_fix_fixsyscaltimes.casa.py\');redtools_legacy_fix_fixsyscaltimes();exit;"'
		self.wrapper.run_shell(cmd)

	def step_legacy_csv2555(self):
		legacy_fixes_script = """def redtools_legacy_csv2555():
		import glob
		from sys import path
		path.append('""" + self.working_path + """/AIV/science/analysis_scripts/')
		# Import ALMA stuff
		import analysisUtils as aU
		# Create an "alias" for analysis utils

		es = aU.stuffForScienceDataReduction()
		mslist = glob.glob('uid___A00*_X*_X*.ms')
		fd = open("casa_pipescript.py.txt", "a")

		for thisvis in mslist:
			print('Running fixForCSV255...')
			es.fixForCSV2555(thisvis)
			
		fd.close()"""

		fd = open("redtools_legacy_csv2555.casa.py", "w")
		fd.write(legacy_fixes_script)
		fd.close()

		cmd = self.env_cmd + ' ; ' + self.casa_cmd + ' -c "execfile(\'redtools_legacy_csv2555.casa.py\');redtools_legacy_csv2555();exit;"'
		self.wrapper.run_shell(cmd)
    
	def step_fix_multi_sbs(self):
		pass

	def step_set_relative_path(self):
		pass

	def step_get_eb_on_ppr(self):
		from subprocess import getoutput
		cmd = "grep ExecBlockId " + self.root_dir + "/SOUS_uid___*/GOUS_uid___*/MOUS_uid___*/working/PPR_uid___*.xml"
		cmdoutput = getoutput(cmd)
		ebs = cmdoutput.replace("<ExecBlockId>", "").replace(" ", "").replace("</ExecBlockId>", "")
		self.eb_uid = ebs.split('\n')
		self.eb_fuid = [e.replace('://', '___').replace('/', '_') for e in self.eb_uid]

	def step_log_rawdata_on_disk(self):
		pass

	def step_da_permissions(self):
		cmd = self.env_cmd + ' ; daPermissions ' + self.cwd
		self.wrapper.run_shell(cmd)
		
	def step_execute_ppr_importonly(self):
		cmd = """def redtools_importonly():
		import pipeline.infrastructure.executeppr
		pipeline.infrastructure.executeppr.executeppr('""" + self.ppr_file + """', importonly=True)"""
	
		fd = open('redtools_importonly.casa.py', 'w')
		fd.write(cmd)
		fd.close()
	
		cmd = self.env_cmd + ' ; xvfb-run -d ' + self.casa_cmd + ' -c "execfile(\'redtools_importonly.casa.py\');redtools_importonly();exit;"'
		self.wrapper.run_shell(cmd)

	def step_get_analysis_utils(self):
		cmd = self.env_cmd + '; getAnalysisUtils'
		self.wrapper.run_shell(cmd)
		
	def step_update_flux_csv(self):
		update_flux_csv_script = """def redtools_update_flux_csv():
		from sys import path
		path.append('""" + self.working_path + """/AIV/science/analysis_scripts/')
		# Import ALMA stuff
		import analysisUtils as aU
		# Create an "alias" for analysis utils
		es = aU.stuffForScienceDataReduction()
		print('Running aU.getALMAFluxcsv')
		aU.getALMAFluxcsv('flux.csv')"""

		fd = open('redtools_update_flux_csv.casa.py', 'w')
		fd.write(update_flux_csv_script)
		fd.close()

		cmd = self.env_cmd + ' ; ' + self.casa_cmd + ' -c "execfile(\'redtools_update_flux_csv.casa.py\');redtools_update_flux_csv();exit;"'
		self.wrapper.run_shell(cmd)

	def step_update_antenna_positions_csv(self):
		update_antenna_positions_csv_script = """def redtools_update_antenna_positions_csv():
		import glob
		from sys import path
		path.append('""" + self.working_path + """/AIV/science/analysis_scripts/')
		# Import ALMA stuff
		import analysisUtils as aU
		# Create an "alias" for analysis utils
		es = aU.stuffForScienceDataReduction()
		mslist = glob.glob('uid___A00*_X*_X*.ms')
		print('Running es.correctMyAntennaPositions')
		es.correctMyAntennaPositions(mslist)"""

		fd = open('redtools_update_antenna_positions_csv.casa.py', 'w')
		fd.write(update_antenna_positions_csv_script)
		fd.close()
		
		cmd = self.env_cmd + ' ; ' + self.casa_cmd + ' -c "execfile(\'redtools_update_antenna_positions_csv.casa.py\');redtools_update_antenna_positions_csv();exit;"'
		self.wrapper.run_shell(cmd)

	def step_update_jyperk_csv(self):
		# Starting routine to get Jansky per Kelvin conversion factor
		get_jyperk_script = """def redtools_get_jyperk():
		import glob
		from sys import path
		path.append('""" + self.working_path + """/AIV/science/analysis_scripts/')
		# Import ALMA stuff
		import analysisUtils as aU
		# Create an "alias" for analysis utils
		es = aU.stuffForScienceDataReduction()
		mslist = glob.glob('uid___A00*_X*_X*.ms')
		print('Running es.getJyPerK')
		es.getJyPerK(mslist)"""
	
		fd = open('redtools_get_jyperk.casa.py', 'w')
		fd.write(get_jyperk_script)
		fd.close()

		cmd = self.env_cmd + ' ; ' + self.casa_cmd + ' -c "execfile(\'redtools_get_jyperk.casa.py\');redtools_get_jyperk();exit;"'
		self.wrapper.run_shell(cmd)

	def step_execute_ppr_from_ms_redPipeSD(self):
		cmd = """def redtools_execute_ppr_from_ms_redpipesd():
		import pipeline.infrastructure.executeppr
		pipeline.infrastructure.executeppr.executeppr('""" + self.ppr_file + """', importonly=False);exit;"""
	
		fd = open('redtools_execute_ppr_from_ms_redpipesd.casa.py', 'w')
		fd.write(cmd)
		fd.close()

		cmd = self.env_cmd + ' ; xvfb-run -d ' + self.casa_cmd + ' -c "execfile(\'redtools_execute_ppr_from_ms_redpipesd.casa.py\');redtools_execute_ppr_from_ms_redpipesd();exit;"'
		self.wrapper.run_shell(cmd)

	def step_execute_ppr_from_ms_redPipeIF(self):
		cmd = """def redtools_execute_ppr_from_ms_redpipeif():
		import pipeline.infrastructure.executeppr
		pipeline.infrastructure.executeppr.executeppr('""" + self.ppr_file + """', importonly=False);exit;"""
	
		fd = open('redtools_execute_ppr_from_ms_redpipeif.casa.py', 'w')
		fd.write(cmd)
		fd.close()

		cmd = self.env_cmd + ' ; xvfb-run -d ' + self.casa_cmd + ' -c "execfile(\'redtools_execute_ppr_from_ms_redpipeif.casa.py\');redtools_execute_ppr_from_ms_redpipeif();exit;"'
		self.wrapper.run_shell(cmd)

	def step_execute_ppr_from_ms_calPipeIF(self):
		cmd = """def redtools_execute_ppr_from_ms_calpipeif():
		import pipeline.infrastructure.executeppr
		pipeline.infrastructure.executeppr.executeppr('""" + self.ppr_file + """', importonly=False, bpaction='break');exit;"""
	
		fd = open('redtools_execute_ppr_from_ms_calpipeif.casa.py', 'w')
		fd.write(cmd)
		fd.close()

		cmd = self.env_cmd + ' ; xvfb-run -d ' + self.casa_cmd + ' -c "execfile(\'redtools_execute_ppr_from_ms_calpipeif.casa.py\');redtools_execute_ppr_from_ms_calpipeif();exit;"'
		self.wrapper.run_shell(cmd)

	def step_casa_pipescript_include_legacy_fixes(self):
		from glob import glob
		pipe_script = glob(self.products_path + '/uid___*.casa_pipescript.py')[0]
		self.l('Starting the routine to add fixes to casa_pipescript file ' + pipe_script)

		fd = open(pipe_script, 'r')
		lines = fd.readlines()
		fd.close()
	
		fd = open("casa_pipescript.py.txt", "r")
		fixeslines = fd.readlines()
		fd.close()

		self.l("Fixes to be applied are: ")
		for f in fixeslines:
			self.l(f)

		newlines = list()
		newlines.append('from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes\n')
		for line in lines:
			newlines.append(line)
			if 'hifa_importdata' in line:
				newlines = newlines + fixeslines
				newlines.append("    h_save() # SACM/JAO - Finish weblog after fixes\n")
				newlines.append("    h_init() # SACM/JAO - Restart weblog after fixes\n")
				newlines.append(line)
					
		fd = open(pipe_script, "w")
		fd.writelines(newlines)
		fd.close()

	def step_casa_restorepipescript_include_legacy_fixes(self):
		from glob import glob
		restore_script = glob(self.products_path + '/uid___*.casa_piperestorescript.py')[0]
		self.l("Starting the routine to add fixes to casa_piperestorescript file " + restore_script)

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

		self.l('Performing the actual modification of casa_piperestorescript')
		fd = open(restore_script, "w")
		fd.writelines(newlines)
		fd.close()

	def step_rename_e2e_root_dir(self):
		from glob import glob
		### Rename the root plRun directory in case of a E2E project code
		if ('E2E' in self.directory):
			cmd = 'mv ' + self.dataproc_dir + '/' + self.directory + ' ' + self.dataproc_dir + '/' + self.directory.replace('E2E', '200')
			self.directory = self.directory.replace('E2E', '200')
			self.root_dir      = self.dataproc_dir + '/' + self.directory
			self.working_path  = self.root_dir + self.ous_path + '/working'
			self.rawdata_path  = self.root_dir + self.ous_path + '/rawdata'
			self.products_path = self.root_dir + self.ous_path + '/products'
						
			self.wrapper.run_shell(cmd)

	def step_move_products_to_staging_apa(self):
		cmd = 'mkdir --parents ' + self.products_dir + '/' + '/'.join(self.products_path.split('/')[-5:-1])
		self.wrapper.run_shell(cmd)
		cmd = 'mv ' + self.products_path + ' ' + self.products_dir + '/' + '/'.join(self.products_path.split('/')[-5:-1])
		self.wrapper.run_shell(cmd)

	def step_move_working_to_spool_area(self):
		from shutil import move

		if self.mous_substate != 'ProcessingProblem':
			try:
				src = self.root_dir
				dst = self.root_dir + '.tospool'
				self.l('Move: src=' + src + ' dst=' + dst)
				move(src, dst)
				src = self.root_dir + '.tospool'
				dst =  self.spool_dir
				self.l('Move: src=' + src + ' dst=' + dst)
				move(src, dst)
				src = self.spool_dir + '/' + self.directory + '.tospool'
				dst =  self.spool_dir + '/' + self.directory
				self.l('Move: src=' + src + ' dst=' + dst)
				move(src, dst)
			except:
				self.l('WARNING: There was an error when moving the Pipeline run to spool area')
		
		#cmd = 'mkdir --parents ' + self.products_dir + '/' + '/'.join(self.products_path.split('/')[-5:-1])
		#self.wrapper.run_shell(cmd)
		#cmd = 'mv ' + self.products_path + ' ' + self.products_dir + '/' + '/'.join(self.products_path.split('/')[-5:-1])
		#self.wrapper.run_shell(cmd)

	def step_get_xtss_mous_state(self):
		from requests.auth import HTTPBasicAuth
		from requests import get
		auth = HTTPBasicAuth('pipelineuser', 'P1p3Line')
		cmd_path = '/xtss-rest-server/service/api/obs-unit-sets?state=Processing'

		xtss_url  = self.asa_api + cmd_path
		self.l('XTSS url to get is: ' + xtss_url)
		mous_state_get = get(xtss_url, auth=auth)
		self.l('XTSS status code id: ' + str(mous_state_get.status_code))

		if mous_state_get.status_code == 200:
				for i in mous_state_get.json():
					if self.mous_uid == i['ousStatusEntityId']:
						self.mous_state = i['state']
						self.mous_substate = i['substate']
						self.l('MOUS state is: ' + self.mous_state)
						self.l('MOUS substate is: ' + self.mous_substate)
						self.l(str(i))
		else:
			self.l('WARNING: Error getting the State and SubState from XTSS')

		if self.mous_state == '':
			self.l('WARNING: MOUS is not in state=Processing')

	def step_put_xtss_mous_state(self):
		from requests.auth import HTTPBasicAuth
		from requests import put
		from pprint import pformat
		auth = HTTPBasicAuth('pipelineuser', 'P1p3Line')

		cmd_path = '/xtss-rest-server/service/api/transition/obs-unit-set'

		xtss_url  = self.asa_api + cmd_path + '/' + self.mous_fuid
		self.l('XTSS url is: ' + xtss_url)

		payload = {'targetState': self.mous_state, 'targetSubstate': self.mous_substate, 'stateChangeComment': str(self.mous_state_transition_msg)}
		self.l('PUT Payload is: ' + pformat(payload))
		mous_state_put = put(xtss_url, data=payload, auth=auth)

		if mous_state_put.status_code == 200:
			self.l('XTSS PUT command ok. JSON output is: ' + pformat(mous_state_put.text))
		else:
			self.l('WARNING: XTSS PUT command error. JSON output is: ' + pformat(mous_state_put.text))

		self.l('MOUS state is: ' + self.mous_state)
		self.l('MOUS substate is: ' + self.mous_substate)
	
class wrapper:
	def __init__(self):
		self.print_flag = True
		self.log_filename     = ''
		self.log_fd     = None
		self.log_buffer     = list()
		
	def log_open(self, filename):
		self.log_fd = open(filename + '.log', 'w')
		
	def log(self, str):
		from datetime import datetime
		str = str.split("\n")
		
		for s in str:
			if self.print_flag:
				now = datetime.now().isoformat()
				print(now + ": " + s)
			
			if self.log_fd is None:
				self.log_buffer.append(s)
			else:
				self.log_buffer.reverse()
				while self.log_buffer != []:
					now = datetime.now().isoformat()
					b = self.log_buffer.pop()
					now = datetime.now().isoformat()
					self.log_fd.write(now + ': ' + b.__str__() + '\n')
					self.log_fd.flush()
					
				now = datetime.now().isoformat()					
				self.log_fd.write(now + ': ' + s + '\n')
				self.log_fd.flush()

	def run_shell(self, command):
		"""This procedure runs a command in background and logs the output line by line in real-time
		command: String containing the command to run."""
		
		from subprocess import Popen, PIPE, STDOUT
		from time import sleep
		from select import select
		from sys import exit

		self.log('Starting to run the shell command: "' + command + '"')

		try:
			proc = Popen(command, shell=True, bufsize=2, stdout=PIPE, stderr=STDOUT, universal_newlines=True)
		except:
			self.log('STDOUT + STDERR' + proc.read())

		for s in proc.stdout:
			self.log(s)
	
		proc.poll()
		proc.terminate()
		proc.kill()
		self.log('Return code of shell command is: ' + str(proc.returncode))
		if proc.returncode:
			raise Exception('Shell command output is <> 0')
		
	def close(self):
		if self.log_fd != None:
			self.log_fd.close()
