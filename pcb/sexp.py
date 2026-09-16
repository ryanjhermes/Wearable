def parse(t):
    i=0; n=len(t)
    def rd():
        nonlocal i
        while i<n and t[i] in ' \t\r\n': i+=1
        if t[i]=='(':
            i+=1; out=[]
            while True:
                while i<n and t[i] in ' \t\r\n': i+=1
                if t[i]==')': i+=1; return out
                out.append(rd())
        if t[i]=='"':
            i+=1; b=[]
            while t[i]!='"':
                if t[i]=='\\': b.append(t[i+1]); i+=2
                else: b.append(t[i]); i+=1
            i+=1; return ('str',''.join(b))
        b=[]
        while i<n and t[i] not in ' \t\r\n()': b.append(t[i]); i+=1
        return ''.join(b)
    return rd()
def dump(x,ind=0):
    if isinstance(x,tuple): return '"%s"'%x[1].replace('\\','\\\\').replace('"','\\"')
    if isinstance(x,str): return x
    inner=' '.join(dump(c) for c in x)
    return '('+inner+')'
def get(node,key):
    return [c for c in node if isinstance(c,list) and c and c[0]==key]
def s(x): return x[1] if isinstance(x,tuple) else x
