class HTMLNode:
    def __init__(self, tag: str = None, value: str = None, children: list = None, props: dict = None):
        self.tag = tag
        self.value = value
        self.children = children or []
        self.props = props or {}

    def to_html(self):
        # raise NotImplementedError()
        
        # Text-only node
        if self.tag is None:
            return (self.value or "") + "".join(
                c.to_html() if hasattr(c, "to_html") else str(c) for c in self.children
            )

        # Self-closing tags
        self_closing = {"img", "br", "hr", "meta", "link"}
        props = self.props_to_html()

        if self.tag in self_closing:
            # include value only if present (for img alt via props usually)
            return f"<{self.tag}{props} />"

        # Normal element: render value (text) then children
        inner = (self.value or "") + "".join(
            c.to_html() if hasattr(c, "to_html") else str(c) for c in self.children
        )
        return f"<{self.tag}{props}>{inner}</{self.tag}>"

    def props_to_html(self):
        if not self.props:
            return ""
        parts = [f'{k}="{v}"' for k, v in self.props.items()]
        return " " + " ".join(parts)

    def __repr__(self):
        return (f"HTMLNode(tag={self.tag!r}, value={self.value!r}, "
                f"children={self.children!r}, props={self.props!r})")


class LeafNode(HTMLNode):
    def __init__(self, tag: str, value: str, props: dict | None = None):
        super().__init__(tag=tag, value=value, children=[], props=props)

    def to_html(self):
        if self.value is None:
            raise ValueError("LeafNode must have a value")
        if self.tag is None:
            return self.value
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"

    def __repr__(self):
        return f"LeafNode(tag={self.tag!r}, value={self.value!r}, props={self.props!r})"
    

class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, children, props)

    def to_html(self):
        if self.tag is None:
            raise ValueError("invalid HTML: no tag")
        if self.children is None:
            raise ValueError("invalid HTML: no children")
        children_html = ""
        for child in self.children:
            children_html += child.to_html()
        return f"<{self.tag}{self.props_to_html()}>{children_html}</{self.tag}>"

    def __repr__(self):
        return f"ParentNode({self.tag}, children: {self.children}, {self.props})"
    