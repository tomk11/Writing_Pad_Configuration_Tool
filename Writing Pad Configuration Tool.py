# The screen grabbing section is based on the code from https://gist.github.com/initbrain/6628609
# Documentation for python-xlib here http://python-xlib.sourceforge.net/doc/html/index.html

import sys
import os
from Xlib import X, display, Xutil, xobject, Xcursorfont
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel

def XSelect():
    d = display.Display()
    screen = d.screen()
    # Draw on the root window (desktop surface)
    window = screen.root

    #cursor = xobject.cursor.Cursor(d, 0)
    #cursor = d.create_resource_object('cursor', 0)
    #cursor = xobject.drawable.Pixmap(d, 34)
    cursor = X.NONE
    window.grab_pointer(1, X.PointerMotionMask|X.ButtonReleaseMask|X.ButtonPressMask, X.GrabModeAsync, X.GrabModeAsync, X.NONE, cursor, X.CurrentTime)

    #window.grab_keyboard(1, X.GrabModeAsync, X.GrabModeAsync, X.CurrentTime)

    colormap = screen.default_colormap
    color = colormap.alloc_color(0, 0, 0)
    # Xor it because we'll draw with X.GXxor function
    xor_color = color.pixel ^ 0xffffff

    gc = window.create_gc(
        line_width = 3,
        line_style = X.LineSolid,
        fill_style = X.FillOpaqueStippled,
        fill_rule  = X.WindingRule,
        cap_style  = X.CapButt,
        join_style = X.JoinMiter,
        foreground = xor_color,
        background = screen.black_pixel,
        function = X.GXxor,
        graphics_exposures = False,
        subwindow_mode = X.IncludeInferiors,
    )

    done    = False
    started = False
    start   = dict(x=0, y=0)
    end     = dict(x=0, y=0)
    last    = None
    drawlimit = 10
    i = 0

    while done == False:
        e = d.next_event()

        # Window has been destroyed, quit
        if e.type == X.DestroyNotify:
            sys.exit(0)

        # Mouse button press
        elif e.type == X.ButtonPress and e.detail == 1:
            # e.detail == 1 --> left
            # e.detail == 3 --> right
            start = dict(x=e.root_x, y=e.root_y)
            started = True

        # Mouse button release
        elif e.type == X.ButtonRelease:
            end = dict(x=e.root_x, y=e.root_y)
            if last:
                draw_rectangle(start, last, window, gc)
            done = True
            pass

        # Mouse movement
        elif e.type == X.MotionNotify and started:
            i = i + 1
            if i % drawlimit != 0:
                continue

            if last:
                draw_rectangle(start, last, window, gc)
                last = None

            last = dict(x=e.root_x, y=e.root_y)
            draw_rectangle(start, last, window, gc)
            pass

        # Keyboard key
        elif e.type == X.KeyPress:
            sys.exit(0)

    d.ungrab_pointer(0)
    d.flush()

    coords = get_coords(start, end)
    area = (coords['start']['x'], coords['start']['y'], coords['width'], coords['height'])
    return area


def get_coords(start, end):
    safe_start = dict(x=0, y=0)
    safe_end   = dict(x=0, y=0)

    if start['x'] > end['x']:
        safe_start['x'] = end['x']
        safe_end['x']   = start['x']
    else:
        safe_start['x'] = start['x']
        safe_end['x']   = end['x']

    if start['y'] > end['y']:
        safe_start['y'] = end['y']
        safe_end['y']   = start['y']
    else:
        safe_start['y'] = start['y']
        safe_end['y']   = end['y']

    return {
        'start': {
            'x': safe_start['x'],
            'y': safe_start['y'],
        },
        'end': {
            'x': safe_end['x'],
            'y': safe_end['y'],
        },
        'width' : safe_end['x'] - safe_start['x'],
        'height': safe_end['y'] - safe_start['y'],
    }

def draw_rectangle(start, end, window, gc):
    coords = get_coords(start, end)
    window.rectangle(gc,
        coords['start']['x'],
        coords['start']['y'],
        coords['end']['x'] - coords['start']['x'],
        coords['end']['y'] - coords['start']['y']
    )


def getCommand(coords):
    screenRes = (1366.0, 768.0)

    xstart = coords[0]
    ystart = coords[1]

    xsize = coords[2]
    ysize = coords[3]

    xtotal = screenRes[0]
    ytotal = screenRes[1]
    command = 'xinput set-prop "HUION H420 Pen" --type=float "Coordinate Transformation Matrix" '
    command +=  str(xsize/xtotal)  + ' 0 ' + str(xstart/xtotal) + ' 0 ' +  str(ysize/ytotal)  + ' ' + str(ystart/ytotal) + ' 0 0 1'
    return command

class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.button = QPushButton('Set Area', self)
        self.label = QLabel(self)
        self.label.setText("Select the screen area you wish to use your writing pad with")
        self.button.clicked.connect(self.handleButton)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.button)

    def handleButton(self):
        area = XSelect()
        os.system(getCommand(area))


if __name__ == '__main__':

        app = QApplication(sys.argv)
        window = Window()
        window.setWindowTitle('Writing Pad Configurer')
        window.show()
        window.resize(250,150)
        sys.exit(app.exec_())
