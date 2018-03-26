# -*- coding: utf-8 -*-
# Developed by Ryan J. Quinlan
# Contact: rjq@rjqfx.com

import nuke
import nukescripts

# from PySide import QtGui
if nuke.NUKE_VERSION_MAJOR < 11:
    from PySide import QtCore, QtUiTools, QtGui, QtGui as QtWidgets
else:
    from PySide2 import QtGui, QtCore, QtUiTools, QtWidgets


def find_file_knobs(knobs):
    """Identifies File_Knob knobs.

    Creates a new set with identified File_Knobs within an iterator of knobs.
    :param knobs: iterator of knobs to search
    :type knobs: iterator
    :returns: set of File_Knobs
    :rtype: {set}
    """
    file_knobs = {k for k in knobs if isinstance(k, nuke.File_Knob) if k.getValue() != ""}
    return file_knobs

def find_range_knobs(knobs):
    """Identifies first and last frame of a node given information from its knobs

    Returns first and last frames from an iterator of knobs based on integer knobs either
    named "first" and "last" or that have "first" and "last" in the knob name.
    :param knobs: iterator of knobs to search through
    :type knobs: iterator
    :returns: first and last frame numbers
    :rtype: {int, int}
    """
    first = None
    last = None

    for knob in knobs:

        if isinstance(knob, nuke.Int_Knob) and knob.enabled():
            knob_name = knob.name()

            if knob_name == "first":
                first = int(knob.getValue())
                if last != None:
                    break

            elif knob_name == "last":
                last = int(knob.getValue())
                if first != None:
                    break

            elif first == None and knob_name.count("first"):
                first = int(knob.getValue())

            elif last == None and knob_name.count("last"):
                last = int(knob.getValue())

    return first, last

def find_file_info(node):
    """Searches through a node to identify if it contains file paths and frame ranges.

    Looks through all of a node's knobs to find File_Knobs with paths set and if there are
    first and last frame knobs.
    :param node: node to search
    :type node: Node
    :returns: list of paths and frame ranges for a single node
    :rtype: {list}
    """
    all_knobs = set(node.allKnobs())
    file_knobs = find_file_knobs(all_knobs)
    file_info = None

    if file_knobs:
        sequence = {pad for pad in file_knobs if (pad.getValue().count("#") or pad.getValue().count("%"))}
        first = None
        last = None

        if len(sequence) > 0:
            other_knobs = all_knobs.difference(file_knobs)
            first, last = find_range_knobs(other_knobs)

        if first and last:
            file_info = ["{0} {1}-{2}".format(file.getValue(), first, last) for file in file_knobs]
        else:
            file_info = [file.getValue() for file in file_knobs]

    return file_info

def copy_paths():
    ''' Copies file knob from selected nodes and put in a human friendly list.
    '''
    nodes = nuke.selectedNodes()

    if len(nodes) > 0:
        nodes.reverse()
        paths = []
        for node in nodes:
            path = find_file_info(node)
            if path:
                paths.extend(path)

        if paths:
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard.setText('\n'.join(paths))
        else:
            nuke.message("No file paths found")
