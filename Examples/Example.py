"""
LP problem in PLP clothes
  min -4*x1 -   x2 - 3*x3
-----------------------------------------------------------------
       2*x1   +     x2   +     x3    +   x4               = 10
       2*x1   +     x2   +     x3           +   x5        = 12
       2*x1   +   2*x2   +   4*x3                  +   x6 = 20
-----------------------------------------------------------------
      0<=x1<=4   0<=x2<=3   0<=x3<=1  0<=x4  0<=x5  0<=x6
-----------------------------------------------------------------
result should be x1=4 ; x2=1 ; x3=1 ; x4=0 ; x5 = 2 ; x6=6
The piesewise linear functions for the six variables are
plf1 = (p, s, p) = (0, -4, 4)
plf2 = (p, s, p) = (0, -1, 3)
plf3 = (p, s, p) = (0, -3, 1)
plf4 = (p, s) = (0, 0)
plf5 = (p, s) = (0, 0)
plf6 = (p, s) = (0, 0)
"""
import plpcom
def setupex1():
    plpcom.plpinit()
    A1 = plpcom.plpvar('x1',[None, 0, -4, 4] )
    A2 = plpcom.plpvar('x2',[None, 0, -1, 3] )
    A3 = plpcom.plpvar('x3',[None, 0, -3, 1] )
    A4 = plpcom.plpvar('x4',[None, 0, 0] )
    A5 = plpcom.plpvar('x5',[None, 0, 0] )
    A6 = plpcom.plpvar('x6',[None, 0, 0] )
    
    E1 = plpcom.plpeq('eqa', [(2,A1), (1,A2), (1,A3), (1,A4), -10] )
    E2 = plpcom.plpeq('eqb', [(2,A1), (1,A2), (1,A3), (1,A5), -12] )
    E2 = plpcom.plpeq('eqc', [(2,A1), (2,A2), (4,A3), (1,A6), -20] )

setupex1()
plpcom.plpexit(5)    
plpcom.megakrachten()
