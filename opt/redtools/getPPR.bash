#!/bin/bash
java -Xmx4g -classpath "$ACSROOT/lib/jACSUtil.jar" "-Djava.endorsed.dirs=$ACSROOT/lib/endorsed:" -Duser.timezone=UTC -DACS.tmp="$ACSDATA/tmp" -DACS.data=$ACSDATA -DACS.loggingBin=false -Djava.system.class.loader=alma.acs.classloading.AcsSystemClassLoader -Dacs.system.classpath.jardirs="$ACSROOT/lib" -Dacs.system.path="$ACSROOT"  alma.pipelinescience.reqmanager.MakeProcessingRequests $@ '' false 



