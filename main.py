import os
from CmdOSPF import cmdOSPF


def main():

    # Stop firewall service to allow all the packets
    bashCommand = "sudo systemctl stop firewalld.service"
    os.system(bashCommand)

    # Allow packet forwarding
    bashCommand = "sysctl -w net.ipv4.ip_forward=1"
    os.system(bashCommand)

    ### Read configuration files ###
    f = open('./configs/routerID', 'r')             #routerID
    routerID=f.readline()
    f.close()

    f = open('./configs/HelloInterval', 'r')        #Hello Interval
    hellointerval = int(f.readline())
    f.close()

    f = open('./configs/RouterDeadInterval', 'r')   #Router dead Interval
    routerDeadInterval = hellointerval* int(f.readline())
    f.close()

    f = open('./configs/RouterPriority', 'r')       #RouterPriority
    RouterPriority = int(f.readline())
    f.close()

    f = open('./configs/IntTransDelay', 'r')  #
    IntTransDelay = int(f.readline())
    f.close()

    commandLineOSPF = cmdOSPF()

    commandLineOSPF.cmdloop(routerID, routerDeadInterval, RouterPriority, hellointerval, IntTransDelay)


if __name__ == '__main__':
    main()