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

from kivyglops.common import *
MODE_EDIT = "edit"
MODE_GAME = "game"


class PyRealTimeKeyState:
    '''
    Properties:
    state -- Set to True (pressed) or False.
    text -- Set to the name of the key (ignores key mapping; allows
        typing even though mapping is used).
    '''

    def __init__(self):
        self.state = False
        self.text = ""


class PyRealTimeController:
    '''
    Properties:
    _requested_keys -- Set this to one of the entries in _keymaps,
        so _requested_keys['left'] is the left key such as "a", etc.
    _tried_other_keys -- Store a list of unmapped keys pressed (such
        as for debugging).
    '''
    def __init__(self):
        self._sequence = ""
        self._requested_keys = None
        self._keyNames = None
        self._tried_other_keys = []
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
                'use': 'enter',
            },
            'colemak': {
                'left': 'a',
                'down': 'r',
                'right': 's',
                'up': 'w',
                'use': 'enter',
            },
        }
        self.set_keymap("qwerty")
        self._keymap = "qwerty"
        self._seq_commands = {}
        for k, v in self._sequences.items():
            self._seq_commands[v] = k
        self._sequence_max = 5
        self._key_states = {}
        self._input_states = {}

    def set_keymap(self, name):
        keymap = self._keymaps.get(name)
        if keymap is None:
            print("Error: \"{}\" is not an implemented keymap."
                  " Try any of: {}"
                  "".format(name, list(self._keymaps.keys())))
            return False
        self._requested_keys = keymap
        self._keyNames = {}
        for name, key in self._requested_keys.items():
            self._keyNames[key] = name
        self._keymap = name

    def get_keymap_dict(self):
        return self._requested_keys

    def set_pressed(self, index, text, state):
        # A series of keys can have a special meaning:
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
            if self._key_states.get(index) is None:
                self._key_states[index] = PyRealTimeKeyState()
            if state is not None:
                self._key_states[index].state = state
            if text is not None:
                self._key_states[index].text = text
        except:  # Exception as e:
            print("Could not finish set_pressed({},...): {}"
                  "".format(index, traceback.format_exc()))
        name = self._keyNames.get(text.lower())
        if name is not None:
            self._input_states[name] = state
        else:
            if text not in self._tried_other_keys:
                self._tried_other_keys.append(text)
            # print("{} is not a mapped key.".format(text.lower()))

    def dump(self):
        print(self._key_states)

    def get_input(self, name):
        '''
        Get True if the button or key number with the given name
        is being pressed, otherwise get False.

        Sequential arguments:
        name -- The name must be a named key in the
            _requested_keys keymap such as 'left'.
        '''
        return self._input_states.get(name)

    def _get_key_state_at(self, index):
        '''
        (formerly get_pressed)
        Get True if the button or key number `index`
        is being pressed, otherwise get False.
        '''
        return_pressing = False
        try:
            if index in self._key_states:
                if self._key_states[index] is not None:
                    return_pressing = self._key_states[index].state
        except:
            print("Could not finish _get_key_state_at: "
                  + str(traceback.format_exc()))
        return return_pressing
