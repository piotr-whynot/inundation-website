#!/usr/bin/env python
# coding: utf-8

import sys,os
import numpy as np
import datetime
import pandas as pd
import timeit
import pyximport; pyximport.install()
import model_delta_cython as hcy
from pandas.tseries.offsets import DateOffset

#*****************************************************************************
#definition of paramater and input files 

file_modset = "./config/modset_delta.dat"

debug=True

file_modpar = sys.argv[1]
file_init = sys.argv[2]
file_input = sys.argv[3]
spinup = int(sys.argv[4])

if file_modpar=="default":
    file_modpar = "./config/modpar_delta.csv"
if file_init=="default":
    file_init="./config/init_delta.csv"


outputfiles=[]
for i in range(5,len(sys.argv)):
    outputfiles=outputfiles+[sys.argv[i]]



#*****************************************************************************
# functions

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
            glfa.append(float(temp[1]))
            glia.append(float(temp[2]))
            glkgw.append(float(temp[3]))
            glfa_total.append(float(temp[1])*glnofgwcells)
            
            
    outletpar=np.zeros([glnofswcells,30])
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

    

 
def read_input(file_input,spinup):
    global glrecdate, glinflow, glprec, glpet, gltminmax, glnoftsteps,glstatratio

    print ("reading input data from: "+file_input)
    inputData=pd.read_csv(file_input, index_col=0, parse_dates=True)
    
    glrecdate=inputData.index.strftime("%Y-%m-%d")
    glinflow=inputData['Inflow-Mohembo'].values.astype("float")
    prec=inputData[['Rainfall-Maun', 'Rainfall-Shakawe']].values.astype("float")
    if inputData.shape[1]==4:
        glpet=inputData['PET-Maun'].values.astype("float")*0.85
    else:
        gltmin=inputData['MinTemperature-Maun'].values
        gltmax=inputData['MaxTemperature-Maun'].values
        evap_calc()
    glnoftsteps=inputData.shape[0]
    
    #calculating unit rainfall
    ratios=np.tile(np.array(glstatratio).reshape(-1,1),glnoftsteps).T
    glprec=prec[:,0].reshape(-1,1)*ratios+prec[:,1].reshape(-1,1)*(1-ratios)
    if spinup>0:
        #spinup in years
        nspinmon=12*spinup
        prepdates=pd.date_range(inputData.index[0]-DateOffset(months=nspinmon), freq="M", periods=nspinmon)
        prepdates=prepdates.union(inputData.index)
        glrecdate=prepdates.strftime("%Y-%m-%d")
        for i in range(spinup):
            glinflow=np.append(glinflow[0:12], glinflow, axis=0)
            glprec=np.append(glprec[0:12,:], glprec, axis=0)
            glpet=np.append(glpet[0:12], glpet, axis=0)
        glnoftsteps=glnoftsteps+nspinmon
    print (str(glnoftsteps) + " time steps read")



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
    
def timer():
    global t0
    _t=timeit.default_timer()
    print (_t-t0)
    t0=timeit.default_timer()



def eco_calc(_mode):
    print("calculating ecoregions...")
    global glalleco
    ecoregs=["Aquatic","Sedgeland", "Inundated grasslands", "Savanna"]
    glout_sa4eco=mergecells(glfin_sa,0)
    dates=glout_sa4eco.index
    fst=np.where(dates.month==1)[0][0]
    lst=np.where(dates.month==12)[0][-1]
    areayearpd=glout_sa4eco.iloc[fst:(lst+1),:].resample("A").mean()
    areamonthpd=glout_sa4eco.iloc[fst:(lst+1),:]
    if _mode=="total":
        areayearpd=pd.DataFrame(areayearpd.mean(1), columns=["Delta"])
        areamonthpd=pd.DataFrame(areamonthpd.mean(1), columns=["Delta"])
    nofyears=areayearpd.shape[0]
    nofunits=areayearpd.shape[1]
    i=0
    areayear=areayearpd.values
    areamonth=areamonthpd.values.reshape(nofyears,12,nofunits)
    
    for unit in range(areayear.shape[1]):
        i=i+1
        maxarea=int(np.ceil(areamonth[:,:,unit].max()))
        minarea=int(np.ceil(areamonth[:,:,unit].min()))
        ecoall=[]
        for size in range(minarea,maxarea):
            eco=np.zeros((nofyears,))
            eco[:]=2
            dur=(areamonth[:,:,unit]>size).sum(1)
            for y in range(1,nofyears):
                if eco[y-1]==1: #A
                    # rules for Aquatic
                    if dur[y] == 0:
                        eco[y] = 2 #RS
                    else:
                        if dur[y - 1] == 12:
                            eco[y] = 1 #"A"
                        elif dur[y - 2] == 12 and dur[y - 3] == 12 and dur[y - 4] == 12:
                            eco[y] == 1 #"A"
                        else:
                            eco[y] = 2 #"RS"
                elif eco[y-1]==2: #"RS"
                # rules for Sedges
                    if dur[y]== 0:
                        eco[y] = 3 #"G"
                    elif dur[y - 1] < 12:
                        eco[y] = 2  #"RS"
                    else:
                        eco[y]=1 #A
                elif eco[y-1]==3: #"G"
                # rules for Grassland
                    if dur[y]== 0:
                        if dur[y - 1]== 0:
                            if dur[y - 2] > 0 or dur[y - 3] > 0 or dur[y - 4] > 0:
                                eco[y] = 3 #"G"
                            else:
                                eco[y] = 4 #"S"
                        elif dur[y - 1] > 0:
                            eco[y] = 3 #"G"
                    elif dur[y] > 0:
                        if dur[y - 1]==0:
                            eco[y]== 3 #"G"
                        else:
                            if dur[y - 2]==0:
                                eco[y] = 3 #"G"
                            else:
                                eco[y] = 2 #"RS"

                elif eco[y-1]==4: #"S"
                    # rules for Savanna
                    if dur[y]== 0:
                        eco[y] = 4 #"S"
                    elif dur[y] > 1:
                        eco[y] = 3 #"G"
                    else:
                        eco[y] = 4 #"S"
            ecoall=ecoall+[eco]
        ecoall=np.array(ecoall)
        ecototal=np.zeros((nofyears,4))
        ecototal[:]=0
        for j in range(4):
            ecototal[:,j]=np.sum(ecoall==j+1, 0)
        ecototal=np.array(ecototal)
        ecototal[:,0]=ecototal[:,0]+minarea
        ecototal[:,-1]=maxarea-np.sum(ecototal[:,0:3],1)
        cols=[glout_sa4eco.keys()[unit]+"-"+x for x in ecoregs]
        temp=pd.DataFrame(ecototal,  index=areayearpd.index, columns=cols)
        if i==1:
            glalleco=temp.copy()
        else:
            glalleco=pd.concat([glalleco, temp], axis=1)
    print("done")


def eco_calc_2018(_mode):
    global glalleco
    ecoregs=["Perennially flooded community","Seasonal aquatic community","Seasonally flooded sedgeland","Seasonally flooded grassland", "Dry floodplain grasslands", "Savanna"]
    glout_sa4eco=mergecells(glfin_sa,0)
    dates=glout_sa4eco.index
    fst=np.where(dates.month==1)[0][0]
    lst=np.where(dates.month==12)[0][-1]
    areayearpd=glout_sa4eco.iloc[fst:(lst+1),:].resample("A").mean()
    areamonthpd=glout_sa4eco.iloc[fst:(lst+1),:]
    
    if _mode=="total":
        areayearpd=pd.DataFrame(areayearpd.mean(1), columns=["Delta"])
        areamonthpd=pd.DataFrame(areamonthpd.mean(1), columns=["Delta"])
    nofyears=areayearpd.shape[0]
    nofunits=areayearpd.shape[1]
    i=0
    areayear=areayearpd.values
    areamonth=areamonthpd.values.reshape(nofyears,12,nofunits)

    for unit in range(areayear.shape[1]):
        i=i+1
        maxarea=int(np.ceil(areamonth[:,:,unit].max()))
        minarea=int(np.ceil(areamonth[:,:,unit].min()))
        ecoall=[]
        for size in range(minarea,maxarea):
            eco=np.zeros((nofyears,))
            dury=(areamonth[:,:,unit]>size).sum(1)
            dur=np.copy(dury)
            for y in range(3,dury.shape[0]):
                dur[y]=dury[(y-3):y].mean()
            dur[0]=dury[0]
            dur[1]=dury[0:1].mean()

            
            eco[dur==12]=1 #PC
            eco[(dur>6.3) & (dur<12)]=2 #SFS
            eco[(dur>4.7) & (dur<=6.3)]=3 #SFS
            eco[(dur>2.8) & (dur<=4.7)]=4 #SFG
            eco[(dur>0) & (dur<=2.8)]=5 #DFG
            eco[dur==0]=6 #SAV
            
            ecoall=ecoall+[eco]
        ecoall=np.array(ecoall)
        ecototal=np.zeros((nofyears,6))
        ecototal[:]=0
        for j in range(6):
            ecototal[:,j]=np.sum(ecoall==j+1, 0)
        ecototal=np.array(ecototal)
        ecototal[:,0]=ecototal[:,0]+minarea
        ecototal[:,-1]=maxarea-np.sum(ecototal[:,0:5],1)
        if _mode=="dist":
            cols=[glout_sa4eco.keys()[unit]+"-"+x for x in ecoregs]
        else:
            cols=ecoregs            
        temp=pd.DataFrame(ecototal,  index=areayearpd.index, columns=cols)
        if i==1:
            glalleco=temp.copy()
        else:
            glalleco=pd.concat([glalleco, temp], axis=1)
    print("done")

def inund_calc(thresh):
    global glinundarr
    from netCDF4 import Dataset
    print("calculating inundation maps...")
    
    import scipy.stats as st
    mapdir="./config/"
    
    nrow,ncol = 300,303
    nofpix = ncol * nrow


    ncdata=Dataset(mapdir+"./m_arc.nc")
    m=ncdata.variables['Band1'][:]
    m[m<0]=1000

    ncdata=Dataset(mapdir+"./sigma_arc.nc")
    sigma=ncdata.variables['Band1'][:]

    ncdata=Dataset(mapdir+"./units_arc.nc")
    units=ncdata.variables['Band1'][:]
    units=units.astype("float")

    units[m<=0]=np.nan
    units[sigma<=0]=np.nan
    codes={1:"Panhandle", 2:"Thaoge", 3:"Xudum", 4:"Boro", 5:"Khwai", 6:"Nqoga", 7:"Selinda", 8:"Maunachira", 9:"Mboroga"}

    unitsf=units.flatten()
    mf=m.flatten()
    sigmaf=sigma.flatten()

    sa=mergecells(glfin_sa, 0) #all timesteps
    nts=sa.shape[0]
    glinundarr=np.zeros([nts,mf.shape[0]]).astype(np.uint8)
#    print(amap.shape)
    for key in codes.keys():
        area=sa[codes[key]]
        sel=np.where(unitsf==key)[0]
        for x in sel:
            prob=st.norm.cdf(area,mf[x],sigmaf[x])
#            print(sel.shape,prob.shape, area.shape, x, amap.shape)
            glinundarr[prob>thresh,x]=255
    glinundarr=glinundarr.reshape(nts,nrow,ncol)
    print("done")

def mergecells(glvar,skip):
    #write areas for each cell
    global gloutputflag, glswcellname, glrecdate
    selcells=glvar[:,np.array(gloutputflag)==1]
    cellnames=np.array(glswcellname)
#    print(cellnames)
    tooutput=np.array(gloutputflag)
    selcellnames=cellnames[tooutput==1]
    #0-Panh 1-Nqo1 2-Nqo2 3-Tha 4-Xud 5-Bor 6-Mch1 7-Mch2 8-Sel 9-Mbo 10-Khw 11-Tot 12-Maun 13-Mab 14-Gomoti
    selcellnames=['Panhandle','Nqoga','Thaoge','Xudum','Boro','Maunachira','Selinda','Mboroga','Khwai']
    merged=[[0],[1,2],[3],[4],[5],[6,7],[8],[9],[10]]
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




def write_botetiinput(file_output, file_input, skip):
    global glout_sqout,glpet

    temp=glout_sqout["Boro"].to_frame().values
    inputData=pd.read_csv(file_input, index_col=0, parse_dates=True)
    pr=inputData['Rainfall-Maun'].values.astype("float")
    pet=glpet[skip:]
    temp=np.append(temp,pr.reshape(-1,1), axis=1)
    temp=np.append(temp,pet.reshape(-1,1), axis=1)
    temp=pd.DataFrame(temp, index=inputData.index, columns=["Inflow-Maun","Rainfall-Maun","PET-Maun"])
    temp.astype(int).to_csv(file_output)

def write_output_cellinundation(file_output):
    global glout_sa
    print ("writing surface area output file...")
    glout_sa.astype(int).to_csv(file_output)

def write_output_totalinundation(file_output):
    global glout_sa
    temp=glout_sa.sum(1).to_frame()
    temp.columns=["Delta"]
    temp.astype(int).to_csv(file_output)

def write_output_cellvolume(file_output):
    global glout_sv
    print ("writing surface volume output file...")
    glout_sv.astype(int).to_csv(file_output)

def write_output_cellq(file_output):
    #write discharges for each cell
    global glout_sqout
    print ("writing discharge output file...")
    glout_sqout.astype(int).to_csv(file_output)

def write_output_ecoregions(file_output, skip):
    #write ecoregions for each cell
    global glalleco
    print ("writing ecoregions output file...")
    glalleco.iloc[skip:,].astype(int).to_csv(file_output)
    print ("done")


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
            

def write_output_inundanimation(outputfile, skip):
    print("writing animated inundation file...")
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.animation as animation
    from matplotlib import pyplot as plt

    global glinundarr
    fps=5
    fig, pl= plt.subplots(figsize=(5, 5))
    #preparing empty frame
    nts=glinundarr.shape[0]
    temp=np.zeros_like(glinundarr[0,:,:]).astype(float)
    temp[:]=0
    im = pl.imshow(temp, cmap=plt.cm.RdBu)
    
    dates=pd.date_range(glrecdate[0], freq="M", periods=len(glrecdate)).strftime("%b %Y") #entire period
    
    #preparing canvas
    pl.set_yticks([])
    pl.set_xticks([])
    tx=pl.text(0.7,0.9,dates[0], transform=pl.transAxes)
    
    def plotflood(ts):
        if ts%10==0:
            print ("ts="+str(ts))
        tx.set_text(dates[ts])
        frame=np.flipud(glinundarr[ts,:,:].astype(float))
        frame[frame==0]=np.nan
        im.set_array(frame)
        return im,

    ani = animation.FuncAnimation(fig, plotflood, range(skip,nts))
    writer = animation.ImageMagickFileWriter(fps=fps)
    ani.save(outputfile, writer=writer)




def write_output_floodmaps(outputfile, skip, how="one"):
    global glinundarr
    print("writing files with inundation data...")
    from PIL import Image
    import zipfile
    imlist=[]
    nts=glinundarr.shape[0]
    dates=pd.date_range(glrecdate[0], freq="M", periods=len(glrecdate)).strftime("%Y%m") #entire period
    for ts in range(skip,nts):
        im=np.flipud(glinundarr[ts,:,:]).astype(np.uint8)
        im=Image.fromarray(im)
        imlist.append(im)
    if how=="all":
        outfile=outputfile[:-9]
        zf = zipfile.ZipFile(outputfile, "w")
        for ts in range(skip,nts):
            outfilename=outfile+"-"+dates[ts]+".tif"
            imlist[ts-skip].save(outfilename, compression="tiff_deflate", save_all=True)
            zf.write(outfilename, os.path.basename(outfilename))
            os.remove(outfilename)
        zf.close()
    else:
        imlist[0].save(outputfile, compression="tiff_deflate", save_all=True, append_images=imlist[1:])



#*****************************************************************************

#model units
unitnames=["panhandle","nqoga1a","nqoga1b","thaoge","xudum","boro","nqoga2a","nqoga2b","selinda","mboroga","khwai"]



print ("Initializing inundaion model with the following:")
print ("parameters:",file_modpar)
print ("initialization:", file_init)
print ("input:",file_input)
print ("spinup:", spinup, "years")
print ("requested output files:", outputfiles)
print ("done")
print ()

#start timer
t0 = timeit.default_timer()


read_modset(file_modset)                                #reading model configuration
print ()
read_modpar(file_modpar)
print ()
read_input(file_input,spinup)                                  #reading inputs
print ()
read_init(file_init)                                    #reading initial conditions
print ()
timer()


print("calculating...")
if debug:
    print (glinflow.shape, glprec.shape, glpet.shape, glsv_init.shape, glfv_init.shape, gliv_init.shape, glunitpar.shape, glgwpar.shape)

#this is when the model is actually run
result=hcy.model_calc(glinflow, glprec, glpet, glsv_init, glfv_init, gliv_init, glunitpar, glgwpar)                         
timer()
print ("done")
print ()


print("preparing output...")
glfin_sqin, glfin_sa, glfin_sv, glfin_sev, glfin_spre, glfin_sqout,glfin_sinf,glfin_fv, glfin_fev,glfin_fpre,glfin_fgwout,glfin_finf,glfin_iv, glfin_iev,glfin_ipre=result


glout_sqin=mergecells(glfin_sqin,spinup*12)
glout_sa=mergecells(glfin_sa,spinup*12)
glout_sv=mergecells(glfin_sv,spinup*12)
glout_sqout=mergecells(glfin_sqout,spinup*12)
glout_sev=mergecells(glfin_sev,spinup*12)
glout_sinf=mergecells(glfin_sinf,spinup*12)

print("done")
print ()

# In[16]:


for outputfile in outputfiles:
    print()
    print(outputfile)
    if "allvolumes" in outputfile:
        write_output_cellvolume(outputfile)
    if "alloutflows" in outputfile:
        write_output_cellq(outputfile)
    if "allinundation" in outputfile:
        write_output_cellinundation(outputfile)
    if "totalinundation" in outputfile:
        write_output_totalinundation(outputfile)                       #total inundation
    if "totalecoregions" in outputfile:
        eco_calc("total") #returns all time steps
        write_output_ecoregions(outputfile, spinup)                       #ecoregions
    if "allecoregions" in outputfile:
        eco_calc("dist")
        write_output_ecoregions(outputfile, spinup)                       #ecoregions

    if "totalecoregions2018" in outputfile:
        eco_calc_2018("total") #returns all time steps
        write_output_ecoregions(outputfile, spinup)                       #ecoregions
    if "allecoregions2018" in outputfile:
        eco_calc_2018("dist")
        write_output_ecoregions(outputfile, spinup)                       #ecoregions

    if "animatedinundation" in outputfile:
        inund_calc(0.7) #returns all timesteps
        write_output_inundanimation(outputfile, spinup*12)                       #inundation movie
    if "inundationmaps-one" in outputfile:
        inund_calc(0.7)
        write_output_floodmaps(outputfile, spinup*12, "one")
    if "inundationmaps-all" in outputfile:
        inund_calc(0.7)
        write_output_floodmaps(outputfile, spinup*12, "all")
    if "finalcond" in outputfile:
        write_init(outputfile, -1)
    if "botetiinput" in outputfile:
        write_botetiinput(outputfile, file_input,spinup*12)


print ()
print("success")





