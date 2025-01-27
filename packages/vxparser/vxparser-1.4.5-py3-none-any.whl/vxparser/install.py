import sys, os, pwd, base64, re

UFILE = b'[Unit]\nSourcePath=\nDescription=MastaaaS MXV-Parser Service\nWants=network-online.target\nAfter=multi-user.target\nStartLimitIntervalSec=0\n \n[Service]\nUser=\nRestart=always\nRestartSec=5\nExecStart=\nExecReload=\nExecStop=\n \n[Install]\nWantedBy=multi-user.target\n\n\n'
SFILE = b'#!/bin/bash\n\nROOTPATH=\nSERVICE=$ROOTPATH/vx-service.py\n\nstart() {\n    pids=$(ps aux | grep \'vx-service.py\' | grep -v grep | awk \'{print $2}\')\n    if ! [ "$pids" == "" ]; then\n        echo \'vx-service is already running\'\n        return 1\n    fi\n    echo \'Starting VX-Parser Service ...\'\n    python3 $SERVICE &\n    echo \'Running in foreground...\'\n    sleep infinity\n}\n\nstop() {\n    pids=$(ps aux | grep "vx-service.py" | grep -v grep | awk \'{print $2}\')\n    if [ "$pids" == "" ]; then\n        echo "vx-service is not running"\n        return 1\n    fi\n    echo "Stopping VX-Parser Service ..."\n    kill -9 $pids 2>/dev/null\n    sleep 1\n}\n\nrestart() {\n    stop\n    sleep 1\n    start\n}\n\ncase "$1" in\n    start) start ;;\n    stop) stop ;;\n    reload) restart ;;\n    restart) restart ;;\n    *) echo "Usage: $0 {start|stop|restart|reload}" ;;\nesac\n\nexit 0\n\n'
MFILE = b'import utils.common as com\ncom.check()\n\nimport cli, services\n\n\ndef main():\n    services.handler(\'init\')\n    #cli.menu()\n\n\nif __name__ == "__main__":\n    main()\n'
CUID = os.getuid()
CU = pwd.getpwuid(CUID)[0]
RP = os.path.dirname(os.path.abspath(__file__))
PUID = os.stat(RP).st_uid
PU = pwd.getpwuid(PUID)[0]


class col:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    YELLOW = '\033[33m'
    ENDC = '\033[0m'
    DEFAULT = '\033[0m'
    BOLD = '\033[1m'


def printc(rText, rColour=col.OKBLUE, rPadding=0):
    print("%s ┌─────────────────────────────────────────────────┐ %s" % (rColour, col.ENDC))
    for i in range(rPadding): print("%s │                                                 │ %s" % (rColour, col.ENDC))
    if isinstance(rText, str):
        print("%s │ %s%s%s │ %s" % (rColour, " "*round(23-(len(rText)/2)), rText, " "*round(46-(22-(len(rText)/2))-len(rText)), col.ENDC))
    elif isinstance(rText, list):
        for text in rText:
            print("%s │ %s%s%s │ %s" % (rColour, " "*round(23-(len(text)/2)), text, " "*round(46-(22-(len(text)/2))-len(text)), col.ENDC))
    for i in range(rPadding): print("%s │                                                 │ %s" % (rColour, col.ENDC))
    print("%s └─────────────────────────────────────────────────┘ %s" % (rColour, col.ENDC))
    print(" ")


def pre_check():
    if not CUID == 0:
        return [ "You need to be run this Script @ root!", "Please try again with sudo!" ]
    if os.path.exists(os.path.join(RP, 'service')): os.remove(os.path.join(RP, 'service'))
    if os.path.exists(os.path.join(RP, 'vx-service.py')): os.remove(os.path.join(RP, 'vx-service.py'))
    if os.path.exists("/etc/systemd/system/vxparser.service"): os.remove("/etc/systemd/system/vxparser.service")
    return True


def main():
    printc("Welcome to my service installer ...", col.HEADER)
    pre = pre_check()
    if not pre == True:
        return printc(pre, col.FAIL)
    if not CU == PU:
        printc(["Current user of this Directory is: %s" % PU, "Would you like to install service as it?" ], col.WARNING)
        i = input("(Y/n): ")
        if i == "" or i.upper() in [ "YES", "Y" ]: USER = PU
        else: USER = CU
    else: USER = CU
    printc("Install Services as User: %s" % USER, col.DEFAULT)

    printc(["Creating File:", str(os.path.join(RP, 'service')) ], col.DEFAULT)
    rFile = open(os.path.join(RP, 'service'), "wb")
    rFile.write(SFILE)
    rFile.close()
    if not os.path.exists(os.path.join(RP, 'service')): 
        return printc(["Failed!","Please try again ..."], col.FAIL)
    os.system("sed -i -e 's|ROOTPATH=|ROOTPATH=%s|g' %s" %(RP, str(os.path.join(RP, 'service'))))
    os.system("chmod +x %s" % os.path.join(RP, 'service'))
    if not USER == 'root':
        os.system('chown %s:%s %s' %(USER, USER, str(os.path.join(RP, 'service'))))

    printc(["Creating File:", str(os.path.join(RP, 'vx-service.py')) ], col.DEFAULT)
    rFile = open(os.path.join(RP, 'vx-service.py'), "wb")
    rFile.write(MFILE)
    rFile.close()
    if not os.path.exists(os.path.join(RP, 'vx-service.py')):
        return printc(["Failed!","Please try again ..."], col.FAIL)
    os.system("chmod +x %s" % os.path.join(RP, 'vx-service.py'))
    if not USER == 'root':
        os.system('chown %s:%s %s' %(USER, USER, str(os.path.join(RP, 'vx-service.py'))))

    printc(["Creating File:", "/etc/systemd/system/vxparser.service" ], col.DEFAULT)
    rFile = open("/etc/systemd/system/vxparser.service", "wb")
    rFile.write(UFILE)
    rFile.close()
    if not os.path.exists("/etc/systemd/system/vxparser.service"):
        return printc(["Failed!","Please try again ..."], col.FAIL)
    os.system("sed -i -e 's|SourcePath=|SourcePath=%s|g' %s" %(str(os.path.join(RP, 'service')), "/etc/systemd/system/vxparser.service"))
    os.system("sed -i -e 's|User=|User=%s|g' %s" %(USER, "/etc/systemd/system/vxparser.service"))
    os.system("sed -i -e 's|ExecStart=|ExecStart=/bin/bash %s start|g' %s" %(str(os.path.join(RP, 'service')), "/etc/systemd/system/vxparser.service"))
    os.system("sed -i -e 's|ExecReload=|ExecReload=/bin/bash %s reload|g' %s" %(str(os.path.join(RP, 'service')), "/etc/systemd/system/vxparser.service"))
    os.system("sed -i -e 's|ExecStop=|ExecStop=/bin/bash %s stop|g' %s" %(str(os.path.join(RP, 'service')), "/etc/systemd/system/vxparser.service"))
    os.system("sudo chmod +x /etc/systemd/system/vxparser.service")
    printc("Everything looks Good !", col.OKGREEN)
    printc("Would you like to enable Service now?", col.DEFAULT)
    i = input("(Y/n): ")
    if i == "" or i.upper() in [ "YES", "Y" ]:
        os.system("sudo systemctl daemon-reload")
        os.system("sudo systemctl enable vxparser.service")
        os.system("sudo systemctl start vxparser.service")
    else:
        printc(["OK!","To enable Service run:", "sudo systemctl daemon-reload", "sudo systemctl enable vxparser.service", "sudo systemctl start vxparser.service"], col.DEFAULT)
    printc(["Everything is Done !", "Have fun with it ...", "Copyright by Mastaaa @2025"], col.OKBLUE)
    return


if __name__ == "__main__":
    main()
