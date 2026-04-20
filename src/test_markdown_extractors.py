import unittest
from markdown_utils import *


class TestMarkdownExtractors(unittest.TestCase):
    def test_extract_markdown_images_basic(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual(
            [("image", "https://i.imgur.com/zjjcJKZ.png")], matches
        )

    def test_extract_markdown_images_multiple(self):
        text = "Here ![one](http://a) and ![two](https://b.example/x.png) end"
        matches = extract_markdown_images(text)
        self.assertListEqual(
            [("one", "http://a"), ("two", "https://b.example/x.png")], matches
        )

    def test_extract_markdown_images_empty_alt(self):
        text = "Start ![](https://example.com/p.png) finish"
        matches = extract_markdown_images(text)
        self.assertListEqual([("", "https://example.com/p.png")], matches)

    def test_extract_markdown_images_with_parentheses_in_url(self):
        text = "![alt](https://example.com/path_(1).png)"
        matches = extract_markdown_images(text)
        self.assertListEqual([("alt", "https://example.com/path_(1).png")], matches)

    def test_extract_markdown_images_none(self):
        matches = extract_markdown_images("no images here [link](http://a)")
        self.assertListEqual([], matches)

    def test_extract_markdown_links_basic(self):
        matches = extract_markdown_links("See [Duck](https://duckduckgo.com)")
        self.assertListEqual([("Duck", "https://duckduckgo.com")], matches)

    def test_extract_markdown_links_multiple(self):
        text = "[a](http://a) middle [b](https://b.com/x) end"
        matches = extract_markdown_links(text)
        self.assertListEqual([("a", "http://a"), ("b", "https://b.com/x")], matches)

    def test_extract_markdown_links_empty_anchor(self):
        matches = extract_markdown_links("Link: [](http://a)")
        self.assertListEqual([("", "http://a")], matches)

    def test_extract_markdown_links_with_parentheses_in_url(self):
        text = "[title](https://example.com/a_(1).html)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("title", "https://example.com/a_(1).html")], matches)

    def test_images_and_links_together(self):
        text = "![i](http://img) and [L](http://link)"
        imgs = extract_markdown_images(text)
        links = extract_markdown_links(text)
        self.assertListEqual([("i", "http://img")], imgs)
        self.assertListEqual([("L", "http://link")], links)

    def test_overlapping_syntax_prefers_image_for_prefixed_exclamation(self):
        text = "![maybe](http://x) and [maybe](http://y)"
        imgs = extract_markdown_images(text)
        links = extract_markdown_links(text)
        self.assertIn(("maybe", "http://x"), imgs)
        self.assertIn(("maybe", "http://y"), links)

    def test_ignores_malformed_markdown(self):
        text = "![no_close(http://a] [bad](no_close"
        self.assertListEqual([], extract_markdown_images(text))
        self.assertListEqual([], extract_markdown_links(text))

class TestSplitImagesAndLinks(unittest.TestCase):
    def assert_nodes_equal(self, a, b):
        self.assertEqual(len(a), len(b), f"Lengths differ: {a!r} vs {b!r}")
        for i, (n1, n2) in enumerate(zip(a, b)):
            self.assertEqual(n1, n2, f"Mismatch at index {i}: {n1!r} != {n2!r}")

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.PLAIN,
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("This is text with an ", TextType.PLAIN),
            TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            TextNode(" and another ", TextType.PLAIN),
            TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
        ]
        self.assert_nodes_equal(new_nodes, expected)

    def test_split_links(self):
        node = TextNode(
            "A link [to boot dev](https://www.boot.dev) and one [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.PLAIN,
        )
        out = split_nodes_link([node])
        expected = [
            TextNode("A link ", TextType.PLAIN),
            TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode(" and one ", TextType.PLAIN),
            TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"),
        ]
        self.assert_nodes_equal(out, expected)

    def test_no_matches_returns_same_node(self):
        node = TextNode("no images or links here", TextType.PLAIN)
        self.assert_nodes_equal(split_nodes_image([node]), [node])
        self.assert_nodes_equal(split_nodes_link([node]), [node])

    def test_multiple_input_nodes(self):
        n1 = TextNode("before ![i](http://a) mid", TextType.PLAIN)
        n2 = TextNode("after", TextType.PLAIN)
        out = split_nodes_image([n1, n2])
        expected = [
            TextNode("before ", TextType.PLAIN),
            TextNode("i", TextType.IMAGE, "http://a"),
            TextNode(" mid", TextType.PLAIN),
            TextNode("after", TextType.PLAIN),
        ]
        self.assert_nodes_equal(out, expected)

    def test_adjacent_images_and_links(self):
        node = TextNode("a ![x](http://i)![y](http://j) b [L](http://l)[M](http://m) c", TextType.PLAIN)
        out_imgs = split_nodes_image([node])
        # images split; links still embedded in plain text for now
        expected_imgs = [
            TextNode("a ", TextType.PLAIN),
            TextNode("x", TextType.IMAGE, "http://i"),
            TextNode("", TextType.PLAIN),
            TextNode("y", TextType.IMAGE, "http://j"),
            TextNode(" b [L](http://l)[M](http://m) c", TextType.PLAIN),
        ]
        self.assert_nodes_equal(out_imgs, expected_imgs)

        # now split links on the result
        out_links = split_nodes_link(out_imgs)
        expected_links = [
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
        self.assert_nodes_equal(out_links, expected_links)

    def test_leading_and_trailing_matches(self):
        node = TextNode("![lead](http://a) middle [link](http://b) ![trail](http://c)", TextType.PLAIN)
        out = split_nodes_image([node])
        expected = [
            TextNode("", TextType.PLAIN),
            TextNode("lead", TextType.IMAGE, "http://a"),
            TextNode(" middle [link](http://b) ", TextType.PLAIN),
            TextNode("trail", TextType.IMAGE, "http://c"),
        ]
        self.assert_nodes_equal(out, expected)

    def test_non_plain_nodes_are_unchanged(self):
        bold = TextNode("bold", TextType.BOLD)
        plain = TextNode("before ![i](http://a) after", TextType.PLAIN)
        out = split_nodes_image([bold, plain])
        expected = [
            bold,
            TextNode("before ", TextType.PLAIN),
            TextNode("i", TextType.IMAGE, "http://a"),
            TextNode(" after", TextType.PLAIN),
        ]
        self.assert_nodes_equal(out, expected)

    def test_images_with_parentheses_in_url(self):
        node = TextNode("Look ![alt](https://example.com/img_(1).png) end", TextType.PLAIN)
        out = split_nodes_image([node])
        expected = [
            TextNode("Look ", TextType.PLAIN),
            TextNode("alt", TextType.IMAGE, "https://example.com/img_(1).png"),
            TextNode(" end", TextType.PLAIN),
        ]
        self.assert_nodes_equal(out, expected)

    def test_malformed_markup_left_unchanged(self):
        node = TextNode("broken ![no_close(http://a] text", TextType.PLAIN)
        self.assert_nodes_equal(split_nodes_image([node]), [node])
        node2 = TextNode("also [bad](no_close", TextType.PLAIN)
        self.assert_nodes_equal(split_nodes_link([node2]), [node2])


class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_leading_trailing_and_multiple_blank_lines(self):
        md = """

# Heading

Paragraph one.


Paragraph two after an extra blank line.




- item1
- item2

"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "# Heading",
                "Paragraph one.",
                "Paragraph two after an extra blank line.",
                "- item1\n- item2",
            ],
        )

    def test_only_whitespace_or_empty_input(self):
        self.assertEqual(markdown_to_blocks(""), [])
        self.assertEqual(markdown_to_blocks("\n\n\n"), [])
        self.assertEqual(markdown_to_blocks("   \n\n  \n"), [])


def test_paragraphs(self):
    md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

    node = markdown_to_html_node(md)
    html = node.to_html()
    self.assertEqual(
        html,
        "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
    )

def test_codeblock(self):
    md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

    node = markdown_to_html_node(md)
    html = node.to_html()
    self.assertEqual(
        html,
        "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
    )

def test_headings_and_inline(self):
    md = """# Top Heading

Some paragraph under the heading with **bold** and a [link](https://example.com)
"""
    node = markdown_to_html_node(md)
    html = node.to_html()
    self.assertEqual(
        html,
        "<div><h1>Top Heading</h1><p>Some paragraph under the heading with <b>bold</b> and a <a href=\"https://example.com\">link</a></p></div>",
    )

def test_blockquote(self):
    md = """> This is a quote line
> that continues on the next line with **bold** text
"""
    node = markdown_to_html_node(md)
    html = node.to_html()
    self.assertEqual(
        html,
        "<div><blockquote>This is a quote line\nthat continues on the next line with <b>bold</b> text</blockquote></div>",
    )

def test_lists_mixed(self):
    md = """- first item with _italic_
- second item

1. one
2. two
3. three
"""
    node = markdown_to_html_node(md)
    html = node.to_html()
    self.assertEqual(
        html,
        "<div><ul><li>first item with <i>italic</i></li><li>second item</li></ul><ol><li>one</li><li>two</li><li>three</li></ol></div>",
    )

def test_extract_title_basic(self):
    self.assertEqual(extract_title("# Hello"), "Hello")

def test_extract_title_missing(self):
    with self.assertRaises(ValueError):
        extract_title("No heading here\nJust text")


if __name__ == "__main__":
    unittest.main()