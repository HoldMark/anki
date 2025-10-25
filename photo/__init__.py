from anki.hooks import addHook
from aqt.utils import tooltip
from aqt.browser import Browser
from PyQt6 import QtWidgets


from .ui import UIDialog
from .utils import choose_default
from .data import possible_names_for_img, possible_names_for_name, possible_names_for_definition

# search query - поле с вводом текста; при выборе source указывается {name field}


def update_notes(browser: Browser, nids):
    # nids - список id карточек

    dialog = QtWidgets.QDialog(browser)
    form = UIDialog()
    form.setup_ui(dialog)

    note_type_set = set()

    for nid in nids:
        note = browser.mw.col.get_note(nid)
        note_type_id = note.note_type().get('id')

        if len(note_type_set) == 0:
            note_type_set.add(note_type_id)
        elif note_type_id in note_type_set:
            raise Exception(f"Note type id {note_type_id} is not unique")
            # TODO: заменить на красивый вывод о проблеме

    # set fields in form
    fields = browser.mw.col.get_note(nids[0]).keys()

    default_target = choose_default(fields, possible_names_for_img)
    form.set_target_fields(fields, default=default_target)

    default_source_1 = choose_default(fields, possible_names_for_name)
    form.set_source_1_fields(fields, default=default_source_1)

    default_source_2 = choose_default(fields, possible_names_for_definition)
    form.set_source_2_fields(fields, default=default_source_2)

    for nid in nids:
        note = browser.mw.col.get_note(nid)

        form.add_text(
            f"Note Id: {nid}; \n{note.items()}"
        )

    dialog.exec()


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
