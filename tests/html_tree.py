"""A small HTML tree for the template tests, from the standard library's parser: find elements
by tag, attributes and class, read their text and attributes."""
from html.parser import HTMLParser

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


class Node(object):
    def __init__(self, tag, attrs, parent=None):
        self.tag = tag
        self.attrs = attrs
        self.parent = parent
        self.children = []

    def __getitem__(self, name):
        return self.attrs[name]

    def get(self, name, default=None):
        return self.attrs.get(name, default)

    @property
    def classes(self):
        return (self.attrs.get("class") or "").split()

    def text(self):
        return "".join(c if isinstance(c, str) else c.text() for c in self.children)

    def words(self):
        """The text, whitespace collapsed."""
        return " ".join(self.text().split())

    def walk(self):
        for child in self.children:
            if isinstance(child, Node):
                yield child
                for node in child.walk():
                    yield node

    def find_all(self, tag=None, class_=None, **attrs):
        """Elements under this one; attrs by name with "_" for "-" (True: present at all)."""
        wanted = {name.replace("_", "-"): value for name, value in attrs.items()}
        found = []
        for node in self.walk():
            if tag is not None and node.tag != tag:
                continue
            if class_ is not None and class_ not in node.classes:
                continue
            if all((name in node.attrs) if value is True else node.attrs.get(name) == value for name, value in wanted.items()):
                found.append(node)
        return found

    def find(self, tag=None, class_=None, **attrs):
        found = self.find_all(tag, class_, **attrs)
        return found[0] if found else None

    def ancestor(self, **attrs):
        node = self.parent
        while node is not None:
            if all((name.replace("_", "-") in node.attrs) if v is True else node.attrs.get(name.replace("_", "-")) == v for name, v in attrs.items()):
                return node
            node = node.parent
        return None


class _Builder(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self, convert_charrefs=True)
        self.root = Node("#root", {})
        self.current = self.root

    def handle_starttag(self, tag, attrs):
        node = Node(tag, {name: ("" if value is None else value) for name, value in attrs}, self.current)
        self.current.children.append(node)
        if tag not in VOID:
            self.current = node

    def handle_startendtag(self, tag, attrs):
        node = Node(tag, {name: ("" if value is None else value) for name, value in attrs}, self.current)
        self.current.children.append(node)

    def handle_endtag(self, tag):
        node = self.current
        while node is not None and node.tag != tag:
            node = node.parent
        if node is not None and node.parent is not None:
            self.current = node.parent

    def handle_data(self, data):
        self.current.children.append(data)


def parse(markup):
    builder = _Builder()
    builder.feed(markup)
    builder.close()
    return builder.root
