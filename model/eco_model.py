"""

Simple model to translate Okavango Delta's surface area into area of Hydro-ecological units

Usage
----------
    python eco_model.py input_file output_file

Parameters
----------
input_file : str
    path and name of the CSV file with input data. File should be a file created by running hydro_model.py

output_file: str
    path and name of file in which output will be stored.
   
Returns
-------
    file: a CSV file containing surface area of hydro-ecologial regions given on an annual basis

"""


#importing modules
import sys
try:
    import numpy as np
    import pandas as pd
except:
    print("")
    print("aborted run. python module missing.")
    print("required python modules: numpy, pandas")
    print("")
    sys.exit()

sys.path.append('./config/')
import gl #this is a file in ./config/ directory which is empty, but a reference to it is used to store global variables


if len(sys.argv)<3:
    print(__doc__)
    sys.exit()



#reading arguments
file_input=sys.argv[1]
file_output=sys.argv[2]

def read_input(inputfile):
    with open(inputfile, "r") as inpf:
        print("reading "+inputfile+"...")
        data=[x.strip("\n").split(",") for x in inpf.readlines()[1:]]
    data=np.array(data)
    nunits=data.shape[1]-2
    dates=pd.to_datetime(data[:,0])
    firstmonth=dates[0].month
    print(firstmonth)
    first2read=(12-firstmonth+1)%12
    gl.firstyear=dates[first2read].year
    print("input file has "+str(len(dates))+" monthly time and "+str(data.shape[1]-2)+" units")
    print("January at timestep "+str(first2read))
    data=data[(first2read):,1:nunits].astype("int")
    gl.floodsize=data.sum(1)
    print(gl.floodsize)

    nts,ncol=data.shape

    print("retained "+str(nts)+" monthly time steps for processing")
    print("done\n")


#new transitions proposed by Mike in e-mail from feb 2015
# are these in the last year? or in the three years prior?
#Division 1: If Hd le 0, SAV; if  Hd ge 12, PC;
#Division 2: If Hd le 4.7 go to Dry; if Hd gt 4.7 go to Wet;
#Division 3a: In Dry, if Hd le 2.8 go to S, if Hd gt 2.8 go to G
#Division 3b: In Wet, if Hd le 6.3 go to SF, if Hd gt 6.3 go to AQ

ecoclasses=["Aquatic","Sedges","Grassland","Savanna"]

def model_calc():
    print("calculating... ")
    size=[]
    nofyears=int(np.floor(len(gl.floodsize)/12))
    nmonths=nofyears*12
    temp=np.copy(gl.floodsize[0:nmonths])
    temp=temp.reshape(nofyears, 12)
    areayear=np.mean(temp,1)
    sizerange=range(1,12000, 1)
    ecoall=[]
    for size in sizerange:
        d=np.sum(temp>size, 1)
        eco=[2]*nofyears
        for y in range(nofyears):
            if eco[y-1]==1: #A
                # rules for Aquatic
                if d[y] == 0:
                    eco[y] = 2 #RS
                else:
                    if d[y - 1] == 12:
                        eco[y] = 1 #"A"
                    elif d[y - 2] == 12 and d[y - 3] == 12 and d[y - 4] == 12:
                        eco[y] == 1 #"A"
                    else:
                        eco[y] = 2 #"RS"
            elif eco[y-1]==2: #"RS"
            # rules for Sedges
                if d[y]== 0:
                    eco[y] = 3 #"G"
                elif d[y - 1] < 12:
                    eco[y] = 2  #"RS"
                else:
                    eco[y]=1 #A
    #            elif d[y - 1] ==12:
    #                if d[y - 2] ==12:
    #                    eco[y] = 1 #"A"
    #                else:
    #                    eco[y] = 2 #"RS"

            elif eco[y-1]==3: #"G"
            # rules for Grassland
                if d[y]== 0:
                    if d[y - 1]== 0:
                        if d[y - 2] > 0 or d[y - 3] > 0 or d[y - 4] > 0:
                            eco[y] = 3 #"G"
                        else:
                            eco[y] = 4 #"S"
                    elif d[y - 1] > 0:
                        eco[y] = 3 #"G"
                elif d[y] > 0:
                    if d[y - 1]==0:
                        eco[y]== 3 #"G"
                    else:
                        if d[y - 2]==0:
                            eco[y] = 3 #"G"
                        else:
                            eco[y] = 2 #"RS"

            elif eco[y-1]==4: #"S"
                # rules for Savanna
                if d[y]== 0:
                    eco[y] = 4 #"S"
                elif d[y] > 1:
                    eco[y] = 3 #"G"
                else:
                    eco[y] = 4 #"S"
        ecoall=ecoall+[eco]
    ecoall=np.array(ecoall)
    gl.ecototal=[[]]*5
    for j in range(0,4):
        gl.ecototal[j]=np.sum(ecoall==j+1, 0)
    gl.ecototal=np.array(gl.ecototal)
    print("done\n")



def write_output(file_output):
    print("writing "+file_output+"...")
    with open(file_output, "w") as foutput:
        foutput.write("Year,");
        for unit in range(4):
            foutput.write(ecoclasses[unit]+",");
        foutput.write("\n");
        nts=len(gl.ecototal[0])
        for ts in range(0, nts):
            foutput.write(str(gl.firstyear+ts)+",")
            for unit in range(4):
                foutput.write(str(int(gl.ecototal[unit][ts]))+",");
            foutput.write("\n");
    print ("output has "+str(nts)+" annual time steps")
    print("done\n")



read_input(file_input)
model_calc()
write_output(file_output)


