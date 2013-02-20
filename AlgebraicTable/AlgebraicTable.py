# (c) Wil Langford 2012
# This work is licensed under the Creative Commons
# Attribution-NonCommercial 3.0 Unported License.

# import numpy
import copy
import sys
import pickle
import itertools
# from collections import Iterable

#array = numpy.array
#shape = numpy.shape
#array_equal = numpy.array_equal
stderr = sys.stderr.write

global table_order

class AlgebraicTable(object):
	"""AlgebraicTable is a class for working with NxN tables in the context of abstract algebra.

It provides functions for extending partial Latin squares, checking whether a table is a group, etc."""

	def __init__(self, table_order, element_map=None, table=None):
		self._table_order = table_order
		if element_map==None:
			self._element_map = range(self._table_order)
		elif isinstance(element_map, list):
			self._element_map = [x for x in element_map]

		self._table = [range(table_order) for x in range(table_order)]
		if table == None:
			table = [[[0] for x in range(table_order)] for y in range(table_order)]
		self.setTable(table)
	
	def getTable_order(self):
		"""Get the order of the size of the table this particular instance is set/able to handle."""
		return self._table_order
	table_order = property(getTable_order)

	def getElement_map(self):
		return self._element_map
	def setElement_map(self, element_map):
		if len(element_map) != self.table_order:
			stderr("Element map must have length table_order.\n")
			sys.exit()
		else:
			self._element_map = [x for x in element_map]
	element_map = property(getElement_map, setElement_map)

	def getTable(self):
		return self._table
	def setTable(self, rawtable, element_map=[]):
#		stderr( 'rawtable\n' + str(rawtable) + '\n')
#		stderr( 'element_map\n' + str(self.element_map) + '\n')
		if isinstance(rawtable, list):		
			if not self._set_table_from_list(rawtable):
				stderr("Table has NOT been set.\n")
				return False
		else:
			stderr("Can't handle this type of input table (yet).\n")
			return False

	table = property(getTable, setTable)

	def setTableWithImpliedMap(self, listtable):
		self.element_map=listtable[0]
		self.table=listtable

	def _set_table_from_list(self, listtable):
		"""This sets the table from any 2D python iterable."""
		rows = range(len(listtable))
		cols = range(len(listtable[0]))
		if len(rows) != self.table_order:
			stderr("Table must have table_order rows. I see {0} instead of {1}.\n".format(rows,self.table_order))
			return False
		elif len(cols) != self.table_order:
			stderr("Table must have table_order cols. I see {0} instead of {1}.\n".format(rows,self.table_order))
			return False

		em = self.element_map

		for row in rows:
			for col in cols:
				item = copy.deepcopy(listtable[row][col])
				if isinstance(item, list):
					setitem = [em.index(x) for x in item]
				elif isinstance(item, int):
					setitem = [item]
				elif isinstance(item, str):
					setitem = [em.index(item)]
				else:
					stderr("I don't know what to do with this table entry input: " + str(item) + "\n")

				self._table[row][col] = setitem

		return True
	
	def __eq__(self,Y):
		X = self	
		if not isinstance(Y,AlgebraicTable):
			return False
		elif X.table_order != Y.table_order:
			return False
		elif X.element_map != Y.element_map:
			return False
		elif X._table != Y._table:
			return False
		else:
			return True

	def __ne__(self,Y):
		return not self == Y
	
	def __repr__(self):

		outstring = 'AlgebraicTable( ' + repr(self.table_order)
		outstring += ', element_map=' + repr(self.element_map)
		outstring += ', table=' + self._tablerepr() + '\n)'

		return outstring

	def _tablerepr(self):
		em=self.element_map
		rows = []
		for row in self.table:
			lists=[]
			for lst in row:
				lists.append('[' + ','.join([repr(em[x]) for x in lst]) + ']')
			rows.append('[' + ','.join(lists) + ']')
		
		return '[\n' + ',\n'.join(rows) + '\n]'

	def __str__(self):
		return self._tablerepr()

	def fix(self,a,b,c):
		em = self.element_map
		self._table[em.index(a)][em.index(b)]=[em.index(c)]


	def singleElimination(self):
		order = self.table_order
		tab = self.table

		while True:
			changed=False
			for row in range(order):
				removeMe = []
				for lst in tab[row]:
					if len(lst) == 1:
						removeMe.append(lst[0])

				for lst in tab[row]:
					for r in removeMe:
						while len(lst)>1 and lst.count(r)>0:
							lst.remove(r)
							changed=True

			for col in range(order):
				removeMe = []
				for row in range(order):
					lst = tab[row][col]
					if len(lst)==1:
						removeMe.append(lst[0])

				for row in range(order):
					lst = tab[row][col]
					for r in removeMe:
						while len(lst)>1 and lst.count(r)>0:
							lst.remove(r)
							changed=True

			if not changed:
				break


	def Completions(self):
		order = self.table_order
		orange = range(order)
		tab = self.table

		self.singleElimination()

		compset = []

		multicount=False
		for row in orange:
			if multicount:
				break
			for col in orange:
				if multicount:
					break
				lst = tab[row][col]
				if len(lst)>1:
					multicount=True
					for each in lst:
						forked = copy.deepcopy(self)
						forked.fix(row,col,each)
						for C in forked.Completions():
							if C:
								try:
									compset.index(C)
								except ValueError:
									compset.append(C)

		if not self.isLatinSquare:
			return False
		elif not multicount:
			return [self]
		else:
			return compset


	def isLatinSquare(self):
		tab = self.table
		orange = range(self.table_order)

		for row in orange:
			for lst in orange:
				if len(tab[row][lst])!=1:
					return False

		for rowcol in orange:
			for element in orange:
				try:
					tab[rowcol].index([element])
					tab[:][rowcol].index([element])
				except ValueError:
					return False

		return True
	
	def op(self,x,y):
		"""op(x,y) performs the operation on x and y as described by the current table."""
		em = self.element_map

		return em[self._numop(em.index(x),em.index(y))]
	
	def _numop(self,x,y):
		if not self.isLatinSquare:
			return False

		return self.table[x][y][0]
		

	def isAssociative(self):
		nop = self._numop
		orange = range(self.table_order)

		if not self.isLatinSquare:
			return False

		for a in orange:
			for b in orange:
				for c in orange:
					ab=nop(a,b)
					bc=nop(b,c)
					if nop(ab,c) != nop(a,bc):
						return False

		return True


		

########################################################
#
#         TEST CODE BELOW HERE
#

if __name__ == '__main__':
	"""Self-test routines."""
	print "Running test suite."
	print "Building test tables."
	Z2data = [['a','b'],['b','a']] 
	SymmetriesTriangle =   [['I','R','r','F','FR','Fr'],
							['R','r','I','FR','Fr','F'],
							['r','I','R','Fr','F','FR'],
							['F','Fr','FR','I','r','R'],
							['FR','F','Fr','R','I','r'],
							['Fr','FR','F','r','R','I']]
	tab1 = AlgebraicTable(6, element_map=['I','R','r','F','FR','Fr'], table=SymmetriesTriangle)
	Z2 = AlgebraicTable(2)
	Z2.setTableWithImpliedMap(Z2data)
	tab3 = AlgebraicTable(2,element_map=[0,1],table=[[0,1],[1,0]])
	tab4 = AlgebraicTable(2,element_map=[0,1],table=[[0,1],[1,1]])
	tab5 = AlgebraicTable(2,element_map=['a','b'],table=[['a','b'],['b','a']])


	print "Testing (in)equality assertions."
	assert tab1 == tab1
	assert Z2 == Z2
	assert tab1 != Z2
	assert Z2 != tab3
	assert Z2 != tab4
	assert Z2 == tab5
	print "Assertions passed."

	tabElim = AlgebraicTable(4, element_map=range(4), table=[[range(4) for y in range(4)] for x in range(4)])
	for rowcol in range(4):
		tabElim.fix(0,rowcol,rowcol)
		tabElim.fix(rowcol,0,rowcol)
	print "Testing singleElimination."
	tabElim.singleElimination()
	print tabElim
	
	print "Testing Latin square checker (1)... " + ('passed.' if not tabElim.isLatinSquare() else 'failed.')
	tabX = copy.deepcopy(Z2)
	print "Testing Latin square checker (2)... " + ('passed.' if tabX.isLatinSquare() else 'failed.')
	tabX.fix('b','b','b')
	print "Testing Latin square checker (3)... " + ('passed.' if not tabX.isLatinSquare() else 'failed.')

	print "Testing completions."
	for C in tabElim.Completions():
		print C
	
	print "Testing associativity checker (1)... " + ('passed.' if Z2.isAssociative() else 'failed.')
	tabNonAssoc = AlgebraicTable(5,element_map=range(5),table=[ [0,1,2,3,4], [1,3,4,0,2], [2,0,3,4,1], [3,4,1,2,0], [4,2,0,1,3]])
	print "Testing associativity checker (2)... " + ('passed.' if not tabNonAssoc.isAssociative() else 'failed.')


######################
#below here I'm just messing around.  Remove for final checking.
	tabFive = AlgebraicTable(5, element_map=range(5), table=[[range(5) for y in range(5)] for x in range(5)])
	for rowcol in range(5):
		tabFive.fix(0,rowcol,rowcol)
		tabFive.fix(rowcol,0,rowcol)
	
	for C in tabFive.Completions():
		if C.isAssociative:
			print C

