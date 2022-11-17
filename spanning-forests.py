import copy
import math
import sys
import time
import json

class Iterator:
    def __init__(self, iterator):
        self.iterator = iterator
        self.current = None
    def __next__(self):
        try:
            self.current = next(self.iterator)
        except StopIteration:
            self.current = None
        finally:
            return self.current

class ProductGraph:
	def __init__(self, *args):
		if isinstance(args[2], bool):
			if args[2] == False:
				self.product = weakProduct(args[0], args[1])
				self.graph1 = args[0];
				self.graph2 = args[1];
				self.type = "weak"
			else:
				self.product = strongProduct(args[0], args[1])
				self.graph1 = args[0];
				self.graph2 = args[1];
				self.type = "strong"

		else:
			self.product = args[0]
			self.graph1 = args[1]
			self.graph2 = args[2]

class Graph:
	def __init__(self, vDict = None):
		if isinstance(vDict, int):
			self.vDict = {}
			for i in range(vDict):
				adjList = set()
				for j in range(vDict):
					if i != j:
						adjList.add(j)
				self.vDict[i] = adjList
		else:
			if vDict is None:
				vDict = []
			self.vDict = vDict

	def getVertices(self):
		return list(self.vDict.keys())

	def getAdjacencies(self, vertex):
		return self.vDict[vertex]

def cantorMap(x,y):
	return round(0.5 * (x + y) * (x + y + 1) + y)

def invCantor(z):
	w = int((math.sqrt(8*z + 1) - 1) * 0.5)
	t = round((w+1)*w*0.5)
	y = z - t
	return [w - y, y]

def mergeTrees(tGraph, tVer, hGraph, hVer):
	nGraph = copy.deepcopy(tGraph)
	for ver in hGraph:
		nGraph[ver] = hGraph[ver].copy()
	nGraph[tVer].add(hVer)
	return nGraph

def mergeComponents(forest):
	vDict = {}
	for component in forest:
		for vKeys in component:
			vDict[vKeys] = component[vKeys].copy()
	return Graph(vDict)

def strongProduct(graph1, graph2):
	vDict = {}
	for gVert in graph1.vDict:
		for hVert in graph2.vDict:
			ghVert = cantorMap(gVert, hVert)
			adjList = set()
			for agVert in graph1.vDict[gVert]:
				adjList.add(cantorMap(agVert, hVert))
			for ahVert in graph2.vDict[hVert]:
				adjList.add(cantorMap(gVert, ahVert))
				for agVert in graph1.vDict[gVert]:
					adjList.add(cantorMap(agVert, ahVert))
			vDict[ghVert] = adjList
	return Graph(vDict)

def weakProduct(graph1, graph2):
	vDict = {}
	for gVert in graph1.vDict:
		for hVert in graph2.vDict:
			ghVert = cantorMap(gVert, hVert)
			adjList = set()
			for agVert in graph1.vDict[gVert]:
				adjList.add(cantorMap(agVert, hVert))
			for ahVert in graph2.vDict[hVert]:
				adjList.add(cantorMap(gVert, ahVert))
			vDict[ghVert] = adjList
	return Graph(vDict)

def getSpanningForests(graph):
	return spanForests(graph, [], [], graph.getVertices(), 0)

def checkTree(forest):
	for vertex in forest.vDict:
		if len(forest.vDict[vertex]) == 0:
			rootVer = vertex
	for vertex in forest.vDict:
		currVer = vertex
		while len(forest.vDict[currVer]) == 1:
			currVer = next(iter(forest.vDict[currVer]))
		if currVer != rootVer:
			return False
	return True

def spanForests(graph, forests, forest, keyList, currIndex):
	if currIndex == len(keyList):
		candFor = mergeComponents(forest)
		"""if not checkTree(candFor):
			return"""
		forests.append(candFor)
		return

	#Adding a single vertex to the forest
	nForest = copy.deepcopy(forest)	
	nForest.append({keyList[currIndex] : set()})
	spanForests(graph, forests, nForest, keyList, currIndex + 1)

	#Adding possible outgoing edges
	for aVert in graph.vDict[keyList[currIndex]]:
		hIndex = -1
		tIndex = -1
		nForest = copy.deepcopy(forest)
		for index, component in enumerate(forest):
			if tIndex == -1 and keyList[currIndex] in component:
				tIndex = index
			if hIndex == -1 and aVert in component:
				hIndex = index 
			if tIndex != -1 and hIndex != -1:
				break
		if tIndex == -1 and hIndex == -1:
			nForest.append({keyList[currIndex] : {aVert}, aVert : set()})
			spanForests(graph, forests, nForest, keyList, currIndex + 1)
		elif tIndex == -1 and hIndex != -1:
			nForest[hIndex][keyList[currIndex]] = {aVert}
			spanForests(graph, forests, nForest, keyList, currIndex + 1)
		elif tIndex != -1 and hIndex == -1:
			nForest[tIndex][keyList[currIndex]] = {aVert}
			nForest[tIndex][aVert] = set()
			spanForests(graph, forests, nForest, keyList, currIndex + 1)
		elif tIndex != hIndex:
			if tIndex > hIndex:
				del nForest[tIndex]
				del nForest[hIndex]
				nForest.append(mergeTrees(forest[tIndex], keyList[currIndex], forest[hIndex], aVert))
				spanForests(graph, forests, nForest, keyList, currIndex + 1)
			else:
				del nForest[hIndex]
				del nForest[tIndex]
				nForest.append(mergeTrees(forest[tIndex], keyList[currIndex], forest[hIndex], aVert))
				spanForests(graph, forests, nForest, keyList, currIndex + 1)
	"""for x in forests:
		print(x.vDict)"""
	return forests

def getGSpanningForests(pGraph, numHori, numDiag, verticalSet, forestSet):
	gForests = []
	for i, forest in enumerate(forestSet):
		if forest[1] == False:
			projection = getGProjection(pGraph, forest[0])
			if (numHori, numDiag) == (projection[0], projection[1]) and verticalSet == projection[2]:
				gForests.append(forest[0])
				forest[1] = True
	return gForests

def getGSpanningVertForests(pGraph, numHori, numDiag, verticalSet, forestSet):
	gForests = []
	for i, forest in enumerate(forestSet):
		if forest[1] == False:
			projection = getGProjection(pGraph, forest[0])
			if (numHori, numDiag) == (projection[0], projection[1]) and verticalSet == projection[2]:
				gForests.append(forest[0])
				forest[1] = True
	return gForests 

def getGProjection(pGraph, forest):
	numHori = 0
	numDiag = 0
	verticalSet = {}
	for tail in forest.vDict:
		if len(forest.vDict[tail]) == 1:
			head = next(iter(forest.vDict[tail]))
			ord1 = invCantor(tail)
			ord2 = invCantor(head)
			if ord1[0] == ord2[0]:
				if ord1[0] in verticalSet:
					verticalSet[ord1[0]] += 1
				else:
					verticalSet[ord1[0]] = 1
			elif ord1[1] == ord2[1]:
				numHori += 1
			else:
				numDiag += 1
	return (numHori, numDiag, verticalSet)

def getMultispin(pGraph, forests, vertSet):
	vSetMultispin = {}
	for vertex in vertSet:
		vSetMultispin[vertex] = {}
	for forest in forests:
		for vertexA in vSetMultispin:
			multispin = {}
			for vertexB in pGraph.graph2.vDict:
				for adjVert in forest.vDict[cantorMap(vertexA, vertexB)]:
					x, y = invCantor(adjVert)
					if x == vertexA:
						if y in multispin:
							multispin[y] += 1
						else:
							multispin[y] = 1
			tMultispin = frozenset(multispin.items())
			if tMultispin in vSetMultispin[vertexA]:
				vSetMultispin[vertexA][tMultispin] += 1
			else:
				vSetMultispin[vertexA][tMultispin] = 1
	return vSetMultispin

def testIndependence(pGraph):
	forestSet = [[x, False] for x in getSpanningForests(pGraph.product)]
	print(len(forestSet))
	for candForest in forestSet:
		if candForest[1] == False:
			if not testIndivIndependence(pGraph, candForest[0], forestSet):
				return False
	return True

def testIndivIndependence(pGraph, forest, forestSet):
	hori, diag, vertSet = getGProjection(pGraph, forest)
	forests = getGSpanningForests(pGraph, hori, diag, vertSet, forestSet)
	vSetMultispin = getMultispin(pGraph, forests, vertSet)
	if len(vSetMultispin) != 0:
		iterList = []
		for vert in vSetMultispin:
			iterList.append(Iterator(iter(vSetMultispin[vert])))
		for it in iterList:
			next(it)
		tupleList = returnTuples(iterList, 0, {}, [], vSetMultispin)
		countList = copy.copy(tupleList)
		for item in countList:
			countList[item] = 0
		for forest in forests:
			multiList = []
			for vertexA in vSetMultispin:
				multispin = {}
				for vertexB in pGraph.graph2.vDict:
					for adjVert in forest.vDict[cantorMap(vertexA, vertexB)]:
						x, y = invCantor(adjVert)
						if x == vertexA:
							if y in multispin:
								multispin[y] += 1
							else:
								multispin[y] = 1
				multiList.append(frozenset(multispin.items()))
			countList[tuple(multiList)] += 1
		for item in countList:
			for i in range(len(vSetMultispin)-1):
				countList[item] *= len(forests)
		if tupleList != countList:
			print(forest.vDict)
			print(getGProjection(pGraph, forest))
			print(countList)
			print(vEdgeSet)
			return False
	return True

def getVertEdgeSet(pGraph, forests, vertSet):
	vEdgeSet = {}
	for vertex in vertSet:
		vEdgeSet[vertex] = {}
	for forest in forests:
		for vertexA in vEdgeSet:
			edgeSet = {}
			for vertexB in pGraph.graph2.vDict:
				for adjVert in forest.vDict[cantorMap(vertexA, vertexB)]:
					x, y = invCantor(adjVert)
					if x == vertexA:
						edgeSet[vertexB] = y
			tEdgeSet = frozenset(edgeSet.items())
			if tEdgeSet in vEdgeSet[vertexA]:
				vEdgeSet[vertexA][tEdgeSet] += 1
			else:
				vEdgeSet[vertexA][tEdgeSet] = 1
	return vEdgeSet

def testVertIndependence(pGraph):
	forestSet = [[x, False] for x in getSpanningForests(pGraph.product)]
	print(len(forestSet))
	for candForest in forestSet:
		if candForest[1] == False:
			if not testIndivVertIndependence(pGraph, candForest[0], forestSet):
				return False
	return True

def testIndivVertIndependence(pGraph, forest, forestSet):
	hori, diag, vertSet = getGProjection(pGraph, forest)
	forests = getGSpanningForests(pGraph, hori, diag, vertSet, forestSet)
	vEdgeSet = getVertEdgeSet(pGraph, forests, vertSet)
	count = 0
	if len(vEdgeSet) != 0:
		iterList = []
		for vert in vEdgeSet:
			iterList.append(Iterator(iter(vEdgeSet[vert])))
		for it in iterList:
			next(it)
		tupleList = returnTuples(iterList, 0, {}, [], vEdgeSet)
		countList = copy.copy(tupleList)
		for item in countList:
			countList[item] = 0
		for forest in forests:
			edgeList = []
			for vertexA in vEdgeSet:
				edgeSet = {}
				for vertexB in pGraph.graph2.vDict:
					for adjVert in forest.vDict[cantorMap(vertexA, vertexB)]:
						x, y = invCantor(adjVert)
						if x == vertexA:
							edgeSet[vertexB] = y
				edgeList.append(frozenset(edgeSet.items()))
			countList[tuple(edgeList)] += 1
		for item in countList:
			for i in range(len(vEdgeSet) - 1):
				countList[item] *= len(forests)
		if tupleList != countList:
			print(forest.vDict)
			print(getGProjection(pGraph, forest))
			print(countList)
			print(vEdgeSet)
			count += 1
	if count != 0:
		print(count)
		return False
	return True

def returnTuples(iterList, index, tupleList, currList, vSet):
	if index == len(iterList):
		prod = 1
		for i, it in enumerate(iterList):
			prod *= vSet[list(vSet.keys())[i]][it.current]
		tupleList[tuple(currList)] = prod
		return
	while True:
		copyList = copy.copy(currList)
		copyList.append(iterList[index].current)
		returnTuples(iterList, index + 1, tupleList, copyList, vSet)
		next(iterList[index])
		if iterList[index].current == None:
			iterList[index] = Iterator(iter(vSet[list(vSet.keys())[index]]))
			next(iterList[index])
			break
	return tupleList
