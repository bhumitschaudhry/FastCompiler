from copy import deepcopy
def pass_constant_fold(ir):
    new_ir=[]
    i=0
    while i<len(ir):
        if i+4<len(ir):
            a,b,c,d,e=ir[i],ir[i+1],ir[i+2],ir[i+3],ir[i+4]
            if a[0]=='CONST' and b[0]=='PUSH_CONST' and c[0]=='CONST' and d[0]=='PUSH_CONST' and e[0]in('ADD','SUB','MUL','DIV'):
                av,bv,op=a[1],c[1],e[0]
                if op=='ADD':res=av+bv
                elif op=='SUB':res=av-bv
                elif op=='MUL':res=av*bv
                elif op=='DIV':res=int(av/bv)if bv!=0 else 0
                new_ir.append(('CONST',res))
                new_ir.append(('PUSH_CONST',))
                i+=5
                continue
        new_ir.append(ir[i])
        i+=1
    return new_ir
def pass_peephole(ir):
    new_ir=[]
    i=0
    while i<len(ir):
        if i+1<len(ir)and ir[i][0]=='LOAD'and ir[i+1][0]=='STORE'and ir[i][1]==ir[i+1][1]:
            i+=2
            continue
        new_ir.append(ir[i])
        i+=1
    return new_ir
def pass_loop_unroll(ir,unroll_factor=2):
    return deepcopy(ir)
PASS_MAP={'const_fold':pass_constant_fold,'peephole':pass_peephole,'loop_unroll':pass_loop_unroll}
def apply_pass_sequence(ir,seq):
    r=deepcopy(ir)
    for p in seq:
        r=PASS_MAP[p](r)
    return r