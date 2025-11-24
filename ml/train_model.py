import itertools
import random
import time
import torch
import torch.nn as nn
import torch.optim as optim
from joblib import dump,load
import os
from ir import ast_to_ir,assemble_ir
from optimizer import apply_pass_sequence
from vm import VM
from parser import Parser
from lexer import tokenize
from ast import Program
from optimizer import PASS_MAP
from collections import defaultdict
MODEL_PATH='ml_model.pt'
SEQ_LIST=list(itertools.permutations(['const_fold','peephole','loop_unroll']))
def extract_features_from_ast(ast:Program):
    counts=defaultdict(int)
    max_depth=0
    def walk(node,depth=0):
        nonlocal max_depth
        max_depth=max(max_depth,depth)
        counts[type(node).__name__]+=1
        if isinstance(node,Program):
            for s in node.statements:walk(s,depth+1)
        elif isinstance(node,(Let,Print)):
            walk(node.expr if hasattr(node,'expr')else node,depth+1)
        elif isinstance(node,BinOp):
            walk(node.left,depth+1)
            walk(node.right,depth+1)
        elif isinstance(node,ForLoop):
            walk(node.start_expr,depth+1)
            walk(node.end_expr,depth+1)
            for s in node.body:walk(s,depth+1)
        elif isinstance(node,If):
            walk(node.cond,depth+1)
            for s in node.then_block:walk(s,depth+1)
            if node.else_block:
                for s in node.else_block:walk(s,depth+1)
    walk(ast,0)
    return {'num_nodes':sum(counts.values()),'num_binops':counts['BinOp'],'num_loops':counts['ForLoop'],'num_lets':counts['Let'],'num_prints':counts['Print'],'max_depth':max_depth}
def features_to_tensor(fdict):
    v=[fdict['num_nodes'],fdict['num_binops'],fdict['num_loops'],fdict['num_lets'],fdict['num_prints'],fdict['max_depth']]
    return torch.tensor(v,dtype=torch.float32)
class MLP(nn.Module):
    def __init__(self,in_dim=6,hidden=64,out_dim=6):
        super().__init__()
        self.net=nn.Sequential(nn.Linear(in_dim,hidden),nn.ReLU(),nn.Linear(hidden,hidden//2),nn.ReLU(),nn.Linear(hidden//2,out_dim))
    def forward(self,x):
        return self.net(x)
def gen_random_program_simple(max_statements=5):
    from ast import Number,Var,BinOp,Let,Print,ForLoop
    var_names=['a','b','c','i','j','x','y']
    def rand_expr(depth=0):
        if depth>2 or random.random()<0.4:
            if random.random()<0.5:return Number(random.randint(0,10))
            else:return Var(random.choice(var_names))
        op=random.choice(['+','-','*','/'])
        return BinOp(op,rand_expr(depth+1),rand_expr(depth+1))
    stmts=[]
    for _ in range(random.randint(1,max_statements)):
        t=random.random()
        if t<0.2:
            var=random.choice(var_names)
            start=Number(0)
            end=Number(random.randint(1,4))
            body=[]
            for _ in range(random.randint(1,2)):
                name=random.choice(var_names)
                body.append(Let(name,rand_expr()))
            if random.random()<0.5:
                body.append(Print(Var(random.choice(var_names))))
            stmts.append(ForLoop(var,start,end,body))
        elif t<0.6:
            name=random.choice(var_names)
            stmts.append(Let(name,rand_expr()))
        else:
            stmts.append(Print(rand_expr()))
    return Program(stmts)
def benchmark_ast(ast,seq,runs=1):
    ir=ast_to_ir(ast)
    ir_opt=apply_pass_sequence(ir,seq)
    try:bc=assemble_ir(ir_opt)
    except Exception:bc=assemble_ir(ir)
    total=0.0
    for _ in range(runs):
        vm=VM(bc)
        t0=time.perf_counter()
        try:vm.run()
        except Exception:return 1e6
        total+=time.perf_counter()-t0
    return total/runs
def generate_dataset_torch(n=300):
    X=[]
    y=[]
    for i in range(n):
        ast=gen_random_program_simple()
        f=extract_features_from_ast(ast)
        times=[]
        for seq in SEQ_LIST:
            times.append(benchmark_ast(ast,seq,runs=1))
        best=int(min(range(len(times)),key=lambda k:times[k]))
        X.append(features_to_tensor(f))
        y.append(best)
        if i%50==0:print('gen',i)
    X=torch.stack(X)
    y=torch.tensor(y,dtype=torch.long)
    return X,y
def train_model(save_path=MODEL_PATH,epochs=50,batch=32):
    X,y=generate_dataset_torch(300)
    model=MLP()
    opt=optim.Adam(model.parameters(),lr=1e-3)
    crit=nn.CrossEntropyLoss()
    dataset=torch.utils.data.TensorDataset(X,y)
    loader=torch.utils.data.DataLoader(dataset,batch_size=batch,shuffle=True)
    model.train()
    for ep in range(epochs):
        total_loss=0.0
        for xb,yb in loader:
            opt.zero_grad()
            logits=model(xb)
            loss=crit(logits,yb)
            loss.backward()
            opt.step()
            total_loss+=loss.item()*len(xb)
        print(f'ep {ep+1}/{epochs} loss {total_loss/len(dataset):.4f}')
    torch.save(model.state_dict(),save_path)
    print('Saved PyTorch model to',save_path)
    return model
def load_model(path=MODEL_PATH):
    if not os.path.exists(path):return None
    model=MLP()
    model.load_state_dict(torch.load(path))
    model.eval()
    return model
def predict_seq_for_ast(ast,model):
    f=extract_features_from_ast(ast)
    x=features_to_tensor(f).unsqueeze(0)
    if model is None:
        return SEQ_LIST[0]
    logits=model(x).detach()
    idx=int(logits.argmax(dim=1).item())
    return SEQ_LIST[idx]