
import os
import sys
import pytest
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from rusta_crawler.spiders.rusta_spider import NewEcomSpider

@pytest.fixture
def spider_functions():
    return NewEcomSpider()

def test_remove_file_if_exists(spider_functions, tmp_path):
    # Create a temporary file
    temp_file = tmp_path / "temp_file.txt"
    temp_file.write_text("This is a test file.")

    # Ensure the file exists
    assert temp_file.exists()

    # Test removing the file
    spider_functions.remove_file_if_exists(str(temp_file))
    assert not temp_file.exists()

    # Test removing a non-existent file
    result = spider_functions.remove_file_if_exists(str(temp_file))
    assert result is False

# def test_process_all_active_and_save(spider_functions)
    