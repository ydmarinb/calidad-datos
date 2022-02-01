library(readxl)
library(VIM)
library(mice)
setwd("G:/Mi unidad/Trabajo de grado maestria/Scripts")
base <- read_excel("df_procedencia_modificada.xlsx")





#table(base$TIPO_NIVEL)

#table(temp$TIPO_NIVEL) 


833/5761   

5989 / 39687 
colnames(base)
a <- base[!is.na(base$TIPO_NIVEL) & !is.na(base$ESTADO_CIVIL) & !is.na(base$DEPTO_PROCEDENCIA) & !is.na(base$EXTRANJERO),]
aggr(a[c("TIPO_NIVEL", "ESTADO_CIVIL", "DEPTO_PROCEDENCIA", 'EXTRANJERO', 'EDAD')])
columns <- c("EXTRANJERO", "EDAD", "ESTADO_CIVIL")
imputed_data1 <- mice(base[,names(base) %in% columns],m = 1,
                      maxit = 1, method = "norm.nob",seed = 2018,print=F)
complete.data1 <- mice::complete(imputed_data1)

#write.csv(x = complete.data1, file = 'df_procedencia_imputada.csv', row.names = F)




png(filename = 'imputacion_estado_civil_proce.png')
plot(density(base$EDAD,na.rm = T),col=2,main="EDAD") # normal
lines(density(complete.data1$EDAD),col=3)# imputada
legend("topright",
       c("Sin imputar","Imputada"),
       fill=c("red","green")
)
dev.off() 

hist(c(6429, 26157, 11751, 6871, 2717, 1041, 849, 432, 208, 139, 108, 35, 26, 23, 4, 6, 2), )


mean(base$EDAD, na.rm = T)
mean(complete.data1$EDAD)
var(base$EDAD, na.rm = T)
var(complete.data1$EDAD)
median(base$EDAD, na.rm = T)
median(complete.data1$EDAD)
