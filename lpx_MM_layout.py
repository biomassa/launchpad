#!/usr/bin/env python3
"""
Light the full Monomachine panel layout on a Novation Launchpad X using
Programmer Mode + static-color Note On messages. Pads keep this lighting
with no host connection required.

Programmer Mode's 8x8 grid is fixed to Note messages (not CC) -- see
Novation's Programmer's Reference Guide. Pressing a pad also emits a
Note On/Off on the same note number, so this is both the lighting map
and the control map.

Requires: pip3 install mido python-rtmidi
"""

import sys
import time
import mido

SYSEX_HEADER = [0x00, 0x20, 0x29, 0x02, 0x0C]

def enter_programmer_mode(port):
    port.send(mido.Message('sysex', data=SYSEX_HEADER + [0x0E, 0x01]))

def exit_programmer_mode(port):
    port.send(mido.Message('sysex', data=SYSEX_HEADER + [0x0E, 0x00]))

def pad_note(row, col):
    """row 1-8 (1=bottom), col 1-8 (1=left) -> Programmer Mode note number."""
    return row * 10 + col

def set_pad_color(port, note, color, channel=0):
    # channel 0 = MIDI channel 1 = static color mode
    port.send(mido.Message('note_on', channel=channel, note=note, velocity=color))

def list_ports():
    print("Available MIDI output ports:")
    for i, name in enumerate(mido.get_output_names()):
        print(f"  [{i}] {name}")

def find_launchpad_port():
    names = mido.get_output_names()
    # Must target the MIDI In port, not DAW In -- DAW In speaks Ableton's
    # control-surface protocol and ignores raw SysEx/Note lighting.
    return [n for n in names
            if 'launchpad' in n.lower() and 'x' in n.lower() and 'daw' not in n.lower()]

# Confirmed Novation palette indices:
#   0 = off, 1 = dim white, 3 = white, 5 = red, 13 = yellow,
#   21 = green, 37 = cyan, 45 = blue, 53 = purple
RED    = 5
YELLOW = 13
GREEN  = 21
CYAN   = 37
BLUE   = 45
PURPLE = 53
WHITE  = 3

# (row, col): (label, color) -- row 1 = bottom, row 8 = top; col 1 = left, col 8 = right
#
# Dropped as FUNCTION combos, not standalone buttons:
#   MUTE 1-6 (FUNCTION + TRACK n), ARP/TRANSP/SWING/SLIDE (combo legends
#   under BANK's A/E-D/H buttons), MUTE MODE (combo of BANK), COPY/CLEAR/
#   PASTE (combo of REC/PLAY/STOP), MIDI SEQ (combo of TRIG SELECT).
LAYOUT = {
    # TRACK 1-6 as a vertical stack, right edge (col 8), top-to-bottom --
    # matching the panel's own vertical arrangement.
    (8, 8): ("TRACK 1", GREEN),
    (7, 8): ("TRACK 2", GREEN),
    (6, 8): ("TRACK 3", GREEN),
    (5, 8): ("TRACK 4", GREEN),
    (4, 8): ("TRACK 5", GREEN),
    (3, 8): ("TRACK 6", GREEN),

    # Utility column, col 7, parallel to the TRACK stack --
    (6, 7): ("TEMPO",     PURPLE),
    (5, 7): ("EDIT UP",   CYAN),
    (4, 7): ("EDIT DOWN", CYAN),

    (7, 1): ("BANK", GREEN),
    (7, 2): ("A/E",  GREEN),
    (7, 3): ("B/F",  GREEN),
    (7, 4): ("C/G",  GREEN),
    (7, 5): ("D/H",  GREEN),

    (6, 2): ("ENTER/YES", CYAN),
    (6, 5): ("UP",        BLUE),

    (5, 2): ("EXIT/NO", CYAN),
    (5, 4): ("LEFT",    BLUE),
    (5, 5): ("DOWN",    BLUE),
    (5, 6): ("RIGHT",   BLUE),

    (4, 3): ("REC",  RED),
    (4, 4): ("PLAY", GREEN),
    (4, 5): ("STOP", WHITE),

    (3, 1): ("FUNCTION",      WHITE),
    (3, 2): ("KIT/SONG SETUP", YELLOW),
    (3, 3): ("PATTERN/SONG",   YELLOW),
    (3, 6): ("TRIG SELECT",    PURPLE),
    (3, 7): ("SCALE SETUP",    YELLOW),

    (2, 1): ("1", RED), (2, 2): ("2", RED), (2, 3): ("3", RED), (2, 4): ("4", RED),
    (2, 5): ("5", RED), (2, 6): ("6", RED), (2, 7): ("7", RED), (2, 8): ("8", RED),
    (1, 1): ("9", RED), (1, 2): ("10", RED), (1, 3): ("11", RED), (1, 4): ("12", RED),
    (1, 5): ("13", RED), (1, 6): ("14", RED), (1, 7): ("15", RED), (1, 8): ("16", RED),
}

if __name__ == '__main__':
    if '--list' in sys.argv:
        list_ports()
        sys.exit(0)

    candidates = find_launchpad_port()
    if not candidates:
        print("No Launchpad X port auto-detected. Run with --list to see all ports,")
        print("then edit PORT_NAME below to match exactly.")
        sys.exit(1)

    if len(candidates) > 1:
        print("Multiple matching ports found (device usually exposes two):")
        for c in candidates:
            print(" -", c)
        print("Using the first match. Edit PORT_NAME below to force a specific one.")

    PORT_NAME = candidates[0]
    print(f"Using port: {PORT_NAME}")

    with mido.open_output(PORT_NAME) as port:
        enter_programmer_mode(port)
        time.sleep(0.1)

        # Clear the entire 8x8 grid first. Programmer Mode pads keep
        # whatever color they were last sent -- without this, pads lit
        # by a previous run that are no longer in LAYOUT stay lit,
        # superimposed on the current layout.
        for row in range(1, 9):
            for col in range(1, 9):
                set_pad_color(port, pad_note(row, col), 0)
        time.sleep(0.05)

        for (row, col), (label, color) in LAYOUT.items():
            note = pad_note(row, col)
            set_pad_color(port, note, color)
            print(f"  row {row} col {col}  note {note:3d}  {label}")

        print(f"\n{len(LAYOUT)} pads lit (grid cleared first).")
        print("Colors stay set with no host connection.")
        print("Run with --exit to return the device to Live mode (add that flag if needed).")

    if '--exit' in sys.argv:
        with mido.open_output(PORT_NAME) as port:
            exit_programmer_mode(port)
            print("Returned to Live mode.")
