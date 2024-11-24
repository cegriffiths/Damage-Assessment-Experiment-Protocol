## DAMAGE INSPECTION RIG APP
## Author: Chirs Griffiths
# Date: November 23, 2024\

## Heavily based off of James Brown's code from Redlen with some minor edits
## This app interacts with AmScope camera (setup camera parameters, take snaps) via amcam.py
## It will also contain basic functionality to save images for batch image collection (multiple sensors on GelPaks) or inline inspection

import amcam
import PIL.Image as Image

def warnRangeSetting(setting, low, high, setVar):
    '''Basic limit setting range check.'''
    if setVar > high or setVar < low:
        print(f"{setting} setting ({setVar}) out of range!")
        return True
    return False

class App:
    def __init__(self, liveCallback = None):
        self.hcam = None
        self.buf = None
        self.stillBuf = None
        self.stillSize = None
        self.total = 0
        self.running = False
        self.liveCallback = liveCallback
        self.saved = True

    def setLiveCallback(self, liveCallback):
        self.liveCallback = liveCallback

# the vast majority of callbacks come from amcam.dll/so/dylib internal threads
    def setupCamera(self):
        print("Starting camera...")
        a = amcam.Amcam.EnumV2()
        if len(a) > 0:
            # Print camera info (for debugging)
            # print('{}: flag = {:#x}, preview = {}, still = {}'.format(a[0].displayname, a[0].model.flag, a[0].model.preview, a[0].model.still))
            # for r in a[0].model.res:
            #     print('\t = [{} x {}]'.format(r.width, r.height))
            self.hcam = amcam.Amcam.Open(a[0].id)
            if self.hcam:
                # try:
                    # set settings
                    if not self.setCameraSettings(exposureTimeMs=3.25):
                        raise Exception("Settings error.")
                    # Set still buffer to highest res (5 MP)
                    r = a[0].model.res[0]
                    stillBufsize = ((r.width * 24 + 31) // 32 * 4) * r.height
                    self.stillSize = (r.width, r.height)
                    self.stillBuf = bytes(stillBufsize)
                    # WARNING: MAY NEED TO CHANGE BYTE ORDER IF NOT USING WINDOWS
                    self.hcam.put_Option(amcam.AMCAM_OPTION_BYTEORDER, 0)
                    # Set preview buffer to low res (0.5 MP)
                    self.hcam.put_eSize(2) # Set low res for preview pull
                    self.width, self.height = self.hcam.get_Size()
                    bufsize = ((self.width * 24 + 31) // 32 * 4) * self.height
                    # print('image size: {} x {}, bufsize = {}'.format(width, height, bufsize))
                    self.buf = bytes(bufsize)
                    if self.buf:
                        try:
                            # Start camera
                            self.hcam.StartPullModeWithCallback(self.cameraCallback, self)
                        except amcam.HRESULTException as ex:
                            print('Failed to start camera, hr=0x{:x}'.format(ex.hr))
                    print("Camera started successfully")
                # finally:
                #     self.closeCam()
                #     print("Closed cam")
            else:
                print('Failed to open camera')
        else:
            print('No camera found')
    
    def snapImage(self, path, res = 0):
        '''Trigger still image capture and set save path.'''
        # print('Snapping!')
        self.saved = False
        try:
            self.hcam.Snap(res)
        except:
            print(f"ERROR: Could not snap still image for path: {path}")
        else:
            # print('Snapped')
            self.stillPath = path
    
    def closeCam(self):
        print("Closing")
        if self.hcam:
            self.hcam.Close()
            self.hcam = None
        self.buf = None
        self.stillBuf = None
        self.stillSize = None
        self.lastFrame = None

    @staticmethod
    def cameraCallback(nEvent, ctx):
        '''Handle amcam events and distribute to subfunctions.'''
        if nEvent == amcam.AMCAM_EVENT_IMAGE:
            ctx.PreviewCallback(nEvent)
        elif nEvent == amcam.AMCAM_EVENT_STILLIMAGE:
            # print("Still")
            ctx.StillCallback(nEvent)

    def PreviewCallback(self, nEvent):
        '''Handle preview (streamed) image updates from amcam.'''
        if nEvent == amcam.AMCAM_EVENT_IMAGE and self.liveCallback is not None:
            try:
                # Pull image data from camera
                self.hcam.PullImageV2(self.buf, 24, None)
                # Construct image from bytes and manipulate as needed (rotate, flip, etc.)
                # self.lastFrame = Image.frombytes('RGB', self.hcam.get_Size(), self.buf).rotate(90, expand=True).transpose(Image.FLIP_TOP_BOTTOM)
                # Call callback provided to app in initialization so calling application can do something with the lastFrame (show it, save it, etc.)
                self.liveCallback()
            except amcam.HRESULTException as ex:
                print('pull image failed, hr=0x{:x}'.format(ex.hr))
        else:
            print('event callback: {}'.format(nEvent))
        
    
    def StillCallback(self, nEvent):
        '''Handle still (snapped) image updates from amcam.'''
        if nEvent == amcam.AMCAM_EVENT_STILLIMAGE:
            try:
                # Pull image data from camera
                self.hcam.PullStillImageV2(self.stillBuf, 24, None)
            except amcam.HRESULTException as ex:
                print('pull still image failed, hr=0x{:x}'.format(ex.hr))
            else:
                try:
                    # Construct image from bytes and manipulate as needed (rotate, flip, etc.)
                    image = Image.frombytes('RGB', self.stillSize, self.stillBuf).rotate(90, expand=True).transpose(Image.FLIP_TOP_BOTTOM)
                    # Save image to path
                    image.save(f"{self.stillPath}.png")
                    # print(f'saved to {self.stillPath}')
                except:
                    print(f'Error writing still image to {self.stillPath}')
            self.saved = True
        else:
            print('event callback: {}'.format(nEvent))
    
    def run(self):
        self.setupCamera()

    def setCameraSettings(self,
                          exposureTimeMs= 3.162,
                          exposureGainPercent= 133,
                          whiteBal = [5233, 1211],
                          contrast = 20,
                          color = True,
                          rotate = 0,
                          flipH = False,
                          flipV = False,
                          sharpen = 100,
                          demosaic = 4):
        if self.hcam:
            try:
                self.hcam.put_AutoExpoEnable(False)
                self.hcam.put_ExpoTime(int(exposureTimeMs*1000))
                print(f'Exposure Time: {self.hcam.get_ExpoTime()}')
                self.hcam.put_ExpoAGain(exposureGainPercent)
                print(f'Exposure Gain: {self.hcam.get_ExpoAGain()}')

                if warnRangeSetting('Color Temperature', 2000, 15000, whiteBal[0]) or warnRangeSetting('Color Tint', 200, 2500, whiteBal[1]):
                    return False
                self.hcam.put_TempTint(whiteBal[0], whiteBal[1])
                print(f'White Balance: {self.hcam.get_TempTint()}')

                if warnRangeSetting('Contrast', -100, 100, contrast):
                    return False
                self.hcam.put_Contrast(contrast)
                print(f'Contrast: {self.hcam.get_Contrast()}')

                if type(color) is not bool:
                    print("Incorrect setting for color!")
                    return False
                self.hcam.put_Chrome(color)

                if type(rotate) is not int or rotate not in [0, 90, 180, 270]:
                    print("Incorrect setting for rotate!")
                    return False
                self.hcam.put_Option(amcam.AMCAM_OPTION_ROTATE, rotate)

                if type(flipH) is not bool:
                    print("Incorrect setting for flipH!")
                    return False
                self.hcam.put_HFlip(flipH)

                if type(flipV) is not bool:
                    print("Incorrect setting for flipV!")
                    return False
                self.hcam.put_VFlip(flipV)

                if warnRangeSetting('Sharpen', 0, 500, sharpen):
                    return False
                self.hcam.put_Option(amcam.AMCAM_OPTION_SHARPENING, sharpen)
                print(f'Sharpen: {self.hcam.get_Option(amcam.AMCAM_OPTION_SHARPENING)}')

                if warnRangeSetting('Demosaic', 0, 4, demosaic):
                    return False
                self.hcam.put_Option(amcam.AMCAM_OPTION_DEMOSAIC, demosaic)
                print(f'Demosaic: {self.hcam.get_Option(amcam.AMCAM_OPTION_DEMOSAIC)}')
            except Exception as e:
                print("Error updating camera settings\n")
                print(e)
                return False
        return True