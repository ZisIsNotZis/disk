from MvCameraControl_class import *
from datetime import datetime
from halcon import himage_from_numpy_array, region_features
from json import loads, dumps
from minio import Minio
from numpy import frombuffer
from paho.mqtt.client import Client
from pymodbus.client import ModbusTcpClient
from socket import gethostname, gethostbyname
from subprocess import Popen, PIPE
from threading import Thread
from time import sleep, time
from uuid import uuid4
from os import getenv, remove, link
import halcon

CFG = loads(open('mock.json').read())#{id:{"cam":[uri,arg...],"plc":uri,"alg":{alg:{op:[arg...]...}...}}}
# NOTE: this line previously carried a literal MinIO access-key/secret-key pair.
# That inline credential has been removed and MUST BE ROTATED by the owner.
# Supply credentials through the environment / a secret store instead.
MINIO = Minio(getenv('MINIO_ENDPOINT','localhost:8001'),getenv('MINIO_ACCESS_KEY'),getenv('MINIO_SECRET_KEY'),secure=0)

def Set(f):
    def Set(_):
        try:
            f[_.__name__] = _
        except TypeError:
            setattr(f, _.__name__, _)
    return Set
def Debug(f):
    def Debug(*_):
        try:
            __ = f(*_)
        except Exception as __:
            print(f.__name__, *_, '->', __)
            raise
        print(f.__name__, *_, '->', __)
        return __
    return Debug

Mq = Client()
Mq.connect(getenv('MQTT_HOST','localhost'))
@Set(Mq)
def on_connect(Mq, *_):
    Mq.subscribe([(f'{gethostname()}/cfg', 1), ('demo/vision/job', 1)])
@Set(Mq)
def on_message(Mq, _, msg):
    global CFG
    if msg.topic == 'demo/vision/job':
        Engine.send(f'{msg.payload[8:].decode()}/'.split('/')[:9])
    else:
        CFG = loads(msg.payload)

def Plc(id):
    plc = ModbusTcpClient(CFG[id]['plc'])
    assert plc.connect()
    plc.read_holding_registers(40)

@Debug
def Cam(id, uri, *_):
    return Cam._.get(uri.split('://')[0],next(iter(Cam._.values())))(id, uri, *_)
Cam._ = {}
@Set(Cam._)
def mv(id, ip, row0, col0, row1, col1, exp, fps):
    stDevInfo = MV_CC_DEVICE_INFO()
    stDevInfo.nTLayerType = MV_GIGE_DEVICE
    stDevInfo.SpecialInfo.stGigEInfo = MV_GIGE_DEVICE_INFO()
    stDevInfo.SpecialInfo.stGigEInfo.nCurrentIp = sum(int(_)<<24-i*8 for i,_ in enumerate(ip.split('.')))
    stDevInfo.SpecialInfo.stGigEInfo.nNetExport = sum(int(_)<<24-i*8 for i,_ in enumerate(gethostbyname(gethostname()).split('.')))
    cam = MvCamera()
    cam.MV_CC_CreateHandle(stDevInfo)
    cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
    cam.MV_CC_GetBoolValue('AcquisitionFrameRateEnable', c_bool(0))
    cam.MV_CC_SetEnumValue('TriggerMode', MV_TRIGGER_MODE_OFF)
    cam.MV_CC_SetIntValue('OffsetX', row0)
    cam.MV_CC_SetIntValue('OffsetY', col0)
    cam.MV_CC_SetIntValue('Height', row1-row0)
    cam.MV_CC_SetIntValue('Width', col1-col0)
    cam.MV_CC_SetFloatValue('ExposureTime', exp)
    cam.MV_CC_StartGrabbing()
    if _ := int(cam.MV_CC_GetOptimalPacketSize()):
        if cam.MV_CC_SetIntValue('GevSCPSPacketSize', _):
            warn('MV_CC_SetIntValue')
    else:
        warn('MV_CC_GetOptimalPacketSize')
    frame = MV_FRAME_OUT()
    ff = Popen(('ffmpeg','-y','-f','rawvideo','-pix_fmt','gray','-s',f'{row1-row0}x{col1-col0}','-r',fps,'-i','-','-c','h264_qsv','-preset','veryfast','-q','30','-f','tee','[f=mp4]{id}.mp4|[f=rtsp,fps_mode=0,fflags=nobuffer,flags=low_delay,strict,experimental,rtsp_transport=tcp]rtsp://<REDACTED:rtsp-host>/{id}.sdp'), stdin=PIPE)
    try:
        while 1:
            if not cam.MV_CC_GetImageBuffer(cam.frame, 999):
                yield himage_from_numpy_array(np.frombuffer(cam.frame.pBufAddr, f'{col1-col0}B'))
                cam.MV_CC_FreeImageBuffer(cam.frame)
    finally:
        ff.terminate()
        cam.MV_CC_StopGrabbing()
        cam.MV_CC_CloseDevice()
        cam.MV_CC_DestroyHandle()
@Set(Cam._)
def rtsp(id, uri, row, col):
    ff = Popen(('ffmpeg','-y','-f','rtsp','-fps_mode','0','-fflags','nobuffer','-flags','low_delay','-strict','experimental','-rtsp_transport','tcp','-an','-i',uri,'-c','copy','-an','-f','tee',f'[f=mp4]{id}.mp4|[f=rawvideo]-'), stdout=PIPE)
    try:
        while 1:
            yield himage_from_numpy_array(frombuffer(ff.stdout.read(row*col), f'{col}B'))
    finally:
        ff.terminate()
@Set(Cam._)
def file(id, uri, row, col):
    ff = Popen(('ffmpeg','-an','-re','-i',uri[7:],'-f','rtsp','-fps_mode','0','-fflags','nobuffer','-flags','low_delay','-strict','experimental','-rtsp_transport','tcp','-c','copy','-an',f'rtsp://localhost:8554/{id}.sdp','-f','rawvideo','-pix_fmt','gray','-'), stdout=PIPE)
    try:
        _ = ff.stdout.read(row*col)
        while _:
            yield himage_from_numpy_array(frombuffer(_, f'{col}B'))
            _ = ff.stdout.read(row*col)            
    finally:
        ff.terminate()
        try:
            remove(f'{id}.mp4')
        except FileNotFoundError:
            pass
        link(uri[7:], f'{id}.mp4')

def Alg(obj, alg):
    res = {}
    ok = 0
    for i,alg in alg.items():
        if i in ('rectangle1_domain','threshold'):
            obj = getattr(halcon, i)(obj, *alg)
        else:
            res[i] = _ = region_features(obj, i)[0]
            ok &= any(alg[i]<_<alg[i+1]for i in range(0,len(alg),2))
    return res, ok
@Debug
def Algs(id, receip, time, cj, pj, lot, wafer, slot, cmd):
    res = {i:[]for i in CFG[id]['alg']}
    for obj in Cam(id, *CFG[id]['cam']):
        if not cmd[0]:
            for i,alg in CFG[id]['alg'].items():
                res[i] += (Alg(obj, alg),)
        elif cmd[0]:
            break
    Mq.publish('demo/vision/jobres', dumps(res,separators=',:'), 1)
    Mq.publish('demo/vision/jobres', f'ERR:RUN/{id}/{receip}/{time}/{cj}/{pj}/{lot}/{wafer}/{slot}/ERRORCODE/ERROR_DESCRIPTION/{uuid4()}')
    MINIO.fput_object('log', datetime.now().strftime(f'%y%m%d/%H%M%S/{id}.mp4'), f'{id}.mp4')
def Engine():
    th = {}
    while 1:
        id,receip,time,cj,pj,lot,wafer,slot,cmd = yield
        if id in th and th[id].is_alive():
            (th.get if cmd=='PROCESSEND'else th.pop)(id)._args[-1][0] = cmd
        else:
            _ = Thread(target=Algs, args=(id, receip, time, cj, pj, lot, wafer, slot, [cmd]))
            _.start()
            th[id] = _
Engine = Engine()
Engine.send(None)

Mq.loop_forever()