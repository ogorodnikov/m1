import os
import sys
import pytest

test_path = os.path.dirname(__file__)

core_relative_path = os.path.join(test_path, '..', 'core-service')

core_path = os.path.abspath(core_relative_path)

sys.path.insert(0, core_path)

# print(f"TESTS test_path {test_path}")
# print(f"TESTS core_relative_path {core_relative_path}")
# print(f"TESTS core_path {core_path}")
# print(f"TESTS sys.path {sys.path}")

from core import engine



code = pytest.main()

print(f"code {code}")
