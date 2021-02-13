#!/bin/env python
'''
View code by parsing python dumps.
'''
import sys
import os
import json
import threading

import kivy
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import StringProperty
from kivy.clock import Clock

def dump_to_json(s):
    s = s.replace("'", '"')
    s = s.replace("(", "[").replace(")", "]")  # tuple
    s = s.replace("True", 'true')
    s = s.replace("False", 'false')
    s = s.replace("None", 'null')
    s = s.replace("\n", " ")  # fix multiline strings etc
    return s

dump_to_json.__doc__ = '''
Transform Python dumped dict such as:

{'Player':
{'inventory selected': '<no slot>', 'name': 'Player 1', 'angles': '-5.5592 -19.599 0.0   ', 'dst_angles': '-5.5592 -19.599 0.0   ', 'free': True,
  'pos': (0.36561642961720947, 0.0, -0.04539086108880123), 'check_pos_enable': True, 'land_speed': 12.5, 'hp': 1.0, 'clip_enable': True
}
, 'camera_glop':
{'pitch': '-5.559265562184036', 'yaw': '-19.5994993233711', 'roll': '0.0',
  'pos': '0.339 1.7  -0.04'
}
, 'View':
{'mouse_pos': '(356.0, 281.0)', 'size': '(800, 600)', 'pitch,yaw': '(-19, -5)', 'screen_angles.xy': '-19.59 -5.559', 'camera xyz: ': '0.33921 1.7    -0.0435', 'modelview_mat': '[[ 0.335443 0.090837 -0.937671 0.000000 ]
[ 0.000000 0.995340 0.096424 0.000000 ]
[ 0.942060 -0.032345 0.333880 0.000000 ]
[ -0.072791 -1.724299 0.168680 1.000000 ]]', 'view_top_ratio': 0.6411360609438305, 'view_bottom_ratio': 0.2970943216985691, 'field of view': '(77, 61)', 'fps': '54.639837136787854'
}
, 'Chimp_Suzanne':
{
  'pos': (0.30468035801434123, 0.6882352551644062, 16.93384035832377)
}

}

to


'''

def error(msg):
    sys.stderr.write(msg + "\n")


def to_fvec(arr):
    results = []
    tmp = None
    if type(arr) == str:
        while "  " in arr:
            arr = arr.replace("  ", " ")
        tmp = arr.split(",")
        if len(tmp) == 1:
            tmp = arr.split(" ")
    else:
        tmp = arr
    for v in tmp:
        try:
            results.append(float(v))
        except ValueError as ex:
            print("to_fvec param: '''")
            print(str(arr))
            print("'''")
            raise ex
    return tuple(results)



class MetaLog:
    OPENERS = ["[", "(", "{"]
    MATCHES = {"[": "]", "(":")", "{":"}"}
    QUOTES = ['"', "'"]
    def __init__(self, sourceName, handler):
        self.sourceName = sourceName
        self.handler = handler
        self.braces = []
        self.quotes = []
        self.chunks = []  # string or dict
        self.gather = None
        pass

    def _on_chunk(self, chunk):
        if hasattr(chunk, 'items'):
            self._on_dict(chunk)
        else:
            colon = chunk.find(":")
            path = None
            if colon > 0:
                path = chunk[:colon]
                if not os.path.isfile(path):
                    path = None
            if path is not None:
                self._on_path(chunk)
            else:
                self._on_string(chunk)

    def on_path(self, path, line, msg):
        if hasattr(self.handler, 'on_path'):
            self.handler.on_path(path, line, msg)
        else:
            print("You can implement the on_path method"
                  " to handle paths.")

    def _on_path(self, chunk):
        '''
        Process a path and line.

        Sequential arguments:
        chunk -- a path and line such as:
                 '/home/owner/git/KivyGlops/kivyglops/__init__.py:3286:'
        '''
        parts = chunk.split(":")
        path = parts[0]
        line = int(parts[1])
        msg = ""
        if len(parts) > 3:
            msg = ":".join(parts[2:])
        elif len(parts) > 2:
            msg = parts[2]
        self.on_path(path, line, msg)

    def on_string(self, msg):
        if hasattr(self.handler, 'on_string'):
            self.handler.on_string(msg)
        else:
            print("You can implement the on_string method to"
                  " handle strings.")

    def _on_string(self, chunk):
        self.on_string(chunk)

    def on_dict(self, d):
        if hasattr(self.handler, 'on_dict'):
            self.handler.on_dict(d)
        else:
            print("You can implement the on_dict method to handle dicts.")

    def _on_dict(self, chunk):
        self.on_dict(chunk)

    def pushLine(self, line, lineNumber):
        line = line.rstrip()
        cI = 0  # Increment before use.
        prevC = None
        other = ""
        for c in line:
            cI += 1
            if len(self.quotes) > 0:
                if (not prevC == "\\") and (c in self.QUOTES):
                    if c == self.quotes[-1]:
                        self.quotes = self.quotes[:-1]
                    else:
                        self.quotes.append(c)
            elif c in self.QUOTES:
                self.quotes.append(c)

            if (c == "{") and (len(self.quotes) < 1):
                self.braces.append("{")
                if self.gather is None:
                    self.gather = c
                else:
                    self.gather += c
            elif (c == "}") and (len(self.quotes) < 1):
                if len(self.braces) > 0:
                    if self.gather is None:
                        error("{}:{}:{}: {}".format(
                            self.sourceName,
                            lineNumber,
                            cI,
                            "unexpected {}".format(c),
                        ))
                        raise RuntimeError("gather shouldn't be None"
                                           " if in braces.")
                    self.gather += c
                    self.braces = self.braces[:-1]
                    if len(self.braces) == 0:
                        gatherJson = dump_to_json(self.gather)
                        try:
                            self.chunks.append(json.loads(gatherJson))
                            # print("* added a dict.")
                        except json.decoder.JSONDecodeError as ex:
                            print("dump = '''")
                            print(self.gather)
                            print("'''")
                            print("json = '''")
                            print(gatherJson)
                            print("'''")
                            raise ex
                        self.gather = None
                else:
                    error("{}:{}:{}: {}".format(
                        self.sourceName,
                        lineNumber,
                        cI,
                        "There is an extra {}".format(c),
                    ))
                    other += c
            elif self.gather is not None:
                # ^ same effect as: len(self.braces) > 0:
                self.gather += c
            else:
                other += c
            prevC = c
        if len(self.braces) < 1:
            if len(other) > 0:
                self.chunks.append(other)

    def finalize(self):
        if len(self.quotes) > 0:
            print("WARNING: {} quotes aren't closed by the end of"
                  " \"{}\"".format(self.quotes, self.sourceName))
        if len(self.braces) > 0:
            print("WARNING: {} aren't closed by the end of"
                  " \"{}\"".format(self.braces, self.sourceName))


class Visualog(FloatLayout):
    logPath = StringProperty(None)
    frameSP = StringProperty("loading...")
    chunkSP = StringProperty("...")

    def __init__(self, **kwargs):
        self.chunkI = 0
        self.frameStartLine = None
        self.meta = None
        self.loaded = False
        self.values = {}
        self.labels = {}
        self.frame = 1
        super(Visualog, self).__init__(**kwargs)
        Clock.schedule_once(self._deferred_load, 0.5)
        self.paused = False

    def get_center(self):
        return self.size[0] / 2.0, self.size[1] / 2.0

    def from_center(self, pos):
        center = self.get_center()
        if len(pos) == 2:
            return center[0] + pos[0], center[1] + pos[1]
        else:
            # use x-z for ground plane if 3D:
            return center[0] + pos[0], center[1] + pos[2]

    def pause_pressed(self, instance):
        self.paused = not self.paused

    def show_frame(self):
        self.frameSP = "frame " + str(self.frame)
        # self.frameLabel.text = "frame " + str(self.frame)

    def show_chunk(self):
        self.chunkLabel.text = ("chunk {} of {}"
                                "".format(self.chunkI+1,
                                          len(self.meta.chunks)))

    def _deferred_load(self, dt):
        print("Loading: {}".format(self.logPath))
        print("_deferred_load: {} dt = {}"
              "".format(type(dt), dt))
        self.load(self.logPath)
        self.pauseBtn = Button(
            text="Pause",
            on_press=self.pause_pressed,
            size_hint=(0.1, 0.05)
        )
        self.add_widget(self.pauseBtn)
        self.frameLabel = Label(
            text=self.frameSP,
            size_hint=(0.1, 0.05),
            pos=(self.pauseBtn.right, 0)
        )
        self.add_widget(self.frameLabel)
        self.chunkLabel = Label(
            text=self.chunkSP,
            size_hint=(0.1, 0.05),
            pos=(self.frameLabel.right, 0)
        )
        self.add_widget(self.chunkLabel)
        Clock.schedule_interval(self.update_visuals, 1 / 10.)

    def on_dict(self, d):
        # print("on_dict...")
        # print(d)
        for actorName, actor in d.items():
            if hasattr(actor, 'items'):
                pos = None
                for k, v in actor.items():
                    if k == 'pos':
                        pos = to_fvec(v)
                        print("{}.pos: {}".format(actorName, v))
                        actorLabel = self.labels.get(actorName)
                        if actorLabel is None:
                            actorLabel = Label(
                                text=actorName,
                                size_hint=(0.1, 0.05),
                                pos=self.from_center(pos)
                            )
                            self.add_widget(actorLabel)
                            self.labels[actorName] = actorLabel
                        else:
                            actorLabel.pos = self.from_center(pos)

    def on_string(self, s):
        parts = s.split(":")
        if len(parts) == 2:
            k = parts[0]
            v = parts[1]
            if k in self.values:
                oldV = self.values[k]
                if oldV != v:
                    self.values[k] = v
                    # print(s)
            else:
                self.values[k] = v
                # print(s)
        else:
            pass
            # print(s)

    def on_path(self, path, line, msg):
        if path.endswith(os.path.join("kivyglops", "__init__.py")):
            if self.frameStartLine is None:
                self.frameStartLine = line
            elif line == self.frameStartLine:
                self.frame += 1
                self.show_frame()

    def update_visuals(self, dt):
        if not self.loaded:
            return
        if self.paused:
            return
        if self.chunkI < len(self.meta.chunks):
            chunk = self.meta.chunks[self.chunkI]
            self.meta._on_chunk(chunk)
            self.chunkI += 1
            self.show_chunk()
        pass

    def loadThread(self):
        print("* loading...")
        with open(self.meta.sourceName, 'r') as ins:
            lineNumber = 0  # Increment before use.
            for rawLine in ins:
                lineNumber += 1
                line = rawLine.rstrip()
                self.meta.pushLine(line, lineNumber)
        self.meta.finalize()
        self.loaded = True
        print("  * loading is complete")
        self.show_frame()

    def load(self, path):
        self.meta = MetaLog(path, self)
        threading.Thread(target = self.loadThread).start()


class VisualogApp(App):
    logPath = StringProperty(None)
    def build(self):
        window = Visualog()
        window.logPath = self.logPath
        return window


if __name__ == "__main__":
    app = VisualogApp()
    logPath = None
    if len(sys.argv) < 2:
        tryLog = "/home/owner/tmp/KivyGlops-debug/all--non-pdb.txt"
        if os.path.isfile(tryLog):
            logPath = tryLog
        else:
            print("Error: You must specify verbose KivyGlops"
                  " standard output.")
    else:
        logPath = sys.argv[1]

    if logPath is not None:
        app.logPath = logPath
    print("Using app.logPath: {}".format(app.logPath))
    app.run()
