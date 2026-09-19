#!/usr/bin/env python3
"""
Light the full Machinedrum panel layout on a Novation Launchpad X using
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

# Confirmed Novation palette indices (from Novation docs / hardware reference):
#   0 = off, 1 = dim white, 3 = white, 5 = red, 13 = yellow,
#   21 = green, 37 = cyan, 45 = blue, 53 = purple
RED    = 5
YELLOW = 13
GREEN  = 21
CYAN   = 37
BLUE   = 45
PURPLE = 53
WHITE  = 3

# (row, col): (label, color)
# row 1 = bottom, row 8 = top; col 1 = left, col 8 = right
#
# Laid out to approximate the physical topology of the Machinedrum panel,
# not grouped by our own functional taxonomy. Gaps are intentional --
# empty cells are left out of this dict entirely and stay dark.
#
# Exclusions (not separate physical buttons, so no pad):
#   COPY/CLEAR/PASTE -- these are the FUNCTION-modified secondary legends
#     printed under REC/PLAY/STOP (FUNCTION+REC=COPY, FUNCTION+PLAY=CLEAR,
#     FUNCTION+STOP=PASTE per the manual). REC/PLAY/STOP and FUNCTION
#     already have pads; no combo needs its own pad.
#   SYNTHESIS/EFFECTS/ROUTING -- the manual refers to this as ONE key
#     ("the [SYNTHESIS/EFFECTS/ROUTING] key") that cycles 3 LED states,
#     not three separate buttons. Collapsed to one pad.
#   1:4/2:4/3:4/4:4 -- read as status LEDs for trig resolution, not
#     independently pressable. Left off pending confirmation.
#
# Confirmed by the user directly against the panel's own label coloring
# (black-on-white = primary/direct function, white-on-maroon = FUNCTION+
# combo, printed as a secondary legend on the same physical button):
#   - The 4 buttons under BANK GROUP are primary-labeled A/E, B/F, C/G,
#     D/H (pattern select). MUTE/ACCENT/SWING/SLIDE are their combo
#     legends -- dropped, achieved via FUNCTION + these same pads.
#   - KIT is the primary label under the bracket; SONG SETUP is that
#     button's combo legend -- dropped, replaced with KIT.
#   - GLOBAL is a combo legend on the PATTERN/SONG button (matches the
#     manual: FUNCTION+PATTERN/SONG opens Global Settings) -- dropped,
#     no separate pad; PATTERN/SONG already has one.
#   - LFO is a combo legend, not a standalone button -- dropped entirely.
LAYOUT = {
    # Row 8 -- top knob-adjacent row -- PURPLE
    (8, 2): ("CLASSIC/EXTENDED", PURPLE),

    # Row 7 -- pattern select strip (Bank Group + its 4 pattern buttons) -- GREEN
    (7, 1): ("BANK GROUP", GREEN),
    (7, 2): ("A/E",        GREEN),
    (7, 3): ("B/F",        GREEN),
    (7, 4): ("C/G",        GREEN),
    (7, 5): ("D/H",        GREEN),

    # Rows 6-5 -- real D-pad shape, matching the panel photo exactly:
    # UP centered directly above DOWN, LEFT/RIGHT flanking DOWN,
    # ENTER stacked above EXIT one column to the left with a gap between --
    (6, 2): ("ENTER/YES", CYAN),   # recolored: takes PLAY/STOP's old cyan
    (6, 5): ("UP",        BLUE),
    (6, 8): ("TEMPO",     PURPLE),  # moved: above SYNTH/FX/ROUTE's new spot
    (5, 2): ("EXIT/NO",   CYAN),   # recolored: takes PLAY/STOP's old cyan
    (5, 4): ("LEFT",      BLUE),
    (5, 5): ("DOWN",      BLUE),
    (5, 6): ("RIGHT",     BLUE),
    (5, 8): ("SYNTH/FX/ROUTE", PURPLE),  # moved: above KIT

    # Row 4 -- transport + kit/pattern-mgmt cluster, one contiguous row,
    # right-aligned, matching the panel photo's own horizontal layout:
    # REC/PLAY/STOP, then a blank, then the last two (PATTERN/SONG, KIT).
    (4, 1): ("SCALE SETUP",  YELLOW),
    (4, 3): ("REC",          RED),
    (4, 4): ("PLAY",         GREEN),
    (4, 5): ("STOP",         WHITE),
    (4, 7): ("PATTERN/SONG", YELLOW),
    (4, 8): ("KIT",          YELLOW),

    # Row 3 -- mostly an intentional unlit gap before the triggers;
    # FUNCTION lives here alone, one-off white, held as a modifier for
    # every combo above --
    (3, 1): ("FUNCTION", WHITE),

    # Row 2 -- triggers 1-8 -- RED
    (2, 1): ("BD", RED),
    (2, 2): ("SD", RED),
    (2, 3): ("HT", RED),
    (2, 4): ("MT", RED),
    (2, 5): ("LT", RED),
    (2, 6): ("CP", RED),
    (2, 7): ("RS", RED),
    (2, 8): ("CB", RED),

    # Row 1 (bottom) -- triggers 9-16 -- RED
    (1, 1): ("CH", RED),
    (1, 2): ("OH", RED),
    (1, 3): ("RC", RED),
    (1, 4): ("CC", RED),
    (1, 5): ("M1", RED),
    (1, 6): ("M2", RED),
    (1, 7): ("M3", RED),
    (1, 8): ("M4", RED),
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

        print(f"\n{len(LAYOUT)} pads lit (grid cleared first). Rows 3 and unlisted cells left dark.")
        print("Colors stay set with no host connection.")
        print("Run with --exit to return the device to Live mode (add that flag if needed).")

    if '--exit' in sys.argv:
        with mido.open_output(PORT_NAME) as port:
            exit_programmer_mode(port)
            print("Returned to Live mode.")
