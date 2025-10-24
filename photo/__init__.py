from anki.hooks import addHook
from aqt.utils import tooltip
from aqt.browser import Browser


def update_notes(browser: Browser, nids):
    # nids - список id карточек

    for nid in nids:
        note = browser.mw.col.get_note(nid)
        print(note.items())


def add_photo(browser: Browser):
    nids = browser.selectedNotes()
    if not nids:
        tooltip("No cards selected.")
        return
    update_notes(browser, nids)


def setup_menu(browser: Browser):
    menu = browser.form.menuEdit
    menu.addSeparator()
    a = menu.addAction('Add Images')
    a.triggered.connect(lambda _, b=browser: add_photo(b))


addHook("browser.setupMenus", setup_menu)
