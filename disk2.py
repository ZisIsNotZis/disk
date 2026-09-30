import numpy as np
from scipy.optimize import least_squares
from pymodbus.client import ModbusTcpClient
from socket import create_connection
from time import sleep
I, Y = np.memmap('in.ixy', '1I,9999,81f', shape=1)[0]
I.shape = ()
X = Y[:, :47]
Y = Y[:, 47:]
heat = ModbusTcpClient('<REDACTED:modbus-plc-host>')
heat.connect()
heat.write_register(801, 12000)
ptm = ModbusTcpClient('<REDACTED:modbus-ptm-host>')
ptm.connect()
sensr = create_connection(('<REDACTED:sensor-host>', 9090))


def F(x):
    if (_ := (X[:I] == x).all(1)).any():
        return Y[_.argmax()]
    heat.write_registers(5, (x[:7]*100).astype('H').tolist())
    ptm.write_registers(4085, (x[:7]*100).astype('H').tolist())
    ptm.write_register(4211, 65535)
    y_, y = 0, 1
    while np.max(abs(y_-y)) > .05:
        y_ = y
        sleep(7.1)
        sensr.send(b'GetData')
        y = np.array(sensr.recv(999)[:-1].split(b',')[-34:], 'f')
    print(x, y.mean(), 3*y.std())
    if I < 48:
        X[I] = x
        Y[I] = y
        I[()] += 1
    return y


least_squares(
    F, np.ones(47, 'f'),
    '2-point',  # 3-point
    (0, 12), 'dogbox',  # trf
    .01, .01, .01, 'jac',  # 1
    'huber',  # linear,soft_l1,cauchy
    1, .27,  # .09,.03
    'lsmr'  # exact,None
)
