import pytest
from unittest.mock import patch
from resume_iq.parser import ResumeParser, parsefile

@patch("resume_iq.parser.ResumeParser.parse")
def test_parsefile_method(mock_parse):
    mock_parse.return_value = {"success": True}
    parser = ResumeParser()
    result = parser.parsefile("dummy.pdf")
    mock_parse.assert_called_once_with("dummy.pdf")
    assert result == {"success": True}

@patch("resume_iq.parser.ResumeParser.parse")
def test_module_parsefile(mock_parse):
    mock_parse.return_value = {"success": True}
    result = parsefile("dummy.pdf")
    mock_parse.assert_called_once_with("dummy.pdf")
    assert result == {"success": True}
