#! /usr/bin/env python

# SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
# SPDX-License-Identifier: BSD-3-Clause
# SPDX-FileType: SOURCE
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the license found in the LICENSE.txt file in the root directory
# of this source tree.


# =======
# Imports
# =======

import os
import glob
from detkit import get_instructions_per_flop

import warnings
warnings.resetwarnings()
warnings.filterwarnings("error")


# =================
# remove saved plot
# =================

def _remove_saved_plot(filenames):
    """
    Deletes image files produced during the test.
    """

    directory = os.getcwd()
    fullpath_filenames = os.path.join(directory, filenames)

    # Get a list of all files matching wildcard
    files_list = glob.glob(fullpath_filenames)

    # Iterate over files
    for file in files_list:
        try:
            os.remove(file)
            print('File %s is deleted.' % file)
        except BaseException as error:
            print('An exception occurred: {}'.format(error))
            print("Error while removing file : ", file)


# ======================
# test get inst per flop
# ======================

def test_get_inst_per_flop():
    """
    Test for `get_inst_per_flop` function.
    """

    # Instructions for each task
    inst_per_matmat = get_instructions_per_flop(task='matmat')
    inst_per_gramian = get_instructions_per_flop(task='gramian')
    inst_per_cholesky = get_instructions_per_flop(task='cholesky')
    inst_per_lu = get_instructions_per_flop(task='lu')
    inst_per_lup = get_instructions_per_flop(task='lup')

    # Instructions relative to matrix-matrix multiplication
    rel_inst_per_matmat = inst_per_matmat / inst_per_matmat
    rel_inst_per_gramian = inst_per_gramian / inst_per_matmat
    rel_inst_per_cholesky = inst_per_cholesky / inst_per_matmat
    rel_inst_per_lu = inst_per_lu / inst_per_matmat
    rel_inst_per_lup = inst_per_lup / inst_per_matmat

    # Print results
    print('instructions per matmat:   %0.3f, rel: %0.3f'
          % (inst_per_matmat, rel_inst_per_matmat))
    print('instructions per gramian:  %0.3f, rel: %0.3f'
          % (inst_per_gramian, rel_inst_per_gramian))
    print('instructions per cholesky: %0.3f, rel: %0.3f'
          % (inst_per_cholesky, rel_inst_per_cholesky))
    print('instructions per lu:       %0.3f, rel: %0.3f'
          % (inst_per_lu, rel_inst_per_lu))
    print('instructions per lup:      %0.3f, rel: %0.3f'
          % (inst_per_lup, rel_inst_per_lup))

    # Check plot
    _ = get_instructions_per_flop(dtype='float32', min_n=100, max_n=500,
                                  num_n=10, plot=True)

    _remove_saved_plot('simd.svg')
    _remove_saved_plot('simd.pdf')


# ===========
# Script main
# ===========

if __name__ == "__main__":
    test_get_inst_per_flop()
