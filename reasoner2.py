from py4j.java_gateway import JavaGateway
import re

# connect to the java gateway of dl4python
gateway = JavaGateway()

# get a parser from OWL files to DL ontologies
parser = gateway.getOWLParser()

# get a formatter to print in nice DL format
formatter = gateway.getSimpleDLFormatter()

print("Loading the ontology...")

# load an ontology from a file
ontology = parser.parseFile("KR1_POKE.rdf")

print("Loaded the ontology!")

# IMPORTANT: the algorithm from the lecture assumes conjunctions to always be over two concepts
# Ontologies in OWL can hopwever have conjunctions over an arbitrary number of concpets.
# The following command changes all conjunctions so that they have at most two conjuncts
print("Converting to binary conjunctions")
gateway.convertToBinaryConjunctions(ontology)

tbox = ontology.tbox()
axioms = tbox.getAxioms()
allConcepts = ontology.getSubConcepts()
conceptNames = ontology.getConceptNames()
elFactory = gateway.getELFactory()
#print([formatter.format(x) for x in allConcepts])
subsumers={}
Subsumers ={}
Nodes = {}
current_node = 0
def find_key(dictionary, target_value):
    for key, value in dictionary.items():
        if value == target_value:
            return key

for axiom in axioms: 
    axiomType = axiom.getClass().getSimpleName() 
    #initial element d0
    if  axiomType == "GeneralConceptInclusion":
        current_element = axiom 
        left = axiom.lhs()
        right = axiom.rhs()
        child = formatter.format(axiom.lhs())
        parent = formatter.format(axiom.rhs())
        if not Nodes:
            Nodes[current_node] = child
            print(Nodes[current_node])
            if child not in Subsumers:
                Subsumers[child] = None
        
        if child in Nodes:
            current_node = find_key(Nodes, child)



        if left.getClass().getSimpleName() == "ConceptConjunction":
            if child not in Nodes[current_node]:
                Nodes[current_node].append(child)
            for conjunct in left.getConjuncts():
                if formatter.format(conjunct) not in Nodes[current_node]:
                    Nodes[current_node].append(formatter.format(conjunct))
        if left.getClass().getSimpleName() == "ExistentialRoleRestriction":
            element = formatter.format(left.role()),'.',formatter.format(left.filler()) 
            if element not in Nodes[current_node]:
                Nodes[current_node].append(element)
                if formatter.format(left.filler()) not in Nodes:
                    Nodes[formatter.format(left.role)]= None
                    Nodes[current_node +1] = formatter.format(left.filler())
        if right.getClass().getSimpleName() == "ConceptConjunction":
            if child not in Nodes[current_node]:
                Nodes[current_node].append(parent)
            for conjunct in right.getConjuncts():
                if formatter.format(conjunct) not in Nodes[current_node]:
                    Nodes[current_node].append(formatter.format(conjunct))
        if left.getClass().getSimpleName() == "ExistentialRoleRestriction":
            element = formatter.format(right.role()),'.',formatter.format(right.filler()) 
            if element not in Nodes[current_node]:
                Nodes[current_node].append(element)
                if formatter.format(right.filler()) not in Nodes:
                    Nodes[formatter.format(right.role)]= None
                    Nodes[current_node +1] = formatter.format(right.filler())
        #elif parent not in Nodes[current_node]:
           # Nodes[current_node].append(parent)
        
        elif parent not in Nodes[current_node]:
            if current_node not in Nodes:
                Nodes[current_node] = [parent]
            else:
                Nodes[current_node].append(parent)



 
        
                




        




'''for axiom in axioms:
    axiomType = axiom.getClass().getSimpleName() 
    conceptType = axiom.getClass().getSimpleName()

    if axiomType == "GeneralConceptInclusion": 
        left = axiom.lhs() 
        right =  axiom.rhs()
        child = formatter.format(axiom.lhs())
        parent = formatter.format(axiom.rhs())
        i=0
        #initial element
        #if left not in Nodes and left.getClass().getSimpleName() == "ConceptName":
         #   Nodes[i] = [child]

        if left.getClass().getSimpleName() == "ConceptName" and right.getClass().getSimpleName() == "ConceptName":
           # if parent not in Nodes[i]:
               # Nodes[i].append(parent)
                
            if child in subsumers and parent not in subsumers[child]:
                    subsumers[child].append(parent)
            else:
                    subsumers[child] = [parent]
        elif right.getClass().getSimpleName() == "ConceptConjunction":
            for conjunct in right.getConjuncts():
                if child in subsumers:
                    print("-",formatter.format(conjunct))
                    subsumers[child].append(formatter.format(conjunct))
                else:
                    subsumers[child] = [formatter.format(conjunct)]
print(subsumers)'''
        

      
            
           


