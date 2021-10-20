import os
import sys
import pytest
import coverage


def add_core_package_to_path():

    test_path = os.path.dirname(__file__)
    
    core_relative_path = os.path.join(test_path, '..', 'app', 'core-service')
    
    core_path = os.path.abspath(core_relative_path)
    
    sys.path.insert(0, core_path)
    
    # print(f"TESTS test_path {test_path}")
    # print(f"TESTS core_relative_path {core_relative_path}")
    # print(f"TESTS core_path {core_path}")
    # print(f"TESTS sys.path {sys.path}")


def run_tests_with_coverage():

    test_path = os.path.dirname(__file__)
    html_coverage_report_path = os.path.join(test_path, 'html_coverage_report')

    cov = coverage.Coverage()
    cov.start()
    
    code = pytest.main([test_path, '-v', '-rP'])
    
    cov.stop()
    cov.save()
    
    cov.report(show_missing=True, skip_empty=True)
    cov.html_report(directory='html_coverage_report')
    

if __name__ == '__main__':
    
    add_core_package_to_path()
    run_tests_with_coverage()