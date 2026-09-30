import numpy as np
from scipy.optimize import nnls
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import make_pipeline
from pymodbus.client import ModbusTcpClient
from socket import create_connection
from time import sleep
@lambda _:_()
def Sim(n=10, set=47, get=34, env=.999, diff=.2):
    set = *np.random.randint(1, n-1, (2,set), 'B'),
    get = *np.random.randint(1, n-1, (2,get), 'B'),
    def Sim(x, t=80):
        __ = 1
        _ = np.zeros((n,n),'f')
        while np.abs(__-_).max()>.001:
            __ = _
            _ = _ * env
            _[set] = x+t
            _[0] = _[1]
            _[-1] = _[-2]
            _[:,0] = _[:,1]
            _[:,-1] = _[:,-2]
            _[1:-1,1:-1] += (_[:-2,1:-1]+_[2:,1:-1]-4*_[1:-1,1:-1]+_[1:-1,:-2]+_[1:-1,2:])*diff
        return _[get]-t
    return Sim
class Add(list):
    def fit(S, x, y):
        for s in S:
            s.fit(x, y)
            y = y-s.predict(x)
        return S
    def predict(s, x):
        return sum(s.predict(x)for s in s)
class GPR(GaussianProcessRegressor):
    def predict(s, x):
        x,s = super().predict(x, return_std=True)
        return x + np.random.default_rng().standard_normal(x.shape,'f')*s
def F(x, eps=.03, force=False):
    X[I] = x
    x = (x*100).astype('H').tolist()
    print(x)
    heat.write_registers(5, x[:7])
    ptm.write_registers(4085, x[7:])
    ptm.write_register(4211, 65535)
    sleep(4)
    y = []
    n = 0
    while n < 5:
        sleep(1.1)
        sensr.send(b'GetData')
        y += np.array(sensr.recv(999)[:-1].split(b',')[-34:],'f'),
        if len(y)>1 and abs(y[-1]-y[-2]).max()<eps:
            n += 1
        else:
            n = 0
    y = sum(y[-5:])/5
    print(y.mean(), 3*y.std())
    Y[I] = y-120
    # Y[I] = sim(x)
    I[()] += 1
    return Y[I-1]
def fit(x, y, w=1):
    w = np.broadcast_to(w,(len(x),1))
    w_ = w.sum()
    x_ = (x*w).sum(0)/w_
    y_ = (y*w).sum(0)/w_
    w = w**.5
    w = np.linalg.lstsq((x-x_)*w,(y-y_)*w)[0]
    return w, y_-x_@w
def fitb_1(x, y, w=1):
    w = np.linalg.lstsq((x[:-1]-x[-1])*w[:-1,None],(y[:-1]-y[-1])*w[:-1,None])[0]
    b = y[-1]-x[-1]@w
    return w, b
def poly(x, d=4):
    return (x[...,None]**np.arange(1,d+1,1,'f')).reshape(*x.shape[:-1],-1)
def hot(I, x):
    return np.array([x*(i==I)for i in range(47)],'f')
def lstsq1(a, b, mi, ma):
    x = min(max(a@b/np.linalg.norm(a)**2, mi), ma)
    return x, np.linalg.norm(a*x-b)
I,Y = np.memmap('in.ixy', '1I,9999,81f', shape=1)[0]
I.shape = ()
X = Y[:,:47]
Y = Y[:,47:]
X_ = np.zeros(47,'f')
Y_ = np.zeros(34,'f')
heat = ModbusTcpClient('<REDACTED:modbus-plc-host>')
heat.connect()
heat.write_register(801, 12000)
ptm = ModbusTcpClient('<REDACTED:modbus-ptm-host>')
ptm.connect()
sensr = create_connection(('<REDACTED:sensor-host>',9090))

# while Y[I-1].std()>.001*120/3:
#     F((fitb_1(Y[:I], X[:I], 1/(np.linalg.norm(Y[:I]-Y[I-1],axis=1)+1e-3))(Y_)).clip(0,13))
w = fitb_1(X[:I], Y[:I], 1/(np.linalg.norm(Y[:I]-Y[I-1],axis=1)+1e-3))[0]
while Y[I-1].std()>.0001*120/3:
    x = X[I-1]
    y = Y[I-1]
    kl = [lstsq1(w,y.mean()-y,-x,13-x)for w,x in zip(w,x)]
    i,(k,l) = min(enumerate(kl), key=lambda ikl:ikl[1][1]+np.random.rand()*.03)
    print(i, x[i], k, 3*l/34**.5)
    w[i] = (F(x+hot(i,k))-y)/k

# while not I or printed(Y[I-1].mean(), Y[I-1].std())>.001*80/3:    
#     F(np.random.default_rng().random(47,'f')*5 if i<100 else Add([
#         LinearRegression(),
#         make_pipeline(StandardScaler(), MLPRegressor(4,'tanh',alpha=.001,max_iter=999,early_stopping=True,validation_fraction=.4))
#         # make_pipeline(StandardScaler(), GPR(C(1.)*RBF(1.), alpha=0., normalize_y=True, n_restarts_optimizer=10))
#         # make_pipeline(StandardScaler(), KNeighborsRegressor(10, weights='distance'))
#     ]).fit(Y[:I],X[:I]).predict(Y_[None])[0].clip(0,12))