import unittest

from textnode import *
from splitnode import split_nodes_delimiter

class TestSplitNodesDelimiter(unittest.TestCase):
    def assert_nodes_equal(self, a, b):
        self.assertEqual(len(a), len(b), f"Lengths differ: {a!r} vs {b!r}")
        for i, (n1, n2) in enumerate(zip(a, b)):
            self.assertEqual(n1, n2, f"Mismatch at index {i}: {n1!r} != {n2!r}")

    def test_no_delimiter_returns_same(self):
        node = TextNode("no delimiters here", TextType.PLAIN)
        out = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assert_nodes_equal(out, [node])

    def test_single_pair_backtick(self):
        node = TextNode("This is `code` text", TextType.PLAIN)
        out = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("This is ", TextType.PLAIN),
            TextNode("code", TextType.CODE),
            TextNode(" text", TextType.PLAIN),
        ]
        self.assert_nodes_equal(out, expected)

    def test_multiple_pairs_backtick(self):
        node = TextNode("a `x` b `y` c", TextType.PLAIN)
        out = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("a ", TextType.PLAIN),
            TextNode("x", TextType.CODE),
            TextNode(" b ", TextType.PLAIN),
            TextNode("y", TextType.CODE),
            TextNode(" c", TextType.PLAIN),
        ]
        self.assert_nodes_equal(out, expected)

    def test_bold_delimiter_double_star(self):
        node = TextNode("start **bold** end", TextType.PLAIN)
        out = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [
            TextNode("start ", TextType.PLAIN),
            TextNode("bold", TextType.BOLD),
            TextNode(" end", TextType.PLAIN),
        ]
        self.assert_nodes_equal(out, expected)

    def test_italic_delimiter_underscore(self):
        node = TextNode("a _italic_ b", TextType.PLAIN)
        out = split_nodes_delimiter([node], "_", TextType.ITALIC)
        expected = [
            TextNode("a ", TextType.PLAIN),
            TextNode("italic", TextType.ITALIC),
            TextNode(" b", TextType.PLAIN),
        ]
        self.assert_nodes_equal(out, expected)

    def test_unmatched_delimiter_raises(self):
        node = TextNode("unmatched ` here", TextType.PLAIN)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "`", TextType.CODE)

    def test_non_plain_nodes_unchanged(self):
        bold = TextNode("bold", TextType.BOLD)
        plain = TextNode("before `x` after", TextType.PLAIN)
        out = split_nodes_delimiter([bold, plain], "`", TextType.CODE)
        # bold should be left as-is; plain should be split
        expected = [
            bold,
            TextNode("before ", TextType.PLAIN),
            TextNode("x", TextType.CODE),
            TextNode(" after", TextType.PLAIN),
        ]
        self.assert_nodes_equal(out, expected)

    def test_empty_delimiter_returns_same(self):
        node = TextNode("something", TextType.PLAIN)
        out = split_nodes_delimiter([node], "", TextType.CODE)
        self.assert_nodes_equal(out, [node])

    def test_adjacent_delimiters_produce_empty_segments(self):
        # e.g. "a `` b" should produce an empty code node between delimiters
        node = TextNode("a `` b", TextType.PLAIN)
        out = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("a ", TextType.PLAIN),
            TextNode("", TextType.CODE),
            TextNode(" b", TextType.PLAIN),
        ]
        self.assert_nodes_equal(out, expected)

    def test_multiple_nodes_input(self):
        n1 = TextNode("one `x`", TextType.PLAIN)
        n2 = TextNode("two", TextType.PLAIN)
        out = split_nodes_delimiter([n1, n2], "`", TextType.CODE)
        expected = [
            TextNode("one ", TextType.PLAIN),
            TextNode("x", TextType.CODE),
            TextNode("", TextType.PLAIN),
            TextNode("two", TextType.PLAIN),
        ]
        self.assert_nodes_equal(out, expected)

    def test_order_of_operations_matters(self):
        # first split bold, then code — ensure result reflects order
        node = TextNode("a **b** `c` d", TextType.PLAIN)
        step1 = split_nodes_delimiter([node], "**", TextType.BOLD)
        # step1 should have a bold node in middle
        self.assertIn(TextNode("b", TextType.BOLD), step1)
        step2 = split_nodes_delimiter(step1, "`", TextType.CODE)
        expected = [
            TextNode("a ", TextType.PLAIN),
            TextNode("b", TextType.BOLD),
            TextNode(" ", TextType.PLAIN),
            TextNode("c", TextType.CODE),
            TextNode(" d", TextType.PLAIN),
        ]
        self.assert_nodes_equal(step2, expected)


if __name__ == "__main__":
    unittest.main()