from copy import deepcopy
def ast_to_ir(ast):
    ir = []
    def emit(node):
        if isinstance(node, Program):
            for s in node.statements: emit(s)
        elif isinstance(node, Let):
            emit(node.expr); ir.append(('STORE', node.name))
        elif isinstance(node, Print):
            emit(node.expr); ir.append(('PRINT',))
        elif isinstance(node, Number):
            ir.append(('CONST', node.value)); ir.append(('PUSH_CONST',))
        elif isinstance(node, Var):
            ir.append(('LOAD', node.name))
        elif isinstance(node, BinOp):
            emit(node.left); emit(node.right)
            if node.op == '+': ir.append(('ADD',))
            elif node.op == '-': ir.append(('SUB',))
            elif node.op == '*': ir.append(('MUL',))
            elif node.op == '/': ir.append(('DIV',))
        elif isinstance(node, ForLoop):
            start_lbl = f'LBL{len(ir)}_S'; end_lbl = f'LBL{len(ir)}_E'
            emit(node.start_expr); ir.append(('STORE', node.var))
            ir.append(('LABEL', start_lbl))
            ir.append(('LOAD', node.var)); emit(node.end_expr); ir.append(('SUB',)); ir.append(('JMP_IF_POS', end_lbl))
            for s in node.body: emit(s)
            ir.append(('LOAD', node.var)); ir.append(('CONST', 1)); ir.append(('PUSH_CONST',)); ir.append(('ADD',)); ir.append(('STORE', node.var))
            ir.append(('JMP', start_lbl)); ir.append(('LABEL', end_lbl))
        elif isinstance(node, If):
            lbl_else = f'LBL{len(ir)}_EL'; lbl_end = f'LBL{len(ir)}_EN'
            emit(node.cond); ir.append(('PUSH_CONST',)); ir.append(('JMP_IF_ZERO', lbl_else))
            for s in node.then_block: emit(s)
            ir.append(('JMP', lbl_end)); ir.append(('LABEL', lbl_else))
            if node.else_block:
                for s in node.else_block: emit(s)
            ir.append(('LABEL', lbl_end))
    emit(ast)
    return ir
def assemble_ir(ir):
    labels = {}
    pc = 0
    for inst in ir:
        if inst[0] == 'LABEL': labels[inst[1]] = pc
        else: pc += 1
    bytecode = []
    for inst in ir:
        if inst[0] == 'LABEL': continue
        op = inst[0]
        if op in ('CONST',): bytecode.append(inst)
        elif op in ('PUSH_CONST','ADD','SUB','MUL','DIV','PRINT','STORE','LOAD'):
            bytecode.append((op, *inst[1:]))
        elif op in ('JMP','JMP_IF_ZERO','JMP_IF_POS'):
            target = inst[1]
            if target not in labels: raise RuntimeError('Unknown label '+str(target))
            bytecode.append((op, labels[target]))
        else:
            bytecode.append(inst)
    return bytecode