import os
import sys
import subprocess
import string
import random
def run_script():

    bashfile=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    bashfile='/tmp/'+bashfile+'.sh'

    f = open(bashfile, 'w')
    s = """#!/bin/bash

    # COPYRIGHT NOTICE
    # Copyright @ 2012 CredenTek Software & Consultancy. All rights reserved.
    # These materials are confidential and proprietary to CredenTek Software and Consultancy and no part of these materials should be reproduced, published, transmitted #or distributed in any form or by any means, electronic, mechanical, photocopying, recording or otherwise, or stored in any information storage or retrieval system of #any nature nor should the materials be disclosed to third parties or used in any other manner for which this is not authorized, without the prior xpress written #authorization of CredenTek Software & Consultancy Pvt Ltd. */
    #/*                                                                 */
    #/*******************************************************************/
    # *
    # * Module Name         : FanTail-P
    # *
    # * File Name           : installFTPservice.sh
    # *
    # * Description         : Install service for non windows server
    # *
    # *            Version Control Block
    # *            ---------------------
    # * Date           Version     Author               Description
    # * ---------     --------  ---------------  ---------------------------
    # * NOV 16, 2012    1.0      Amit Agarwal         Base Version
    # * Jun 15, 2014    2.0      Mohd. Rahil          Modified for libmtsk.so.1
    # * May 15, 2020    3.0      Ashutosh        Modified for Java Agent 
    # **********************************************************************/
    # End Copyright

    #*************************************************************
    #FUNCTION NAME : Install_Service
    #DESCRIPTION   : Service Installation Steps
    #PARAMETERS    : username,group,ssl path,crypto path, exepath
    #*************************************************************

    #! /bin/sh
    Edit_Agentconfig()
    {

    cd $Exe_Path 	 
    chown $l_user:$l_group $Exe_Path/fantailp_$l_Cnt.jar
    chmod u+s  $Exe_Path/fantailp_$l_Cnt.jar
    chmod g+u  $Exe_Path/fantailp_$l_Cnt.jar
    chmod 6711 $Exe_Path/fantailp_$l_Cnt.jar

    echo Setting Log Path = $cur_dir/work/log ...
    
    echo 1 > option
    echo 1 >> option
    echo $cur_dir/work/log/>> option
    echo N >> option
    echo 0 >> option
    java -jar configurator.jar agentconfig.xml < option >> con_log

    echo Setting Log Format = fantailp.log ...

    echo 1 > option
    echo 2 >> option
    echo fantailp.log >> option
    echo N >> option
    echo 0 >> option
    java -jar configurator.jar agentconfig.xml < option >> con_log


    echo Setting Log LEVEL = RUN ...

    echo 1 > option
    echo 3 >> option
    echo RUN >> option
    echo N >> option
    echo 0 >> option
    java -jar configurator.jar agentconfig.xml < option >> con_log


    echo Setting PROCESSING Path = $cur_dir/work/processing ...

    echo 2 > option
    echo 1 >> option
    echo $cur_dir/work/processing/ >> option
    echo N >> option
    echo 0 >> option
    java -jar configurator.jar agentconfig.xml < option >> con_log


    echo Setting PROCESSED Path = $cur_dir/work/processed ...

    echo 2 > option
    echo 2 >> option
    echo $cur_dir/work/processed/>> option
    echo N >> option
    echo 0 >> option
    java -jar configurator.jar agentconfig.xml < option >> con_log


    echo Setting REJECT Path = $cur_dir/work/reject ...

    echo 2 > option
    echo 3 >> option
    echo $cur_dir/work/reject/>> option
    echo N >> option
    echo 0 >> option
    java -jar configurator.jar agentconfig.xml < option >> con_log


    echo Setting BIN Path ...

    echo 2 > option
    echo 4 >> option
    echo $cur_dir/bin/>> option
    echo N >> option
    echo 0 >> option
    java -jar configurator.jar agentconfig.xml < option >> con_log


    echo Setting Agent Name = AGNT ...

    echo 3 > option
    echo 1 >> option
    echo AGNT11.0>> option
    echo N >> option
    echo 0 >> option
    java -jar configurator.jar agentconfig.xml < option >> con_log


    echo Setting MODE = ONLINE ...

    echo 3 > option
    echo 2 >> option
    echo ONLINE>> option
    echo N >> option
    echo 0 >> option
    java -jar configurator.jar agentconfig.xml < option >> con_log


    echo No Of THREADS = 200 ...

    echo 3 > option
    echo 3 >> option
    echo 200 >> option
    echo N >> option
    echo 0 >> option
    java -jar configurator.jar agentconfig.xml < option >> con_log


    echo Setting ENCRYPTION KEY ...

    echo 4 > option
    echo 1 >> option
    echo AES>> option
    echo N >> option
    echo 0 >> option
    java -jar configurator.jar agentconfig.xml < option >> con_log

    echo 4 > option
    echo 2 >> option
    echo "PKCS #1 SHA-1 With RSA Encryption" >> option
    echo N >> option
    echo 0 >> option
    java -jar configurator.jar agentconfig.xml < option >> con_log


    echo 4	> option
    echo 3	>> option
    echo "Credentek Software and Consultancy Pvt ltd." >> option
    echo N >> option
    echo 0 >> option
    java -jar configurator.jar agentconfig.xml < option >> con_log


    echo 4 > option
    echo 4 >> option
    echo 1024 >> option
    echo N >> option
    echo 0 >> option
    java -jar configurator.jar agentconfig.xml < option >> con_log


    echo 4 > option
    echo 5 >> option
    echo N >> option
    echo 0 >> option
    java -jar configurator.jar agentconfig.xml < option >> con_log

    echo 5 > option
    echo 1 >> option
    echo 5051 >> option
    echo N >> option
    echo 0 >> option
    java -jar configurator.jar agentconfig.xml < option >> con_log

    rm con_log
    rm option
    }

    Create_stopsh()
    {
    echo "#!/bin/sh"  > stop.sh
    echo "#*******************************************************************/"  >> stop.sh
    echo "#*"  >> stop.sh
    echo "#  COPYRIGHT NOTICE"  >> stop.sh
    echo "#  Copyright @ 2012 CredenTek Software & Consultancy Pvt Ltd. All rights reserved."  >> stop.sh

    echo "#  These materials are confidential and proprietary to CredenTek and no part of these materials should be reproduced, published, transmitted or distributed in any form or by any means, electronic, mechanical, photocopying, recording or otherwise, or stored in any information storage or retrieval system of any nature nor should the materials be disclosed to third parties or used in any other manner for which this is not authorized, without the prior express written authorization of CredenTek Software & Consultancy Pvt Ltd*/ " >> stop.sh
    echo "#*                                                                 */ " >> stop.sh
    echo "#*******************************************************************/ " >> stop.sh

    echo "#********************************************************************** " >> stop.sh
    echo "#*" >> stop.sh
    echo "#* Module Name         :FanTail-P" >> stop.sh
    echo  "#*" >> stop.sh
    echo "#* File Name           :fantailp" >> stop.sh
    echo "#*" >> stop.sh
    echo "#* Description         : The stop.sh script use to stop java agent" >> stop.sh
    echo "#*" >> stop.sh
    echo "#*            Version Control Block" >> stop.sh
    echo "#*            ---------------------" >> stop.sh
    echo "#* Date           Version     Author               Description ">> stop.sh
    echo "#* ---------     --------  ---------------  --------------------------- ">> stop.sh
    echo "#* Sep 11 2012     1.0       Mohd Rahil            Base Version ">> stop.sh
    echo "#**********************************************************************/" >> stop.sh
    echo "# processname: stop.sh" >> stop.sh
    echo 'l_pid=`ps -ef | grep fantailp_'$l_Cnt'.jar | grep agentconfig.xml | awk {'\\''print ''$2'''\\''}`' >> stop.sh
    echo 'kill -9 $l_pid > /dev/null 2>&1' >> stop.sh
    }

    Create_startsh()
    {
    l_user=$1
    l_group=$2
    Exe_Path=$3

    echo "#!/bin/sh"  > start.sh 
    echo "#*******************************************************************/"  >> start.sh
    echo "#*"  >> start.sh 
    echo "#  COPYRIGHT NOTICE"  >> start.sh 
    echo "#  Copyright @ 2012 CredenTek Software & Consultancy Pvt Ltd. All rights reserved."  >> start.sh
    
    echo "#  These materials are confidential and proprietary to CredenTek and no part of these materials should be reproduced, published, transmitted or distributed in any form or by any means, electronic, mechanical, photocopying, recording or otherwise, or stored in any information storage or retrieval system of any nature nor should the materials be disclosed to third parties or used in any other manner for which this is not authorized, without the prior express written authorization of CredenTek Software & Consultancy Pvt Ltd*/ " >> start.sh
    echo "#*                                                                 */ " >> start.sh
    echo "#*******************************************************************/ " >> start.sh

    echo "#********************************************************************** " >> start.sh
    echo "#*" >> start.sh
    echo "#* Module Name         :FanTail-P" >> start.sh
    echo  "#*" >> start.sh
    echo "#* File Name           :fantailp" >> start.sh
    echo "#*" >> start.sh
    echo "#* Description         : The start.sh script use to start java agent" >> start.sh
    echo "#*" >> start.sh
    echo "#*            Version Control Block" >> start.sh
    echo "#*            ---------------------" >> start.sh
    echo "#* Date           Version     Author               Description ">> start.sh
    echo "#* ---------     --------  ---------------  --------------------------- ">> start.sh
    echo "#* Sep 11 2012     1.0       Mohd Rahil            Base Version ">> start.sh
    echo "#**********************************************************************/" >> start.sh
    echo "cd $Exe_Path" >> start.sh
    echo "java -jar fantailp_$l_Cnt.jar agentconfig.xml > /dev/null & " >> start.sh
    }
    #creating fantailp script
    Create_fantailp()
    {
    l_user=$1
    l_group=$2
    Exe_Path=$3
    l_fileName=fantailp$l_Cnt

    echo "#!/bin/sh"  > fantailp$l_Cnt
    echo "#*******************************************************************/"  >> fantailp$l_Cnt
    echo "#*"  >> fantailp$l_Cnt
    echo "#  COPYRIGHT NOTICE"  >> fantailp$l_Cnt
    echo "#  Copyright @ 2012 CredenTek Software & Consultancy Pvt Ltd. All rights reserved."  >> fantailp$l_Cnt
    
    echo "#  These materials are confidential and proprietary to CredenTek and no part of these materials should be reproduced, published, transmitted or distributed in any form or by any means, electronic, mechanical, photocopying, recording or otherwise, or stored in any information storage or retrieval system of any nature nor should the materials be disclosed to third parties or used in any other manner for which this is not authorized, without the prior express written authorization of CredenTek Software & Consultancy Pvt Ltd*/ " >> fantailp$l_Cnt
    echo "#*                                                                 */ " >> fantailp$l_Cnt
    echo "#*******************************************************************/ " >> fantailp$l_Cnt

    echo "#********************************************************************** " >> fantailp$l_Cnt
    echo "#*" >> fantailp$l_Cnt
    echo "#* Module Name         :FanTail-P" >> fantailp$l_Cnt
    echo  "#*" >> fantailp$l_Cnt
    echo "#* File Name           :fantailp" >> fantailp$l_Cnt
    echo "#*" >> fantailp$l_Cnt
    echo "#* Description         : The FanTailP Server provides Secure Remote File Transfer" >> fantailp$l_Cnt
    echo "#*" >> fantailp$l_Cnt
    echo "#*            Version Control Block" >> fantailp$l_Cnt
    echo "#*            ---------------------" >> fantailp$l_Cnt
    echo "#* Date           Version     Author               Description ">> fantailp$l_Cnt
    echo "#* ---------     --------  ---------------  --------------------------- ">> fantailp$l_Cnt
    echo "#* Sep 11 2012     1.0       Susanta Mishra       Base Version ">> fantailp$l_Cnt
    echo "#**********************************************************************/" >> fantailp$l_Cnt
    echo "# chkconfig: 2345 95 20" >> fantailp$l_Cnt
    echo "# description: Some description" >> fantailp$l_Cnt
    echo "# What your script does (not sure if this is necessary though)" >> fantailp$l_Cnt
    echo "# processname: fantailp" >> fantailp$l_Cnt
    echo set -e >> fantailp$l_Cnt

    echo umask 022 >> fantailp$l_Cnt

    echo "#. /lib/lsb/init-functions ">> fantailp$l_Cnt

    echo "# Are we running from init?" >> fantailp$l_Cnt

    echo "Exe_Path=$Exe_Path"  >> fantailp$l_Cnt
    echo "l_group=$l_group"  >> fantailp$l_Cnt
    echo "l_user=$l_user"  >> fantailp$l_Cnt
    echo ""  >> fantailp$l_Cnt
    
    echo "run_by_init() {" >> fantailp$l_Cnt
    echo '([ "$previous" ] && [ "$runlevel" ]) || [ "$runlevel" = S ]' >> fantailp$l_Cnt
    echo "}" >> fantailp$l_Cnt

    echo "check_dev_null() {" >> fantailp$l_Cnt
        echo "if [ ! -c /dev/null ]; then" >> fantailp$l_Cnt
        echo 'if [ "$1" = log_end_msg ]; then' >> fantailp$l_Cnt
            echo "log_end_msg 1 || true" >> fantailp$l_Cnt
        echo fi >> fantailp$l_Cnt
        echo "if ! run_by_init; then" >> fantailp$l_Cnt
            echo "log_action_msg /dev/null is not a character device!" >> fantailp$l_Cnt
        echo fi >> fantailp$l_Cnt
        echo "exit 1" >> fantailp$l_Cnt
        echo fi >> fantailp$l_Cnt
    echo "}" >> fantailp$l_Cnt


    echo "check_privsep_dir() {" >> fantailp$l_Cnt
        # Create the PrivSep empty dir if necessary >> fantailp
        echo "l_group=$l_group"  >> fantailp$l_Cnt
        echo "l_user=$l_user"  >> fantailp$l_Cnt
        echo "Exe_Path=$Exe_Path"  >> fantailp$l_Cnt

        echo 'if [ ! -d $Exe_Path/fantailpd'$l_Cnt' ]; then' >> fantailp$l_Cnt
        echo 'mkdir $Exe_Path/fantailpd'$l_Cnt >> fantailp$l_Cnt
            echo 'chmod 6777 $Exe_Path/fantailpd'$l_Cnt >> fantailp$l_Cnt
            echo 'chown $l_user:$l_group $Exe_Path/fantailpd'$l_Cnt >> fantailp$l_Cnt
        echo "fi" >> fantailp$l_Cnt

        echo 'if [ ! -f $Exe_Path/fantailpd'$l_Cnt'/fantailpd.pid ]; then' >> fantailp$l_Cnt
        echo 'touch $Exe_Path/fantailpd'$l_Cnt'/fantailpd.pid' >> fantailp$l_Cnt
            echo 'chmod 6777 $Exe_Path/fantailpd'$l_Cnt'/fantailpd.pid' >> fantailp$l_Cnt
            echo 'chown $l_user:$l_group $Exe_Path/fantailpd'$l_Cnt'/fantailpd.pid' >> fantailp$l_Cnt
        echo fi >> fantailp$l_Cnt
    echo "}" >> fantailp$l_Cnt

    # Hard Code user and group for each machine for which id agent has to be run. In case of esdte user userid and user group will be esdte and esdte. >> fantailp


    echo 'if [ -f $Exe_Path/fantail_test.log ]; then' >> fantailp$l_Cnt
    echo 'rm $Exe_Path/fantail_test.log' >> fantailp$l_Cnt
    echo fi >> fantailp$l_Cnt

    echo 'if [ ! -f $Exe_Path/fantail_test.log ]; then' >> fantailp$l_Cnt
        echo 'touch $Exe_Path/fantail_test.log' >> fantailp$l_Cnt
        echo 'chmod 777 $Exe_Path/fantail_test.log' >> fantailp$l_Cnt
        echo  'chown $l_user:$l_group $Exe_Path/fantail_test.log' >> fantailp$l_Cnt
    echo fi >> fantailp$l_Cnt

    #echo echo 'Step 1 >> $Exe_Path/fantail_test.log' >> fantailp$l_Cnt
    #echo echo 'Step 2 >> $Exe_Path/fantail_test.log' >> fantailp$l_Cnt
    #echo echo 'Step 55 >> $Exe_Path/fantail_test.log' >> fantailp$l_Cnt

    echo 'case "$1" in' >> fantailp$l_Cnt
    echo "start)" >> fantailp$l_Cnt
        echo check_privsep_dir >> fantailp$l_Cnt
        echo check_dev_null >> fantailp$l_Cnt
        echo 'l_pid=`ps -ef | grep fantailp_'$l_Cnt'.jar | grep agentconfig.xml | awk {'\\''print ''$2'''\\''}`' >> fantailp$l_Cnt
        echo 'if [ "$l_pid" = "" ]' >> fantailp$l_Cnt
        echo then	>> fantailp$l_Cnt
                
                    echo 'su - $l_user $Exe_Path/start.sh' >> fantailp$l_Cnt
                
                
            echo 'if [ $? = 0 ]' >> fantailp$l_Cnt
            echo then >> fantailp$l_Cnt
                echo "sleep 2;" >> fantailp$l_Cnt
                        echo 'echo Step 3 >> $Exe_Path/fantail_test.log' >> fantailp$l_Cnt
                echo 'echo `ps -ef | grep fantailp_'$l_Cnt'.jar | grep agentconfig.xml | awk {'\\''print ''$2'''\\''}` > $Exe_Path/fantailpd'$l_Cnt'/fantailpd.pid;' >> fantailp$l_Cnt
                echo "echo Starting Secure File Transfer Server FanTailPd          [OK];" >> fantailp$l_Cnt #process started successfully 
            echo else >> fantailp$l_Cnt
                echo "echo Starting Secure File Transfer Server FanTailPd          [FAIL];" >> fantailp$l_Cnt #process termined 
            echo fi >> fantailp$l_Cnt
        echo else >> fantailp$l_Cnt
            echo 'l_existpid=`cat $Exe_Path | head -1`' >> fantailp$l_Cnt    
                    echo 'echo "Step 44" >> $Exe_Path/fantail_test.log' >> fantailp$l_Cnt
            echo 'if [ "$l_existpid" = "$l_pid" ]' >> fantailp$l_Cnt
            echo then >> fantailp$l_Cnt
                echo "echo Starting Secure File Transfer Server FanTailPd          [FAIL1];" >> fantailp$l_Cnt # process is already exist
            echo else >> fantailp$l_Cnt
            echo 'echo $l_pid > $Exe_Path/fantailpd'$l_Cnt'/fantailpd.pid;' >> fantailp$l_Cnt
                echo "echo Starting Secure File Transfer Server FanTailPd          [FAIL];" >> fantailp$l_Cnt # mismatch current pid and existing pid >> fantailp
            echo fi  >> fantailp$l_Cnt
        echo fi >> fantailp$l_Cnt

        echo ";;" >> fantailp$l_Cnt
    echo "stop)" >> fantailp$l_Cnt
            echo "echo Stopping Secure File Transfer Server FanTailPd " >> fantailp$l_Cnt  #process is not started yet
            echo 'sh $Exe_Path/stop.sh' >> fantailp$l_Cnt
            
            echo 'if [ $? = 0 ]' >> fantailp$l_Cnt
            echo then >> fantailp$l_Cnt
                echo "sleep 2;" >> fantailp$l_Cnt
                        echo 'echo Step 33 >> $Exe_Path/fantail_test.log' >> fantailp$l_Cnt
                        echo "echo Stopping Secure File Transfer Server FanTailPd    [OK];" >> fantailp$l_Cnt #process stopped successfully 
            echo else >> fantailp$l_Cnt
                echo "Stopping Secure File Transfer Server          [FAILED];" >> fantailp$l_Cnt #process termined 
            echo fi >> fantailp$l_Cnt
        echo ";;" >> fantailp$l_Cnt
    echo "restart)" >> fantailp$l_Cnt
        echo check_privsep_dir >> fantailp$l_Cnt
            echo 'l_existpid=`cat $Exe_Path/fantailpd'$l_Cnt'/fantailpd.pid | head -1`' >> fantailp$l_Cnt    
            echo 'if [ "$l_existpid" = "" ]' >> fantailp$l_Cnt
            echo then >> fantailp$l_Cnt
            echo 'echo Step 7 >> $Exe_Path/fantail_test.log' >> fantailp$l_Cnt
            echo "echo Stopping Secure File Transfer Server FanTailPd          [FAIL];" >> fantailp$l_Cnt #process is not started yet
            echo "exit;" >> fantailp$l_Cnt
        echo else >> fantailp$l_Cnt 
            echo 'if kill -9 `cat $Exe_Path/fantailpd'$l_Cnt'/fantailpd.pid` > /dev/null 2>&1;' >> fantailp$l_Cnt
            echo then >> fantailp$l_Cnt
            echo 'echo Step 8 >> $Exe_Path/fantail_test.log' >> fantailp$l_Cnt
                echo 'echo "" > $Exe_Path/fantailpd'$l_Cnt'/fantailpd.pid;' >> fantailp$l_Cnt
                echo "echo Stopping Secure File Transfer Server FanTailPd          [OK];" >> fantailp$l_Cnt #process stopped successfully
            echo else >> fantailp$l_Cnt
                echo "echo Stopping Secure File Transfer Server FanTailPd          [FAIL];" >> fantailp$l_Cnt 
                echo "exit;" >> fantailp$l_Cnt
            echo fi >> fantailp$l_Cnt
        echo fi >> fantailp$l_Cnt

        echo check_dev_null >> fantailp$l_Cnt
        echo 'l_pid=`ps -ef | grep fantailp_'$l_Cnt'.jar | grep agentconfig.xml | awk {'\\''print ''$2'''\\''}`' >> fantailp$l_Cnt
        echo 'if [ "$l_pid" = "" ]' >> fantailp$l_Cnt
        echo then	>> fantailp$l_Cnt
            
                    echo 'su - $l_user $Exe_Path/start.sh' >> fantailp$l_Cnt
                    
            echo 'if [ $? = 0 ]' >> fantailp$l_Cnt
            echo then >> fantailp$l_Cnt
                echo "sleep 2;" >> fantailp$l_Cnt
                echo 'echo `ps -ef | grep fantailp_'$l_Cnt'.jar | grep agentconfig.xml | awk {'\\''print ''$2'''\\''}`' >> fantailp$l_Cnt
                echo "echo Starting Secure File Transfer Server FanTailPd          [OK];"  >> fantailp$l_Cnt #process started successfully
                echo 'l_pid=`ps -ef | grep fantailp_'$l_Cnt'.jar | grep agentconfig.xml | awk {'\\''print ''$2'''\\''}`' >> fantailp$l_Cnt
                echo 'echo $l_pid > $Exe_Path/fantailpd'$l_Cnt'/fantailpd.pid;' >> fantailp$l_Cnt
            echo else >> fantailp$l_Cnt
                echo "echo Starting Secure File Transfer Server FanTailPd          [FAIL];" >> fantailp$l_Cnt #process termined 
            echo fi >> fantailp$l_Cnt
        echo else >> fantailp$l_Cnt
            echo 'l_existpid=`cat $Exe_Path/fantailpd'$l_Cnt'/fantailpd.pid | head -1`' >> fantailp$l_Cnt    
            echo 'if [ "$l_existpid" = "$l_pid" ]' >> fantailp$l_Cnt
            echo then >> fantailp$l_Cnt
                echo "echo Starting Secure File Transfer Server FanTailPd          [FAIL];" >> fantailp$l_Cnt # process is already exist
            echo else >> fantailp$l_Cnt
            echo 'echo $l_pid > $Exe_Path/fantailpd'$l_Cnt'/fantailpd.pid;' >> fantailp$l_Cnt
                echo "echo Starting Secure File Transfer Server FanTailPd          [FAIL];" >> fantailp$l_Cnt # mismatch current pid and existing pid
            echo fi  >> fantailp$l_Cnt
        echo fi >> fantailp$l_Cnt
        echo ";;" >> fantailp$l_Cnt

    echo "status)" >> fantailp$l_Cnt

        echo 'l_pid=`ps -ef | grep fantailp_'$l_Cnt'.jar | grep agentconfig.xml | awk {'\\''print ''$2'''\\''}`' >> fantailp$l_Cnt 
        echo 'if [ "$l_pid" = "" ]' >> fantailp$l_Cnt
            echo then >> fantailp$l_Cnt
            echo echo "FanTailP Process is stopped;" >> fantailp$l_Cnt
        echo else >> fantailp$l_Cnt
            echo echo "FanTailP Process is running;" >> fantailp$l_Cnt
        echo fi >> fantailp$l_Cnt
        echo ";;" >> fantailp$l_Cnt

    echo "*)" >> fantailp$l_Cnt
        echo check_privsep_dir >> fantailp$l_Cnt
        echo check_dev_null >> fantailp$l_Cnt
        echo 'l_pid=`ps -ef | grep fantailp_'$l_Cnt'.jar | grep agentconfig.xml | awk {'\\''print ''$2'''\\''}`' >> fantailp$l_Cnt
        echo 'if [ "$l_pid" = "" ]' >> fantailp$l_Cnt
        echo then >> fantailp$l_Cnt
            
                    echo "sh - $l_user $Exe_Path/start.sh" >> fantailp$l_Cnt
                    echo 'if [ $? = 0 ]' >> fantailp$l_Cnt
            echo then >> fantailp$l_Cnt
                echo 'sleep 2;' >> fantailp$l_Cnt
                        echo 'echo Step 3 >> $Exe_Path/fantail_test.log' >> fantailp$l_Cnt
                echo 'echo `ps -ef | grep fantailp_'$l_Cnt'.jar | grep agentconfig.xml | awk {'\\''print ''$2'''\\''}` > $Exe_Path/fantailpd'$l_Cnt'/fantailpd.pid;' >> fantailp$l_Cnt
                echo "echo Starting Secure File Transfer Server FanTailPd          [OK];" >> fantailp$l_Cnt #process started successfully
            echo else >> fantailp$l_Cnt
                echo "echo Starting Secure File Transfer Server FanTailPd          [FAIL];" >> fantailp$l_Cnt #process termined 
            echo fi >> fantailp$l_Cnt
        echo else >> fantailp$l_Cnt
            echo 'l_existpid=`cat $Exe_Path/fantailpd'$l_Cnt'/fantailpd.pid | head -1`'>> fantailp$l_Cnt    
                    echo 'echo Step 4 >> $Exe_Path/fantail_test.log' >> fantailp$l_Cnt
            echo 'if [ "$l_existpid" = "$l_pid" ]' >> fantailp$l_Cnt
            echo then >> fantailp$l_Cnt
                echo "echo Starting Secure File Transfer Server FanTailPd          [FAIL1];" >> fantailp$l_Cnt # process is already exist
            echo else >> fantailp$l_Cnt
            echo 'echo $l_pid > $Exe_Path/fantailpd'$l_Cnt'/fantailpd.pid;' >> fantailp$l_Cnt
                echo  "echo Starting Secure File Transfer Server FanTailPd          [FAIL];" >> fantailp$l_Cnt # mismatch current pid and existing pid
            echo fi  >> fantailp$l_Cnt
        echo fi >> fantailp$l_Cnt

        echo ";;" >> fantailp$l_Cnt
    echo esac >> fantailp$l_Cnt

    echo "exit 0" >> fantailp$l_Cnt
    mv `pwd`/fantailp$l_Cnt $Exe_Path

    chown $l_user:$l_group $Exe_Path/fantailp$l_Cnt
    chmod u+s  $Exe_Path/fantailp$l_Cnt
    chmod g+u  $Exe_Path/fantailp$l_Cnt
    chmod 6711 $Exe_Path/fantailp$l_Cnt

    }
    Install_Service()
    {
        l_user=$1
        l_group=$2
    #a	l_pathssl=$3
        #aif [ $l_osName = Linux_64_bit ] || [ $l_osName = Linux_32_bit ] || [ $l_osName = Solaris_sparc_64_bit ] || [ $l_osName = Solaris_sparc_32_bit ];
        #athen 	
        #al_pathcrypt=$3
        #aExe_Path=$4
        #aelse 
        Exe_Path=$3
    #aa	fi

        echo "-----------------------------------------Service Details-------------------------------------------"
        echo "USERNAME                           : $l_user"
        echo "GROUP                              : $l_group"
    #a	echo "PATH FOR SSL .SO FILES             : $l_pathssl"
        #if [ $l_osName = Linux_64_bit ] || [ $l_osName = Linux_32_bit ] || [ $l_osName = Solaris_sparc_64_bit ] || [ $l_osName = Solaris_sparc_32_bit ];
            #then
        #echo "PATH FOR CRYPTO .SO FILES          : $l_pathcrypt"
        #fi
        echo "BIN PATH                           : $Exe_Path"
        echo "---------------------------------------------------------------------------------------------------"

    # for root user service_installation

    if [ $l_installChoice = 1 ]; then
        echo user  : $l_user > INSTALL_"$l_osName"_SERVICE.LOG
        echo group : $l_group >> INSTALL_"$l_osName"_SERVICE.LOG
            chmod 755 INSTALL_"$l_osName"_SERVICE.LOG

    #	echo "Step : 1" >> INSTALL_"$l_osName"_SERVICE.LOG

        # if [ -d /lib/64 ]; then
        #cp $Exe_Path/lib/libcrypto.so* /lib/64/ //Add by Rahil suggested by vagesh sir
        #cp $Exe_Path/lib/libcrypto* /lib/64/
        # fi

        #cp $Exe_Path/lib/libcrypto.so* /usr/lib/ 
        #//Add by Rahil suggested by vagesh sir
        #cp $Exe_Path/lib/libcrypto* /usr/lib/
        #echo "Copying library to /usr/lib/" >> INSTALL_"$l_osName"_SERVICE.LOG

    #a	echo "* * * * Copying libssl.so* to /lib/64 * * * *" >> INSTALL_"$l_osName"_SERVICE.LOG
    #a	echo "* * * * Copying libcrypto.so* to /lib/64 * * * *" >> INSTALL_"$l_osName"_SERVICE.LOG

    #a	cp $l_pathssl/libssl.so* /lib/64
        #a if [ $l_osName = Linux_64_bit ] || [ $l_osName = Linux_32_bit ] || [ $l_osName = Solaris_sparc_64_bit ] || [ $l_osName = Solaris_sparc_32_bit ];
            #a then
        #a cp $l_pathcrypt/libcrypto.so* /lib/64
        #a fi

        echo "Step : 1" >> INSTALL_"$l_osName"_SERVICE.LOG
        if [ $l_osName = Linux_64_bit ] || [ $l_osName = Linux_32_bit ] || [ $l_osName = Solaris_sparc_64_bit ] || [ $l_osName = Solaris_sparc_32_bit ] || [ $l_osName = Red_hat_32_bit ] || [ $l_osName = Solaris_amd_64_bit ] || [ $l_osName = Red_hat_64_bit ] || [ $l_osName = CentOs_32_bit ];
        then
        echo "* * * * copying fantail /etc/init.d/ * * * *" >> INSTALL_"$l_osName"_SERVICE.LOG
            ln -s $Exe_Path/fantailp$l_Cnt /etc/init.d/fantailp$l_Cnt
        chown -h $l_user:$l_group /etc/init.d/fantailp$l_Cnt
        # for AIX_64_bit
        elif [ $l_osName = AIX_64_bit ]
        then
        echo "* * * * copying fantailp /etc/rc.d/init.d * * * *" >> INSTALL_"$l_osName"_SERVICE.LOG
            ln -s $Exe_Path/fantailp$l_Cnt /etc/rc.d/init.d/fantailp$l_Cnt
        chown -h $l_user:$l_group /etc/rc.d/init.d/fantailp$l_Cnt 
        else
        # for HP_64_bit
        echo "* * * * copying fantail /sbin/init.d * * * *" >> INSTALL_"$l_osName"_SERVICE.LOG
            ln -s $Exe_Path/fantailp /sbin/init.d/fantailp$l_Cnt
        chown -h $l_user:$l_group /sbin/init.d/fantailp$l_Cnt 

        fi
            
        echo "Step : 2" >> INSTALL_"$l_osName"_SERVICE.LOG
        if [ $l_osName = Linux_64_bit ] || [ $l_osName = Linux_32_bit ] || [ $l_osName = Solaris_sparc_64_bit ] || [ $l_osName = Solaris_sparc_32_bit ] || [ $l_osName = Red_hat_32_bit ]  || [ $l_osName = Solaris_amd_64_bit ] ||  [ $l_osName = Red_hat_64_bit ] || [ $l_osName = CentOs_32_bit ];
        then
        echo "* * * * Creating SoftLink of /etc/init.d/fantailp$l_Cnt/ /etc/rc2.d/S02fantailp$l_Cnt * * * *" >> INSTALL_"$l_osName"_SERVICE.LOG
        ln -s /etc/init.d/fantailp$l_Cnt /etc/rc2.d/S02fantailp$l_Cnt
        chown -h $l_user:$l_group /etc/rc2.d/S02fantailp$l_Cnt 
            chmod 755 /etc/rc2.d/S02fantailp$l_Cnt

        elif [ $l_osName = AIX_64_bit ]
        then
        echo "* * * * Creating SoftLink of /etc/init.d/fantailp$l_Cnt/ /etc/rc.d/rc2.d/Sfantailp$l_Cnt * * * *" >> INSTALL_"$l_osName"_SERVICE.LOG
            ln -s /etc/rc.d/init.d/fantailp$l_Cnt /etc/rc.d/rc2.d/Sfantailp$l_Cnt
        chown -h $l_user:$l_group /etc/rc.d/rc2.d/Sfantailp$l_Cnt 
            chmod 755 /etc/rc.d/rc2.d/Sfantailp$l_Cnt
        else
        # for HP_64_bit
        echo "* * * * Creating SoftLink of /sbin/init.d/fantailp$l_Cnt /sbin/rc2.d/Sfantailp$l_Cnt * * * *" >> INSTALL_"$l_osName"_SERVICE.LOG
            ln -s /sbin/init.d/fantailp$l_Cnt /sbin/rc2.d/Sfantailp$l_Cnt
        chown -h $l_user:$l_group /sbin/rc2.d/Sfantailp$l_Cnt
            chmod 755 /sbin/rc2.d/Sfantailp$l_Cnt

        fi

            if [ -d $Exe_Path/fantailpd$l_Cnt ]; then
            rm -rf $Exe_Path/fantailpd$l_Cnt
            fi

        echo "Step : 3" >> INSTALL_"$l_osName"_SERVICE.LOG
        echo "* * * * Making Dir fantailpd directory in /var/run * * * *" >> INSTALL_"$l_osName"_SERVICE.LOG
        mkdir $Exe_Path/fantailpd$l_Cnt

        echo "* * * * changing mode of /var/run/fantailpd$l_Cnt  * * * *" >> INSTALL_"$l_osName"_SERVICE.LOG
            chown $l_user:$l_group $Exe_Path/fantailpd$l_Cnt
            
            chmod 6777 $Exe_Path/fantailpd$l_Cnt

        echo "Step : 4" >> INSTALL_"$l_osName"_SERVICE.LOG
        echo "* * * * Making Dir /usr/share/fantailp$l_Cnt * * * *" >> INSTALL_"$l_osName"_SERVICE.LOG
        mkdir /usr/share/fantailp$l_Cnt

        echo "Step : 5" >> INSTALL_"$l_osName"_SERVICE.LOG
        echo "* * * * Creating SoftLink of agentconfig.xml to /usr/share/fantailp$l_Cnt/agentconfig.xml * * * *" >> INSTALL_"$l_osName"_SERVICE.LOG
        ln -s $Exe_Path/agentconfig.xml  /usr/share/fantailp$l_Cnt/agentconfig.xml
        chown -h $l_user:$l_group /usr/share/fantailp$l_Cnt/agentconfig.xml
        echo "Step : 6" >> INSTALL_"$l_osName"_SERVICE.LOG
        echo "* * * * Creating SoftLink of fantailp.jar to /usr/share/fantailp$l_Cnt/fantailp.jar * * * *" >> INSTALL_"$l_osName"_SERVICE.LOG
        ln -s $Exe_Path/fantailp_$l_Cnt.jar  /usr/sbin/fantailp$l_Cnt
        chown -h $l_user:$l_group /usr/sbin/fantailp$l_Cnt
            
        echo "Step : 7. Service Successfull" >> INSTALL_"$l_osName"_SERVICE.LOG
        chown $l_user:$l_group INSTALL_"$l_osName"_SERVICE.LOG
        chmod u+s  INSTALL_"$l_osName"_SERVICE.LOG
        chmod g+u  INSTALL_"$l_osName"_SERVICE.LOG
        chmod 6711 INSTALL_"$l_osName"_SERVICE.LOG 
    fi


    }

    Install ()
    {

            if [ $l_installChoice = 1 ]
            then
            Exe_Path=`pwd`/bin

                if [ -d $Exe_Path ];then
            Install_Service $l_user $l_group $Exe_Path
                else
                echo "It seems that bin area is not present. Agent setup not installed earlier, Can't create service. Please install agent first using normal user"
                fi

                exit
            fi       
        mkdir `pwd`/bin
            chmod 6777 `pwd`/bin
            chown $l_user:$l_group `pwd`/bin
        
        tar xvf Packages.tar
        chmod 6777 `pwd`/Packages 
        chown $l_user:$l_group `pwd`/Packages
        
        cp -r `pwd`/Packages/* `pwd`/bin/
        rm -r Packages

        mv `pwd`/bin/fantailp.jar `pwd`/bin/fantailp_$l_Cnt.jar

        mkdir `pwd`/work
        chmod 6777 `pwd`/work
        chown $l_user:$l_group `pwd`/work
        mkdir `pwd`/work/processing
        chmod 6777 `pwd`/work/processing
        chown $l_user:$l_group `pwd`/work/processing
        mkdir `pwd`/work/processed
        chmod 6777 `pwd`/work/processed
        chown $l_user:$l_group `pwd`/work/processed
        mkdir `pwd`/work/reject
        chmod 6777 `pwd`/work/reject
        chown $l_user:$l_group `pwd`/work/reject
        mkdir `pwd`/work/log
        chmod 6777 `pwd`/work/log
        chown $l_user:$l_group `pwd`/work/log
        
        Exe_Path=`pwd`/bin

        chmod 6777 `pwd`/bin/* 
        chown $l_user:$l_group `pwd`/bin/*
        Create_startsh $l_user $l_group $Exe_Path
        mv `pwd`/start.sh $Exe_Path/
        chown $l_user:$l_group $Exe_Path/start.sh
        chmod u+s  $Exe_Path/start.sh
        chmod g+u  $Exe_Path/start.sh
        chmod 6711 $Exe_Path/start.sh
        
        Create_stopsh $l_user $l_group $Exe_Path
        mv `pwd`/stop.sh $Exe_Path/
        chown $l_user:$l_group $Exe_Path/stop.sh
        chmod u+s $Exe_Path/stop.sh
        chmod g+u $Exe_Path/stop.sh
        chmod 6711 $Exe_Path/stop.sh
            Create_fantailp $l_user $l_group $Exe_Path
            echo "Editing agentconfig.xml . . ."
            cur_dir=`pwd`
            echo "Printing Current Directory"	
            echo $cur_dir
            echo "Calling Agentconfig"
            Edit_Agentconfig

            echo "Installing Service . . . "

    }


    echo "Please select option to install service or agent"
    echo "1) Install only service as a root user"
    echo "2) Install agent as a normal user"
    read l_installChoice
    echo "you have select the option:"$l_installChoice

    if [ $l_installChoice = 1 ];
    then 

        #longID=$(id)
        #shortID=${longID:0:5}
        
        #if [ $shortID == "uid=0" ];
        #if [ "$(id -u)" = 0 ];
        #if [ "$(id | cut -c1-5)" = uid=0 ];
        l_id=`id | cut -c1-5`
        if [ "$l_id" = "uid=0" ];
        then
        #echo "################# Start to Remove Previous Install FTP Service  ######################" 
        #rm /etc/init.d/fantailp$l_Cnt
        #rm /etc/rc2.d/S02fantailp$l_Cnt
        #rm /etc/rc.d/init.d/fantailp$l_Cnt
        #rm /etc/rc.d/rc2.d/Sfantailp$l_Cnt
        #rm /sbin/init.d/fantailp$l_Cnt
        #rm /sbin/rc2.d/Sfantailp$l_Cnt
        #rm -r /usr/share/fantailp$l_Cnt
        #rm /usr/sbin/fantailp$l_Cnt
        #echo "################# Removed Previous Install FTP Service  ######################" 
        echo "You are a root user please proceed"
        else
        echo "You are not a root user"
        echo "Please select the option: 2"
        exit 1;		
        fi
        
    #fi

    elif [ $l_installChoice = 2 ]
    then

        #longID=$(id)
        #shortID=${longID:0:5}
        
        #if [ $shortID == "uid=0" ];
            #if [ "$(id -u)" = 0 ];
        #if [ "$(id | cut -c1-5)" == "uid=1" ];
        l_id=`id | cut -c1-5`
        if [ "$l_id" = "uid=0" ];
            then
        echo "You are a root user"
        echo "Please select the option: 1"
        exit 1;
        fi
    else 
        echo "Please select the correct choice." 
        exit 1;
    fi

    #echo "################# Creating FTP Service  ######################" 
    echo " **************** Please Input the Following Information********************* "
    echo "Please enter the User And Group to which service will belong"
    echo "Note: You can use Command - id [username] For eg. id fantailp to get all the information(group,uid etc ) for fantailp user "
    echo "ENTER USER : "
    read l_user

    id $l_user

    echo "ENTER GROUP : "
    read l_group

    echo "Enter Agent Installation Count : "
    read l_Cnt


    if [ $l_installChoice = 1 ];
    then 
        echo "################# Start to Remove Previously Installed FTP Service  ######################" 
        rm /etc/init.d/fantailp$l_Cnt
        rm /etc/rc2.d/S02fantailp$l_Cnt
        rm /etc/rc.d/init.d/fantailp$l_Cnt
        rm /etc/rc.d/rc2.d/Sfantailp$l_Cnt
        rm /sbin/init.d/fantailp$l_Cnt
        rm /sbin/rc2.d/Sfantailp$l_Cnt
        rm -r /usr/share/fantailp$l_Cnt
        rm /usr/sbin/fantailp$l_Cnt
        echo "################# Removed Previously Installed FTP Service  ######################" 
        echo "################# Creating FTP Service  ######################" 
    fi

    echo "Please select the OS of your machine"
    echo "1) Ubuntu 64 bit"
    echo "2) Ubuntu 32 bit"
    echo "3) Solaris sparc 64 bit"
    echo "4) Solaris sparc 32 bit"
    echo "5) AIX 64 bit"
    echo "6) HP 64 bit"
    echo "7) Red hat 32 bit"
    echo "8) Solaris amd 64 bit"
    echo "9) Red hat 64 bit"
    echo "10) CentOs 32 bit"
    read l_osChoice
    echo "you have select the choice:"$l_osChoice

    if [ $l_osChoice = 1 ]
    then 
    #	[ "$(command | pipeline)" = 1 ]
        if [ "$(uname -a | grep -E 'Linux.*Ubuntu.*x86_64')" ]
        then 
        echo "you are working on Linux Ubuntu 64 bit"
        l_osName="Linux_64_bit"
        Install
        else
        echo "Your os type is not compatible"
        echo "Your OS configuration is:"
            echo "$(uname -a)"
        l_osName="Linux_64_bit"
            echo "Do you want to try it forcefully,It may not work, Please speak to support team before going ahead." 
            echo "Enter 1 to forcefully go ahead  and any other key to stop installation"
            read l_forcechoice
            if [ $l_forcechoice = 1 ]
            then
                Install
            fi    
        fi

    elif [ $l_osChoice = 2 ]
    then
        if [ "$(uname -a | grep -E 'Linux.*i386|i386.*Linux')" ]
        then
        echo "you are working on Linux Ubuntu 32 bit"
        l_osName="Linux_32_bit"
            Install
        else
        echo "your os type is not compatible"
        echo "Your OS configuration is:"
            echo "$(uname -a)"
        l_osName="Linux_32_bit"
            echo "Do you want to try it forcefully, It may not work, please speak to support team before going ahead." 
            echo "Enter 1 to forcefully go ahead  any other key to stop installation"
            read l_forcechoice
            if [ $l_forcechoice = 1 ]
            then
                Install
            fi    
        fi

    elif [ $l_osChoice = 3 ]
    then
        if [ "$(isainfo -b | grep 64)" ]
        then
        echo "you are working on Solaris sparc 64 bit"
        l_osName="Solaris_sparc_64_bit"
        Install	
        else
        echo "your os type is not compatible"
        echo "Your OS configuration is:"
            echo "$(uname -a)"
        l_osName="Solaris_sparc_64_bit"
            echo "Do you want to try it forcefully, It may not work, please speak to support team before going ahead." 
            echo "Enter 1 to forcefully go ahead  any other key to stop installation"
            read l_forcechoice
            if [ $l_forcechoice = 1 ]
            then
                Install
            fi    

        fi

    elif [ $l_osChoice = 4 ]
    then
        if [ "$(isainfo -b | grep 32)" ]
        then
        echo "you are working on Solaris sparc 32 bit"
        l_osName="Solaris_sparc_32_bit"
        Install
        else
        echo "your os type is not compatible"
        echo "Your OS configuration is:"
            echo "$(uname -a)"
        l_osName="Solaris_sparc_32_bit"
            echo "Do you want to try it forcefully, It may not work, please speak to support team before going ahead." 
            echo "Enter 1 to forcefully go ahead  any other key to stop installation"
            read l_forcechoice
            if [ $l_forcechoice = 1 ]
            then
                Install
            fi    
        fi

    elif [ $l_osChoice = 5 ]
    then
        if [ "$(getconf KERNEL_BITMODE | grep 64)" ]
        then
        echo "you are working on AIX 64 bit "
        l_osName="AIX_64_bit"
        Install
        else
        echo "your os type is not compatible"
        echo "Your OS configuration is:"
            echo "$(uname -a)"
        l_osName="AIX_64_bit"
            echo "Do you want to try it forcefully, It may not work, please speak to support team before going ahead." 
            echo "Enter 1 to forcefully go ahead  any other key to stop installation"
            read l_forcechoice
            if [ $l_forcechoice = 1 ]
            then
                Install
            fi    
        fi
    elif [ $l_osChoice = 6 ]
    then
        if [ "$(getconf KERNEL_BITS)" ]
        then
        echo "you are working on HP 64 bit"
        l_osName="HP_64_bit"
        Install
        else
        echo "your os type is not compatible"
        echo "Your OS configuration is:"
            echo "$(uname -a)"
        l_osName="HP_64_bit"
            echo "Do you want to try it forcefully, It may not work, please speak to support team before going ahead." 
            echo "Enter 1 to forcefully go ahead  any other key to stop installation"
            read l_forcechoice
            if [ $l_forcechoice = 1 ]
            then
                Install
            fi    
        fi

    elif [ $l_osChoice = 7 ]
    then
        if [ "$(uname -a | grep -E 'Linux.*i686|i386.*Linux')" ]
        then
            echo "you are working on Red Hat Linux 32 bit"
            l_osName="Red_hat_32_bit"
            Install
        else
            echo "your os type is not compatible"
            echo "Your OS configuration is:"
            echo "$(uname -a)"
            l_osName="Red_hat_32_bit"
            echo "Do you want to try it forcefully, It may not work, please speak to support team before going ahead." 
            echo "Enter 1 to forcefully go ahead  any other key to stop installation"
            read l_forcechoice
            if [ $l_forcechoice = 1 ]
            then
                Install
            fi
        fi


    elif [ $l_osChoice = 8 ]
    then
        if [ "$(isainfo -n | grep 64)" ]
        then
        echo "you are working on Solaris amd 64 bit"
        l_osName="Solaris_amd_64_bit"
        Install	
        else
        echo "your os type is not compatible"
        echo "Your OS configuration is:"
            echo "$(uname -a)"
        l_osName="Solaris_amd_64_bit"
            echo "Do you want to try it forcefully, It may not work, please speak to support team before going ahead." 
            echo "Enter 1 to forcefully go ahead  any other key to stop installation"
            read l_forcechoice
            if [ $l_forcechoice = 1 ]
            then
                Install
            fi    

        fi

    elif [ $l_osChoice = 9 ]
    then
        if [ "$(uname -a | grep -E 'Linux.*i686|i386.*Linux')" ]
        then
            echo "you are working on Red Hat Linux 64 bit"
            l_osName="Red_hat_64_bit"
            Install
        else
            echo "your os type is not compatible"
            echo "Your OS configuration is:"
            echo "$(uname -a)"
            l_osName="Red_hat_64_bit"
            echo "Do you want to try it forcefully, It may not work, please speak to support team before going ahead." 
            echo "Enter 1 to forcefully go ahead  any other key to stop installation"
            read l_forcechoice
            if [ $l_forcechoice = 1 ]
            then
                Install
            fi
        fi


    elif [ $l_osChoice = 10 ]
    then
        if [ "$(uname -a | grep -E 'Linux.*i686|i386.*Linux')" ]
        then
            echo "you are working on CentOs Linux 32 bit"
            l_osName="CentOs_32_bit"
            Install
        else
            echo "your os type is not compatible"
            echo "Your OS configuration is:"
            echo "$(uname -a)"
            l_osName="CentOs_32_bit"
            echo "Do you want to try it forcefully, It may not work, please speak to support team before going ahead." 
            echo "Enter 1 to forcefully go ahead  any other key to stop installation"
            read l_forcechoice
            if [ $l_forcechoice = 1 ]
            then
                Install
            fi
        fi


    else 
        echo "Please select the correct choice." 
        exit 1;
    fi
    """
    f.write(s)
    f.close()
    os.chmod(bashfile, 0o755)
    subprocess.call(["bash", bashfile] + sys.argv[1:])

