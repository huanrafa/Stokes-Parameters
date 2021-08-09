#This code is used to calculate Stokes Parameters from our Converted folder
#The calculation method is Fourier Analysis (from Polarized Light book)
#The Converted folder contains 37 measurements (from 0 degree to 360 degree) in form of *.asc
#This code will return a file containing: wavelengths, S0, S1, S2, S3, Polarization Degree, S1/S0, S2/S0, S3/S0, S0-Min, (S0-Min)/Max, abs(S1/S0), abs(S2/S0), abs(S3/S0), Ellipticity(degree), Orientation(degree)

#UPDATE: This code add Ellipticity and Orientation calculation

yourpath = r"C:\Users\hangu\Creative Cloud Files\2. RESEARCH\2020 Laser system test\3. Categorizing Green Laser\2. New Alignment\Try 10 (QWP = vertical at 0 degree) Accumulation 100 _ 0.00499s\1_10. LP1 at Vertical (238) _ LP(stokes) = 0\Converted"

import math
import os
import numpy as np
import pandas as pd

def number_name(file_name):
     return int(file_name[0:-4])

def deg_to_rad(degree):
    return degree*math.pi/180

def rad_to_deg(rad):
    return rad*180/math.pi

#1 Create DataFrame:
df = pd.DataFrame()

for root, dirs, files in os.walk(yourpath, topdown=False):
    files = sorted(files, key=number_name)                  # "files" is a list: 0 10 20 30 ... 360, length = 37
    for name in files[:-1]:                                 # we only want 0 -> 350
        md = open(os.path.join(root, name), 'r')

        intensity_lst = []
        wavelength_lst = []
        #temp_count = 0
        for line in md:
            line = line.split()
            intensity_lst.append(int(float(line[1])))

            #print(temp_count)
            #temp_count += 1

            wavelength_lst.append(float(line[0]))           # wavelength_lst: 397.33273 .... 679.00134, length = 1024, ColA

        #print(name)
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
S0_lst = [a_i - c_i for a_i, c_i in zip(A_lst, C_lst)]          #S0, ColB
S1_lst = [i*2 for i in C_lst]                                   #S1, ColC
S2_lst = [i*2 for i in D_lst]                                   #S2, ColD
S3_lst = [-i for i in B_lst]                                    #S3, ColE

#4 Make other lists:
#PolDeg, ColF
PD_lst = [math.sqrt(s1i**2 + s2i**2 + s3i**2)/s0i for s1i, s2i, s3i, s0i in zip(S1_lst, S2_lst, S3_lst, S0_lst)]
                                                                

#S1/S0
S1_S0_lst = [s1i/s0i for s1i, s0i in zip(S1_lst, S0_lst)]       #S1/S0, ColG

#S2/S0
S2_S0_lst = [s2i/s0i for s2i, s0i in zip(S2_lst, S0_lst)]       #S2/S0, ColH

#S3/S0
S3_S0_lst = [s3i/s0i for s3i, s0i in zip(S3_lst, S0_lst)]       #S3/S0, ColI

#S0-Min
S0_min_lst = [s0i-min(S0_lst) for s0i in S0_lst]                #S0_min, ColJ: (Subtract min of col B)

#S0-Min/Max
S0_minmax_lst = [s0i/max(S0_min_lst) for s0i in S0_min_lst]     #S0_min/max, ColK: (Divide J by max of col J)

#ABSOLS1/S0
S1_S0_abs_lst = [abs(i) for i in S1_S0_lst]                     #ABSOL(S1/S0), ColL: Absolute value of col G

#ABSOLS2/S0
S2_S0_abs_lst = [abs(i) for i in S2_S0_lst]                     #ABSOL(S2/S0), ColM: Absolute value of col H

#ABSOLS3/S0
S3_S0_abs_lst = [abs(i) for i in S3_S0_lst]                     #ABSOL(S3/S0), ColN: Absolute value of col I

orient_lst = [0.5*rad_to_deg(math.atan(s2i/s1i)) for s2i, s1i in zip(S2_lst, S1_lst)]                                       #ColO: Orientation angle (degrees)

ellip_lst = [0.5*rad_to_deg(math.atan(s3i/math.sqrt(s1i**2 + s2i**2))) for s3i, s1i, s2i in zip(S3_lst, S1_lst, S2_lst)]    #ColP: Ellipticity (degrees)



#5 Create a new file containing the stokes parameters:
new_file = open("Stokes parameters (no correction).txt", "w")
new_file.write('Wavelength(nm)' + ' ' + 'S0' + ' ' + 'S1' + ' ' + 'S2' + ' ' + 'S3' 
                + ' ' + 'PolDeg' + ' ' + 'S1/S0' + ' ' + 'S2/S0' + ' ' + 'S3/S0' 
                + ' ' + 'S0-Min' + ' ' + 'S0-Min/Max' + ' ' + 'ABSOL(S1/S0)'
                + ' ' + 'ABSOL(S2/S0)' + ' ' + 'ABSOL(S3/S0)' + ' ' + 'Ellipticity(degree)'+ ' ' + 'Orientation(degree)' + '\n')

for i in range(len(S0_lst)):
    new_file.write(str(wavelength_lst[i]) + ' ' + str(S0_lst[i]) + ' ' + str(S1_lst[i]) + ' ' + str(S2_lst[i]) + ' ' + str(S3_lst[i])
                   + ' ' + str(PD_lst[i]) + ' ' + str(S1_S0_lst[i]) + ' ' + str(S2_S0_lst[i]) + ' ' + str(S3_S0_lst[i]) 
                   + ' ' + str(S0_min_lst[i]) + ' ' + str(S0_minmax_lst[i]) + ' ' + str(S1_S0_abs_lst[i])
                    + ' ' + str(S2_S0_abs_lst[i]) + ' ' + str(S3_S0_abs_lst[i]) + ' ' + str(ellip_lst[i]) + ' ' + str(orient_lst[i]) + '\n')

new_file.close()



