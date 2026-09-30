import torch
from torch.nn import *
from pymodbus.client import ModbusTcpClient
from threading import Thread
from socket import create_connection

X = torch.empty(10000,1,47)
I = 0
bus = ModbusTcpClient('<REDACTED:modbus-plc-host>')
bus.connect()
def set(t, x):
    X[I] = x
    bus.write_register(801, t)
    bus.write_register(5, x[:7])
    bus.write_register(2085, x[7:])

T = torch.empty(10000,1,34)
@lambda _:Thread(target=_).start()
def get():
    global I
    disk = create_connection(('<REDACTED:sensor-host>',9090))
    while 1:
        disk.send(b'GetData')
        T[I] = [int(_)for _ in disk.recv(999)[:-1].split(b',')[-34:]]
        I += 1

setv = torch.zeros(34)
set(setv)
tgt = torch.tensor(100.)
m = Rnn(8, 8, 32)
o = torch.optim.Adam(m.parameters(), .02, eps=1e-15)
O = OvershotLR(o, K=1.01)
o2 = torch.optim.Adam((setv,), .1, eps=1e-15)
O2 = OvershotLR(o2, K=1.01)
scale = Scale()
i = 0
while 1:
    O(functional.mse_loss(m(X[:I+1], T[:I+1])[0], T[1:i+2]))
    if I//10 > i:
        i = I//10
        set(setv + torch.randn(34)/i)
        if not i%10:
            m.requires_grad_(False)
            setv.requires_grad_()
            for _ in range(1000):
                O2(functional.mse_loss(m(scale(setv)[None], l=256)[0][-1], scale(tgt)))
            setv.requires_grad_(False)
            m.requires_grad_()
            set(setv)
            import matplotlib.pyplot as plt
            from IPython.display import clear_output
            plt.subplot(211)
            O(None)
            plt.subplot(212)
            O2(None)
            clear_output(True)
            plt.show()