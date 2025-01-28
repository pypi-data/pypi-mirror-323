import unittest
import os
import tempfile
import shutil
import sys
import dyn_import_utils

test_dir = os.path.dirname(__file__)
dyn_import_utils.add_sys_path(test_dir)
module_path = os.path.join(test_dir, "test_module.py")
package_dir = os.path.join(test_dir, "test_package")

#    def test_01_import_module(self):
#        module = dyn_import_utils.import_module(self.module_path)
#        self.assertTrue(hasattr(module, "hello"))
#        self.assertEqual(module.hello(), "Hello, world!")

package = dyn_import_utils.import_package(package_dir)



