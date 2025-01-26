import os
import unittest

from pychemstation.control import HPLCController
from tests.constants import *


class TestMethod(unittest.TestCase):
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

    def test_load_method_from_disk(self):
        self.hplc_controller.switch_method(DEFAULT_METHOD)
        try:
            gp_mtd = self.hplc_controller.method_controller.load_from_disk(DEFAULT_METHOD)
            self.assertTrue(gp_mtd.first_row.organic_modifier == 5)
        except Exception as e:
            self.fail(f"Should have not failed, {e}")

    def test_edit_method(self):
        self.hplc_controller.method_controller.switch(DEFAULT_METHOD)
        new_method = gen_rand_method()
        try:
            self.hplc_controller.edit_method(new_method)
        except Exception as e:
            self.fail(f"Should have not failed: {e}")

    def test_load_method(self):
        self.hplc_controller.method_controller.switch(DEFAULT_METHOD)
        new_method = gen_rand_method()
        try:
            self.hplc_controller.edit_method(new_method)
            loaded_method = self.hplc_controller.load_method()
            self.assertEqual(new_method.first_row.organic_modifier,
                             loaded_method.first_row.organic_modifier)
            self.assertEqual(new_method.subsequent_rows,
                             loaded_method.subsequent_rows)
            self.assertEqual(new_method.first_row.flow,
                             loaded_method.first_row.flow)
        except Exception as e:
            self.fail(f"Should have not failed: {e}")

    def test_run_method(self):
        try:
            self.hplc_controller.run_method(experiment_name="test_experiment")
            chrom = self.hplc_controller.get_last_run_method_data()
        except Exception as e:
            self.fail(f"Should have not failed: {e}")


if __name__ == '__main__':
    unittest.main()
