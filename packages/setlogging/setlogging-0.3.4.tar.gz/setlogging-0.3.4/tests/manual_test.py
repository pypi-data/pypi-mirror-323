import shutil
from pathlib import Path
from setlogging.logger import get_logger
import json
import logging
from setlogging.logger import CustomFormatter, setup_logging


# Define a global temp_path for storing log files
temp_path = Path("/tmp/setlogging")
temp_path.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists


def get_log_file_for_function(func_name: str) -> str:
    """
    Generate a log file path for a given function name.
    """
    return str(temp_path / f"{func_name}.log")


def cleanup_temp_path():
    """
    Remove all files in the temp_path directory after testing.
    """
    print("\nCleaning up temporary log files...")
    if temp_path.exists():
        shutil.rmtree(temp_path)
        print(f"All files in {temp_path} have been removed.")


def test_log_rotation():
    """
    Test log rotation functionality.
    """
    log_file = get_log_file_for_function("test_log_rotation")
    logger = get_logger(
        log_level=logging.INFO,
        log_file=log_file,
        max_size_mb=1,  # 1MB log file size
        backup_count=3,  # Keep 3 backup files
        console_output=True,
        json_format=True,
        indent=4,
    )

    message = "This is a test log message. " * 500  # Approx 2KB per log
    for i in range(1000):  # Write enough logs to trigger rotation
        logger.info(f"{i}: {message}")

    print(
        f"Log files created for test_log_rotation: {
          list(temp_path.glob('*'))}"
    )


def test_json_indent():
    """
    Test JSON indentation functionality.
    """
    log_file = get_log_file_for_function("test_json_indent")
    logger = get_logger(json_format=True, indent=2, log_file=log_file)

    logger.info("Test indent message")
    logger.info("Another JSON log message")

    # Read and print log entries
    with open(log_file) as f:
        for line in f:
            print(f"Log entry: {line.strip()}")


def test_file_rotation():
    """
    Test log file rotation functionality.
    """
    log_file = get_log_file_for_function("test_file_rotation")
    logger = get_logger(
        log_level=logging.INFO,
        log_file=log_file,
        max_size_mb=1,  # 1MB log file size
        backup_count=3,  # Keep 3 backup files
    )

    for i in range(104):  # Write enough logs to trigger rotation
        logger.info("x" * 1024 * 10)  # Each log is ~10KB

    print(
        f"Log rotation files for test_file_rotation: {
          list(temp_path.glob('*'))}"
    )


def test_json():
    """
    Test JSON logging functionality.
    """
    log_file = get_log_file_for_function("test_json")
    logger = get_logger(
        log_level=logging.DEBUG,
        log_file=log_file,
        max_size_mb=1,
        backup_count=3,
        json_format=True,
        indent=2,
    )

    logger.debug("This DEBUG message will not be printed.")
    logger.info("This is an INFO message.")
    logger.warning("This is a WARNING message.")
    logger.error("This is an ERROR message.")
    logger.critical("This is a CRITICAL message.")
    logger.info("Test custom field", extra={"custom_field": "value"})


def test_plain_log():
    """
    Test non-JSON logging functionality.
    """
    log_file = get_log_file_for_function("test_plain_log")
    logger = get_logger(
        log_level=logging.CRITICAL,
        log_file=log_file,
        max_size_mb=1,
        backup_count=3,
        json_format=False,
    )

    logger.debug("This is a DEBUG message.")
    logger.info("This is an INFO message.")
    logger.warning("This is a WARNING message.")
    logger.error("This is an ERROR message.")
    logger.critical("This is a CRITICAL message.")


def manual_test_json_structure():
    """
    Manually test JSON log entry structure.
    """
    log_file = get_log_file_for_function("manual_test_json_structure")
    logger = get_logger(json_format=True, log_file=log_file)

    logger.info("Structured log message", extra={"custom_field": "custom_value"})

    # Validate JSON structure
    required_fields = ["time", "level", "message", "name"]
    with open(log_file) as f:
        for line_number, line in enumerate(f, start=1):
            print(f"\nProcessing line {line_number}: {line.strip()}")
            try:
                log_entry = json.loads(line.strip())
                missing_fields = [
                    field for field in required_fields if field not in log_entry
                ]
                if missing_fields:
                    print(f"❌ Missing fields: {missing_fields}")
                else:
                    print(f"✅ Log entry is valid.")
            except json.JSONDecodeError as e:
                print(f"❌ JSON decoding error: {e}")


def manual_test_custom_log_format():
    """
    Test custom log format functionality.
    """
    log_file = get_log_file_for_function("manual_test_custom_log_format")
    custom_format = "%(levelname)s - %(message)s"
    logger = get_logger(log_format=custom_format, log_file=log_file)

    logger.info("Test message")
    print(f"Log file for custom log format created: {log_file}")


def test_timezone_awareness():
    """Test timezone information in logs"""

    # Set up the logger with the CustomFormatter
    logger = get_logger()  # Or manually set up with CustomFormatter

    # Debugging: Print the types of handlers and their formatters
    print(f"Logger handlers: {logger.handlers}")
    for h in logger.handlers:
        print(f"Handler type: {type(h)}")
        if hasattr(h, "formatter"):
            print(f"Formatter type: {type(h.formatter)}")
            print(f"Formatter: {h.formatter}")
            print(f"Formatter class name: {h.formatter.__class__.__name__}")
            print(f"Formatter module: {h.formatter.__module__}")
            print(f"Formatter object ID: {id(h.formatter)}")
            # Check if the formatter is an instance of CustomFormatter
            validation = isinstance(h.formatter, CustomFormatter)
            print(f"Is CustomFormatter: {validation}")
        else:
            print("No formatter found for this handler.")
        if hasattr(h, "formatter"):
            print(f"Formatter的类ID: {id(h.formatter.__class__)}")


def test_file_handler_edge_cases(tmp_path):
    """Test file handler edge cases"""
    # Test invalid file path
    invalid_path = tmp_path / "nonexistent" / "test.log"
    get_logger(log_file=str(invalid_path))

    # Test read-only file
    read_only_file = tmp_path / "read_only.log"
    read_only_file.touch(mode=0o444)
    get_logger(log_file=str(read_only_file))


def test_setup_logging_configurations(tmp_path):
    """Test different setup_logging configurations"""
    # Test basic setup
    log_file = tmp_path / "basic.log"
    setup_logging(log_file=str(log_file))
    logger = logging.getLogger()
    logger.info("Basic setup test")
    assert log_file.exists()

    # Test JSON format with indentation
    json_file = tmp_path / "json.log"
    setup_logging(log_file=str(json_file), json_format=True, indent=4)
    test_message = "JSON format test"
    logger.info(test_message)

    rotate_file = tmp_path / "rotate.log"
    setup_logging(
        log_file=str(rotate_file),
        max_size_mb=1,  # 1MB rotation threshold
        backup_count=3,
    )
    for i in range(150):
        logger.info(f"Rotation test {i}: " + "x" * 1024 * 10)  # 10KB per log entry
        # Explicitly flush after each write to ensure rotation happens
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()


# def test_parameter_validation():
#     """Test parameter validation edge cases"""
#     # Test invalid log level
#     with pytest.raises(ValueError):
#         get_logger(log_level=999)  # Invalid log level number

#     # Test invalid date format
#     with pytest.raises(ValueError):
#         get_logger(date_format="INVALID_FORMAT")

#     # Test invalid log format
#     with pytest.raises(ValueError):
#         get_logger(log_format="INVALID_FORMAT")


def main():
    # print(f"Test代码中的CustomFormatter ID: {id(CustomFormatter)}")
    print("Manual testing started...")

    # Call all test functions
    # test_log_rotation()
    # test_json_indent()
    # test_file_rotation()
    # test_json()
    # test_plain_log()
    # manual_test_json_structure()
    # manual_test_custom_log_format()
    # test_timezone_awareness()
    # get_logger(indent=-1, json_format=True)
    # test_file_handler_edge_cases(temp_path)
    # get_logger(date_format="INVALID_FORMAT")
    log_format = "INVALID_FORMAT"
    # Cleanup
    # cleanup_temp_path()


if __name__ == "__main__":
    main()
