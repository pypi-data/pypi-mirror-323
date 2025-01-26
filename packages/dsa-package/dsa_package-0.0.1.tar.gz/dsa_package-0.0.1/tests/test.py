import pytest
from dsa_package.src.dsa_package_AKV163 import dsa_sorting as sorting

def test_bubble_sort():
    assert sorting.sorting([4,0,2,101,3,4]) == [0,2,3,4,4,101]