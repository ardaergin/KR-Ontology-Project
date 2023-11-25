from py4j.java_gateway import JavaGateway
import sys
import os
import time

def find_key(dictionary, target_value):
    for key, value in dictionary.items():
        if value == target_value:
            return key

# For finding the existantial role relations
def check_values(dictionary, target_substring, filler):
    matching_keys = []

    for key, values in dictionary.items():
        for value in values:

            # If target role relation in value
            if target_substring in value:

                # Extract the substring that follows the target substring
                index_of_target = value.find(target_substring)

                # Find concept Name attached to role relation
                substring_after_target = value[index_of_target + len(target_substring):]

                # Check if the concept Name after the role is a value for any key
                for other_key, other_values in dictionary.items():
                    if substring_after_target in other_values and filler in dictionary.get(other_key, []):
                        matching_keys.append(key)
        return matching_keys

"""
- Example: HoneySoySauce <= VegetarianSauce
"""
def entailment_rule(current_node, child, parent):
    if current_node not in Nodes:
        Nodes[current_node] = []  # Initialize the value as an empty list or another appropriate default value
    if child not in Nodes[current_node]:
        if isinstance(Nodes[current_node], list):
            Nodes[current_node].append(child)
    if parent not in Nodes[current_node]:
        if isinstance(Nodes[current_node], list):
            Nodes[current_node].append(parent)
    if child in Subsumers:
        if parent not in Subsumers[child]:
            Subsumers[child].append(parent)
    else:
        Subsumers[child] = [parent]

"""
- Example: HoneySoySauce <= VegetarianSauce
"""
def conjunction_rule_left(current_node, child, parent):
    if current_node not in Nodes:
        Nodes[current_node] = []
    if child not in Nodes[current_node]:
        Nodes[current_node].append(child)
    for conjunct in left.getConjuncts():
        if formatter.format(conjunct) not in Nodes[current_node]:
            Nodes[current_node].append(formatter.format(conjunct))

"""
 Example: TeriyakiSauce <= (VegetarianSauce n VeganSauce)
"""
def conjunction_rule_right(current_node, child, parent):
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

def existential_rule_left(element, left, current_node):
    if current_node not in Nodes:
        Nodes[current_node] = []
    if element not in Nodes[current_node]:
        Nodes[current_node].append(element)
        if formatter.format(left.filler()) not in Nodes.values():
            Nodes[current_node + 1] = formatter.format(left.filler())
        if formatter.format(left.filler()) not in Subsumers:
            Subsumers[formatter.format(left.filler())] = []

"""
Example: ChickenBowl <= EhasBase.PokeBase
"""
def existential_rule_right(element, right, current_node):
    if current_node not in Nodes:
        Nodes[current_node] = []
    # Role relation
    target_substring = (formatter.format(right.role()) + ".")
    # Concept name connected to role relation
    filler = formatter.format(right.filler())
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

    # Entailment rule
    if left.getClass().getSimpleName() == "ConceptName" and not left.getClass().getSimpleName() == "ExistentialRoleRestriction" and not left.getClass().getSimpleName() == "ConceptConjunction" and not '∀' in child:
        if right.getClass().getSimpleName() == "ConceptName" and not right.getClass().getSimpleName() == "ExistentialRoleRestriction" and not right.getClass().getSimpleName() == "ConceptConjunction" and not '∀' in parent:
            entailment_rule(current_node, child, parent) # Call entailment function

    # Conjunction rules for left and right
    if left.getClass().getSimpleName() == "ConceptConjunction":
        if not left.getClass().getSimpleName() == "ExistentialRoleRestriction" and not '∀' in child:
            conjunction_rule_left(current_node, child, parent) # call conjunction function for left

    # Example: TeriyakiSauce <= (VegetarianSauce n VeganSauce)
    if right.getClass().getSimpleName() == "ConceptConjunction":
        if not right.getClass().getSimpleName() == "ExistentialRoleRestriction" and not '∀' in parent:
            conjunction_rule_right(current_node, child, parent)

    # Existential rule
    if left.getClass().getSimpleName() == "ExistentialRoleRestriction":
        element = formatter.format(left.role()),'.',formatter.format(left.filler())
        existential_rule_left(element, left, current_node) # Call function existential rule
        if left.filler().getClass().getSimpleName() == "ConceptConjunction":
            conjunction_rule_left(current_node,child,parent)

    if right.getClass().getSimpleName() == "ExistentialRoleRestriction":
        element = formatter.format(right.role()),'.',formatter.format(right.filler())
        # If there is already a Node that has same role, check if the connected filler is
        # saved in a key that already contains the filler from current element in questions
        existential_rule_right(element, right, current_node)
        if right.filler().getClass().getSimpleName() == "ConceptConjunction":
            conjunction_rule_right(current_node,child,parent)

def complete_subsumers(subsumers):
    # Create a copy to modify
    SubsumersComplete = subsumers.copy()

    for key, value_list in subsumers.items():
        # Ensure the current value is a list
        if not isinstance(value_list, list):
            value_list = [value_list]

        for value in value_list:
            if value in subsumers:
                # If the value is also a key, extend its list to the current key's list
                additional_values = subsumers[value]
                if isinstance(additional_values, list):
                    for item in additional_values:
                        if item not in SubsumersComplete[key]:
                            SubsumersComplete[key].append(item)
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

    # print(sys.argv)
    ontology_file = sys.argv[1]
    class_name = sys.argv[2]
    # print(class_name)

    if os.path.exists(ontology_file) == False:
        print("ERROR: ONTOLOGY_FILE cannot be found.")
        sys.exit(1)

    gateway = JavaGateway()  # connect to the java gateway of dl4python
    parser = gateway.getOWLParser() # get a parser from OWL files to DL ontologies
    formatter = gateway.getSimpleDLFormatter() # get a formatter to print in nice DL format
    ontology = parser.parseFile(ontology_file)     # load an ontology from a file

    # IMPORTANT: the algorithm from the lecture assumes conjunctions to always be over two concepts
    gateway.convertToBinaryConjunctions(ontology)

    tbox = ontology.tbox()
    axioms = tbox.getAxioms()
    allConcepts = ontology.getSubConcepts()
    conceptNames = ontology.getConceptNames()
    elFactory = gateway.getELFactory()

    Subsumers = {}
    Nodes = {}

    current_node = 0
    start_time = time.time()

    for axiom in axioms:
        axiomType = axiom.getClass().getSimpleName()

        # Initial element d0
        if axiomType == "GeneralConceptInclusion":

            current_element = axiom
            left = axiom.lhs()
            right = axiom.rhs()
            child = formatter.format(axiom.lhs())
            parent = formatter.format(axiom.rhs())

            if not Nodes: # Add first key-value pair to dictionary
                completion_alg(left, right, current_node, child, parent)
            if Nodes:
                if child in Nodes:
                    current_node = find_key(Nodes, child)
                    completion_alg(left, right, current_node, child, parent)

                elif child not in Nodes:
                    current_node = current_node + 1
                    completion_alg(left, right, current_node, child, parent)

        # Example: NonSpicyPoke ≡ (¬SpicyPoke ⊓ PokeBowl)
        elif axiomType == "EquivalenceAxiom":
            element_left, element_right = axiom.getConcepts()
            format_element_left = formatter.format(element_left)
            format_element_right = formatter.format(element_right)

            if Nodes:
                # Handels both directions of the equivalence
                for left, right in [(element_left, element_right), (element_right, element_left)]:
                    formatted_child = formatter.format(left)
                    formatted_parent = formatter.format(right)

                    current_node = find_key(Nodes, formatted_child) if left in Nodes else current_node + 1
                    completion_alg(left, right, current_node, formatted_child, formatted_parent)

    Subsumers = complete_subsumers(Subsumers)

    if class_name not in Subsumers:
        print('ERROR: The given classname is not found to be a class in the current ontology.')
        sys.exit(1)
    else:
        for concept in Subsumers[class_name]:
            print(concept)