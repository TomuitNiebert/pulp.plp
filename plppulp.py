"""
Convex Piecewise Linear Programming interface to PULP.

written by Tom van der Hoeven.
"""
from pulp import *
solvexe = 'cbc'
#solvexe = 'glpk'
__version__ = '2016-12-23'

def None0(a): return 0.0 if a == None else a

def zetlpvar(self):
    name = self.name
    plf = self.plf
    if type(plf) <> list : plf = [plf]
    if len(plf) == 1 : # 1 slope
        self.lp = LpVariable(name)
        plpinfo.totcost.append( (plf[0] ,self.lp) )
        return

    lb = None if plf[0]<>None else plf[ 1]
    ub = None if len(plf)%2   else plf[-1]
    islopes = [i for i, val in enumerate(plf) if i%2 == 0 and val<>None]

    self.lp = minlp = LpVariable(name, lb, ub)
    if islopes == [] : return # 1 point
        
    islopemin = min(islopes, key=lambda x : abs(plf[x]))
    ip = islopemin-1 if plf[islopemin]>0 else islopemin+1
    if ip<0 : ip +=2
    if ip>len(plf)-1 : ip -=2
    #print plf, islopemin, ip
    xo = plf[ip]

    self.islopemin = islopemin
    selfcost = []
    self.vslope = plf[:]

    for i in islopes :
        if i<islopemin:
            vslope = LpVariable(name + '_' + str(i), 0)
            plpinfo.prob += -vslope <= minlp - plf[i+1] , vslope.name + '_' + str(islopemin)
            selfcost.append( ( -(plf[i] - plf[i+2]) , vslope) )
        elif i == islopemin :
            vslope = minlp
            selfcost += [ (plf[i] ,self.lp), - plf[i] * xo]
        elif i>islopemin:
            vslope = LpVariable(name + '_' + str(i), 0)
            plpinfo.prob += vslope >= minlp - plf[i-1] , vslope.name + '_' + str(islopemin)
            selfcost.append( (  (plf[i] - plf[i-2]) , vslope) )
        self.vslope[i]= vslope
    plpinfo.totcost += selfcost

def vares(self): 
    #print self.name, self.lp.varValue, self.lp.dj,self.lp.__dict__
    x  = None0(self.lp.varValue)
    dj = None0(self.lp.dj)
    plf = self.plf if type(self.plf) == list else [self.plf]
    lenplf = len(plf)
    if lenplf == 1 : # 1 slope
        force = float(plf[0]) ; 
        ix = 0 ;
        return x, force, ix

    islopes = [i for i, val in enumerate(plf) if i%2 == 0 and val<>None]
    if islopes == [] : # 1 point
        force = - dj
        ix = 1
        return x, force, ix

    # find ix
    ipoints = [i for i, val in enumerate(plf) if i%2]
    ipoint = min(ipoints, key=lambda i : abs(plf[i]-x))
    if abs(plf[ipoint]-x) < 1.0e-7 * max(1,abs(x)+abs(plf[ipoint])): ix = ipoint
    elif x<plf[ipoint] : ix = ipoint - 1
    else               : ix = ipoint + 1

    # alternative: take dual variable into account when looking for ix

    # find force
    islopemin = self.islopemin
    #print self.name, self.plf, x, ix,islopemin
    if ix%2: #point
        if   ix==1 and plf[0]==None : force = plf[2] - dj
        elif ix == lenplf-1         : force = plf[lenplf-2] - dj
        elif ix<islopemin           : force = plf[ix-1] + None0(self.vslope[ix-1].dj)
        else                        : force = plf[ix+1] - None0(self.vslope[ix+1].dj)
    else                        : force = float(plf[ix])
    
    return x, force, ix
    
def zetlpeq(self):
    name = self.name
    coefvar = self.coefvar
    const = sum(a for a in coefvar if not isinstance(a,tuple))
    cv = [ ( a[1].lp , a[0] ) for a in coefvar if isinstance(a,tuple) and a[0]<>0.0]
    aa = LpAffineExpression(cv) + const
    plpinfo.prob += aa == 0 , name

def eqres(self):
    name = self.name.replace('-','_')
    c = plpinfo.prob.constraints[name]
    return None0(c.slack), None0(c.pi)

class plpinfo():
    pass

def init(pname, plpvar, plpeq ):
    plpinfo.pname = pname
    plpinfo.cost = LpVariable('cost')
    plpinfo.prob = LpProblem(pname, LpMinimize)
    plpinfo.prob += plpinfo.cost,'Total cost'
    plpinfo.totcost = []
    for va in plpvar : zetlpvar(va)
    for eq in plpeq  : zetlpeq(eq)
    const = sum(a for a in plpinfo.totcost if not isinstance(a,tuple))
    #print plpvar.totcost,const
    plpinfo.totcost = [(a[1],a[0]) for a in plpinfo.totcost if isinstance(a,tuple) and a[0]<>0.0]
    #print plpinfo.totcost,const
    plpinfo.prob += plpinfo.cost == const + LpAffineExpression(plpinfo.totcost) , 'costeq'

def maaksom():
    if solvexe == 'glpk':# or it>1:
        glpk_solver = GLPK_CMD(
        #path='C:\\Users\\Tom\\Documents\\werk\\LP\\glpk-4.55\\w32\\glpsol.exe',
        path='C:\\GLPK\\winglpk-4.60\\glpk-4.60\\w64\\glpsol.exe',
        keepFiles=1, msg = 0)#,options =['nopresol'])
        #print 'glpk_solver.available(ii)', glpk_solver.available()
        glpk_solver.actualSolve(plpinfo.prob)
    else :
        cbc_solver = PULP_CBC_CMD(keepFiles=1
        #, msg = 1
        , maxSeconds=2)#, presolve = 10)
        #, options =['vector on'])#,'scaling off'])
        cbc_solver.solve_CBC(plpinfo.prob, use_mps=False)
    lpcost   = plpinfo.lpcost   = plpinfo.cost.varValue
    lpstatus = plpinfo.lpstatus = LpStatus[plpinfo.prob.status]
    return lpcost, lpstatus

if __name__ == "__main__":
    print 'pulp version is:',VERSION
    #print PULP_CBC_CMD().getSolverVersion()
    pulp.pulpTestAll()
