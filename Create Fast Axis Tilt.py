#Update (compared to Stokes Parameters - Correction2 (change ABCD)): In this version, we can apply the concept of Fast Axis Tilt: tan(4*delta) = -C/B
#This code returns "Fast Axis Tilt file"

#Note: The equation tan(4*delta) = -C/B is only applicable for Horizontal/Vertical Polarized Light
#Note: wavelength range of the retardance curve is 416.11859 --> 750.89575

#Intensity files:
yourpath = r'C:\Users\PA\Desktop\Test objectives 2020\6. Stokes Parameters of white light\Vertical Polarized Light\Converted'
#Retardance curve file (radian):
thetapath = r'C:\Users\PA\Desktop\retardance curve extended(416_750nm) (QWP_Stokes) (radian).txt'

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
delta_lst = [(math.atan(-c_i/b_i))/4 for b_i, c_i in zip(B_lst, C_lst)]


#5 Create a new file containing the stokes parameters:
new_file = open("Fast_Axis_Tilt.txt", "w")
new_file.write('Wavelength' + ' ' + 'Fast_Axis_Tilt' + '\n')

for i in range(len(delta_lst)):
    new_file.write(str(wavelength_lst[i]) + ' ' + str(delta_lst[i]) + '\n')

new_file.close()


