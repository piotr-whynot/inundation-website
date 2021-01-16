import sys
import numpy as np
import datetime
import pandas as pd
#from pandas.plotting import register_matplotlib_converters
#register_matplotlib_converters()
#from netCDF4 import Dataset
#import timeit
#from matplotlib import pyplot as plt
import pyximport; pyximport.install()
import hydro_model_cython as hcy

#*****************************************************************************
#definition of paramater and input files 
    
file_modset = "./config/modset.dat"


file_modpar = sys.argv[1] 
file_init = sys.argv[2] 
file_input = sys.argv[3] 
spinup = sys.argv[4]

if file_modpar=="default":
    file_modpar = "./config/modpar.dat"
if file_init=="default":
    file_init="./config/init.dat"


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

#*****************************************************************************
   

 
def read_input(file_input):
    global glrecdate, glinflow, glprec, glpet, gltminmax, glnoftsteps,glstatratio

    print ("reading input data from: "+file_input)
    inputData=pd.read_csv(file_input, index_col=0, parse_dates=True)
    
    glrecdate=inputData.index.strftime("%Y-%m-%d")
    glinflow=inputData['Inflow-Mohembo'].values
    prec=inputData[['Rainfall-Maun', 'Rainfall-Shakawe']].values
    if inputData.shape[1]==4:
        glpet=inputData['PET-Maun'].values
    else:
        gltmin=inputData['MinTemperature-Maun'].values
        gltmax=inputData['MaxTemperature-Maun'].values
        evap_calc()
    glnoftsteps=inputData.shape[0]
    
    #calculating unit rainfall
    ratios=np.tile(np.array(glstatratio).reshape(-1,1),glnoftsteps).T
    glprec=prec[:,0].reshape(-1,1)*ratios+prec[:,1].reshape(-1,1)*(1-ratios)

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
    glsv_init=temp[:,1].astype(float)
        
    #initial storage of groundwater cells
    temp=data[glnofswcells:(glnofswcells*2)]
    temp=np.array([x.strip().split(",") for x in temp])
    glfv_init=temp[:,1:].astype(float)
    
    temp=data[(glnofswcells*2):(glnofswcells*3)]
    temp=np.array([x.strip().split(",") for x in temp])
    gliv_init=temp[:,1:].astype(float)
    
    print("done")


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
            
            
    outletpar=np.zeros([16,30])
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
    glunitpar=np.append(glunitpar, outletpar, axis=1)

    glgwpar=np.array([fdet,fpor,idet,ipor])
    print ("done")

    
    
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
    glout_sa.sum(0).astype(int).to_csv(file_output)
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


def mergecells(glvar):
    #write areas for each cell
    global gloutputflag, glswcellname, glrecdate
    selcells=glvar[:,np.array(gloutputflag)==1]
    cellnames=np.array(glswcellname)
    tooutput=np.array(gloutputflag)
    selcellnames=cellnames[tooutput==1]
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
    outputFrame=pd.DataFrame(np.array(outputtable).T, index=pd.to_datetime(glrecdate), columns=outputcellnames)    
    return outputFrame


def write_init(output_file, _ts):
    global glnofswcells, glfin_sv, glfin_fv, glfin_iv
    with open(output_file, "w") as outf:
        for scell in range(glnofswcells):
            outf.write("s_"+str(scell)+","+str(int(glfin_sv[scell,_ts]))+"\n")
        for scell in range(glnofswcells):
            line="f_"+str(scell)+","+",".join([str(np.round(x,2)) for x in glfin_fv[scell,:,_ts].tolist()])
            outf.write(line+"\n")
        for scell in range(glnofswcells):
            line="i_"+str(scell)+","+",".join([str(np.round(x,2)) for x in glfin_iv[scell,:,_ts].tolist()])
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
#    print (finputs.shape, foutputs.shape, fvdelta.shape)
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



def eco_calc():
    print("calculating eco model... ")
    size=[]
    nofyears=int(np.floor(gl.noftsteps)/12)
    nmonths=nofyears*12
    cellnames,celldata=mergecells(gl.fin_sa_end)

    dates=pd.to_datetime(gl.recdate)
    firstmonth=dates[0].month
    print(firstmonth)
    first2read=(12-firstmonth+1)%12
    gl.firstyear=dates[first2read].year
    print("input file has "+str(len(dates))+" monthly time and "+str(celldata.shape[1])+" units")
    print("January at timestep "+str(first2read))

    floodsize=np.sum(celldata[(first2read):],0)
    temp=np.copy(floodsize[0:nmonths])
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



def inund_calc(outputfile):
    print("Animating inundation...\n")
    import struct
    import numpy as np
    import PIL
    import sys
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib import pyplot as plt
    import scipy.stats as st
    import matplotlib.animation as animation

    fps=5

    mapdir="./config/"
    nrow,ncol = 300,303
    nofpix = ncol * nrow

    skip=3
    thresh=0.7

    print("reading inundation map parameters...")

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

    codes={1:"Panhandle", 2:"Thaoge", 3:"Xudum", 4:"Boro", 5:"Khwai", 6:"Nqoga-1a", 7:"Selinda", 8:"Nqoga-2a", 9:"Mboroga"}

    unitsf=units.flatten()
    mf=m.flatten()
    sigmaf=sigma.flatten()

    print("done\n")


    cellnames,cellvalues=mergecells(gl.fin_sa_end)
    dates=pd.to_datetime(gl.recdate)
    
    sa=pd.DataFrame(cellvalues.T,index=dates, columns=cellnames)

    nts=sa.shape[0]

    print("read", nts, "time steps")
    print("will skip", skip, "time steps")

    print("done\n")


    print("processing...")

    fig, pl= plt.subplots(figsize=(5, 5))

    #preparing empty frame
    temp=np.zeros_like(units).astype(float)
    temp[:]=0
    im = pl.imshow(temp, cmap=plt.cm.RdBu)

    #plt.show()

    #preparing canvas
    pl.set_yticks([])
    pl.set_xticks([])
    tx=pl.text(0.7,0.9,sa.index.strftime('%Y %B')[0], transform=pl.transAxes)


    def plotflood(ts): 
        if ts%10==0:
            print ("ts="+str(ts))
        inu=sa.iloc[ts,:]
        amap=np.zeros_like(mf).astype(float)
        amap[:]=np.nan
        for key in codes.keys():
            area=inu[codes[key]]
            sel=np.where(unitsf==key)[0]
            for x in sel:
                prob=st.norm.cdf(area,mf[x],sigmaf[x])
                if thresh>0:
                    if prob>thresh:
                        amap[x]=1
                else:
                        amap[x]=prob
        amap=np.flipud(amap.reshape(nrow,ncol))
        tx.set_text(sa.index.strftime('%Y %B')[ts])
        im.set_array(amap)
        return im,


    ani = animation.FuncAnimation(fig, plotflood, range(skip,nts))
    writer = animation.ImageMagickFileWriter(fps=fps)
    ani.save(outputfile, writer=writer) 
    print ("done")






print ("parameters",file_modpar)
print ("initialization", file_init)
print ("input",file_input)
print ("spinup", spinup)
print ("output", outputfiles)

#t0 = timeit.default_timer()

read_modset(file_modset)                                #reading model configuration
read_modpar(file_modpar)                                #reading model parameters
read_input(file_input)                                  #reading inputs
read_init(file_init)                                    #reading initial conditions




result=hcy.model_calc(glinflow, glprec, glpet, glsv_init, glfv_init, gliv_init, glunitpar, glgwpar)                                            #this is when the model is actually run

glfin_sqin, glfin_sa, glfin_sv, glfin_sev, glfin_spre, glfin_sqout,glfin_sinf,\
glfin_fv, glfin_fev,glfin_fpre,glfin_fgwout,glfin_finf,\
glfin_iv, glfin_iev,glfin_ipre=result



glout_sa=mergecells(glfin_sa)
glout_sv=mergecells(glfin_sv)
glout_sqout=mergecells(glfin_sqout)
glout_sev=mergecells(glfin_sev)
glout_sinf=mergecells(glfin_sinf)


for outputfile in outputfiles:
    if "allinundation" in outputfile:
        write_output_cellinundation(outputfile)                     #inundation by unit
    if "alloutflows" in outputfile:
        write_output_cellq(outputfile)                       #streamflow/unit discharges
    if "totalinundation" in outputfile:
        write_output_totalinundation(outputfile)                       #total inundation
    if "totalecoregions" in outputfile:
        eco_calc()
        write_output_totalecoregions(outputfile)                       #ecoregions
    if "animatedinundation" in outputfile:
        inund_calc(outputfile)
#        write_output_animatedinundation(outputfile)                       #inundation movie

print("success")

