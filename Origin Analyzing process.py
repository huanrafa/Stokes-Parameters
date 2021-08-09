#IMPORTANT: File names has to put in order (eg. 1, 2, 3 ,4 ...) before using this code
#This code is used after applying Stokes parameters code to all data in a measurement set. This code helps grouping each Stokes component, saving time from using Origin.

#Folder contains Stokes files:
yourpath = r"C:\Users\hangu\Desktop\New folder\New folder"


import math
import os
import numpy as np
import pandas as pd

def number_name(file_name):
     return int(file_name[0:-4])


#1 Create DataFrameS:
df_s0 = pd.DataFrame()      #S0
df_s1 = pd.DataFrame()      #Abs(S1)
df_s2 = pd.DataFrame()      #Abs(S2)
df_s3 = pd.DataFrame()      #Abs(S3)
df_pd = pd.DataFrame()      #PolDeg
df_s1_s0 = pd.DataFrame()   #Abs(S1/S0)
df_s2_s0 = pd.DataFrame()   #Abs(S2/S0)
df_s3_s0 = pd.DataFrame()   #Abs(S3/S0)
df_el = pd.DataFrame()      #Ellipticity
df_or = pd.DataFrame()      #Orientation


for root, dirs, files in os.walk(yourpath, topdown=False):
    files = sorted(files, key=number_name)                  # IMPORTANT: File names has to put in order (eg. 1, 2, 3 ,4 ...) before using this code
    for name in files:                                      # Open each Stokes file 
        md = open(os.path.join(root, name), 'r')

        
        wavelength_lst = []
        wavelength_lst_final = []

        s0_lst = []
        s1_lst = []
        s2_lst = []
        s3_lst = []
        pd_lst = []
        s1_s0_lst = []
        s2_s0_lst = []
        s3_s0_lst = []
        el_lst = []
        or_lst = []

        
        line_index = 0
        for line in md:
            if line_index != 0:
                line = line.split()

                wavelength_lst.append(float(line[0]))         #NOTE: the indices here depend on the Stokes file. If you change the way you arrange data in Stokes file, this has to be changed accordingly.
                s0_lst.append(float(line[1]))
                s1_lst.append(float(line[11]))
                s2_lst.append(float(line[12]))
                s3_lst.append(float(line[13]))
                pd_lst.append(float(line[5]))
                s1_s0_lst.append(float(line[14]))
                s2_s0_lst.append(float(line[15]))
                s3_s0_lst.append(float(line[16]))
                el_lst.append(float(line[17]))
                or_lst.append(float(line[18]))
            line_index += 1      


        if len(wavelength_lst_final) < len(wavelength_lst):     #wavelength_lst_final is the list of wavelengths used for all DFs
            wavelength_lst_final = wavelength_lst

        
        df_s0[name] = s0_lst
        df_s1[name] = s1_lst
        df_s2[name] = s2_lst
        df_s3[name] = s3_lst
        df_pd[name] = pd_lst
        df_s1_s0[name] = s1_s0_lst
        df_s2_s0[name] = s2_s0_lst
        df_s3_s0[name] = s3_s0_lst
        df_el[name] = el_lst
        df_or[name] = or_lst
md.close()

#2: Create list of Dataframes and list of names:
dfs = []
dfs.append(df_s0)
dfs.append(df_s1)
dfs.append(df_s2)
dfs.append(df_s3)
dfs.append(df_pd)
dfs.append(df_s1_s0)
dfs.append(df_s2_s0)
dfs.append(df_s3_s0)
dfs.append(df_el)
dfs.append(df_or)

names = ["S0", "Abs(S1)", "Abs(S2)", "Abs(S3)", "PolDeg", "S1S0", "S2S0", "S3S0", "Ellipticity", "Orientation"]
#names = ["S0", "Abs(S1)", "Abs(S2)", "Abs(S3)", "PolDeg", "Abs(S1/S0)", "Abs(S2/S0)", "Abs(S3/S0)", "Ellipticity", "Orientation"]
#PROBLEM: Now we have all DFs, but they still don't have wavelength column (which is supposed to be wavelength_lst_final).

#3 Create new files containing each stokes parameter:
for k in range(len(dfs)):                                               #For each Dataframe:
    new_file = open("{}.txt".format(names[k]), "w")
    #new_file.write('Wavelength(nm)' + ' ' + names[k] + '\n')
    new_file.write('Wavelength(nm)' + ' ')
    for m in range(len(files)):                                        
            new_file.write(names[k] + ' ')
    new_file.write('\n')

    for i in range(len(wavelength_lst_final)):                          #For each wavelength (aka. each row):
        new_file.write(str(wavelength_lst_final[i]) + ' ')

        for j in range(len(files)):                                     #For each value (aka. each column):
            df = dfs[k]
            row = df.loc[i]
            new_file.write(str(row[j]) + ' ')
        new_file.write('\n')

    new_file.close()


#with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#   print(sum_df)
#for i in df.loc[0]:
#    print(i)
#print(min(S0_lst))
#print(C_lst[0])
#print(len(wavelength_lst))
#print(len(list(df.index)))