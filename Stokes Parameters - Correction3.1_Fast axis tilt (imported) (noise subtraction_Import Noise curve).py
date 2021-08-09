#Update (compared to Stokes Parameters - Correction2 (change ABCD)): In this version, we can apply the concept of Fast Axis Tilt: We import an already-made Fast Axis Tilt file
#NOTE: wavelength range of the retardance curve is 416.11859 --> 750.89575
#NOTE: The way we call ABCDE here is different from the book. Please take a look at my "Stokes Correction" file
#UPDATE: This code subtract Background Noise. NOTE: Background noise file depends on CCD's exposure time and accumulation, we have to use the correct Noise Curve.

#This code will return a file containing: wavelengths, S0, S1, S2, S3, Polarization Degree, S1/S0, S2/S0, S3/S0, S0-Min, (S0-Min)/Max, abs(S1), abs(S2), abs(S3), abs(S1/S0), abs(S2/S0), abs(S3/S0), Ellipticity(degree), Orientation(degree)


#Intensity files:
yourpath = r"C:\Users\hangu\Creative Cloud Files\1. P3HT Measure\1. Huan's data\2021\1. Measurements\11. P3HT Mn = 54000 + CHCl3 _ Methanol measurement sets\2_5. Me 5 (Day 85)\Attempt 3\Converted"
#BackgroundNoise curve:
noisepath = r"C:\Users\hangu\Creative Cloud Files\1. P3HT Measure\1. Huan's data\2021\1. Measurements\11. P3HT Mn = 54000 + CHCl3 _ Methanol measurement sets\2_1. Me 1 (Day 84)\Noise curve _ Accumulation 5 _ 0.70002s (smoothed).txt"
#Retardance curve file (radian):
thetapath = r'C:\Users\hangu\Creative Cloud Files\2. RESEARCH\2020 Laser system test\retardance curve extended(416_750nm) (QWP_Stokes) (radian) Try3.txt'
#Fast Axis Tilt file (radian):
deltapath = r'C:\Users\hangu\Creative Cloud Files\2. RESEARCH\2020 Laser system test\Fast_Axis_Tilt (HPL).txt'

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
    
def cotan(radian):
    return 1/math.tan(radian)

#0 Create Noise list:
md2 = open(noisepath, 'r')

noise_lst = []
wavelength_n_lst = []
for line in md2:
    line = line.split()
    noise_lst.append(float(line[1]))
    wavelength_n_lst.append(float(line[0]))                 

md2.close()

#1 Create DataFrame:
df = pd.DataFrame()

for root, dirs, files in os.walk(yourpath, topdown=False):
    files = sorted(files, key=number_name)                  # "files" is a list: 0 10 20 30 ... 360, length = 37
    for name in files[:-1]:                                 # we only want 0 -> 350
        md = open(os.path.join(root, name), 'r')

        intensity_lst = []
        wavelength_lst = []
        
        noise_index = 0        
        for line in md:
            line = line.split()
            intensity_lst.append(int(float(line[1])) - noise_lst[noise_index])

            noise_index += 1
            wavelength_lst.append(float(line[0]))           # wavelength_lst: any range, length = 1024, ColA

        df[int(name[0:-4])] = intensity_lst
md.close()

#1_2_1 Create Retardance curve:
md2 = open(thetapath, 'r')

retardance_lst = []
wavelength_r_lst = []
for line in md2:
    line = line.split()
    retardance_lst.append(float(line[1]))
    wavelength_r_lst.append(float(line[0]))                 # wavelength_r_lst: 416.11859 --> 750.89575, length = 1220

md2.close()

#1_2_2 Create Fast Axis Tilt:
md3 = open(deltapath, 'r')

delta_lst = []
wavelength_d_lst = []
for line in md3:
    line = line.split()
    delta_lst.append(float(line[1]))
    wavelength_d_lst.append(float(line[0]))                 # wavelength_d_lst: 416.11859 --> 697.52661, length = 1024

md3.close()

#1_3 Define the range of Retardance curve being used for correction:
if float(wavelength_lst[0]) > float(wavelength_r_lst[0]):
    min_range = abs(float(wavelength_lst[0]) - float(wavelength_r_lst[0]))
    index = 0
    for i in range(len(wavelength_r_lst)):
        #print(min_range)
        if abs(float(wavelength_lst[0]) - float(wavelength_r_lst[i])) < min_range:
            min_range = abs(float(wavelength_lst[0]) - float(wavelength_r_lst[i]))
            index = i
        

    if wavelength_lst[-1] <= wavelength_r_lst[-1]:                             # if the wavelength range does not exceed 750nm (Case1)
        wavelength_r_lst = wavelength_r_lst[index:index+len(wavelength_lst)]   # new wavelength_r_lst, length = len(wavelength_lst)
        retardance_lst = retardance_lst[index:index+len(wavelength_lst)]       # new retardance_lst, length = len(wavelength_lst)
    else:                                                                      # if the wavelength range does exceed 750nm (Case2)
        df = df[:len(wavelength_r_lst)-index]
        wavelength_lst = wavelength_lst[:len(wavelength_r_lst)-index]

        wavelength_r_lst = wavelength_r_lst[index:]   
        retardance_lst = retardance_lst[index:]
               

else:                                                                           #Case3
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

#1_4 Define the range of Fast Axis curve being used for correction:
if float(wavelength_lst[0]) > float(wavelength_d_lst[0]):
    min_range = abs(float(wavelength_lst[0]) - float(wavelength_d_lst[0]))
    index = 0
    for i in range(len(wavelength_d_lst)):
        #print(min_range)
        if abs(float(wavelength_lst[0]) - float(wavelength_d_lst[i])) < min_range:
            min_range = abs(float(wavelength_lst[0]) - float(wavelength_d_lst[i]))
            index = i
        

    if wavelength_lst[-1] <= wavelength_d_lst[-1]:                             # Case1
        wavelength_d_lst = wavelength_d_lst[index:index+len(wavelength_lst)]   # new wavelength_d_lst, length = len(wavelength_lst)
        delta_lst = delta_lst[index:index+len(wavelength_lst)]                 # new delta_lst, length = len(wavelength_lst)
    else:                                                                      # Case2
        df = df[:len(wavelength_d_lst)-index]
        wavelength_lst = wavelength_lst[:len(wavelength_d_lst)-index]
        retardance_lst = retardance_lst[:len(wavelength_d_lst)-index]

        wavelength_d_lst = wavelength_d_lst[index:]   
        delta_lst = delta_lst[index:]
               

else:                                                                           #Case3
    min_range = abs(float(wavelength_d_lst[0]) - float(wavelength_lst[0]))
    index = 0
    for i in range(len(wavelength_lst)):
        if abs(float(wavelength_d_lst[0]) - float(wavelength_lst[i])) < min_range:
            min_range = abs(float(wavelength_d_lst[0]) - float(wavelength_lst[i]))
            index = i
        #print(str(i))

    wavelength_d_lst = wavelength_d_lst[:(len(wavelength_lst)-index)]   # new wavelength_d_lst
    delta_lst = delta_lst[:(len(wavelength_lst)-index)]                 # new delta_lst
    
    df = df[index:]                                                     # new dataframe, which is shorter than the previous one
    wavelength_lst = wavelength_lst[index:]                             # new wavelength_lst, this is only used for printing wavelength labels in the output file
    retardance_lst = retardance_lst[index:]                             # new retardance_lst, which is shorter than the previous one


#print(min_range)
#print(index)
print(len(wavelength_lst))
print(len(retardance_lst))
print(len(delta_lst))
print(len(list(df.index.values)))


#2 Make lists of A B C D E:
#NOTE: The way we call ABCDE here is different from the book. Please take a look at my "Stokes Correction" file
A_lst = []
B_lst = []
C_lst = []
D_lst = []
E_lst = []

for wavelength in list(df.index):
    cal_A = 2/36*(df.loc[wavelength].sum())

    cal_B = 0
    deg = 0
    for intensity in df.loc[wavelength]:
        cal_B += intensity*math.cos(4*deg_to_rad(deg))
        deg += 10
    cal_B = 4/36*cal_B

    cal_C = 0
    deg = 0
    for intensity in df.loc[wavelength]:
        cal_C += intensity*math.sin(4*deg_to_rad(deg))
        deg += 10
    cal_C = 4/36*cal_C

    cal_D = 0
    deg = 0
    for intensity in df.loc[wavelength]:
        cal_D += intensity*math.sin(2*deg_to_rad(deg))
        deg += 10
    cal_D = 4/36*cal_D

    cal_E = 0
    deg = 0
    for intensity in df.loc[wavelength]:
        cal_E += intensity*math.cos(2*deg_to_rad(deg))
        deg += 10
    cal_E = 4/36*cal_E

    A_lst.append(cal_A)
    B_lst.append(cal_B)
    C_lst.append(cal_C)
    D_lst.append(cal_D)
    E_lst.append(cal_E)

#2_2 Make the list of delta (Fast Axis Tilt): unit = rad
#??? Should we use delta_list created by D and E here? Or should we use delta_list created from some particular light source (VPL, HPL ...)?
#delta_lst = [(math.atan(e_i/d_i))/2 for e_i, d_i in zip(E_lst, D_lst)]

#3 Make lists of S0 S1 S2 S3:
#NOTE: Here we calculate S0_R, S1_R, S2_R, S3_R directly from ABCD and delta (unlike what we did in "Stokes Parameters - Correction2.py", which we calculated S0, S1, S2, S3 first)

S1R_lst = [(b_i*math.cos(4*delta)-c_i*math.sin(4*delta))/(math.sin(phi/2)*math.sin(phi/2)) for b_i, c_i, delta, phi in zip(B_lst, C_lst, delta_lst, retardance_lst)]        #S1, ColC
S2R_lst = [(b_i*math.sin(4*delta)+c_i*math.cos(4*delta))/(math.sin(phi/2)*math.sin(phi/2)) for b_i, c_i, delta, phi in zip(B_lst, C_lst, delta_lst, retardance_lst)]        #S2, ColD
S0R_lst = [a_i - s1_i*(math.cos(phi/2)*math.cos(phi/2)) for a_i, s1_i, phi in zip(A_lst, S1R_lst, retardance_lst)]                                                          #S0, ColB
S3R_lst = [-d_i/(math.sin(phi)*math.cos(2*delta)) for d_i, phi, delta in zip(D_lst, retardance_lst, delta_lst,)]                                                            #S3, ColE


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
S0R_min_lst = [s0i-min(S0R_lst) for s0i in S0R_lst]               #S0_R_min, ColJ: (Subtract min of col B)

#S0-Min/Max
S0R_minmax_lst = [s0i/max(S0R_min_lst) for s0i in S0R_min_lst]    #S0_R_min/max, ColK: (Divide J by max of col J)

#ABSOL S1
S1_abs_lst = [abs(i) for i in S1R_lst]                             #ABSOL(S1), ColL: Absolute value of col C

#ABSOL S2
S2_abs_lst = [abs(i) for i in S2R_lst]                             #ABSOL(S2), ColM: Absolute value of col D

#ABSOL S3
S3_abs_lst = [abs(i) for i in S3R_lst]                             #ABSOL(S3), ColN: Absolute value of col E

#ABSOLS1/S0
S1_S0_abs_lst = [abs(i) for i in S1_S0_lst]                       #ABSOL(S1_R/S0_R), ColO: Absolute value of col G

#ABSOLS2/S0
S2_S0_abs_lst = [abs(i) for i in S2_S0_lst]                       #ABSOL(S2_R/S0_R), ColP: Absolute value of col H

#ABSOLS3/S0
S3_S0_abs_lst = [abs(i) for i in S3_S0_lst]                       #ABSOL(S3_R/S0_R), ColQ: Absolute value of col I

orient_lst = [0.5*rad_to_deg(math.atan(s2i/s1i)) for s2i, s1i in zip(S2R_lst, S1R_lst)]                                        #ColR: Orientation angle (degrees)

ellip_lst = [0.5*rad_to_deg(math.atan(s3i/math.sqrt(s1i**2 + s2i**2))) for s3i, s1i, s2i in zip(S3R_lst, S1R_lst, S2R_lst)]    #ColS: Ellipticity (degrees)


#5 Create a new file containing the stokes parameters:
new_file = open("Stokes parameters (noise subtracted _ Import Noise Curve)(corrected_retardance + Fast Axis HPL).txt", "w")
new_file.write('Wavelength(nm)' + ' ' + 'S0_R' + ' ' + 'S1_R' + ' ' + 'S2_R' + ' ' + 'S3_R' 
                + ' ' + 'PolDeg' + ' ' + 'S1_R/S0_R' + ' ' + 'S2_R/S0_R' + ' ' + 'S3_R/S0_R' 
                + ' ' + 'S0_R-Min' + ' ' + 'S0_R-Min/Max' + ' ' + 'ABSOL(S1_R)'
                + ' ' + 'ABSOL(S2_R)' + ' ' + 'ABSOL(S3_R)' + ' ' + 'ABSOL(S1_R/S0_R)'
                + ' ' + 'ABSOL(S2_R/S0_R)' + ' ' + 'ABSOL(S3_R/S0_R)' + ' ' + 'Ellipticity(degree)'+ ' ' + 'Orientation(degree)' + '\n')

for i in range(len(S0R_lst)):      
    new_file.write(str(wavelength_lst[i]) + ' ' + str(S0R_lst[i]) + ' ' + str(S1R_lst[i]) + ' ' + str(S2R_lst[i]) + ' ' + str(S3R_lst[i])
                   + ' ' + str(PD_lst[i]) + ' ' + str(S1_S0_lst[i]) + ' ' + str(S2_S0_lst[i]) + ' ' + str(S3_S0_lst[i]) 
                   + ' ' + str(S0R_min_lst[i]) + ' ' + str(S0R_minmax_lst[i]) + ' ' + str(S1_abs_lst[i])
                    + ' ' + str(S2_abs_lst[i]) + ' ' + str(S3_abs_lst[i]) + ' ' + str(S1_S0_abs_lst[i])
                    + ' ' + str(S2_S0_abs_lst[i]) + ' ' + str(S3_S0_abs_lst[i]) + ' ' + str(ellip_lst[i]) + ' ' + str(orient_lst[i]) + '\n')

new_file.close()


