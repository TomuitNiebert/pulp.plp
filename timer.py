"""
timer
"""
import datetime
import sys
__version__ = '2016-12-23'

sna = {}
def timer(name):
    t = datetime.datetime.now()
    try    : t0, tot, keer = sna[name]
    except : t0, tot, keer = None, 0 , 0 #first time 
    # before action 
    if t0 == None : sna[name] = t, tot, keer
    # after action
    else          : sna[name] = None, tot + (t-t0).total_seconds(), keer + 1
    
def timerout():
    print '\n'.join('{:10} {:8.3f} {:2}x'.format(name,v[1],v[2]) for name, v in sna.items())
    print '{:19.3f}  total time'.format(sum(v[1] for name, v in sna.items()))

if __name__ == "__main__":
    import math
    def doe(naam):
        timer(naam)
        for i in range(1000000):
            a = math.sin(88)
        timer(naam)
    
    for j in range(2):
        doe('first')
        doe('second')
        doe('third')
    
    timerout()
    