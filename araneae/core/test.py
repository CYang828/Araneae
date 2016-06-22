
class A:
    
    def chain(self,l):
        for i in l:
            yield i

    def hello(self):
        a = ['h','e','l','l','o']
        return self.chain(a)

a = A()
for b in a.hello():
    print b

