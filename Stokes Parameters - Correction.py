yourpath = r'C:\Users\PA\Desktop\TestCode_LP1 and LP2 at (max) _ LP(stokes) = 4\Converted'

import math
import os
import numpy as np
import pandas as pd

def number_name(file_name):
     return int(file_name[0:-4])

def deg_to_rad(degree):
    return degree*math.pi/180

def cotan(degree):
    rad = deg_to_rad(degree)
    return 1/math.tan(rad)

#Retardance (degree):
theta = 90

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
            wavelength_lst.append(float(line[0]))           # wavelength_lst: 397.33273 .... 679.00134, length = 1024, ColA

        df[int(name[0:-4])] = intensity_lst
md.close()

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
S0R_lst = [s0i + s1i*(1-cotan(theta/2)*cotan(theta/2))/2 for s0i, s1i in zip(S0_lst, S1_lst)]          #S0_R, ColB
S1R_lst = [s1i/(2*math.sin(deg_to_rad(theta/2))*math.sin(deg_to_rad(theta/2))) for s1i in S1_lst]          #S1_R, ColC
S2R_lst = [s2i/(2*math.sin(deg_to_rad(theta/2))*math.sin(deg_to_rad(theta/2))) for s2i in S2_lst]          #S2_R, ColD
S3R_lst = [s3i/math.sin(deg_to_rad(theta)) for s3i in S3_lst]                                          #S3_R, ColE

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



#with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#   print(sum_df)
#for i in df.loc[0]:
#    print(i)
#print(min(S0_lst))
#print(C_lst[0])
#print(len(wavelength_lst))
#print(len(list(df.index)))