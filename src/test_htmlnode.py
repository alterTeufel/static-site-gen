import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode

class TestHTMLNode(unittest.TestCase):
    def test_props_to_html_with_multiple_props(self):
        node = HTMLNode(tag="a", props={"href": "https://www.google.com", "target": "_blank"})
        self.assertEqual(node.props_to_html(), ' href="https://www.google.com" target="_blank"')

    def test_props_to_html_with_empty_and_none(self):
        node_empty = HTMLNode(tag="div", props={})
        node_none = HTMLNode(tag="span", props=None)
        self.assertEqual(node_empty.props_to_html(), "")
        self.assertEqual(node_none.props_to_html(), "")

    def test_repr_includes_fields(self):
        child = HTMLNode(tag="b", value="bold")
        node = HTMLNode(tag="p", value="text", children=[child], props={"class": "intro"})
        rep = repr(node)
        self.assertIn("HTMLNode(", rep)
        self.assertIn("tag='p'", rep)
        self.assertIn("value='text'", rep)
        self.assertIn("children=[", rep)
        self.assertIn("props={'class': 'intro'}", rep)

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_a(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(node.to_html(), '<a href="https://www.google.com">Click me!</a>')

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

if __name__ == "__main__":
    unittest.main()
