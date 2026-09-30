import torch
import numpy as np
from threading import Thread
from time import time, sleep
from torch.nn import *
def add(a, b):
    return a if b is None else a+b
def dot(a, b):
    return None if a is None else a@b
class Rnn(Linear):
    def __init__(s, i, o, h, act=torch.tanh):
        super().__init__(i+o+h, h)
        s._ = Linear(h, o)
        s.act = act
    def forward(s, i, o=None, h=None, l=-1):
        I,O,H = s.weight.mT.split([i.size(-1),s._.out_features,s.out_features])
        h = [h]
        if o is None or o.ndim<3:
            o = [o]
            for _ in functional.linear(i, I.mT, s.bias).broadcast_to(l,-1,-1):
                h.append(s.act(add(add(_, dot(o[-1], O)), dot(h[-1], H))))
                o.append(s._(h[-1]))
            return torch.stack(o[1:])
        for _ in add(functional.linear(i, I.mT, s.bias), dot(o, O)).broadcast_to(l,-1,-1):
            h.append(s.act(add(_, dot(h[-1], H))))
        return s._(torch.stack(h[1:]))
def OvershotLR(o, k=.5, w=1, K=1.005, W=1):
    N = 0
    L = 9e9
    def OvershotLR(l):
        nonlocal N,L
        l.backward()
        utils.clip_grad_norm_(o.param_groups[0]['params'], 1.)
        N = min(N,1)-1 if l>L else max(N,-1)+1
        o.param_groups[0]['lr'] = r = o.param_groups[0]['lr']*(k*w**N if l>L else K*W**N)
        o.step()
        o.zero_grad()
        L = l
        return l.data, r
    return OvershotLR

from pymodbus.client import ModbusTcpClient
from socket import create_connection
I = np.memmap('ixy', 'I', shape=1)
X = np.memmap('ixy', '1,47f,1,34f', offset=4, shape=9999999)
Y = X['f1']
X = X['f0']
heat = ModbusTcpClient('<REDACTED:modbus-plc-host>')
heat.connect()
heat.write_register(801, 8000)
ptm = ModbusTcpClient('<REDACTED:modbus-ptm-host>')
ptm.connect()
def set(x):
    x = x[0].numpy()
    X[I[0]:I[0]+16] = x
    heat.write_registers(5, (x[:7]*1000).astype('H').tolist())
    ptm.write_registers(2085, (x[7:]*1200).astype('H').tolist())
disk = create_connection(('<REDACTED:sensor-host>',9090))
@lambda _:Thread(target=_,daemon=True).start()
def get():
    while 1:
        t = time()
        disk.send(b'GetData')
        Y[I[0]] = np.array(disk.recv(999)[:-1].split(b',')[-34:],'f')-80
        I[:] += 1
        sleep(max(t+.1-time(),0))

def stat(_):
    return f'{_.min():.3f}/{_.mean():.3f}±{_.std():.1f}/{_.max():.3f}'
tgt = torch.tensor(0.)
setv = torch.full((1,47), .1)
set((setv+.5*(torch.rand_like(setv)-.5)).relu_())
m = Rnn(47, 34, 64)
o = torch.optim.Adam(m.parameters(), .01)
O = OvershotLR(o, k=.99, K=1.01)
t0 = t = t2 = time()
while 1:
    l = I[0]
    l,r = O(functional.mse_loss(m(torch.from_numpy(X[:l-1]), torch.from_numpy(Y[:l-1])), torch.from_numpy(Y[1:l])))
    if time() - t > 5:
        if time() - t2 > 5:
            m.requires_grad_(False)
            x = torch.zeros((1,47), requires_grad=True)
            o2 = torch.optim.Adam([x], .001)
            O2 = OvershotLR(o2, k=1, K=1)
            for _ in range(20):
                for _ in range(1000):
                    l2,r2 = O2(functional.mse_loss(m(x.sigmoid(), torch.from_numpy(Y[I[0]-1]), l=128)[0][-1], tgt))
                print(end=f'{l2.data:1.2e} {r2:1.1e}\n')
            if l2.isfinite():
                setv = x.requires_grad_(False).sigmoid()
            m.requires_grad_()
            t2 = time()
        set((setv+(1-(time()-t0)/900)*.5*(torch.rand_like(setv)-.5)).relu_())
        print(l.data, r, I[0], stat(Y[I[0]-1,0]), stat(X[I[0],0,:7]*10), stat(X[I[0],0,7:]*1200))
        t = time()