from py4j.java_gateway import JavaGateway
import re

gateway = JavaGateway() # connect to the java gateway of dl4python
parser = gateway.getOWLParser() # get a parser from OWL files to DL ontologies
formatter = gateway.getSimpleDLFormatter() # get a formatter to print in nice DL format
ontology = parser.parseFile("KR1_POKE.rdf") # load an ontology from a file

# # print(ontology)
#
# # IMPORTANT: the algorithm from the lecture assumes conjunctions to always be over two concepts
# # Ontologies in OWL can however have conjunctions over an arbitrary number of concpets.
# # The following command changes all conjunctions so that they have at most two conjuncts
# gateway.convertToBinaryConjunctions(ontology)
#
# # get the TBox axioms
# tbox = ontology.tbox()
# axioms = tbox.getAxioms()
#
# print("These are the axioms in the TBox:")
# for axiom in axioms:
#     print(formatter.format(axiom))
#
# # get all concepts occurring in the ontology
# allConcepts = ontology.getSubConcepts()
#
# print()
# print("There are ",len(allConcepts), " concepts occurring in the ontology")
# print("These are the concepts occurring in the ontology:")
# print([formatter.format(x) for x in allConcepts])
#
# conceptNames = ontology.getConceptNames()
#
# print()
# print("There are ", len(conceptNames), " concept names occurring in the ontology")
# print("These are the concept names: ")
# print([formatter.format(x) for x in conceptNames])
#
#
# # access the type of axioms:
# foundGCI = False
# foundEquivalenceAxiom = False
# print()
# print("Looking for axiom types in EL")
# for axiom in axioms:
#     axiomType = axiom.getClass().getSimpleName()
#     #print(axiomType)
#     if(not(foundGCI)
#        and axiomType == "GeneralConceptInclusion"):
#         print("I found a general concept inclusion:")
#         print(formatter.format(axiom))
#         print("The left hand side of the axiom is: ", formatter.format(axiom.lhs()))
#         print("The right hand side of the axiom is: ", formatter.format(axiom.rhs()))
#         print()
#         foundGCI = True
#
#     elif(not(foundEquivalenceAxiom)
#          and axiomType == "EquivalenceAxiom"):
#         print("I found an equivalence axiom:")
#         print(formatter.format(axiom))
#         print("The concepts made equivalent are: ")
#         for concept in axiom.getConcepts():
#             print(" - "+formatter.format(concept))
#         print()
#         foundEquivalenceAxiom = True
#
# # accessing the relevant types of concepts:
# foundConceptName=False
# foundTop=False
# foundExistential=False
# foundConjunction=False
# foundConceptTypes = set()
#
# print()
# print("Looking for concept types in EL")
# for concept in allConcepts:
#     conceptType = concept.getClass().getSimpleName()
#     if(not(conceptType in foundConceptTypes)):
#         print(conceptType)
#         foundConceptTypes.add(conceptType)
#     if(not(foundConceptName) and conceptType == "ConceptName"):
#         print("I found a concept name: "+formatter.format(concept))
#         print()
#         foundConceptName = True
#     elif(not(foundTop) and conceptType == "TopConcept$"):
#         print("I found the top concept: "+formatter.format(concept))
#         print()
#         foundTop = True
#     elif(not(foundExistential) and conceptType == "ExistentialRoleRestriction"):
#         print("I found an existential role restriction: "+formatter.format(concept))
#         print("The role is: "+formatter.format(concept.role()))
#         print("The filler is: "+formatter.format(concept.filler()))
#         print()
#         foundExistential = True
#     elif(not(foundConjunction) and conceptType == "ConceptConjunction"):
#         print("I found a conjunction: "+formatter.format(concept))
#         print("The conjuncts are: ")
#         for conjunct in concept.getConjuncts():
#             print(" - "+formatter.format(conjunct))
#         print()
#         foundConjunction=True
#
#
# # Creating EL concepts and axioms
#
# elFactory = gateway.getELFactory()
#
# conceptA = elFactory.getConceptName("A")
# conceptB = elFactory.getConceptName("B")
# conjunctionAB = elFactory.getConjunction(conceptA, conceptB)
# role = elFactory.getRole("r")
# existential = elFactory.getExistentialRoleRestriction(role,conjunctionAB)
# top = elFactory.getTop()
# conjunction2 = elFactory.getConjunction(top,existential)
#
# gci = elFactory.getGCI(conjunctionAB,conjunction2)
#
# print()
# print()
# print("I made the following GCI:")
# print(formatter.format(gci))
#
# # Using the reasoners
# elk = gateway.getELKReasoner()
# hermit = gateway.getHermiTReasoner() # might the upper case T!
#
# OctoBowl = elFactory.getConceptName('"PokeBase"')
#
# print()
# print("I am first testing ELK.")
# elk.setOntology(ontology)
# print()
# print("According to ELK, pokebase has the following subsumers: ")
# subsumers = elk.getSubsumers(OctoBowl)
# for concept in subsumers:
#     print(" - ",formatter.format(concept))
# print("(",len(subsumers)," in total)")
#
# print(subsumers.toString())
#
# print()
# print("I can also classify the ontology with ELK.")
# classificationResult = elk.classify()
# print("But I am not printing the result, because that would be too much stuff (it is a dictionary)")
# print()
#
# print()
# print("I am now testing HermiT.")
# hermit.setOntology(ontology)
# print()
# print("According to HermiT, pokebase has the following subsumers: ")
# subsumers = hermit.getSubsumers(OctoBowl)
#
# print(subsumers.toString())
#
# for concept in subsumers:
#     print(" - ",formatter.format(concept))
# print("(",len(subsumers)," in total)")
# print()
# print("I can also classify the ontology with HermiT")
# classificationResult = hermit.classify()
# print("But I am not printing the result, because that would be too much stuff (it is a dictionary)")
# print()

def rearrange_ontology(ontology):
    tbox = ontology.tbox()
    axioms = tbox.getAxioms()

    rbox = str(ontology.rbox())
    rbox = rbox.split('\n')
    properties_list = []

    # Create a list w the properties
    # IS NOT USED YET, MIGHT BE HELPFUL LATER
    for property_ in rbox:
        property_split = property_.split(' ')
        for element in property_split:
            if element.isalpha() and element not in properties_list:
                properties_list.append(element)

    print(properties_list)

    delimiters = r"([∀∃¬⊓⊔,.() ])" # All the characters on which we want to split the string
    quantifiers_list = ['∀','∃','¬']

    classes = {} # keys are children, values are parents
    properties = {}
    equal_to = {}

    for axiom in axioms:
        f_axiom = formatter.format(axiom)
        split_axiom = re.split(delimiters, f_axiom) # splits string in multiple substrings: 'SpicyTempehBowl ⊑ SpicyPoke' becomes ['SpicyTempehBowl', '⊑', 'SpicyPoke']

        elements_to_remove = {'', ' '}
        split_axiom = [x for x in split_axiom if x not in elements_to_remove] # Removes all unnecessary elements from list
        print(split_axiom)

        if '.' in split_axiom:
            if '⊑' in split_axiom:
                # if split_axiom[-2] == '.':  # Takes all strings like: SalmonBowl ⊑ ∃hasBase.PokeBase
                if len(split_axiom) == 6: # Takes all strings like: SalmonBowl ⊑ ∃hasBase.PokeBase, as they have 6 elements in the split_axiom

                    concept = split_axiom[0]  # SalmonBowlwen
                    property_ = split_axiom[split_axiom.index('.') - 1]  # hasBase
                    property_object = split_axiom[split_axiom.index('.') + 1] # PokeBase

                    count_quantifier = sum(1 for element in split_axiom if element in quantifiers_list)  # Counts amount of quantifiers, some have multiple

                    if count_quantifier == 1:
                        quantifier_1 =  split_axiom[split_axiom.index('⊑') + 1]

                        if concept in properties:  # object is added to the dictionary like this: Key: SalmonBowls, value: [∃, hasBase, PokeBase]
                            if property_ in properties[concept]['properties']:
                                properties[concept]['properties'][property_].append(property_object)
                        else:
                            properties[concept] = {'quantifier_1': [quantifier_1],
                                                   'properties': {property_: [property_object]}}

                    elif count_quantifier == 2:
                        pass  # TODO
                    else:
                        pass  # TODO

                else:
                    if split_axiom[split_axiom.index('⊑') + 1] == '(': # Checks whether element after ⊑ is a (
                        if split_axiom[split_axiom.index('(') + 2] == '⊓':
                            pass # TODO: Should take lists like: ['SoySauce', '⊑', '(', 'VegetarianSauce', '⊓', 'VeganSauce', ')']
                        elif split_axiom[split_axiom.index('(') + 2] == '⊔':
                            pass # TODO: # Should take lists like: ['VeganTunaBowl', '⊑', '∀', 'hasTopping', '.', '(', 'Corn', '⊔', 'Edamame', '⊔', 'SesameMix', '⊔', 'Avocado', '⊔', 'Cucumber', ')']

                    pass
            if '≡' in split_axiom:
                pass # TODO

        elif '⊑' in split_axiom: # takes all strings like: VegetarianSauce ⊑ PokeSauce
            parent = split_axiom[2] # Define child and parent
            child = split_axiom[0]
            if child in classes:  # check whether parent already exists
                classes[child].append(parent)
            else:
                classes[child] = [parent]

    return classes, properties

def find_subsumers(concept, ontology):
    subsumers_list = []

    classes = rearranged_ontology[0]
    properties = rearranged_ontology[1] # TODO: function needs to use properties to find subsumers

    if concept in classes:
        subsumers_list.extend(classes[concept]) # Add all the parents of the concept to the list

    for element in subsumers_list:
        if element in classes:
            subsumers_list.extend(classes[element]) # loop over all the parents of the concept, and extend the subsumers list w their parents

    return subsumers_list

if __name__ == "__main__":

    concept = "OctoBowl"
    rearranged_ontology = rearrange_ontology(ontology)

    print(rearrange_ontology(ontology)[0]) # Prints all classes (children as keys, parents as values)
    print(rearrange_ontology(ontology)[1]) # Prints all properties (concepts as keys, list of lists with the following as values [quantifier, property, property concept])

    # Find subsumers
    subsumers_ = find_subsumers(concept, rearranged_ontology)
    print(subsumers_)






