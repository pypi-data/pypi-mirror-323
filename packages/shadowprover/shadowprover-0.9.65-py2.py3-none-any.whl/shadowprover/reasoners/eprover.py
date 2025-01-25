import subprocess
from functools import cache

# @cache
# def run_eprover_with_string_input(input_spec: str, find_answer=False, max_answers=5) -> str:
#    if find_answer:
#       options = ["/Users/naveensundar/projects/py_laser/eprover/PROVER/eprover-ho",  "--auto", f"--answers={max_answers}"] 
#    else:
#       options = ["/Users/naveensundar/projects/py_laser/eprover/PROVER/eprover-ho", "--auto"] 
#    completed_process = subprocess.run(
#        options, input=input_spec.encode(), capture_output=True
#     )
#    return completed_process

#"/Users/naveensundar/projects/py_laser/eprover/PROVER/eprover-ho
@cache
def run_eprover_with_string_input(input_spec: str, find_answer=False, max_answers=5, e_prover_invocation="/Users/naveensundar/projects/shadow_prover/eprover/PROVER/eprover-ho") -> str:
   if find_answer:
      options = [e_prover_invocation,  "--auto", f"--answers={max_answers}"] 
   else:
      options = [e_prover_invocation, "--auto"] 
   completed_process = subprocess.run(
       options, input=input_spec.encode(), capture_output=True
    )
   return completed_process
