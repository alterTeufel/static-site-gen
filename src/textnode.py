from enum import Enum
from htmlnode import LeafNode


class TextType(Enum):
    TEXT = "text"
    PLAIN = "plain"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"


class TextNode:
    def __init__(self, text: str, text_type: TextType, url: str = None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        if not isinstance(other, TextNode):
            return False
        return (
            self.text == other.text
            and self.text_type == other.text_type
            and self.url == other.url
        )

    def __repr__(self):
        return f"TextNode({self.text!r}, {self.text_type.value!r}, {self.url!r})"


def text_node_to_html_node(text_node):
    t = text_node.text_type
    if t is TextType.PLAIN:
        return LeafNode(None, text_node.text)
    if t is TextType.BOLD:
        return LeafNode("b", text_node.text)
    if t is TextType.ITALIC:
        return LeafNode("i", text_node.text)
    if t is TextType.CODE:
        return LeafNode("code", text_node.text)
    if t is TextType.LINK:
        if not text_node.url:
            raise ValueError("LINK TextNode requires a url")
        return LeafNode("a", text_node.text, {"href": text_node.url})
    if t is TextType.IMAGE:
        if not text_node.url:
            raise ValueError("IMAGE TextNode requires a url")
        props = {"src": text_node.url, "alt": text_node.text}
        return LeafNode("img", "", props)
    raise TypeError(f"Unsupported TextNode type: {t!r}")

