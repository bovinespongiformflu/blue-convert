import subprocess
import json
import socket
import os
import time
diskinventory = []
nvmeinventory = []
diskinventoryfile = open("disks.txt", "r")
diskinventory = diskinventoryfile.readlines()
diskinventoryfile.close
nvmeinventoryfile = open("nvme.txt", "r")
nvmeinventory = nvmeinventoryfile.readlines()
nvmeinventoryfile.close
isprocrun=99

def main():
    print("This utility will convert any osd file-stores into blue-stores, WARNING: BE SURE ALL DISKS IN THE SYSTEM ARE OPERATIONAL")
    print("Proceeding will purge all osds's on THIS system, destroy all data, clear all partitions, and create new OSD's that will be added to the cluster")
    print("To proceed type \"proceed\" and press enter, any other input will exit")
    moveforward=str(input())
    if moveforward=="proceed":
        print ("Proceeding")
        stoposdprocess()
        purgeosdid()
        wipedisks()
        #createlg()
        #createbs()
    else:
        print ("Exiting")
        exit()

def checkosdprocess():
    result1 = subprocess.Popen(['pgrep', 'ceph-osd'], stdout=subprocess.PIPE)
    resultstdout1 = result1.communicate()[0]
    result2 = subprocess.Popen(['pgrep', 'skdakwkk2kk'], stdout=subprocess.PIPE)
    resultstdout2 = result2.communicate()[0]
    global isprocrun
    if resultstdout1 == resultstdout2:
        isprocrun=0
    else:
        isprocrun=1

def stoposdprocess():
    checkosdprocess()
    g=0
    if isprocrun==1:
        print("ceph osd's are still running, stopping them.")
        os.system("systemctl stop ceph-osd@*")
        time.sleep(10)
        print("rechecking")
        time.sleep(3)
        g=g+1
        if g > 3:
            print("Could not stop processes, exiting")
            exit()
        else:
            stoposdprocess()
    else:
        print("processes not running, dismounting osds")
        os.system("umount /var/lib/ceph/osd/*")
        time.sleep(5)

def purgeosdid():
    osdlist=[]
    result = subprocess.Popen(['ceph', 'osd', 'tree', '-f', 'json-pretty'], stdout=subprocess.PIPE) #run shell command and receive output into shell buffer
    resultstdout = result.communicate()[0]
    dictOSDTree=json.loads(resultstdout.decode('utf-8')) #take json output from shell buffer and put into this dictionary
    for i in range(len(dictOSDTree['nodes'])):
        if dictOSDTree['nodes'][i]['name']==socket.gethostname(): #look for systemname
            for g in range(len(dictOSDTree['nodes'][i]['children'])): #loop to enumerate osds on the system
                osdlist.append(dictOSDTree['nodes'][i]['children'][g])
    for i in range(len(osdlist)):
        purgecmdrun=subprocess.Popen(['ceph', 'osd', 'purge', str(osdlist[i])], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(10)
        print("purge command for OSD ID", osdlist[i], "successful")

def wipedisks():
    for i in range(len(diskinventory)):
        zapcmd = "ceph-volume lvm zap /dev/" + diskinventory[i]
        os.system(zapcmd)
        time.sleep(10)
    for i in range(len(nvmeinventory)):
        zapcmd = "ceph-volume lvm zap /dev/" + nvmeinventory[i]
        os.system(zapcmd)
        time.sleep(10)
    os.system("partprobe")

def createlg():
    g=0
    for i in range(len(nvmeinventory)):
        vgcmd = "echo vgstuff ceph-nvm" + str(g) + " /dev/" + nvmeinventory[i]
        os.system(vgcmd)
        time.sleep(10)
        g=g+1

    #for i in range(len(diskinventory)):

def createbs():
    print("this creates the bluestores!")

if __name__ == "__main__":
    main()