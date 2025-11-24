class VM:
    def __init__(self,bytecode):
        self.bc=bytecode
        self.stack=[]
        self.vars={}
        self.pc=0
        self.output=[]
    def step(self):
        if self.pc>=len(self.bc):
            return False
        inst=self.bc[self.pc]
        op=inst[0]
        if op=='CONST':
            self.const_val=inst[1]
        elif op=='PUSH_CONST':
            self.stack.append(self.const_val)
        elif op=='LOAD':
            self.stack.append(self.vars.get(inst[1],0))
        elif op=='STORE':
            self.vars[inst[1]]=self.stack.pop()
        elif op=='ADD':
            b=self.stack.pop()
            a=self.stack.pop()
            self.stack.append(a+b)
        elif op=='SUB':
            b=self.stack.pop()
            a=self.stack.pop()
            self.stack.append(a-b)
        elif op=='MUL':
            b=self.stack.pop()
            a=self.stack.pop()
            self.stack.append(a*b)
        elif op=='DIV':
            b=self.stack.pop()
            a=self.stack.pop()
            self.stack.append(int(a/b)if b!=0 else 0)
        elif op=='PRINT':
            self.output.append(str(self.stack.pop()))
        elif op=='JMP':
            self.pc=inst[1]
            return True
        elif op=='JMP_IF_ZERO':
            v=self.stack.pop()
            if v==0:
                self.pc=inst[1]
                return True
        elif op=='JMP_IF_POS':
            v=self.stack.pop()
            if v>0:
                self.pc=inst[1]
                return True
        else:
            raise RuntimeError('Unknown op '+str(op))
        self.pc+=1
        return True
    def run(self,max_steps=100000):
        steps=0
        while self.step():
            steps+=1
            if steps>max_steps:
                raise RuntimeError('Max steps exceeded')
        return self.output