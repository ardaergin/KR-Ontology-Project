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

Subsumers ={}
Nodes = {}

current_node = 0
def find_key(dictionary, target_value):
    for key, value in dictionary.items():
        if value == target_value:
            return key
#for finding the existantial role relations
def check_values(dictionary, target_substring,filler):

    matching_keys = []

    for key, values in dictionary.items():
        for value in values:
            #if target role relation in value
            if target_substring in value:
                # Extract the substring that follows the target substring
                index_of_target = value.find(target_substring)
                #find concept Name attached to role relation
                substring_after_target = value[index_of_target + len(target_substring):]

                # Check if the concept Name after the role is a value for any key
                for other_key, other_values in dictionary.items():
                    if substring_after_target in other_values and filler in dictionary.get(other_key, []):
                        matching_keys.append(key)


        return matching_keys
#completion algorithm
def completion_alg(left,right, current_node):
    child = formatter.format(axiom.lhs())
    parent = formatter.format(axiom.rhs())
#entailment rule
    if left.getClass().getSimpleName() == "ConceptName" and not left.getClass().getSimpleName() == "ExistentialRoleRestriction" and not left.getClass().getSimpleName() == "ConceptConjunction" and not '∀' in child:
            if right.getClass().getSimpleName() == "ConceptName" and not right.getClass().getSimpleName() == "ExistentialRoleRestriction" and not right.getClass().getSimpleName() == "ConceptConjunction" and not '∀' in parent:
                if current_node not in Nodes:
                    Nodes[current_node] = []  # Initialize the value as an empty list or another appropriate default value
                if child not in Nodes[current_node]:
                    Nodes[current_node].append(child)
                if parent not in Nodes[current_node]:
                    Nodes[current_node].append(parent)
                if child in Subsumers:
                    if parent not in Subsumers[child]: 
                        Subsumers[child].append(parent)
                else: 
                    Subsumers[child] = [parent]
#Conjunctionrules for left and right
    if left.getClass().getSimpleName() == "ConceptConjunction":
        if not left.getClass().getSimpleName() == "ExistentialRoleRestriction" and not '∀' in child:
            if current_node not in Nodes:
                    Nodes[current_node] = [] 
            if child not in Nodes[current_node]:
                Nodes[current_node].append(child)
            for conjunct in left.getConjuncts():
                if formatter.format(conjunct) not in Nodes[current_node]:
                    Nodes[current_node].append(formatter.format(conjunct))
    if right.getClass().getSimpleName() == "ConceptConjunction":
        if not right.getClass().getSimpleName() == "ExistentialRoleRestriction" and not '∀' in parent:
            if current_node not in Nodes:
                    Nodes[current_node] = [] 
            if parent not in Nodes[current_node]:
                Nodes[current_node].append(parent)
            for conjunct in right.getConjuncts():
                if formatter.format(conjunct) not in Nodes[current_node]:
                    Nodes[current_node].append(formatter.format(conjunct))
                if child in Subsumers:
                    if formatter.format(conjunct) not in Subsumers[child]: 
                        Subsumers[child].append(formatter.format(conjunct))
                else: 
                    Subsumers[child] = [formatter.format(conjunct)]
#existential rule
    if left.getClass().getSimpleName() == "ExistentialRoleRestriction":
            element = formatter.format(left.role()),'.',formatter.format(left.filler()) 
            if element not in Nodes[current_node]:
                Nodes[current_node].append(element)
                if formatter.format(left.filler()) not in Nodes[any]:
                    Nodes[current_node +1] = formatter.format(left.filler())
                if formatter.format(left.filler()) not in Subsumers:
                     Subsumers[formatter.format(left.filler())] = []
                    ##  other existential rule missing
    if right.getClass().getSimpleName() == "ExistentialRoleRestriction":
            element = formatter.format(right.role()),'.',formatter.format(right.filler()) 
            #if there is already a Node that has same role, check if the connected filler is 
            # saved in a key that already contains the filler from current element in questions hahaha

            #role relation
            target_substring = (formatter.format(right.role())+".")
            #conceptname connected to role relation
            filler =formatter.format(right.filler())
            result = check_values(Nodes, target_substring, filler)
            if result:
                Nodes[result].append(element)  

            elif element not in Nodes.get(current_node, []):
                Nodes.setdefault(current_node, []).append(element)
                foundkey = True
                for key, values in Nodes.items():
                    for value in values:
                        if not value == filler:
                            if (current_node+1) not in Nodes:
                                foundkey = False
                                break
                if not foundkey:
                    Nodes[(current_node+1)] = [] 
                    Nodes[(current_node+1)].append(filler)
                            
               
    

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
            completion_alg(left,right, current_node)
        if Nodes: 
            if child in Nodes:
                current_node = find_key(Nodes, child)
                completion_alg(left,right,current_node)
            elif child not in Nodes: 
                current_node = current_node +1
                completion_alg(left,right,current_node)
                

print(Nodes)
 
