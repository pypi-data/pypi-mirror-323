from dataclasses import dataclass
from .roundit import (round_to_nearest, 
                      round_towards_plus_inf, 
                      round_towards_minus_inf, 
                      round_towards_zero, 
                      stochastic_rounding, 
                      stochastic_rounding_equal)
import jax.numpy as jnp
from jax import random
import gc

@dataclass
class customs:
    t: int
    emax: int
        
        
@dataclass
class options:
    t: int
    emax: int
    prec: int
    subnormal: bool
    rmode: bool
    flip: bool
    explim: bool
    p: float

        
from time import time

class chop(object):

    """
    Parameters
    ----------
    prec : str, default='s':
        The target arithmetic format.
    
    subnormal : boolean
        Whether or not support subnormal numbers are supported.
        If set `subnormal=False`, subnormals are flushed to zero.
        
    rmode : int, default=1
        The supported rounding modes include:
        1. Round to nearest using round to even last bit to break ties (the default).
        2. Round towards plus infinity (round up).
        3. Round towards minus infinity (round down).
        4. Round towards zero.
        5. Stochastic rounding - round to the next larger or next smaller
           floating-point number with probability proportional to the distance 
           to those floating-point numbers.
        6. Stochastic rounding - round to the next larger or next smaller 
           floating-point number with equal probability.

    flip : boolean, default=False
        Default is False; If ``flip`` is True, then each element
        of the rounded result has a randomly generated bit in its significand flipped 
        with probability ``p``. This parameter is designed for soft error simulation. 

    explim : boolean, default=True
        Default is True; If ``explim`` is False, then the maximal exponent for
        the specified arithmetic is ignored, thus overflow, underflow, or subnormal numbers
        will be produced only if necessary for the data type.  
        This option is designed for exploring low precisions independent of range limitations.

    p : float, default=0.5
        The probability ``p` for each element of the rounded result has a randomly
        generated bit in its significand flipped  when ``flip`` is True

    randfunc : callable, default=None
        If ``randfunc`` is supplied, then the random numbers used for rounding  will be generated 
        using that function in stochastic rounding (i.e., ``rmode`` of 5 and 6). Default is numbers
        in uniform distribution between 0 and 1, i.e., jnp.random.uniform.

    customs : dataclass, default=None
        If customs is defined, then use customs.t and customs.emax for floating point arithmetic.

    random_state : int, default=0
        Random seed set for stochastic rounding settings.

        
    Methods
    ----------
    chop(x):
        Method that convert ``x`` to the user-specific arithmetic format.
        
    """

    def __init__(self, prec='h', subnormal=None, rmode=1, flip=False, explim=1,
                 p=0.5, randfunc=None, customs=None, random_state=0):
        
        self.key = random.key(random_state)
        self.prec = prec
        
        if subnormal is not None:
            self.subnormal = subnormal
        else:
            if self.prec in {'b','bfloat16'}:
                self.subnormal = False
            else:
                self.subnormal = True
            
        self.rmode = rmode
        self.flip = flip
        self.explim = explim
        self.p = p
        
        self.randfunc = randfunc
        if self.rmode == 1:
            self._chop = _chop_round_to_nearest
            
        elif self.rmode == 2:
            self._chop = _chop_round_towards_plus_inf
            
        elif self.rmode == 3:
            self._chop = _chop_round_towards_minus_inf
            
        elif self.rmode == 4:
            self._chop = _chop_round_towards_zero
            
        elif self.rmode == 5:
            self._chop = _chop_stochastic_rounding
            
        elif self.rmode == 6:
            self._chop = _chop_stochastic_rounding_equal

        else:
            raise ValueError('Unsupported value of rmode.')

        if customs is not None:
            self.t = customs.t
            self.emax = customs.emax
            
        elif self.prec in {'h','half','fp16','b','bfloat16','s',
                   'single','fp32','d','double','fp64',
                   'q43','fp8-e4m3','q52','fp8-e5m2'}:
            if self.prec in {'q43','fp8-e4m3'}:
                self.t = 4
                self.emax = 7
            elif self.prec in {'q52','fp8-e5m2'}:
                self.t = 3
                self.emax = 15
            elif self.prec in {'h','half','fp16'}:
                self.t = 11
                self.emax = 15
            elif self.prec in {'b','bfloat16'}:
                self.t = 8
                self.emax = 127  
            elif self.prec in {'s','single','fp32'}:
                self.t = 24
                self.emax = 127
            elif self.prec in {'d','double','fp64'}:
                self.t = 53
                self.emax = 1023
        else:
            raise ValueError('Please enter valid prec value.')

        self.u = None
        
            
    def __call__(self, x):
        if str(x).isnumeric():
            raise ValueError('Chop requires real input values (not integer).')
        
        if not hasattr(x, "__len__"):
            x = jnp.array(x, ndmin=1)
            
        if hasattr(self, 'customs'):
            if self.rmode == 1:
                self.maxfraction = (x.dtype == 'float32')  * 11 + (x.dtype == 'float64')  * 25
            else:
                self.maxfraction = (x.dtype == 'float32')  * 23 + (x.dtype == 'float64') * 52
                
            if self.t > self.maxfraction:
                raise ValueError('Precision of the custom format must be at most')
                
        y = self.chop_wrapper(x.copy())
        return y
        

    
    def chop_wrapper(self, x):
        return self._chop(self.key, x, t=self.t, emax=self.emax, subnormal=self.subnormal, flip=self.flip, 
                                explim=self.explim, p=self.p)
    

    @property
    def options(self):
        return options(self.t, 
                       self.emax,
                       self.prec,
                       self.subnormal,
                       self.rmode,
                       self.flip,
                       self.explim,
                       self.p
                      )
    
    
    
def _chop_round_to_nearest(key, x, t, emax, subnormal=1, flip=0, 
          explim=1, p=0.5, randfunc=None, *argv, **kwargs):
              
    if randfunc is None:
        randfunc = lambda n: random.uniform(key, shape=n)

    emin = 1 - emax                # Exponent of smallest normalized number.
    xmin = 2**emin                 # Smallest positive normalized number.
    emins = emin + 1 - t           # Exponent of smallest positive subnormal number.
    xmins = pow(2, emins)          # Smallest positive subnormal number.

    _, e = jnp.frexp(jnp.abs(x)) 
    e = jnp.array(e - 1, ndmin=1)
    ktemp = (e < emin) & (e >= emins)

    if explim:
        k_sub = ktemp
        k_norm = ~ktemp
    else:
        k_sub = jnp.array([], dtype=bool)
        k_norm = jnp.full(ktemp.shape, True, dtype=bool)

    w = jnp.power(2.0, t-1-e[k_norm])
    x = x.at[k_norm].set(round_to_nearest(
        key=key, x=x[k_norm] * w, 
        flip=flip, p=p,
        t=t,
        randfunc=randfunc
    )) 

    x = x.at[k_norm].set(x[k_norm] / w) 

    if k_sub.size != 0:
        temp = emin-e[k_sub]
        t1 = t - jnp.fmax(temp, jnp.zeros(temp.shape))
        
        x = x.at[k_sub].set(round_to_nearest(
            key=key, x=x[k_sub] * jnp.power(2, t1-1-e[k_sub]), 
            flip=flip, p=p,
            t=t,
            randfunc=randfunc
        ) * jnp.power(2, e[k_sub]-(t1-1)))

        del temp, t1
        
    del w; gc.collect()

    if explim:
        xboundary = 2**emax * (2- 0.5 * 2**(1-t))
        x = x.at[x >= xboundary].set(jnp.inf)# Overflow to +inf.
        x = x.at[x <= -xboundary].set(-jnp.inf) # Overflow to -inf.
                
        # Round to smallest representable number or flush to zero.
        if subnormal == 0:
            min_rep = xmin
        else:
            min_rep = xmins

        k_small = jnp.abs(x) < min_rep
        
        if subnormal == 0:
            k_round = k_small & (jnp.abs(x) >= min_rep/2)
        else:
            k_round = k_small & (jnp.abs(x) > min_rep/2)
        
        x = x.at[k_round].set(jnp.sign(x[k_round]) * min_rep)
        x = x.at[k_small & ~k_round].set(0)

    return x
    
    
    
    

def _chop_round_towards_plus_inf(key, x, t, emax, subnormal=1, flip=0, 
          explim=1, p=0.5, randfunc=None, *argv, **kwargs):
              
    if randfunc is None:
        randfunc = lambda n: random.uniform(key, shape=n)
        
    emin = 1 - emax                # Exponent of smallest normalized number.
    xmin = 2**emin                 # Smallest positive normalized number.
    emins = emin + 1 - t           # Exponent of smallest positive subnormal number.
    xmins = pow(2, emins)          # Smallest positive subnormal number.
    xmax = pow(2,emax) * (2-2**(1-t))

    _, e = jnp.frexp(jnp.abs(x)) 
    e = jnp.array(e - 1, ndmin=1)
    ktemp = (e < emin) & (e >= emins)
              
    if explim:
        k_sub = ktemp
        k_norm = ~ktemp
    else:
        k_sub = jnp.array([], dtype=bool)
        k_norm = jnp.full(ktemp.shape, True, dtype=bool)

    w = jnp.power(2.0, t-1-e[k_norm])
    x = x.at[k_norm].set(round_towards_plus_inf(
        key=key, x=x[k_norm] * w, 
        flip=flip, p=p,
        t=t,
        randfunc=randfunc
    ))
    x = x.at[k_norm].set(x[k_norm] / w) 
    
    if k_sub.size != 0:
        temp = emin-e[k_sub]
        t1 = t - jnp.fmax(temp, jnp.zeros(temp.shape))
        
        x = x.at[k_sub].set(round_towards_plus_inf(
            key=key, x=x[k_sub] * jnp.power(2, t1-1-e[k_sub]), 
            flip=flip, p=p,
            t=t,
            randfunc=randfunc
        ) * jnp.power(2, e[k_sub]-(t1-1)))
        del temp, t1
        
    del w; gc.collect()
        
    if explim:
        x = x.at[x > xmax].set(jnp.inf)
        x = x.at[(x < -xmax) & (x != -jnp.inf)].set(-xmax)
                
        # Round to smallest representable number or flush to zero.
        if subnormal == 0:
            min_rep = xmin
        else:
            min_rep = xmins

        k_small = jnp.abs(x) < min_rep
        
        k_round = k_small & (x > 0) & (x < min_rep)
        x = x.at[k_round].set(min_rep)
        x = x.at[k_small & ~k_round].set(0)
                
    return x



def _chop_round_towards_minus_inf(key, x, t, emax, subnormal=1, flip=0, 
          explim=1, p=0.5, randfunc=None, *argv, **kwargs):
              
    if randfunc is None:
        randfunc = lambda n: random.uniform(key, shape=n)
        
    emin = 1 - emax                # Exponent of smallest normalized number.
    xmin = 2**emin                 # Smallest positive normalized number.
    emins = emin + 1 - t           # Exponent of smallest positive subnormal number.
    xmins = pow(2, emins)          # Smallest positive subnormal number.
    xmax = pow(2,emax) * (2-2**(1-t))
    
    _, e = jnp.frexp(jnp.abs(x)) 
    e = jnp.array(e - 1, ndmin=1)
    ktemp = (e < emin) & (e >= emins)
              
    if explim:
        k_sub = ktemp
        k_norm = ~ktemp
    else:
        k_sub = jnp.array([], dtype=bool)
        k_norm = jnp.full(ktemp.shape, True, dtype=bool)

    w = jnp.power(2.0, t-1-e[k_norm])

    x = x.at[k_norm].set(round_towards_minus_inf(
        key=key, x=x[k_norm] * w, 
        flip=flip, p=p,
        t=t,
        randfunc=randfunc
    ))

    x = x.at[k_norm].set(x[k_norm] / w) 
    
    if k_sub.size != 0:
        temp = emin-e[k_sub]
        t1 = t - jnp.fmax(temp, jnp.zeros(temp.shape))
        
        x = x.at[k_sub].set(round_towards_minus_inf(
            key=key, x=x[k_sub] * jnp.power(2, t1-1-e[k_sub]), 
            flip=flip, p=p,
            t=t,
            randfunc=randfunc
        ) * jnp.power(2, e[k_sub]-(t1-1)))
        del temp, t1
        
    del w; gc.collect()
        
    if explim:
        x = x.at[(x > xmax) & (x != jnp.inf)].set(xmax)
        x = x.at[x < -xmax].set(-jnp.inf)
        
        # Round to smallest representable number or flush to zero.
        if subnormal == 0:
            min_rep = xmin
        else:
            min_rep = xmins

        k_small = jnp.abs(x) < min_rep

        k_round = k_small & (x < 0) & (x > -min_rep)
        x = x.at[k_round].set(-min_rep)
        x = x.at[k_small & ~k_round].set(0)
                
    return x



def _chop_round_towards_zero(key, x, t, emax, subnormal=1, flip=0, 
          explim=1, p=0.5, randfunc=None, *argv, **kwargs):
              
    if randfunc is None:
        randfunc = lambda n: random.uniform(key, shape=n)
        
    emin = 1 - emax                # Exponent of smallest normalized number.
    xmin = 2**emin                 # Smallest positive normalized number.
    emins = emin + 1 - t           # Exponent of smallest positive subnormal number.
    xmins = pow(2, emins)          # Smallest positive subnormal number.
    xmax = pow(2,emax) * (2-2**(1-t))
    
    _, e = jnp.frexp(jnp.abs(x)) 
    e = jnp.array(e - 1, ndmin=1)
    ktemp = (e < emin) & (e >= emins)
              
    if explim:
        k_sub = ktemp
        k_norm = ~ktemp
    else:
        k_sub = jnp.array([], dtype=bool)
        k_norm = jnp.full(ktemp.shape, True, dtype=bool)

    w = jnp.power(2.0, t-1-e[k_norm])

    x = x.at[k_norm].set(round_towards_zero(
        key=key, x=x[k_norm] * w, 
        flip=flip, p=p,
        t=t,
        randfunc=randfunc
    ))
    
    x = x.at[k_norm].set(x[k_norm] / w) 
    
    if k_sub.size != 0:
        temp = emin-e[k_sub]
        t1 = t - jnp.fmax(temp, jnp.zeros(temp.shape))
        
        x= x.at[k_sub].set(round_towards_zero(
            key=key, x=x[k_sub] * jnp.power(2, t1-1-e[k_sub]), 
            flip=flip, p=p,
            t=t,
            randfunc=randfunc
        ) * jnp.power(2, e[k_sub]-(t1-1)))
        del temp, t1
        
    del w; gc.collect()
        
    if explim:
        x = x.at[(x > xmax) & (x != jnp.inf)].set(xmax)
        x = x.at[(x < -xmax) & (x != -jnp.inf)].set(-xmax)
                
        # Round to smallest representable number or flush to zero.
        if subnormal == 0:
            min_rep = xmin
        else:
            min_rep = xmins

        k_small = jnp.abs(x) < min_rep
        x = x.at[k_small].set(0)
                
    return x



def _chop_stochastic_rounding(key, x, t, emax, subnormal=1, flip=0, 
          explim=1, p=0.5, randfunc=None, *argv, **kwargs):
              
    if randfunc is None:
        randfunc = lambda n: random.uniform(key, shape=n)
        
    emin = 1 - emax                # Exponent of smallest normalized number.
    xmin = 2**emin                 # Smallest positive normalized number.
    emins = emin + 1 - t           # Exponent of smallest positive subnormal number.
    xmins = pow(2, emins)          # Smallest positive subnormal number.
    xmax = pow(2,emax) * (2-2**(1-t))
    
    _, e = jnp.frexp(jnp.abs(x)) 
    e = jnp.array(e - 1, ndmin=1)
    ktemp = (e < emin) & (e >= emins)
              
    if explim:
        k_sub = ktemp
        k_norm = ~ktemp
    else:
        k_sub = jnp.array([], dtype=bool)
        k_norm = jnp.full(ktemp.shape, True, dtype=bool)

    w = jnp.power(2.0, t-1-e[k_norm])

    x = x.at[k_norm].set(stochastic_rounding(
        key=key, x=x[k_norm] * w, 
        flip=flip, p=p,
        t=t,
        randfunc=randfunc
    ))
    
    x = x.at[k_norm].set(x[k_norm] / w) 
    
    if k_sub.size != 0:
        temp = emin-e[k_sub]
        t1 = t - jnp.fmax(temp, jnp.zeros(temp.shape))
        
        x = x.at[k_sub].set(stochastic_rounding(
            key=key, x=x[k_sub] * jnp.power(2, t1-1-e[k_sub]), 
            flip=flip, p=p,
            t=t,
            randfunc=randfunc
        ) * jnp.power(2, e[k_sub]-(t1-1)))
        del temp, t1
        
    del w; gc.collect()
        
    if explim:
        x = x.at[(x > xmax) & (x != jnp.inf)].set(xmax)
        x = x.at[(x < -xmax) & (x != -jnp.inf)].set(-xmax)
        
        # Round to smallest representable number or flush to zero.
        if subnormal == 0:
            min_rep = xmin
        else:
            min_rep = xmins

        k_small = jnp.abs(x) < min_rep
        x = x.at[k_small].set(0)
                
    return x



def _chop_stochastic_rounding_equal(key, x, t, emax, subnormal=1, flip=0, 
          explim=1, p=0.5, randfunc=None, *argv, **kwargs):
              
    if randfunc is None:
        randfunc = lambda n: random.uniform(key, shape=n)
        
    emin = 1 - emax                # Exponent of smallest normalized number.
    xmin = 2**emin                 # Smallest positive normalized number.
    emins = emin + 1 - t           # Exponent of smallest positive subnormal number.
    xmins = pow(2, emins)          # Smallest positive subnormal number.
    
    _, e = jnp.frexp(jnp.abs(x)) 
    e = jnp.array(e - 1, ndmin=1)
    ktemp = (e < emin) & (e >= emins)
              
    if explim:
        k_sub = ktemp
        k_norm = ~ktemp
    else:
        k_sub = jnp.array([], dtype=bool)
        k_norm = jnp.full(ktemp.shape, True, dtype=bool)

    w = jnp.power(2.0, t-1-e[k_norm])

    x = x.at[k_norm].set(stochastic_rounding_equal(
        key=key, x=x[k_norm] * w, 
        flip=flip, p=p,
        t=t,
        randfunc=randfunc
    ))
    
    x = x.at[k_norm].set(x[k_norm] / w) 
    
    if k_sub.size != 0:
        temp = emin-e[k_sub]
        t1 = t - jnp.fmax(temp, jnp.zeros(temp.shape))
        
        x = x.at[k_sub].set(stochastic_rounding_equal(
            key=key, x=x[k_sub] * jnp.power(2, t1-1-e[k_sub]), 
            flip=flip, p=p,
            t=t,
            randfunc=randfunc
        ) * jnp.power(2, e[k_sub]-(t1-1)))
        del temp, t1
        
    del w; gc.collect()
        
    if explim:
        xboundary = 2**emax * (2- 0.5 * 2**(1-t))
        x = x.at[x >= xboundary].set(jnp.inf)    # Overflow to +inf.
        x = x.at[x <= -xboundary].set(-jnp.inf)  # Overflow to -inf.
                
        # Round to smallest representable number or flush to zero.
        if subnormal == 0:
            min_rep = xmin
        else:
            min_rep = xmins

        k_small = jnp.abs(x) < min_rep
        x = x.at[k_small].set(0)

    return x

