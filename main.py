import sys
from lexer import tokenize
from parser import Parser
from ir import ast_to_ir,assemble_ir
from vm import VM
from ml.train_model import train_model,load_model,predict_seq_for_ast
from optimizer import apply_pass_sequence
EXAMPLE='''
let x = 0
for i in 0..4 {
    let x = x + i
}
print(x)
'''
def compile_and_run(code,model=None):
    toks=list(tokenize(code))
    parser=Parser(toks)
    ast=parser.parse()
    seq=predict_seq_for_ast(ast,model)
    print('Using sequence:',seq)
    ir=ast_to_ir(ast)
    print('IR before opt:\n',ir)
    ir_opt=apply_pass_sequence(ir,seq)
    print('IR after opt:\n',ir_opt)
    bc=assemble_ir(ir_opt)
    vm=VM(bc)
    out=vm.run()
    print('Output:',out)
if __name__=='__main__':
    cmd=sys.argv[1]if len(sys.argv)>1 else'run'
    if cmd=='train':
        train_model(epochs=30)
    elif cmd=='run':
        model=load_model()
        compile_and_run(EXAMPLE,model=model)
    else:
        print('Unknown command')