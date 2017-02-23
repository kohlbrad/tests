#!/usr/bin/env python
"""
Gmsh2R3t
========

Read Gmsh ASCII file and return mesh3d.dat for R3t.

Filename of the file to read (*.msh). The file must conform
to the `MSH ASCII file version 2 <http://geuz.org/gmsh/doc/
texinfo/gmsh.html#MSH-ASCII-file-format>`_ format.

Created on Nov 16, 2012
by fwagner@gfz-potsdam.de
"""

from os.path import basename
from Tkinter import Tk
from tkFileDialog import askopenfilename, asksaveasfilename
import tkMessageBox

# start gui, get filenames
gui = Tk()
gui.withdraw()
infile = askopenfilename(title='Choose Gmsh output file.', filetypes=[('Gmsh output', '.msh')])
gui.withdraw()
outfile = asksaveasfilename(title='Save mesh3d.dat for R3t.', filetypes=[('R3t mesh file', '.dat')], initialfile='mesh3d.dat')

# read gmsh file
inNodes, inElements, ncount, ecount = 0, 0, 0, 0
fid = open(infile)

for line in fid:

    if line[0] == '$':
        if line.find('Nodes') > 0: inNodes = 1
        if line.find('EndNodes') > 0: inNodes = 0
        if line.find('Elements') > 0: inElements = 1
        if line.find('EndElements') > 0: inElements = 0

    else:
        if inNodes == 1:
            if len(line.split()) == 1:
                nodes = []
            else:
                entry = map(float, line.split())[1:]
                nodes.append(entry)

        elif inElements == 1:
            if len(line.split()) == 1:
                prisms, tets, zones = [], [], []

            else:
                entry = map(int, line.split())[1:]
                # mapping physical region to zone number
                if entry[0] == 6:
                    prisms.append(entry[-6:] + [entry[2]])
                    zones.append(entry[2])
                elif entry[0] == 4:
                    tets.append(entry[-4:] + [entry[2]])
                    zones.append(entry[2])
fid.close()

# check mesh type
if len(prisms) > len(tets):
    npere = 6
    mesh_type = 'Triangular prisms'
    elements = prisms
else:
    npere = 4
    mesh_type = 'Tetrahedra'
    elements = tets

# create mesh3d.dat
fid = open(outfile, 'w')
# one dirichlet node, datum = 0
fid.write('%d %d 1 0 %d \n' % (len(elements), len(nodes), npere))

for i, elem in enumerate(elements):
    fid.write('%d ' % (i + 1))
    elem.insert(-1, i) # unique parameter number
    for entry in elem:
        fid.write('%d ' % entry)
    fid.write('\n')

for i, node in enumerate(nodes):
    node_entry = list(node)
    node_entry.insert(0, i+1)
    fid.write('%d %f %f %f \n' % tuple(node_entry) )
fid.write('1')  # dirichlet node
fid.close()

# show info and close gui
message = """
%s has been successfully created.

Mesh Info:

Type of elements: %s
Nodes: %d
Elements: %d
Zones: %d
""" % (basename(outfile), mesh_type, len(elements), len(nodes), len(set(zones)))

gui.withdraw()
tkMessageBox.showinfo(title='Gmsh2R3t', message=message)
gui.destroy()
