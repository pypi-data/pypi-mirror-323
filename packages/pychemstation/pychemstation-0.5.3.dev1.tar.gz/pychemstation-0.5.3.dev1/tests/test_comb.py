import os

import unittest

from pychemstation.control import HPLCController
from tests.constants import *

run_too = False




class TestCombinations(unittest.TestCase):
    def setUp(self):
        path_constants = room(254)
        for path in path_constants:
            if not os.path.exists(path):
                self.fail(
                    f"{path} does not exist on your system. If you would like to run tests, please change this path.")

        self.hplc_controller = HPLCController(comm_dir=path_constants[0],
                                              method_dir=path_constants[1],
                                              data_dir=path_constants[2],
                                              sequence_dir=path_constants[3])

    def test_run_method_after_update(self):
        self.hplc_controller.method_controller.switch(DEFAULT_METHOD)

        try:
            rand_method = gen_rand_method()
            self.hplc_controller.edit_method(rand_method)
            if run_too:
                self.hplc_controller.run_method(experiment_name="changed_method")
        except Exception as e:
            self.fail(f"Should have not failed: {e}")

    def test_run_after_table_edit(self):
        try:
            self.hplc_controller.switch_sequence(sequence_name=DEFAULT_SEQUENCE)
            seq_table = self.hplc_controller.load_sequence()
            seq_table.rows[0].vial_location = TenColumn.FIVE
            seq_table.rows[1].vial_location = TenColumn.ONE
            seq_table.rows[0].inj_source = InjectionSource.HIP_ALS
            seq_table.rows[1].inj_source = InjectionSource.MANUAL
            self.hplc_controller.edit_sequence(seq_table)
            if run_too:
                self.hplc_controller.run_sequence(seq_table)
                chrom = self.hplc_controller.get_last_run_sequence_data()
                self.assertTrue(len(chrom) == 2)
        except Exception as e:
            self.fail("Failed")

    def test_run_after_existing_row_edit(self):
        try:
            self.hplc_controller.switch_sequence(sequence_name=DEFAULT_SEQUENCE)
            seq_table = self.hplc_controller.load_sequence()
            self.hplc_controller.edit_sequence_row(seq_entry, 1)
            if run_too:
                self.hplc_controller.run_sequence(seq_table)
                chrom = self.hplc_controller.get_last_run_sequence_data()
                self.assertTrue(len(chrom) == 2)
        except Exception:
            self.fail("Failed")

    def test_update_method_update_seq_table_run(self):
        try:
            self.hplc_controller.method_controller.switch(DEFAULT_METHOD)
            rand_method = gen_rand_method()
            self.hplc_controller.edit_method(rand_method, save=True)

            self.hplc_controller.switch_sequence(sequence_name=DEFAULT_SEQUENCE)
            seq_table = self.hplc_controller.load_sequence()
            seq_table.rows[0].vial_location = TenColumn.ONE
            seq_table.rows[0].inj_source = InjectionSource.HIP_ALS
            seq_table.rows[1].vial_location = TenColumn.TWO
            seq_table.rows[1].inj_source = InjectionSource.HIP_ALS
            self.hplc_controller.edit_sequence(seq_table)

            if run_too:
                self.hplc_controller.run_sequence(seq_table)
                chrom = self.hplc_controller.get_last_run_sequence_data()
                self.assertTrue(len(chrom) == 2)
        except Exception:
            self.fail("Failed")

    def test_update_table_then_row(self):
        try:
            self.hplc_controller.method_controller.switch(DEFAULT_METHOD)
            self.hplc_controller.switch_sequence(sequence_name=DEFAULT_SEQUENCE)
            rand_method = gen_rand_method()
            self.hplc_controller.edit_method(rand_method, save=True)

            seq_table = self.hplc_controller.load_sequence()
            seq_table.rows[0].vial_location = TenColumn.ONE
            seq_table.rows[0].inj_source = InjectionSource.HIP_ALS
            seq_table.rows[0].method = DEFAULT_METHOD
            seq_table.rows[1].vial_location = TenColumn.TWO
            seq_table.rows[1].inj_source = InjectionSource.HIP_ALS
            seq_table.rows[1].method = DEFAULT_METHOD

            self.hplc_controller.edit_sequence(seq_table)
            self.hplc_controller.edit_sequence_row(
                SequenceEntry(
                    vial_location=TenColumn.ONE,
                    method=DEFAULT_METHOD,
                    num_inj=3,
                    inj_vol=4,
                    sample_name="Blank",
                    sample_type=SampleType.BLANK,
                )
            )
            if run_too:
                self.hplc_controller.run_sequence(seq_table)
                chrom = self.hplc_controller.get_last_run_sequence_data()
                self.assertTrue(len(chrom) == 2)
        except Exception:
            self.fail("Failed")

    def test_run_after_new_row_edit(self):
        try:
            self.hplc_controller.switch_sequence(sequence_name=DEFAULT_SEQUENCE)
            seq_table = self.hplc_controller.load_sequence()
            self.hplc_controller.edit_sequence_row(seq_entry, 3)
            if run_too:
                self.hplc_controller.run_sequence(seq_table)
                chrom = self.hplc_controller.get_last_run_sequence_data()
                self.assertTrue(len(chrom) == 2)
        except Exception:
            self.fail("Failed")
