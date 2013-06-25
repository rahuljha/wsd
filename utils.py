def singularize(word):
    """Return the singular form of a word
 
    >>> singularize('rabbits')
    'rabbit'
    >>> singularize('potatoes')
    'potato'
    >>> singularize('leaves')
    'leaf'
    >>> singularize('knives')
    'knife'
    >>> singularize('spies')
    'spy'
    """
    sing_rules = [lambda w: w[-3:] == 'ies' and w[:-3] + 'y',
                  lambda w: w[-4:] == 'ives' and w[:-4] + 'ife',
                  lambda w: w[-3:] == 'ves' and w[:-3] + 'f',
                  lambda w: w[-2:] == 'es' and w[:-2],
                  lambda w: w[-1:] == 's' and w[:-1],
                  lambda w: w,
                  ]
    word = word.strip()
    singleword = [f(word) for f in sing_rules if f(word) is not False][0]
    return singleword
 

def flatten_list(l):
    return [item for sublist in l for item in sublist]
