# -*- coding: UTF-8 -*-
# Copyright 2016-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

# See https://dev.lino-framework.org/dev/bleach.html

import re
from bs4 import BeautifulSoup, NavigableString, Comment, Doctype
from bs4.element import Tag
import logging; logger = logging.getLogger(__file__)
from lino.api import dd


PARAGRAPH_TAGS = {
    "p",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "h7",
    "h8",
    "h9",
    "pre",
    "li",
    "div",
}

WHITESPACE_TAGS = PARAGRAPH_TAGS | {
    "[document]",
    "span",
    "ul",
    "html",
    "head",
    "body",
    "base",
}


class Style:
    # TODO: Extend rstgen.sphinxconf.sigal_image.Format to incoroporate this.
    def __init__(self, s):
        self._map = {}
        if s:
            for i in s.split(";"):
                k, v = i.split(":", maxsplit=1)
                self._map[k.strip()] = v.strip()
        self.is_dirty = False

    def __contains__(self, *args):
        return self._map.__contains__(*args)

    def __setitem__(self, k, v):
        if k in self._map and self._map[k] == v:
            return
        self._map[k] = v
        self.is_dirty = True

    def __delitem__(self, k):
        if k in self._map:
            self.is_dirty = True
        return self._map.__delitem__(k)

    def adjust_size(self):
        # if self['float'] == "none":
        #     return
        if "width" in self._map:
            del self["width"]
        self["height"] = dd.plugins.memo.short_preview_image_height

    def as_string(self):
        return ";".join(["{}:{}".format(*kv) for kv in self._map.items()])


class TextCollector:
    def __init__(self, max_length=None):
        self.text = ""
        self.sep = ""  # becomes "\n\n" after a PARAGRAPH_TAGS
        self.remaining = max_length or settings.SITE.plugins.memo.short_preview_length
        self.image = None

    def add_chunk(self, ch):
        # print("20230712 add_chunk", ch.name, ch)

        if ch.name in WHITESPACE_TAGS:
            for c in ch.children:
                if not self.add_chunk(c):
                    return False
            if ch.name in PARAGRAPH_TAGS:
                self.sep = "\n\n"
            else:
                self.sep = " "
            return True

        assert ch.name != "IMG"

        if ch.name == "img":
            if self.image is not None:
                # Ignore all images except the first one.
                self.text += self.sep
                return True
            style = Style(ch.get("style", None))
            if not "float" in style:
                style["float"] = "right"
            style.adjust_size()
            if style.is_dirty:
                ch["style"] = style.as_string()
            self.image = ch
            # print("20231023 a", ch)

        we_want_more = True
        if ch.string is not None:
            if len(ch.string) > self.remaining:
                # print("20231023", len(ch.string), '>', self.remaining)
                ch.string = ch.string[: self.remaining] + "..."
                we_want_more = False
                # print("20230927", ch.string, ch)
                # self.text += str(ch.string) + "..."
                # return False
            self.remaining -= len(ch.string)

        if isinstance(ch, NavigableString):
            self.text += self.sep + ch.string
        else:
            self.text += self.sep + str(ch)

        self.remaining -= len(self.sep)
        self.sep = ""
        return we_want_more


def truncate_comment(html_str, max_length=300):
    # Returns a single paragraph with a maximum number of visible chars.
    # new implementation since 20230713
    html_str = html_str.strip()  # remove leading or trailing newlines

    if not html_str.startswith("<"):
        # print("20231023 c", html_str)
        if len(html_str) > max_length:
            return html_str[:max_length] + "..."
        return html_str

    # if "choose one or the other" in html_str:
    #     print(html_str)
    #     raise Exception("20230928 {} {}".format(len(html_str), max_length))

    soup = BeautifulSoup(html_str, features="html.parser")
    tc = TextCollector(max_length)
    tc.add_chunk(soup)
    return tc.text



def old_truncate_comment(html_str, max_p_len=None):
    # returns a single paragraph with a maximum number of visible chars.
    # No longer used. Replaced by new truncate_comment() below
    if max_p_len is None:
        max_p_len = settings.SITE.plugins.memo.short_preview_length
    html_str = html_str.strip()  # remove leading or trailing newlines

    if not html_str.startswith("<"):
        if len(html_str) > max_p_len:
            txt = html_str[:max_p_len] + "..."
        else:
            txt = html_str
        return txt
    soup = BeautifulSoup(html_str, "html.parser")
    ps = soup.find_all(
        ["p", "h1", "h2", "h3", "h4", "h5", "h6", "h7", "h8", "h9", "pre"]
    )
    if len(ps) > 0:
        anchor_end = "</a>"
        txt = ""
        for p in ps:
            text = ""
            for c in p.contents:
                if isinstance(c, Tag):
                    if c.name == "a":
                        text += str(c)
                        max_p_len = max_p_len + len(text) - len(c.text)
                    else:
                        # text += str(c)
                        text += c.text
                else:
                    text += str(c)

            if len(txt) + len(text) > max_p_len:
                txt += text
                if anchor_end in txt:
                    ae_index = txt.index(anchor_end) + len(anchor_end)
                    if ae_index >= max_p_len:
                        txt = txt[:ae_index]
                        txt += "..."
                        break
                txt = txt[:max_p_len]
                txt += "..."
                break
            else:
                txt += text + "\n\n"
        return txt
    return html_str

# remove these tags including their content.
blacklist = frozenset(["script", "style", "head"])

# unwrap these tags (remove the wrapper and leave the content)
unwrap = frozenset(["html", "body"])

useless_main_tags = frozenset(["p", "div", "span"])

ALLOWED_TAGS = frozenset([
    "a",
    "b",
    "i",
    "em",
    "ul",
    "ol",
    "li",
    "strong",
    "p",
    "br",
    "span",
    "pre",
    "def",
    "div",
    "img",
    "table",
    "th",
    "tr",
    "td",
    "thead",
    "tfoot",
    "tbody",
])


# Map of allowed attributes by tag. Copied from bleach.sanitizer:
ALLOWED_ATTRIBUTES = {
    "a": {"href", "title"},
    "abbr": {"title"},
    "acronym": {"title"},
}

ALLOWED_ATTRIBUTES["span"] = {
    "class",
    "data-index",
    "data-denotation-char",
    "data-link",
    "data-title",
    "data-value",
    "contenteditable",
}
ALLOWED_ATTRIBUTES["p"] = {"align", "style"}

# def safe_css(attr, css):
#     if attr == "style":
#         return re.sub("(width|height):[^;]+;", "", css)
#     return css

def sanitize(old):

    # Inspired by https://chase-seibert.github.io/blog/2011/01/28/sanitize-html-with-beautiful-soup.html

    old = old.strip()
    if not old:
        return old

    try:
        soup = BeautifulSoup(old, features="lxml")
    except HTMLParseError as e:
        logger.info("Could not sanitize %r : %s", old, e)
        return f"Could not sanitize content ({e})"

    for tag in soup.findAll():
        # print(tag)
        tag_name = tag.name.lower()
        if tag_name in blacklist:
            # blacklisted tags are removed in their entirety
            tag.extract()
        elif tag_name in unwrap:
            tag.unwrap()
        elif tag_name in ALLOWED_TAGS:
            # tag is allowed. Make sure all the attributes are allowed.
            allowed = ALLOWED_ATTRIBUTES.get(tag_name, None)
            if allowed is None:
                tag.attrs = dict()
            else:
                tag.attrs = {k: v for k, v in tag.attrs.items() if k in allowed}
        else:
            # print(tag.name)
            # tag.decompose()
            # tag.extract()
            # not a whitelisted tag. I'd like to remove it from the tree
            # and replace it with its children. But that's hard. It's much
            # easier to just replace it with an empty span tag.
            tag.name = "span"
            tag.attrs = dict()

    # remove all comments because they might contain scripts
    comments = soup.findAll(text=lambda text:isinstance(text, (Comment, Doctype)))
    for comment in comments:
        comment.extract()

    # remove the wrapper tag if it is useless
    if len(soup.contents) == 1:
        main_tag = soup.contents[0]
        if main_tag.name in useless_main_tags and not main_tag.attrs:
            main_tag.unwrap()

    return str(soup).strip()
