from textnode import *


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for node in old_nodes:
        # only attempt splitting plain text nodes
        if node.text_type is not TextType.PLAIN:
            new_nodes.append(node)
            continue
        
        text = node.text
        if delimiter == "":
            new_nodes.append(node)
            continue

        parts = text.split(delimiter)
        if len(parts) == 1:
            # no delimiter present
            new_nodes.append(node)
            continue
    
        # We expect delimiters to come in pairs: pieces are like
        # [before, mid1, mid2, ..., after] where middles alternate between inside/outside.
        # If there's an unmatched delimiter, that's invalid markdown.
        if text.count(delimiter) % 2 != 0:
            raise ValueError(f"Unmatched delimiter {delimiter!r} in text {text!r}")
        
        pieces = []
        for i, piece in enumerate(parts):
            ## if piece == "" and i == 0:
                # leading empty before first delimiter -> treat as empty text
                ## pieces.append(TextNode(piece, TextType.PLAIN))
                ## continue
            if i % 2 == 0:
                # even index -> plain text
                ## if piece != "":
                pieces.append(TextNode(piece, TextType.PLAIN))
            else:
                # odd index -> inside delimiter -> target type
                pieces.append(TextNode(piece, text_type))

        new_nodes.extend(pieces)

    return new_nodes
