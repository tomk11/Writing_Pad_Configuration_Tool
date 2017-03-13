#!/usr/bin/env python

from __future__ import division
import cairo
from gi.repository import Gtk, Gdk
from Xlib import X, display, Xutil, xobject, Xcursorfont
import sys, os

class AreaSelector(Gtk.Window):
    def __init__(self):
        super(AreaSelector, self).__init__()
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(20)
        self.screen = self.get_screen()
        self.visual = self.screen.get_rgba_visual()

        # Set transparancy if possible
        if self.visual != None and self.screen.is_composited():
            self.set_visual(self.visual)

        # Remove window borders
        self.set_decorated(False)

        # Set the entire window to be a button - which moves the main window
        box = Gtk.EventBox()
        box.connect ('button-press-event', lambda widget, event: self.begin_move_drag(1, int(event.x_root), int(event.y_root), event.time))
        self.add(box)

        # Transparency and colouring
        self.set_app_paintable(True)
        self.connect("draw", self.area_draw)
        self.show_all()

    def area_draw(self, widget, cr):
        cr.set_source_rgba(.7, .7, .7, 0.5)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)


def getCommand(coords):
    window = Gtk.Window()
    screen = window.get_screen()
    screenRes = (screen.get_width(), screen.get_height())
    print(screenRes)

    xstart = coords[0]
    ystart = coords[1]

    xsize = coords[2]
    ysize = coords[3]

    xtotal = screenRes[0]
    ytotal = screenRes[1]
    command = 'xinput set-prop "HUION H420 Pen" --type=float "Coordinate Transformation Matrix" '
    command +=  str(xsize/xtotal)  + ' 0 ' + str(xstart/xtotal) + ' 0 ' +  str(ysize/ytotal)  + ' ' + str(ystart/ytotal) + ' 0 0 1'
    print(command)
    return command

class MainWindow (Gtk.Window):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(30)
        self.screen = self.get_screen()

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        setAreaButton = Gtk.Button(label="Set Writing Pad Area")
        setAreaButton.connect('clicked', self.setArea)
        vbox.add(setAreaButton)

        applyButton = Gtk.Button(label="Apply")
        applyButton.connect('clicked', self.apply)
        vbox.add(applyButton)

        errorReportButton = Gtk.Button(label="Send Error Report")
        errorReportButton.connect('clicked', self.generateErrorReport)
        vbox.add(errorReportButton)

        label = Gtk.Label('Select the area on your screen you want to map your writing pad to.')
        label.set_line_wrap(1)
        vbox.add(label)

        self.show_all()
        self.connect("delete-event", self.safeExit)

    def safeExit(self,*events):
        print(events)
        sys.exit(0)

    def generateErrorReport(self, event):
        print(os.system('xinput list'))

    def setArea(self, event):
        print(event)
        if hasattr(self,'selector'):
            self.selector.show()
        else:
            self.selector = AreaSelector()

    def apply(self, event):
        if hasattr(self,'selector'):
            position = self.selector.get_position()
            size = self.selector.get_size()
            print(position + size)
            self.selector.hide()
            command = getCommand(position+size)
            os.system(command)


MainWindow()
Gtk.main()