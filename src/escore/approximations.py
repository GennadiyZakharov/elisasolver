'''
Created on 01.11.2013

@author: gena
'''
from __future__ import division,print_function
import numpy as np
import numpy.random as npr
import matplotlib.pyplot as plt
from scipy.optimize import leastsq
from string import ascii_uppercase

class Approximation(object):
    '''
    Abstract class for approximation function 
    '''
    name = 'Abstract'
    referenceCount = -1
    
    def __init__(self):
        self.p = None
    
    def makeGuess(self,x,y):
        '''
        Overridable function to make initial parameter guess
        '''
        pass
    
    def eval(self, x):
        '''
        return function value with stored coefficients
        '''
        return self.evalFunc(x, self.p)
    
    def invEval(self, y):
        '''
        return value for inverse function with stored coefficients
        '''
        return self.invEvalFunc(y, self.p)
    
    def evalFunc(self, x,p):
        '''
        return function value with given coefficients
        '''
        pass
    
    def invEvalFunc(self, y,p):
        '''
        return value for inverse function with stored coefficients
        '''
        pass
    
    def isFitted(self):
        return self.p is not None
    
    def fitPvals(self, x,y):
        '''
        Fit coefficients according to data x and y
        '''
        def residualsAbs(p, x, y):
            """Deviations of data from fitted curve"""
            err = y-self.evalFunc(x, p)
            return err
        # Create p0
        print('Fitting coefficients...')
        self.p = self.makeGuess(x, y)
        print('Guessed coefficients: ',self.p)
        # Fit equation using least squares optimization
        self.p,cov,infodict,mesg,ier = leastsq(residualsAbs,self.p,args=(x,y),
                                          full_output=True)
        print('Fitted coefficients: ',self.p)
        ss_err=(infodict['fvec']**2).sum()
        ss_tot=((y-y.mean())**2).sum()
        self.rsquared=1-(ss_err/ss_tot)
        maxx=max(x)
        minx=min(x)
        xsize=maxx-minx
        xstart=minx-0.1*xsize
        xstop=maxx+0.1*xsize
        xx=np.linspace(minx, maxx, 50)
        plt.plot(xx,self.eval(xx),'-',x,y,'o')
        plt.xlim((xstart, xstop))
        plt.title('Least-squares {} fit, R^2={:.3f}'.format(self.name,self.rsquared))
        plt.legend([self.name+' fit', 'Reference'], loc='upper left')
        params = ascii_uppercase[:len(self.p)]
        ycor = max(y)
        ystep = (ycor-min(y))/8
        for i, (param, est) in enumerate(zip(params, self.p)):
            plt.text(minx, ycor*0.8-i*ystep, 'est({}) = {:.3f}'.format(param, est))
        self.fitPlot=plt

class Linear(Approximation):
    '''
    Simple linear approximation
    '''  
    name = 'Linear'
    referenceCount = 2
    
    def evalFunc(self, x, p):
        A,B = p
        return  A*x+B
    
    def invEvalFunc(self, y,p):
        A,B = p
        return (y-B)/A
    
    def makeGuess(self,x,y):
        A = (y[-1]-y[1])/(x[-1]-x[1])
        return A,(y[1]-A*x[1])
     
class Logistic4(Approximation):
    '''
    4-parametric logistic function approximation
    '''
    name = '4PL'
    referenceCount = 4
    
    def evalFunc(self, x, p):
        A,B,C,D = p
        return ((A-D)/(1.0+((x/C)**B))) + D
    
    def invEvalFunc(self, y,p):
        A,B,C,D = p
        if y<=A:
            return 0
        if y>=D:
            return np.Inf
        return C*( ( (D-A)/(D-y) -1.0 )**(1/B) )
    
    def makeGuess(self,x,y):
        return y.min(),1.0,x.mean(),y.max()
    
class Logistic5(Approximation):
    '''
    5-parametric  logistic function approximation
    '''  
    name = '5PL'
    referenceCount = -5
    
    def evalFunc(self, x, p):
        A,B,C,D,E = p
        return  ( (A-D)/( (1.0+((x/C)**B))**E ) ) + D
    
    def invEvalFunc(self, y,p):
        A,B,C,D,E = p
        if y<=A:
            return 0
        if y>=D:
            return np.Inf
        return C*( ( ( (D-A)/(D-y)  )**(1/E) -1.0 )**(1/B) )
    
    def makeGuess(self,x,y):
        return y.min(),1.0,x.mean(),y.max(),1.0
        
    
approximations = [Linear,Logistic4,Logistic5]

def indexByName(name):
    for index in range(len(approximations)) :
        if name == approximations[index].name :
            return index
#=========================================================================
def main():
    def testApproximation(approximation, x,p,noise,name='function',comment=''):
        y_true = approximation.evalFunc(x, p)
        y_meas = y_true + noise
        approximation.fitPvals(x, y_meas)
        fitPlot = approximation.fitPlot
        fitPlot.show()
        # Plot results
        '''
        plt.plot(x,approximation.eval(x),x,y_meas,'o',x,y_true)
        plt.title('Least-squares {} fit to noisy data, '.format(name)+comment)
        plt.legend(['Fit', 'Noisy', 'True'], loc='upper left')
        params = ascii_uppercase[:len(p)]
        for i, (param, actual, est) in enumerate(zip(params, p, approximation.p)):
            plt.text(10, 3-i*0.5, '%s = %.2f, est(%s) = %.2f' % (param, actual, param, est))
        plt.show()
        '''
    
    x = np.linspace(1,20,20)
    noise = npr.randn(len(x))
    logistic4 = Logistic4()
    logistic5 = Logistic5()
    p4=(0.5,2.5,10,7.3)
    p5=(0.5,2.5,10,7.3,1.2)
    for noiseLevel in (0.02,0.1,0.3) :
        testApproximation(logistic4, x, p4,noise*noiseLevel,'4PL','noiseLevel={}'.format(noiseLevel))
        testApproximation(logistic5, x, p5,noise*noiseLevel,'5PL','noiseLevel={}'.format(noiseLevel))
    
if __name__ == '__main__':
    main()
