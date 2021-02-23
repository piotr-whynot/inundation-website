import sys
import numpy as np
import datetime
import pandas as pd
#from pandas.plotting import register_matplotlib_converters
#register_matplotlib_converters()
#from netCDF4 import Dataset
import timeit
#from matplotlib import pyplot as plt
#%load_ext Cython
#import Cython
#import json, shutil
import pyximport; pyximport.install()
import model_boteti_cython as hcy


#*****************************************************************************
#definition of paramater and input files 


debug=True

file_modpar = sys.argv[1]
file_init = sys.argv[2]
file_input = sys.argv[3]
spinup = int(sys.argv[4])


outputfiles=[]
for i in range(5,len(sys.argv)):
    outputfiles=outputfiles+[sys.argv[i]]

file_modset = "./config/modset_boteti.dat"

if file_modpar=="default":
    file_modpar = "./config/modpar_boteti.csv"
if file_init=="default":
    file_init="./config/init_boteti.csv"



#*****************************************************************************
def evap_calc():
    global glnoftsteps, glrecdate, gltminmax, glpet   
    r0 = [16.35261505, 14.95509782, 12.8087226, 10.86376736, 9.847079426, 10.22676382, 11.84785549, 14.00041471, 15.76601788, 16.82545576, 17.20206337, 17.09344496]
    kc= [0.95, 0.9, 0.8, 0.7, 0.63, 0.6, 0.6, 0.63, 0.7, 0.8, 0.9, 0.95]
    glpet=[]
    for ts in range(glnoftsteps):
        curmonth=datetime.datetime.strptime(glrecdate[ts], "%b-%Y").month
        temp= 31 * kc[curmonth-1] * 0.0023 * r0[curmonth-1] * (gltminmax[ts][1] - gltminmax[ts][0]) ** 0.5 * (((gltminmax[ts][1] + gltminmax[ts][0]) / 2) + 17.8)
        glpet.append(temp)
    glpet=np.array(glpet)
    print ("calculated evap...")
    

def write_output_cellinundation(file_output):
    global glout_sa
    print ("writing surface area output file...")
    glout_sa.astype(int).to_csv(file_output)
    print ("done")

def write_output_totalinundation(file_output):
    global glout_sa
    print ("writing surface area output file...")
    glout_sa.astype(int).to_csv(file_output)
    print ("done")


def write_output_cellvolume(file_output):
    global glout_sv
    print ("writing surface volume output file...")
    glout_sv.astype(int).to_csv(file_output)
    print ("done")

def write_output_cellq(file_output):
#write discharges for each cell
    global glout_sqout
    print ("writing discharge output file...")
    glout_sqout.astype(int).to_csv(file_output)
    print ("done")

def write_output_hydroregions(file_output):
    #write ecoregions for each cell
    global glhydroregions
    print ("writing hydro regions output file...")
    glhydroregions.astype(float).to_csv(file_output)
    print ("done")

def write_output_inundateddistance(file_output):
    #write inundated distance
    global glinunddist
    print ("writing inundated distance output file...")
    glinunddist.astype(int).to_csv(file_output)
    print ("done")



def mergecells(glvar,skip):
    #write areas for each cell
    global gloutputflag, glswcellname, glrecdate
    selcells=glvar[:,np.array(gloutputflag)==1]
    cellnames=np.array(glswcellname)
#    print(cellnames)
    tooutput=np.array(gloutputflag)
    selcellnames=cellnames[tooutput==1]
    selcellnames=['Boteti']
    merged=[[0]]
    outputtable=[]
    outputcellnames=[]
    for j,m in enumerate(merged):
        outputcellnames=outputcellnames+[selcellnames[j]]
        current=0
        for i in m:
            current=current+selcells[:,i]
        outputtable=outputtable+[current]
    index=pd.date_range(glrecdate[0], freq="M", periods=len(glrecdate))
    outputFrame=pd.DataFrame(np.array(outputtable).T, index=index, columns=outputcellnames)    
    outputFrame=outputFrame.iloc[skip:,:]
    return outputFrame


def write_init(output_file, _ts):
    global glnofswcells, glfin_sv, glfin_fv, glfin_iv
    print(glnofswcells, glfin_sv.shape, glfin_fv.shape, glfin_iv.shape)
    with open(output_file, "w") as outf:
        for scell in range(glnofswcells):
            outf.write("s_"+str(scell)+","+str(int(glfin_sv[_ts,scell]))+"\n")
        for scell in range(glnofswcells):
            line="f_"+str(scell)+","+",".join([str(np.round(x,2)) for x in glfin_fv[_ts,scell,:].tolist()])
            outf.write(line+"\n")
        for scell in range(glnofswcells):
            line="i_"+str(scell)+","+",".join([str(np.round(x,2)) for x in glfin_iv[_ts,scell,:].tolist()])
            outf.write(line+"\n")
            

def wbalance_calc():
    global glsq_in, glfin_spre, glfin_sqout, glfin_sev, glfin_sinf, glfin_sv, glsv_init, glfin_fv, glfv_init 
    global glfin_fev, glfin_finf, glfin_fgwout,glfin_fpre, glfin_iv, gliv_init, glfin_ipre, glfin_iev
    #surface reservoir
    sinflow=glfin_sqin.sum(0)
    srainfall=glfin_spre.sum(0)
    soutflow=glfin_sqout.sum(0)
    sevap=glfin_sev.sum(0)
    sinfiltration=glfin_sinf.sum(0)
    svdelta=glfin_sv[-1,:]-glsv_init
    sinputs=sinflow+srainfall
    soutputs=soutflow+sevap+sinfiltration
    swbal=sinputs-soutputs-svdelta
#    swbalclosure=wbalmerge(swbal)/wbalmerge(svdelta)*100
    swbalclosure=swbal/sinputs*100
    
    #floodplain reservoir
    fvdelta=(glfin_fv[-1,:,:]-glfv_init).sum(1)
    fevap=glfin_fev.sum((0,2))
    finfiltration=glfin_finf.sum((0,2))
    fgwoutflow=glfin_fgwout.sum((0,2)) 
    frainfall=glfin_fpre.sum((0,2))
    finputs=finfiltration+frainfall
    foutputs=fgwoutflow+fevap
    print (finputs.shape, foutputs.shape, fvdelta.shape)
    fwbal=finputs-foutputs-fvdelta
    fwbalclosure=fwbal/finputs*100
#    print fvdelta, fevap, frainfall,finfiltration,fgwoutflow
    
    #island reservoir
    ivdelta=(glfin_iv[-1,:,:]-gliv_init).sum(1)
    ievap=glfin_iev.sum((0,2))
    irainfall=glfin_ipre.sum((0,2))
    iinputs=fgwoutflow+irainfall
    ioutputs=ievap
    iwbal=iinputs-ioutputs-ivdelta
    iwbalclosure=iwbal/iinputs*100

    return swbalclosure[np.where(glfinalsumflag==1)[0]], fwbalclosure[np.where(glfinalsumflag==1)[0]], iwbalclosure[np.where(glfinalsumflag==1)[0]]



def calc_hydroregions(_thresh, skip):
    global glhydroregions
    _poolyears=3
    _sa=mergecells(glfin_sa, 0)
    _sa[_sa>_thresh]=_thresh
    _sa=_sa/_thresh
    _max=_sa.resample("A-Jul").max()
    permanent=_sa.resample("A-Jul").min()
    pastwet=_sa.resample("A-Jul").max().rolling(_poolyears).max()
    pools=pastwet-permanent
    dry=1-pastwet
    glhydroregions=pd.concat([permanent,pools,dry], 1)
    glhydroregions.columns=["permanent","pools","dry"]
    glhydroregions=glhydroregions.iloc[skip:,:]


def calc_inundateddistance(_thresh, _maxdist, skip):
    #write inundated distance
    global glinunddist
    _sa=mergecells(glfin_sa, 0)
    glinunddist=_sa/_thresh
    glinunddist[glinunddist>1]=1
    glinunddist=glinunddist.iloc[skip:,0]*_maxdist
    print ("done")



def timer():
    global t0
    _t=timeit.default_timer()
    print (_t-t0)
    t0=timeit.default_timer()

            
#*****************************************************************************
def read_modset(file_modset):
    global glconvcrit, glmaxiter, glnofswcells, glnofgwcells, glnofoutlets, glnoflinks, gldowncell, gloutputflag, glfinalsumflag, glswcellname
    print("reading model setup from "+file_modset+"...")
    with open(file_modset, "r") as fmodset:
        #convergence criterion
        glconvcrit=float(fmodset.readline().strip().split(",")[1])
        #maxiterations
        glmaxiter=int(fmodset.readline().strip().split(",")[1])
        
        # numbers of cells are read
        glnofswcells=int(fmodset.readline().strip().split(",")[1])
        glnofgwcells=int(fmodset.readline().strip().split(",")[1])
        glnofoutlets=int(fmodset.readline().strip().split(",")[1])
        # links between reservoirs are read
        glnoflinks=[]
        gldowncell=[]
        for scell in range(glnofswcells):
            nlinks=int(fmodset.readline().strip().split(",")[1])
            glnoflinks.append(nlinks)
            temp=[]
            if nlinks>0:
                for link in range(nlinks):
                    temp.append(int(fmodset.readline().strip().split(",")[1]))
            gldowncell.append(temp)
        # ouput flag for cells
        gloutputflag=[]
        for scell in range(glnofswcells):
            gloutputflag.append(int(fmodset.readline().strip().split(",")[1]))

        # final sum flag
        glfinalsumflag=[]
        for scell in range(glnofswcells):
            glfinalsumflag.append(int(fmodset.readline().strip().split(",")[1]))

        glswcellname=[]
        for scell in range(glnofswcells):
            cellname=fmodset.readline().strip().split(",")[1]
            #print(scell,cellname)
            glswcellname.append(cellname)
        glfinalsumflag=np.array(glfinalsumflag)
    print("done")


    
    
    
    
#*****************************************************************************
   
#*****************************************************************************
def read_modpar(file_modpar):
    global glgwpar, glunitpar, glexponent, glbpar, glk, glV, gldelay,glstatratio,glfa, glia,glkgw,glfa_total,glnofgwcells,glnofswcells, glnoflinks
    print ("reading model parameters from: "+file_modpar)
    with open(file_modpar, "r") as fmodpar:
        # spatially constant parameters
        fdet=float(fmodpar.readline().strip().split(",")[1])
        idet=float(fmodpar.readline().strip().split(",")[1])
        fpor=float(fmodpar.readline().strip().split(",")[1])
        ipor=float(fmodpar.readline().strip().split(",")[1])
    
        # volume-area parameters
        glbpar=[]
        glexponent=[]
        for scell in range(glnofswcells):
            temp=fmodpar.readline().strip().split(",")
#            print("vol-area", temp)
            glexponent.append(float(temp[1]))
            glbpar.append(float(temp[2]))

        # outlet parameters
        glk=[]
        glV=[]
        for scell in range(glnofswcells):
            temp2=[]
            temp3=[]
            if glnoflinks[scell] > 0:
                for link in range(glnoflinks[scell]):
                    temp=fmodpar.readline().strip().split(",")
#                    print("outlet", temp)
                    temp2.append(float(temp[1]))
                    temp3.append(float(temp[2]))                
            glk.append(temp2)
            glV.append(temp3)
            

        # delay parameter for units
        gldelay=[]
        for scell in range(glnofswcells):
            gldelay.append(int(fmodpar.readline().strip().split(",")[1]))

        # maun/shakawe rainfall ratio parameters
        glstatratio=[]
        for scell in range(glnofswcells):
            glstatratio.append(float(fmodpar.readline().strip().split(",")[1]))

        # groundwater reservoir areas and "transmissivity"
        glfa=[]
        glia=[]
        glkgw=[]
        glfa_total=[]
        for scell in range(glnofswcells):
            temp=fmodpar.readline().strip().split(",")
#            print("gw", temp)
            glfa.append(float(temp[1]))
            glia.append(float(temp[2]))
            glkgw.append(float(temp[3]))
            glfa_total.append(float(temp[1])*glnofgwcells)
            
            
    outletpar=np.zeros([2,30])
    for i,k in enumerate(glk):
        for ii,kk in enumerate(k):
            outletpar[i,ii]=kk
    for i,v in enumerate(glV):
        for ii,vv in enumerate(v):
            outletpar[i,ii+10]=vv
    for i,c in enumerate(gldowncell):
        for ii,cc in enumerate(c):
            outletpar[i,ii+20]=cc

    glunitpar=np.array(gldelay).reshape(-1,1)
    glunitpar=np.append(glunitpar, np.array(glstatratio).reshape(-1,1), axis=1)
    glunitpar=np.append(glunitpar, np.array(glbpar).reshape(-1,1), axis=1)
    glunitpar=np.append(glunitpar, np.array(glexponent).reshape(-1,1), axis=1)
    glunitpar=np.append(glunitpar, np.array(glfa).reshape(-1,1), axis=1)
    glunitpar=np.append(glunitpar, np.array(glia).reshape(-1,1), axis=1)
    glunitpar=np.append(glunitpar, np.array(glkgw).reshape(-1,1), axis=1)
    print(glunitpar.shape, outletpar.shape)
    glunitpar=np.append(glunitpar, outletpar, axis=1)

    glgwpar=np.array([fdet,fpor,idet,ipor])
    print ("done")

    

 
def read_input(file_input):
    global glrecdate, glinflow, glprec, glpet, gltminmax, glnoftsteps,glstatratio

    print ("reading input data from: "+file_input)
    inputData=pd.read_csv(file_input, index_col=0, parse_dates=True)
    
    glrecdate=inputData.index.strftime("%Y-%m-%d")
    glinflow=inputData['Inflow-Maun'].values.astype("float")
    prec=inputData['Rainfall-Maun'].values.astype("float")
    if inputData.shape[1]==3:
        glpet=inputData['PET-Maun'].values*0.85
    else:
        gltmin=inputData['MinTemperature-Maun'].values
        gltmax=inputData['MaxTemperature-Maun'].values
        evap_calc()
    glnoftsteps=inputData.shape[0]
    
    #calculating unit rainfall
    ratios=np.tile(np.array(glstatratio).reshape(-1,1),glnoftsteps).T
    glprec=prec[:].reshape(-1,1)*ratios
    print(glprec.shape, ratios.shape,prec.shape)
    print (str(glnoftsteps) + " time steps read")

#*****************************************************************************
def read_init(file_init):
    global glsv_init, glfv_init, gliv_init, glnofswcells, glnofgwcells
    
    print ("reading initial condition from: "+file_init)
    with open(file_init, "r") as finit:
        data=finit.readlines()
        # initial storage of surface cells
    temp=data[0:glnofswcells]
    temp=np.array([x.strip().split(",") for x in temp])
#    print(temp)
    glsv_init=temp[:,1].astype(float)
        
    #initial storage of groundwater cells
    temp=data[glnofswcells:(glnofswcells*2)]
    temp=np.array([x.strip().split(",") for x in temp])
#    print (temp)
    glfv_init=temp[:,1:].astype(float)
    
    temp=data[(glnofswcells*2):(glnofswcells*3)]
    temp=np.array([x.strip().split(",") for x in temp])
#    print (temp)
    gliv_init=temp[:,1:].astype(float)
    
    print("done")


    
    
    
    


    
    
    
print ("parameters",file_modpar)
print ("initialization", file_init)
print ("input",file_input)
print ("spinup", spinup)
print ("output", outputfiles)

#debug=False
debug1=True

#start timer
t0 = timeit.default_timer()


read_modset(file_modset)                                #reading model configuration
read_modpar(file_modpar)
read_input(file_input)                                  #reading inputs
read_init(file_init)                                    #reading initial conditions





timer()
read_modpar(file_modpar)

result=hcy.model_calc(glinflow, glprec, glpet, glsv_init, glfv_init, gliv_init, glunitpar, glgwpar)                                 #this is when the model is actually run
timer()


glfin_sqin, glfin_sa, glfin_sv, glfin_sev, glfin_spre, glfin_sqout,glfin_sinf,\
glfin_fv, glfin_fev,glfin_fpre,glfin_fgwout,glfin_finf,\
glfin_iv, glfin_iev,glfin_ipre=result


glout_sqin=mergecells(glfin_sqin, spinup)
glout_sa=mergecells(glfin_sa, spinup)
glout_sv=mergecells(glfin_sv, spinup)
glout_sqout=mergecells(glfin_sqout, spinup)
glout_sev=mergecells(glfin_sev, spinup)
glout_sinf=mergecells(glfin_sinf, spinup)

print("done")
print()

thresh=16
maxdist=400

for outputfile in outputfiles:
    print()
    print(outputfile)
    if "allvolumes" in outputfile:
        write_output_cellvolume(outputfile)
    if "alloutflows" in outputfile:
        write_output_cellq(outputfile)
    if "inundateddistance" in outputfile:
        calc_inundateddistance(thresh,maxdist, spinup*12)
        write_output_inundateddistance(outputfile)
    if "totalinundation" in outputfile:
        write_output_totalinundation(outputfile)                       #total inundation
    if "hydroregions" in outputfile:
        calc_hydroregions(thresh, spinup)
        write_output_hydroregions(outputfile)                       #hydroregions
    if "finalcond" in outputfile:
        write_init(outputfile, -1)
    if "input" in outputfile:
        donothing=True


print ()
print("success")
