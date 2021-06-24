#!/usr/bin/env python

"""
This module contains classes for storing and retrieving real-time input
data such as key states.
"""

import traceback

# class KivyRealTimeKeyState(PyRealTimeKeyState):
#     pass
#
# class KivyRealTimeController(PyRealTimeController):
#     pass
#

from common import *
MODE_EDIT = "edit"
MODE_GAME = "game"


class PyRealTimeKeyState:
    state = None
    text = None

    def __init__(self):
        self.state = False
        self.text = ""


class PyRealTimeController:

    def __init__(self):
        self._sequence = ""
        self._requested_keys = None
        self._sequences = {
            'asd': "qwerty",
            'ars': "colemak",
        }
        self._keymaps = {
            'qwerty': {
                'left': 'a',
                'down': 's',
                'right': 'd',
                'up': 'w',
            },
            'colemak': {
                'left': 'a',
                'down': 'r',
                'right': 's',
                'up': 'w',
            },
        }
        self.set_keymap("qwerty")
        self._keymap = "qwerty"
        self._seq_commands = {}
        for k, v in self._sequences.items():
            self._seq_commands[v] = k
        self._sequence_max = 5
        self._keystates = {}

    def set_keymap(self, name):
        keymap = self._keymaps.get(name)
        if keymap is None:
            print("Error: \"{}\" is not an implemented keymap."
                  " Try any of: {}"
                  "".format(name, list(self._keymaps.keys())))
            return False
        self._requested_keys = keymap
        self._keymap = name

    def get_keymap_dict(self):
        return self._requested_keys

    def set_pressed(self, index, text, state):
        if not self._sequence.endswith(text):
            self._sequence += text
        if len(self._sequence) > self._sequence_max:
            remove_len = len(self._sequence) - self._sequence_max
            self._sequence = self._sequence[remove_len:]

        seq_op = None
        for k, v in self._sequences.items():
            if k in self._sequence:
                seq_op = v
                break

        colemak_seq = self._seq_commands['colemak']
        qwerty_seq = self._seq_commands['qwerty']
        # print("* sequence: {}".format(self._sequence))
        if (seq_op == "qwerty") and (self._keymap != "qwerty"):
            self.set_keymap("qwerty")
            print("* You switched to QWERTY asdw movement by typing"
                  " \"{}\""
                  " (type \"{}\" to switch to Colemak"
                  " arsw movement)"
                  "".format(qwerty_seq, colemak_seq))
        elif (seq_op == 'colemak') and (self._keymap != 'colemak'):
            self.set_keymap("colemak")
            print("* You switched to Colemak arsw movement by typing"
                  " \"{}\""
                  " (type \"{}\" to switch back to QWERTY"
                  " asdw movement)"
                  "".format(colemak_seq, qwerty_seq))

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

    def get_pressed(self, index):
        '''
        Get True if the button or key number `index`
        is being pressed, otherwise get False.
        '''
        return_pressing = False
        try:
            if index in self._keystates:
                if self._keystates[index] is not None:
                    return_pressing = self._keystates[index].state
        except:
            print("Could not finish get_pressed: "+str(traceback.format_exc()))
        return return_pressing
