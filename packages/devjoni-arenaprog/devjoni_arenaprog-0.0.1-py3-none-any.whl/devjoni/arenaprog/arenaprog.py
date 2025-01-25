'''Arena GUI program
'''

import sys
import atexit
import platform

import devjoni.guibase as gb
from devjoni.hosguibase.video import VideoWidget

from .arenalib import Arena
from .cardstimgen import CardStimWidget

__version__ = '0.0.1'

IMAGE_UPDATE_INTERVAL = 10 # ms


class MovementView(gb.FrameWidget):
    '''Control the arena lift up and down
    '''

    def __init__(self, parent, arena):
        super().__init__(parent)

        self.arena = arena

        self.pos = gb.TextWidget(self, '')
        self.pos.set(text=f'{self.arena.pos}')
        self.pos.grid(row=0, column=0)

        self.move_buttons = []

        for i, N in enumerate([10,3,1,-1,-3,-10]):
            b = gb.ButtonWidget(
                    self, f'Move {N}',
                    lambda N=N: self.move(N)
                    )
            b.grid(row=i+1, column=0)
            self.move_buttons.append(b)

        align = gb.ButtonWidget(self, 'End-align', self.do_align)
        align.grid(row=i+2, column=0)
        

    def move(self, N_steps):
        self.arena.move_platform(N_steps)
        self.pos.set(text=f'{self.arena.pos} ')

    def do_align(self):
        self.arena.step_end_align()
        self.pos.set(text=f'{self.arena.pos}')


class LightView(gb.FrameWidget):
    '''Control the arena lights
    '''
    def __init__(self, parent, arena):
        super().__init__(parent)

        self.arena = arena
        
        self.led_buttons = []
        for i_led in range(self.arena.get_N_leds()):
            b = gb.ButtonWidget(self, f'LED {i_led+1}')
            b.grid(row=i_led, column=0)
            self.led_buttons.append(b)



class StimView(gb.FrameWidget):
    '''Control the stimulus presentation
    '''
    def __init__(self, parent):

        super().__init__(parent)

        self.b_generate = gb.ButtonWidget(
                self, 'Generate cards',
                command=self.generate_cards)
        self.b_generate.grid(row=0, column=0)
        
        self.b_open = gb.ButtonWidget(
                self, 'Open in window',
                command=self.open_window)
        self.b_open.grid(row=2, column=0)
        
        self.preview = CardStimWidget(self, 100, 100)
        self.preview.grid(row=1, column=0)

        self.view = None

    def generate_cards(self):
        self.preview.create_multipie_cards()
        self.preview.next_card()
    
        if self.view:
            self.view[1].create_multipie_cards()
            self.view[1].next_card()

    def open_window(self):
        
        if self.view is not None:
            toplevel, view = self.view
            view.destroy()
            toplevel.destroy()
            self.preview.next_card_callback = None

        root = self.get_root()    
        toplevel = gb.MainWindow(parent=root)
        
        view = CardStimWidget(toplevel, 300, 300)
        view.b_next.destroy()
        self.preview.next_card_callback = view.next_card
        view.grid()

        self.view = [toplevel, view]
        

class CameraControlView(gb.FrameWidget):
    '''Camera controls like start imaging, recording etc.

    Attributes
    ----------
    camera_view : obj or None
        A CameraView Widget to be controlled
    '''
    def __init__(self, parent, camera_view=None):
        super().__init__(parent)

        self.camera_view = camera_view

        self.play = gb.ButtonWidget(self, text='Play', command=self.play)
        self.play.grid(row=0, column=0)
        self.stop = gb.ButtonWidget(self, text='Stop', command=self.stop)
        self.stop.grid(row=0, column=1)
        
        self.change = gb.ButtonWidget(
                self, text='Change camera', command=self.next_camera)
        self.change.grid(row=0, column=2)
   
        self.record = gb.ButtonWidget(
                self, text='Record', command=self.record)
        self.record.grid(row=0, column=3)
        
        self.record_details = gb.TextWidget(
                self, text='')
        self.record_details.grid(row=0, column=4)
  

    def play(self):
        self.camera_view.play()

    def stop(self):
        self.camera_view.stop()
    
    def record(self):
        self.camera_view.record()
        if self.camera_view.do_record:
            self.record.set(bg="red")
            fn = self.camera_view.record_fn
            fps = self.camera_view.record_fps
            self.record_details.set(
                    text=f'{fn} @ {fps}'
                    )
        else:
            self.record.set(bg="gray")
            self.record_details.set(text='Recording finished')

    def next_camera(self):
        self.camera_view.next_camera()
        if self.camera_view.do_record:
            self.record.set(bg="gray")
            self.record_details.set(text='Recording finished')


class CameraView(gb.FrameWidget):
    '''Camera view using the opencv cameralib.
    '''
    def __init__(self, parent):
        super().__init__(parent)

        cams = detect_cameras()
        self.camera = MultiprocessCamera(cams[0])

        
        self.image = gb.ImageImage(None, 200,200)
        self.canvas = gb.ImageWidget(self, self.image)

        self.canvas.grid(0,0, sticky='NSWE')

        self._is_playing = False

        atexit.register(self.stop)

    def play(self):
        if self._is_playing:
            return
        self._is_playing = True
        self.camera.open()
        self.after(IMAGE_UPDATE_INTERVAL, self.tick)
        
    def stop(self):
        self._is_playing = False
        self.camera.close()


    def tick(self):
        if not self.camera.is_open():
            return
        im = self.camera.get_frame()
        if im is not None:
            print(im)
            self.canvas.image.set_from_rgb(im)
        
        if self._is_playing:
            self.after(IMAGE_UPDATE_INTERVAL, self.tick)


    def next_camera(self):
        pass


class FastCameraView(gb.FrameWidget):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.video = VideoWidget(self)
        self.video.grid()
        self.video.relative_size=0.75
        self.video.tcoder.source_type = "camera"

        self.ffmpeg_line = ''

        self.do_record = False
        self.record_fn = 'test.mp4'
        self.record_fps = 100

        cameras = self.video.tcoder.detect_cameras()
        if cameras:
            self.video.source = cameras[0]


    def play(self):
        if self.do_record:
            self.video.tcoder.set_video_output(
                    self.record_fn, fps=self.record_fps,
                    opts=[
                        '-c:v', 'libx264',
                        '-preset', 'ultrafast',
                        '-crf', '28',
                        ])
            
            # Enforce that the webcam is being read fast
            # Arducam UC-844
            system = platform.system()
            if system == 'Linux':
                opts = ['-f', 'v4l2', '-framerate', 100,
                        '-video_size', '1280x800', '-input_format',
                        'mjpeg']
            else:
                opts = ['-f', 'dshow', '-video_size', '1280x800',
                        '-framerate', 100, '-vcodec', 'mjpeg']
            self.video.tcoder.source_opts = opts
        else:
            self.video.tcoder.set_video_output(None)
            self.video.tcoder.source_opts = None
        self.video.start()

    def stop(self, stop_record=True):
        if self.do_record and stop_record:
            self.do_record = False
        self.video.stop()
    
    def record(self):
        if self.do_record:
            self.do_record = False
        else:
            self.do_record = True
        self.stop(stop_record=False)
        self.play()
    
    def next_camera(self):
        
        # Always stop recording when changing the camera
        if self.do_record:
            self.do_record=False
            self.stop()

        cameras = self.video.tcoder.detect_cameras()
        if not cameras:
            return
        
        if self.video.source not in cameras:
            camera = cameras[0]
        else:
            index = cameras.index(self.video.source)
            index += 1

            if index >= len(cameras):
                index = 0
            camera = cameras[index]
        
        print(camera)
        self.stop()
        self.video.source = camera
        self.play()


class TotalView(gb.FrameWidget):
    def __init__(self, parent):
        super().__init__(parent)

        # Camera side

        camerabox = gb.FrameWidget(self)
        camerabox.grid(row=0, column=1, rowspan=2)
        
        control = CameraControlView(camerabox)
        control.grid(row=0, column=0, sticky='')

        camera = FastCameraView(camerabox)
        camera.grid(row=1, column=0)

        control.camera_view = camera

        # Motion control side
        
        try:
            arena = Arena()
        except:
            arena = Arena(fake_serial=True)

        controlbox = gb.FrameWidget(self)
        controlbox.grid(row=0, column=0)
 
        movement = MovementView(controlbox, arena)
        movement.grid(row=0, column=0)
        
        light = LightView(controlbox, arena)
        light.grid(row=0, column=1)

        # Stimulus

        stim = StimView(self)
        stim.grid(row=1, column=0)


def main():

    window = gb.MainWindow()
    window.title = f'Arena Program - v{__version__}'

    view = TotalView(window)
    view.grid()


    window.run()

if __name__ == "__main__":
    main()
    #cProfile.run('main()')
