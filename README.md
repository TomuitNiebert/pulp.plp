# pulp.plp
Convex Piecewise Linear Programming frontend to PULP

Convex piecewise linear programming is a small and useful extension to linear programming.
Two Python modules will allow easy formulation of a PLP problem with variables and equations.
The CBC solver is accessed via the PULP package.
For each variable there is a plf consisting of slopes and points like [ s0 , p1 , s2 , p3 ]

#Small example
Consider a pipe between node A and B.
The maximum pressure is 70 bar and the minimum contractual pressure is 40 bar.
Pressure cannot go below zero bar.
The contractual flow Q = 400. The pipe equation P A − P B = 0.1 x Q.
With Q = 400 it can be calculated that P A − P B = 40, while the maximum pressure drop is 30 bar.
So this problem is infeasible, when we apply the constraints and equate the flow to 400.

`from plpcom import plpinit, plpvar, plpeq, plpexit, plpresults
plpinit()`
###variables
`PA = plpvar(’pa’,[None, 0, -1e5, 40, -0.01 , 70] )
PB = plpvar(’pb’,[None, 0, -1e5, 40, -0.01 , 70] )
Q = plpvar(’q’ ,[None, 0, -1e3, 400] )`
###equation
`Epipe = plpeq(’epi’, [(1,PA), (-1,PB), (-0.1,Q)] )`
###do-it
'plpexit(1)

print ’ PA PB Q’
print ’x {:11.2f} {:11.2f} {:11.2f} ’.format(PA.x, PB.x, Q.x)
print ’force {:11.2f} {:11.2f} {:11.2f} ’.format(PA.force, PB.force, Q.force)
'
###The result is
`         PA        PB        Q
x        70.00     40.00   300.00
force 10000.00 -10000.00 -1000.00'
