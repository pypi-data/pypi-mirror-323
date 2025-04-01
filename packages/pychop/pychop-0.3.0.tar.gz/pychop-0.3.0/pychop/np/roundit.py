import numpy as np

                      
def round_to_nearest(x, flip=0, p=0.5, t=24, **kwargs):
    y = np.abs(x)
    inds = (y - (2 * np.floor(y / 2))) == 0.5
    y[inds] = y[inds] - 1
    u = np.round(y)
    u[u == -1] = 0 # Special case, negative argument to ROUND.
    y = np.sign(x) * u
    
    if flip:
        sign = lambda x: np.sign(x) + (x==0)
        temp = np.random.randint(low=0, high=1, size=y.shape)
        k = temp <= p # Indices of elements to have a bit flipped.
        if np.any(k):
            u = np.abs(y[k])
            b = np.random.randint(low=1, high=t-1, size=u.shape) 
            # Flip selected bits.
            u = np.bitwise_xor(np.int32(u), np.power(2, b-1))
            y[k] = sign(y[k])*u
    
    return y



def round_towards_plus_inf(x, flip=0, p=0.5, t=24, **kwargs):
    y = np.ceil(x)
            
    if flip:
        sign = lambda x: np.sign(x) + (x==0)
        temp = np.random.randint(low=0, high=1, size=y.shape)
        k = temp <= p # Indices of elements to have a bit flipped.
        if np.any(k):
            u = np.abs(y[k])
            b = np.random.randint(low=1, high=t-1, size=u.shape) 
            # Flip selected bits.
            u = np.bitwise_xor(np.int32(u), np.power(2, b-1))
            y[k] = sign(y[k])*u
    
    return y



def round_towards_minus_inf(x, flip=0, p=0.5, t=24, **kwargs):
    y = np.floor(x)
            
    if flip:
        sign = lambda x: np.sign(x) + (x==0)
        temp = np.random.randint(low=0, high=1, size=y.shape)
        k = temp <= p # Indices of elements to have a bit flipped.
        if np.any(k):
            u = np.abs(y[k])
            b = np.random.randint(low=1, high=t-1, size=u.shape) 
            # Flip selected bits.
            u = np.bitwise_xor(np.int32(u), np.power(2, b-1))
            y[k] = sign(y[k])*u
    
    return y


def round_towards_zero(x, flip=0, p=0.5, t=24, **kwargs):
    y = ((x >= 0) | (x == -np.inf)) * np.floor(x) + ((x < 0) | (x == np.inf)) * np.ceil(x)
            
    if flip:
        sign = lambda x: np.sign(x) + (x==0)
        temp = np.random.randint(low=0, high=1, size=y.shape)
        k = temp <= p # Indices of elements to have a bit flipped.
        if np.any(k):
            u = np.abs(y[k])
            b = np.random.randint(low=1, high=t-1, size=u.shape) 
            # Flip selected bits.
            u = np.bitwise_xor(np.int32(u), np.power(2, b-1))
            y[k] = sign(y[k])*u
    
    return y



def stochastic_rounding(x, flip=0, p=0.5, t=24, randfunc=None):
    y = np.abs(x)
    frac = y - np.floor(y)
 
    if np.count_nonzero(frac) == 0:
        y = x 
    else:   
        sign = lambda x: np.sign(x) + (x==0)
        rnd = randfunc(frac.shape)
        j = rnd <= frac
            
        y[j] = np.ceil(y[j])
        y[~j] = np.floor(y[~j])
        y = sign(x)*y
                
        if flip:
            
            temp = np.random.randint(low=0, high=1, size=y.shape)
            k = temp <= p # Indices of elements to have a bit flipped.
            if np.any(k):
                u = np.abs(y[k])
                b = np.random.randint(low=1, high=t-1, size=u.shape) 
                # Flip selected bits.
                u = np.bitwise_xor(np.int32(u), np.power(2, b-1))
                y[k] = sign(y[k])*u
        
    return y



def stochastic_rounding_equal(x, flip=0, p=0.5, t=24, randfunc=None):
    y = np.abs(x)
    frac = y - np.floor(y)
    
    if np.count_nonzero(frac) == 0:
        y = x 
    else:   
        # Uniformly distributed random numbers
        sign = lambda x: np.sign(x) + (x==0)
        rnd = randfunc(frac.shape)
        j = rnd <= 0.5
        y[j] = np.ceil(y[j])
        y[~j] = np.floor(y[~j])
        y = sign(x)*y
            
    if flip:
        sign = lambda x: np.sign(x) + (x==0)
        temp = np.random.randint(low=0, high=1, size=y.shape)
        k = temp <= p # Indices of elements to have a bit flipped.
        if np.any(k):
            u = np.abs(y[k])
            b = np.random.randint(low=1, high=t-1, size=u.shape) 
            # Flip selected bits.
            u = np.bitwise_xor(np.int32(u), np.power(2, b-1))
            y[k] = sign(y[k])*u
    
    return y



def roundit_test(x, rmode=1, flip=0, p=0.5, t=24, randfunc=None):
    if randfunc is None:
        randfunc = lambda n: np.random.randint(0, 1, n)
            

    if rmode == 1:
        y = np.abs(x)
        u = np.round(y - ((y % 2) == 0.5))
        
        u[u == -1] = 0 # Special case, negative argument to ROUND.
            
        y = np.sign(x) * u
        
    elif rmode == 2:
        y = np.ceil(x)
        
    elif rmode == 3:
        y = np.floor(x)
        
    elif rmode == 4:
        y = ((x >= 0) | (x == -np.inf)) * np.floor(x) + ((x < 0) | (x == np.inf)) * np.ceil(x)
        
    elif rmode == 5 | 6:
        y = np.abs(x)
        frac = y - np.floor(y)
        k = np.nonzero(frac != 0)[0]
        
        if len(k) == 0:
            y = x 
        else:   
            # Uniformly distributed random numbers
            
            rnd = randfunc(len(k))
            
            vals = frac[k]
            
            if len(vals.shape) == 2:
                vals = return_column_order(vals)
            else:
                pass
            
            if rmode == 5: # Round up or down with probability prop. to distance.
                j = rnd <= vals
            elif rmode == 6: # Round up or down with equal probability.       
                j = rnd <= 0.5
                
            y[k[j==0]] = np.ceil(y[k[j==0]])
            y[k[j!=0]] = np.floor(y[k[j!=0]])
            y = sign(x)*y
            
    else:
        raise ValueError('Unsupported value of rmode.')
            
    if flip:
        sign = lambda x: np.sign(x) + (x==0)
        temp = np.random.randint(low=0, high=1, size=y.shape)
        k = temp <= p # Indices of elements to have a bit flipped.
        if np.any(k):
            u = np.abs(y[k])
            
            # Random bit flip in significand.
            # b defines which bit (1 to p-1) to flip in each element of y.
            # Using SIZE avoids unwanted implicit expansion.
            # The custom (base 2) format is defined by options.params, which is a
            # 2-vector [t,emax] where t is the number of bits in the significand
            # (including the hidden bit) and emax is the maximum value of the
            # exponent.  

            
            b = np.random.randint(low=1, high=t-1, size=u.shape) 
            # Flip selected bits.
            u = np.bitwise_xor(np.int32(u), np.power(2, b-1))
            y[k] = sign(y[k])*u
    
    return y
    
    
    
   
    
    
    
def return_column_order(arr):
    return arr.T.reshape(-1)
