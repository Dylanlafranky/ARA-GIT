#!/usr/bin/python3

import sys
import itertools

class dataItem():
    def __init__(self,dType,dOrient="U",dAngle="-1"):
        self.type = dType
        self.orient = dOrient
        #self.angle = float(dAngle)
        try:
            if (dAngle):
                self.angle = dAngle
            else:
                self.angle = "-1"
        except:
            self.angle = "-1"
            


def processData(infile,outfile):
    first= 1
    dataRaw=[]
    
    for line in infile:
        if first:
            header=line.strip().split(",")
            headCols={header[i]:i for i in range(len(header))}
            nMax=int(header[-4][2:-2])
            first=0
        else:
            sp = line.strip().split(",")
            dataRaw.append([sp])
            flowerUnits=[]
            nCurr = 1
            dataRaw[-1].append(getObserverID(sp[0]))
            while nCurr <= nMax:
                col=headCols["nr"+str(nCurr)]
                if (sp[col]):
                    flowerUnits.append(dataItem(sp[col],sp[col+1],sp[col+2]))
                else:
                    break
                nCurr +=1
            #print(dataRaw[-1][0])
            dataRaw[-1].append(getInfo(flowerUnits))
    header.append(getInfoHeader())
    outfile.write(",".join(header)+"\n")
    for d in dataRaw:
        #outfile.write(",".join(str(s) for s in d)+'\n')
        #outfile.write(",".join([str(s) for s in list(itertools.chain.from_iterable(d))])+"\n") ## wrong.
        outfile.write(",".join([','.join([str(s) for s in shortlist]) for shortlist in d])+"\n") ## wrong.

def getObserverID(flID):
    if flID[0] == "L":
        return "1"
    if flID[0] == "E":
        return "2"
    if flID[0] == "M":
        return "3"
    if flID[0] == "A":
        return "4"
    if flID[0] == "S":
        return "5"
    if flID[0] == "C":
        return "6"

def getInfo(flowers):
   infoItems = []
   infoItems.append(getPhylOrientation(flowers))
   infoItems.append(getFlowerOrientation(flowers))
   #infoItems.append([i for i in getPhylOrientation(flowers)])
   #infoItems.append([i for i in getFlowerOrientation(flowers)])
   #print(infoItems)
   return list(itertools.chain.from_iterable(infoItems))

       
    
def getInfoHeader():
    return ",".join(["observer","phyllotaxisOrientation","phyllotaxisLogical","flowerOrientation_naive_strict","flowerOrientation_naive_withUnsure", "flowerOrientation_skipFirst_strict", "flowerOrientation_skipFirst_withUnsure","isLogical","n_naive_strict","n_naive_withUnsure","n_skipFirst_strict","n_skipFirst_withUnsure","organSequence","orientSequence"])

def getPhylOrientation(flowers):
    ## CW = 1; CCW = -1
    nCW= 0
    nCCW = 0
    nNeutral = 0
    sensible = 1
    for f in flowers:
        if f.angle == "-1":
            continue
        if f.angle == "111":
            nCW += 1
        elif f.angle == "107":
            nCCW += 1
        else:
            a = float(f.angle)
            if a == 9:
                nNeutral += 1
            if a > 9 :
                if a <= 16:
                    nCW += 1
                    if a > 13:
                        sensible = 0
            if a < 9 :
                if a >= 2:
                    nCCW += 1
                    if a < 5:
                        sensible = 0
    if sensible == 0:
        return [0,sensible]
    if nCW * nCCW > 0:
        return [0,sensible]
    if nCW > 0:
        return [1,sensible]
    if nCCW > 0:
        return [-1,sensible]
    return [0,sensible]

def getFlowerOrientation(flowers):
    ## naive: all flowers
    ## skip first: ignore orientation of oldest primordium (F/S/P)
    ## strict: only interpret L an R as known orientation (LU and RU as U)
    ## withUnsure: interpret LU as L and RU as R
    ## isLogical: order of primordia as expected by developmental sequence
    isLogical = 1
    nLeft = 0
    nRight = 0
    nLeftStrict = 0
    nRightStrict = 0
    fSeq = []
    noInfo = ["G","X"]  ## primodium with flower stalk, gone; only partial info: must come before V
    prOrder = { "N": 1, "B": 2, "F": 3, "FS": 4, "S":5, "P":6, "G":7, "X":8, "V":9}  ## G can be in any position before V!
    #unsure = [ "LU", "RU" ]
    lastItem = 0
    lastGenerative = ""
    nLast = 0
    nSure = 0
    nWUnsure = 0
    fSeq = ""
    oriSeq = ""
    for i in range(len(flowers)):
        f = flowers[i]  
        fSeq = fSeq + "."+ f.type
        oriSeq = oriSeq + "." + f.orient
        #if f.type == "G":
        if f.type in noInfo:
            if lastItem == prOrder["V"]:
                isLogical = 0
        else:
            thisItem = prOrder[f.type]
            if thisItem < lastItem: 
                isLogical = 0
            lastItem = thisItem
        if f.type != "V":
            lastGenerative = prOrder[f.type]
            nLast = i
        if f.orient == "L":
            nLeft += 1
            nLeftStrict += 1
            nSure += 1
        elif f.orient == "LU":
            nLeft += 1
            nWUnsure += 1
        if f.orient == "R":
            nRight += 1
            nRightStrict += 1
            nSure += 1
        elif f.orient == "RU":
            nRight += 1
            nWUnsure += 1
    
    noFirstSure = nSure
    nWUnsure += nSure
    noFirstAll = nWUnsure 
    naiveStrict = flowerOrientation(nLeftStrict,nRightStrict)
    naiveWUnsure = flowerOrientation(nLeft,nRight)
    if lastGenerative < prOrder["S"]:
        if flowers[nLast].orient == "LU":
            nLeft -= 1
            noFirstAll -= 1
        if flowers[nLast].orient == "L":
            nLeft -= 1
            nLeftStrict -= 1
            noFirstAll -= 1
            noFirstSure -= 1
        if flowers[nLast].orient == "RU":
            nRight -= 1
            noFirstAll -= 1
        if flowers[nLast].orient == "R":
            nRight -= 1
            nRightStrict -= 1
            noFirstAll -= 1
            noFirstSure -= 1
    noFirstStrict = flowerOrientation(nLeftStrict,nRightStrict)
    noFirstWUnsure = flowerOrientation(nLeft,nRight)
    return [naiveStrict, naiveWUnsure, noFirstStrict, noFirstWUnsure,isLogical,nSure,nWUnsure,noFirstSure,noFirstAll,fSeq[1:],oriSeq[1:]]

def flowerOrientation (nLeft,nRight):
    if nLeft * nRight > 0:
        return 0
    if nLeft > 0:
        return -1
    if nRight > 0:
        return 1
    return 0


if __name__ == '__main__':
    if not sys.argv[1][-3:] == "csv":
        print ("Unexpected input argument. Must be comma separated csv.")
    else:
        infile=open(sys.argv[1],'r')
        outfile=open(sys.argv[1][:-4]+"_processed.csv","w")
        processData(infile,outfile)
        infile.close()
        outfile.close()
