import pytest

from textual.css.errors import StyleValueError
from textual.css.query import NoMatchingNodesError
from textual.dom import DOMNode


def test_display_default():
    node = DOMNode()
    assert node.display is True


@pytest.mark.parametrize(
    "setter_value,style_value",
    [[True, "block"], [False, "none"], ["block", "block"], ["none", "none"]],
)
def test_display_set_bool(setter_value, style_value):
    node = DOMNode()
    node.display = setter_value
    assert node.styles.display == style_value


def test_display_set_invalid_value():
    node = DOMNode()
    with pytest.raises(StyleValueError):
        node.display = "blah"


@pytest.fixture
def parent():
    parent = DOMNode(id="parent")

    child1 = DOMNode(id="child1")
    child1.add_class("foo")
    child2 = DOMNode(id="child2")
    child2.add_class("bar")

    grandchild1 = DOMNode(id="grandchild1")
    child1.add_child(grandchild1)

    parent.add_child(child1)
    parent.add_child(child2)

    yield parent


def test_get_child_gets_first_child(parent):
    child = parent.get_child(".foo")
    assert child.id == "child1"
    assert child.get_child("#grandchild1").id == "grandchild1"
    assert parent.get_child(".bar").id == "child2"


def test_get_child_no_matching_child(parent):
    with pytest.raises(NoMatchingNodesError):
        parent.get_child("#doesnt-exist")


def test_get_child_only_immediate_descendents(parent):
    with pytest.raises(NoMatchingNodesError):
        parent.get_child("#grandchild1")
