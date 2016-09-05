import io
import textwrap
import itertools
from aqt import mw
from aqt.qt import *
from anki.exporting import *
from PyQt4 import QtCore


class Window(QDialog):
    def __init__(self, mw):
        super(Window, self).__init__()
        self.mw = mw
        self.setWindowTitle("ConvertDecks2CramList")
        self.decks = []
        self.all_decks = mw.col.decks.allNames()
        self.home()
        self.show()

    def home(self):
    	'''Builds UI for plugin.'''
        label = QLabel(self)
        text = "Choose decks you want to export to file."
        longest_line = len(text)
        label.setText(text)
        label.move(0, 5)
        for index, deck in enumerate(self.all_decks):
            self.check_box = MyCheckBox(deck, self)
            self.check_box.stateChanged.connect(self.check_box.add_or_remove_deck_from_export)
            self.check_box.move(0, 30 + 20*index)
            if longest_line < len(deck):
                longest_line  = len(deck)
        btn = QPushButton("EXPORT", self)
        btn.resize(btn.sizeHint())
        bottom = 50 + 20*len(self.all_decks)
        btn.move(0, bottom)
        height = bottom + 40
        self.setGeometry(50, 50, longest_line*8, height)
        self.exporter = Exporter(self)
        btn.clicked.connect(self.exporter.convert_2_cram_list)

class MyCheckBox(QCheckBox):
    def __init__(self, text, window):
        self.text = text
        self.window = window
        super(QCheckBox,self).__init__(text, window)

    def add_or_remove_deck_from_export(self, state):
        if state == QtCore.Qt.Checked:
            self.window.decks.append(self.text)
        elif self.text in self.window.decks:
            self.window.decks.remove(self.text)


class Exporter(object):
    def __init__(self, window):
        self.window = window
        self.decks_to_export = self.window.decks

    def make_list_from_one_deck(self, deckName):
    	'''Converts a deck from SQL database into list of notes. '''
        col = mw.col
        decks = col.decks
        rosId = decks.id(deckName)
        list_of_cards = decks.cids(rosId)
        notes = []
        for id in list_of_cards:
            card = col.getCard(id) 
            note = card.note()
            notes.append([note.fields[0],note.fields[1]])
        return notes

    def get_file_name(self):
    	'''Initiates 'save into' window.'''
        name = QFileDialog.getSaveFileName()
        return name

    def make_list_from_decks(self, array):
    	'''Appends lists of notes from all checked decks into one list.'''
        decks = []
        for deck in array:
            decks += self.make_list_from_one_deck(deck)
        return decks

    def wrap_into_half_lines(self, decks):
    	'''Divides long sentences into 35 characters long lines and 
        matches part of given sentence with its translation.'''
        rows = decks
        rows = [[textwrap.wrap(thing, width=35) for thing in row] for row in rows]
        rows = [list(itertools.izip_longest(row[0], row[1], fillvalue = "")) for row in rows]
        rows = [[list(line) for line in row ] for row in rows]
        return rows

    def adjust_half_lines(self, rows):
    	'''Formats list into 2 columns.'''
        for index, row in enumerate(rows):
            length = len(rows[index])
            k = 0
            while k < length:
                i=0
                while i < len(rows[index][k]):
                    rows[index][k][i] = rows[index][k][i].ljust(35, " ") 
                    i+=1
                k+=1
        return rows

    def make_formatted_string(self, rows):
    	'''Converts list into nicely formatted string.'''
        to_save = ''
        for row in rows:
            for line in row: 
                to_save = to_save + line[0] + " " + line[1] + "\n\n"
        return to_save

    def save_string_to_file(self, file_name, string_to_save):
        if not string_to_save:
            with io.open(file_name, "wb") as readFile:
                readFile.write(string_to_save)
        else:
            with io.open(file_name, "w") as readFile:
                readFile.write(string_to_save)

    def convert_2_cram_list(self):
        decks = self.make_list_from_decks(self.decks_to_export)
        rows = self.wrap_into_half_lines(decks)
        name = self.get_file_name()
        rows = self.adjust_half_lines(rows)
        string_to_save = self.make_formatted_string(rows)
        self.save_string_to_file(name, string_to_save)

def run():
    GUI = Window(mw)
    GUI.exec_()

action = QAction("ConvertDecks2CramList", mw)
mw.connect(action, SIGNAL("triggered()"), run)
mw.form.menuTools.addAction(action)