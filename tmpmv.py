from MvCameraControl_class import *
from ctypes import *
from sys import argv, stderr
from os import write
MvCamera.MV_CC_Initialize()
stDevInfo = MV_CC_DEVICE_INFO()
stGigEDev = MV_GIGE_DEVICE_INFO()
stGigEDev.nCurrentIp = sum(int(_)<<24-i*8 for i,_ in enumerate(argv[1].split('.')))
stGigEDev.nNetExport = sum(int(_)<<24-i*8 for i,_ in enumerate(argv[2].split('.')))
stDevInfo.nTLayerType = MV_GIGE_DEVICE
stDevInfo.SpecialInfo.stGigEInfo = stGigEDev
cam = MvCamera()
assert cam.MV_CC_CreateHandle(stDevInfo)==0
assert cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)==0
if stDevInfo.nTLayerType == MV_GIGE_DEVICE:
    nPacketSize = int(cam.MV_CC_GetOptimalPacketSize())
    if nPacketSize:
        if cam.MV_CC_SetIntValue("GevSCPSPacketSize", nPacketSize):
            print('WRN MV_CC_SetIntValue', file=stderr)
    else:
        print('WRN MV_CC_GetOptimalPacketSize', file=stderr)
stBool = c_bool(0)
assert cam.MV_CC_GetBoolValue("AcquisitionFrameRateEnable", stBool)==0
assert cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)==0
assert cam.MV_CC_SetFloatValue("ExposureTime", float(argv[3])if len(argv)>3 else 5000)==0
assert cam.MV_CC_StartGrabbing()==0
stOutFrame = MV_FRAME_OUT()
memset(byref(stOutFrame), 0, sizeof(stOutFrame))
while 1:
    if cam.MV_CC_GetImageBuffer(stOutFrame, 1000):
        print('WRN MV_CC_GetImageBuffer', file=stderr)
        continue
    if stderr:
        print(stOutFrame.stFrameInfo.nWidth, stOutFrame.stFrameInfo.nHeight, stOutFrame.stFrameInfo.nFrameLen, file=stderr)
        stderr = 0
    img_save = (c_ubyte*stOutFrame.stFrameInfo.nWidth*stOutFrame.stFrameInfo.nHeight)()
    memmove(byref(img_save), stOutFrame.pBufAddr, stOutFrame.stFrameInfo.nWidth*stOutFrame.stFrameInfo.nHeight)
    write(1, img_save)
    cam.MV_CC_FreeImageBuffer(stOutFrame)
assert cam.MV_CC_StopGrabbing()==0
assert cam.MV_CC_CloseDevice()==0
assert cam.MV_CC_DestroyHandle()==0
MvCamera.MV_CC_Finalize()