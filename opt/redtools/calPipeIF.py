#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def usage():
	print("\nUsage: calPipeIF [options]") 
	print("\nDescription: This script assists in the execution of the ALMA interferometric calibration pipeline.")
	print("\nOptions:")
	print("\t--mous=<mous_uid>       MOUS status uid to execute the pipeline.")
	print("\t--eb=<mous_uid>         Comma-separated EBs uid to use.")
	print("\t--dir=<path>            Absolute or relative path to the root of a pipeline execution to look for a PPR.")
	print("\t--env=<path>            Path to file to 'source' environment variables. Usage of this flag is not supported.")
	print("\t-h, --help              Show this help.")
	        
	print("\nExamples: ")
	print("\t* Execute the pipeline for a FullyObserved MOUS:")
	print("\t\tcalPipeIF --mous=uid://A002/X5ce05d/X6b\n")
	print('\t\tcalPipeIF --mous=uid://A001/X2fe/Xb1e --eb=uid://A002/Xb857f1/X29ec,uid://A002/Xb857f1/X990d\n')
	print("\t\tcalPipeIF --mous=uid://A002/X5ce05d/X6b --env=/opt/sacm/etc/c4r2\n")
	
def main():
	from redtools import plrun, wrapper
	from sys import argv, exit
	from getopt import getopt, GetoptError
	from datetime import datetime

	## Error codes
	#  1: Error in an execution step_*()
	#  2: Arguments and options parsing error.

	## Arguments and options parsing.
	if len(argv) == 1:
		usage()
		exit()
	try:
		opts, args = getopt(argv[1:], "medeh", ["mous=", "eb=", "dir=", "env=", "help"])
	except GetoptError as err: 
		usage()
		exit(2)

	## plrun and wrapper objects to use on this execution
	w = wrapper()
	p = plrun()
	p.mous_uid  = argv[1]
	p.wrapper = w
	p.l = p.wrapper.log
	
	## Arguments and options detection.
	for o, a in opts:
		if o in ("--mous="):
			p.mous_uid = a

		if o in ("--eb="):
			p.eb_uid = a.split(',')

		if o in ("--dir="):
			p.root_dir = abspath(a)
			p.pprmode = True

		if o in ("--env="):
			p.env_cmd = 'source ' + a
			p.supported = False

		if o in ("-h", "--help"):
			usage()
			exit(0)
	
	p.mous_fuid = p.mous_uid.replace('://', '___').replace('/', '_')
	p.ous_path = '/SOUS_uid___*/GOUS_uid___*/MOUS_uid___*'

	p.run('step_environ_config')
	p.intents   = p.calPipeIF_intents
	p.procedure = p.calPipeIF_procedure
	p.run('step_get_xtss_mous_state')
	p.run('step_log_shell_environment')
	p.run('step_get_ppr')
	p.run('step_edit_ppr_eb')
	p.run('step_get_eb_on_ppr')
	p.mous_fuid = p.mous_uid.replace("/", "_").replace(":", "_")
	p.identifier = p.directory.split('_')[0].replace('.', '_') + '.' + p.mous_fuid + '.' + p.directory[15:].replace('.', '_') + '.calPipeIF'
	p.wrapper.log_open(p.root_dir + '/' + p.identifier)

	p.run('step_log_os_environ')
	p.run('step_log_casa_environment')
	p.run('step_log_plrun_attributes')
	p.run('step_get_asdm')
	p.chdir(p.root_dir)
	p.run('step_da_permissions')
	p.chdir(p.working_path)
	p.run('step_execute_ppr_importonly')
	p.run('step_get_apa_qa0_flags')
	p.run('step_get_apa_qa2_flags')
	p.run('step_get_analysis_utils')
	p.run('step_update_antenna_positions_csv')
	p.run('step_update_flux_csv')
	p.run('step_da_permissions')	
	p.run('step_legacy_csv2555')
	p.run('step_legacy_fix_fixplanets')
	p.run('step_legacy_fix_fixsyscaltimes')

	p.run('step_execute_ppr_from_ms_calPipeIF')

	p.run('step_casa_pipescript_include_legacy_fixes')
	p.run('step_casa_restorepipescript_include_legacy_fixes')
	p.run('step_da_permissions')

	p.l('At this point it is considered a successfull Pipeline run')

	p.run('step_rename_e2e_root_dir')
	p.run('step_move_products_to_staging_apa')
	p.run('step_move_working_to_spool_area')
	p.l('calPipeIF has finished :)')
	
	#p.mous_state = 'ReadyForReview'
	#p.mous_state_transition_msg = dict()
	#p.mous_state_transition_msg['tstamp'] = datetime.now().isoformat()
	#p.mous_state_transition_msg['step'] = 'calPipeIF'
	#p.mous_state_transition_msg['hint'] = 'calPipeIF has finished :)'
	#p.run('step_put_xtss_mous_state')

	p.wrapper.close()

main()
