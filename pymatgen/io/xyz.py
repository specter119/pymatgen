# coding: utf-8
# Copyright (c) Pymatgen Development Team.
# Distributed under the terms of the MIT License.

from __future__ import division, unicode_literals

"""
Module implementing an XYZ file object class.
"""


__author__ = "Shyue Ping Ong"
__copyright__ = "Copyright 2012, The Materials Project"
__version__ = "0.1"
__maintainer__ = "Shyue Ping Ong"
__email__ = "shyuep@gmail.com"
__date__ = "Apr 17, 2012"

import re

from pymatgen.core.structure import Molecule
from monty.io import zopen


class XYZ(object):
    """
    Basic class for importing and exporting Molecules or Structures in XYZ
    format.

    Args:
        mol: Input molecule

    .. note::
        Exporting periodic structures in the XYZ format will lose information
        about the periodicity. Essentially, only cartesian coordinates are
        written in this format and no information is retained about the
        lattice.
    """
    def __init__(self, mol, coord_precision=6):
        self._mol = mol
        self.precision = coord_precision

    @property
    def molecule(self):
        """
        Returns molecule associated with this XYZ.
        """
        return self._mol

    @staticmethod
    def from_string(contents):
        """
        Creates XYZ object from a string.

        Args:
            contents: String representing an XYZ file.

        Returns:
            XYZ object
        """
        lines = contents.split("\n")
        num_sites = int(lines[0])
        coords = []
        sp = []
        coord_patt = re.compile(
            "(\w+)\s+([0-9\-\.e]+)\s+([0-9\-\.e]+)\s+([0-9\-\.e]+)"
        )
        for i in range(2, 2 + num_sites):
            m = coord_patt.search(lines[i])
            if m:
                sp.append(m.group(1))  # this is 1-indexed
                # this is 0-indexed
                coords.append([float(j) for j in m.groups()[1:4]])
        return XYZ(Molecule(sp, coords))

    @staticmethod
    def from_file(filename):
        """
        Creates XYZ object from a file.

        Args:
            filename: XYZ filename

        Returns:
            XYZ object
        """
        with zopen(filename) as f:
            return XYZ.from_string(f.read())

    def __str__(self):
        output = [str(len(self._mol)), self._mol.composition.formula]
        fmtstr = "{{}} {{:.{0}f}} {{:.{0}f}} {{:.{0}f}}".format(self.precision)
        for site in self._mol:
            output.append(fmtstr.format(site.specie, site.x, site.y, site.z))
        return "\n".join(output)

    def write_file(self, filename):
        """
        Writes XYZ to file.

        Args:
            filename: File name of output file.
        """
        with zopen(filename, "wt") as f:
            f.write(self.__str__())


class MXYZ(object):
    """
    Basic class for multiple frame XYZ file.

    Args:
        mols: Input molecule

    .. note::
        Exporting periodic structures in the XYZ format will lose information
        about the periodicity. Essentially, only cartesian coordinates are
        written in this format and no information is retained about the
        lattice.
    """
    def __init__(self, mols, coord_precision=6):
        self._mols = mols
        self.precision = coord_precision

    @property
    def molecules(self):
        """
        Returns molecules associated with this multiple frame XYZ.
        """
        return self._mols

    @staticmethod
    def from_string(contents):
        """
        Creates XYZ object from a string.

        Args:
            contents: String representing an XYZ file.

        Returns:
            XYZ object
        """
        if contents[-1] != "\n":
            contents += "\n"
        white_space = r"[ \t\r\f\v]"
        natoms_line = white_space + r"*\d+" + white_space + r"*\n"
        comment_line = r"[^\n]*\n"
        coord_lines = r"(\s*\w+\s+[0-9\-\.e]+\s+[0-9\-\.e]+\s+[0-9\-\.e]+\s*\n)+"
        frame_pattern_text = natoms_line + comment_line + coord_lines
        pat = re.compile(frame_pattern_text, re.MULTILINE)
        mols = []
        for xyz_match in pat.finditer(contents):
            xyz_text = xyz_match.group(0)
            mols.append(XYZ.from_string(xyz_text).molecule)
        return MXYZ(mols)


    @staticmethod
    def from_file(filename):
        """
        Creates MXYZ object from a file.

        Args:
            filename: multiple frame XYZ filename

        Returns:
            MXYZ object
        """
        with zopen(filename) as f:
            return MXYZ.from_string(f.read())

    def __str__(self):
        return "\n".join([str(mol) for mol in self._mols])

    def write_file(self, filename):
        """
        Writes multiple frame XYZ to file.

        Args:
            filename: File name of output file.
        """
        with zopen(filename, "wt") as f:
            f.write(self.__str__())