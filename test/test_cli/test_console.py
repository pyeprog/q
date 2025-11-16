import pytest
from q.cli.console import CliConsole
from q.workflow.util.output import ExtraParam


def test_print_markup_string(capsys):
    console = CliConsole()
    console.print(
        "[bold red]run this test in terminal, it should be in red[/]", extra_param=ExtraParam(markdownify=False)
    )
    captured = capsys.readouterr()
    assert "[bold red]" not in captured.out, "[bold red] is the format mark, it's not part of the content"


@pytest.fixture
def text_map() -> dict[str, str]:
    markdown_text = "# Hello\n\nThis is **bold** and *italic* text.\n\n- Item 1\n- Item 2\n\n[Link](https://example.com)\n\n    ```plain\n\n\n```"
    xml_text = "<note><to>User</to><from>Test</from><body>Hello</body></note>"
    json_text = '{"message": "hello", "count": 1}'
    toml_text = """
    title = "TOML Example"
    [owner]
    name = "Tom Preston-Werner"
    dob = 1979-05-27T07:32:00Z
    """
    yaml_text = """
    - message: "hello"
      count: 1
    """
    return {
        "markdown": markdown_text,
        "xml": xml_text,
        "json": json_text,
        "toml": toml_text,
        "yaml": yaml_text,
    }


def test_is_markdown(text_map):
    console = CliConsole()
    assert console.is_markdown_or_yaml(text_map["markdown"])
    assert console.is_markdown_or_yaml(text_map["yaml"])
    assert not console.is_markdown_or_yaml(text_map["xml"])
    assert not console.is_markdown_or_yaml(text_map["json"])
    assert not console.is_markdown_or_yaml(text_map["toml"])


def test_is_xml(text_map):
    console = CliConsole()
    assert not console.is_xml(text_map["markdown"])
    assert console.is_xml(text_map["xml"])
    assert not console.is_xml(text_map["json"])
    assert not console.is_xml(text_map["toml"])


def test_is_json(text_map):
    console = CliConsole()
    assert not console.is_json(text_map["markdown"])
    assert not console.is_json(text_map["xml"])
    assert console.is_json(text_map["json"])
    assert not console.is_json(text_map["toml"])


def test_is_toml(text_map):
    console = CliConsole()
    assert not console.is_toml(text_map["markdown"])
    assert not console.is_toml(text_map["xml"])
    assert not console.is_toml(text_map["json"])
    assert console.is_toml(text_map["toml"])
    assert not console.is_toml(text_map["yaml"])
