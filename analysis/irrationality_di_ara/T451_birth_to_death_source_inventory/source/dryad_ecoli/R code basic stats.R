### This script analyzes some of the E. coli experiment from Paris with only the 516 early daughters that produced late daughters included
# 
setwd("C:/Users/usteiner/Desktop/Imperfect assymetric division")

setwd("C:/Users/usteiner/OneDrive - Syddansk Universitet/Imperfect assymetric division/R code Evolution")

# Clear everything
#rm(list=ls(all=TRUE))

library(coda)

library(stats)
library(languageR)

library(lme4)
library(plotrix)
library(Hmisc)
library(reshape2)
library(popbio)
library(nls2)
library(ggplot2)
library(scales)
library(gridExtra)
library(grid)


# load data.1 which is columns of: 1)Folder, 2)Slicenumber, 3)Death first cell, 4)death second cell, 5)death third cell, 6)average div.1, 7)average div.2, 8)average div.3,  
#

data.1<-read.csv("C:/Users/usteiner/Desktop/Imperfect assymetric division/R_output2_readin2.csv", header = T)

length(which(data.1$Death.1==1))

data.1$Folder <- factor(data.1$Folder)


#excludes death 0 for first and second cohort
data.1d<-subset(data.1, Death.1>0)
data.1<-subset(data.1d, Death.2>0)


#creates a list of subdata (only Death.1 and death.2 data included) and then does histogram with an at death distribution for initial cells and last daughters
list<-data.1[,c(3,4)]

list[list>=(30*15)]<-((30*15)-1)
median(list[,c(1)]/15)
median(list[,c(2)]/15)
mean(list[,c(1)]/15)
is.numeric(coM[2])

#par(mfrow=c(1,2))
ggplot(list, aes(x=list[,c(1)]/15)) + geom_histogram(aes(y=..density..),binwidth=5) + theme_grey(base_size = 25) + xlab("Lifespan (hours)")+   ylab("Proportion") 

ggplot(list, aes(x=list[,c(2)]/15)) + geom_histogram(aes(y=..density..),binwidth=5) + theme_grey(base_size = 25) + xlab("Lifespan (hours)")+   ylab("Proportion")

####this is the plot (Fig. 1) 
p1<-ggplot(list, aes(x=list[,c(1)]/15)) + geom_histogram(aes(y=(..count..)/sum(..count..)),binwidth=5) + 
  theme_bw(base_size = 16) + scale_y_continuous(labels = percent)+xlab("Lifespan (hours)") +   
  ylab("Proportion") + expand_limits(y=c(0,0.52)) + #ggtitle("E)") + 
  geom_vline(xintercept = median(list[,c(1)]/15), colour="red", linetype = "dashed", size=1) + 
  geom_vline(xintercept = mean(list[,c(1)]/15), colour="red", size=1) + 
  geom_text(x=0,y=0.5,label="E)",size=4)
  #theme(plot.title = element_text(hjust = 0.01, , vjust=-2.2))
p2<-ggplot(list, aes(x=list[,c(2)]/15)) + geom_histogram(aes(y=(..count..)/sum(..count..)),binwidth=5) + 
  theme_bw(base_size = 16) + scale_y_continuous(labels = percent)+xlab("Lifespan (hours)") +   
  ylab("Proportion") + expand_limits(y=c(0,0.52)) + #ggtitle("F)")+ 
  geom_vline(xintercept = median(list[,c(2)]/15), colour="red", linetype = "dashed", size=1) + 
  geom_vline(xintercept = mean(list[,c(2)]/15), colour="red", size=1) + 
  geom_text(x=0,y=0.5,label="F)",size=4)
  #theme(plot.title = element_text(hjust = 0.01, , vjust=-2.2))
grid.arrange(p1,p2,ncol=2)
names(list)



#estimates mean age at death and CV
mean1<-mean(list[,c(1)]/15, na.rm=T)
sd1<-sd(list[,c(1)]/15, na.rm=T)
mean2<-mean(list[,c(2)]/15, na.rm=T)
sd2<-sd(list[,c(2)]/15, na.rm=T)
cv1<-sd1/mean1
cv2<-sd2/mean2


#creates a list of subdata includes death at time 0 for death.3
list2<-data.1[,c(3,4,5)]
max(list2)
names(list2)
list2<-subset(list2, Death.3>0)
dim(list2)
#multhist(list2, breaks=seq(0,850,by=my.bin.width), col=c("red","blue","grey"))
list2[list2>=(30*15)]<-((30*15)-1)
median(list2[,c(1)]/15)
median(list2[,c(2)]/15)
median(list2[,c(3)]/15)

sd(list2[,c(1)]/15)/mean(list2[,c(1)]/15, na.rm=T)
sd(list2[,c(2)]/15)/mean(list2[,c(2)]/15, na.rm=T)
sd(list2[,c(3)]/15)/mean(list2[,c(3)]/15, na.rm=T)



####This is the plot for the Supplement Ext. Fig. 
p3<-ggplot(list2, aes(x=list2[,c(1)]/15)) + geom_histogram(aes(y=(..count..)/sum(..count..)),binwidth=5) + 
  theme_bw(base_size = 16) + theme(plot.title = element_text(size = 16)) + scale_y_continuous(labels = percent)+
  geom_vline(xintercept = median(list2[,c(1)]/15, na.rm=T), colour="red", linetype = "dashed", size=2) + 
  geom_vline(xintercept = mean(list2[,c(1)]/15, na.rm=T), colour="red", size=2) + 
  xlab("Lifespan (hours)") +   ylab("Proportion") + expand_limits(y=c(0,0.61)) + ggtitle("A) early daughters\n ")
p4<-ggplot(list2, aes(x=list2[,c(2)]/15)) + geom_histogram(aes(y=(..count..)/sum(..count..)),binwidth=5) + 
  theme_bw(base_size = 16) + theme(plot.title = element_text(size = 16)) + scale_y_continuous(labels = percent)+
  geom_vline(xintercept = median(list2[,c(2)]/15, na.rm=T), colour="red", linetype = "dashed", size=2) + 
  geom_vline(xintercept = mean(list2[,c(2)]/15, na.rm=T), colour="red", size=2) + 
  xlab("Lifespan (hours)") +   ylab("Proportion") + expand_limits(y=c(0,0.61)) + ggtitle("B) late daughters\n ")
p5<-ggplot(list2, aes(x=list2[,c(3)]/15)) + geom_histogram(aes(y=(..count..)/sum(..count..)),binwidth=5) + 
  theme_bw(base_size = 16) + theme(plot.title = element_text(size = 16)) + scale_y_continuous(labels = percent)+
  geom_vline(xintercept = median(list2[,c(3)]/15, na.rm=T), colour="red", linetype = "dashed", size=2) + 
  geom_vline(xintercept = mean(list2[,c(3)]/15, na.rm=T), colour="red", size=2) + 
  xlab("Lifespan (hours)") +   ylab("Proportion") + expand_limits(y=c(0,0.61)) + ggtitle("C) second gen.\nlate daughters")
grid.arrange(p3,p4,p5,ncol=3)
s8<-grid.arrange(p3,p4,p5,ncol=3)

#sqrt, sqrt transformed data behaves fairly well Tests for correlation in age at death between initial cells and last daughters
model.1<-glm(sqrt(Death.2/15)~sqrt(Death.1/15), family=Gamma, data=data.1)
model.2<-glm(sqrt(Death.2/15)~sqrt(Death.1/15), family=gaussian, data=data.1)
model.3<-glm(sqrt(Death.2/15)~1, family=gaussian, data=data.1)
model.3.1<-glm(sqrt(Death.2/15)~I(Death.1/15), family=gaussian, data=data.1)
#summary(model.1)
summary(model.2)
summary(model.3)
summary(model.3.1)

Pred<-predict(model.2, type="response") # predicted values


### Fig. 2G
p1G<-ggplot(data.1, aes(x=sqrt(data.1$Death.1/15), y=sqrt(data.1$Death.2/15))) +
  geom_point(shape=1, ) + theme_bw(base_size = 16) + xlab(expression(paste("Lifespan early d. (", sqrt(h),")")))+   ylab(expression(paste("Lifespan late d. (", sqrt(h),")"))) +
  geom_text(x=0.8,y=6.8,label="G)",size=4)
  



#removes Death.3==0

data.2<-data.1[data.1$Death.3>"0",]
names(data.2)
data.2

#creates a list of subdata (only Death.1 and death.2 data included) need to remove death for death.3
list3<-data.2[,c(3,4,5)]
dim(list3)
max(list3)

### Extended data Fig. S10heritability
s9<-ggplot(data.2, aes(x=sqrt(data.2$Death.2/15), y=sqrt(data.2$Death.3/15))) +
  geom_point(shape=1) + theme_bw(base_size = 16) + xlab("Lifespan late d. \n(mothers)")+   ylab("Lifespan sec. g. late d. \n(daughters)")


model.5<-glm((Death.3)~(Death.2)+Death.2, family=Gamma, data=data.2)
model.6<-glm((Death.3)~(Death.2), family=gaussian, data=data.2)
model.7<-glm((Death.3)~(Death.2)+I(Death.2^2), family=Gamma, data=data.2)
summary(model.5)
summary(model.6)
summary(model.7)

list1<-data.2[,c(3,4,5)] #only selects death.1 death.2 death.3 data

#####load data for length of cells and division of cells
data.3<-read.csv("C:/Users/usteiner/Desktop/Imperfect assymetric division/leng3.1.csv", header = T)
data.4<-read.csv("C:/Users/usteiner/Desktop/Imperfect assymetric division/div2.1.csv", header = T)

data.3<-data.3[,c(1:4,6:ncol(data.3))]
data.4<-data.4[,c(1:4,6:ncol(data.4))]

data.3b<-data.3[data.3$CellNum==2,] #selects all data of late daughters
data.3a<-data.3[data.3$CellNum==1,] #selects all data of initial cells/early daughters/mothers
data.3c<-data.3[data.3$CellNum==3,] #selects all data of second generation late daughters

data.3a <- merge(data.3a,data.3b[,c(1:2)],by=c("Folder","SliceNum")) 

data.3 <- rbind(data.3a, data.3b,data.3c) #now new data.3 only contains the 516 mother cells that have daughter cells

data.4b<-data.4[data.4$CellNum==2,] #selects all data of late daughters
data.4a<-data.4[data.4$CellNum==1,] #selects all data of initial cells/early daughters/mothers
data.4c<-data.4[data.4$CellNum==3,] #selects all data of second generation late daughters

data.4a <- merge(data.4a,data.4b[,c(1:2)],by=c("Folder","SliceNum")) 

data.4 <- rbind(data.4a, data.4b,data.4c) #now new data.4 only contains the 516 mother cells that have daughter cells

#data.3.1 is size "Folder","SliceNum","CellNum","Death","Time","Size"
# kind of reverse pivot, stacks values on top of each other creates new time variable and convertes Size and Time in numeric variable
data.3.1 <- melt(data.3, id=c("Folder","SliceNum","CellNum","Death"), rm.nan=F) 
data.3.1 <- data.3.1[complete.cases(data.3.1), ]
data.3.1 <-as.data.frame(sapply(data.3.1,gsub,pattern="Size",replacement=""))
colnames(data.3.1)<-c( "Folder","SliceNum","CellNum","Death","Time","Size")
data.3.1$Size<-as.numeric(levels(data.3.1$Size))[data.3.1$Size]
data.3.1$Time<-as.numeric(levels(data.3.1$Time))[data.3.1$Time]
names(data.3.1)

#data.4.1 is division "Folder","SliceNum","CellNum","Death","Time","Div"
data.4.1 <- melt(data.4, id=c("Folder","SliceNum","CellNum","Death"), rm.nan=F) 
data.4.1 <- data.4.1[complete.cases(data.4.1), ]
data.4.1 <-as.data.frame(sapply(data.4.1,gsub,pattern="Div",replacement=""))
colnames(data.4.1)<-c( "Folder","SliceNum","CellNum","Death","Time","Div")
data.4.1$Div<-as.numeric(levels(data.4.1$Div))[data.4.1$Div]
data.4.1$Time<-as.numeric(levels(data.4.1$Time))[data.4.1$Time]
#creates new column with Div only 0 and 1 
#data.4.1["DivWO2"]<-NA
data.4.1$Div2<-data.4.1$Div
data.4.1$Div2[data.4.1$Div2==2]<-1
data.4.1$Div2[data.4.1$Div2==3]<-1

###hist LRS number of divisions
data.4LRS<-data.4[,c(1:4)]
data.4LRS[,5]<-rowSums(data.4[,5:ncol(data.4)],na.rm=TRUE)
colnames(data.4LRS)[5]<-"LRS"
names(data.4LRS)
dim(data.4LRS)

#creates a list of subdata (only Death.1 and death.2 data included) and then does histogram with at at death distribution for initial cells and last daughters
data.4LRS1<-data.4LRS[data.4LRS$CellNum==1,]

data.4LRS2<-data.4LRS[data.4LRS$CellNum==2,]

data.4LRS3<-data.4LRS[data.4LRS$CellNum==3,]
names(data.4LRS1)


### Fig.S6
p8<-  ggplot(data.4LRS1, aes(x=data.4LRS1$Death/15, y=data.4LRS1$LRS)) +
  geom_point(shape=1) + theme_bw(base_size = 16) + xlab("Lifespan (hours) \n(early daughters)")+   ylab("Lifetime reproductive success\n(number of divisions)") +
  ylim(0,90) + ggtitle("A)")

p9<-ggplot(data.4LRS2, aes(x=data.4LRS2$Death/15, y=data.4LRS2$LRS)) +
    geom_point(shape=1) + theme_bw(base_size = 16) + xlab("Lifespan (hours) \n(late daughters)") +ylab("") +
  ylim(0,90)+ ggtitle("B)")

p10<-ggplot(data.4LRS3, aes(x=data.4LRS3$Death/15, y=data.4LRS3$LRS)) +
  geom_point(shape=1) + theme_bw(base_size = 16) + xlab("Lifespan (hours) \n(second gen. late daughters)")+ylab("") +
  ylim(0,90)+ ggtitle("C)")
grid.arrange(p8,p9,p10,ncol=3)
s5<-grid.arrange(p8,p9,p10,ncol=3)


par(mfrow=c(1,1))

max(data.4LRS1[,5])
hist(data.4LRS1[,5], breaks = 44)

max(data.4LRS2[,5])
hist(data.4LRS2[,5], breaks = 44)

max(data.4LRS3[,5])
hist(data.4LRS3[,5], breaks = 44)

#averages of hours for division
data.5<-data.4[,c(1:4)]
names(data.5)
for (i in 0:78){data.5[paste("AverDiv",i+5)]<-rowMeans(data.4[,4+(15*i+1:15)],na.rm=TRUE)}
dim(data.5)



dummy<-colMeans(data.5,na.rm=TRUE)
dummy<-cbind(dummy,apply(data.5,2,var,na.rm=T)) 

colnames(dummy)<-c("AvDivRate", "VarDivrate")
agedivrate<-dummy[5:nrow(dummy),]
agedivrate<-cbind(agedivrate,seq(1:nrow(agedivrate)))

agedivrate<-cbind(agedivrate,sqrt(agedivrate[,2]))

colnames(agedivrate)<-c("AvDivRate", "VarDivrate","Time", "SD_Divrate")
plot(AvDivRate~Time,data=agedivrate, xlim=c(0,60), ylim=c(0,0.159))

agedivrate<-data.frame(agedivrate)
names(agedivrate)


### reverse from age at death for div rate

data.4rev = data.4

for (ii in 1:nrow(data.4) ) {
  dummy=max(which(sapply(data.4[ii,5:ncol(data.4)], is.finite)==TRUE))+4
  data.4rev[ii, 5:dummy] = data.4[ii,dummy:5]
}

#cluster above age 30h reverse
data.4rev.30<-data.4rev[,c(1:4)]
names(data.4rev.30)
for (i in 0:29){data.4rev.30[paste("AverDiv",i+5)]<-rowMeans(data.4rev[,4+(15*i+1:15)],na.rm=TRUE)*15}
data.4rev.30[,dim(data.4rev.30)[2]+1]<-(rowMeans(data.4rev[,(15*i+20):(dim(data.4rev)[2])],na.rm=TRUE))*15
colnames(data.4rev.30)[35]<-"AverDiv 35"

data.4rev.1 <- data.4rev.30[data.4rev.30$CellNum==1,]
data.4rev.2 <- data.4rev.30[data.4rev.30$CellNum==2,]
data.4rev.3 <- data.4rev.30[data.4rev.30$CellNum==3,]

## rev div first cohort cells
dummy<-colMeans(data.4rev.1,na.rm=TRUE)
dummy<-cbind(dummy,apply(data.4rev.1,2,var,na.rm=T)) 
dummy<-cbind(dummy,apply(data.4rev.1,2,sd,na.rm=T))
dummy<-cbind(dummy,(sqrt(dummy[,2]/colSums(!is.na(data.4rev.1)))))


colnames(dummy)<-c("AvDivRate", "VarDivrate", "SDDivrate", "SERRDivrate")
agedivrate<-dummy[5:nrow(dummy),]
agedivrate<-cbind(agedivrate,seq(1:nrow(agedivrate)))

colnames(agedivrate)<-c("AvDivRate", "VarDivrate", "SDDivrate", "SERRDivrate","Time")

agedivrate<-data.frame(agedivrate)
names(agedivrate)


names(data.4rev.1)
#data.4rev.1 is div "Folder","SliceNum","CellNum","Death","Time","Div"
# kind of reverse pivot, stacks values on top of each other creates new time variable and convertes Size and Time in numeric variable
data.4rev.11 <- melt(data.4rev.1, id=c("Folder","SliceNum","CellNum","Death"), rm.nan=F) 
data.4rev.11 <- data.4rev.11[complete.cases(data.4rev.11), ]
data.4rev.11 <-as.data.frame(sapply(data.4rev.11,gsub,pattern="AverDiv",replacement=""))
colnames(data.4rev.11)<-c( "Folder","SliceNum","CellNum","Death","Time","AverDiv")
data.4rev.11$AverDiv<-as.numeric(levels(data.4rev.11$AverDiv))[data.4rev.11$AverDiv]
data.4rev.11$Time<-as.numeric(levels(data.4rev.11$Time))[data.4rev.11$Time]
data.4rev.11$Time<-data.4rev.11$Time-4
names(data.4rev.11)

model.4rev.11.1<-glm(AverDiv~1, data=data.4rev.11)
model.4rev.11.2<-glm(AverDiv~Time, data=data.4rev.11)
model.4rev.11.3<-glm(AverDiv~Time+I(Time^2), data=data.4rev.11)

summary(model.4rev.11.1)
summary(model.4rev.11.2)
summary(model.4rev.11.3)
#summary(model.7.11.4)

AIC(model.4rev.11.1, model.4rev.11.2, model.4rev.11.3)

par(mfrow=c(1,1))

plot(agedivrate$Time, agedivrate$AvDivRate, type="n", xlim=c(0,32), ylim=c(0,2.8), ann=FALSE)
with (data = agedivrate, expr = errbar(Time, AvDivRate, AvDivRate+SERRDivrate, AvDivRate-SERRDivrate, add=T, pch=0.001, cap=.01))
#lines(data.4rev.11$Time, model.4rev.11.3$fitted, type="l", col="red", lwd=3)
mtext(side = 2, text = "(early daughters)", line = 2)
mtext(side = 2, text = "Division rate", line = 3)
mtext(side = 1, text = "Time before death", line = 2)
mtext(side = 1, text = "(in hours; Death = 0)", line = 3)


newd<-t(rbind(data.4rev.11$Time,predict(model.4rev.11.3))) 
newd<-data.frame(newd)
colnames(newd) <- c("Time","Predi")
names(newd)
dim(newd)

#Fig.S7A
p12<-
  ggplot(agedivrate, aes(x=Time, y=AvDivRate)) +
  geom_point(shape=1, size=3) +    # Use hollow circles
  theme_bw(base_size = 16) +
  ylim(0, 3) +
  xlab("Time before death\n (hours; Death = 0)")+
  ylab("Division rate\n(early daughters)") +
  ggtitle("A)") +
  geom_errorbar(aes(ymin = AvDivRate-SERRDivrate,ymax = AvDivRate+SERRDivrate), size=0.5)
  #geom_line(data = newd, aes(x = Time, y =Predi), colour="red", size=1 )


## rev div second cohort cells
dummy<-colMeans(data.4rev.2,na.rm=TRUE)
dummy<-cbind(dummy,apply(data.4rev.2,2,var,na.rm=T)) 
dummy<-cbind(dummy,apply(data.4rev.2,2,sd,na.rm=T))
dummy<-cbind(dummy,(sqrt(dummy[,2]/colSums(!is.na(data.4rev.2)))))


colnames(dummy)<-c("AvDivRate", "VarDivrate", "SDDivrate", "SERRDivrate")
agedivrate<-dummy[5:nrow(dummy),]
agedivrate<-cbind(agedivrate,seq(1:nrow(agedivrate)))

colnames(agedivrate)<-c("AvDivRate", "VarDivrate", "SDDivrate", "SERRDivrate","Time")

agedivrate<-data.frame(agedivrate)
names(agedivrate)


names(data.4rev.2)
#data.4rev.2 is div "Folder","SliceNum","CellNum","Death","Time","Div"
# kind of reverse pivot, stacks values on top of each other creates new time variable and convertes Size and Time in numeric variable
data.4rev.21 <- melt(data.4rev.2, id=c("Folder","SliceNum","CellNum","Death"), rm.nan=F) 
data.4rev.21 <- data.4rev.21[complete.cases(data.4rev.21), ]
data.4rev.21 <-as.data.frame(sapply(data.4rev.21,gsub,pattern="AverDiv",replacement=""))
colnames(data.4rev.21)<-c( "Folder","SliceNum","CellNum","Death","Time","AverDiv")
data.4rev.21$AverDiv<-as.numeric(levels(data.4rev.21$AverDiv))[data.4rev.21$AverDiv]
data.4rev.21$Time<-as.numeric(levels(data.4rev.21$Time))[data.4rev.21$Time]
data.4rev.21$Time<-data.4rev.21$Time-4
names(data.4rev.21)

model.4rev.21.1<-glm(AverDiv~1, data=data.4rev.21)
model.4rev.21.2<-glm(AverDiv~Time, data=data.4rev.21)
model.4rev.21.3<-glm(AverDiv~Time+I(Time^2), data=data.4rev.21)

summary(model.4rev.21.1)
summary(model.4rev.21.2)
summary(model.4rev.21.3)

AIC(model.4rev.21.1, model.4rev.21.2, model.4rev.21.3)

newd<-t(rbind(data.4rev.21$Time,predict(model.4rev.21.3))) 
newd<-data.frame(newd)
colnames(newd) <- c("Time","Predi")
names(newd)
dim(newd)

#Fig. S7B
p13<-
ggplot(agedivrate, aes(x=Time, y=AvDivRate)) +
  geom_point(shape=1, size=3) +    # Use hollow circles
  theme_bw(base_size = 16) +
  ylim(0, 3) +
  xlab("Time before death\n (hours; Death = 0)")+
  ylab("Division rate\n(late daughters)") +
  ggtitle("B)") +
  geom_errorbar(aes(ymin = AvDivRate-SERRDivrate,ymax = AvDivRate+SERRDivrate), size=0.5) #+
  #geom_line(data = newd, aes(x = Time, y =Predi), colour="red", size=1 )

## rev div third cohort cells
dummy<-colMeans(data.4rev.3,na.rm=TRUE)
dummy<-cbind(dummy,apply(data.4rev.3,2,var,na.rm=T)) 
dummy<-cbind(dummy,apply(data.4rev.3,2,sd,na.rm=T))
dummy<-cbind(dummy,(sqrt(dummy[,2]/colSums(!is.na(data.4rev.3)))))


colnames(dummy)<-c("AvDivRate", "VarDivrate", "SDDivrate", "SERRDivrate")
agedivrate<-dummy[5:nrow(dummy),]
agedivrate<-cbind(agedivrate,seq(1:nrow(agedivrate)))

colnames(agedivrate)<-c("AvDivRate", "VarDivrate", "SDDivrate", "SERRDivrate","Time")

agedivrate<-data.frame(agedivrate)
names(agedivrate)


names(data.4rev.3)
#data.4rev.3 is div "Folder","SliceNum","CellNum","Death","Time","Div"
# kind of reverse pivot, stacks values on top of each other creates new time variable and convertes Size and Time in numeric variable
data.4rev.31 <- melt(data.4rev.3, id=c("Folder","SliceNum","CellNum","Death"), rm.nan=F) 
data.4rev.31 <- data.4rev.31[complete.cases(data.4rev.31), ]
data.4rev.31 <-as.data.frame(sapply(data.4rev.31,gsub,pattern="AverDiv",replacement=""))
colnames(data.4rev.31)<-c( "Folder","SliceNum","CellNum","Death","Time","AverDiv")
data.4rev.31$AverDiv<-as.numeric(levels(data.4rev.31$AverDiv))[data.4rev.31$AverDiv]
data.4rev.31$Time<-as.numeric(levels(data.4rev.31$Time))[data.4rev.31$Time]
data.4rev.31$Time<-data.4rev.31$Time-4
names(data.4rev.31)

model.4rev.31.1<-glm(AverDiv~1, data=data.4rev.31)
model.4rev.31.2<-glm(AverDiv~Time, data=data.4rev.31)
model.4rev.31.3<-glm(AverDiv~Time+I(Time^2), data=data.4rev.31)

summary(model.4rev.31.1)
summary(model.4rev.31.2)
summary(model.4rev.31.3)

AIC(model.4rev.31.1, model.4rev.31.2, model.4rev.31.3)

newd<-t(rbind(data.4rev.31$Time,predict(model.4rev.31.3))) 
newd<-data.frame(newd)
colnames(newd) <- c("Time","Predi")
names(newd)
dim(newd)

#Fig. S7C
p14<-
  ggplot(agedivrate, aes(x=Time, y=AvDivRate)) +
  geom_point(shape=1, size=3) +    # Use hollow circles
  theme_bw(base_size = 16) +
  ylim(0, 3) +
  xlab("Time before death\n (hours; Death = 0)")+
  ylab("Division rate\n(sec. gen. late daught.)") +
  ggtitle("C)") +
  geom_errorbar(aes(ymin = AvDivRate-SERRDivrate,ymax = AvDivRate+SERRDivrate), size=0.5) #+
  #geom_line(data = newd, aes(x = Time, y =Predi), colour="red", size=1 )

grid.arrange(p12,p13,p14,ncol=3)
s6<-grid.arrange(p12,p13,p14,ncol=3)

#cluster above age 30h normal division rate
data.5.1<-data.4[,c(1:4)]
names(data.5.1)
for (i in 0:30){data.5.1[paste("AverDiv",i+5)]<-rowMeans(data.4[,4+(15*i+1:15)],na.rm=TRUE)*15}
data.5.1[,dim(data.5.1)[2]+1]<-(rowMeans(data.4[,(15*i+20):(dim(data.4)[2])],na.rm=TRUE))*15
dim(data.5.1)

dummy<-colMeans(data.5.1,na.rm=TRUE)
dummy<-cbind(dummy,apply(data.5.1,2,var,na.rm=T)) 
dummy<-cbind(dummy,apply(data.5.1,2,sd,na.rm=T))
dummy<-cbind(dummy,(sqrt(dummy[,2]/colSums(!is.na(data.5.1)))))


colnames(dummy)<-c("AvDivRate", "VarDivrate", "SDDivrate", "SERRDivrate")
agedivrate<-dummy[5:nrow(dummy),]
agedivrate<-cbind(agedivrate,seq(1:nrow(agedivrate)))

colnames(agedivrate)<-c("AvDivRate", "VarDivrate", "SDDivrate", "SERRDivrate","Time")
plot(AvDivRate~Time,data=agedivrate, xlim=c(0,32), ylim=c(0,2.5))

agedivrate<-data.frame(agedivrate)
names(agedivrate)

# add error bars
data.frame(agedivrate)
plot(agedivrate$Time, agedivrate$AvDivRate, type="n", xlim=c(0,32), ylim=c(0,2.5), xlab = "Age in hours", ylab = "Division Rate per hour", main = "Division Rate All Cells")
with (data = agedivrate, expr = errbar(Time, AvDivRate, AvDivRate+SERRDivrate, AvDivRate-SERRDivrate, add=T, pch=0.001, cap=.01))

#only initial cells for division
data.6<-data.4[data.4$CellNum==1,]
dim(data.6)

#only last cells (last daugther) cells for division
data.7<-data.4[data.4$CellNum==2,]
dim(data.7)

#only last cells  of last daugther cells for division
data.8<-data.4[data.4$CellNum==3,]
dim(data.8)

#cluster above age 30h
data.6.1<-data.6[,c(1:4)]
names(data.6.1)
for (i in 0:29){data.6.1[paste("AverDiv",i+5)]<-rowMeans(data.6[,4+(15*i+1:15)],na.rm=TRUE)*15}
data.6.1[,dim(data.6.1)[2]+1]<-(rowMeans(data.6[,(15*i+20):(dim(data.6)[2])],na.rm=TRUE))*15
colnames(data.6.1)[35]<-"AverDiv 35"



dummy<-colMeans(data.6.1,na.rm=TRUE)
dummy<-cbind(dummy,apply(data.6.1,2,var,na.rm=T)) 
dummy<-cbind(dummy,apply(data.6.1,2,sd,na.rm=T))
dummy<-cbind(dummy,(sqrt(dummy[,2]/colSums(!is.na(data.6.1)))))


colnames(dummy)<-c("AvDivRate", "VarDivrate", "SDDivrate", "SERRDivrate")
agedivrate<-dummy[5:nrow(dummy),]
agedivrate<-cbind(agedivrate,seq(1:nrow(agedivrate)))

colnames(agedivrate)<-c("AvDivRate", "VarDivrate", "SDDivrate", "SERRDivrate","Time")
plot(AvDivRate~Time,data=agedivrate, xlim=c(0,32), ylim=c(0,2.5))

agedivrate<-data.frame(agedivrate)
names(agedivrate)

agedivrateLeslie<-agedivrate[,c(1)]


names(data.6.1)
#data.6.1 is size "Folder","SliceNum","CellNum","Death","Time","Div"
# kind of reverse pivot, stacks values on top of each other creates new time variable and convertes Size and Time in numeric variable
data.6.11 <- melt(data.6.1, id=c("Folder","SliceNum","CellNum","Death"), rm.nan=F) 
data.6.11 <- data.6.11[complete.cases(data.6.11), ]
data.6.11 <-as.data.frame(sapply(data.6.11,gsub,pattern="AverDiv",replacement=""))
colnames(data.6.11)<-c( "Folder","SliceNum","CellNum","Death","Time","AverDiv")
data.6.11$AverDiv<-as.numeric(levels(data.6.11$AverDiv))[data.6.11$AverDiv]
data.6.11$Time<-as.numeric(levels(data.6.11$Time))[data.6.11$Time]
data.6.11$Time<-data.6.11$Time-4
names(data.6.11)

model.6.11.1<-glm(AverDiv~1, data=data.6.11)
model.6.11.2<-glm(AverDiv~Time, data=data.6.11)
model.6.11.3<-glm(AverDiv~Time+I(Time^2), data=data.6.11)
#model.6.11.4<-glm(AverDiv~Time*I(Time^2), data=data.6.11)

summary(model.6.11.1)
summary(model.6.11.2)
summary(model.6.11.3)
#summary(model.6.11.4)

#plot(model.6.11.3)

AIC(model.6.11.1, model.6.11.2, model.6.11.3)

par(mfrow=c(1,1),oma=c(0,0,0,0))


newd<-t(rbind(data.6.11$Time,predict(model.6.11.3))) 
newd<-data.frame(newd)
colnames(newd) <- c("Time","Predi")
names(newd)
dim(newd)

#Fig. 2A
p15<-
  ggplot(agedivrate, aes(x=Time, y=AvDivRate)) +
  geom_point(shape=1, size=3) +    
  theme_bw(base_size = 16) +
  ylim(0, 2.7) +
  xlab("Age (hours)")+
  ylab("Division rate") +
  geom_errorbar(aes(ymin = AvDivRate-SERRDivrate,ymax = AvDivRate+SERRDivrate), size=0.5) +
  #geom_line(data = newd, aes(x = Time, y =Predi), colour="red", size=1 ) +
  ggtitle("Early daughters") +
  theme(plot.title = element_text(vjust=1.5, size=16)) +
  annotate("text", label = "A)", x = 1.5, y = 2.6, size = 4, colour = "black")

#cluster above age 30h
data.7.1<-data.7[,c(1:4)]
names(data.7.1)
for (i in 0:29){data.7.1[paste("AverDiv",i+5)]<-rowMeans(data.7[,4+(15*i+1:15)],na.rm=TRUE)*15}
data.7.1[,dim(data.7.1)[2]+1]<-(rowMeans(data.7[,(15*i+20):(dim(data.7)[2])],na.rm=TRUE))*15
colnames(data.7.1)[35]<-"AverDiv 35"
dim(data.7.1)

dummy<-colMeans(data.7.1,na.rm=TRUE)
dummy<-cbind(dummy,apply(data.7.1,2,var,na.rm=T)) 
dummy<-cbind(dummy,apply(data.7.1,2,sd,na.rm=T))
dummy<-cbind(dummy,(sqrt(dummy[,2]/colSums(!is.na(data.7.1)))))


colnames(dummy)<-c("AvDivRate", "VarDivrate", "SDDivrate", "SERRDivrate")
agedivrate<-dummy[5:nrow(dummy),]
agedivrate<-cbind(agedivrate,seq(1:nrow(agedivrate)))

colnames(agedivrate)<-c("AvDivRate", "VarDivrate", "SDDivrate", "SERRDivrate","Time")

agedivrate<-data.frame(agedivrate)

#data.7.1 is size "Folder","SliceNum","CellNum","Death","Time","Div"
# kind of reverse pivot, stacks values on top of each other creates new time variable and convertes Size and Time in numeric variable
data.7.11 <- melt(data.7.1, id=c("Folder","SliceNum","CellNum","Death"), rm.nan=F) 
data.7.11 <- data.7.11[complete.cases(data.7.11), ]
data.7.11 <-as.data.frame(sapply(data.7.11,gsub,pattern="AverDiv",replacement=""))
colnames(data.7.11)<-c( "Folder","SliceNum","CellNum","Death","Time","AverDiv")
data.7.11$AverDiv<-as.numeric(levels(data.7.11$AverDiv))[data.7.11$AverDiv]
data.7.11$Time<-as.numeric(levels(data.7.11$Time))[data.7.11$Time]
data.7.11$Time<-data.7.11$Time-4
names(data.7.11)

model.7.11.1<-glm(AverDiv~1, data=data.7.11)
model.7.11.2<-glm(AverDiv~Time, data=data.7.11)
model.7.11.3<-glm(AverDiv~Time+I(Time^2), data=data.7.11)
#model.7.11.4<-glm(AverDiv~Time*I(Time^2), data=data.7.11)

summary(model.7.11.1)
summary(model.7.11.2)
summary(model.7.11.3)
#summary(model.7.11.4)

AIC(model.7.11.1, model.7.11.2, model.7.11.3)

newd<-t(rbind(data.7.11$Time,predict(model.7.11.3))) 
newd<-data.frame(newd)
colnames(newd) <- c("Time","Predi")
names(newd)
dim(newd)

#Fig. 2B
p16<-
  ggplot(agedivrate, aes(x=Time, y=AvDivRate)) +
  geom_point(shape=1, size=3) +    
  theme_bw(base_size = 16) +
  ylim(0, 2.7) +
  xlab("Age (hours)")+
  ylab("Division rate") +
  geom_errorbar(aes(ymin = AvDivRate-SERRDivrate,ymax = AvDivRate+SERRDivrate), size=0.5) +
  #geom_line(data = newd, aes(x = Time, y =Predi), colour="red", size=1 ) +
  ggtitle("Late daughters") +
  theme(plot.title = element_text(vjust=1.5, size=16)) +
  annotate("text", label = "B)", x = 1.5, y = 2.6, size = 4, colour = "black")


#cluster above age 30h
data.8.1<-data.8[,c(1:4)]
names(data.8.1)
for (i in 0:29){data.8.1[paste("AverDiv",i+5)]<-rowMeans(data.8[,4+(15*i+1:15)],na.rm=TRUE)*15}
data.8.1[,dim(data.8.1)[2]+1]<-(rowMeans(data.8[,(15*i+20):(dim(data.8)[2])],na.rm=TRUE))*15
dim(data.8.1)

dummy<-colMeans(data.8.1,na.rm=TRUE)
dummy<-cbind(dummy,apply(data.8.1,2,var,na.rm=T)) 
dummy<-cbind(dummy,apply(data.8.1,2,sd,na.rm=T))
dummy<-cbind(dummy,(sqrt(dummy[,2]/colSums(!is.na(data.8.1)))))


colnames(dummy)<-c("AvDivRate", "VarDivrate", "SDDivrate", "SERRDivrate")
agedivrate<-dummy[5:nrow(dummy),]
agedivrate<-cbind(agedivrate,seq(1:nrow(agedivrate)))

colnames(agedivrate)<-c("AvDivRate", "VarDivrate", "SDDivrate", "SERRDivrate","Time")
#plot(AvDivRate~Time,data=agedivrate, xlim=c(0,32), ylim=c(0,2.5))

agedivrate<-data.frame(agedivrate)

#data.8.1 is size "Folder","SliceNum","CellNum","Death","Time","Div"
# kind of reverse pivot, stacks values on top of each other creates new time variable and convertes Size and Time in numeric variable
data.8.11 <- melt(data.8.1, id=c("Folder","SliceNum","CellNum","Death"), rm.nan=F) 
data.8.11 <- data.8.11[complete.cases(data.8.11), ]
data.8.11 <-as.data.frame(sapply(data.8.11,gsub,pattern="AverDiv",replacement=""))
colnames(data.8.11)<-c( "Folder","SliceNum","CellNum","Death","Time","AverDiv")
data.8.11$AverDiv<-as.numeric(levels(data.8.11$AverDiv))[data.8.11$AverDiv]
data.8.11$Time<-as.numeric(levels(data.8.11$Time))[data.8.11$Time]
data.8.11$Time<-data.8.11$Time-4
data.8.11 <- data.8.11[complete.cases(data.8.11), ]
names(data.8.11)

model.8.11.1<-glm(AverDiv~1, data=data.8.11)
model.8.11.2<-glm(AverDiv~Time, data=data.8.11)
model.8.11.3<-glm(AverDiv~Time+I(Time^2), data=data.8.11)
#model.8.11.4<-glm(AverDiv~Time*I(Time^2), data=data.8.11)

summary(model.8.11.1)
summary(model.8.11.2)
summary(model.8.11.3)
#summary(model.8.11.4)

newd<-t(rbind(data.8.11$Time,predict(model.8.11.3))) 
newd<-data.frame(newd)
colnames(newd) <- c("Time","Predi")
names(newd)
dim(newd)

#Fig. S5A
p17<-
  ggplot(agedivrate, aes(x=Time, y=AvDivRate)) +
  geom_point(shape=1, size=3) +    
  theme_bw(base_size = 16) +
  ylim(0, 2.7) +
  xlab("Age (hours)")+
  ylab("Division rate\n(second gen. late daughters)") +
  geom_errorbar(aes(ymin = AvDivRate-SERRDivrate,ymax = AvDivRate+SERRDivrate), size=0.5) +
  #geom_line(data = newd, aes(x = Time, y =Predi), colour="red", size=1 )+
  geom_text(x=2,y=2.7,label="A)",size=4)

  
#estimates lx, qx, for initial cells
dummy<-tabulate(data.1[,c(3)])

length(dummy)
dummy2<-rep(NA,(ceiling(length(dummy)/15)))
for (i in 0:(ceiling(length(dummy)/15))){dummy2[i+1]<-sum(dummy[(15*i+1:15)],na.rm=TRUE)}
dx<-dummy2
sum(dx)
dummy3<-sum(dx)-cumsum(dx)
lx<-rep(NA,(length(dummy2)+1))
lx[2:length(lx)]<-dummy3
lx[1]<-sum(dx)
age<-1:40
qx<-dx/(lx[1:length(lx)-1])
sx<-cumprod(1-qx)
survrate<-cbind(dx,lx[2:length(lx)],lx[1:length(lx)-1],age,qx,sx)
colnames(survrate)<-c("dx", "surv", "lx","age","qx","sx")

survrate30<-survrate[1:31,]
survrate30[31,1:3]<-colSums(survrate[31:40,1:3], na.rm = FALSE)
survrate30[31,5]<-(survrate30[31,1]/survrate30[31,3])
colnames(survrate30)<-c("dx", "surv", "lx","age","qx","sx")
survrate30<-data.frame(survrate30)
is.data.frame(survrate30)

save(survrate30, file = "survrate30")
write.csv(survrate30, file = "survrate30.csv")

newd1<-t(rbind(2:31,muGGM(x=0:29,par=tr2.1$opt$bestmem,KequalsL=TRUE))) 
newd1<-data.frame(newd1)
colnames(newd1) <- c("Time","Predi")
names(newd1)
dim(newd1)

p18<-
  ggplot(survrate30, aes(x=age, y=qx)) +
  geom_point(shape=1, size=3) +    
  theme_bw(base_size = 16) +
  ylim(0, 0.45) +
  labs(y=expression("Probability of death q"[x]), x=expression("Age (hours)")) +
  geom_errorbar(aes(ymin = survrate30$qx-sterMorRt,ymax = survrate30$qx+sterMorRt), size=0.5) 
  #geom_line(data = newd1, aes(x = Time, y =Predi), colour="red", size=1 ) +
  
  ggtitle("C)") +
  theme(plot.title = element_text(hjust = 0.01, , vjust=-2.2))
ageests<-rep(1:29,3)
ests<-cbind(ests, ageests)
ests1<-subset(ests, Generation==1)
ests2<-subset(ests, Generation==2)
ests3<-subset(ests, Generation==3)

p18<-
  ggplot(survrate30, aes(x=age, y=qx)) +
  geom_point(shape=1, size=3) +    
  theme_bw(base_size = 20) +
  ylim(0, 0.45) +
  labs(y=expression("Probability of death q"[x]), x=expression("Age (hours)")) 
  #geom_errorbar(aes(ymin = survrate30$qx-sterMorRt,ymax = survrate30$qx+sterMorRt), size=0.5) +
  #geom_line(data = ests1, aes(x = ageests, y =Mean), colour="red", size=1 ) +
  
  ggtitle("C)") +
  theme(plot.title = element_text(hjust = 0.01, , vjust=-2.2))

gp1c <- ggplot(data=dat1c,aes(x=age,y=qx)) +
  geom_ribbon(aes(ymin=low,ymax=high),alpha=0.7,fill="lightblue")+
  geom_line(aes(y=mean), color="red", size=1)+
  #geom_point(shape=1, size=3)+
  theme_bw(base_size = 16) +
  xlim(c(1, 30))+ylim(c(0, 0.35))+xlab("Age")+ ylab("Probability of death") +
  geom_point(aes(x=1, y=(516-dat1c$N[1])/516), color="darkgrey", size=3)+
  geom_point(aes(x=1, y=(516-dat1c$N[1])/516),shape=1, size=3) + 
  geom_text(x=2,y=0.34,label="C)",size=4)
  #ggtitle("C)") +
  #theme(plot.title = element_text(hjust = 0.01, , vjust=-2.2))

#####estimates lx, dx, qx, for death.2 cells
dummy<-tabulate(data.1[,c(4)])

length(dummy)
dummy2<-rep(NA,(ceiling(length(dummy)/15)))
for (i in 0:(ceiling(length(dummy)/15))){dummy2[i+1]<-sum(dummy[(15*i+1:15)],na.rm=TRUE)}
dx2<-dummy2
dummy3<-sum(dx2)-cumsum(dx2)
lx2<-rep(NA,(length(dummy2)+1))
lx2[2:length(lx2)]<-dummy3
lx2[1]<-sum(dx2)
qx2<-dx2/(lx2[1:(length(lx2)-1)])
sx2<-cumprod(1-qx2)


age<-1:40
agevec<-1:length(lx2)

survrate2<-cbind(dx2,lx2[2:length(lx2)],lx2[1:length(lx2)-1],agevec[1:length(lx2)-1],qx2,sx2)
colnames(survrate2)<-c("dx", "surv", "lx","age","qx","sx")

survrate30.2<-survrate2[1:31,]
survrate30.2[31,1:3]<-colSums(survrate2[31:length(agevec)-1,1:3], na.rm = FALSE)
survrate30.2[31,5]<-(survrate30.2[31,1]/survrate30.2[31,3])
colnames(survrate30.2)<-c("dx", "surv", "lx","age","qx","sx")
survrate30.2<-data.frame(survrate30.2)
is.data.frame(survrate30.2)

save(survrate30.2, file = "survrate30.2")
write.csv(survrate30.2, file = "survrate30.2.csv")


#test if late mortality plateau differs between first and second cohort cells
dummy11<-cbind(1,survrate30[survrate30$age>19,])
colnames(dummy11)[1]<-"CellNum"
dummy12<-cbind(2,survrate30.2[survrate30.2$age>19,])
colnames(dummy12)[1]<-"CellNum"
survplat<-rbind(dummy11,dummy12)
as.factor(survplat$CellNum)
model.plat.1<-glm(cbind(dx,surv)~1, family=binomial, data=survplat)
model.plat.2<-glm(cbind(dx,surv)~age, family=binomial, data=survplat)
model.plat.3<-glm(cbind(dx,surv)~CellNum, family=binomial, data=survplat)
model.plat.4<-glm(cbind(dx,surv)~CellNum+age, family=binomial, data=survplat)
model.plat.5<-glm(cbind(dx,surv)~CellNum*age, family=binomial, data=survplat)

colMeans(survrate30[survrate30$age>19,])[5]
sterrCol=(apply(survrate30[survrate30$age>19,], 2, sd)[5])/sqrt(dim(survrate30[survrate30$age>19,])[1])

colMeans(survrate30.2[survrate30.2$age>19,])[5]
sterrCol=(apply(survrate30.2[survrate30.2$age>19,], 2, sd)[5])/sqrt(dim(survrate30.2[survrate30.2$age>19,])[1])

AIC(model.plat.1,model.plat.2,model.plat.3,model.plat.4,model.plat.5)

summary(model.plat.1)
summary(model.plat.2)
summary(model.plat.3)


newd<-t(rbind(survrate30.2$age,model.b2.30.1$fitted)) 
newd<-data.frame(newd)
colnames(newd) <- c("Time","Predi")
names(newd)
dim(newd)

p19<-
  ggplot(survrate30.2, aes(x=age, y=qx)) +
  geom_point(size=5) +    
  theme_bw(base_size = 20) +
  ylim(0, 0.45) +
  labs(y=expression("Probability of death q"[x]), x=expression("Age (hours)")) +
  geom_errorbar(aes(ymin = survrate30.2$qx-sterMorRt2,ymax = survrate30.2$qx+sterMorRt2), size=0.5) +
  #geom_line(data = newd, aes(x = Time, y =Predi), colour="red", size=2 ) +
  ggtitle("D)") +
  theme(plot.title = element_text(hjust = 0.01, , vjust=-2.2))

gp1d <- ggplot(data=dat1D,aes(x=age,y=qx)) +
  geom_ribbon(aes(ymin=low,ymax=high),alpha=0.7,fill="lightblue")+
  geom_line(aes(y=mean), color="red", size=1)+
  #geom_point(size=3, shape=1)+
  theme_bw(base_size = 16) +
  geom_text(x=2,y=0.34,label="D)",size=4)+
  #ggtitle("D)") +
  #theme(plot.title = element_text(hjust = 0.01, vjust=0.5)) +
  xlim(c(1, 30))+ylim(c(0, 0.35))+xlab("Age")+ ylab("Probability of death") +
  geom_point(aes(x=1, y=(516-dat1D$N[1])/516), color="darkgrey", size=3) +
  geom_point(aes(x=1, y=(516-dat1D$N[1])/516),shape=1, size=3) 
  

t <- textGrob("")
grid.arrange(p15,p16,t,gp1c,gp1d,t,p1,p2,p1G, ncol=3)


####estimates lx, dx, qx, for death.3 cells
dumm<-data.1[data.1$Death.3>"0",]
dim(dumm)
dummy<-tabulate(dumm[,c(5)])

length(dummy)
dummy2<-rep(NA,(ceiling(length(dummy)/15)))
for (i in 0:(ceiling(length(dummy)/15))){dummy2[i+1]<-sum(dummy[(15*i+1:15)],na.rm=TRUE)}
dx3<-dummy2
dummy3<-sum(dx3)-cumsum(dx3)
lx3<-rep(NA,(length(dummy2)+1))
lx3[2:(length(dummy3)+1)]<-dummy3
lx3[1]<-sum(dx3)
qx3<-dx3/(lx3[1:(length(lx3)-1)])
sx3<-cumprod(1-qx3)

agevec<-1:length(lx3)

age<-1:40
agevec<-1:length(lx3)

survrate3<-cbind(dx3,lx3[2:length(lx3)],lx3[1:length(lx3)-1],agevec[1:length(lx3)-1],qx3,sx3)
colnames(survrate3)<-c("dx", "surv", "lx","age","qx","sx")

survrate30.3<-survrate3[1:31,]
survrate30.3[31,1:3]<-colSums(survrate3[31:length(agevec)-1,1:3], na.rm = FALSE)
survrate30.3[31,5]<-(survrate30.3[31,1]/survrate30.3[31,3])
colnames(survrate30.3)<-c("dx", "surv", "lx","age","qx","sx")
survrate30.3<-data.frame(survrate30.3)
is.data.frame(survrate30.3)

save(survrate30.3, file = "survrate30.3")
write.csv(survrate30.3, file = "survrate30.3.csv")

newd<-t(rbind(survrate30.3$age,model.b3.30.3$fitted)) 
newd<-data.frame(newd)
colnames(newd) <- c("Time","Predi")
names(newd)
dim(newd)

p20<-
  ggplot(survrate30.3, aes(x=age, y=qx)) +
  geom_point(size=5)+    
  theme_bw(base_size = 20) +
  #ylim(0, 0.45) +
  xlab("Age (hours)")+
  ylab(expression(atop("Probability of death q"[x],paste("(second generation late daughters)")))) +
  geom_errorbar(aes(ymin = qx3[1:31]-CIMorRt3[1:31],ymax = qx3[1:31]+CIMorRt3[1:31]), size=0.5) +
  #geom_line(data = newd, aes(x = Time, y =Predi), colour="red", size=2 ) +
  ggtitle("B)") +
  theme(plot.title = element_text(hjust = 0))

gp1CS <- ggplot(data=dat1CS,aes(x=age,y=qx)) +
  geom_ribbon(aes(ymin=low,ymax=high),alpha=0.7,fill="lightblue")+
  geom_line(aes(y=mean), color="red", size=1)+
  #geom_point(size=3, shape=1)+
  theme_bw(base_size = 16) +
  geom_text(x=2,y=0.38,label="B)",size=4)+
  #ggtitle("D)") +
  #theme(plot.title = element_text(hjust = 0.01, vjust=0.5)) +
  xlim(c(1, 30))+ylim(c(0, 0.4))+xlab("Age")+ ylab("Probability of death") +
  geom_point(aes(x=1, y=(298-dat1CS$N[1])/298), color="darkgrey", size=3)


grid.arrange(p17,gp1CS, ncol=2)


survrate3<-cbind(dx3,lx3[2:length(lx3)],lx3[1:length(lx3)-1],agevec[1:length(lx3)-1],qx3)
colnames(survrate3)<-c("dx", "surv", "lx","age","qx")

survrate30.3<-survrate3[1:31,]
survrate30.3[31,1:3]<-colSums(survrate3[31:length(agevec)-1,1:3], na.rm = FALSE)
survrate30.3[31,5]<-(survrate30.3[31,1]/survrate30.3[31,3])
colnames(survrate30.3)<-c("dx", "surv", "lx","age","qx")
survrate30.3<-data.frame(survrate30.3)
is.data.frame(survrate30.3)


### check if first qx of second and third cohort cell differs from late age mortality plateau of first cohort cells (>age 19)
#first cohortcells
colSums(survrate30[survrate30$age>19,])[1:2]
#colMeans(survrate30[survrate30$age>19,])[5]
survrate30.2[1,1:2]
survrate30.3[1,1:2]

chisqtestMatrix1 <- rbind(t(colSums(survrate30[survrate30$age>19,])[1:2]),survrate30.2[1,1:2],survrate30.3[1,1:2])

chisq.test(chisqtestMatrix1)

chisq.test(chisqtestMatrix1, simulate.p.value = T, B = 10000)

#####Growth rate
names(data.3)
dim(data.3)


#growth rates
data.3g<-data.3[,c(1:4)]
for (i in 1:1194){data.3g[paste("Growth",i)]<-(data.3[,5+i]/data.3[,4+i])}
data.3g1<-data.3g
#makes sure no growth beyond age of death
for (i in 1:(dim(data.3g)[1])){data.3g1[i,c((data.3g[i,4]+4):(dim(data.3g)[2]))]<-NaN}

#removes cell that devide for growth rates
data.3g1[data.3g1<0.8] <- NaN
data.3g1[,c(1:4)]<-data.3g[,c(1:4)]
names(data.3g1)

#averages of hours for growth
data.3g2<-data.3g1[,c(1:4)]
names(data.3g2)
for (i in 0:29){data.3g2[paste("Growth",i+1)]<-rowMeans(data.3g1[,4+(15*i+1:15)],na.rm=TRUE)}
data.3g2[,dim(data.3g2)[2]+1]<-(rowMeans(data.3g1[,(15*i+20):(dim(data.3g1)[2])],na.rm=TRUE))
colnames(data.3g2)[35]<-"Growth 31"
names(data.3g2)
dim(data.3g2)

#data.3g2a is size "Folder","SliceNum","CellNum","Death","Time","Div"
# kind of reverse pivot, stacks values on top of each other creates new time variable and convertes growth and Time in numeric variable
data.3g2a <- melt(data.3g2, id=c("Folder","SliceNum","CellNum","Death"), rm.nan=F) 
data.3g2a <- data.3g2a[complete.cases(data.3g2a), ]
data.3g2a <-as.data.frame(sapply(data.3g2a,gsub,pattern="Growth",replacement=""))
colnames(data.3g2a)<-c( "Folder","SliceNum","CellNum","Death","Time","Growth")
data.3g2a$Growth<-as.numeric(levels(data.3g2a$Growth))[data.3g2a$Growth]
data.3g2a$Time<-as.numeric(levels(data.3g2a$Time))[data.3g2a$Time]
names(data.3g2a)


#only initial cells for growth lim age 30
data.3g21<-data.3g2a[data.3g2a$CellNum==1,]
data.3g21 <- data.3g21[complete.cases(data.3g21), ]
dim(data.3g21)
names(data.3g21)

model.g.1.1<-glm(data.3g21$Growth~1, data=data.3g21)
model.g.1.2<-glm(data.3g21$Growth~data.3g21$Time, data=data.3g21)
model.g.1.3<-glm(data.3g21$Growth~data.3g21$Time+I(data.3g21$Time^2), data=data.3g21)
model.g.1.4<-glm(data.3g21$Growth~data.3g21$Time*I(data.3g21$Time^2), data=data.3g21)

summary(model.g.1.1)
summary(model.g.1.2)
summary(model.g.1.3)
summary(model.g.1.4)

AIC(model.g.1.1,model.g.1.2,model.g.1.3,model.g.1.4)


#only second cells for growth lim age 30
data.3g22<-data.3g2a[data.3g2a$CellNum==2,]
data.3g22 <- data.3g22[complete.cases(data.3g22), ]
dim(data.3g22)
names(data.3g22)

model.g.2.1<-glm(data.3g22$Growth~1, data=data.3g22)
model.g.2.2<-glm(data.3g22$Growth~data.3g22$Time, data=data.3g22)
model.g.2.3<-glm(data.3g22$Growth~data.3g22$Time+I(data.3g22$Time^2), data=data.3g22)
model.g.2.4<-glm(data.3g22$Growth~data.3g22$Time*I(data.3g22$Time^2), data=data.3g22)

summary(model.g.2.1)
summary(model.g.2.2)
summary(model.g.2.3)
summary(model.g.2.4)

AIC(model.g.2.1,model.g.2.2,model.g.2.3,model.g.2.4)

#only third cohort cells for growth lim age 30
data.3g23<-data.3g2a[data.3g2a$CellNum==3,]
data.3g23 <- data.3g23[complete.cases(data.3g23), ]
dim(data.3g23)
names(data.3g23)

model.g.3.1<-glm(data.3g23$Growth~1, data=data.3g23)
model.g.3.2<-glm(data.3g23$Growth~data.3g23$Time, data=data.3g23)
model.g.3.3<-glm(data.3g23$Growth~data.3g23$Time+I(data.3g23$Time^2), data=data.3g23)
model.g.3.4<-glm(data.3g23$Growth~data.3g23$Time*I(data.3g23$Time^2), data=data.3g23)

summary(model.g.3.1)
summary(model.g.3.2)
summary(model.g.3.3)
summary(model.g.3.4)

AIC(model.g.3.1,model.g.3.2,model.g.3.3,model.g.3.4)

#only initial cells for growth lim age 30
data.3g21m<-data.3g2[data.3g2$CellNum==1,]
dummy<-colMeans(data.3g21m,na.rm=TRUE)
dummy<-cbind(dummy,apply(data.3g21m,2,var,na.rm=T)) 
dummy<-cbind(dummy,apply(data.3g21m,2,sd,na.rm=T))
dummy<-cbind(dummy,(sqrt(dummy[,2]/colSums(!is.na(data.3g21m)))))
colnames(dummy)<-c("AvGrRate", "VarGrrate", "SDGrrate", "SERRGrrate")                   
ageGrorate<-dummy[5:nrow(dummy),]
ageGrorate<-cbind(ageGrorate,seq(1:nrow(ageGrorate)))
colnames(ageGrorate)<-c("AvGrRate", "VarGrrate", "SDGrrate", "SERRGrrate","Time")
#plot(AvGrRate~Time,data=ageGrorate, xlim=c(0,32))

ageGrorate<-data.frame(ageGrorate)
names(ageGrorate)

newd<-t(rbind(data.3g21$Time,predict(model.g.1.3))) 
newd<-data.frame(newd)
colnames(newd) <- c("Time","Predi")
names(newd)
dim(newd)

#Fig. S4A
p21<-
  ggplot(ageGrorate, aes(x=Time, y=AvGrRate)) +
  geom_point(size=3, shape=1)+    
  theme_bw(base_size = 20) +
  ylim(0.95, 1.15) +
  xlab("Age (hours)")+
  ylab("Cell elongation rate \n (early daughters, per 4 min)") +
  geom_errorbar(aes(ymin = AvGrRate-SERRGrrate,ymax = AvGrRate+SERRGrrate), size=0.5) +
  #geom_line(data = newd, aes(x = Time, y =Predi), colour="red", size=2 )+
  #ggtitle("A)") +
  #theme(plot.title = element_text(hjust = 0))
  annotate("text", label = "A)", x = 3, y = 1.15, size = 8, colour = "black")


#only second cells for growth age 30+ clustered
data.3g22m<-data.3g2[data.3g2$CellNum==2,]
dummy<-colMeans(data.3g22m,na.rm=TRUE)
dummy<-cbind(dummy,apply(data.3g22m,2,var,na.rm=T)) 
dummy<-cbind(dummy,apply(data.3g22m,2,sd,na.rm=T))
dummy<-cbind(dummy,(sqrt(dummy[,2]/colSums(!is.na(data.3g22m)))))
colnames(dummy)<-c("AvGrRate", "VarGrrate", "SDGrrate", "SERRGrrate")                   
ageGrorate<-dummy[5:nrow(dummy),]
ageGrorate<-cbind(ageGrorate,seq(1:nrow(ageGrorate)))
colnames(ageGrorate)<-c("AvGrRate", "VarGrrate", "SDGrrate", "SERRGrrate","Time")
#plot(AvGrRate~Time,data=ageGrorate, xlim=c(0,32))

ageGrorate<-data.frame(ageGrorate)
names(ageGrorate)


newd<-t(rbind(data.3g22$Time,predict(model.g.2.3))) 
newd<-data.frame(newd)
colnames(newd) <- c("Time","Predi")
names(newd)
dim(newd)

#Fig. S4B
p22<-
  ggplot(ageGrorate, aes(x=Time, y=AvGrRate)) +
  geom_point(size=3, shape=1)+    
  theme_bw(base_size = 20) +
  ylim(0.95, 1.15) +
  xlab("Age (hours)")+
  ylab("Cell elongation rate \n (late daughters, per 4 min)") +
  geom_errorbar(aes(ymin = AvGrRate-SERRGrrate,ymax = AvGrRate+SERRGrrate), size=0.5) +
  #geom_line(data = newd, aes(x = Time, y =Predi), colour="red", size=2 ) +
  #ggtitle("B)") +
  #theme(plot.title = element_text(hjust = 0))
  annotate("text", label = "B)", x = 3, y = 1.15, size = 8, colour = "black")


#only third cohort cells for growth age 30+ clustered
data.3g23m<-data.3g2[data.3g2$CellNum==3,]
dummy<-colMeans(data.3g23m,na.rm=TRUE)
dummy<-cbind(dummy,apply(data.3g23m,2,var,na.rm=T)) 
dummy<-cbind(dummy,apply(data.3g23m,2,sd,na.rm=T))
dummy<-cbind(dummy,(sqrt(dummy[,2]/colSums(!is.na(data.3g23m)))))
colnames(dummy)<-c("AvGrRate", "VarGrrate", "SDGrrate", "SERRGrrate")                   
ageGrorate<-dummy[5:nrow(dummy),]
ageGrorate<-cbind(ageGrorate,seq(1:nrow(ageGrorate)))
colnames(ageGrorate)<-c("AvGrRate", "VarGrrate", "SDGrrate", "SERRGrrate","Time")
#plot(AvGrRate~Time,data=ageGrorate, xlim=c(0,32))

ageGrorate<-data.frame(ageGrorate)
names(ageGrorate)

newd<-t(rbind(data.3g23$Time,predict(model.g.3.3))) 
newd<-data.frame(newd)
colnames(newd) <- c("Time","Predi")
names(newd)
dim(newd)

#Fig. S4C
p23<-
  ggplot(ageGrorate, aes(x=Time, y=AvGrRate)) +
  geom_point(shape=1, size=3)+    
  theme_bw(base_size = 20) +
  ylim(0.95, 1.15) +
  xlab("Age (hours)")+
  ylab("Cell elongation rate \n (sec. gen. late d.)\n (per 4 min)") +
  geom_errorbar(aes(ymin = AvGrRate-SERRGrrate,ymax = AvGrRate+SERRGrrate), size=0.5) +
  #geom_line(data = newd, aes(x = Time, y =Predi), colour="red", size=2 ) +
  #ggtitle("C)") +
  #theme(plot.title = element_text(hjust = 0))
  annotate("text", label = "C)", x = 3, y = 1.15, size = 8, colour = "black")

### reverse from age at death for growth rate

data.3g1rev = data.3g1

for (ii in 1:nrow(data.3g1) ) {
  if (sum((sapply(data.3g1[ii,5:ncol(data.3g1)], is.finite)==TRUE))==0) {}
  else
  {
  dummy=max(which(sapply(data.3g1[ii,5:ncol(data.3g1)], is.finite)==TRUE))+4
  data.3g1rev[ii, 5:dummy] = data.3g1[ii,dummy:5]
  }
}

#averages of hours for growth
data.3g2rev<-data.3g1rev[,c(1:4)]
names(data.3g2rev)
for (i in 0:29){data.3g2rev[paste("Growth",i+1)]<-rowMeans(data.3g1rev[,4+(15*i+1:15)],na.rm=TRUE)}
data.3g2rev[,dim(data.3g2rev)[2]+1]<-(rowMeans(data.3g1rev[,(15*i+20):(dim(data.3g1rev)[2])],na.rm=TRUE))
colnames(data.3g2rev)[35]<-"Growth 31"
names(data.3g2rev)
dim(data.3g2rev)

#data.3g2arev is size "Folder","SliceNum","CellNum","Death","Time","Growth"
# kind of reverse pivot, stacks values on top of each other creates new time variable and convertes growth and Time in numeric variable
data.3g2arev <- melt(data.3g2rev, id=c("Folder","SliceNum","CellNum","Death"), rm.nan=F) 
data.3g2arev <- data.3g2arev[complete.cases(data.3g2arev), ]
data.3g2arev <-as.data.frame(sapply(data.3g2arev,gsub,pattern="Growth",replacement=""))
colnames(data.3g2arev)<-c( "Folder","SliceNum","CellNum","Death","Time","Growth")
data.3g2arev$Growth<-as.numeric(levels(data.3g2arev$Growth))[data.3g2arev$Growth]
data.3g2arev$Time<-as.numeric(levels(data.3g2arev$Time))[data.3g2arev$Time]
names(data.3g2arev)


#only initial cells for growth lim age 30
data.3g21rev<-data.3g2arev[data.3g2arev$CellNum==1,]
data.3g21rev <- data.3g21rev[complete.cases(data.3g21rev), ]
dim(data.3g21rev)
names(data.3g21rev)

model.g.1.1rev<-glm(data.3g21rev$Growth~1, data=data.3g21rev)
model.g.1.2rev<-glm(data.3g21rev$Growth~data.3g21rev$Time, data=data.3g21rev)
model.g.1.3rev<-glm(data.3g21rev$Growth~data.3g21rev$Time+I(data.3g21rev$Time^2), data=data.3g21rev)
model.g.1.4rev<-glm(data.3g21rev$Growth~data.3g21rev$Time*I(data.3g21rev$Time^2), data=data.3g21rev)

summary(model.g.1.1rev)
summary(model.g.1.2rev)
summary(model.g.1.3rev)
summary(model.g.1.4rev)

AIC(model.g.1.1rev,model.g.1.2rev,model.g.1.3rev,model.g.1.4rev)

#only second cells for growth lim age 30
data.3g22rev<-data.3g2arev[data.3g2arev$CellNum==2,]
data.3g22rev <- data.3g22rev[complete.cases(data.3g22rev), ]
dim(data.3g22rev)
names(data.3g22rev)

model.g.2.1rev<-glm(data.3g22rev$Growth~1, data=data.3g22rev)
model.g.2.2rev<-glm(data.3g22rev$Growth~data.3g22rev$Time, data=data.3g22rev)
model.g.2.3rev<-glm(data.3g22rev$Growth~data.3g22rev$Time+I(data.3g22rev$Time^2), data=data.3g22rev)
model.g.2.4rev<-glm(data.3g22rev$Growth~data.3g22rev$Time*I(data.3g22rev$Time^2), data=data.3g22rev)

summary(model.g.2.1rev)
summary(model.g.2.2rev)
summary(model.g.2.3rev)
summary(model.g.2.4rev)

AIC(model.g.2.1rev,model.g.2.2rev,model.g.2.3rev,model.g.2.4rev)

#only third cohort cells for growth lim age 30
data.3g23rev<-data.3g2arev[data.3g2arev$CellNum==3,]
data.3g23rev <- data.3g23rev[complete.cases(data.3g23rev), ]
dim(data.3g23rev)
names(data.3g23rev)

model.g.3.1rev<-glm(data.3g23rev$Growth~1, data=data.3g23rev)
model.g.3.2rev<-glm(data.3g23rev$Growth~data.3g23rev$Time, data=data.3g23rev)
model.g.3.3rev<-glm(data.3g23rev$Growth~data.3g23rev$Time+I(data.3g23rev$Time^2), data=data.3g23rev)
model.g.3.4rev<-glm(data.3g23rev$Growth~data.3g23rev$Time*I(data.3g23rev$Time^2), data=data.3g23rev)

summary(model.g.3.1rev)
summary(model.g.3.2rev)
summary(model.g.3.3rev)
summary(model.g.3.4rev)

AIC(model.g.3.1rev,model.g.3.2rev,model.g.3.3rev,model.g.3.4rev)

#only initial cells for growth lim age 30
data.3g21mrev<-data.3g2rev[data.3g2rev$CellNum==1,]
dummy<-colMeans(data.3g21mrev,na.rm=TRUE)
dummy<-cbind(dummy,apply(data.3g21mrev,2,var,na.rm=T)) 
dummy<-cbind(dummy,apply(data.3g21mrev,2,sd,na.rm=T))
dummy<-cbind(dummy,(sqrt(dummy[,2]/colSums(!is.na(data.3g21mrev)))))
colnames(dummy)<-c("AvGrRate", "VarGrrate", "SDGrrate", "SERRGrrate")                   
ageGrorate<-dummy[5:nrow(dummy),]
ageGrorate<-cbind(ageGrorate,seq(1:nrow(ageGrorate)))
colnames(ageGrorate)<-c("AvGrRate", "VarGrrate", "SDGrrate", "SERRGrrate","Time")
#plot(AvGrRate~Time,data=ageGrorate, xlim=c(0,32))

ageGrorate<-data.frame(ageGrorate)
names(ageGrorate)

newd<-t(rbind(data.3g21rev$Time,predict(model.g.1.3rev))) 
newd<-data.frame(newd)
colnames(newd) <- c("Time","Predi")
names(newd)
dim(newd)

#Fig. S8A
p24<-
  ggplot(ageGrorate, aes(x=Time, y=AvGrRate)) +
  geom_point(size=3, shape=1)+    
  theme_bw(base_size = 20) +
  ylim(0.95, 1.16) +
  xlab("Time before death \n in hours; death = 0")+
  ylab("Cell elongation rate \n (early d., per 4 min)") +
  geom_errorbar(aes(ymin = AvGrRate-SERRGrrate,ymax = AvGrRate+SERRGrrate), size=0.5) +
  #geom_line(data = newd, aes(x = Time, y =Predi), colour="red", size=2 ) +
  #ggtitle("A)") +
  #theme(plot.title = element_text(hjust = 0))
  annotate("text", label = "A)", x = 3, y = 1.15, size = 8, colour = "black")

#only second cells for growth age 30+ clustered
data.3g22mrev<-data.3g2rev[data.3g2rev$CellNum==2,]
dummy<-colMeans(data.3g22mrev,na.rm=TRUE)
dummy<-cbind(dummy,apply(data.3g22mrev,2,var,na.rm=T)) 
dummy<-cbind(dummy,apply(data.3g22mrev,2,sd,na.rm=T))
dummy<-cbind(dummy,(sqrt(dummy[,2]/colSums(!is.na(data.3g22mrev)))))
colnames(dummy)<-c("AvGrRate", "VarGrrate", "SDGrrate", "SERRGrrate")                   
ageGrorate<-dummy[5:nrow(dummy),]
ageGrorate<-cbind(ageGrorate,seq(1:nrow(ageGrorate)))
colnames(ageGrorate)<-c("AvGrRate", "VarGrrate", "SDGrrate", "SERRGrrate","Time")
#plot(AvGrRate~Time,data=ageGrorate, xlim=c(0,32))

ageGrorate<-data.frame(ageGrorate)
names(ageGrorate)

newd<-t(rbind(data.3g22rev$Time,predict(model.g.2.3rev))) 
newd<-data.frame(newd)
colnames(newd) <- c("Time","Predi")
names(newd)
dim(newd)

#Fig. S8B
p25<-
  ggplot(ageGrorate, aes(x=Time, y=AvGrRate)) +
  geom_point(size=3, shape=1)+    
  theme_bw(base_size = 20) +
  ylim(0.95, 1.16) +
  xlab("Time before death \n in hours; death = 0")+
  ylab("Cell elongation rate \n (late d., per 4 min)") +
  geom_errorbar(aes(ymin = AvGrRate-SERRGrrate,ymax = AvGrRate+SERRGrrate), size=0.5) +
  #geom_line(data = newd, aes(x = Time, y =Predi), colour="red", size=2 ) +
  #ggtitle("B)") +
  #theme(plot.title = element_text(hjust = 0))
  annotate("text", label = "B)", x = 3, y = 1.15, size = 8, colour = "black")


#only third cohort cells for growth age 30+ clustered
data.3g23mrev<-data.3g2rev[data.3g2rev$CellNum==3,]
dummy<-colMeans(data.3g23mrev,na.rm=TRUE)
dummy<-cbind(dummy,apply(data.3g23mrev,2,var,na.rm=T)) 
dummy<-cbind(dummy,apply(data.3g23mrev,2,sd,na.rm=T))
dummy<-cbind(dummy,(sqrt(dummy[,2]/colSums(!is.na(data.3g23mrev)))))
colnames(dummy)<-c("AvGrRate", "VarGrrate", "SDGrrate", "SERRGrrate")                   
ageGrorate<-dummy[5:nrow(dummy),]
ageGrorate<-cbind(ageGrorate,seq(1:nrow(ageGrorate)))
colnames(ageGrorate)<-c("AvGrRate", "VarGrrate", "SDGrrate", "SERRGrrate","Time")
#plot(AvGrRate~Time,data=ageGrorate, xlim=c(0,32))

ageGrorate<-data.frame(ageGrorate)
names(ageGrorate)

newd<-t(rbind(data.3g23rev$Time,predict(model.g.3.3rev))) 
newd<-data.frame(newd)
colnames(newd) <- c("Time","Predi")
names(newd)
dim(newd)

#Fig. S8C
p26<-
  ggplot(ageGrorate, aes(x=Time, y=AvGrRate)) +
  geom_point(size=3, shape=1)+    
  theme_bw(base_size = 20) +
  ylim(0.95, 1.16) +
  xlab("Time before death \n in hours; death = 0")+
  ylab("Cell elongation rate \n (sec. gen. late d.)\n (per 4 min)") +
  geom_errorbar(aes(ymin = AvGrRate-SERRGrrate,ymax = AvGrRate+SERRGrrate), size=0.5) +
  #geom_line(data = newd, aes(x = Time, y =Predi), colour="red", size=2 ) +
  #ggtitle("C)") +
  #theme(plot.title = element_text(hjust = 0))
  annotate("text", label = "C)", x = 3, y = 1.15, size = 8, colour = "black")


####size at division
dummy<-data.3[,6:(dim(data.3)[2])]
dummy2<-data.4[,6:(dim(data.4)[2])]
dummy2[dummy2==0]<-NaN
dummy3<-dummy+dummy2
sizediv<-data.3[,c(1:5)]
sizediv[,c(6:(dim(data.4)[2]))]<-dummy3

#hourly size at division
sizedivh<-sizediv[,c(1:4)]
for (i in 0:29){sizedivh[paste("SizeDiv",i+1)]<-rowMeans(sizediv[,4+(15*i+1:15)],na.rm=TRUE)}
sizedivh[,dim(sizedivh)[2]+1]<-(rowMeans(sizediv[,(15*i+20):(dim(sizediv)[2])],na.rm=TRUE))
colnames(sizedivh)[35]<-"SizeDiv 31"
dim(sizedivh)
names(sizedivh)



#sizedivh is size at division "Folder","SliceNum","CellNum","Death","Time","Size"
# kind of reverse pivot, stacks values on top of each other creates new time variable and convertes growth and Time in numeric variable
sizedivha <- melt(sizedivh, id=c("Folder","SliceNum","CellNum","Death"), rm.nan=F) 
sizedivha <- sizedivha[complete.cases(sizedivha), ]
sizedivha <-as.data.frame(sapply(sizedivha,gsub,pattern="SizeDiv",replacement=""))
colnames(sizedivha)<-c( "Folder","SliceNum","CellNum","Death","Time","SizeDiv")
sizedivha$SizeDiv<-as.numeric(levels(sizedivha$SizeDiv))[sizedivha$SizeDiv]
sizedivha$Time<-as.numeric(levels(sizedivha$Time))[sizedivha$Time]
names(sizedivha)


#only initial cells for sizeDiv lim age 30
sizedivh1<-sizedivha[sizedivha$CellNum==1,]
sizedivh1 <- sizedivh1[complete.cases(sizedivh1), ]
dim(sizedivh1)
names(sizedivh1)

model.sd.1.1<-glm(sizedivh1$SizeDiv~1, data=sizedivh1)
model.sd.1.2<-glm(sizedivh1$SizeDiv~sizedivh1$Time, data=sizedivh1)
model.sd.1.3<-glm(sizedivh1$SizeDiv~sizedivh1$Time+I(sizedivh1$Time^2), data=sizedivh1)
model.sd.1.4<-glm(sizedivh1$SizeDiv~sizedivh1$Time*I(sizedivh1$Time^2), data=sizedivh1)

summary(model.sd.1.1)
summary(model.sd.1.2)
summary(model.sd.1.3)
summary(model.sd.1.4)

AIC(model.sd.1.1,model.sd.1.2,model.sd.1.3,model.sd.1.4)

#only first cohort for division age >30
data.9<-sizedivh[sizedivh$CellNum==1,]
dim(data.9)

dummy<-colMeans(data.9,na.rm=TRUE)
dummy<-cbind(dummy,apply(data.9,2,var,na.rm=T)) 
dummy<-cbind(dummy,apply(data.9,2,sd,na.rm=T))
dummy<-cbind(dummy,(sqrt(dummy[,2]/colSums(!is.na(data.9)))))
colnames(dummy)<-c("AvSizeatdev", "VarSizeatdev", "SdSizeatdev", "SErrSizeatdev")                   
ageSizeDiv<-dummy[6:nrow(dummy),]
ageSizeDiv<-cbind(ageSizeDiv,seq(1:nrow(ageSizeDiv)))
colnames(ageSizeDiv)<-c("AvSizeatdev", "VarSizeatdev", "SdSizeatdev", "SErrSizeatdev","Time")
#plot(AvSizeatdev~Time,data=ageSizeDiv)

ageSizeDiv<-data.frame(ageSizeDiv)
names(ageSizeDiv)

newd<-t(rbind(sizedivh1$Time,predict(model.sd.1.3))) 
newd<-data.frame(newd)
colnames(newd) <- c("Time","Predi")
names(newd)
dim(newd)

#Fig. S4D
p27<-
  ggplot(ageSizeDiv, aes(x=Time, y=AvSizeatdev)) +
  geom_point(shape=1, size=3)+    
  theme_bw(base_size = 20) +
  ylim(60, 140) +
  xlab("Age in hours")+
  ylab("Cell size at division \n (early daughters)") +
  geom_errorbar(aes(ymin = AvSizeatdev-SErrSizeatdev,ymax = AvSizeatdev+SErrSizeatdev), size=0.5) +
  #geom_line(data = newd, aes(x = Time, y =Predi), colour="red", size=2 ) +
  #ggtitle("D)") +
  #theme(plot.title = element_text(hjust = 0))
  annotate("text", label = "D)", x = 3, y = 135, size = 8, colour = "black")

#only second cohort cells for sizeDiv lim age 30
sizedivh2<-sizedivha[sizedivha$CellNum==2,]
sizedivh2 <- sizedivh2[complete.cases(sizedivh2), ]
dim(sizedivh2)
names(sizedivh2)

model.sd.2.1<-glm(sizedivh2$SizeDiv~1, data=sizedivh2)
model.sd.2.2<-glm(sizedivh2$SizeDiv~sizedivh2$Time, data=sizedivh2)
model.sd.2.3<-glm(sizedivh2$SizeDiv~sizedivh2$Time+I(sizedivh2$Time^2), data=sizedivh2)
model.sd.2.4<-glm(sizedivh2$SizeDiv~sizedivh2$Time*I(sizedivh2$Time^2), data=sizedivh2)

summary(model.sd.2.1)
summary(model.sd.2.2)
summary(model.sd.2.3)
summary(model.sd.2.4)

AIC(model.sd.2.1,model.sd.2.2,model.sd.2.3,model.sd.2.4)

#plot(model.sd.2.3)


#only second cohort cells for division >30
data.10<-sizedivh[sizedivh$CellNum==2,]
dim(data.10)

dummy<-colMeans(data.10,na.rm=TRUE)
dummy<-cbind(dummy,apply(data.10,2,var,na.rm=T)) 
dummy<-cbind(dummy,apply(data.10,2,sd,na.rm=T))
dummy<-cbind(dummy,(sqrt(dummy[,2]/colSums(!is.na(data.10)))))
colnames(dummy)<-c("AvSizeatdev", "VarSizeatdev", "SdSizeatdev", "SErrSizeatdev")                   
ageSizeDiv<-dummy[6:nrow(dummy),]
ageSizeDiv<-cbind(ageSizeDiv,seq(1:nrow(ageSizeDiv)))
colnames(ageSizeDiv)<-c("AvSizeatdev", "VarSizeatdev", "SdSizeatdev", "SErrSizeatdev","Time")

ageSizeDiv<-data.frame(ageSizeDiv)
names(ageSizeDiv)

newd<-t(rbind(sizedivh2$Time,predict(model.sd.2.3))) 
newd<-data.frame(newd)
colnames(newd) <- c("Time","Predi")
names(newd)
dim(newd)

#Fig. S4E
p28<-
  ggplot(ageSizeDiv, aes(x=Time, y=AvSizeatdev)) +
  geom_point(shape=1, size=3)+    
  theme_bw(base_size = 20) +
  ylim(60, 140) +
  xlab("Age in hours")+
  ylab("Cell size at division \n (late daughters)") +
  geom_errorbar(aes(ymin = AvSizeatdev-SErrSizeatdev,ymax = AvSizeatdev+SErrSizeatdev), size=0.5) +
  #geom_line(data = newd, aes(x = Time, y =Predi), colour="red", size=2 ) +
  #ggtitle("E)") +
  #theme(plot.title = element_text(hjust = 0))
  annotate("text", label = "E)", x = 3, y = 135, size = 8, colour = "black")

#only third cohort cells for sizeDiv lim age 30
sizedivh3<-sizedivha[sizedivha$CellNum==3,]
sizedivh3 <- sizedivh3[complete.cases(sizedivh3), ]
dim(sizedivh3)
names(sizedivh3)

model.sd.3.1<-glm(sizedivh3$SizeDiv~1, data=sizedivh3)
model.sd.3.2<-glm(sizedivh3$SizeDiv~sizedivh3$Time, data=sizedivh3)
model.sd.3.3<-glm(sizedivh3$SizeDiv~sizedivh3$Time+I(sizedivh3$Time^2), data=sizedivh3)
model.sd.3.4<-glm(sizedivh3$SizeDiv~sizedivh3$Time*I(sizedivh3$Time^2), data=sizedivh3)

summary(model.sd.3.1)
summary(model.sd.3.2)
summary(model.sd.3.3)
summary(model.sd.3.4)

AIC(model.sd.3.1,model.sd.3.2,model.sd.3.3,model.sd.3.4)

#only third cohort cells for division >30
data.11<-sizedivh[sizedivh$CellNum==3,]
dim(data.11)

dummy<-colMeans(data.11,na.rm=TRUE)
dummy<-cbind(dummy,apply(data.11,2,var,na.rm=T)) 
dummy<-cbind(dummy,apply(data.11,2,sd,na.rm=T))
dummy<-cbind(dummy,(sqrt(dummy[,2]/colSums(!is.na(data.11)))))
colnames(dummy)<-c("AvSizeatdev", "VarSizeatdev", "SdSizeatdev", "SErrSizeatdev")                   
ageSizeDiv<-dummy[6:nrow(dummy),]
ageSizeDiv<-cbind(ageSizeDiv,seq(1:nrow(ageSizeDiv)))
colnames(ageSizeDiv)<-c("AvSizeatdev", "VarSizeatdev", "SdSizeatdev", "SErrSizeatdev","Time")
#plot(AvSizeatdev~Time,data=ageSizeDiv)
ageSizeDiv<-data.frame(ageSizeDiv)

newd<-t(rbind(sizedivh3$Time,predict(model.sd.3.3))) 
newd<-data.frame(newd)
colnames(newd) <- c("Time","Predi")
names(newd)
dim(newd)

#Fig. S4F
p29<-
  ggplot(ageSizeDiv, aes(x=Time, y=AvSizeatdev)) +
  geom_point(shape=1, size=3)+    
  theme_bw(base_size = 20) +
  ylim(60, 140) +
  xlab("Age in hours")+
  ylab("Cell size at division \n (sec. gen. late d.)") +
  geom_errorbar(aes(ymin = AvSizeatdev-SErrSizeatdev,ymax = AvSizeatdev+SErrSizeatdev), size=0.5) +
  #geom_line(data = newd, aes(x = Time, y =Predi), colour="red", size=2 ) +
  #ggtitle("F)") +
  #theme(plot.title = element_text(hjust = 0))
  annotate("text", label = "F)", x = 3, y = 135, size = 8, colour = "black")

names(ageSizeDiv)


### size at division reverse time
sizedivrev = sizediv

for (ii in 1:nrow(sizediv) ) {
  if (sum((sapply(sizediv[ii,5:ncol(sizediv)], is.finite)==TRUE))==0) {}
  else
  {
    dummy=max(which(sapply(sizediv[ii,5:ncol(sizediv)], is.finite)==TRUE))+4
    sizedivrev[ii, 5:dummy] = sizediv[ii,dummy:5]
  }
}

#hourly size at division reverse
sizedivhrev<-sizedivrev[,c(1:4)]
for (i in 0:29){sizedivhrev[paste("SizeDiv",i+1)]<-rowMeans(sizedivrev[,4+(15*i+1:15)],na.rm=TRUE)}
sizedivhrev[,dim(sizedivhrev)[2]+1]<-(rowMeans(sizedivrev[,(15*i+20):(dim(sizedivrev)[2])],na.rm=TRUE))
colnames(sizedivhrev)[35]<-"SizeDiv 31"
dim(sizedivhrev)
names(sizedivhrev)


#sizedivh is size at division "Folder","SliceNum","CellNum","Death","Time","Size"
# kind of reverse pivot, stacks values on top of each other creates new time variable and convertes growth and Time in numeric variable
sizedivharev <- melt(sizedivhrev, id=c("Folder","SliceNum","CellNum","Death"), rm.nan=F) 
sizedivharev <- sizedivharev[complete.cases(sizedivharev), ]
sizedivharev <-as.data.frame(sapply(sizedivharev,gsub,pattern="SizeDiv",replacement=""))
colnames(sizedivharev)<-c( "Folder","SliceNum","CellNum","Death","Time","SizeDiv")
sizedivharev$SizeDiv<-as.numeric(levels(sizedivharev$SizeDiv))[sizedivharev$SizeDiv]
sizedivharev$Time<-as.numeric(levels(sizedivharev$Time))[sizedivharev$Time]
names(sizedivharev)

#only initial cells for sizeDiv lim age 30
sizedivh1rev<-sizedivharev[sizedivharev$CellNum==1,]
sizedivh1rev <- sizedivh1rev[complete.cases(sizedivh1rev), ]
dim(sizedivh1rev)
names(sizedivh1rev)

model.sd.1.1rev<-glm(sizedivh1rev$SizeDiv~1, data=sizedivh1rev)
model.sd.1.2rev<-glm(sizedivh1rev$SizeDiv~sizedivh1rev$Time, data=sizedivh1rev)
model.sd.1.3rev<-glm(sizedivh1rev$SizeDiv~sizedivh1rev$Time+I(sizedivh1rev$Time^2), data=sizedivh1rev)
model.sd.1.4rev<-glm(sizedivh1rev$SizeDiv~sizedivh1rev$Time*I(sizedivh1rev$Time^2), data=sizedivh1rev)

summary(model.sd.1.1rev)
summary(model.sd.1.2rev)
summary(model.sd.1.3rev)
summary(model.sd.1.4rev)

AIC(model.sd.1.1rev,model.sd.1.2rev,model.sd.1.3rev,model.sd.1.4rev)

#only first cohort for division age >30
data.9rev<-sizedivhrev[sizedivhrev$CellNum==1,]
dim(data.9rev)

dummy<-colMeans(data.9rev,na.rm=TRUE)
dummy<-cbind(dummy,apply(data.9rev,2,var,na.rm=T)) 
dummy<-cbind(dummy,apply(data.9rev,2,sd,na.rm=T))
dummy<-cbind(dummy,(sqrt(dummy[,2]/colSums(!is.na(data.9rev)))))
colnames(dummy)<-c("AvSizeatdev", "VarSizeatdev", "SdSizeatdev", "SErrSizeatdev")                   
ageSizeDiv<-dummy[6:nrow(dummy),]
ageSizeDiv<-cbind(ageSizeDiv,seq(1:nrow(ageSizeDiv)))
colnames(ageSizeDiv)<-c("AvSizeatdev", "VarSizeatdev", "SdSizeatdev", "SErrSizeatdev","Time")
#plot(AvSizeatdev~Time,data=ageSizeDiv)

ageSizeDiv<-data.frame(ageSizeDiv)
names(ageSizeDiv)

newd<-t(rbind(sizedivh1rev$Time,predict(model.sd.1.3rev))) 
newd<-data.frame(newd)
colnames(newd) <- c("Time","Predi")
names(newd)
dim(newd)

#Fig. S8A
p30<-
  ggplot(ageSizeDiv, aes(x=Time, y=AvSizeatdev)) +
  geom_point(size=3, shape=1)+    
  theme_bw(base_size = 20) +
  ylim(20, 120) +
  xlab("Time before death\n(in hours; death = 0)")+
  ylab("Cell size at division \n (early daughters)") +
  geom_errorbar(aes(ymin = AvSizeatdev-SErrSizeatdev,ymax = AvSizeatdev+SErrSizeatdev), size=0.5) +
  #geom_line(data = newd, aes(x = Time, y =Predi), colour="red", size=2 ) +
  #ggtitle("D)") +
  #theme(plot.title = element_text(hjust = 0))
  annotate("text", label = "D)", x = 3, y = 120, size = 8, colour = "black")

#only second cohort cells for sizeDiv lim age 30 rev
sizedivh2rev<-sizedivharev[sizedivharev$CellNum==2,]
sizedivh2rev <- sizedivh2rev[complete.cases(sizedivh2rev), ]
dim(sizedivh2rev)
names(sizedivh2rev)

model.sd.2.1rev<-glm(sizedivh2rev$SizeDiv~1, data=sizedivh2rev)
model.sd.2.2rev<-glm(sizedivh2rev$SizeDiv~sizedivh2rev$Time, data=sizedivh2rev)
model.sd.2.3rev<-glm(sizedivh2rev$SizeDiv~sizedivh2rev$Time+I(sizedivh2rev$Time^2), data=sizedivh2rev)
model.sd.2.4rev<-glm(sizedivh2rev$SizeDiv~sizedivh2rev$Time*I(sizedivh2rev$Time^2), data=sizedivh2rev)

summary(model.sd.2.1rev)
summary(model.sd.2.2rev)
summary(model.sd.2.3rev)
summary(model.sd.2.4rev)

AIC(model.sd.2.1rev,model.sd.2.2rev,model.sd.2.3rev,model.sd.2.4rev)

#only second cohort for division age >30
data.10rev<-sizedivhrev[sizedivhrev$CellNum==2,]
dim(data.10rev)

dummy<-colMeans(data.10rev,na.rm=TRUE)
dummy<-cbind(dummy,apply(data.10rev,2,var,na.rm=T)) 
dummy<-cbind(dummy,apply(data.10rev,2,sd,na.rm=T))
dummy<-cbind(dummy,(sqrt(dummy[,2]/colSums(!is.na(data.10rev)))))
colnames(dummy)<-c("AvSizeatdev", "VarSizeatdev", "SdSizeatdev", "SErrSizeatdev")                   
ageSizeDiv<-dummy[6:nrow(dummy),]
ageSizeDiv<-cbind(ageSizeDiv,seq(1:nrow(ageSizeDiv)))
colnames(ageSizeDiv)<-c("AvSizeatdev", "VarSizeatdev", "SdSizeatdev", "SErrSizeatdev","Time")
#plot(AvSizeatdev~Time,data=ageSizeDiv)

ageSizeDiv<-data.frame(ageSizeDiv)
names(ageSizeDiv)

newd<-t(rbind(sizedivh2rev$Time,predict(model.sd.2.3rev))) 
newd<-data.frame(newd)
colnames(newd) <- c("Time","Predi")
names(newd)
dim(newd)

#Fig. S8E
p31<-
  ggplot(ageSizeDiv, aes(x=Time, y=AvSizeatdev)) +
  geom_point(size=3, shape=1)+    
  theme_bw(base_size = 20) +
  ylim(20, 120) +
  xlab("Time before death\n(in hours; death = 0)")+
  ylab("Cell size at division \n (late daughters)") +
  geom_errorbar(aes(ymin = AvSizeatdev-SErrSizeatdev,ymax = AvSizeatdev+SErrSizeatdev), size=0.5) +
  #geom_line(data = newd, aes(x = Time, y =Predi), colour="red", size=2 )+
  #ggtitle("E)") +
  #theme(plot.title = element_text(hjust = 0))
  annotate("text", label = "E)", x = 3, y = 120, size = 8, colour = "black")
  
#only third cohort cells for sizeDiv lim age 30 rev
sizedivh3rev<-sizedivharev[sizedivharev$CellNum==3,]
sizedivh3rev <- sizedivh3rev[complete.cases(sizedivh3rev), ]
dim(sizedivh3rev)
names(sizedivh3rev)

model.sd.3.1rev<-glm(sizedivh3rev$SizeDiv~1, data=sizedivh3rev)
model.sd.3.2rev<-glm(sizedivh3rev$SizeDiv~sizedivh3rev$Time, data=sizedivh3rev)
model.sd.3.3rev<-glm(sizedivh3rev$SizeDiv~sizedivh3rev$Time+I(sizedivh3rev$Time^2), data=sizedivh3rev)
model.sd.3.4rev<-glm(sizedivh3rev$SizeDiv~sizedivh3rev$Time*I(sizedivh3rev$Time^2), data=sizedivh3rev)

summary(model.sd.3.1rev)
summary(model.sd.3.2rev)
summary(model.sd.3.3rev)
summary(model.sd.3.4rev)

AIC(model.sd.3.1rev,model.sd.3.2rev,model.sd.3.3rev,model.sd.3.4rev)

#only second cohort for division age >30
data.11rev<-sizedivhrev[sizedivhrev$CellNum==3,]
dim(data.11rev)

dummy<-colMeans(data.11rev,na.rm=TRUE)
dummy<-cbind(dummy,apply(data.11rev,2,var,na.rm=T)) 
dummy<-cbind(dummy,apply(data.11rev,2,sd,na.rm=T))
dummy<-cbind(dummy,(sqrt(dummy[,2]/colSums(!is.na(data.11rev)))))
colnames(dummy)<-c("AvSizeatdev", "VarSizeatdev", "SdSizeatdev", "SErrSizeatdev")                   
ageSizeDiv<-dummy[6:nrow(dummy),]
ageSizeDiv<-cbind(ageSizeDiv,seq(1:nrow(ageSizeDiv)))
colnames(ageSizeDiv)<-c("AvSizeatdev", "VarSizeatdev", "SdSizeatdev", "SErrSizeatdev","Time")
#plot(AvSizeatdev~Time,data=ageSizeDiv)

ageSizeDiv<-data.frame(ageSizeDiv)
names(ageSizeDiv)

newd<-t(rbind(sizedivh3rev$Time,predict(model.sd.3.3rev))) 
newd<-data.frame(newd)
colnames(newd) <- c("Time","Predi")
names(newd)
dim(newd)

#Fig. S8F
p32<-
  ggplot(ageSizeDiv, aes(x=Time, y=AvSizeatdev)) +
  geom_point(size=3, shape=1)+    
  theme_bw(base_size = 20) +
  ylim(20, 120) +
  xlab("Time before death\n(in hours; death = 0)")+
  ylab("Cell size at division \n (sec. gen. late d.)") +
  geom_errorbar(aes(ymin = AvSizeatdev-SErrSizeatdev,ymax = AvSizeatdev+SErrSizeatdev), size=0.5) +
  #geom_line(data = newd, aes(x = Time, y =Predi), colour="red", size=2 )+
  #ggtitle("F)") +
  #theme(plot.title = element_text(hjust = 0))
  annotate("text", label = "F)", x = 3, y = 120, size = 8, colour = "black")

#Fig. S4
grid.arrange(p21,p22,p23,p27,p28,p29,ncol=3)

#Fig. S8
grid.arrange(p24,p25,p26,p30,p31,p32,ncol=3)

#Leslie matrix for first cohort cell averaged above age 30
Lesliemm <- matrix(0, 31, 31)
Lesliemm[1,]<-agedivrateLeslie

diag(Lesliemm[-1,])<-survrateLeslie[1:30] 
Lesliemm[31,31]<-survrateLeslie[31]
eig<-eigen(Lesliemm)
distrib<-eig$vectors[,1]
distrib1<-distrib/sum(distrib)
sum(distrib1)
par(mfrow=c(1,1)) 
plot(1:31,distrib1, ann=FALSE)
mtext(side = 2, text = "(early daughters)", line = 2)
mtext(side = 2, text = expression("exponential growth phase cells"), line = 3)
mtext(side = 2, text = expression("Age distribution of"), line = 4)
mtext(side = 1, text = "Age", line = 2)
mtext(side = 1, text = "(in hours)", line = 3)

distrib<-t(rbind(1:31,distrib1)) 
distrib<-data.frame(distrib)
colnames(distrib) <- c("Time","Predi")
names(distrib)
distrib$Time<-as.numeric(distrib$Time)
distrib$Predi<-as.numeric(distrib$Predi)
dim(distrib)
is.data.frame(distrib)
is.factor(distrib$Predi)

#Fig. S2
ggplot(distrib, aes(x=Time, y=Predi)) +
  geom_bar(stat="identity") +
  xlim(0,8) +
  theme_bw(base_size = 20) +
  #theme_grey(base_size = 20) +
  #ylim(20, 120) +
  xlab("Age (hours)")+
  ylab("Age distribution of \n exponential growth phase cells\n early daughters")  


# ------------------------ define functions ---------- #

# Gamma-Gompertz-Makeham force of mortality with separate K and L or
# K=L parametrization for gam=1/K=1/L
muGGM <- function(x,par,KequalsL=TRUE) {
  if(KequalsL==FALSE) {
    a <- par[1]
    b <- par[2]
    k <- par[3]
    l <- par[4]
    m <- par[5]
    a*exp(b*x)*k/(l+a/b*(exp(b*x)-1))+m
  } else {
    a <- par[1]
    b <- par[2]
    gam <- par[3]
    m <- par[4]
    a*exp(b*x)/(1+gam*a/b*(exp(b*x)-1))+m
  }
}
