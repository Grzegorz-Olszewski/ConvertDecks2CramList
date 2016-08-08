# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showText
# import all of the Qt GUI library
from aqt.qt import *
from anki.exporting import *
import io
import textwrap
import itertools
from time import sleep
from PyQt4 import QtCore
from functools import partial


class Window(QDialog):

	def __init__(self, mw):
		super(Window, self).__init__()
		self.mw = mw
		self.setGeometry(50, 50, 500, 300)
		self.setWindowTitle("PQ status!")
		self.decks = []
		self.all_decks = mw.col.decks.allNames()
		self.home()
		self.show()

	def home(self):
		btn = QPushButton("EXPORT", self)
		btn.resize(btn.sizeHint())
		btn.move(0, 0)
		export = Exporter(self)
		btn.clicked.connect(export.convert2CramList)
		for index, deck in enumerate(self.all_decks):
			self.checkBox = aCheckBox(deck, self)
			self.checkBox.stateChanged.connect(self.checkBox.add_or_remove_deck_from_export)
			self.checkBox.move(0, 30+20*index)

	def enlarge_window(self, state):
		if state == QtCore.Qt.Checked:
			self.setGeometry(50, 50, 1000, 600)
		else:
			self.setGeometry(50, 50, 500, 300)


class aCheckBox(QCheckBox):
	def __init__(self, text, window):
		self.text = text
		self.window = window
		super(QCheckBox,self).__init__(text, window)

	def add_or_remove_deck_from_export(self, state):
		if state == QtCore.Qt.Checked:
			self.window.decks.append(self.text)
			self.window.setGeometry(50, 50, 1000, 600)	

		elif self.text in self.window.decks:
			self.window.decks.remove(self.text)

class Exporter(object):
	def __init__(self,window):
		self.window = window
		self.decks_to_export = self.window.decks

	def exportTextToFile(self):
		name  = QFileDialog.getSaveFileName()
		col = mw.col
		export = TextNoteExporter(col)
		with open(name, 'w') as newFile:
			export.doExport(newFile)
		return name
	def exportDeckToFile(self):
		col = mw.col
		decks = col.decks
		rosId = decks.id("Rosetta Spanish 1")
		listOfCards = decks.cids(rosId)
		notes = []
		for id in listOfCards:
		    card = col.getCard(id) 
		    note = card.note()
		    notes.append([note.fields[0],note.fields[1]])
		    
		return notes
	def wrapIntoHalfLines(self,textFile):
		rows = []
		if type(textFile) is list:
			rows = textFile
		else:
			with io.open(textFile, "r+", encoding='utf-8') as readFile:
				rows = []
				for row in readFile:
				    rows.append(row.split("\t"))
		rows = [[textwrap.wrap(thing,width=35) for thing in row] for row in rows]
		rows = [list(itertools.izip_longest(row[0],row[1],fillvalue="")) for row in rows]
		rows = [[list(line) for line in row ] for row in rows]
		return rows
	def adjustHalfLines(self,rows):
		for index, row in enumerate(rows):
			length = len(rows[index])
			k = 0
			while k < length:
				i=0
				while i < len(rows[index][k]):
					rows[index][k][i] = rows[index][k][i].ljust(35," ") 
					i+=1
				k+=1
		return rows

	def makeFormatedString(self,rows):
		to_save = ''
		for row in rows:
			for line in row:
				to_save = to_save + line[0] +" "+ line[1] + "\n\n"
		return to_save

	def saveStringToFile(self,fileName,string_to_save):
		with io.open(fileName, "w") as readFile:
			readFile.write(string_to_save)

	def convert2CramList(self):
		    
		name = exportTextToFile()
		rows = wrapIntoHalfLines(name)
		#name = "NewOne1.txt"
		rows = adjustHalfLines(rows)
		string_to_save = makeFormatedString(rows)
		saveStringToFile(name,string_to_save)


def run():
	GUI = Window(mw)
	GUI.exec_()

action = QAction("ConvertDecks2CramList", mw)
mw.connect(action, SIGNAL("triggered()"), run)
mw.form.menuTools.addAction(action)