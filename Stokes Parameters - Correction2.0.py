#Update (compared to Stokes Parameters - Correction): In the previous version, we're only able to use one single value of Retardance. In this version, we can apply a Retardance curve file
#Note: wavelength range of the retardance curve is 416.11859 --> 750.89575nm

#Intensity files:
yourpath = r'C:\Users\PA\Desktop\TestCode_LP1 and LP2 at (max) _ LP(stokes) = 4\Converted P3HT'
#Retardance curve file (radian):
thetapath = r'C:\Users\hangu\Desktop\Test objectives 2020\retardance curve extended(416_750nm) (QWP_Stokes) (radian).txt'

import math
import os
import numpy as np
import pandas as pd

def number_name(file_name):
     return int(file_name[0:-4])

def deg_to_rad(degree):
    return degree*math.pi/180

def cotan(radian):
    return 1/math.tan(radian)



#1 Create DataFrame:
df = pd.DataFrame()

for root, dirs, files in os.walk(yourpath, topdown=False):
    files = sorted(files, key=number_name)                  # "files" is a list: 0 10 20 30 ... 360, length = 37
    for name in files[:-1]:                                 # we only want 0 -> 350
        md = open(os.path.join(root, name), 'r')

        intensity_lst = []
        wavelength_lst = []
        for line in md:
            line = line.split()
            intensity_lst.append(int(line[1]))
            wavelength_lst.append(float(line[0]))           # wavelength_lst: 398.35928 .... 680.01367, length = 1024, ColA

        df[int(name[0:-4])] = intensity_lst
md.close()

#1_2 Create Retardance curve:
md2 = open(thetapath, 'r')

retardance_lst = []
wavelength_r_lst = []
for line in md2:
    line = line.split()
    retardance_lst.append(float(line[1]))
    wavelength_r_lst.append(float(line[0]))                 # wavelength_r_lst: 416.11859 .... 750.89575, length = 1220

md2.close()

#1_3 Define the range of Retardance curve being used for correction:
if float(wavelength_lst[0]) > float(wavelength_r_lst[0]):
    min_range = abs(float(wavelength_lst[0]) - float(wavelength_r_lst[0]))
    index = 0
    for i in range(len(wavelength_r_lst)):
        #print(min_range)
        if abs(float(wavelength_lst[0]) - float(wavelength_r_lst[i])) < min_range:
            min_range = abs(float(wavelength_lst[0]) - float(wavelength_r_lst[i]))
            index = i
        

    if wavelength_lst[-1] <= wavelength_r_lst[-1]:                             # if the wavelength range does not exceed 750nm
        wavelength_r_lst = wavelength_r_lst[index:index+len(wavelength_lst)]   # new wavelength_r_lst, length = len(wavelength_lst)
        retardance_lst = retardance_lst[index:index+len(wavelength_lst)]       # new retardance_lst, length = len(wavelength_lst)
    else:                                                                      # if the wavelength range does exceed 750nm
        df = df[:len(wavelength_r_lst)-index]
        wavelength_r_lst = wavelength_r_lst[index:]   
        retardance_lst = retardance_lst[index:]
               

else:                                                                    
    min_range = abs(float(wavelength_r_lst[0]) - float(wavelength_lst[0]))
    index = 0
    for i in range(len(wavelength_lst)):
        if abs(float(wavelength_r_lst[0]) - float(wavelength_lst[i])) < min_range:
            min_range = abs(float(wavelength_r_lst[0]) - float(wavelength_lst[i]))
            index = i
        #print(str(i))

    wavelength_r_lst = wavelength_r_lst[:(len(wavelength_lst)-index)]   # new wavelength_r_lst
    retardance_lst = retardance_lst[:(len(wavelength_lst)-index)]       # new retardance_lst
    df = df[index:]                                                     # new dataframe, which is shorter than the original one
    wavelength_lst = wavelength_lst[index:]                             # new wavelength_lst, this is only used for printing wavelength labels in the output file

#print(min_range)
#print(index)
#print(len(wavelength_r_lst))
#print(len(retardance_lst))
#print(len(list(df.index.values)))


#2 Make lists of A B C D:
A_lst = []
B_lst = []
C_lst = []
D_lst = []


for wavelength in list(df.index):
    cal_A = 2/36*(df.loc[wavelength].sum())

    cal_B = 0
    deg = 0
    for intensity in df.loc[wavelength]:
        cal_B += intensity*math.sin(2*deg_to_rad(deg))
        deg += 10
    cal_B = 4/36*cal_B

    cal_C = 0
    deg = 0
    for intensity in df.loc[wavelength]:
        cal_C += intensity*math.cos(4*deg_to_rad(deg))
        deg += 10
    cal_C = 4/36*cal_C

    cal_D = 0
    deg = 0
    for intensity in df.loc[wavelength]:
        cal_D += intensity*math.sin(4*deg_to_rad(deg))
        deg += 10
    cal_D = 4/36*cal_D

    A_lst.append(cal_A)
    B_lst.append(cal_B)
    C_lst.append(cal_C)
    D_lst.append(cal_D)

#3 Make lists of S0 S1 S2 S3:
S0_lst = [a_i - c_i for a_i, c_i in zip(A_lst, C_lst)]          #S0
S1_lst = [i*2 for i in C_lst]                                   #S1
S2_lst = [i*2 for i in D_lst]                                   #S2
S3_lst = [-i for i in B_lst]                                    #S3

#3_2 Make lists of corrections parameters S0_R S1_R S2_R S3_R:
S0R_lst = [s0i + s1i*(1-cotan(theta_i/2)*cotan(theta_i/2))/2 for s0i, s1i, theta_i in zip(S0_lst, S1_lst, retardance_lst)]      #S0_R, ColB
S1R_lst = [s1i/(2*math.sin(theta_i/2)*math.sin(theta_i/2)) for s1i, theta_i in zip(S1_lst, retardance_lst)]                     #S1_R, ColC
S2R_lst = [s2i/(2*math.sin(theta_i/2)*math.sin(theta_i/2)) for s2i, theta_i in zip(S2_lst, retardance_lst)]                     #S2_R, ColD
S3R_lst = [s3i/math.sin(theta_i) for s3i, theta_i in zip(S3_lst, retardance_lst)]                                               #S3_R, ColE

#4 Make other lists:
#PolDeg, ColF
PD_lst = [math.sqrt(s1i**2 + s2i**2 + s3i**2)/s0i for s1i, s2i, s3i, s0i in zip(S1R_lst, S2R_lst, S3R_lst, S0R_lst)]
                                                                

#S1/S0
S1_S0_lst = [s1i/s0i for s1i, s0i in zip(S1R_lst, S0R_lst)]       #S1_R/S0_R, ColG

#S2/S0
S2_S0_lst = [s2i/s0i for s2i, s0i in zip(S2R_lst, S0R_lst)]       #S2_R/S0_R, ColH

#S3/S0
S3_S0_lst = [s3i/s0i for s3i, s0i in zip(S3R_lst, S0R_lst)]       #S3_R/S0_R, ColI

#S0-Min
S0R_min_lst = [s0i-min(S0_lst) for s0i in S0R_lst]                #S0_R_min, ColJ: (Subtract min of col B)

#S0-Min/Max
S0R_minmax_lst = [s0i/max(S0R_min_lst) for s0i in S0R_min_lst]     #S0_R_min/max, ColK: (Divide J by max of col J)

#ABSOLS1/S0
S1_S0_abs_lst = [abs(i) for i in S1_S0_lst]                     #ABSOL(S1_R/S0_R), ColL: Absolute value of col G

#ABSOLS2/S0
S2_S0_abs_lst = [abs(i) for i in S2_S0_lst]                     #ABSOL(S2_R/S0_R), ColL: Absolute value of col H

#ABSOLS3/S0
S3_S0_abs_lst = [abs(i) for i in S3_S0_lst]                     #ABSOL(S3_R/S0_R), ColL: Absolute value of col I

#5 Create a new file containing the stokes parameters:
new_file = open("stokes_parameters.txt", "w")
new_file.write('Wavelength' + ' ' + 'S0_R' + ' ' + 'S1_R' + ' ' + 'S2_R' + ' ' + 'S3_R' 
                + ' ' + 'PolDeg' + ' ' + 'S1_R/S0_R' + ' ' + 'S2_R/S0_R' + ' ' + 'S3_R/S0_R' 
                + ' ' + 'S0_R-Min' + ' ' + 'S0_R-Min/Max' + ' ' + 'ABSOL(S1_R/S0_R)'
                + ' ' + 'ABSOL(S2_R/S0_R)' + ' ' + 'ABSOL(S3_R/S0_R)' + '\n')

for i in range(len(S0_lst)):
    new_file.write(str(wavelength_lst[i]) + ' ' + str(S0R_lst[i]) + ' ' + str(S1R_lst[i]) + ' ' + str(S2R_lst[i]) + ' ' + str(S3R_lst[i])
                   + ' ' + str(PD_lst[i]) + ' ' + str(S1_S0_lst[i]) + ' ' + str(S2_S0_lst[i]) + ' ' + str(S3_S0_lst[i]) 
                   + ' ' + str(S0R_min_lst[i]) + ' ' + str(S0R_minmax_lst[i]) + ' ' + str(S1_S0_abs_lst[i])
                    + ' ' + str(S2_S0_abs_lst[i]) + ' ' + str(S3_S0_abs_lst[i]) + '\n')

new_file.close()


