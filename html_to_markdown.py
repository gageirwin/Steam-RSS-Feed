from html.parser import HTMLParser


class HTMLToMarkdownParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.markdown = ""
        self.links = []
        self.links_without_text = []

    def handle_starttag(self, tag, attrs):
        if tag == "p":
            self.markdown += "\n\n"
        elif tag == "strong" or tag == "b":
            self.markdown += "**"
        elif tag == "em" or tag == "i":
            self.markdown += "_"
        elif tag == "a":
            attrs_dict = dict(attrs)
            if "href" in attrs_dict:
                self.links.append({"text": "", "href": attrs_dict["href"]})

    def handle_endtag(self, tag):
        if tag == "p":
            self.markdown += "\n\n"
        elif tag == "strong" or tag == "b":
            self.markdown += "**"
        elif tag == "em" or tag == "i":
            self.markdown += "_"
        elif tag == "a":
            link = self.links.pop()
            if link["text"]:
                self.markdown += f"[{link['text']}]({link['href']}) "
            else:
                self.markdown += " "
                self.links_without_text.append(link["href"])

    def handle_data(self, data):
        if self.links:
            self.links[-1]["text"] += data
        else:
            self.markdown += data


def html_to_markdown(html):
    parser = HTMLToMarkdownParser()
    parser.feed(html)
    return parser.markdown, parser.links_without_text
