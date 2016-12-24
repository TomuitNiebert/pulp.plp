"""
Convex Piecewise Linear Programming frontend.

written by Tom van der Hoeven.
"""
__version__ = '2016-12-23'
import timer
#import plpsnel as plp
import plppulp as plp
print 'plpcom version ', __version__
def clip(a,b,c) : return a if b<a else c if b>c else b

def doname(self):
    """Add name to list lll and dir ddd and test on uniqueness."""
    self.lll.append(self)
    name = self.name
    if name in self.ddd : print 'equal name', str(self)
    else : self.ddd[name] = self 

class plpvar(object):
    """Handles plp variables."""
    def __init__(self, name, plf = 0.0, funcost = 'c'):
        """Makes variable with name and piecewise linear function
        plf = [s0, p1, s2, p3, ........]
        
        s0 <= s2 <= s4 .....
        p1 <= p3 <= p5 .....
        special cases:
        plf = 5.6 is equivalent to plf = [5.6]
        plf = [] meaningles, forbidden
        plf = [None] meaningles, forbidden
        plf = [4.5] cost coef = 4.5
        plf = [None, a] lb = a , ub = a
        plf = [3.7, 8.5] cost coef 3.7 ub 8.5
        plf = [None, -5, 7] : lb = -5 cost coef = 7
        """
        self.name = name
        self.plf = plf
        doname(self)
                    
    def set_plf(self, plf):
        """set en test plf"""
        self._plf = plf
        if type(plf)==list:
            if plf == [] or plf == [None]:
                raise Exception('plf error {} plf, []'.format(self.__str__()) )
            else:
                ib = 2 + (plf[0] == None)
                for i in range(ib, len(plf)) :
                    if plf[i] < plf[i-2] + 1e-6 :
                       raise Exception('plf order error indices {} and {}  {}'.
                              format(i-2, i, self.__str__() ) )

    def get_plf(self):
        return self._plf

    plf = property(get_plf, set_plf)
    
    def res(self):
        """Set variable attibutes x, force, ix and plfcost"""
        x, f, ix = plp.vares(self)
        self.x, self.force, self.ix = x, f, ix
        # bereken plfcost
        plf = self.plf
        if type(plf)<>list: plf = [plf]
        som = 0
        for i, val in enumerate(plf):
            if i%2 : #punt
                if i == 1    : som += sloop * ( min(x,val)      - val )
                elif sloop>0 : som += sloop * (clip(last,x,val) - last)
                elif sloop<0 : som += sloop * (clip(last,x,val) - val )
                last = val
            elif val == None : sloop = 0
            else : sloop = val
        if len(plf) == 1 : som = plf[0] * x
        elif len(plf)%2  : som += sloop * ( max(x,last) - last) 
        self.plfcost = som

    def __repr__(self): 
        return self.name

    def __str__(self): 
        return self.name + str(self.plf)

    def lowside(self):
        """Gives point with lowest cost beside slope ix"""
        #print self.name, self.ix,self.plf
        ix = self.ix
        plf = self.plf
        if type(plf)<>list or len(plf)== 1 : xp = 0
        else :
            ip = ix-1 if ix>=len(plf) or plf[ix]>0 else ix+1
            if ip<0 : ip +=2
            if ip>len(plf)-1 : ip -=2
            xp = plf[ip]
        return xp

class plpeq:
    """Handles plp euations."""
    def __init__(self, name, coefvar):
        """Makes equation with name and list of coeficients and variables
        list has format [(coef1,var1),(coef2,var2),constant1,(coef3,var3),constant2]
        """
        self.name = name
        self.coefvar = coefvar
        doname(self)

    def res(self) :
        """Set x (=0) and force"""
        self.x, self.force = plp.eqres(self)
    
    def __repr__(self): 
        return self.name

    def __str__(self): 
        return self.name + str(self.coefvar)

def plpinit():
    """Empty list lll directorie ddd of plp variables and plp equations"""
    plpvar.lll = []
    plpvar.ddd = {}
    plpeq.lll = []
    plpeq.ddd = {}

def plpexit(pname="N"):
    """Initiates and executes the solver and get results."""
    if type(pname)==int or type(pname)==float : pname = 'N' + str(pname)
    print '\n-- start solve {} --'.format(pname),

    timer.timer('plpsetup')
    plp.init(pname, plpvar.lll, plpeq.lll)
    timer.timer('plpsetup')

    timer.timer('plpsolve')
    lpcost, lpstatus = plp.maaksom()
    print 'Status : {:10}'.format(lpstatus),
    timer.timer('plpsolve')

    timer.timer('plpout') # translate from lp back to plp
    for va in plpvar.lll : va.res()
    for eq in plpeq.lll    : eq.res()
    timer.timer('plpout')
    totplfcost = sum(va.plfcost for va in plpvar.lll)
    print ' lpcost : {:12.2f} sumplfcost :{:12.2f}'.format(lpcost, totplfcost )

def mis(args, key, defval):
    if not key in args : args[key] = defval

def plpresults(**args):
    """Print list of plp results"""
    mis(args, 'minvalue', 0.0)
    mis(args, 'maxnumber', 1000000)
    mis(args, 'dosort', False)
    mis(args, 'equat', False)
    
    mm = [v for v in plpvar.lll if abs(v.force)>=args['minvalue'] 
                                  or abs(v.plfcost)>=args['minvalue']]
    if args['equat'] and args['dosort']<>'cost': 
        mm += [e for e in plpeq.lll if abs(e.force)>=args['minvalue']]
    
    if   args['dosort']=='force' : mm.sort( key = lambda v : -abs(v.force))
    elif args['dosort']=='cost'  : mm.sort( key = lambda v : -v.plfcost)
    elif args['dosort']=='name'  : mm.sort( key = lambda v : v.name)
    
    print '\n',args
    print 'name                         x        force ix         cost    low-point'
    for v in mm[:args['maxnumber']] : 
        top = '{:19} {:10.2f} {:12.2f}'.format(v.name, v.x, v.force)
        if hasattr(v,'plf') :
           top += ' {:2} {:12.2f}'.format(v.ix, v.plfcost)
           if not v.ix%2: top += ' {:12.2f}'.format(v.lowside())
        print top
    
def addplf(a,b):
    """Returns the sum of two piecewise linear functions."""
    #print '------ ', a, ' ------- ', b, ' -------'
    delta = 1.0e-5
    ia, na = 0, len(a)
    ib, nb = 0, len(b)
    c = []
    while ia<na and ib<nb :
        sa, pa = a[ia], a[ia+1] if ia+1<na else None
        sb, pb = b[ib], b[ib+1] if ib+1<nb else None
        sc = None if sa==None or sb==None else sa+sb
        pc = None if pa==pb==None else pa if pb==None else pb if pa==None else min(pa,pb)
        #print 'a i=',ia,' s=',sa,' p=',pa
        #print 'b i=',ib,' s=',sb,' p=',pb
        #print 'c',sc,pc
        if c==[] : c = [sc,pc]
        elif sc==None: c[1] = pc
        else:
            c.append(sc)
            if pc==None:return c
            else : c.append(pc)
        if pa<>None and pa<=pc+delta : ia+=2
        if pb<>None and pb<=pc+delta : ib+=2
        #print ia,ib,c
    return c
    
def test1():
    """Test x, ix, plfcost with x = xval"""
    print '\n' + test1.__doc__
    plfs = [
     [-1000, 7, -100, 9, -10, 11, 100, 13,1000]
    ,[-1000, 7, -100, 9, -10, 11, 100, 13     ]
    ,[None,  7, -100, 9, -10, 11, 100, 13,1000]
    ,[5,     7,    6, 9,  10, 11, 100, 13,1000]
    ,[-1000, 7, -100, 9, -10, 11,  -6, 13,  -5] ]
    print '\n'.join(str(i)+str(plf) for i,plf in enumerate(plfs))
    plpinit()
    for xval in range(6,15):
        for i , plf in enumerate(plfs) :
            nstr = 'plf_{}_x_{}'.format(i,xval)
            A = plpvar('v_'+nstr, plf)
            xv = xval
            if plf[0] == None : xv = max(xv, plf[1])
            if len(plf)%2 == 0 : xv = min(xv, plf[-1])
            plpeq('eq_' + nstr, [(-1, A),xv] )
    plpexit(xval)    
    plpresults()
    print 'end test1'

def test2():
    """Test force"""
    print '\n' + test2.__doc__
    plf = [-105, 7, -100, 9, -10, 11, 100, 13, 101]
    print '  '.join('{}:{}'.format('p' if i%2 else 's',val) for i, val in enumerate(plf))
    plfs = [
    ['slope'], [None, -20, 'slope'], [None, -20, 'slope',10] ]
    print '\n'.join(str(i)+str(plf) for i,plf in enumerate(plfs))
    plpinit()
    for slope in [ -106, -105, -104, -101, -100, -99, -11, -10, -9, 99, 100, 101, 102]:
        for i , plfy in enumerate(plfs) :
            nstr = 'plf_{}_s_{}'.format(i,slope)
            AA = plpvar('x_' + nstr, plf )
            sl = slope
            plfc = plfy[:]
            it = plfy.index('slope')
            plfc[it] = slope
            #print i, plfc, it
            if plf[0]<>None and len(plfc)%2 and plfc[-1]<plf[0] : plfc.append(1000)
            if plfc[0]<>None and len(plf)%2 and plf[-1]<plfc[0] : plfc = [None,-1000] + plfc
            BB = plpvar('y_' + nstr, plfc )
            plpeq('eq_' + nstr, [ (1,AA), (1,BB) ] )
    plpexit('slope')    
    plpresults()  
    print 'end slope test'
              
def test3():
    unitcost = [2111, 888,  88,  8, 0, -8, -88, -888, -2111]

    for uc in unitcost:
        plpinit()
        AA = plpvar('x' , [1, 10.5, 2] )
        BB = plpvar('y' , [None, 5, uc, 15] )
        plpeq('deq', [ (-1,AA) , (1,BB) ] )
        plpexit()
        AA.res()
        BB.res()        
        plpresults()
        print 'AA', AA.x, AA.force
        print 'BB', BB.x, BB.force        

def test4():
    """Test addplf"""
    print '\n' + test4.__doc__
    def doe(plf1,plf2,plfres):
        assert addplf(plf1,plf2)==plfres
    doe( [None,1] , [None,1] ,[None,1] )
    doe( [None,1] , [None,2] ,[None,1] )
    doe( [None,1,3] , [None,2] ,[None,2] )
    doe( [None,2] , [-4,1] ,[None,1] )
    doe( [-3,4,1,5] ,[-2,3,1,4,3] , [-5,3,-2,4,4,5] )
    doe( [-3,4,1,5,7] , [-2,3,1,4,3] , [-5,3,-2,4,4,5,10] )
    doe( [-3,4.0+1.0e-6,1,5,7] , [-2,3,1,4,3] , [-5,3,-2,4,4,5,10] )
    doe( [-2,3,1,4,3] , [-3,4,1,5,7] , [-5,3,-2,4,4,5,10] )
    print 'test addplf goed doorstaan'
    
if __name__ == "__main__":
    test1()
    test2()
#    test3()
    test4()
    timer.timerout()
