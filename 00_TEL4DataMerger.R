####setup####
rm(list = ls())
library(readxl)

####merger####
start.date="2024-04-23"
end.date="2024-06-16"

v1_and_v2 <- data.frame()

for (i in c('V1', 'V2')) {
  
  target.folder= paste("C:\\Users\\bened\\Dropbox\\TEL4\\3_Survey related\\Data\\", i, sep='')
  
  
  full.list=list.files(target.folder)
  
  full.subject=NA
  full.HHmember=NA
  full.PTcards=NA
  
  a=1
  date.pot=substr(full.list[a],17,22)
  if(nchar(full.list[a])==32){
    s.pot.1=substr(full.list[a],24,25)
    s.pot.2=substr(full.list[a],26,27)
  } else if(nchar(full.list[a])==34 & substr(full.list[a],28,28)!="_"){
    s.pot.1=substr(full.list[a],24,26)
    s.pot.2=substr(full.list[a],27,29)
  } else {
    s.pot.1=substr(full.list[a],24,25)
    s.pot.2=substr(full.list[a],26,27)
  }
  hold.subject=read_xlsx(paste0(target.folder,"\\",full.list[a]),sheet="Subject")
  hold.subject=cbind(hold.subject,Date=date.pot,SX=s.pot.1,SY=s.pot.2)
  full.subject=hold.subject
  hold.HHmember=read_xlsx(paste0(target.folder,"\\",full.list[a]),sheet="HHMembers")
  hold.HHmember=cbind(hold.HHmember,Date=date.pot,SX=s.pot.1,SY=s.pot.2)
  full.HHmember=hold.HHmember
  hold.PTcards=read_xlsx(paste0(target.folder,"\\",full.list[a]),sheet="PTCards")
  hold.PTcards=cbind(hold.PTcards,Date=date.pot,SX=s.pot.1,SY=s.pot.2)
  full.PTcards=hold.PTcards
  a=a+1
  while(a<length(full.list)+1){
    date.pot=substr(full.list[a],17,22)
    if(nchar(full.list[a])==32){
      s.pot.1=substr(full.list[a],24,25)
      s.pot.2=substr(full.list[a],26,27)
    } else if(nchar(full.list[a])==34 & substr(full.list[a],28,28)!="_"){
      s.pot.1=substr(full.list[a],24,26)
      s.pot.2=substr(full.list[a],27,29)
    } else {
      s.pot.1=substr(full.list[a],24,25)
      s.pot.2=substr(full.list[a],26,27)
    }
    
    hold.subject=read_xlsx(paste0(target.folder,"\\",full.list[a]),sheet="Subject")
    if(nrow(hold.subject)>0){
      hold.subject=cbind(hold.subject,Date=date.pot,SX=s.pot.1,SY=s.pot.2)
      full.subject=rbind(full.subject,hold.subject)
    }
    hold.HHmember=read_xlsx(paste0(target.folder,"\\",full.list[a]),sheet="HHMembers")
    if(nrow(hold.HHmember)>0){
      hold.HHmember=cbind(hold.HHmember,Date=date.pot,SX=s.pot.1,SY=s.pot.2)
      full.HHmember=rbind(full.HHmember,hold.HHmember)
    }
    hold.PTcards=read_xlsx(paste0(target.folder,"\\",full.list[a]),sheet="PTCards")
    if(nrow(hold.PTcards)>0){
      hold.PTcards=cbind(hold.PTcards,Date=date.pot,SX=s.pot.1,SY=s.pot.2)
      full.PTcards=rbind(full.PTcards,hold.PTcards)
    }
    a=a+1
  }
  
  v1_and_v2 <- plyr::rbind.fill(v1_and_v2, full.subject)
}


write.csv(
  v1_and_v2,
  "C:/Users/bened/OneDrive/Desktop/NUS-econ-predoc/03-TEL-LG-TW-PL/Code/v1_and_v2_17Jun2024_0.csv"
)

####subject count####
full.type=unique(full.subject$Type)
full.subject$Date=as.Date(full.subject$Date,"%d%m%y")

#recurited type count
type.count=c()
a=1
while(a<length(full.type)+1){
  type.count=c(type.count,sum(full.subject$Type==full.type[a]))
  a=a+1
}

full.type=data.frame(full.type,type.count)
full.type
sum(full.type$type.count)

#landed by household count
hh.landed.uni=unique(full.subject$Postal[is.na(full.subject$Unit)])

hh.landed.subject.count=c()
a=1
while(a<length(hh.landed.uni)+1){
  hh.landed.subject.count=c(hh.landed.subject.count,sum(full.subject$Postal==hh.landed.uni[a]))
  a=a+1
}
hh.landed.count=c()
a=1
while(a<max(hh.landed.subject.count)+1){
  hh.landed.count=c(hh.landed.count,sum(hh.landed.subject.count==a))
  a=a+1
}
hh.landed.count=data.frame(Subjects=1:max(hh.landed.subject.count),Count=hh.landed.count)
hh.landed.count

#HDB by household count
hh.HDB.uni=unique(paste0(full.subject$Postal[!is.na(full.subject$Unit)],"_",full.subject$Unit[!is.na(full.subject$Unit)]))

hh.HDB.subject.count=c()
HDB.address.hold=paste0(full.subject$Postal[!is.na(full.subject$Unit)],"_",full.subject$Unit[!is.na(full.subject$Unit)])
a=1
while(a<length(hh.HDB.uni)+1){
  hh.HDB.subject.count=c(hh.HDB.subject.count,sum(HDB.address.hold==hh.HDB.uni[a]))
  a=a+1
}
hh.HDB.count=c()
a=1
while(a<max(hh.HDB.subject.count)+1){
  hh.HDB.count=c(hh.HDB.count,sum(hh.HDB.subject.count==a))
  a=a+1
}
hh.HDB.count=data.frame(Subjects=1:max(hh.HDB.subject.count),Count=hh.HDB.count)
hh.HDB.count



####survyor payment####
cut.subject=full.subject[full.subject$Date<=end.date & full.subject$Date>=start.date,]
s.type=sort(unique(c(cut.subject$SX,cut.subject$SY)))
s.count=c()
HDB.count=c()
HDBdriver.count=c()
Landed.count=c()
a=1
while(a<length(s.type)+1){
  s.count=c(s.count,sum(c(cut.subject$SX==s.type[a],cut.subject$SY==s.type[a])))
  HDB.count=c(HDB.count,sum(c(cut.subject$SX[cut.subject$Type=="HDB"]==s.type[a],cut.subject$SY[cut.subject$Type=="HDB"]==s.type[a])))
  HDBdriver.count=c(HDBdriver.count,sum(c(cut.subject$SX[cut.subject$Type=="HDBDriver"]==s.type[a],cut.subject$SY[cut.subject$Type=="HDBDriver"]==s.type[a])))
  Landed.count=c(Landed.count,sum(c(cut.subject$SX[cut.subject$Type=="Landed"]==s.type[a],cut.subject$SY[cut.subject$Type=="Landed"]==s.type[a])))
  a=a+1
}
full.s=data.frame(s.type,s.count,HDB.count,HDBdriver.count,Landed.count)
sum(full.s$s.count)/2

s.payment=(full.s$HDB.count*5)+(full.s$HDBdriver.count*7)+(full.s$Landed.count*7)
full.s=cbind(full.s,s.payment)
full.s


pay.dates=seq.Date(as.Date(start.date),as.Date(end.date),1)
week.mon.index=which(weekdays(pay.dates)=="Monday")
week.sun.index=which(weekdays(pay.dates)=="Sunday")
week.sun.index=week.sun.index[-1] #only for may payroll, remove after
bonus.roll=c()
a=1
while(a<length(week.sun.index)+1){
  cut.subject.temp=full.subject[full.subject$Date<=pay.dates[week.sun.index[a]] & full.subject$Date>=pay.dates[week.mon.index[a]],]
  s.count.temp=c()
  b=1
  while(b<length(s.type)+1){
    s.count.temp=c(s.count.temp,sum(c(cut.subject.temp$SX==s.type[b],cut.subject.temp$SY==s.type[b])))
    b=b+1
  }
  bonus.roll=c(bonus.roll,s.type[which(s.count.temp>=60)])
  a=a+1
}

bonus.roll



####surveyor day count####
date.counter.s=c()
a=1
while(a<length(s.type)+1){
  date.counter.s=c(date.counter.s,length(unique(cut.subject$Date[cut.subject$SX==s.type[a] | cut.subject$SY==s.type[a]])))
  a=a+1
}
date.counter.s=cbind(s.type,date.counter.s)
date.counter.s

####csv outputs####
write.csv(full.s,"C:\\Users\\Patrick Lim\\Desktop\\paymentMayV2.csv",na="",row.names = F)

full.subject$Unit=paste0("`",full.subject$Unit)
write.csv(full.subject,"C:\\Users\\Patrick Lim\\Desktop\\subjectV2.csv",na="",row.names = F)
write.csv(full.HHmember,"C:\\Users\\Patrick Lim\\Desktop\\HHmemberV2.csv",na="",row.names = F)
write.csv(full.PTcards,"C:\\Users\\Patrick Lim\\Desktop\\PTcardsV2.csv",na="",row.names = F)

####misc####
ID.PT=paste0(full.PTcards$Postal[!is.na(full.PTcards$Credit)],"_",full.PTcards$Unit[!is.na(full.PTcards$Credit)],"_",full.PTcards$Participating[!is.na(full.PTcards$Credit)])


table(table(ID.PT))
