from pathlib import Path
import pytest
from q.cli.parser import parser as gen_parser

parser = gen_parser()


def test_empty_param():
    namespace = parser.parse_args([])
    assert namespace.command is None


def test_helper():
    with pytest.raises(SystemExit):
        parser.parse_args(["--help"])


def test_say_helper():
    with pytest.raises(SystemExit):
        parser.parse_args(["say", "-h"])


def test_say_with_no_extra_tools():
    namespace = parser.parse_args(["say", "user prompt here"])
    assert namespace.command == "say"
    assert namespace.prompt == "user prompt here"
    assert namespace.extra_tools == []


def test_say_with_extra_tools():
    namespace = parser.parse_args(["say", "user prompt here", "-t", "think1, think2"])
    assert namespace.command == "say"
    assert namespace.prompt == "user prompt here"
    assert namespace.extra_tools == ["think1", "think2"]


def test_s_with_extra_tools_in_different_order():
    namespace = parser.parse_args(["s", "-t", "employees", "who is employee with id 3241?"])
    assert namespace.command == "s"
    assert namespace.prompt == "who is employee with id 3241?"
    assert namespace.extra_tools == ["employees"]


def test_create_helper():
    with pytest.raises(SystemExit):
        parser.parse_args(["create", "--help"])


def test_create_for_no_directory_specified():
    namespace = parser.parse_args(["create"])
    assert namespace.command == "create"
    assert namespace.directory == Path.cwd()
    assert namespace.workflow == "default"
    assert namespace.refer_dir is None
    assert namespace.extra_tools == []


def test_create_for_directory_specified():
    namespace = parser.parse_args(["create", "/tmp/abc"])
    assert namespace.command == "create"
    assert namespace.directory == Path("/tmp/abc")
    assert namespace.workflow == "default"
    assert namespace.refer_dir is None
    assert namespace.extra_tools == []


def test_create_and_specify_workflow():
    namespace = parser.parse_args(["create", "-w", "research", "/tmp/abc"])
    assert namespace.command == "create"
    assert namespace.directory == Path("/tmp/abc")
    assert namespace.workflow == "research"
    assert namespace.refer_dir is None
    assert namespace.extra_tools == []


def test_create_and_specify_refer_dir():
    namespace = parser.parse_args(["create", "--refer_dir", "/tmp/cde"])
    assert namespace.command == "create"
    assert namespace.refer_dir == Path("/tmp/cde")
    assert namespace.extra_tools == []


def test_create_with_tools():
    namespace = parser.parse_args(["create", "-t", "t1,t2,  t3"])
    assert namespace.command == "create"
    assert namespace.directory == Path.cwd()
    assert namespace.workflow == "default"
    assert namespace.refer_dir is None
    assert namespace.extra_tools == ["t1", "t2", "t3"]


def test_info_without_directory():
    namespace = parser.parse_args(["info"])
    assert namespace.directory == Path.cwd()


def test_info_with_directory():
    namespace = parser.parse_args(["info", "/tmp/abc"])
    assert namespace.directory == Path("/tmp/abc")
    assert namespace.command == "info"


def test_ls_with_no_params():
    namespace = parser.parse_args(["ls"])
    assert namespace.directory == Path.cwd()


def test_ls_with_all_params():
    namespace = parser.parse_args(["ls", "/tmp/cde", "-s", "3", "-f", "message_history"])
    assert namespace.command == "ls"
    assert namespace.directory == Path("/tmp/cde")
    assert namespace.snapshot == 3
    assert namespace.field == "message_history"


def test_ls_with_default_params():
    namespace = parser.parse_args(["ls", "/tmp/cde"])
    assert namespace.command == "ls"
    assert namespace.directory == Path("/tmp/cde")
    assert namespace.snapshot == -1
    assert namespace.field == ""


def test_config_without_param():
    namespace = parser.parse_args(["config"])
    assert namespace.command == "config"
    assert namespace.key_value_strs is None
    assert namespace.unset_keys is None


def test_config_with_set():
    namespace = parser.parse_args(["config", "--set", "a=b", "c=d"])
    assert namespace.command == "config"
    assert namespace.key_value_strs == ["a=b", "c=d"]
    assert namespace.unset_keys is None


def test_config_with_unset():
    namespace = parser.parse_args(["config", "--unset", "a", "b"])
    assert namespace.command == "config"
    assert namespace.key_value_strs is None
    assert namespace.unset_keys == ["a", "b"]


def test_config():
    namespace = parser.parse_args(["config"])
    assert namespace.command == "config"
    assert namespace.key_value_strs is None
    assert namespace.unset_keys is None


def test_workflow_add():
    namespace = parser.parse_args(["w", "--add", "/tmp/lib1", "/tmp/lib2"])
    assert namespace.command == "w"
    assert namespace.workflow_mods_to_add == [Path("/tmp/lib1"), Path("/tmp/lib2")]


def test_workflow_rm():
    namespace = parser.parse_args(["workflow", "--rm", "lib1", "lib2"])
    assert namespace.command == "workflow"
    assert namespace.workflow_mods_to_rm == ["lib1", "lib2"]


def test_tool_add():
    namespace = parser.parse_args(["t", "--add", "/tmp/lib1", "/tmp/lib2"])
    assert namespace.command == "t"
    assert namespace.tool_mods_to_add == ["/tmp/lib1", "/tmp/lib2"]


def test_tool_rm():
    namespace = parser.parse_args(["tool", "--rm", "lib1", "lib2"])
    assert namespace.command == "tool"
    assert namespace.tool_mods_to_rm == ["lib1", "lib2"]
