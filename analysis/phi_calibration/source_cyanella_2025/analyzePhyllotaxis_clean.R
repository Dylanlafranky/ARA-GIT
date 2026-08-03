#!/usr/bin/R
library(ggplot2)
library("dplyr")
library(reshape2)
library(data.table)
library("gridExtra")

dataDir <- getwd()
dirSep <- "/"
outputDir <- paste0(getwd(),dirSep,"graphs")

fileFlavescens <- paste0(dataDir,dirSep,"cyanellaAlbaFlavescens_final_export_processed.csv")

corrTable <- list()

dataFlavescens <- read.csv(file=fileFlavescens)

filteredFlavescens <- subset(dataFlavescens, isLogical* phyllotaxisLogical == 1 ) %>% subset(n_naive_withUnsure > 0 )

#ct<- cor.test(dataFlavescens$phyllotaxisOrientation,dataFlavescens$flowerOrientation_skipFirst_withUnsure)
ct<- cor.test(dataFlavescens$phyllotaxisOrientation[dataFlavescens$n_skipFirst_withUnsure>0],dataFlavescens$flowerOrientation_skipFirst_withUnsure[dataFlavescens$n_skipFirst_withUnsure>0])
print(ct)
corrTable[[1]]<-list(subspecies="flavescens",skipFirst="1",withUnsure="1",filtered="0",corr=ct$estimate,low=ct$conf.int[1],high=ct$conf.int[2],n=ct$parameter+2)
ct<- cor.test(dataFlavescens$phyllotaxisOrientation[dataFlavescens$n_naive_withUnsure>0],dataFlavescens$flowerOrientation_naive_withUnsure[dataFlavescens$n_naive_withUnsure>0])
print(ct)
corrTable[[2]]<-list(subspecies="flavescens",skipFirst="0",withUnsure="1",filtered="0",corr=ct$estimate,low=ct$conf.int[1],high=ct$conf.int[2],n=ct$parameter+2)
ct<- cor.test(dataFlavescens$phyllotaxisOrientation[dataFlavescens$n_skipFirst_strict>0],dataFlavescens$flowerOrientation_skipFirst_strict[dataFlavescens$n_skipFirst_strict>0])
print(ct)
corrTable[[3]]<-list(subspecies="flavescens",skipFirst="1",withUnsure="0",filtered="0",corr=ct$estimate,low=ct$conf.int[1],high=ct$conf.int[2],n=ct$parameter+2)
ct<- cor.test(dataFlavescens$phyllotaxisOrientation[dataFlavescens$n_naive_strict>0],dataFlavescens$flowerOrientation_naive_strict[dataFlavescens$n_naive_strict>0])
print(ct)
corrTable[[4]]<-list(subspecies="flavescens",skipFirst="0",withUnsure="0",filtered="0",corr=ct$estimate,low=ct$conf.int[1],high=ct$conf.int[2],n=ct$parameter+2)

#ct<- cor.test(filteredFlavescens$phyllotaxisOrientation,filteredFlavescens$flowerOrientation_skipFirst_withUnsure)
ct<- cor.test(filteredFlavescens$phyllotaxisOrientation[filteredFlavescens$n_skipFirst_withUnsure>0],filteredFlavescens$flowerOrientation_skipFirst_withUnsure[filteredFlavescens$n_skipFirst_withUnsure>0])
print(ct)
corrTable[[5]]<-list(subspecies="flavescens",skipFirst="1",withUnsure="1",filtered="1",corr=ct$estimate,low=ct$conf.int[1],high=ct$conf.int[2],n=ct$parameter+2)
#ct<- cor.test(filteredFlavescens$phyllotaxisOrientation,filteredFlavescens$flowerOrientation_naive_withUnsure)
ct<- cor.test(filteredFlavescens$phyllotaxisOrientation[filteredFlavescens$n_naive_withUnsure>0],filteredFlavescens$flowerOrientation_naive_withUnsure[filteredFlavescens$n_naive_withUnsure>0])
print(ct)
print("flowers+buds, naive_strict", sum(filteredFlavescens$n_naive_strict)/length(filteredFlavescens$n_naive_strict))
corrTable[[6]]<-list(subspecies="flavescens",skipFirst="0",withUnsure="1",filtered="1",corr=ct$estimate,low=ct$conf.int[1],high=ct$conf.int[2],n=ct$parameter+2)
#ct<- cor.test(filteredFlavescens$phyllotaxisOrientation,filteredFlavescens$flowerOrientation_skipFirst_strict)
ct<- cor.test(filteredFlavescens$phyllotaxisOrientation[filteredFlavescens$n_skipFirst_strict>0],filteredFlavescens$flowerOrientation_skipFirst_strict[filteredFlavescens$n_skipFirst_strict>0])
print(ct)
corrTable[[7]]<-list(subspecies="flavescens",skipFirst="1",withUnsure="0",filtered="1",corr=ct$estimate,low=ct$conf.int[1],high=ct$conf.int[2],n=ct$parameter+2)
#ct<- cor.test(filteredFlavescens$phyllotaxisOrientation,filteredFlavescens$flowerOrientation_naive_strict)
ct<- cor.test(filteredFlavescens$phyllotaxisOrientation[filteredFlavescens$n_naive_strict>0],filteredFlavescens$flowerOrientation_naive_strict[filteredFlavescens$n_naive_strict>0])
print(ct)
corrTable[[8]]<-list(subspecies="flavescens",skipFirst="0",withUnsure="0",filtered="1",corr=ct$estimate,low=ct$conf.int[1],high=ct$conf.int[2],n=ct$parameter+2)

print(rbindlist(corrTable))
pdf(paste0(dataDir,dirSep,"phyllotaxisCorrelationTable.pdf"))
#grid.table(round(rbindlist(corrTable),digits=2),theme=ttheme_default(base_size=8))
grid.table(rbindlist(corrTable),theme=ttheme_default(base_size=8),rows=NULL)
dev.off()

print(paste0("flowers+buds, naive_strict: ", sum(filteredFlavescens$n_naive_strict)/(length(filteredFlavescens$n_naive_strict)-1))) ## subtract 1, for a plant without informative flowers
#[1] 2.73484848484848
print(paste0("flowers+buds, naive_withUnsure: ", sum(filteredFlavescens$n_naive_withUnsure)/(length(filteredFlavescens$n_naive_withUnsure)-1)))
#> sum(filteredFlavescens$n_naive_withUnsure)/length(filteredFlavescens$n_naive_withUnsure)
#[1] 2.84848484848485
#> median(filteredFlavescens$n_naive_withUnsure)
#[1] 3
#> median(filteredFlavescens$n_naive_strict)
#[1] 3




myplot <- ggplot() + geom_jitter(data=filteredFlavescens,aes(x=flowerOrientation_skipFirst_withUnsure,y=phyllotaxisOrientation),width=0.2,height=0.2) + 
scale_x_continuous(name="Flower orientation",label=c("Left","Mixed","Right"),breaks=(c(-1,0,1))) + 
scale_y_continuous(name="Phyllotaxis orientation",label=c("CCW","Mixed","CW"),breaks=(c(-1,0,1))) 

pdf(paste0(outputDir,dirSep,"phyllotaxis_CalbaFlavescens_dataScatter.pdf"))
print(myplot)
dev.off()


### alice style plots
inshift <- 0.88 ## factor to shift position of counts by
rMax <- 17 ## max radius of the bubbles

countsFlavescens <- filteredFlavescens %>%group_by(phyllotaxisOrientation, flowerOrientation_skipFirst_withUnsure) %>% dplyr::summarize(count=n()) %>% mutate(mix=phyllotaxisOrientation*flowerOrientation_skipFirst_withUnsure)

myplot <- ggplot() + geom_point(data=countsFlavescens,aes(x=flowerOrientation_skipFirst_withUnsure,y=phyllotaxisOrientation,size=count,colour=mix)) +
scale_x_continuous(name="Flower orientation",label=c("Left","Mixed","Right"),breaks=(c(-1,0,1))) +
scale_y_continuous(name="Phyllotaxis orientation",label=c("CCW","Mixed","CW"),breaks=(c(-1,0,1))) +
  scale_colour_gradient2(low ="#00628c", mid = "#999999" , high = "#cab23c",       
                         midpoint = 0)+
scale_radius(range=c(1,rMax)) +
 theme(legend.position = "none", axis.text=element_text(size=18),
        axis.title=element_text(size=24))+
  geom_text(data=countsFlavescens,
            aes(flowerOrientation_skipFirst_withUnsure*inshift, phyllotaxisOrientation*inshift, label = count,colour=mix), size=7)
pdf(paste0(outputDir,dirSep,"phyllotaxis_CalbaFlavescens_dataBubbles_skipFirst_withUnsure.pdf"))
print(myplot)
dev.off()

countsFlavescens <- filteredFlavescens %>%group_by(phyllotaxisOrientation, flowerOrientation_naive_withUnsure) %>% dplyr::summarize(count=n()) %>% mutate(mix=phyllotaxisOrientation*flowerOrientation_naive_withUnsure)


myplot <- ggplot() + geom_point(data=countsFlavescens,aes(x=flowerOrientation_naive_withUnsure,y=phyllotaxisOrientation,size=count,colour=mix)) +
scale_x_continuous(name="Flower orientation",label=c("Left","Mixed","Right"),breaks=(c(-1,0,1))) +
scale_y_continuous(name="Phyllotaxis orientation",label=c("CCW","Mixed","CW"),breaks=(c(-1,0,1))) +
  scale_colour_gradient2(low ="#00628c", mid = "#999999" , high = "#cab23c",       
                         midpoint = 0)+
scale_radius(range=c(1,rMax)) +
 theme(legend.position = "none", axis.text=element_text(size=18),
        axis.title=element_text(size=24))+
  geom_text(data=countsFlavescens,
            aes(flowerOrientation_naive_withUnsure*inshift, phyllotaxisOrientation*inshift, label = count,colour=mix), size=7)
pdf(paste0(outputDir,dirSep,"phyllotaxis_CalbaFlavescens_dataBubbles_naive_withUnsure.pdf"))
print(myplot)
dev.off()


countsFlavescens <- filteredFlavescens %>%group_by(phyllotaxisOrientation, flowerOrientation_skipFirst_strict) %>% dplyr::summarize(count=n()) %>% mutate(mix=phyllotaxisOrientation*flowerOrientation_skipFirst_strict)

myplot <- ggplot() + geom_point(data=countsFlavescens,aes(x=flowerOrientation_skipFirst_strict,y=phyllotaxisOrientation,size=count,colour=mix)) +
scale_x_continuous(name="Flower orientation",label=c("Left","Mixed","Right"),breaks=(c(-1,0,1))) +
scale_y_continuous(name="Phyllotaxis orientation",label=c("CCW","Mixed","CW"),breaks=(c(-1,0,1))) +
  scale_colour_gradient2(low ="#00628c", mid = "#999999" , high = "#cab23c",       
                         midpoint = 0)+
scale_radius(range=c(1,rMax)) +
 theme(legend.position = "none", axis.text=element_text(size=18),
        axis.title=element_text(size=24))+
  geom_text(data=countsFlavescens,
            aes(flowerOrientation_skipFirst_strict*inshift, phyllotaxisOrientation*inshift, label = count,colour=mix), size=7)
pdf(paste0(outputDir,dirSep,"phyllotaxis_CalbaFlavescens_dataBubbles_skipFirst_strict.pdf"))
print(myplot)
dev.off()

countsFlavescens <- filteredFlavescens %>%group_by(phyllotaxisOrientation, flowerOrientation_naive_strict) %>% dplyr::summarize(count=n()) %>% mutate(mix=phyllotaxisOrientation*flowerOrientation_naive_strict)


myplot <- ggplot() + geom_point(data=countsFlavescens,aes(x=flowerOrientation_naive_strict,y=phyllotaxisOrientation,size=count,colour=mix)) +
scale_x_continuous(name="Flower orientation",label=c("Left","Mixed","Right"),breaks=(c(-1,0,1))) +
scale_y_continuous(name="Phyllotaxis orientation",label=c("CCW","Mixed","CW"),breaks=(c(-1,0,1))) +
  scale_colour_gradient2(low ="#00628c", mid = "#999999" , high = "#cab23c",       
                         midpoint = 0)+
scale_radius(range=c(1,rMax)) +
 theme(legend.position = "none", axis.text=element_text(size=18),
        axis.title=element_text(size=24))+
  geom_text(data=countsFlavescens,
            aes(flowerOrientation_naive_strict*inshift, phyllotaxisOrientation*inshift, label = count,colour=mix), size=7)
pdf(paste0(outputDir,dirSep,"phyllotaxis_CalbaFlavescens_dataBubbles_naive_strict.pdf"))
print(myplot)
dev.off()



deviationInterval <- function(inconsistent,all,expect) { ## ignoring mixed plants
	if (all == 0 ){
return (list(estimate=NA,low=NA,high=NA,pval=NA,n=0))
	}
  mrTemp <- binom.test(inconsistent,all,expect)
#return (c(mrTemp$estimate,mrTemp$conf.int[1],mrTemp$conf.int[2],mrTemp$p.value))
return (list(estimate=mrTemp$estimate,low=mrTemp$conf.int[1],high=mrTemp$conf.int[2],pval=mrTemp$p.value,n=mrTemp$parameter))
}

### flavescens, strict (i.e., ignore unsure flower orientations)

fileFlavescensDeviations <- paste0(dataDir,dirSep,"cyanellaAlbaFlavescens_final_export_processed_deviationsStrict.csv")
deviations <- read.csv2(file=fileFlavescensDeviations,sep="\t") ## Structure: list

fDeviationsAverage_UF <- sum(deviations$inconsistent_UF) / sum(deviations$count_UF)
fDeviationsAverage_All <- sum(deviations$inconsistent_All) / sum(deviations$count_All)
fDeviationsAverage_Aligned <- sum(deviations$inconsistent_Aligned) / sum(deviations$count_Aligned)
fDeviationsAverage_mixed <- sum(deviations$inconsistent_mixed) / sum(deviations$count_mixed)
fDeviationsAverage_mixedAligned <- sum(deviations$inconsistent_mixedAligned) / sum(deviations$count_mixedAligned)


#chiStat <- function (o, e ) {
#return	(1.*(o-e)**2/e)
#}
#chiO <- deviations$inconsistent_All
#chiE <- deviations$count_All * fDeviationsAverage_All
#chiList <- chiStat(chiO,chiE)
#chiO <- deviations$consistent_All
#chiE <- deviations$count_All * (1.-fDeviationsAverage_All)
#chiList2 <- chiStat(chiO,chiE)
## too convoluted ; does demonstrate that the effect strongly hinges on the last two ; therefore also test without these
chiTableFlavescensStrict <- list()
ct<- chisq.test(data.frame(deviations$inconsistent_Aligned, deviations$consistent_Aligned))
chiTableFlavescensStrict[[1]]<-list(subspecies="flavescens",positions="all",data="Aligned",chi=ct$statistic,df=ct$parameter,p=ct$p.value %>% round(4),n=sum(deviations$count_Aligned),E=paste(collapse=' ',ct$expected[,1] %>% round(1)))
ct<- chisq.test(data.frame(deviations$inconsistent_Aligned[1:7], deviations$consistent_Aligned[1:7]))
chiTableFlavescensStrict[[2]]<-list(subspecies="flavescens",positions="1-7",data="Aligned",chi=ct$statistic,df=ct$parameter,p=ct$p.value %>% round(4),n=sum(deviations$count_Aligned[1:7]),E=paste(collapse=' ',ct$expected[,1] %>% round(1)))
ct<- chisq.test(data.frame(deviations$inconsistent_Aligned[1:6], deviations$consistent_Aligned[1:6]))
chiTableFlavescensStrict[[3]]<-list(subspecies="flavescens",positions="1-6",data="Aligned",chi=ct$statistic,df=ct$parameter,p=ct$p.value %>% round(4),n=sum(deviations$count_Aligned[1:6]),E=paste(collapse=' ',ct$expected[,1] %>% round(1)))
ct<- chisq.test(data.frame(deviations$inconsistent_Aligned[1:5], deviations$consistent_Aligned[1:5]))
chiTableFlavescensStrict[[4]]<-list(subspecies="flavescens",positions="1-5",data="Aligned",chi=ct$statistic,df=ct$parameter,p=ct$p.value %>% round(4),n=sum(deviations$count_Aligned[1:5]),E=paste(collapse=' ',ct$expected[,1] %>% round(1)))
ct<- chisq.test(data.frame(deviations$inconsistent_Aligned[1:4], deviations$consistent_Aligned[1:4]))
chiTableFlavescensStrict[[5]]<-list(subspecies="flavescens",positions="1-4",data="Aligned",chi=ct$statistic,df=ct$parameter,p=ct$p.value %>% round(4),n=sum(deviations$count_Aligned[1:4]),E=paste(collapse=' ',ct$expected[,1] %>% round(1)))
ct<- chisq.test(data.frame(deviations$inconsistent_Aligned[1:3], deviations$consistent_Aligned[1:3]))
chiTableFlavescensStrict[[6]]<-list(subspecies="flavescens",positions="1-3",data="Aligned",chi=ct$statistic,df=ct$parameter,p=ct$p.value %>% round(4),n=sum(deviations$count_Aligned[1:3]),E=paste(collapse=' ',ct$expected[,1] %>% round(1)))
ct<- chisq.test(data.frame(deviations$inconsistent_Aligned[1:2], deviations$consistent_Aligned[1:2]))
chiTableFlavescensStrict[[7]]<-list(subspecies="flavescens",positions="1-2",data="Aligned",chi=ct$statistic,df=ct$parameter,p=ct$p.value %>% round(4),n=sum(deviations$count_Aligned[1:2]),E=paste(collapse=' ',ct$expected[,1] %>% round(1)))

print(rbindlist(chiTableFlavescensStrict))
pdf(paste0(dataDir,dirSep,"phyllotaxisPositionChiSquaredTable_flavescens_strict.pdf"))
#grid.table(round(rbindlist(chiTableFlavescensStrict),digits=2),theme=ttheme_default(base_size=8))
grid.table(rbindlist(chiTableFlavescensStrict),theme=ttheme_default(base_size=8),rows=NULL)
dev.off()


errorData <- list()
for (i in 1:length(deviations$position)) {
	errorData[[i]] <-  deviationInterval(deviations$inconsistent_UF[i],deviations$count_UF[i],fDeviationsAverage_UF)
}
plotForm_UF <- rbindlist(errorData)


errorData <- list()
for (i in 1:length(deviations$position)) {
	errorData[[i]] <-  deviationInterval(deviations$inconsistent_All[i],deviations$count_All[i],fDeviationsAverage_All)
}
plotForm_All <- rbindlist(errorData)

errorData <- list()
for (i in 1:length(deviations$position)) {
	errorData[[i]] <-  deviationInterval(deviations$inconsistent_Aligned[i],deviations$count_Aligned[i],fDeviationsAverage_Aligned)
}
plotForm_Aligned <- rbindlist(errorData)

errorData <- list()
for (i in 1:length(deviations$position)) {
	errorData[[i]] <-  deviationInterval(deviations$inconsistent_mixed[i],deviations$count_mixed[i],fDeviationsAverage_mixed)
}
plotForm_mixed <- rbindlist(errorData)

errorData <- list()
for (i in 1:length(deviations$position)) {
	errorData[[i]] <-  deviationInterval(deviations$inconsistent_mixedAligned[i],deviations$count_mixedAligned[i],fDeviationsAverage_mixedAligned)
}
plotForm_mixedAligned <- rbindlist(errorData)

print("C. alba flavescens, strict")
print("UF unfiltered")
print(fDeviationsAverage_UF)
print(plotForm_UF)

myplot <- ggplot() + geom_pointrange(data=plotForm_UF,aes(x=rownames(plotForm_UF),y=estimate,ymin=low,ymax=high)) + 
	xlab("Flower position (old to young)") + ylab("Deviation from prediction (fraction)") +
	geom_hline(yintercept=fDeviationsAverage_UF,colour="darkred")+
	geom_label(data=plotForm_UF,aes(x=rownames(plotForm_UF),y=-0.05,label=n))

pdf(paste0(outputDir,dirSep,"phyllotaxis_CalbaFlavescens_deviationsPerPosition_unfiltered_strict.pdf"))
print(myplot)
dev.off()

print("All")
print(fDeviationsAverage_All)
print(plotForm_All)

myplot <- ggplot() + geom_pointrange(data=plotForm_All,aes(x=rownames(plotForm_All),y=estimate,ymin=low,ymax=high)) + 
	xlab("Flower position (old to young)") + ylab("Deviation from prediction (fraction)") +
	geom_hline(yintercept=fDeviationsAverage_All,colour="darkred")+
	geom_label(data=plotForm_All,aes(x=rownames(plotForm_All),y=-0.05,label=n))

pdf(paste0(outputDir,dirSep,"phyllotaxis_CalbaFlavescens_deviationsPerPosition_allOKdata_strict.pdf"))
print(myplot)
dev.off()

print("Aligned")
print(fDeviationsAverage_Aligned)
print(plotForm_Aligned)

myplot <- ggplot() + geom_pointrange(data=plotForm_Aligned,aes(x=rownames(plotForm_Aligned),y=estimate,ymin=low,ymax=high)) + 
	xlab("Flower position (old to young)") + ylab("Deviation from prediction (fraction)") +
	geom_hline(yintercept=fDeviationsAverage_Aligned,colour="darkred") +
	geom_label(data=plotForm_Aligned,aes(x=rownames(plotForm_Aligned),y=-0.05,label=n))

pdf(paste0(outputDir,dirSep,"phyllotaxis_CalbaFlavescens_deviationsPerPosition_alignedData_strict.pdf"))
print(myplot)
dev.off()

print("mixed")
print(fDeviationsAverage_mixed)
print(plotForm_mixed)

myplot <- ggplot() + geom_pointrange(data=plotForm_mixed,aes(x=rownames(plotForm_mixed),y=estimate,ymin=low,ymax=high)) + 
	xlab("Flower position (old to young)") + ylab("Deviation from prediction (fraction)") +
	geom_hline(yintercept=fDeviationsAverage_mixed,colour="darkred")+
	geom_label(data=plotForm_mixed,aes(x=rownames(plotForm_mixed),y=-0.05,label=n))

pdf(paste0(outputDir,dirSep,"phyllotaxis_CalbaFlavescens_deviationsPerPosition_mixed_strict.pdf"))
print(myplot)
dev.off()

print("mixedAligned")
print(fDeviationsAverage_mixedAligned)
print(plotForm_mixedAligned)

myplot <- ggplot() + geom_pointrange(data=plotForm_mixedAligned,aes(x=rownames(plotForm_mixedAligned),y=estimate,ymin=low,ymax=high)) + 
	xlab("Flower position (old to young)") + ylab("Deviation from prediction (fraction)") +
	geom_hline(yintercept=fDeviationsAverage_mixedAligned,colour="darkred")+
	geom_label(data=plotForm_mixedAligned,aes(x=rownames(plotForm_mixedAligned),y=-0.05,label=n))

pdf(paste0(outputDir,dirSep,"phyllotaxis_CalbaFlavescens_deviationsPerPosition_mixedAligned_strict.pdf"))
print(myplot)
dev.off()

q()
## flavescens  with Unsure  
## To run this part, first create the data by editing and running the python script ./findDeviationsFromPattern.py as indicated in the script

fileFlavescensDeviations <- paste0(dataDir,dirSep,"cyanellaAlbaFlavescens_final_export_processed_deviations.csv")
deviations <- read.csv2(file=fileFlavescensDeviations,sep="\t") ## Structure: list

fDeviationsAverage_UF <- sum(deviations$inconsistent_UF) / sum(deviations$count_UF)
fDeviationsAverage_All <- sum(deviations$inconsistent_All) / sum(deviations$count_All)
fDeviationsAverage_Aligned <- sum(deviations$inconsistent_Aligned) / sum(deviations$count_Aligned)
fDeviationsAverage_mixed <- sum(deviations$inconsistent_mixed) / sum(deviations$count_mixed)
fDeviationsAverage_mixedAligned <- sum(deviations$inconsistent_mixedAligned) / sum(deviations$count_mixedAligned)


chiTableFlavescens <- list()
ct<- chisq.test(data.frame(deviations$inconsistent_Aligned, deviations$consistent_Aligned))
chiTableFlavescens[[1]]<-list(subspecies="flavescens",positions="all",data="Aligned",chi=ct$statistic,df=ct$parameter,p=ct$p.value %>% round(4),n=sum(deviations$count_Aligned),E=paste(collapse=' ',ct$expected[,1] %>% round(1)))
ct<- chisq.test(data.frame(deviations$inconsistent_Aligned[1:7], deviations$consistent_Aligned[1:7]))
chiTableFlavescens[[2]]<-list(subspecies="flavescens",positions="1-7",data="Aligned",chi=ct$statistic,df=ct$parameter,p=ct$p.value %>% round(4),n=sum(deviations$count_Aligned[1:7]),E=paste(collapse=' ',ct$expected[,1] %>% round(1)))
ct<- chisq.test(data.frame(deviations$inconsistent_Aligned[1:6], deviations$consistent_Aligned[1:6]))
chiTableFlavescens[[3]]<-list(subspecies="flavescens",positions="1-6",data="Aligned",chi=ct$statistic,df=ct$parameter,p=ct$p.value %>% round(4),n=sum(deviations$count_Aligned[1:6]),E=paste(collapse=' ',ct$expected[,1] %>% round(1)))
ct<- chisq.test(data.frame(deviations$inconsistent_Aligned[1:5], deviations$consistent_Aligned[1:5]))
chiTableFlavescens[[4]]<-list(subspecies="flavescens",positions="1-5",data="Aligned",chi=ct$statistic,df=ct$parameter,p=ct$p.value %>% round(4),n=sum(deviations$count_Aligned[1:5]),E=paste(collapse=' ',ct$expected[,1] %>% round(1)))
ct<- chisq.test(data.frame(deviations$inconsistent_Aligned[1:4], deviations$consistent_Aligned[1:4]))
chiTableFlavescens[[5]]<-list(subspecies="flavescens",positions="1-4",data="Aligned",chi=ct$statistic,df=ct$parameter,p=ct$p.value %>% round(4),n=sum(deviations$count_Aligned[1:4]),E=paste(collapse=' ',ct$expected[,1] %>% round(1)))
ct<- chisq.test(data.frame(deviations$inconsistent_Aligned[1:3], deviations$consistent_Aligned[1:3]))
chiTableFlavescens[[6]]<-list(subspecies="flavescens",positions="1-3",data="Aligned",chi=ct$statistic,df=ct$parameter,p=ct$p.value %>% round(4),n=sum(deviations$count_Aligned[1:3]),E=paste(collapse=' ',ct$expected[,1] %>% round(1)))
ct<- chisq.test(data.frame(deviations$inconsistent_Aligned[1:2], deviations$consistent_Aligned[1:2]))
chiTableFlavescens[[7]]<-list(subspecies="flavescens",positions="1-2",data="Aligned",chi=ct$statistic,df=ct$parameter,p=ct$p.value %>% round(4),n=sum(deviations$count_Aligned[1:2]),E=paste(collapse=' ',ct$expected[,1] %>% round(1)))

print(rbindlist(chiTableFlavescens))
pdf(paste0(dataDir,dirSep,"phyllotaxisPositionChiSquaredTable_flavescens.pdf"))
#grid.table(round(rbindlist(chiTableFlavescens),digits=2),theme=ttheme_default(base_size=8))
grid.table(rbindlist(chiTableFlavescens),theme=ttheme_default(base_size=8),rows=NULL)
dev.off()


errorData <- list()
for (i in 1:length(deviations$position)) {
	errorData[[i]] <-  deviationInterval(deviations$inconsistent_UF[i],deviations$count_UF[i],fDeviationsAverage_UF)
}
plotForm_UF <- rbindlist(errorData)


errorData <- list()
for (i in 1:length(deviations$position)) {
	errorData[[i]] <-  deviationInterval(deviations$inconsistent_All[i],deviations$count_All[i],fDeviationsAverage_All)
}
plotForm_All <- rbindlist(errorData)

errorData <- list()
for (i in 1:length(deviations$position)) {
	errorData[[i]] <-  deviationInterval(deviations$inconsistent_Aligned[i],deviations$count_Aligned[i],fDeviationsAverage_Aligned)
}
plotForm_Aligned <- rbindlist(errorData)

errorData <- list()
for (i in 1:length(deviations$position)) {
	errorData[[i]] <-  deviationInterval(deviations$inconsistent_mixed[i],deviations$count_mixed[i],fDeviationsAverage_mixed)
}
plotForm_mixed <- rbindlist(errorData)

errorData <- list()
for (i in 1:length(deviations$position)) {
	errorData[[i]] <-  deviationInterval(deviations$inconsistent_mixedAligned[i],deviations$count_mixedAligned[i],fDeviationsAverage_mixedAligned)
}
plotForm_mixedAligned <- rbindlist(errorData)

print("C. alba flavescens")
print("UF unfiltered")
print(fDeviationsAverage_UF)
print(plotForm_UF)

myplot <- ggplot() + geom_pointrange(data=plotForm_UF,aes(x=rownames(plotForm_UF),y=estimate,ymin=low,ymax=high)) + 
	xlab("Flower position (old to young)") + ylab("Deviation from prediction (fraction)") +
	geom_hline(yintercept=fDeviationsAverage_UF,colour="darkred")+
	geom_label(data=plotForm_UF,aes(x=rownames(plotForm_UF),y=-0.05,label=n))

pdf(paste0(outputDir,dirSep,"phyllotaxis_CalbaFlavescens_deviationsPerPosition_unfiltered.pdf"))
print(myplot)
dev.off()

print("All")
print(fDeviationsAverage_All)
print(plotForm_All)

myplot <- ggplot() + geom_pointrange(data=plotForm_All,aes(x=rownames(plotForm_All),y=estimate,ymin=low,ymax=high)) + 
	xlab("Flower position (old to young)") + ylab("Deviation from prediction (fraction)") +
	geom_hline(yintercept=fDeviationsAverage_All,colour="darkred")+
	geom_label(data=plotForm_All,aes(x=rownames(plotForm_All),y=-0.05,label=n))

pdf(paste0(outputDir,dirSep,"phyllotaxis_CalbaFlavescens_deviationsPerPosition_allOKdata.pdf"))
print(myplot)
dev.off()

print("Aligned")
print(fDeviationsAverage_Aligned)
print(plotForm_Aligned)

myplot <- ggplot() + geom_pointrange(data=plotForm_Aligned,aes(x=rownames(plotForm_Aligned),y=estimate,ymin=low,ymax=high)) + 
	xlab("Flower position (old to young)") + ylab("Deviation from prediction (fraction)") +
	geom_hline(yintercept=fDeviationsAverage_Aligned,colour="darkred") +
	geom_label(data=plotForm_Aligned,aes(x=rownames(plotForm_Aligned),y=-0.05,label=n))

pdf(paste0(outputDir,dirSep,"phyllotaxis_CalbaFlavescens_deviationsPerPosition_alignedData.pdf"))
print(myplot)
dev.off()

print("mixed")
print(fDeviationsAverage_mixed)
print(plotForm_mixed)

myplot <- ggplot() + geom_pointrange(data=plotForm_mixed,aes(x=rownames(plotForm_mixed),y=estimate,ymin=low,ymax=high)) + 
	xlab("Flower position (old to young)") + ylab("Deviation from prediction (fraction)") +
	geom_hline(yintercept=fDeviationsAverage_mixed,colour="darkred")+
	geom_label(data=plotForm_mixed,aes(x=rownames(plotForm_mixed),y=-0.05,label=n))

pdf(paste0(outputDir,dirSep,"phyllotaxis_CalbaFlavescens_deviationsPerPosition_mixed.pdf"))
print(myplot)
dev.off()

print("mixedAligned")
print(fDeviationsAverage_mixedAligned)
print(plotForm_mixedAligned)

myplot <- ggplot() + geom_pointrange(data=plotForm_mixedAligned,aes(x=rownames(plotForm_mixedAligned),y=estimate,ymin=low,ymax=high)) + 
	xlab("Flower position (old to young)") + ylab("Deviation from prediction (fraction)") +
	geom_hline(yintercept=fDeviationsAverage_mixedAligned,colour="darkred")+
	geom_label(data=plotForm_mixedAligned,aes(x=rownames(plotForm_mixedAligned),y=-0.05,label=n))

pdf(paste0(outputDir,dirSep,"phyllotaxis_CalbaFlavescens_deviationsPerPosition_mixedAligned.pdf"))
print(myplot)
dev.off()



