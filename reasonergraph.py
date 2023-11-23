from py4j.java_gateway import JavaGateway
import sys
import os
import time


import networkx as nx

class OntologyGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.concepts = set()

    def add_concept(self, concept):
        self.graph.add_node(concept)

    def add_subclass_relation(self, subclass, superclass):
        self.graph.add_edge(subclass, superclass)

    def add_role_relation(self, source, target, role):
        if not self.graph.has_edge(source, target):
            self.graph.add_edge(source, target, roles=set())
        self.graph[source][target]['roles'].add(role)

    def get_subsumers(self, concept):
        return nx.descendants(self.graph.reverse(), concept)
    def concept_exists(self, concept):
        return concept in self.concepts
    def is_subclass(self, subclass, superclass):
        if subclass not in self.concepts or superclass not in self.concepts:
            return False
        return nx.has_path(self.graph, subclass, superclass)

def entailment_rule(child, parent):
    if not Ontology.concept_exists(child):
        Ontology.add_concept(child)
    if not Ontology.is_subclass(child, parent):
        Ontology.add_subclass_relation(child,parent)
def conjunction_rule(child,parent, side):#check if you need to create for case: both sides are conjunction
    if side == left:
        for conjunct in side.getConjuncts():
            if conjunct.getClass().getSimpleName() == "ExistentialRoleRestriction":
                existential_rule(formatter.format(conjunct), conjunct.role(), conjunct.filler(),left)
            else:
                if not Ontology.concept_exists(formatter.format(conjunct)):
                    Ontology.add_concept(formatter.format(conjunct))
                if not Ontology.is_subclass(formatter.format(conjunct), parent):
                    Ontology.add_subclass_relation(formatter.format(conjunct),parent)
    if side == right:
        for conjunct in side.getConjuncts():
            if conjunct.getClass().getSimpleName() == "ExistentialRoleRestriction":
                existential_rule(formatter.format(conjunct), conjunct.role(), conjunct.filler(),right)
            else:
                if not Ontology.concept_exists(formatter.format(conjunct)):
                    Ontology.add_concept(formatter.format(conjunct))
                if not Ontology.is_subclass(child, formatter.format(conjunct)):
                    Ontology.add_subclass_relation(child,formatter.format(conjunct))

def existential_rule(element,Role,Filler,side):
    if side == left:
        Ontology.add_role_relation(parent, formatter.format(Filler), formatter.format(Role))
    if side == right:
        Ontology.add_role_relation(child, formatter.format(Filler), formatter.format(Role))
        

Ontology = OntologyGraph()
def completion_alg(left, right,child, parent):
    if left.getClass().getSimpleName() == "ConceptName" and not left.getClass().getSimpleName() == "ExistentialRoleRestriction" and not left.getClass().getSimpleName() == "ConceptConjunction" and not '∀' in child:
        if right.getClass().getSimpleName() == "ConceptName" and not right.getClass().getSimpleName() == "ExistentialRoleRestriction" and not right.getClass().getSimpleName() == "ConceptConjunction" and not '∀' in parent:
            entailment_rule(child, parent) # Call entailment function

    # Conjunction rules for left and right
    if left.getClass().getSimpleName() == "ConceptConjunction":
        if not left.getClass().getSimpleName() == "ExistentialRoleRestriction" and not '∀' in child:
            conjunction_rule(child,parent, left) # call conjunction function for left

    # Example: TeriyakiSauce <= (VegetarianSauce n VeganSauce)
    if right.getClass().getSimpleName() == "ConceptConjunction":
        if not right.getClass().getSimpleName() == "ExistentialRoleRestriction" and not '∀' in parent:
            conjunction_rule(child,parent,right)

    # Existential rule
    if left.getClass().getSimpleName() == "ExistentialRoleRestriction":
        # print(f'test: {formatter.format(left)}')
        element = formatter.format(left.role()),'.',formatter.format(left.filler())
        print(element)
        existential_rule(element, left.role(),left.filler(),left) # Call function existential rule
        if left.filler().getClass().getSimpleName() == "ConceptConjunction":
            conjunction_rule(formatter.format(left.filler()),parent,left)

    if right.getClass().getSimpleName() == "ExistentialRoleRestriction":
        # print(formatter.format(axiom))
        element = formatter.format(right.role()),'.',formatter.format(right.filler())
        existential_rule(element, right.role(),right.filler(),right)
        if right.filler().getClass().getSimpleName() == "ConceptConjunction":
            conjunction_rule(formatter.format(child,right.filler()),right)
       
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python reasoner.py ONTOLOGY_FILE CLASS_NAME")
        sys.exit(1)

    ontology_file = sys.argv[1]
    class_name = sys.argv[2]

    # Start the timer
    start_time = time.time()

    if os.path.exists(ontology_file) == False:
        print("ERROR: ONTOLOGY_FILE cannot be found.")
        sys.exit(1)

    gateway = JavaGateway() # connect to the java gateway of dl4python
    parser = gateway.getOWLParser() # get a parser from OWL files to DL ontologies
    formatter = gateway.getSimpleDLFormatter() # get a formatter to print in nice DL format

    ontology = parser.parseFile(ontology_file)     # load an ontology from a file
    gateway.convertToBinaryConjunctions(ontology)

    tbox = ontology.tbox()
    axioms = tbox.getAxioms()
    allConcepts = ontology.getSubConcepts()
    conceptNames = ontology.getConceptNames()
    elFactory = gateway.getELFactory()

    for axiom in axioms:
        axiomType = axiom.getClass().getSimpleName()
        if axiomType == "GeneralConceptInclusion":
            left = axiom.lhs()
            right = axiom.rhs()
            child = formatter.format(axiom.lhs())
            parent = formatter.format(axiom.rhs())

            completion_alg(left, right, child, parent)

        elif axiomType == "EquivalenceAxiom":
            element_left, element_right = axiom.getConcepts()

            format_element_left = formatter.format(element_left)
            format_element_right = formatter.format(element_right)

                # Handels both directions of the equivalence
            for left, right in [(element_left, element_right), (element_right, element_left)]:
                formatted_child = formatter.format(left)
                formatted_parent = formatter.format(right)

                completion_alg(left, right, formatted_child, formatted_parent)

    end_time = time.time()
    # Calculate elapsed time
    elapsed_time = end_time - start_time

    # Comparison against the hermit reasoner
    start_time1 = time.time()
    hermit = gateway.getHermiTReasoner() # might the upper case T!
    class_ = elFactory.getConceptName(class_name)
    hermit.setOntology(ontology)
    
    subsumers = hermit.getSubsumers(class_)
    end_time1 = time.time()
    # Calculate elapsed time
    elapsed_time1 = end_time1 - start_time1

    print("Hermit finds", len(subsumers), "Subsumers for ", class_)
    print(f"Reasoning time for Hermit: {elapsed_time1} seconds")

    print("Subsumers according to hermit: ")
    print(subsumers.toString())
    for concept in subsumers:
        print(" - ",formatter.format(concept))
    print()

    # THIS IS THE CORRECT OUTPUT! ALL OTHER PRINTS SHOULD BE DELETED
    subsumers = Ontology.get_subsumers(class_name)
    if class_name not in subsumers:
        print('ERROR: The given classname is not found to be a class in the current ontology.')
        sys.exit(1)
    else:
        print("Our reasoner finds", len(subsumers[class_name]), "Subsumers for ", class_name)
        print(f"Reasoning time for our Reasoner: {elapsed_time} seconds")
        for concept in subsumers:
            print(concept)

