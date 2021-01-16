import numpy as np
cimport numpy as cnp
import sys

cdef cnp.ndarray _glfin_sqin = np.zeros([600,16], dtype=np.float)
cdef cnp.ndarray _glfin_sqout = np.zeros([600,16], dtype=np.float)
cdef cnp.ndarray _glfin_spre = np.zeros([600,16], dtype=np.float)
cdef cnp.ndarray _glfin_sev = np.zeros([600,16], dtype=np.float)
cdef cnp.ndarray _glfin_sinf = np.zeros([600,16], dtype=np.float)
cdef cnp.ndarray _glfin_sa = np.zeros([600,16], dtype=np.float)
cdef cnp.ndarray _glfin_sv = np.zeros([600,16], dtype=np.float)

cdef double[:,:] glfin_sqin=_glfin_sqin
cdef double[:,:] glfin_sqout=_glfin_sqout
cdef double[:,:] glfin_spre=_glfin_spre
cdef double[:,:] glfin_sev=_glfin_sev
cdef double[:,:] glfin_sinf=_glfin_sinf
cdef double[:,:] glfin_sa=_glfin_sa
cdef double[:,:] glfin_sv=_glfin_sv

cdef cnp.ndarray _glfin_fpre = np.zeros([600,16,5], dtype=np.float)
cdef cnp.ndarray _glfin_fev = np.zeros([600,16,5], dtype=np.float)
cdef cnp.ndarray _glfin_finf = np.zeros([600,16,5], dtype=np.float)
cdef cnp.ndarray _glfin_fgwout = np.zeros([600,16,5], dtype=np.float)
cdef cnp.ndarray _glfin_fv = np.zeros([600,16,5], dtype=np.float)

cdef double[:,:,:] glfin_fpre=_glfin_fpre
cdef double[:,:,:] glfin_fev=_glfin_fev
cdef double[:,:,:] glfin_finf=_glfin_finf
cdef double[:,:,:] glfin_fgwout=_glfin_fgwout
cdef double[:,:,:] glfin_fv=_glfin_fv

cdef cnp.ndarray _glfin_ipre = np.zeros([600,16,5], dtype=np.float)
cdef cnp.ndarray _glfin_iev = np.zeros([600,16,5], dtype=np.float)
cdef cnp.ndarray _glfin_iv = np.zeros([600,16,5], dtype=np.float)

cdef double[:,:,:] glfin_ipre=_glfin_ipre
cdef double[:,:,:] glfin_iev=_glfin_iev
cdef double[:,:,:] glfin_iv=_glfin_iv

cdef cnp.ndarray _glfa_frac_start = np.zeros([16,5], dtype=np.float)
cdef cnp.ndarray _glfa_frac_finish = np.zeros([16,5], dtype=np.float)
cdef cnp.ndarray _glfa_frac_avg = np.zeros([5,], dtype=np.float)

cdef double[:,:] glfa_frac_start=_glfa_frac_start
cdef double[:,:] glfa_frac_finish=_glfa_frac_finish
cdef double[:] glfa_frac_avg=_glfa_frac_avg


cdef cnp.ndarray _glprecip = np.zeros([600,16], dtype=np.float)
cdef cnp.ndarray _glpet = np.zeros([600,], dtype=np.float)

cdef double[:,:] glprecip=_glprecip
cdef double[:] glpet=_glpet

cdef Py_ssize_t nsu=16
cdef Py_ssize_t ngw=5
cdef Py_ssize_t nts
cdef Py_ssize_t n
cdef Py_ssize_t ts, sur, gw, isl, delayindex
cdef float glconvcrit=0.001
cdef int glmaxiter=100

cdef cnp.ndarray _gldelay = np.zeros([16,], dtype=np.float)
cdef cnp.ndarray _gltopopar = np.zeros([16,2], dtype=np.float)
cdef cnp.ndarray _glspar = np.zeros([16,30], dtype=np.float)
cdef cnp.ndarray _glsv_init = np.zeros([16,], dtype=np.float)
cdef cnp.ndarray _glfv_init = np.zeros([16,5], dtype=np.float)
cdef cnp.ndarray _gliv_init = np.zeros([16,5], dtype=np.float)
cdef cnp.ndarray _glfa = np.zeros([16,], dtype=np.float)
cdef cnp.ndarray _glia = np.zeros([16,], dtype=np.float)
cdef cnp.ndarray _glkgw = np.zeros([16,], dtype=np.float)

cdef double[:] gldelay=_gldelay
cdef double[:,:] gltopopar=_gltopopar
cdef double[:,:] glspar=_glspar
cdef double[:] glsv_init=_glsv_init
cdef double[:,:] glfv_init=_glfv_init
cdef double[:,:] gliv_init=_gliv_init
cdef double[:] glfa=_glfa
cdef double[:] glia=_glia
cdef double[:] glkgw=_glkgw

# for surf iteration
cdef cnp.ndarray _celloutflows = np.zeros([10], dtype=np.float)
cdef cnp.ndarray _fa_frac = np.zeros([5,], dtype=np.float)
cdef double[:] celloutflows=_celloutflows
cdef double[:] fa_frac=_fa_frac

cdef float glrain, glsa_beg, glsa_end, glipv, gliev, glfev, glfpv, glfdet, glidet, glfpor, \
glipor, glfq, gliv_end, glsinf
cdef int glsv_isincr

cdef int iitern, iiter_flag
cdef float iv_endmin, iv_endmax, evapi, iv_endc

cdef float sqin, sv_beg, sv_end, sv_av, sv_endmin, sv_endmax, sa_av, spre, sev, sv_endc
cdef int sitern, siter_flag, cellno
cdef float fa_cum, fa_incrfrac, fa_cumprev
cdef int fiter_flag, fitern
cdef float fv_endmin, fv_endmax
cdef int debug, dts, last


#***************************************************************************
def model_calc(double[:] _inflow, double[:,:] _precip, double[:] _pet, double[:] _glsv_init, double[:,:] _glfv_init, double[:,:] _gliv_init, double[:,:] _unitpar, double[:] _gwpar):
    global glfin_sqin, glfin_sqout, glfin_spre, glfin_sev, glfin_sinf, glfin_fpre, glfin_finf, glfin_fev
    global glfin_fgwout,glfin_ipre,glfin_iev,glfin_sa,glfin_sv,glfin_fv, glfin_iv, glfdet, glfpor, glidet, glipor
    global glfa_frac_start, glfa_frac_finish, glfa_frac_avg
    global nsu, ngw, nts, ts, sur, flo, isl
    global celloutflows, debug
    print ("running model..")
    #adjusting dimensions
    nts=_inflow[:].shape[0]    
    debug=0
    dts=-1

    #populating forcing variables
    glfin_sqin[:]=0
    glfin_sqin[0:nts,0]=_inflow                              #inflow
    glprecip[0:nts,:]=_precip
    glpet[0:nts]=_pet

    glsv_init[0:nts]=_glsv_init
    glfv_init[0:nts,:]=_glfv_init
    gliv_init[0:nts,:]=_gliv_init

    #other parameters
    gldelay[:]=_unitpar[:,0]
    gltopopar[:,:]=_unitpar[:,2:4]
    glfa[:]=_unitpar[:,4]
    glia[:]=_unitpar[:,5]
    glkgw[:]=_unitpar[:,6]
    
    glspar[:,:]=_unitpar[:,7:37]

    glfdet,glfpor,glidet,glipor=_gwpar
    #iterate through time steps
    if dts<0:
        last=nts
    else:
        last=dts
    
    for ts in np.arange(0,last):
        if ts%10==0:
            print ("ts="+str(ts))
        #itera\te through model cells
        for sur in range(nsu):
            calc_surface_iter()
#            if debug and ts==dts:
#                print("done", ts, nts, sur, nsu)

    cdef list results
    results=[_glfin_sqin[0:nts,:],_glfin_sa[0:nts,:], _glfin_sv[0:nts,:], _glfin_sev[0:nts,:],\
             _glfin_spre[0:nts,:],_glfin_sqout[0:nts,:], _glfin_sinf[0:nts,:],\
             _glfin_fv[0:nts,:], _glfin_fev[0:nts,:],_glfin_fpre[0:nts,:], _glfin_fgwout[0:nts,:],\
             _glfin_finf[0:nts,:,:],\
             _glfin_iv[0:nts,:], _glfin_iev[0:nts,:],_glfin_ipre[0:nts,:]]
    
    return results
    

    
#***************************************************************************    
cdef calc_surface_iter():
    global ts, sur
    global glprecip, gldelay, glrainfrac, glrain, gltopopar, glspar, glfa
    global glfa_frac_start, glfa_frac_finish, glfa_frac_avg
    global glsv_init, glsinf, glfin_sa
    global nsu, ngw, nts, n, delayindex
    global glsv_isincr, glsa_end, glsa_beg
    global sqin, sv_beg, sv_end, sv_av, sv_endmin, sv_endmax, sa_av, spre, sev, sv_endc
    global sitern, siter_flag, cellno, debug
    
    # this calculates surface reservoir
    # global variables: gldelay, glfin_sqin, glsv_init, glfin_sv, glV, glk
    # local variables: sqin, celloutflows, sv_av, sa_av, spre, sev, sqout
    # sv_beg, sv_end, glsa_end, glsa_beg, glsinf
    
    
    # reset outlets outflow
    celloutflows[:]=0
    
    # rain 
    glrain= glprecip[ts,sur] # in mm

    # delay
    #Panhandle 1 Nqoga-1a 0 Nqoga-1b 0 Thaoge 0 Xudum 1 Boro 1 Nqoga-2a 0 Nqoga-2b 0
    #Selinda 0 Empty 0 Toteng 0 Maun 0 Shashe 0 Mboroga 1 Khwai 1 out 0
    delayindex=(max(0, ts - int(gldelay[sur])))
    sqin = glfin_sqin[delayindex,sur]    #this delay makes sense

    #initial condition
    if ts==0:
        sv_beg = glsv_init[sur]
    else:
        sv_beg = glfin_sv[ts-1,sur]
        
    #first guess of end of time step volume
    sv_end = sv_beg + 0.5 * sqin 
    
    #iteration parameters
    sitern = 0
    sv_endmin = 0
    sv_endmax = -999
    siter_flag=1
    
    #iterate
    while siter_flag:
        sv_av = (sv_end + sv_beg) / 2
        glsa_beg = (gltopopar[sur,0] * sv_beg)**gltopopar[sur,1]
        glsa_end = (gltopopar[sur,0] * sv_end)**gltopopar[sur,1]
        #check if flood is increasing in the sw cell
        if sv_end > sv_beg:
            glsv_isincr = 1
        else:
            glsv_isincr = 0

        #############################################################################################
        # special rules
        #Panhandle 0 Nqoga-1a 1 Nqoga-1b 2 Thaoge 3 Xudum 4 Boro 5 Nqoga-2a 6 Nqoga-2b 7
        #Selinda 8 Empty 9 Toteng 10 Maun 11 Shashe 12 Mboroga 13 Khwai 14 out 15

        #change shape of volume-area curve
        if sur==0:
            #Panhandle
            #Case 1
            if sv_beg < 1500:
                glsa_beg = (0.006 * sv_beg)**3

            if sv_end < 1500:
                glsa_end = (0.006 * sv_end)**3

        #constrain the extent of inundation
        elif sur==1 or sur==6 or sur==5 or sur==13 or sur==14:  
            #Case 2, 7, 6, 14, 15
            if glsa_beg > glfa[sur]*ngw:
                glsa_beg = glfa[sur]*ngw
        
            if glsa_end > glfa[sur]*ngw:
                glsa_end = glfa[sur]*ngw
        
        #############################################################################################
        
        sa_av = (glsa_beg + glsa_end) / 2
        spre = glrain * sa_av / 1000
    
    
        #############################################################################################
        # this delay does not make sense
        # and this was a bug... it was ==0
#        if ts - gldelay[sur] < 0:
        sev = glpet[ts] * sa_av / 1000
#        else:
#            sev = glpet[ts - int(gldelay[sur])] * sa_av / 1000
#            sev = kc(Month(inp(ts - delay(scell)).recdate)) * inp(ts - delay(scell)).evap * sa_av / 1000
        #############################################################################################


        #-------------------------------------------------------------------------
        # calculate surface outflows
        for n in range(10):
            if sv_av > glspar[sur,n+10]:
                celloutflows[n] = glspar[sur,n] * (sv_av - glspar[sur,n+10])
            else:
                celloutflows[n] = 0                
        sqout=_celloutflows.sum()
        #calculate groundwater outflow
        glsinf=0
#        if debug==1 and ts==dts:
#            print("sw-0", sv_beg, spre, sev, sqout, sqin, glsinf)
            
        calc_gw_iter()
#        print("check", sv_beg, spre, sev, sqout, sqin, glsinf)

        #calculate end water balance
        sv_endc = sv_beg + spre - sev - sqout + sqin - glsinf
    
        #-------------------------------------------------------------------------
        #check if convergence is achieved
        if abs(sv_endc - sv_end) < glconvcrit * sv_end:
            siter_flag = 0
        elif sv_end < 0.001:
            #unit dries
            sv_end = 0
            siter_flag = 0
        else:
            if sv_end > sv_endc:
                sv_endmax = sv_end
            else:
                sv_endmin = sv_end
        
            if sv_endmax==-999:
                sv_end = sv_endc
            else:
                sv_end = sv_endmin + 0.5 * (sv_endmax - sv_endmin)
        
        #-------------------------------------------------------------------------
        #advance iteration
    
        sitern = sitern + 1
                
        if sitern > glmaxiter:
            print (str(glmaxiter) + " s iterations in cell " + str(sur) + " in " + str(ts))
            siter_flag=0
#    print "check"
    #saving end of time stp variables
    glfin_spre[ts,sur] = spre
    glfin_sqout[ts,sur] = sqout
    glfin_sa[ts,sur] = glsa_end
    glfin_sv[ts,sur] = sv_end
    glfin_sev[ts,sur] = sev
    glfin_sinf[ts,sur] = glsinf
                       
    glfa_frac_start[sur,:] = glfa_frac_finish[sur,:]
    
        
    #get inflows to the downstream cells
    for n in range(10):
        cellno=int(glspar[sur,n+20])
        if cellno>0:
            glfin_sqin[ts,cellno] = glfin_sqin[ts,cellno] + celloutflows[n]
        
#    print("end surface")

#    if debug==1:
#        print "\t sitern:",sitern

#*****************************************************************************
cdef calc_gw_iter():
    
    global glsa_end, glsa_beg, glfv_beg, gliv_beg, glfv_end, glfpv, glfev, flpv, gliev, gliv_end, glsinf
    global ngw, fa_frac, gw, glfv_init, glfq
    global fa_cum, fa_incrfrac, fa_cumprev, debug
    # this calculates a coupled groundwater reservoir, but here, only infitration phase, gw flow is calculated within iteration_1 and 2
    # prepare data
    #-----------------------------------------------------------------------------
    #get initial values of variables
    fa_cum=0
    fa_incrfrac=0
    fa_cumprev=0
    glsinf = 0

    #-----------------------------------------------------------------------------
    #-----------------------------------------------------------------------------
    # calculate status of gwcells flooding at the end of the time step
    # this is done for calculating rapid infiltration  
    fa_frac[:]=0 #it is fraction of cell flooded at the end of the timestep
    
    for gw in range(ngw):
        fa_cumprev = fa_cum #it's ok, because on the first cell fa_cum is 0
        fa_cum = fa_cum + glfa[sur]
        if fa_cum <= glsa_end:
            #cell entirely flooded
            fa_frac[gw] = 1
        elif fa_cum > glsa_end and fa_cumprev <= glsa_end:
            #cell partially flooded
            fa_frac[gw] = (glsa_end - fa_cumprev) / glfa[sur]
            if glsa_beg > fa_cumprev and glsa_end > glsa_beg:
                #if cell partially flooded previously
                 fa_incrfrac = (glsa_end - glsa_beg) / (fa_cum - glsa_beg) #this is ok, because incrfac is fraction of the part that is not flooded yet
            else:
                #if cell not flooded previously
                fa_incrfrac = fa_frac[gw]
        else:
            #cell not flooded
            fa_frac[gw] = 0
        #this is correct fraction ONLY if there is no expansion of flood
        glfa_frac_avg[gw] = (fa_frac[gw] + glfa_frac_start[sur, gw]) / 2 
        glfa_frac_finish[sur,gw] = fa_frac[gw]

    #*****************************************************************************
    #calculate groundwater flow between floodplains and islands
    for gw in range(ngw):
        glfv_max = glidet * glfpor * glfa[sur] 
       #-----------------------------------------------------------------------------
#        if debug:
#            print "\tgwcell",gwcell
        if ts==0:
            glfv_beg=glfv_init[sur,gw]
        else:
            glfv_beg=glfin_fv[ts-1,sur,gw]
            
#        if debug==1 and ts==dts:
#            print("gw",glfv_beg,glfv_max,_glfa_frac_avg, glfa[sur], glfq)
            
        iteration_1()
        
        
        #if not flooded it will be 0, if flooded all the time it will be 1
        siv_adv = glfa_frac_avg[gw] * glfq
        
        siv_front = ((glidet * glfpor * glfa[sur]) - glfv_end) * fa_incrfrac
        
        #-----------------------------------------------------------------------------
        #sets initial values for the next time step
        glfv_end=glfv_end+siv_front
    
    
    
        #-----------------------------------------------------------------------------
        #calculates composite fluxes
        finf=siv_front + siv_adv
        glsinf = glsinf + finf              #sw cell infiltration
        glfin_fgwout[ts,sur,gw]=glfq
        glfin_fpre[ts,sur,gw]=glfpv
        glfin_finf[ts,sur,gw]=finf
        glfin_fev[ts,sur,gw]=glfev
        glfin_fv[ts,sur,gw] = glfv_end
        
        glfin_iev[ts,sur,gw]=gliev
        glfin_ipre[ts,sur,gw]=glipv
        glfin_iv[ts,sur,gw] = gliv_end
        

cdef iteration_1():
    global glrain, glfv_av, glfv_end, glfpv, glfev, glfa, glfq
    global sur, gw, t, glconvcrit, glmaxiter, ngw
    global fiter_flag, fitern, fv_endmin, fv_endmax, debug
    
    # this calculates the floodplain groundwater reservoir
    #**********************************************************************************
    #prepare data
    
    fiter_flag = 1
    fitern = 0
    fv_endmin = 0
    fv_endmax = -999
    
    glfv_end = glfv_beg       #initial guess of end floodplain groundwater volume
    #**********************************************************************************
    #outer iteration start
    while fiter_flag:
        glfv_av = (glfv_end + glfv_beg) / 2
        glfev = 0
        if glfv_av > ((glidet - glfdet) * glfa[sur] * glfpor):
            #if average volume greater than something???
            temp = ((glfv_av - ((glidet - glfdet) * glfa[sur] * glfpor)) / (glfdet * glfa[sur] * glfpor)) * (1 - glfa_frac_avg[gw])
            if temp > 1:
                temp = 1
            glfev = (glpet[ts] / 1000 * glfa[sur] * temp)
            
#            glfpv = (glrain / 1000 * glfa[scell]) * (1 - glfa_frac_avg[gwcell])    
        glfpv = (glrain / 1000 * glfa[sur]) * (1 - glfa_frac_avg[gw])
    
#        if debug==1 and ts==dts:
#            print("i1-0",glfv_beg, glfv_end,glfv_av,glfpv,glfev,glfq,glfa_frac_avg[gw])

        iteration_2()
#        if debug==1 and ts==dts:
#            print("i1-1",glfv_beg, glfv_end,glfv_av,glfpv,glfev,glfq,glfa_frac_avg[gw])
        

        fv_endc = glfv_beg + glfpv - glfq - glfev+ glfa_frac_avg[gw]*glfq
        #-----------------------------------------------------------------------------
        #check if outer iteration convergence is achieved
        if abs(fv_endc - glfv_end) < (glconvcrit * glfv_end):
            fiter_flag = 0
        elif glfv_end < 0.001:
            fiter_flag = 0
        else:
            if glfv_end > fv_endc:
                fv_endmax = glfv_end
            else:
                fv_endmin = glfv_end

            #----------------------------------------------------
            if fv_endmax==-999:
                glfv_end = fv_endc
            else:
                glfv_end = fv_endmin + 0.5 * (fv_endmax - fv_endmin)

    #-----------------------------------------------------------------------------
    #advance the iteration
        fitern = fitern + 1
        if fitern > glmaxiter:
            print (str(glmaxiter) + " f iterations in scell " + str(sur) + ", gwcell"+str(gw)+" in " + str(ts))
            fiter_flag=0

#    if debug==1:
#        print "\t\t fitern:",fitern



cdef iteration_2():
    global glfv_av, glfin_iv, gliv_init, glidif, glfq, gliev, glipv, gliv_end, glipor, glidet, glfpor, glfdet
    global sur, gw, t, glconvcrit, glmaxiter, ngw
    global iitern,iiter_flag,iv_endmin,iv_endmax,evapi, iv_endc, debug
    #
    #uses: glfv_av
    #
    
    # this calculates the island groundwater reservoir
    #*********************************************************************************
    #prepare data
    iitern = 0
    iiter_flag = 1
    iv_endmin = 0
    iv_endmax = -999
    #-----------------------------------------------------------------------------
    #initial guess of end island volume
    if ts==0:
        iv_beg=gliv_init[sur,gw]
    else:
        iv_beg = glfin_iv[ts-1, sur, gw]
    gliv_end = iv_beg
    #**********************************************************************************
    #inner iteration start
    while iiter_flag: 
        iv_av = (gliv_end + iv_beg) / 2
        glfq = ((glfv_av / (glfa[sur] * glfpor)) - (iv_av / ((glia[sur]) * glipor))) * glkgw[sur]
        evapi = iv_av / (glipor * glidet * glia[sur])    
        if evapi > 0.6:
            evapi = 0.6
        gliev = glpet[ts]  / 1000 * (glia[sur]) * evapi
        glipv = glrain / 1000 * glia[sur]
        

        iv_endc = iv_beg + glfq - gliev + glipv
        
        if debug and ts==dts:
            print "iter2", iv_beg, iv_av, glfq, gliev, glipv, evapi, glfv_av,iv_endmax, iv_endmin
    
        #-----------------------------------------------------------------------------
        #check if inner iteration convergence is achieved
        
        if abs(iv_endc - gliv_end) < glconvcrit * gliv_end:
            iiter_flag = 0
#            if debug:
#                print "\t\t\tcase 1", glconvcrit, iv_endc - gliv_end,  glconvcrit * gliv_end
        elif gliv_end < glconvcrit:
            iiter_flag = 0
#            if debug:
#                print "\t\t\tcase 2", gliv_end
        else:
#            if debug:
#                print "\t\t\tcase 3", iv_endc - gliv_end,  glconvcrit * gliv_end
            if gliv_end > iv_endc:
                iv_endmax = np.copy(gliv_end)
            else:
                iv_endmin = gliv_end

            if iv_endmax==-999:
                gliv_end = iv_endc
            else:
                gliv_end = iv_endmin + 0.5 * (iv_endmax - iv_endmin)
#        if debug==1 and ts==dts:
#            print "iter2-2", iv_endc, gliv_end, iv_endmax, iv_endmin

        #-----------------------------------------------------------------------------
        #advance the iteration
        iitern = iitern + 1
        if iitern > glmaxiter:
            print (str(glmaxiter) + " i iterations in scell " + str(sur) + ", gwcell"+str(gw)+" in " + str(ts))
            iiter_flag=0
    
#    if debug==1:
#        print "\t\t\t i_iter2:",iitern


