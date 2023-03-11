from rich.text import Text

def strip_markups(txt: str):
    txt_obj = Text().from_markup(txt)
    return ''.join(txt_obj._text)