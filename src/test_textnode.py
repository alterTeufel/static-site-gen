import unittest

from textnode import TextNode, TextType, text_node_to_html_node
from markdown_utils import text_to_textnodes, BlockType, block_to_block_type


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_not_equal_different_text(self):
        node = TextNode("Text A", TextType.PLAIN)
        node2 = TextNode("Text B", TextType.PLAIN)
        self.assertNotEqual(node, node2)

    def test_not_equal_different_type(self):
        node = TextNode("Same text", TextType.ITALIC)
        node2 = TextNode("Same text", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_url_default_none_and_inequality(self):
        # default url should be None
        node = TextNode("Link text", TextType.LINK)
        node2 = TextNode("Link text", TextType.LINK, url=None)
        self.assertEqual(node, node2)

        # different url makes them unequal
        node_with_url = TextNode("Link text", TextType.LINK, url="https://example.com")
        self.assertNotEqual(node, node_with_url)

    def test_text(self):
        node = TextNode("This is a text node", TextType.PLAIN)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_image(self):
        node = TextNode("This is an image", TextType.IMAGE, "https://www.boot.dev")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(
            html_node.props,
            {"src": "https://www.boot.dev", "alt": "This is an image"},
        )

    def test_bold(self):
        node = TextNode("This is bold", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "This is bold")


class TestTextToTextNodes(unittest.TestCase):
    def assert_nodes_equal(self, a, b):
        self.assertEqual(len(a), len(b), f"Lengths differ: {a!r} vs {b!r}")
        for x, y in zip(a, b):
            self.assertEqual(x.text, y.text)
            self.assertEqual(x.text_type, y.text_type)
            self.assertEqual(getattr(x, "url", None), getattr(y, "url", None))

    def test_plain_text(self):
        s = "Just some plain text."
        out = text_to_textnodes(s)
        expected = [TextNode("Just some plain text.", TextType.PLAIN)]
        self.assert_nodes_equal(out, expected)

    def test_bold_italic_code(self):
        s = "This is **bold** and _italic_ with `code`."
        out = text_to_textnodes(s)
        expected = [
            TextNode("This is ", TextType.PLAIN),
            TextNode("bold", TextType.BOLD),
            TextNode(" and ", TextType.PLAIN),
            TextNode("italic", TextType.ITALIC),
            TextNode(" with ", TextType.PLAIN),
            TextNode("code", TextType.CODE),
            TextNode(".", TextType.PLAIN),
        ]
        self.assert_nodes_equal(out, expected)

    def test_image_and_link(self):
        s = "An ![alt text](http://img) here and a [link](https://example.com)"
        out = text_to_textnodes(s)
        expected = [
            TextNode("An ", TextType.PLAIN),
            TextNode("alt text", TextType.IMAGE, "http://img"),
            TextNode(" here and a ", TextType.PLAIN),
            TextNode("link", TextType.LINK, "https://example.com"),
        ]
        self.assert_nodes_equal(out, expected)

    def test_adjacent_images_and_links(self):
        s = "a ![x](http://i)![y](http://j) b [L](http://l)[M](http://m) c"
        out = text_to_textnodes(s)
        expected = [
            TextNode("a ", TextType.PLAIN),
            TextNode("x", TextType.IMAGE, "http://i"),
            TextNode("", TextType.PLAIN),
            TextNode("y", TextType.IMAGE, "http://j"),
            TextNode(" b ", TextType.PLAIN),
            TextNode("L", TextType.LINK, "http://l"),
            TextNode("", TextType.PLAIN),
            TextNode("M", TextType.LINK, "http://m"),
            TextNode(" c", TextType.PLAIN),
        ]
        self.assert_nodes_equal(out, expected)

    def test_full_example_from_prompt(self):
        s = ("This is **text** with an _italic_ word and a `code block` and an "
             "![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)")
        out = text_to_textnodes(s)
        expected = [
            TextNode("This is ", TextType.PLAIN),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.PLAIN),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.PLAIN),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.PLAIN),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.PLAIN),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assert_nodes_equal(out, expected)


class TestBlockToBlockType(unittest.TestCase):
    def test_paragraph(self):
        b = "This is a simple paragraph with **bold** and text."
        self.assertEqual(block_to_block_type(b), BlockType.PARAGRAPH)

    def test_heading(self):
        b = "### This is a level 3 heading"
        self.assertEqual(block_to_block_type(b), BlockType.HEADING)

    def test_code_block(self):
        b = "```\nline1\nline2\n```"
        self.assertEqual(block_to_block_type(b), BlockType.CODE)

    def test_quote_block(self):
        b = "> Quote line one\n>Quote line two\n> another line"
        self.assertEqual(block_to_block_type(b), BlockType.QUOTE)

    def test_unordered_list(self):
        b = "- first item\n- second item\n- third item"
        self.assertEqual(block_to_block_type(b), BlockType.UNORDERED_LIST)

    def test_ordered_list(self):
        b = "1. first\n2. second\n3. third"
        self.assertEqual(block_to_block_type(b), BlockType.ORDERED_LIST)


if __name__ == "__main__":
    unittest.main()
