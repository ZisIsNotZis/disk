import torch
import numpy as np
from torch.nn import *
from threading import Thread
from time import sleep, time
def Sim(_, set, get, envk=.999, diffk=.2):
    set = *torch.randint(1, _-1, (2,set)),
    get = *torch.randint(1, _-1, (2,get)),
    _ = torch.zeros(_,_)
    def Sim(setv):
        if setv is None:
            _[()] = 0
        else:
            _[()] *= envk
            _[set] = setv
            _[0] = _[1]
            _[-1] = _[-2]
            _[:,0] = _[:,1]
            _[:,-1] = _[:,-2]
            _[1:-1,1:-1] += (_[:-2,1:-1]+_[2:,1:-1]-4*_[1:-1,1:-1]+_[1:-1,:-2]+_[1:-1,2:])*diffk
            return _[get]
    return Sim
def stat(_):
    return f'{_.min():.3f}/{_.mean():.3f}/{_.max():.3f}'

X = np.memmap('ixy', 'I', shape=1+9999999*81)
I = X[:1].reshape(())
X = torch.from_numpy(X[1:].reshape(-1,1,81).view('f'))
@lambda _:Thread(target=_,daemon=True).start()
def _():
    # from pymodbus.client import ModbusTcpClient
    # set = ModbusTcpClient('<REDACTED:modbus-plc-host>')
    # set.connect()
    # set.write_register(801, 8000)
    # ptm = ModbusTcpClient('<REDACTED:modbus-ptm-host>')
    # ptm.connect()
    t = time()
    while True:
        # X.data[-1,0,:47] += (1-(time()-t)/1800)*10*torch.randn(47)
        # set.write_register(5, (x[0,:7].sigmoid()*1000).short().tolist())
        # ptm.write_register(2085, (x[0,7:].sigmoid()*1200).short().tolist())
        X.data[-1,0,:47] += (1-(time()-t)/900)*.5*torch.randn(47)
        sleep(1)
@lambda _:Thread(target=_,daemon=True).start()
def _():
    from socket import create_connection
    # get = create_connection(('<REDACTED:sensor-host>',9090))
    get = Sim(12, 47, 34)
    while True:
        X.data[I,0,:47] = X[-1,0,:47]
        # get.send(b'GetData')
        # X.data[I,0,47:] = np.array(get.recv(999)[:-1].split(b',')[-34:],'f')-80
        X.data[I,0,47:] = get(X[-1,0,:47]+80)-80
        I[()] += 1
        sleep(.1)

sleep(1)
m = Sequential(LSTM(47+34, 128), Linear(128, 34))
o = torch.optim.Adam(m.parameters(), .03)
z = torch.tensor(0.)
while True:
    l = 2
    t = time()
    i = I.item()
    while l > 1:
        y,h = m[0](X[:i-1])
        y = m[1](y)
        l = functional.mse_loss(y, X[1:i,:,47:])
        l.backward()
        utils.clip_grad_norm_(m.parameters(), 1)
        o.step()
        o.zero_grad()
        if time() - t > .2:
            print('m', l.data, I, stat(X[-1,0,:47]), stat(X[I-1,0,47:]))
            t = time()
    m.requires_grad_(False)
    x = X[-1:,:,:47].clone().requires_grad_()
    o_ = torch.optim.Adam([x], .5)
    t = time()
    for _ in range(1000):
        y_ = y.data[-1:]
        h_ = [h.data for h in h]
        for _ in range(64):
            y_,h_ = m[0](torch.cat([x,y_], 2), h_)
            y_ = m[1](y_[-1:])
        l = functional.mse_loss(y_, z)
        l.backward()
        utils.clip_grad_norm_([x], 1)
        o_.step()
        o_.zero_grad()
        if time() - t > .2:
            print('x', l.data, I, stat(X[-1,0,:47]), stat(X[I-1,0,47:]))
            t = time()
    if l.isfinite():
        X.data[-1,:,:47] = x.data
    m.requires_grad_()

