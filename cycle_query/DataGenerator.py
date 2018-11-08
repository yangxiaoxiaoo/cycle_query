#!/usr/bin/env python

# Each tuple appears in only one relation
# Every relation is binary

import cPickle as pickle
import sys
import random
import numpy as np

# The maximum weight of a tuple (hardcoded)
weightrange = 100


def parse_args():
    ## -- Read input
    import argparse
    parser = argparse.ArgumentParser(description='Data Generator for Cyclic/Path Join Queries')

    parser.add_argument('-o', action="store", dest="outFile", default="out", help="Path of output file")
    parser.add_argument('-q', action="store", dest="queryType", choices={"Path", "Cycle"}, default="Path", help="Query Type: Can be either \"Path\" or \"Cycle\"")
    parser.add_argument('-n', action="store", dest="n", default=5, type=int, help="Maximum cardinality of relations")
    parser.add_argument('-l', action="store", dest="length", default=4, type=int, help="Length of Path or Cycle")
    parser.add_argument('-d', action="store", dest="DensityOfEdges", choices={"Full", "Random"}, default="Full", help="\"Full\"=Maximum possible cardinality for relations|\"Random\"=Random cardinality for each relation")
    parser.add_argument('-ed', action="store", dest="edgeDistribution", choices={"HardCase", "Random"}, default="Random", help="\"HardCase\"=Fanout:1->max->1->...|\"Random\"=Edges are distributed randomly")
    parser.add_argument('-u', action="store", dest="unionOfDatabases", default=1, type=int, help="By setting this option, the result will be the union of that many sub-databases (Useful for the Hard Case where it will alternate the fanout across databases)")
    parser.add_argument('--v', action="store_true", dest='verbose', default=False, help="Print attributes and Relations to STDIN")

    arg_results = parser.parse_args()
    outFile = arg_results.outFile
    queryType = arg_results.queryType
    n = arg_results.n
    length = arg_results.length
    DensityOfEdges = arg_results.DensityOfEdges
    edgeDistribution = arg_results.edgeDistribution
    databasesNo = arg_results.unionOfDatabases
    verbose = arg_results.verbose

    return outFile, queryType, n, length, DensityOfEdges, edgeDistribution, databasesNo, verbose

## -- For printing
def printAttributes(attributeList):
    from prettytable import PrettyTable
    pretty = PrettyTable()
    ## First find max column length
    maxl = 0
    for attribute in attributeList:
        if len(attribute) > maxl: maxl = len(attribute)
    for i in range (len(attributeList)):
        attributeName = "A" + str(i)
        attribute = attributeList[i]
        col = []
        for (val, edgeCount) in attribute:
            col.append(str(val) + " (" + str(edgeCount) + " edges)")
        while (len(col) < maxl): col.append("")
        pretty.add_column(attributeName, col)
    print pretty

## -- For printing
def printRelations(relation2tuple):
    from prettytable import PrettyTable
    pretty = PrettyTable()
    ## First find max column length
    maxl = 0
    for relation in relation2tuple.keys():
        tupleSet = relation2tuple[relation]
        if len(tupleSet) > maxl: maxl = len(tupleSet)
    for relation in relation2tuple.keys():
        tupleSet = relation2tuple[relation]
        tupleList = list(tupleSet)
        sorted_tupleList = sorted(tupleList)
        while (len(sorted_tupleList) < maxl): sorted_tupleList.append("")
        pretty.add_column(relation, sorted_tupleList)
    print pretty

##-- When used from the command line, save the output to a pickle file
def save_to_file(outFile, relation2tuple, tuple2weight):
    # -- Output dictionaries
    outFile1 = open(outFile + "_tuples.pkl", "wb")
    pickle.dump(relation2tuple, outFile1)
    outFile1.close()

    outFile2 = open(outFile + "_weights.pkl", "wb")
    pickle.dump(tuple2weight, outFile2)
    outFile2.close()

##-- Main class
class MainGenerator:
    def __init__(self, queryType, n, length, DensityOfEdges, edgeDistribution, databasesNo, verbose = False):
        self.queryType = queryType
        self.n = n
        self.length = length
        self.DensityOfEdges = DensityOfEdges
        self.edgeDistribution = edgeDistribution
        self.databasesNo = databasesNo
        self.verbose = verbose
        ## -- Initialize
        self.value_counter = 0   ## Used for counting, we dont want to repeat a value
        self.relation2tuple = dict() # Hold the relations
        for i in range(length): self.relation2tuple["R" + str(i)] = set()    # Initialize relations
        self.tuple2weight = dict()   ## Holds the weights of tuples
        self.edgesForEachDatabase = [n / databasesNo] * databasesNo
        self.edgesForEachDatabase[0] += n % databasesNo
        if verbose:
            self.attributeList = []
            attribute_no = length if queryType == "Cycle" else length + 1
            for i in range(attribute_no):
                self.attributeList.append([])

    ## -- A function that determines the number of edges for a given relation and a given database
    def getNumberOfEdges(self, database):
        if self.DensityOfEdges == "Full":
            return self.edgesForEachDatabase[database]
        elif self.DensityOfEdges == "Random":
            return random.randint(1, self.edgesForEachDatabase[database])

    ## -- This function distributes the available edges of a current attribute to elements of the next attribute
    ## -- The number of elements of the next attribute is then decided by this distribution
    ## -- Given previous edges, we might want a number of different elements as a minimum
    ## -- Returns a list of edges, e.g., [30,5,10] -> a1 with 30 outgoing edges, a2 with 5, a3 with 10
    def getDistributionOfEdges(self, available, atLeastDifferent):
        if (self.edgeDistribution == "Random"):
            ## Initialize the result with atLeastDifferent "1" which are substracted from the total available
            result = []
            for i in range(atLeastDifferent):
                result.append(1)
            available -= atLeastDifferent
            ## Iteratively choose randomly from the available edges
            iterations = 0
            while (available > 0):
                chosen = random.randint(1, available)
                if (iterations < atLeastDifferent):
                    result[iterations] += chosen
                else:
                    result.append(chosen)
                available -= chosen
                iterations += 1
            return result
        elif (self.edgeDistribution == "HardCase"):
            ## atLeastDifferent will either be 1 or n, indicating the fanout
            ## if it is 1, it means that we structly want just one element
            if (atLeastDifferent == 1):
                result = [available]
            else:
                result = [1] * available
            return result

    ## -- Returns an attribute as a list of (value, edgeCount) tuples, where edgeCount denotes how many outgoing(towards right) edges this value will have towards the next attribute
    ## -- Given a previous attribute and its edges, it may have to contain a number of elements as a minimum
    def buildAttribute(self, i, database, atLeastElements):
        res = []
        cardinality = self.getNumberOfEdges(database)
        edgesDistribution = self.getDistributionOfEdges(cardinality, atLeastElements)
        for edgeCount in edgesDistribution:
            val = self.value_counter
            self.value_counter += 1
            res.append((val, edgeCount))
        if self.verbose: self.attributeList[i] += res
        return res

    ## -- For future
    def assignWeight(self, (val1, val2)):
        return random.uniform(0, weightrange)

    ## -- Takes as input a left attribute containing a distribution of edges among its elements and a right attribute containing the possible destinations
    ## -- Outputs a list of tuples, which correspond to the relation that contains those two attributes
    def buildRelation(self, aLeft, aRight):
        res = []
        for (val1, edgeCount) in aLeft:
            ## val1 of aLeft has edgeCount edges towards aRight
            ## if aRight does not have enough elements, restrict the edgeCount (useful for the last relation in a cycle)
            if len(aRight) < edgeCount: edgeCount = len(aRight)
            ## Choose random values from aRight for the outgoing edges
            val2_list = [x[0] for x in aRight]
            chosen_val2 = np.random.choice(val2_list, replace=False, size=edgeCount)
            for j in range(edgeCount):
                val2 = chosen_val2[j]
                res.append((val1, val2))
        return res

    ## -- Given a list of tuples of Ri, it adds them to our database
    ## -- It also assigns them a weight
    def addTuplesToRelation(self, tuples, i):
        for (val1, val2) in tuples:
            self.relation2tuple["R" + str(i)].add((val1, val2))
            ## Assign weight to this tuple
            self.tuple2weight[(val1, val2)] = self.assignWeight((val1, val2))

    ## -- After initializing an object, this function build the database and returns it as two dictionaries
    def build_database(self):
        ## -- Build each sub-database
        for k in range(self.databasesNo):
            ## -- Build attributes and relations except the last relation
            ## We need to start from somewhere
            if (self.edgeDistribution == "Random"): min_values_of_Attibute0 = 0
            elif (self.edgeDistribution == "HardCase"):
                ## For the hardcase, alternate the sequence for each sub-database to get a mixture of results
                if (k % 2 == 0): min_values_of_Attibute0 = self.getNumberOfEdges(k)
                else: min_values_of_Attibute0 = 1
            attribute0 = self.buildAttribute(0, k, min_values_of_Attibute0)
            ## Build the rest of the attributes and all the relations except the last one
            prev_attribute = attribute0
            for i in range(0, self.length - 1):
                # This attribute needs to have at least as many values as the maximum fanout of the previous attribute
                atLeast = max([x[1] for x in prev_attribute])
                attribute = self.buildAttribute(i + 1, k, atLeast)
                ## Now build the Relation Ri between prev_attribute and attribute
                tuples = self.buildRelation(prev_attribute, attribute)
                self.addTuplesToRelation(tuples, i)
                ## Continue to the next one
                prev_attribute = attribute
            ## -- Build the last relation
            if (self.queryType == "Cycle"):
                ## -- If cycle, we have to connect the previous attribute with the 0-one
                tuples = self.buildRelation(prev_attribute, attribute0)
                self.addTuplesToRelation(tuples, self.length-1)
            elif (self.queryType == "Path"):
                ## -- If path, just add one more attribute and connect it with the previous one
                # This attribute needs to have at least as many values as the maximum fanout of the previous attribute
                atLeast = max([x[1] for x in prev_attribute])
                attribute = self.buildAttribute(self.length, k, atLeast)
                ## Now build the Relation R(length-1) between prev_attribute and attribute
                tuples = self.buildRelation(prev_attribute, attribute)
                self.addTuplesToRelation(tuples, self.length-1)
        return self.relation2tuple, self.tuple2weight


##-- Use this function as an interface when calling from another program
##-- Instantiates an object, calls its driver function and returns the result
def getDatabase(queryType, n, length, DensityOfEdges, edgeDistribution, databasesNo):
    gen = MainGenerator(queryType, n, length, DensityOfEdges, edgeDistribution, databasesNo)
    relation2tuple, tuple2weight = gen.build_database()
    return relation2tuple, tuple2weight

if __name__ == "__main__":
    outFile, queryType, n, length, DensityOfEdges, edgeDistribution, databasesNo, verbose = parse_args()
    gen = MainGenerator(queryType, n, length, DensityOfEdges, edgeDistribution, databasesNo, verbose)
    relation2tuple, tuple2weight = gen.build_database()
    if verbose: printAttributes(gen.attributeList)
    if verbose: printRelations(relation2tuple)
    save_to_file(outFile, relation2tuple, tuple2weight)