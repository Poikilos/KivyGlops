#!/usr/bin/env python

"""
This module contains classes for storing and retrieving real-time input
data such as key states
"""

import traceback

# class KivyRealTimeKeyState(PyRealTimeKeyState):
#     pass
#
# class KivyRealTimeController(PyRealTimeController):
#     pass
#

MODE_EDIT = "edit"
MODE_GAME = "game"


class PyRealTimeKeyState:
    state = None
    text = None

    def __init__(self):
        self.state = False
        self.text = ""


class PyRealTimeController:

    _keystates = None

    def __init__(self):
        self._keystates = dict()

    def set_pressed(self, index, text, state):
        try:
            if index not in self._keystates:
                self._keystates[index] = PyRealTimeKeyState()
            if state is not None:
                self._keystates[index].state = state
            if text is not None:
                self._keystates[index].text = text
        except:  # Exception as e:
            print("Could not finish set_pressed: "+str(traceback.format_exc()))

    def dump(self):
        print(self._keystates)

    # returns: True if pressing button or key number
    def get_pressed(self, index):
        return_pressing = False
        try:
            if index in self._keystates:
                if self._keystates[index] is not None:
                    return_pressing = self._keystates[index].state
        except:
            print("Could not finish get_pressed: "+str(traceback.format_exc()))
        return return_pressing
