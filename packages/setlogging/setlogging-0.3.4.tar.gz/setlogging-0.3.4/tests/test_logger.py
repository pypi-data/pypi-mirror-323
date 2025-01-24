import pytest
import json
import os
import logging
from datetime import datetime
from setlogging.logger import (
    get_logger,
    setup_logging,
    get_config_message,
    CustomFormatter,
)


class LogCapture:
    def __init__(self):
        self.records = []

    def __enter__(self):
        self.handler = logging.StreamHandler()
        self.handler.setLevel(logging.DEBUG)
        self.records = []
        self.handler.emit = lambda record: self.records.append(record)
        logging.getLogger().addHandler(self.handler)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.getLogger().removeHandler(self.handler)


def test_basic_logger():
    """Test basic logger initialization"""
    logger = get_logger()
    assert logger is not None
    assert isinstance(logger, logging.Logger)
    assert logger.level == logging.DEBUG


def test_json_logging(tmp_path):
    """Test JSON format logging"""
    # Create a temporary file for logging
    log_file = tmp_path / "test_json_format.log"

    # Initialize the logger with JSON format and specify the log file
    logger = get_logger(json_format=True, log_file=str(log_file))
    test_message = "Test JSON logging"

    # Log a test message
    logger.info(test_message)

    # Read the log file line by line and parse each line as JSON
    with open(log_file) as f:
        for line in f:
            # Parse each line as a JSON object
            log_entry = json.loads(line.strip())

            # Validate the parsed JSON structure for each log entry
            # Focus on the test message entry
            if log_entry.get("message") == test_message:
                assert "message" in log_entry  # Check if "message" key exists
                # Verify the message content
                assert log_entry["message"] == test_message
                assert "level" in log_entry  # Check if "level" key exists
                # Verify the log level is "INFO"
                assert log_entry["level"] == "INFO"


def test_timezone_awareness():
    """Test timezone information in logs"""

    # Set up the logger with the CustomFormatter
    logger = get_logger()  # Or manually set up with CustomFormatter
    print(type(logger.handlers))
    for h in logger.handlers:
        print(type(h.formatter))
    formatter = next(
        (
            h.formatter
            for h in logger.handlers
            if isinstance(h.formatter, CustomFormatter)
        ),
        None,
    )

    # Assert that the formatter is correctly applied
    assert formatter is not None


def test_file_rotation(tmp_path):
    """Test log file rotation"""
    log_file = tmp_path / "rotate.log"
    max_size_mb = 1  # 1MB
    backup_count = 3
    logger = get_logger(
        log_file=str(log_file), max_size_mb=max_size_mb, backup_count=backup_count
    )

    # Write enough data to trigger rotation
    for i in range(104):
        logger.info("x" * 1024 * 10)  # 10KB per log entry

    assert os.path.exists(log_file)
    assert os.path.exists(f"{log_file}.1")

    # Check the size of the rotated log file
    log_file_size = os.path.getsize(f"{log_file}.1")  # Size in bytes
    expected_size = max_size_mb * 1024 * 1024  # Convert MB to bytes

    # Allow a 5% margin of error
    margin = expected_size * 0.05
    assert abs(log_file_size - expected_size) <= margin, (
        f"Expected size around {expected_size} bytes (±{margin:.0f}), "
        f"but got {log_file_size} bytes"
    )


def test_invalid_parameters():
    """Test error handling for invalid parameters"""
    with pytest.raises(ValueError):
        get_logger(max_size_mb=-1)

    with pytest.raises(ValueError):
        get_logger(backup_count=-1)

    with pytest.raises(ValueError):
        get_logger(indent=2, json_format=False)

    # Test invalid indent values
    with pytest.raises(ValueError):
        get_logger(indent=-1, json_format=True)

    with pytest.raises(ValueError):
        get_logger(indent=-2, json_format=True)


def test_console_output(capsys):
    """Test console output"""
    logger = get_logger(console_output=True)
    test_message = "Test console output"
    logger.info(test_message)
    captured = capsys.readouterr()
    assert test_message in captured.err or test_message in captured.out


def test_json_indent(tmp_path):
    """Test JSON indentation formatting"""
    # Test various indent values
    for indent in [None, 0, 2, 4]:
        log_file = tmp_path / f"test_indent_{indent}.json"
        logger = get_logger(json_format=True, indent=indent, log_file=str(log_file))

        # Generate some log entries
        test_message = f"Test indent {indent}"
        logger.info(test_message)
        logger.info("Another message")

        # Validate the indentation of the log file
        with open(log_file) as f:
            for line_number, line in enumerate(f, start=1):
                # Skip empty lines
                if not line.strip():
                    continue

                # Count the number of leading spaces
                leading_spaces = len(line) - len(line.lstrip())

                if indent is None or indent == 0:
                    # No indentation expected
                    assert leading_spaces == 0, (
                        f"Line '{line.strip()}' has unexpected indentation: "
                        f"{leading_spaces} spaces (expected 0). "
                        f"The line number is: {line_number}"
                    )
                else:
                    # Ensure the leading spaces are a multiple of the specified indent
                    assert leading_spaces % indent == 0, (
                        f"Line '{line.strip()}' has incorrect indentation: "
                        f"{leading_spaces} spaces (expected multiple of {indent}). "
                        f"The line number is: {line_number}"
                    )


def test_invalid_json_parameters():
    """Test invalid JSON parameters"""
    # Test invalid indent with json_format=False
    with pytest.raises(ValueError, match="indent parameter is only valid"):
        get_logger(json_format=False, indent=2)


def test_log_level_configuration():
    """Test different log levels"""
    logger = get_logger(log_level=logging.WARNING)
    assert logger.level == logging.WARNING

    # Debug shouldn't log
    with LogCapture() as capture:
        logger.debug("Debug message")
        assert len(capture.records) == 0

        # Warning should log
        logger.warning("Warning message")
        assert len(capture.records) == 1


def test_custom_date_format(tmp_path):
    """Test custom date format"""
    log_file = tmp_path / "date_format.log"
    date_format = "%Y-%m-%d"
    logger = get_logger(log_file=str(log_file), date_format=date_format)
    logger.info("Test message")

    with open(log_file) as f:
        content = f.read()
        assert datetime.now().strftime(date_format) in content


def test_custom_log_format():
    """Test custom log format"""
    custom_format = "%(levelname)s - %(message)s"
    logger = get_logger(log_format=custom_format)
    print(f"logger.handlers: {logger.handlers}")

    with LogCapture() as capture:
        logger.info("Test message")

        # Get the first captured log record
        log_record = capture.records[0]

        # Format the LogRecord using the custom format
        formatter = logging.Formatter(custom_format)
        formatted_message = formatter.format(log_record)

        # Assert the formatted message matches the expected output
        assert (
            formatted_message == "INFO - Test message"
        ), f"Expected 'INFO - Test message' but got '{formatted_message}'"


def test_multiple_handlers():
    """Test multiple handlers configuration"""
    logger = get_logger(console_output=True)

    # Ensure at least two handlers are present (e.g., console and file)
    assert len(logger.handlers) >= 2, "Expected at least 2 handlers (file and console)"

    # Check handler types
    handler_types = [type(h) for h in logger.handlers]
    assert logging.StreamHandler in handler_types, "StreamHandler (console) is missing"
    assert any(
        issubclass(h, logging.FileHandler) for h in handler_types
    ), "No FileHandler or RotatingFileHandler found in logger handlers"


def test_get_config_message():
    """Test get_config_message helper function"""

    # Create a mock file handler
    class MockFileHandler:
        def __init__(self, filename):
            self.baseFilename = filename

    # Test JSON format
    json_config = get_config_message(
        log_level=logging.INFO,
        file_handler=MockFileHandler("test.log"),
        max_size_mb=10,
        backup_count=5,
        console_output=True,
        json_format=True,
    )
    config_dict = json.loads(json_config)
    assert config_dict["Level"] == "INFO"
    assert config_dict["LogFile"] == "test.log"
    assert config_dict["MaxFileSizeMB"] == 10
    assert config_dict["BackupCount"] == 5
    assert config_dict["ConsoleOutput"] is True

    # Test text format
    text_config = get_config_message(
        log_level=logging.DEBUG,
        file_handler=MockFileHandler("test.log"),
        max_size_mb=20,
        backup_count=3,
        console_output=False,
        json_format=False,
    )
    assert "Logging Configuration" in text_config
    assert "DEBUG" in text_config
    assert "test.log" in text_config
    assert "20.00 MB" in text_config
    assert "3" in text_config


def test_setup_logging_configurations(tmp_path):
    """Test different setup_logging configurations"""
    # Test basic setup

    log_file = tmp_path / "basic.log"
    setup_logging(log_file=str(log_file))
    logger = get_logger()
    logger.info("Basic setup test")
    assert log_file.exists()

    # Test JSON format with indentation
    json_file = tmp_path / "json.log"
    setup_logging(log_file=str(json_file), json_format=True, indent=4)
    test_message = "JSON format test"
    logger.info(test_message)

    # Read and parse all log entries
    with open(json_file) as f:
        for line in f:
            try:
                content = json.loads(line)
                # Skip configuration messages
                if "message" in content and content["message"] == test_message:
                    assert content["message"] == test_message
                    assert "time" in content
                    assert "level" in content
                    assert content["level"] == "INFO"
                    break
            except json.JSONDecodeError:
                continue

    # Test with custom date format
    date_file = tmp_path / "date_format.log"
    setup_logging(log_file=str(date_file), date_format="%Y-%m-%d")
    logger.info("Date format test")
    with open(date_file) as f:
        content = f.read()
        assert datetime.now().strftime("%Y-%m-%d") in content

    # Test with rotation
    rotate_file = tmp_path / "rotate.log"
    setup_logging(
        log_file=str(rotate_file),
        max_size_mb=1,  # 1MB rotation threshold
        backup_count=3,
    )
    logger.info("Rotation test start: \n ======================")
    # Write enough data to trigger rotation (1.5MB total)
    for i in range(150):
        logger.info(f"Rotation test {i}: " + "x" * 1024 * 10)  # 10KB per log entry
        # Explicitly flush after each write to ensure rotation happens
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.close()  # 显式关闭处理器以确保轮转完成

    # Verify rotation occurred
    assert os.path.exists(rotate_file), "Original log file should exist"
    assert os.path.getsize(rotate_file) > 0, "Original log file should not be empty"

    # Check for rotated files
    rotated_files = [f"{rotate_file}.{i}" for i in range(1, 4)]
    assert any(
        os.path.exists(f) for f in rotated_files
    ), "At least one rotated file should exist"

    # Verify rotation sizes
    for rotated_file in rotated_files:
        if os.path.exists(rotated_file):
            rotated_size = os.path.getsize(rotated_file)
            assert (
                rotated_size >= 1024 * 1024 * 0.9
            ), f"Rotated file {rotated_file} should be at least 90% of 1MB, got {rotated_size} bytes"
            assert (
                rotated_size <= 1024 * 1024 * 1.1
            ), f"Rotated file {rotated_file} should be at most 110% of 1MB, got {rotated_size} bytes"

    # Verify backup count
    assert (
        sum(os.path.exists(f) for f in rotated_files) <= 3
    ), "Should not exceed backup count"

    # Test console output
    setup_logging(console_output=True)
    with LogCapture() as capture:
        logger.info("Console output test")
        assert len(capture.records) == 1


@pytest.fixture(autouse=True)
def cleanup():
    """Clean up log files after tests"""
    # Store initial handlers
    initial_handlers = logging.getLogger().handlers[:]

    yield

    # Clean up any added handlers
    for handler in logging.getLogger().handlers[:]:
        if handler not in initial_handlers:
            handler.close()
            logging.getLogger().removeHandler(handler)


def test_cleanup_fixture():
    """Test that the cleanup fixture removes handlers"""
    # Get initial handler count
    initial_count = len(logging.getLogger().handlers)

    # Add a test handler
    test_handler = logging.StreamHandler()
    logging.getLogger().addHandler(test_handler)

    # Verify handler was added
    assert len(logging.getLogger().handlers) == initial_count + 1

    # The cleanup fixture should run after this test and remove the handler


def test_file_handler_edge_cases(tmp_path):
    """Test file handler edge cases"""
    # Test invalid file path
    invalid_path = tmp_path / "nonexistent" / "test.log"
    get_logger(log_file=str(invalid_path))
    # If directory does not exist, it would be created automatically
    assert invalid_path.exists()

    # Test read-only file
    read_only_file = tmp_path / "read_only.log"
    read_only_file.touch(mode=0o444)
    with pytest.raises(PermissionError):
        get_logger(log_file=str(read_only_file))


def test_json_indentation_edge_cases(tmp_path):
    """Test JSON indentation edge cases"""
    # Test large indent value
    log_file = tmp_path / "large_indent.log"
    logger = get_logger(json_format=True, indent=16, log_file=str(log_file))
    logger.info("Test message")

    with open(log_file) as f:
        content = f.read()
        assert " " * 16 in content, "Should have 16-space indentation"

    # Test zero indent with JSON
    log_file = tmp_path / "zero_indent.log"
    logger = get_logger(json_format=True, indent=0, log_file=str(log_file))
    logger.info("Test message")

    with open(log_file) as f:
        content = f.read()
        assert "\n" in content, "Should have newlines even with zero indent"
        assert "  " not in content, "Should have no indentation spaces"


def test_parameter_validation():
    """Test parameter validation edge cases"""
    # Test invalid log level
    with pytest.raises(ValueError):
        get_logger(log_level=999)  # Invalid log level number

    # Test invalid date format
    with pytest.raises(ValueError):
        get_logger(date_format="INVALID_FORMAT")

    # Test invalid log format
    with pytest.raises(ValueError):
        get_logger(log_format="INVALID_FORMAT")
