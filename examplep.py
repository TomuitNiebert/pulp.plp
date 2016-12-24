"""
Consider a pipe between node A and B
  A----------------B
The maximum pressure is 70 bar and the minimum contractual pressure is 40 bar
Pressure cannot go below zero bar.
The required flow Q = 400
The pipe equation PA - PB = 0.1 Q
"""
import plpcom
print plpcom.__doc__
print plpcom.__version__
#help(plpcom)
from plpcom import plpinit, plpvar, plpeq, plpexit, plpresults
def setupexp():
    plpinit()
    # lower and upper pressure bound are 0 and 70
    # going below 40 is at high cost: 1e5
    # if the pressures are between 40 and 70 
    #   we like the result to be as hight as possible : -0.01
    PA = plpvar('pa',[None, 1, -1e5, 40, -0.01 , 70] )
    PB = plpvar('pb',[None, 1, -1e5, 40, -0.01 , 70] )
    # lower and upper flow bound are 0 and 400
    # we like very strongly the flow to be 400 : -1e3
    Q  = plpvar('aq' ,[None, 0, -1e3, 400] )
    Epipe = plpeq('eqpi', [(1,PA), (-1,PB), (-0.1,Q)] )
    return PA, PB, Q, Epipe

PA, PB, Q, Epipe = setupexp()
#PA.plf = [None, 50, -1e5, 80, -0.01 , 70]
plpexit(1)
print '               PA          PB           Q'
print 'x     {:11.2f} {:11.2f} {:11.2f} '.format(PA.x, PB.x, Q.x)
print 'force {:11.2f} {:11.2f} {:11.2f} '.format(PA.force, PB.force, Q.force)
plpresults()
plpresults(equat = True)
plpresults(equat = True, dosort = 'name')
plpresults(equat = True, dosort = 'force')
plpresults(equat = True, dosort = 'cost')
plpresults(minvalue = 90, maxnumber = 20, equat = True)
print 'ttt ',PA.lll
print 'ttt ',PB.lll
print 'ttt ',Q.lll
print 'ttt ',plpvar.lll
# the result is PA = 70 PB = 40 and Q = 300
# the flow is not on target.
# force:
#   if a variable is on a slope the force has the value of the slope
#   if a variable is on a point the force is between the valuaes of the ajacend slopes
# the result shows on pa (70) a positive force 1000
# and on pb (40) a negative force of -1000
# so if we enlarge the maximum pressure or lessen the minimum pressure 
# there will be more flow
#-------------------------------------------------------------------
# We could also make our "desire" to get a flow of 400 bigger
#
PA, PB, Q, Epipe = setupexp()
Q.plf = [None, 0, -1e6, 400]
plpexit(2)    
plpresults()

#another way to reach the same goal is the reduce the cost of going under 40
# the slope must be lower than the force
PA, PB, Q, Epipe = setupexp()
PB.plf = [None, 0, -9900, 40, -0.01 , 70]
plpexit(3)    
plpresults()

# Suppose that you want a flow of 800
PA, PB, Q, Epipe = setupexp()
Q.plf = [None, 0, -1e6, 800]
plpexit(4)    
plpresults()
plpresults(equat = True)
plpresults(equat = True, dosort = 'name', minvalue = 70)
plpresults(equat = True, dosort = 'force')
plpresults(equat = True, dosort = 'cost')

PA, PB, Q, Epipe = setupexp()
Q.plf = [None, 0, -1e6, 200]
plpexit(4)    
plpresults()
plpresults(equat = True)
plpresults(equat = True, dosort = 'name', minvalue = 70)
plpresults(equat = True, dosort = 'force', minvalue = 70)
plpresults(equat = True, dosort = 'cost', minvalue = 70)

# only a flow of 700 is reached because the pressure cannnot go below 0
#timerout()
print 1.84e-106**(1.0/32.65)
print 2000**32.65
values = [3,6,1,5]
index_min = min(xrange(len(values)), key=values.__getitem__)
print index_min
import plpcom
help(plpcom)