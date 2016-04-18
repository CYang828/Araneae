#*-*coding:utf8*-*

import lxml.etree

def element_len(s):
    num = 0

    if isinstance(s,list):
        for i in s:
            r = element_len(i)

            if not r:
                num = len(s)
                return num
            else:
                num += r

        return num
            
    else:
        return None

def element2text(e):
    for xn,n in enumerate(e):
        for xm,m in enumerate(n):
            if isinstance(m,lxml.etree.ElementBase):
                e[xn][xm] = m.text
                continue
            for xp,p in enumerate(m):
                if isinstance(p,lxml.etree.ElementBase):
                    e[xn][xm][xp] = p.text
                    continue
    return e
            
        
