#!/usr/bin/python3

import sys
#import itertools



def processData(infile,outfile):
    first= 1
    countsAllUnfiltered=[[0,0,0] for i in range(20)]  # [consisted, inconsistent, total]
    countsAll=[[0,0,0] for i in range(20)]
    countsAligned=[[0,0,0] for i in range(20)]
    countsMixedOnly=[[0,0,0] for i in range(20)]
    countsAlignedMixed=[[0,0,0] for i in range(20)]
    #header: return ",".join(["observer","phyllotaxisOrientation","phyllotaxisLogical","flowerOrientation_naive_strict","flowerOrientation_naive_withUnsure", "flowerOrientation_skipFirst_strict", "flowerOrientation_skipFirst_withUnsure","isLogical","n_naive_strict","n_naive_withUnsure","n_skipFirst_strict","n_skipFirst_withUnsure","organSequence","orientSequence"])
    ## NOTE: adjust output name appendix according to choice here. 
    #dataChoice = "naive_withUnsure" ## only sensible alternative: "naive_strict"
    dataChoice = "naive_strict" ## only sensible alternative: "naive_withUnsure"
    
    for line in infile:
        if first:
            header=line.strip().split(",")
            headCols={header[i]:i for i in range(len(header))}
            #nMax=int(header[-4][2:-2])
            first=0
        else:
            sp = line.strip().split(",")
            if sp[headCols["n_"+dataChoice]] == "0":
                print(sp)
                continue
            organDev=sp[headCols["organSequence"]].split(".")[::-1]  ## reverses list / string
            orientDev=sp[headCols["orientSequence"]].split(".")[::-1] ## reverses list / string
            firstCertain = 0
            while organDev[0] == "V":
                organDev = organDev[1:]
                orientDev = orientDev[1:]
                firstCertain = 1
            isMixed=0
            if sp[headCols["flowerOrientation_"+dataChoice]] == "0":
                isMixed=1
            phylLogic = int(sp[headCols["phyllotaxisLogical"]])
            phylOrient = int(sp[headCols["phyllotaxisOrientation"]])
            if phylLogic * phylOrient == 0:
                continue
            flowerPredict = -1 * phylOrient
            for i in range(len(organDev)):
                thisFlower = parseOrient(orientDev[i],dataChoice)
                if thisFlower == 0:
                    continue
                isInconsistent = 0
                if thisFlower * flowerPredict == -1:
                    isInconsistent = 1
                countsAllUnfiltered[i][isInconsistent] += 1
                countsAllUnfiltered[i][2] += 1
                if int(sp[headCols["isLogical"]]): # and phylLogic: ## implicitly OK: tested above
                    countsAll[i][isInconsistent] += 1
                    countsAll[i][2] += 1
                    if firstCertain:
                        countsAligned[i][isInconsistent] += 1
                        countsAligned[i][2] += 1
                    if isMixed:
                        countsMixedOnly[i][isInconsistent] += 1
                        countsMixedOnly[i][2] += 1
                        if firstCertain:
                            countsAlignedMixed[i][isInconsistent] += 1
                            countsAlignedMixed[i][2] += 1
    outfile.write("\t".join(["position","consistent_UF","inconsistent_UF","count_UF","consistent_All","inconsistent_All","count_All","consistent_Aligned","inconsistent_Aligned","count_Aligned","consistent_mixed","inconsistent_mixed","count_mixed","consistent_mixedAligned","inconsistent_mixedAligned","count_mixedAligned"])+'\n')
    for i in range(20):
        if countsAllUnfiltered[i][2] == 0:
            break
        outfile.write("\t".join([str(i+1)]+["\t".join([str(s) for s in theList]) for theList in [countsAllUnfiltered[i],countsAll[i],countsAligned[i],countsMixedOnly[i],countsAlignedMixed[i]  ]])+'\n')

def parseOrient(fl,dataChoice):
    if fl == "L":
        return -1
    if fl == "LU" and dataChoice == "naive_withUnsure": ## alternative: "naive_strict" ; which does not count unsure
        return -1
    if fl == "R":
        return 1
    if fl == "RU" and dataChoice == "naive_withUnsure": ## alternative: "naive_strict" ; which does not count unsure
        return 1
    return 0



if __name__ == '__main__':
    if not sys.argv[1][-3:] == "csv":
        print ("Unexpected input argument. Must be comma separated csv.")
    else:
        infile=open(sys.argv[1],'r')
        ## Hand edit name convention below in line with the options chosen above
        #outfile=open(sys.argv[1][:-4]+"_deviations.csv","w")
        outfile=open(sys.argv[1][:-4]+"_deviationsStrict.csv","w")
        processData(infile,outfile)
        infile.close()
        outfile.close()
