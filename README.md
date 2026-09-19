# Launchpad X — Machinedrum / Monomachine Control Layouts

## Purpose

The scripts put a Novation Launchpad X into Programmer Mode. Programmer Mode maps each pad to one MIDI note. The scripts set a static color for each pad. Pressing a pad sends the same note number that lights it.

The layouts match the panel controls of the Machinedrum and Monomachine emulators. Use the pads to trigger and control the emulators over MIDI.

## Files

- `lpx_MD_layout.py` — Machinedrum layout. Run this script to light the pads.
- `lpx_MD_layout.png` — Picture of the Machinedrum layout.
- `lpx_MM_layout.py` — Monomachine layout. Run this script to light the pads.
- `lpx_MM_layout.png` — Picture of the Monomachine layout.

## Requirements

Install two Python packages before you run a script.

```
pip3 install mido python-rtmidi
```

## Usage

Connect the Launchpad X to the computer. Run the script for the layout you need.

```
python3 lpx_MD_layout.py
```

```
python3 lpx_MM_layout.py
```

The script finds the Launchpad X MIDI port and sends the layout. The pads stay lit. The computer does not need to stay connected after the script runs.

List the available MIDI ports:

```
python3 lpx_MD_layout.py --list
```

Return the Launchpad X to Live Mode:

```
python3 lpx_MD_layout.py --exit
```

## Port selection

The Launchpad X exposes two MIDI ports: DAW In and MIDI In. The scripts use MIDI In only. DAW In does not accept raw Note or SysEx messages.

## Layout rules

Each layout includes only the panel's primary buttons. Each panel prints two label styles:

- Black text on a light background marks the primary function of a button.
- White text on a dark background marks a combination. A combination needs the FUNCTION button held down.

The scripts do not map combinations. A combination is already reachable through the FUNCTION pad plus the pad for the button it modifies.

## Editing a layout

Each script contains a `LAYOUT` dictionary. Each entry maps a grid position to a label and a color. Row 1 is the bottom row. Row 8 is the top row. Column 1 is the left column.

Edit the `LAYOUT` dictionary to change the mapping. Keep the script and the picture in sync.
