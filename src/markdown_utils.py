import re
from textnode import *
from enum import Enum
from htmlnode import HTMLNode


_RE_CODE = re.compile(r'`([^`]+?)`')
_RE_BOLD = re.compile(r'\*\*([^\*]+?)\*\*')
_RE_ITALIC = re.compile(r'_([^_]+?)_')
_IMAGE_RE = re.compile(r'!\[([^\]]*)\]\(([^)\s]*?(?:\([^\)]*\)[^)\s]*?)*?)\)')
_LINK_RE = re.compile(r'(?<!\!)\[([^\]]*)\]\(([^)\s]*?(?:\([^\)]*\)[^)\s]*?)*?)\)')

def extract_markdown_images(text: str):
    # This returns a list of (alt, url) tuples for each match; alt may be empty if markup uses [Image blocked: No description].
    return [(m.group(1), m.group(2)) for m in _IMAGE_RE.finditer(text)]

def extract_markdown_links(text: str):
    """Return list of (anchor_text, url) for markdown links like [text](url)."""
    # This returns an empty list if no matches; anchor text may be empty for [](url).
    return [(m.group(1), m.group(2)) for m in _LINK_RE.finditer(text)]

def _split_by_pattern(old_nodes, pattern, make_node):
    new_nodes = []
    for node in old_nodes:
        if node.text_type is not TextType.PLAIN:
            new_nodes.append(node)
            continue
        text = node.text
        pos = 0
        any_match = False
        for m in pattern.finditer(text):
            any_match = True
            start, end = m.span()
            # append plain piece before match (may be empty)
            new_nodes.append(TextNode(text[pos:start], TextType.PLAIN))
            # append the matched node (image/link)
            new_nodes.append(make_node(m))
            pos = end
        if any_match:
            # append trailing plain piece if non-empty
            tail = text[pos:]
            if tail != "":
                new_nodes.append(TextNode(tail, TextType.PLAIN))
        else:
            # no matches — keep original node as-is
            new_nodes.append(node)
    return new_nodes

def split_nodes_image(old_nodes):
    def make_image_node(m):
        alt = m.group(1)
        url = m.group(2)
        return TextNode(alt, TextType.IMAGE, url=url)
    return _split_by_pattern(old_nodes, _IMAGE_RE, make_image_node)


def split_nodes_link(old_nodes):
    def make_link_node(m):
        anchor = m.group(1)
        url = m.group(2)
        return TextNode(anchor, TextType.LINK, url=url)
    return _split_by_pattern(old_nodes, _LINK_RE, make_link_node)

def text_to_textnodes(text: str):
    # start with one plain TEXT node
    nodes = [TextNode(text, TextType.PLAIN)]

    # order matters: code first, then bold, italic, images, links
    def make_code(m):
        return TextNode(m.group(1), TextType.CODE)
    nodes = _split_by_pattern(nodes, _RE_CODE, make_code)

    def make_bold(m):
        return TextNode(m.group(1), TextType.BOLD)
    nodes = _split_by_pattern(nodes, _RE_BOLD, make_bold)

    def make_italic(m):
        return TextNode(m.group(1), TextType.ITALIC)
    nodes = _split_by_pattern(nodes, _RE_ITALIC, make_italic)

    def make_image(m):
        return TextNode(m.group(1), TextType.IMAGE, url=m.group(2))
    nodes = _split_by_pattern(nodes, _IMAGE_RE, make_image)

    def make_link(m):
        return TextNode(m.group(1), TextType.LINK, url=m.group(2))
    nodes = _split_by_pattern(nodes, _LINK_RE, make_link)

    return nodes


def markdown_to_blocks(markdown: str):
    """
    Split a raw Markdown document into block strings.

    Rules:
    - Split on two or more consecutive newlines (treat as block separators).
    - Strip leading/trailing whitespace from each block.
    - Omit empty blocks.
    """
    if markdown is None:
        return []

    # Normalize line endings, then split on two-or-more newlines
    # Use simple split by '\n\n' repeatedly to handle multiple blank lines
    parts = markdown.replace('\r\n', '\n').replace('\r', '\n').split('\n\n')

    blocks = []
    for p in parts:
        b = p.strip()
        if b:
            blocks.append(b)
    return blocks


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

def block_to_block_type(block: str) -> BlockType:
    if block is None:
        return BlockType.PARAGRAPH
    b = block.strip()
    if b == "":
        return BlockType.PARAGRAPH

    # Heading: 1-6 # then space
    if re.match(r'^(#{1,6})\s+', b):
        return BlockType.HEADING

    # Code block: starts with ``` and ends with ``` and has at least one newline
    if b.startswith("```") and "\n" in b and b.rstrip().endswith("```"):
        return BlockType.CODE

    # Split lines and normalize
    lines = [ln.rstrip() for ln in b.splitlines() if ln is not None]
    if not lines:
        return BlockType.PARAGRAPH

    # Quote: every line begins with '>' (optionally followed by space)
    if all(re.match(r'^\>\s?.*', ln) for ln in lines):
        return BlockType.QUOTE

    # Unordered list: every line begins with '- ' (dash then space)
    if all(re.match(r'^\-\s+.+', ln) for ln in lines):
        return BlockType.UNORDERED_LIST

    # Ordered list: every line matches 'N. ' with consecutive numbering starting at 1
    expected = 1
    ord_ok = True
    for ln in lines:
        m = re.match(r'^(\d+)\.\s+(.+)', ln)
        if not m:
            ord_ok = False
            break
        if int(m.group(1)) != expected:
            ord_ok = False
            break
        expected += 1
    if ord_ok and len(lines) > 0:
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH

def _wrap_children_in_tag(tag: str, children):
    """Create an HTMLNode with tag and attach children (list of HTMLNode)."""
    node = HTMLNode(tag=tag, props={}, children=[])
    for c in children:
        node.children.append(c)
    return node

def _inline_text_to_htmlnodes(text: str):
    """Convert inline markdown text into a list of HTMLNode children by using text_to_textnodes -> text_node_to_html_node."""
    text_nodes = text_to_textnodes(text)
    html_children = [text_node_to_html_node(tn) for tn in text_nodes]
    return html_children

def markdown_to_html_node(markdown: str):
    """
    Convert a full markdown document into a single parent HTMLNode (div) containing block HTMLNodes.
    Relies on:
      - markdown_to_blocks(markdown) -> list[str]
      - block_to_block_type(block) -> BlockType
      - text_to_textnodes(text) -> list[TextNode]
      - text_node_to_html_node(text_node) -> HTMLNode
    """
    parent = HTMLNode(tag="div", props={}, children=[])

    blocks = markdown_to_blocks(markdown)
    for blk in blocks:
        btype = block_to_block_type(blk)

        if btype is BlockType.HEADING:
            # count heading level
            m = re.match(r'^(#{1,6})\s+(.*)', blk, flags=re.DOTALL)
            if m:
                level = len(m.group(1))
                inner = m.group(2).strip()
            else:
                # fallback: treat as paragraph if malformed
                level = 1
                inner = blk
            tag = f"h{level}"
            children = _inline_text_to_htmlnodes(inner)
            block_node = _wrap_children_in_tag(tag, children)

        elif btype is BlockType.PARAGRAPH:
            children = _inline_text_to_htmlnodes(blk)
            block_node = _wrap_children_in_tag("p", children)

        elif btype is BlockType.CODE:
            # For fenced code block, don't parse inline markdown.
            # Remove surrounding ``` fences if present.
            content = blk
            if content.startswith("```"):
                # strip starting fence and optional language line
                # locate first newline after opening ```
                first_nl = content.find("\n")
                if first_nl != -1:
                    body = content[first_nl+1:]
                else:
                    body = ""
                # strip trailing fence if present
                if body.endswith("```"):
                    body = body[:-3]
                # don't strip internal leading/trailing newlines except common ones
                code_text = body
            else:
                code_text = content
            # create a text node and convert to HTMLNode (usually <code> or <pre><code>)
            tn = TextNode(code_text, TextType.CODE)
            code_html = text_node_to_html_node(tn)
            # ensure we wrap in <pre> if not already block-level from text_node_to_html_node
            # assume text_node_to_html_node returns a <code> tag; wrap in <pre>
            block_node = HTMLNode(tag="pre", props={}, children=[code_html])

        elif btype is BlockType.QUOTE:
            # strip leading "> " from each line before inline parsing
            lines = [re.sub(r'^\>\s?', '', ln) for ln in blk.splitlines()]
            joined = "\n".join(lines)
            children = _inline_text_to_htmlnodes(joined)
            block_node = _wrap_children_in_tag("blockquote", children)

        elif btype is BlockType.UNORDERED_LIST:
            # each line starts with "- "
            items = [re.sub(r'^\-\s+', '', ln) for ln in blk.splitlines()]
            li_nodes = []
            for it in items:
                children = _inline_text_to_htmlnodes(it)
                li = _wrap_children_in_tag("li", children)
                li_nodes.append(li)
            block_node = HTMLNode(tag="ul", props={}, children=li_nodes)

        elif btype is BlockType.ORDERED_LIST:
            # lines like "1. text"
            items = []
            for ln in blk.splitlines():
                m = re.match(r'^\d+\.\s+(.*)', ln)
                items.append(m.group(1) if m else ln)
            li_nodes = []
            for it in items:
                children = _inline_text_to_htmlnodes(it)
                li = _wrap_children_in_tag("li", children)
                li_nodes.append(li)
            block_node = HTMLNode(tag="ol", props={}, children=li_nodes)

        else:
            # fallback to paragraph
            children = _inline_text_to_htmlnodes(blk)
            block_node = _wrap_children_in_tag("p", children)

        parent.children.append(block_node)

    return parent

def extract_title(markdown: str) -> str:
    """
    Return the firts level-1 heading text (a line starting with a single '#').
    Raise ValeuError if no H1 heading is found.
    """
    if markdown is None:
        raise ValueError("No markdown provided")
    
    # Normalize line endings and iterate lines
    for ln in markdown.replace('\r\n', '\n').replace('\r', '\n').split('\n'):
        s = ln.strip()
        if not s:
            continue
        # Match a single leading '#' followed by at least one space
        if s.startswith("# "):
            return s[2:].strip()
        # m = re.match(r'^\\#\s+(.*)\$', s)
        # if m:
        #     return m.group(1).strip()
        
    raise ValueError("No level-1 heading found")