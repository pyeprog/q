import re
from typing import Generator

import pytest
from q.cli.config import CentralizedConfig
from q.cli.entry_point import print_config, set_config, unset_config


def test_print_config(capsys):
    print_config()
    captured = capsys.readouterr()
    assert 'OPENROUTER_API_KEY' in captured.out
    assert 'TAVILY_API_KEY' in captured.out
    
    
def test_set_config(capsys):
    print_config()
    captured = capsys.readouterr()
    pattern = re.compile(r"TAVILY_API_KEY\s*=\s*(\S+)", re.MULTILINE)
    origin_tavily_api_key = pattern.search(captured.out).group(1) # type: ignore

    some_key = "abccddde"
    set_config([f"TAVILY_API_KEY={some_key}"])
    
    print_config()
    captured = capsys.readouterr()
    pattern = re.compile(r"TAVILY_API_KEY\s*=\s*(\S+)", re.MULTILINE)
    tavily_api_key = pattern.search(captured.out).group(1) # type: ignore
    assert tavily_api_key == some_key

    set_config([f"TAVILY_API_KEY={origin_tavily_api_key}"])

    
def test_unset_config(capsys):
    print_config()
    captured = capsys.readouterr()
    pattern = re.compile(r"TAVILY_API_KEY\s*=\s*(.+)$", re.MULTILINE)
    origin_tavily_api_key = pattern.search(captured.out).group(1) # type: ignore
    print(origin_tavily_api_key)
    
    unset_config(["TAVILY_API_KEY"])
    
    print_config()
    captured = capsys.readouterr()
    pattern = re.compile(r"TAVILY_API_KEY\s*=\s*(\S+)", re.MULTILINE)
    tavily_api_key = pattern.search(captured.out).group(1) # type: ignore
    assert tavily_api_key == CentralizedConfig.PLACEHOLDER
    
    set_config([f"TAVILY_API_KEY={origin_tavily_api_key}"])