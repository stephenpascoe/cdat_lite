from cdms import MV
import cdms,cdtime,string,types,MA,Numeric,sys

def centroid(msk,bounds,coords=None):
    ''' Computes the centroid of a bunch of point
    Authors: Charles Doutriaux/Karl Taylor
    Date: April 2001
    Input:
      s: a slab
      bounds : the bounds of the overall thing      
      coords : the coordinate spanned by each subset
    Output:
      centroid: a slab representing the centroid, values are between 0 (data evenly distributed evenly across the center) and +/-1 (data not evenly distributed)
      centroid is 1D less than s
      '''
    # determine the length,spread, shape and mean
    sh=msk.shape
    mean=float(bounds[1]+bounds[0])/2.
    if coords is None:
        coords=msk.getAxis(0).getBounds() # if MV then gets the bounds from there
    n=len(coords)
    mask=msk.mask()
    if mask is None:
        msk=Numeric.zeros(msk.shape,Numeric.Float)
    else:
        msk=mask.astype(Numeric.Float)
    sw=0.
    for i in range(n):
        w=float(coords[i][1]-coords[i][0]) # width
        sw=sw+w*(1.-msk[i])
        c=float(coords[i][0]+coords[i][1])/2.-mean # location
        w=w*c/float(bounds[1]-bounds[0]) # factor to multiply by plus normalization
        msk[i]=(1.-msk[i])*w
    msk=MA.sum(msk) # sums it
    sw=sw/2.
    msk=msk/sw
    return msk
    
def cyclicalcentroid(s,bounds,coords=None):
    '''
    returns the centroid, but this assumes cyclical axis, therefore spread the points around a circle, before computing the centroid
    Usage:
      cyclecentroid=cyclicalcentroid(s,bounds)
    Input:
      s: a slab
      bounds : the bounds of the overall thing      
      coords : the coordinate spanned by each subset
    Output:
      cyclecentroid : slab is same shape than s but without the 1st dim
    '''
    if coords is None:
        coords=s.getAxis(0).getBounds() # if MV then gets the bounds from there
    n=len(coords)
    length=float(bounds[1]-bounds[0])
    nax=Numeric.zeros((n,2),Numeric.Float)
    for i in range(n):
        nax[i][0]=coords[i][0]/length*2.*Numeric.pi
        nax[i][1]=coords[i][1]/length*2.*Numeric.pi
    # Places the point evenly around the axis
    # Compute the centroid on x and y
    xc=centroid(s,[0,2.*Numeric.pi],Numeric.cos(nax))
    yc=centroid(s,[0,2.*Numeric.pi],Numeric.sin(nax))
    # compute the new centroid
    return Numeric.sqrt(xc*xc+yc*yc)/Numeric.sqrt(2.)

def getMonthString(my_list):
    '''Given a list of month creates the string representing the sequence'''
    if not type(my_list) in [types.ListType,types.TupleType]:
        my_list=[my_list]
    dic = {
        1:'JANUARY',2:'FEBRUARY',3:'MARCH',
        4:'APRIL',5:'MAY',6:'JUNE',
        7:'JULY',8:'AUGUST',9:'SEPTEMBER',
        10:'OCTOBER',11:'NOVEMBER',12:'DECEMBER'}
    out=[]
    for i in my_list:
        out.append(dic[i][0])
    if len(out)==1: out=[dic[my_list[0]]]
    return string.join(out,'')
    
def getMonthIndex(my_str):
   """
   Given a string representing a month or a season (common abrev)
   Returns the ordered indices of the month
   Author: Krishna Achutarao
   Date: April 2001
   """
   my_str = string.upper(my_str)
   mon_list = ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY',
               'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER']
   if my_str in mon_list:
       return [mon_list.index(my_str)+1]
   # end of if string.upper(my_str) in yr_arr:
   #
   for mon in mon_list:
       if string.find(mon,  my_str) != -1:
           return [mon_list.index(mon)+1]
       # end of if string.find(mon,  my_str) != -1:
   # end of for mon in mon_list:
   yr = 'JFMAMJJASOND'
   yrs = yr+yr[:6]
   #
   result = string.find(yrs, my_str)
   if result == -1: return []
   month =  result + 1
   lis = range(month, month+len(my_str))
   for i in range(len(lis)):
       if lis[i] > 12: lis[i] -= 12
   return lis


def isMonthly(s):
    '''This function test if the data are monthly data from the time axis'''
    tim=s.getTime()
    units=tim.units
    monthly=1
    for i in range(len(tim)-1):
      month1=cdtime.reltime(tim[i],units).torel('months since 2000').value
      month2=cdtime.reltime(tim[i+1],units).torel('months since 2000').value
      if month2-month1!=1 : monthly=0
    return monthly


def mergeTime(ds,statusbar=1):
    '''
    Merge chronologically a bunch of slab
    Version 1.0
    Author: Charles Doutriaux, doutriaux1@llnl.gov
    Usage:
    mymerged=mergeTime(ds)
    where:
    ds is a list or an array of slabs to merge, each slab MUST be in chronological order
    Output:
    a slab merging all the slab of ds
    order is the order of the first slab
    '''
    # first determine the number of slabs
    nslab=len(ds)
    order0=None
    times=[[]]*nslab
    vals=[]
    ax=ds[0].getAxisList()
    # Now makes sure time is first
    timesleft=[]
    for i in range(nslab):
        order=ds[i].getOrder(ids=1)
        if order0 is None : order0=order
        if order[0]!='t' :
            ds[i]=ds[i](order='t...')
        times[i]=ds[i].getTime()
        units=times[i].units
        cal=times[i].getCalendar()
        tmpdic={}
        for ii in range(len(times[i])):  # creates the dictionary of times not matched yet
            t=times[i][ii]
            tmpval=cdtime.reltime(times[i][ii],units).torel('seconds since 2000',cal)
            tmpdic[ii]=tmpval
            vals.append(tmpval.value)
        timesleft.append(tmpdic)
    vals.sort()
    nt=len(vals)
    # sys.exit()
    # Quick error check (no duplicate)
    
    for i in range(nt-1):
        if vals[i]==vals[i+1] :
            errtime=cdtime.reltime(vals[i],'seconds since 2000').tocomp()
            err='Error in merging process : duplicate time point\n'
            err=err+str(errtime)+' is duplicated, cannot merge'
            raise err

    # Now create the big array that will be the merged
    sh=list(ds[0].shape)
    sh[0]=nt
    out=MA.zeros(tuple(sh),MV.Float)
    # bounds array
    bnds=Numeric.zeros((nt,2),MV.Float)
    fvals=Numeric.zeros((nt),MV.Float)
    if not statusbar is None:
        import genutil
        prev=0
    for v in range(nt):
        if not statusbar is None and nt!=1:
            if not type(statusbar) in [type([]),type(())]:
                statusbar=float(v)/(nt-1.)
            elif v==0:
                statusbar.insert(0,float(v)/(nt-1.))
            else:
                statusbar[0]=float(v)/(nt-1.)
                
            prev=genutil.statusbar(statusbar,prev=prev,title='Merging')
        try:  # In order to speeed up, raise an execption to exit the inner loops
            for i in range(nslab):
                tim=times[i]
                for it in Numeric.sort(timesleft[i].keys()):
                    t=tim[it]
                    val=timesleft[i][it]
                    if val.value==vals[v]:
                        out[v]=ds[i][it]
                        fvals[v]=val.torel(times[0].units,times[0].getCalendar()).value
                        bnds[v]=tim.getBounds()[it]
                        bnds[v][0]=switchCalendars(bnds[v][0],tim.units,tim.getCalendar(),times[0].units,times[0].getCalendar()).value
                        bnds[v][1]=switchCalendars(bnds[v][1],tim.units,tim.getCalendar(),times[0].units,times[0].getCalendar()).value
                        del(timesleft[i][it])
                        raise  # to exit the it and i loops
                    elif val.value>vals[v]:
                        break
        except:
            pass
    if not statusbar is None and nt!=1:
        if type(prev[0])!=type(0) : prev[0].destroy()

    t=cdms.createAxis(fvals,bounds=bnds)
    t.designateTime()
    t.id='time'
    t.units=times[0].units
    t.setCalendar(times[0].getCalendar())
    ax[0]=t
    out=cdms.createVariable(out,id=ds[0].id,axes=ax,copy=0)
    if out.getOrder(ids=1)!=order0:
        return out(order=order0)
    else:
        return out


def switchCalendars(t1,u1,c1,u2,c2=None):
    '''
    converts a relative time from one calendar to another, assuming that they are in different calendar
    Usage: cvreltime(t1,c1,u2,c2)
    where t1 is cdtime reltime object or a value (then u1 is needed)
    c1,c2 are cdtime calendars
    u1, u2 the units in the final calendar
    '''
    if not (type(t1)==types.IntType or type(t1)==types.FloatType):
      c2=u2
      u2=c1
      c1=u1
      u1=t1.units
      t1=t1.value
    # makes t1 a cdtime object
    t1=cdtime.reltime(t1,u1)
    # Converts t1 to comptime
    t1=t1.tocomp(c1)
    return t1.torel(u2,c2)



class TimeSlicer:
    '''
    Author : Charles Doutriaux: doutriaux1@llnl.gov
    Date: April 2001
    Returns masked average of specific time slices
    "slicer" determine which slices of the Transient Variable (TV) are processed
    "criteria" gets TV (with time dimension) and returns a "timeless" mask, used to mask the averaged slices
    
    "slicer"
      Input:
            - Time Axis
            - User argument (can be anything) (in a list if more than one argument)
      Output:
          indices             : the indices for each season:
                                                     [[i1,i2,...,il],
                                                     [j1,j2,...,jm],
                                                     ...,
                                                     [k1,k2,...kn]]
          bounds              : the bounds covered by each slice for each season:
                                                     [[[i1b1,i1b2],[i2b1,i2b2],...,[ilb1,ilb2]],
                                                     [[[j1b1,j1b2],[j2b1,j2b2],...,[jmb1,jmb2]],
                                                     ...,
                                                     [[k1b1,k1b2],[k2b1,k2b2],...,[knb1,knb2]]]
          norm                : the actual length of each "season", and its start
                                                     [[Li,Si],
                                                     [Lj,Sj],
                                                     ...,
                                                     [Lk,Sk]]
    "criteria"
      Input:
            - slab : a slab
            - mask:  the actual percentage of data in each subset used to produce the slab
                     the bounds of its first (time) dimension must be correct
                     they will be used by centroid
            - spread: the begining and end time of the slice processed 
            - User argument (can be anything)
      Output:
            - the slab, masked
            
    Once constructed the object, beside "slicer" and "criteria" has 3 functions:
    
    "get" : which returns the slices wanted, appropriately masked
       Input:
          slab : the slab on which to operate
          sliceruserargument  : anything your slicer function needs, default is None
          criteriauserargument: anything your criteria function needs, default is None
       Output:
          out  : averaged and masked slices of slab
          
    "departures" : which returns the departures of slab from the result of get
       Input:
          slab                : slab from which the we want to get the departure
          sliceruserargument  : anything your slicer function needs, default is None
          criteriauserargument: anything your criteria function needs, default is None
          (ref): optional     : result from get or equivalent precomputed
          
       Output:
          out : departure of slab from ref
          
    "average" : which return the average of the result of get
       Input:
          slab                : the slab on which to operate
          slices              : the slices for each part
          bounds              : the length of each slice
          norm                : the actual length of each "season"
          criteriaarg         : arguments for criteria thing
       Output:
          out : the average of slab, masked by criteria

    Example of construction:
    TS=TimeSlicer(slicerfunc,criteriafunc)
    myres=TS(myslab,[[slicerarg,[criteriaarg]])
    myresdeparture=TS(myslab,[[slicerarg,[criteriaarg,ref]]]
    '''
    def __init__(self,slicerfunction=None,criteriafunction=None):
        self.slicer=slicerfunction
        self.criteria=criteriafunction
        self.__call__=self.get
        self.prev=0
        self.title=''
        
    def get(self,slab,slicerarg=None,criteriaarg=None,statusbar=None):
        return _get(self,slab,slicerarg,criteriaarg,statusbar)
    
    def _get(self,slab,slicerarg=None,criteriaarg=None,statusbar=None):
        '''
    Returns the slices wanted, appropriately masked
       Input:
          slab : the slab on which to operate
          sliceruserargument  : anything your slicer function needs, default is None
          criteriauserargument: anything your criteria function needs, default is None
          statusbar=None : statusbar ?
       Output:
          out  : averaged and masked slices of slab
        '''
        
        
        # Makes sure time is first
        initialorder=slab.getOrder(ids=1)
        if initialorder[0]!='t' : slab=slab(order='t...')

        # retrieve the time axis
        tim=slab.getTime()
        
        # Let slicer figure out wich slices we want
        slices,bounds,norm=self.slicer(tim,slicerarg)
##         print 'Slices:',slices,len(slices)
##         print 'Bounds:',bounds
##         print 'Norm:',norm
##         print 'Slices:',slices[-3:]
##         print 'Bounds:',bounds[-3:]
##         print 'Norm:',norm[-3:]
        
        # Check we have something
        if slices==[] : raise 'Error Slicer return nothing for: '+str(slicerarg)
        # How many slices ?
        out=self.average(slab,slices,bounds,norm,criteriaarg,statusbar)
            
        # Put the dimensions
        out=cdms.createVariable(out,id=slab.id,copy=0)
        for i in range(1,len(slab.shape)):
            out.setAxis(i,slab.getAxis(i))
        # Time axis
        n=len(slices)
        vals=Numeric.zeros((n),MV.Float)  # time values
        bnds=Numeric.zeros((n,2),MV.Float) # time bounds
        # Retrieve the bounds
        sh=out.shape
        for i in range(sh[0]):
            b0=norm[i][1]
            b1=norm[i][0]+b0
            bnds[i]=b0,b1
            v=cdtime.reltime(b0,tim.units).value
            v=v+cdtime.reltime(b1,tim.units).value
            v=v/2.
            vals[i]=v
        t=cdms.createAxis(vals,bounds=bnds)
        t.designateTime()
        t.id=tim.id
        t.units=tim.units
        t.setCalendar(tim.getCalendar())
        out.setAxis(0,t)
        if out.getOrder(ids=1)!=initialorder:
            return out(order=initialorder)
        else:
            return out
            

    def departures(self,slab,slicerarg=None,criteriaarg=None,ref=None,statusbar=None):
        return self._departures(self,slab,slicerarg=slicerarg,criteriaarg=criteriaarg,ref=ref,statusbar=statusbar)
    
    def _departures(self,slab,slicerarg=None,criteriaarg=None,ref=None,statusbar=None):
        '''
    Returns the departures of slab from the result of get
       Input:
          slab                : slab from which the we want to get the departure
          sliceruserargument  : anything your slicer function needs, default is None
          criteriauserargument: anything your criteria function needs, default is None
          (ref): optional     : result from get or equivalent precomputed
          statusbar           : statusbar stuff (see statusbar function for details)
          
       Output:
          out : departure of slab from ref
          '''
        sliced=self._get(slab,slicerarg,criteriaarg,statusbar=statusbar)
##         print "sliced:",sliced
        order=sliced.getOrder(ids=1)
        if order[0]!='t' : sliced=sliced(order='t...')
        order2=sliced.getOrder(ids=1)
        if ref is None:
            ref=MA.average(sliced,0)
        elif len(order2[1:])>0:
            ref=ref(order=order2[1:])
        if cdms.isVariable(ref):
            out=cdms.asVariable(sliced(raw=1)-ref(raw=1))
        else:
            out=cdms.asVariable(sliced(raw=1)-ref)
        # put the axes back
        out.id=slab.id
        for i in range(len(sliced.shape)):
            out.setAxis(i,sliced.getAxis(i))
        if out.getOrder(ids=1)!=order:
            return out(order=order)
        else:
            return out


    def average(self,slab,slices,bounds,norm,criteriaarg=None,statusbar=None):
        '''
    Return the average of the result of slicer
       Input:
          slab                : the slab on which to operate
          slices              : the slices for each part
          bounds              : the length of each slice
          norm                : the actual length of each "season"
          criteriaarg         : arguments for criteria thing
       Output:
          out : the average of slab, masked by criteria
          '''
        n=len(slices)
        sh=list(slab.shape)
        sh[0]=n
        out=MA.zeros(sh,typecode=MA.Float)
        for i in range(n):
            self.statusbar1(i,n,statusbar)
            sub=slices[i]
            sh[0]=len(sub)
            msk=Numeric.ones(sh,typecode=MA.Float)
            subb=bounds[i]
            nrm=norm[i][0]
##             print sub,subb,nrm,'are subb, nrm',len(sub)
            if len(sub)==1:
                out[i]=slab[sub[0]]
                if not criteriaarg is None:
                    w=float(subb[0][1]-subb[0][0])/nrm
                    msk=msk*w
            else:
                for j in range(len(sub)):
                    w=float(subb[j][1]-subb[j][0])/nrm
                    m=slab[sub[j]].mask()
                    if not m is None:
                        msk[j]=msk[j]*(1.-m.astype(MV.Float))*w
                    else:
                        msk[j]=msk[j]*w
##                 print msk.shape,slab[sub[0]:sub[-1]+1].shape
                out[i]=MA.sum(slab[sub[0]:sub[-1]+1]*msk,axis=0)
                out[i]=out[i]/MA.sum(msk,axis=0)
            if not criteriaarg is None:
                msk=cdms.asVariable(msk)
                ax=msk.getAxis(0)
                b=Numeric.array(bounds[i])
                ax.setBounds(b)
                msk.setAxis(0,ax)
                out[i]=self.criteria(out[i],msk,[norm[i][1],norm[i][1]+norm[i][0],],criteriaarg)
        self.statusbar2(statusbar)
        return out


    
    def statusbar1(self,i,n,statusbar):
        if not statusbar is None and n!=1:
            import genutil
            if not type(statusbar) in [type([]),type(())]:
                if type(statusbar)!=type(''):
                    status=float(i)/(n-1.)
                else:
                    status=float(i+eval(statusbar)[0]*n)/(eval(statusbar)[1]*n)
            else:
                status=statusbar[1:]
                tot=eval(statusbar[0])
                if type(tot)==type(''):
                    status.insert(0,float(i+eval(statusbar)[0]*n)/(eval(statusbar)[1]*n))
                else:
                    status.insert(0,float(i)/(n-1.))
            self.prev=genutil.statusbar(status,prev=self.prev,title=self.title)

    def statusbar2(self,statusbar):
        if not statusbar is None:
            if not type(statusbar) in [type([]),type(())]:
                if type(statusbar)!=type(''):
                    if type(self.prev) in [type([]),type(())] :
                        if type(self.prev[0])!=type(0):self.prev[0].destroy()
                    self.prev=0
                elif eval(statusbar)[0]==eval(statusbar)[1]-1:
                    if type(self.prev) in [type([]),type(())] :
                        if type(self.prev[0])!=type(0):self.prev[0].destroy()
                    self.prev=0
            else:
                status=statusbar[1:]
                tot=eval(statusbar[0])
                if type(tot)==type(''):
                    if eval(statusbar)[0]==eval(statusbar)[1]-1:
                        if type(self.prev) in [type([]),type(())]  :
                            if type(self.prev[0])!=type(0):self.prev[0].destroy()
                        self.prev=0                        
                else:
                    if type(self.prev) in [type([]),type(())]  :
                        if type(self.prev[0])!=type(0):self.prev[0].destroy()
                    self.prev=0
            if type(statusbar) in [type([]),type(())]: statusbar.pop(0)


def monthBasedSlicer(tim,arg=None):
    '''
    slicer function for the TimeSlicer class
    select months
    Author : Charles Doutriaux, doutriaux1@llnl.gov
    Original Date: April 2001
    Last Modified: October, 2001
    Input:
      - tim: time axis
      - arg: character string representing the desired month/season or integer(s)
             also you can pass a list of the months you want (string or integer)
             you can mix integer and strings
    Output:
      - 
    '''
    # First convert the input
    if not type(arg) in [types.ListType , types.TupleType]:
        arg=[arg]
    # Now convert the strings and add to the valid months
    months=[]
    for i in range(len(arg)):
        if type(arg[i])==types.StringType:
            vals=getMonthIndex(arg[i])
            for j in vals: months.append(j)
        else:
            months.append(arg[i])
    slices=[]
    bounds=[]
    seaslength=[]
    sub=[]
    subb=[]
    subs=[]
    bnds=tim.getBounds()
    cal=tim.getCalendar()
    units=tim.units
    nt=len(tim)
    for i in range(nt):
        b0=cdtime.reltime(bnds[i][0],units)
        b1=cdtime.reltime(bnds[i][1],units)
        iout=0
        # Now figures out what the length of
        # the requested season
        b=b0.tocomp(cal)
        yr=b.year
        if months[-1]==12:
            bb=cdtime.comptime(b.year+1)
        else:
            bb=cdtime.comptime(b.year,months[-1]+1)
##         if b.cmp(bb)>0:
##             yr=yr+1
        # do we span 2 years ?
        if months[0]>months[-1] : # yes
            ## Are we in the part before the year's end
            if b.month<months[0]: ## no
                t0=cdtime.comptime(yr-1,months[0])
                t1=cdtime.comptime(yr,months[-1]+1)
            else: ## yes
##                 print 'in here ?',b
                t0=cdtime.comptime(yr,months[0])
                t1=cdtime.comptime(yr+1,months[-1]+1)                
        else:
            t0=cdtime.comptime(yr,months[0])
            if months[-1]!=12:
                t1=cdtime.comptime(yr,months[-1]+1)
            else:
                t1=cdtime.comptime(yr+1)
        t1=t1.torel(units,cal)
        t0=t0.torel(units,cal)
        lenseas=float(t1.value-t0.value)
        # Now checks if we overlap the season
##         print b0.tocomp(),b1.tocomp(),t0.tocomp(),t1.tocomp(),i
        if t0.cmp(b0)>-1:        # cell starts before season
##             print 'index t0>=b0 ,time',i,tim[i],t0.tocomp(),b0.tocomp(),b0
            if b1.cmp(t1)>=0 :            # and ends after the season
                sub.append(i)
                subb.append([t0.value,t1.value])
                subs.append([lenseas,t0.value])
            elif t0.cmp(b1)>-1:        # all before the season
                iout=1
            else:                      # ends during the season
                sub.append(i)
                subb.append([t0.value,b1.value])
                subs.append([lenseas,t0.value])
            # Now check if if this is exactly one season long !
            if (b1.value-b0.value==lenseas) and t0.cmp(b0)==0:
                iout=1

        elif t1.cmp(b0)==1:      # end season after beginning of cell ?
##             print 'index,t1>b0 time',i,tim[i],t1.tocomp(),b0.tocomp(),b
            if b1.cmp(t1)>0:             # and ends after the end
                sub.append(i)
                subb.append([b0.value,t1.value])
                subs.append([lenseas,t0.value])
##                 print 'haha',len(months),t0.value
##                 if len(months)==12 or lenseas==(b1.value-b1.value):
                if len(months)==12:
##                     print "i:",i,tim[i]
##                     print "sub :",sub
##                     print "subb:",subb
##                     print "subs:",subs
                    slices.append(sub)
                    bounds.append(subb)
                    seaslength.append([lenseas,t0.value])
                    sub=[i]
                    subb=[[t1.value,b1.value]]
                    subs=[[lenseas,t1.value]]
            else:                       # but ends during
                sub.append(i)
                subb.append([b0.value,b1.value])
                subs.append([lenseas,t0.value])
                if len(months)==12 and b1.cmp(t1)==0:
                    slices.append(sub)
                    bounds.append(subb)
                    seaslength.append([lenseas,t0.value])
                    sub=[]
                    subb=[]
                    subs=[]
        else:
            iout=1
        if iout:
            if sub!=[]:
                slices.append(sub)
                bounds.append(subb)
                seaslength.append(subs[-1])
                sub=[]
                subb=[]
                subs=[]
        ## ??? Add something here for 12 omnths span....
        ## like remenbering which season we're at, etc....
    if sub!=[]:
        slices.append(sub)
        bounds.append(subb)
##         print 'using:',subs
        seaslength.append(subs[-1])
    # Now looks for the cyclical thing
    # ??? do something here as well......
    return slices,bounds,seaslength


def dayBasedSlicer(tim,arg=None):
    '''
    slicer function for the TimeSlicer class
    select days
    Author : Charles Doutriaux, doutriaux1@llnl.gov
    Original Date: June, 2003
    Last Modified: ...
    Input:
      - tim: time axis
      - arg: character string representing the desired day/days or day number(s) (jan 1st, is day 0, feb 29th is day 59.5...)
             day are represented as "Jan-01" "January-01" "jan-1", "1-january", case does not matter
             days can be represented by 2 number but then month is assumed to be first ! e.g "01-25" = "jan-25"
             you can mix definitions
    Output:
      - 
    '''
    # First convert the input
    if not type(arg) in [types.ListType , types.TupleType]:
        arg=[arg]
    # Now convert the strings and add to the valid month/day tupples
    tupples=[]
    for i in range(len(arg)):
        subarg=arg[i]
        if type(subarg)!=types.StringType:
            raise "Error, arguments to dayBasedSlicer must be strings"
        sp=string.split(subarg,"-")
        if sp[0]==subarg:
            sp=string.split(subarg,'/')
            if sp[0]==subarg:
                try:
                    index=string.atof(subarg)
                    if index==59.5:
                        subarg='feb-29'
                    else:
                        t=cdtime.reltime(index,'month since 1997')
                        t=t.tocomp()
                        subarg=str(t.month)+'-'+str(t.day)
                except:
                    raise "Error, dayBasedSlicer args must have '-' or '/' as month/day separator"
        try:
            day=string.atoi(sp[1])
            try:
                month=getMonthIndex(sp[0])
            except:
                month=string.atoi(sp[0])
        except:
            try:
                day=string.atoi(sp[0])
                try:
                    month=getMonthIndex(sp[1])
                except:
                    month=string.atoi(sp[1])
            except:
                raise "Error dayBasedSlicer couldn't understand argument: "+subarg
        tupples.append([day,month])
    slices=[]
    bounds=[]
    seaslength=[]
    sub=[]
    subb=[]
    subs=[]
    bnds=tim.getBounds()
    cal=tim.getCalendar()
    units=tim.units
    nt=len(tim)
    for i in range(nt):
        b0=cdtime.reltime(bnds[i][0],units)
        b1=cdtime.reltime(bnds[i][1],units)
        iout=0
        # Now figures out what the length of
        # the requested season
        b=b0.tocomp(cal)
        yr=b.year
        if months[-1]==12:
            bb=cdtime.comptime(b.year+1)
        else:
            bb=cdtime.comptime(b.year,months[-1]+1)
        if b.cmp(bb)>0:
            yr=yr+1
        # do we span 2 years ?
        if months[0]>months[-1] : # yes
            t0=cdtime.comptime(yr-1,months[0])
            if months[-1]!=12:
                t1=cdtime.comptime(yr,months[-1]+1)
            else:
                t1=cdtime.comptime(yr+1)                
        else:
            t0=cdtime.comptime(yr,months[0])
            if months[-1]!=12:
                t1=cdtime.comptime(yr,months[-1]+1)
            else:
                t1=cdtime.comptime(yr+1)
        t1=t1.torel(units,cal)
        t0=t0.torel(units,cal)
        lenseas=float(t1.value-t0.value)
##         print 't0,b0,t1,b1',t0,b0,t1,b1
        # Now checks if we overlap the season
        if t0.cmp(b0)>-1:        # cell starts before season
            if b1.cmp(t1)>0 :            # and ends after the season
                sub.append(i)
                subb.append([t0.value,t1.value])
                subs.append([lenseas,t0.value])
            elif t0.cmp(b1)>-1:        # all before the season
                iout=1
            else:                      # ends during the season
                sub.append(i)
                subb.append([t0.value,b1.value])
                subs.append([lenseas,t0.value])
            # Now check if if this is exactly one season long !
            if (b1.value-b0.value==lenseas) and t0.cmp(b0)==0:
                iout=1

        elif t1.cmp(b0)==1:      # end season after beginning of cell ?
##             print 'index,time',i,tim[i]
            if b1.cmp(t1)>0:             # and ends after the end
                sub.append(i)
                subb.append([b0.value,t1.value])
                subs.append([lenseas,t0.value])
##                 print 'haha',len(months),t0.value
##                 if len(months)==12 or lenseas==(b1.value-b1.value):
                if len(months)==12:
##                     print "i:",i,tim[i]
##                     print "sub :",sub
##                     print "subb:",subb
##                     print "subs:",subs
                    slices.append(sub)
                    bounds.append(subb)
                    seaslength.append([lenseas,t0.value])
                    sub=[i]
                    subb=[[t1.value,b1.value]]
                    subs=[[lenseas,t1.value]]
            else:                       # but ends during
                sub.append(i)
                subb.append([b0.value,b1.value])
                subs.append([lenseas,t0.value])
                if len(months)==12 and b1.cmp(t1)==0:
                    slices.append(sub)
                    bounds.append(subb)
                    seaslength.append([lenseas,t0.value])
                    sub=[]
                    subb=[]
                    subs=[]
        else:
            iout=1
        if iout:
            if sub!=[]:
                slices.append(sub)
                bounds.append(subb)
                seaslength.append(subs[-1])
                sub=[]
                subb=[]
                subs=[]
        ## ??? Add something here for 12 omnths span....
        ## like remenbering which season we're at, etc....
    if sub!=[]:
        slices.append(sub)
        bounds.append(subb)
##         print 'using:',subs
        seaslength.append(subs[-1])
    # Now looks for the cyclical thing
    # ??? do something here as well......
    return slices,bounds,seaslength

def weekday(a,calendar=None):
    if calendar is None:
        b=a.torel('days since 0')
    else:
        b=a.torel('days since 0',calendar)        
    d=(b.value - 3) % 7
    if d==1:
        return 'monday'
    elif d==2:
        return 'tuesday'
    elif d==3:
        return 'wednesday'
    elif d==4:
        return 'thursday'
    elif d==5:
        return 'friday'
    elif d==6:
        return 'saturday'
    else:
        return 'sunday'



def generalCriteria(slab,mask,spread,arg):
    '''
    Default Conditions:
      50% of the data
      AND 
      Centroid < x (in absolute value), centroid is always between 0 (perfect and 1, none perfect)
      by default centroid is not used
      
    Author: Charles Doutriaux, doutriaux1@llnl.gov

    Usage:
        generalCriteria(slab,sliced,slices,arg)
        slab : the original slab
        mask:  the actual percentage of data in each subset used to produce the slab
               the bounds of its first (time) dimension must be correct
               they will be used by centroid
        spread: the begining and end time of the slice processed 
        arg:
            First represent the % of value present to retain a slice
            Second represent the value of the centroid (between 0: perfect and 1: bad
            If you do not want to use one these criteria pass None
            if you would rather use a cyclicalcnetroid pass: "cyclical" as an Xtra argument
    '''
    # Reads the arguments
    slab=MV.asVariable(slab)
    sh=slab.shape
##     print slab,mask,spread,arg
    if not arg is None:
        min=arg[0]
        centro=arg[1]
    # prepare the mask
##     print 'Mask shape',mask.shape
    if not min is None:
        fmask=Numeric.sum(mask)
        fmask=Numeric.less(fmask,min)
##         print 'fmask,slab',fmask.shape,slab.shape
##         import sys,vcs
##         x=vcs.init()
##         x.plot(mask)
##         sys.stdin.readline()
##         x.clear()
##         x.plot(fmask)
        slab=MA.masked_where(fmask,slab)
    if not centro is None:
        a=MA.equal(mask,0.)
        a=MV.masked_where(a,a)
        a.setAxis(0,mask.getAxis(0))
        mask=a
        if 'cyclical' in arg:
            c=cyclicalcentroid(mask,spread)
        else:
            c=centroid(mask,spread)
            c=MA.absolute(c)
        slab=MA.masked_where(MA.greater_equal(c,centro),slab)
    return slab

def setAxisTimeBoundsDaily(axis,frequency=1):
    """ Sets the bounds correctly for the time axis (beginning to end of day)
    Usage:
    tim=s.getTime()
    cdutil.times.setAxisTimeBoundsMonthly(tim,frequency=1)
    e.g. for twice-daily data use frequency=2
         for 6 hourly data use frequency=4
         for   hourly data use frequency=24
    Origin of day is always midnight
    """
    tim=axis
    if not tim.isTime():
        raise ValueError,'Time Axis only please !'
    if tim is None:
        return
    units=tim.units
    timc=tim.asComponentTime()
    n=len(tim)
    bnds=Numeric.zeros((n,2),Numeric.Float)
    frequency=int(frequency)
    for i in range(n):
        t=timc[i]
        d=t.day
        m=t.month
        y=t.year
        h=t.hour
        for f in range(frequency):
            if f*(24/frequency)<=h<(f+1)*(24/frequency):
                t1=cdtime.comptime(y,m,d,f*(24/frequency))
                t2=t1.add(24/frequency,cdtime.Hours,tim.getCalendar())
                t1=t1.torel(units,tim.getCalendar())
                t2=t2.torel(units,tim.getCalendar())
        bnds[i,0]=t1.value
        bnds[i,1]=t2.value
    tim.setBounds(bnds)
    return

def setSlabTimeBoundsDaily(slab,frequency=1):
    """Sets the bounds correctly for the time axis (beginning to end of day)
    for 'frequency'-daily data
    Usage:
    cdutil.times.setSlabTimeBoundsDaily(slab,frequency=1)
    e.g. for twice-daily data use frequency=2
         for 6 hourly data use frequency=4
         for   hourly data use frequency=24
    Origin of day is always midnight
    """
    tim=slab.getTime()
    setAxisTimeBoundsDaily(tim,frequency=frequency)
    return

def setTimeBoundsDaily(obj,frequency=1):
    """Sets the bounds correctly for the time axis (beginning to end of day)
    for 'frequency'-daily data
    Usage:
    cdutil.times.setSlabTimeBoundsDaily(slab,frequency=1)
    or
    cdutil.times.setSlabTimeBoundsDaily(time_axis,frequency=1)
    e.g. for twice-daily data use frequency=2
         for 6 hourly data use frequency=4
         for   hourly data use frequency=24
    Origin of day is always midnight
    """
    if isinstance(obj,cdms.AbstractAxis):
        setAxisTimeBoundsDaily(obj,frequency=frequency)
    elif isinstance(obj,cdms.MV.AbstractVariable):
        setSlabTimeBoundsDaily(obj,frequency=frequency)
    return

def setAxisTimeBoundsMonthly(axis,stored=0):
    """ Sets the bounds correctly for the time axis (beginning to end of month)
    Set stored to 1 to indicate that your data are stored at the end of the month
    Usage:
    tim=s.getTime()
    cdutil.times.setAxisTimeBoundsMonthly(tim,stored=0)
    """
    tim=axis
    if not tim.isTime():
        raise ValueError,'Time Axis only please !'
    if tim is None:
        return
    units=tim.units
    timc=tim.asComponentTime()
    n=len(tim)
    bnds=Numeric.zeros((n,2),Numeric.Float)
    for i in range(n):
        t=timc[i]
        d=t.day
        m=t.month
        y=t.year
        if stored == 1 and d<2: #data stored at the end of the month
            if m==1 : y=y-1
            m=m-1
            if m==0 : m=12
        t1=cdtime.comptime(y,m)
        t2=t1.add(1,cdtime.Month,tim.getCalendar())
        t1=t1.torel(units,tim.getCalendar())
        t2=t2.torel(units,tim.getCalendar())
        bnds[i,0]=t1.value
        bnds[i,1]=t2.value
    tim.setBounds(bnds)
    return

def setSlabTimeBoundsMonthly(slab,stored=0):
    """ Sets the bounds correctly for the time axis for monthly data stored
    without bounds.
    Set stored to 1 to indicate that your data are stored at the end of the month
    Usage:
    cdutil.times.setSlabTimeBoundsMonthly(slab,stored=0)
"""
    tim=slab.getTime()
    setAxisTimeBoundsMonthly(tim,stored=stored)
    return

def setTimeBoundsMonthly(obj,stored=0):
    """ Sets the bounds correctly for the time axis (beginning to end of month)
    Set stored to 1 to indicate that your data are stored at the end of the month
    Usage:
    tim=s.getTime()
    cdutil.times.setAxisTimeBoundsMonthly(s,stored=0)
    or
    cdutil.times.setAxisTimeBoundsMonthly(tim,stored=0)
    """
    if isinstance(obj,cdms.AbstractAxis):
        setAxisTimeBoundsMonthly(obj,stored=stored)
    elif isinstance(obj,cdms.MV.AbstractVariable):
        setSlabTimeBoundsMonthly(obj,stored=stored)
    return


def setAxisTimeBoundsYearly(axis):
    """ Sets the bounds correctly for the time axis (beginning to end of year)
    Usage:
    tim=s.getTime()
    cdutil.times.setAxisTimeBoundsYearly(tim)
    """
    tim=axis
    if tim is None:
        return
    units=tim.units
    timc=tim.asComponentTime()
    n=len(tim)
    bnds=Numeric.zeros((n,2),Numeric.Float)
    for i in range(n):
        t=timc[i]
        y=t.year
        t1=cdtime.comptime(y)
        t2=t1.add(1,cdtime.Year,tim.getCalendar())
        t1=t1.torel(units,tim.getCalendar())
        t2=t2.torel(units,tim.getCalendar())
        bnds[i,0]=t1.value
        bnds[i,1]=t2.value
    tim.setBounds(bnds)
    return

def setSlabTimeBoundsYearly(slab):
    """ Sets the bounds correctly for the time axis for yearly data
    Usage:
    cdutil.times.setSlabTimeBoundsYearly(slab)
"""
    tim=slab.getTime()
    setAxisTimeBoundsYearly(tim)
    return

def setTimeBoundsYearly(obj):
    """ Sets the bounds correctly for the time axis for yearly data
    Usage:
    cdutil.times.setSlabTimeBoundsYearly(slab)
    or
    cdutil.times.setSlabTimeBoundsYearly(time_axis)
"""
    if isinstance(obj,cdms.AbstractAxis):
        setAxisTimeBoundsYearly(obj)
    elif isinstance(obj,cdms.MV.AbstractVariable):
        setSlabTimeBoundsYearly(obj)
    return



class ASeason(TimeSlicer):
    def __init__(self):
        self.prev=0
        self.title=''
        self.slicer=monthBasedSlicer
        self.criteria=generalCriteria

class Seasons(ASeason):
    def __init__(self,*seasons):
        self.__call__=self.get
        if len(seasons)==1:
            seasons=seasons[0]
        if type(seasons)==types.StringType:
            seasons=[seasons]
        for i in range(len(seasons)):
            if type(seasons[i]) in [types.ListType,types.TupleType,types.IntType]:
                seasons[i]=getMonthString(seasons[i])
        self.seasons=seasons
        self.slicer=monthBasedSlicer
        self.criteria=generalCriteria
        self.prev=0
        self.title=''

    def get(self,slab,slicerarg=None,criteriaarg=None,statusbar=None):
        '''Get the seasons asked for and return them in chronological order
        i.e. if you asked for DJF and JJA and the first season of your dataset is JJA you will have a JJA first !!!!
        Check your time axis coordinate !!!
        slicerarg will be ignored
        it is recomended to use Season(slab,criteria=mycriteriaarguments) syntax
        rather than Season(slab,None,None,mycriteriaarguments)
        Now for the original doc of the get function see get2__doc__:
        '''
        s=[]
        i=-1
        for season in self.seasons:
            i=i+1
            self.statusbar1(i,len(self.seasons),statusbar)
            s.append(self._get(slab,season,criteriaarg,statusbar=statusbar))
        self.statusbar2(statusbar)
        return mergeTime(s,statusbar=statusbar)

    def departures(self,slab,slicerarg=None,criteriaarg=None,ref=None,statusbar=None):
        ''' Return the departures for the list of season you specified, returned in chronological order
        i.e. if you asked for DJF and JJA and the first season of your dataset is JJA you will have a JJA first !!!!
        Check your time axis coordinate !!!
        To pass a specific array from which to compute departures, please pass 1 per season (or None if we should compute it)
        for info one default departures see: departures2.__doc__
        '''
        s=[]
        # Loop through the seasons
        self.departures_seasons=self.seasons
        for i in range(len(self.departures_seasons)):
            self.seasons=[self.departures_seasons[i]]
            # Do we want a statusbar ?
            if not statusbar is None:
                if not type(statusbar) in [type([]),type(())]:
                    statusbar=str([float(i),len(self.departures_seasons)])
                elif i==0:
                    statusbar.insert(0,str([float(i),len(self.departures_seasons)]))
                else:
                    statusbar[0]=str([float(i),len(self.departures_seasons)])
            # Did we pass a reference to copmute the departures from ?
            if not ref is None :
                newref=ref[i]
            else:
                newref=None
            # now computes the departures
            out=self._departures(slab,slicerarg=self.departures_seasons[i],criteriaarg=criteriaarg,statusbar=statusbar,ref=newref)
            # Adds it to the list
            s.append(out)
        self.seasons=self.departures_seasons
        if not statusbar is None and len(self.seasons)!=1 :
            if type(statusbar) in [type([]),type(())]: statusbar.pop(0)
        # Now merges the stuff
        return mergeTime(s,statusbar=statusbar)
                                    
    def climatology(self,slab,criteriaarg=None,criteriaargclim=None,statusbar=None):
        ''' Compute the climatology from a slab
        Input:
          slab
          criteriaarg     : the argument for criteria function when slicing the season (and clim)
          criteriaargclim : the argument for criteria function when averaging the seasons together
                            if different from criteriarg
        Output:
          The Average of the seasons in the order passed when constructing it
          i.e if DJF and JJA are asked, the output will have the average DJF first, then the average JJA
          2 criteria can be passed one for the slicing part and one for the climatology part
        '''
        if criteriaargclim is None: criteriaargclim=criteriaarg
        order=slab.getOrder(ids=1)
        if order[0]!='t' : slab=slab(order='t...')
        timeaxis=slab.getAxis(0)
        timecalendar=timeaxis.getCalendar()
        sh=list(slab.shape)
        nseason=len(self.seasons)
        sh[0]=nseason
        s=MA.zeros(sh,MV.Float)
        vals=Numeric.zeros(nseason,MV.Float)
        bnds=Numeric.zeros((nseason,2),MV.Float)
        tim=slab.getTime()
        for i in range(nseason):
            if not statusbar is None:
                if not type(statusbar) in [type([]),type(())]:
                    statusbar=str([float(i),len(self.seasons)])
                elif i==0:
                    statusbar.insert(0,str([float(i),len(self.seasons)]))
                else:
                    statusbar[0]=str([float(i),len(self.seasons)])
            months=getMonthIndex(self.seasons[i])
            if len(months)==1 : months=months*2
            if months[0]>months[1] : months[0]=months[0]-12
            v1=cdtime.reltime(months[0]-1,'months since 0').torel('days since 0',timecalendar)
            v2=cdtime.reltime(months[-1],'months since 0').torel('days since 0',timecalendar)
            vals[i]=float(v1.value+v2.value)/2.
            bnds[i]=[v1.value,v2.value]
            tmp=self._get(slab,self.seasons[i],criteriaarg,statusbar=statusbar)
            if not criteriaargclim is None:
                tmp2=tmp.mask().astype(MV.Float)
                if tmp2 is None:
                    tmp2=Numeric.ones(tmp.shape,typecode=Numeric.Float)
                else:
                    tmp2=1.-tmp2
                tim=tmp.getTime()
                bnd=tim.getBounds()
                tot=0
                for j in range(len(bnd)):
                    w=float(bnd[j][1]-bnd[j][0])
                    tot=tot+w
                    tmp2[j]=tmp2[j]*w
                tmp2=tmp2/tot
                if not cdms.isVariable(tmp2): tmp2=cdms.asVariable(tmp2)
                tmp2.setAxis(0,tim)
                tmp=MA.average(tmp)
                tmp=self.criteria(tmp,tmp2,bnds[i],criteriaargclim)
            else:
                tmp=MA.average(tmp)                
            s[i]=tmp
        if not statusbar is None and len(self.seasons)!=1 :
            if type(statusbar) in [type([]),type(())]: statusbar.pop(0)
        t=cdms.createAxis(vals,bounds=bnds)
        t.id='time'
        t.units='days since 0'
        t.designateTime()
        t.setCalendar(tim.getCalendar())
        ax=slab.getAxisList()
        ax[0]=t
        s=cdms.createVariable(s,id=slab.id,axes=ax,copy=0)
        if s.getOrder(ids=1)!=order:
            return s(order=order)
        else:
            return s
    
## Seasons.get.__doc__=Seasons.get.__doc__+Seasons._get.__doc__
## Seasons.departures.__doc__=Seasons.departures.__doc__+Seasons._departures.__doc__

ANNUALCYCLE=Seasons([1,2,3,4,5,6,7,8,9,10,11,12])
SEASONALCYCLE=Seasons(['DJF','MAM','JJA','SON'])

DJF=Seasons('DJF')
MAM=Seasons('MAM')
JJA=Seasons('JJA')
SON=Seasons('SON')
JAN=Seasons('JAN')
FEB=Seasons('FEB')
MAR=Seasons('MAR')
APR=Seasons('APR')
MAY=Seasons('MAY')
JUN=Seasons('JUN')
JUL=Seasons('JUL')
AUG=Seasons('AUG')
SEP=Seasons('SEP')
OCT=Seasons('OCT')
NOV=Seasons('NOV')
DEC=Seasons('DEC')

YEAR=Seasons('JFMAMJJASOND')

