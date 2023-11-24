from py4j.java_gateway import JavaGateway
import sys
import os
import time
from itertools import chain


def find_key(dictionary, target_value):
    for key, value in dictionary.items():
        if value == target_value:
            return key
#for finding the existantial role relations
def check_values(dictionary, target_substring, filler):
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


def entailment_rule(current_node, child, parent):
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


def conjunction_rule(current_node, element, side):
    if current_node not in Nodes:
        Nodes[current_node] = []
    if element not in Nodes[current_node]:
        Nodes[current_node].append(element)

    for conjunct in side.getConjuncts():
        # print(f'conjuncts: {formatter.format(conjunct)} {conjunct.getClass().getSimpleName()}')

        if formatter.format(conjunct) not in Nodes[current_node]:
            Nodes[current_node].append(formatter.format(conjunct))

            # Example: (∃hasTopping.SpicyTopping ⊔ ∃hasSauce.SpicySauce)
            if conjunct.getClass().getSimpleName() == "ConceptDisjunction":

                pass # TODO: conceptdisjunctions are not handled properly yet

            # Example: conjuncts: ¬∃hasProtein.Landmeat
            if conjunct.getClass().getSimpleName() == "ConceptComplement":
                pass # TODO: Do we have to do something with this?

            if conjunct.getClass().getSimpleName() == "MaxNumberRestriction":
                pass # TODO: Do we have to do something with this?
            if conjunct.getClass().getSimpleName() == "ExistentialRoleRestriction" and not conjunct.getClass().getSimpleName() == "ConceptConjunction":
                existential_rule(formatter.format(conjunct), conjunct.role(), conjunct.filler(), current_node)
           # elif conjunct.filler().getClass().getSimpleName() == "ConceptConjunction":
                #conjunction_rule_right(current_node, child, formatter.format(conjunct.filler()))


        if child in Subsumers:
            if formatter.format(conjunct) not in Subsumers[child]:
                Subsumers[child].append(formatter.format(conjunct))
        else:
            Subsumers[child] = [formatter.format(conjunct)]
        


def existential_rule(element,Role,Filler, current_node):
    # Role relation
    target_substring = (formatter.format(Role) + ".")
    # Concept name connected to role relation
    filler = formatter.format(Filler)
    result = check_values(Nodes, target_substring, filler)

    if result:
        Nodes[result].append(element)

    elif element not in Nodes.get(current_node, []):
        Nodes.setdefault(current_node, []).append(element)

        # I don't understand what is happening here
        foundkey = True
        for key, values in Nodes.items():
            for value in values:
                if not value == filler:
                    if (current_node + 1) not in Nodes:
                        foundkey = False
                        break
        if not foundkey:
            Nodes[(current_node + 1)] = []
            Nodes[(current_node + 1)].append(filler)

#completion algorithm
def completion_alg(left, right, current_node, child, parent):
    # child = formatter.format(axiom.lhs())
    # parent = formatter.format(axiom.rhs())

    # Entailment rule
    if left.getClass().getSimpleName() == "ConceptName" and not left.getClass().getSimpleName() == "ExistentialRoleRestriction" and not left.getClass().getSimpleName() == "ConceptConjunction" and not '∀' in child:
        if right.getClass().getSimpleName() == "ConceptName" and not right.getClass().getSimpleName() == "ExistentialRoleRestriction" and not right.getClass().getSimpleName() == "ConceptConjunction" and not '∀' in parent:
            entailment_rule(current_node, child, parent) # Call entailment function

    # Conjunction rules for left and right
    if left.getClass().getSimpleName() == "ConceptConjunction":
        if not left.getClass().getSimpleName() == "ExistentialRoleRestriction" and not '∀' in child:

            conjunction_rule(current_node, child, left) # call conjunction function for left

    # Example: TeriyakiSauce <= (VegetarianSauce n VeganSauce)
    if right.getClass().getSimpleName() == "ConceptConjunction":
        if not right.getClass().getSimpleName() == "ExistentialRoleRestriction" and not '∀' in parent:
            conjunction_rule(current_node, parent, right)

    # Existential rule
    if left.getClass().getSimpleName() == "ExistentialRoleRestriction":
        # print(f'test: {formatter.format(left)}')
        element = formatter.format(left.role()),'.',formatter.format(left.filler())
        print(element)
        existential_rule(element, left.role(),left.filler(), current_node) # Call function existential rule
        if left.filler().getClass().getSimpleName() == "ConceptConjunction":
            conjunction_rule(current_node,formatter.format(left.filler()),left.filler())

    # TODO: Add other existential rule

    if right.getClass().getSimpleName() == "ExistentialRoleRestriction":
        # print(formatter.format(axiom))
        element = formatter.format(right.role()),'.',formatter.format(right.filler())
        # If there is already a Node that has same role, check if the connected filler is
        # saved in a key that already contains the filler from current element in questions hahaha
        existential_rule(element, right.role(),right.filler(), current_node)
        if right.filler().getClass().getSimpleName() == "ConceptConjunction":
            conjunction_rule(current_node,formatter.format(right.filler()),right.filler())
       

def equivalence_axiom(axiom, Nodes, current_node):
    pass # TODO: I want to move the equivalence code in the main loop here, but doesn't work yet somehow

def complete_subsumers(subsumers):
    # Create a copy to modify
    SubsumersComplete =  Subsumers.copy()

    for key, value_list in subsumers.items():
        # Ensure the current value is a list
        if not isinstance(value_list, list):
            value_list = [value_list]

        for value in value_list:
            if value in subsumers:
                # If the value is also a key, extend its list to the current key's list
                additional_values = subsumers[value]
                if isinstance(additional_values, list):
                    SubsumersComplete[key] = list(chain(SubsumersComplete[key], additional_values))
                    #SubsumersComplete[key].extend(additional_values)
                else:
                    SubsumersComplete[key].append(additional_values)

        # Remove duplicates by converting to a set and back to a list
        SubsumersComplete[key] = list(set(SubsumersComplete[key]))

    # Append key and 'TOP' to all list items
    for key in SubsumersComplete.keys():
        SubsumersComplete[key].append(key)
        SubsumersComplete[key].append('TOP')

    # Update the original dictionary
    subsumers = SubsumersComplete

    return(subsumers)

if __name__ == "__main__":

    
    if len(sys.argv) < 3:
        print("Usage: python reasoner.py ONTOLOGY_FILE CLASS_NAME")
        sys.exit(1)

    ontology_file = sys.argv[1]
    class_name = sys.argv[2]

    if os.path.exists(ontology_file) == False:
        print("ERROR: ONTOLOGY_FILE cannot be found.")
        sys.exit(1)

    gateway = JavaGateway() # connect to the java gateway of dl4python
    parser = gateway.getOWLParser() # get a parser from OWL files to DL ontologies
    formatter = gateway.getSimpleDLFormatter() # get a formatter to print in nice DL format

    # print("Loading the ontology...")
    ontology = parser.parseFile(ontology_file)     # load an ontology from a file
    
    gateway.convertToBinaryConjunctions(ontology)

    tbox = ontology.tbox()
    axioms = tbox.getAxioms()
    allConcepts = ontology.getSubConcepts()
    conceptNames = ontology.getConceptNames()
    elFactory = gateway.getELFactory()

    Subsumers = {}
    Nodes = {}

    current_node = 0
     # Start the timer
    start_time = time.time()
    for axiom in axioms:
        axiomType = axiom.getClass().getSimpleName()
        if axiomType == "GeneralConceptInclusion":

            current_element = axiom
            left = axiom.lhs()
            right = axiom.rhs()
            child = formatter.format(axiom.lhs())
            parent = formatter.format(axiom.rhs())
            # print(f'Axiom: {formatter.format(axiom)}')

            if not Nodes: # Add first key-value pair to dictionary
                completion_alg(left, right, current_node, child, parent)

            if Nodes:
                if child in Nodes:
                    current_node = find_key(Nodes, child)
                    completion_alg(left, right, current_node, child, parent)

                elif child not in Nodes:
                    current_node = current_node + 1
                    completion_alg(left, right, current_node, child, parent)

        elif axiomType == "DisjointnessAxiom":
            # print(formatter.format(axiom))
            pass # TODO:

        elif axiomType == "DomainAxiom":
            pass # TODO:

        # Example: NonSpicyPoke ≡ (¬SpicyPoke ⊓ PokeBowl)
        elif axiomType == "EquivalenceAxiom":
            # print(f'Axiom: {formatter.format(axiom)}')
            element_left, element_right = axiom.getConcepts()

            format_element_left = formatter.format(element_left)
            format_element_right = formatter.format(element_right)

            # NonSpicyPoke ≡ (¬SpicyPoke ⊓ PokeBowl), This is the same as:
            # NonSpicyPoke <= (¬SpicyPoke ⊓ PokeBowl) and (¬SpicyPoke ⊓ PokeBowl) <= NonSpicyPoke
            if Nodes:
                # Handels both directions of the equivalence
                for left, right in [(element_left, element_right), (element_right, element_left)]:
                    formatted_child = formatter.format(left)
                    formatted_parent = formatter.format(right)
                    # print(f'left = {formatted_child} {left.getClass().getSimpleName()}')
                    # print(f'right = {formatted_parent} {right.getClass().getSimpleName()}')

                    current_node = find_key(Nodes, formatted_child) if left in Nodes else current_node + 1
                    completion_alg(left, right, current_node, formatted_child, formatted_parent)

        elif axiomType == "RangeAxiom":
            pass # TODO:
    print('help')
    Subsumers = complete_subsumers(Subsumers)
    end_time = time.time()
    # Calculate elapsed time
    elapsed_time = end_time - start_time

    # Comparison against the hermit reasoner
    start_time1 = time.time()
    hermit = gateway.getHermiTReasoner() # might the upper case T!
    class_ = elFactory.getConceptName(class_name)
    hermit.setOntology(ontology)
    
    subsumers1 = hermit.getSubsumers(class_)
    end_time1 = time.time()
    # Calculate elapsed time
    elapsed_time1 = end_time1 - start_time1

    print("Hermit finds", len(subsumers1), "Subsumers for ", class_)
    print(f"Reasoning time for Hermit: {elapsed_time1} seconds")

    print("Subsumers according to hermit: ")
    print(subsumers1.toString())
    for concept in subsumers1:
        print(" - ",formatter.format(concept))
    print()
#ELK reasoner
    start_time2 = time.time()
    elk = gateway.getELKReasoner() # might the upper case T!
    class_ = elFactory.getConceptName(class_name)
    elk.setOntology(ontology)
    
    subsumers2 = elk.getSubsumers(class_)
    end_time2 = time.time()
    # Calculate elapsed time
    elapsed_time2 = end_time2 - start_time2

    print("ELK finds", len(subsumers2), "Subsumers for ", class_)
    print(f"Reasoning time for ELK: {elapsed_time1} seconds")

    print("Subsumers according to ELK: ")
    print(subsumers2.toString())
    for concept in subsumers2:
        print(" - ",formatter.format(concept))
    print()
    #print(Subsumers)
    # THIS IS THE CORRECT OUTPUT! ALL OTHER PRINTS SHOULD BE DELETED
    if class_name not in Subsumers:
        print('ERROR: The given classname is not found to be a class in the current ontology.')
        sys.exit(1)
    else:
        print("Our reasoner finds", len(Subsumers[class_name]), "Subsumers for ", class_name)
        print(f"Reasoning time for our Reasoner: {elapsed_time} seconds")
        for concept in Subsumers[class_name]:
            print(concept)

