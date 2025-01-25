import itertools
from edn_format import Keyword
from syntax.reader import r
from syntax.expression import *
from fol.fol_prover import *
from syntax.reader import *

from reasoners.shadow_prover import *
from unifiers.first_order_unify import *
from edn_format import Keyword
from syntax.expression import *
import edn_format
from edn_format import Keyword
from syntax.expression import *

name_keyword = Keyword("name")
description_keyword = Keyword("description")
assumptions_keyword = Keyword("assumptions")
goal_keyword = Keyword("goal")
schema_keyword = Keyword("schema")
name_keyword = Keyword("name")

inputs_keyword = Keyword("inputs")
output_keyword = Keyword("output")


    
class Action:
    def __init__(self, predicate,  precondition, additions, deletions):
        self.predicate = predicate
        self.precondition = precondition
        self.additions = set(additions)
        self.deletions = set(deletions)
        self.variables = list(map(str, predicate.args))

    def __existentially_quantified__(self, expr):
        return r(f"(exists [{' '.join(map(str, self.predicate.args))}] {str(expr)})")

    def __universally_quantified__(self, expr):
        
        return r(f"(forall [{' '.join(map(str, expr.args))}]  {str(expr)})")

    
    def applicable(self, domain, background, state, prover, max_answers):
        existential = self.__existentially_quantified__(self.precondition)
        answers = is_satisfied_with_matches(background.union(state), existential, prover, max_answers)
        if not answers:
            return None
        return answers

    def apply(self,  state, theta):
        deletions = set([d.apply_substitution(theta) for d in self.deletions])
        additions = set([a.apply_substitution(theta) for a in self.additions])
        
        new_state = (state - deletions) | additions
        return {"new_state":  new_state, "additions": additions, "deletions": deletions}
    


def is_satisfied_with_matches(state, test, prover, max_answers):
    (satisfied, proof, answers) = prover(state, test, find_answer=True, max_answers=max_answers)
    
    if satisfied:

        
        return answers if answers else True
    else:
        return None


def plan2(domain, background, current_state, goal, actions, prover=fol_prove, visited=None, changes_so_far =[]):



    match = is_satisfied_with_matches(current_state, goal, prover, max_answers=len(domain))
    
    if match == True:
        return []  

    if not visited:
        visited = set([frozenset(current_state)])
    
    for action in actions:
        matching_substitutions = action.applicable(domain, background, current_state, prover, max_answers=len(domain))
        if type(matching_substitutions)==list:

            for matching_substitution in matching_substitutions:
                changes = action.apply(current_state, matching_substitution)
                new_state = changes["new_state"]
                additions = changes["additions"]
                deletions = changes["deletions"]
                del changes['new_state']

                if frozenset(new_state) not in visited:
                    for change in changes_so_far:
                        if change["additions"] == deletions and change["deletions"] == additions:
                            return False
                    from_here = plan2(domain, background, new_state, goal, actions, prover,
                                      visited.union(set([frozenset(new_state)])), changes_so_far + [changes])
                    if from_here is not False:
                        return [action.predicate.apply_substitution(matching_substitution)]+from_here
                        

    return False   



def planbfs(domain, background, start_state, goal, actions, prover=fol_prove):

    Q =  []
    Q.append((start_state, []))    
    explored = set([frozenset(start_state)])
    
    while Q:
        v, path = Q.pop(0)
        match = is_satisfied_with_matches(v, goal, prover, max_answers=len(domain))
        if match:
            return path
        for action in actions:
            matching_substitutions = action.applicable(domain, background, v, prover, max_answers=len(domain))
            if type(matching_substitutions)==list:
                for matching_substitution in matching_substitutions:
                    changes = action.apply(v, matching_substitution)
                    new_state = frozenset(changes["new_state"])
                    if new_state not in explored: 
                        explored.add(new_state)
                        Q.append((new_state, path + [action.predicate.apply_substitution(matching_substitution)]))
                                

    return None   