import pytest

from leaguemanager.core.toolbox import dynamic_loader


def create_test_files(base_path, files):
    for file_path in files:
        full_path = base_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.touch()


@pytest.fixture
def mock_module_dir(tmp_path_factory):
    base_dir = tmp_path_factory.mktemp("modules_test")
    files = ["module/submodule/__init__.py", "module/submodule/subsubmodule/module1.py", "module/module2.py"]
    create_test_files(base_dir, files)
    return base_dir


# def test_get_modules(mock_module_dir):
#     expected = {"submodule.subsubmodule.module1", "module2"}
#     result = set(get_modules(str(mock_module_dir / "module")))
#     assert result == expected, f"Expected {expected}, got {result}"


@pytest.fixture
def mock_module(mocker):
    """Creates a mock module with a class to be dynamically loaded."""

    class TestClass:
        pass

    # Use mocker to create a mock module
    module = mocker.MagicMock()
    module.TestClass = TestClass
    module.__all__ = ["TestClass"]
    return module


@pytest.fixture
def other_mock_module(mocker):
    """Creates a mock module with a class to be dynamically loaded."""

    class NotTestClass:
        pass

    # Use mocker to create a mock module
    module = mocker.MagicMock()
    module.TestClass = NotTestClass

    return module


def test_dynamic_loader(mock_module, mocker):
    mocker.patch("leaguemanager.core.toolbox.get_modules", return_value=["mock_module", "other_mock_module"])
    mocker.patch.dict("sys.modules", {"mock_module": mock_module, "other_mock_module": mock_module})
    # Mock the compare function to always return True
    compare_func = mocker.MagicMock(return_value=True)

    # Execute dynamic_loader and convert the result to a list to evaluate
    result = list(dynamic_loader("mock_module", compare_func))

    # Assert that our mock class is in the result
    assert mock_module.TestClass in result
    assert mock_module.NotTestClass not in result

    # Additionally, check if compare_func was called with the expected class
    compare_func.assert_called_with(mock_module.TestClass)
