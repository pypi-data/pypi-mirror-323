import re 
import sys
import traceback

from openai import OpenAI
from IPython import get_ipython

import os
import getpass
from IPython.display import display
import ipywidgets as widgets

from IPython.display import display, HTML

def in_colab():
  try:
    import google.colab
    return True
  except:
    return False

def get_code_and_error_trace():
  # Get the code from the previous cell
  ip = get_ipython()
  if ip is not None:
    # Running in a Jupyter notebook
    if hasattr(ip, 'history_manager') and hasattr(ip.history_manager, 'input_hist_raw'):
        # Access the input history
        ih = ip.history_manager.input_hist_raw

        previous_cell_code = ih[-2]  # _ih is an alias for In, and -2 refers to the previous cell

  # Get the error trace from the previous cell's execution
  error_trace = ""
  if sys.last_type is not None:  # Check if an exception occurred
      error_trace = "".join(traceback.format_exception(sys.last_type, sys.last_value, sys.last_traceback))
  
  return previous_cell_code, error_trace

def get_out_code(input_string):
  section = re.search(r"```(.*?)```", input_string, re.DOTALL).group(1) if re.search(r"```(.*?)```", input_string, re.DOTALL) else None
  output_string = '\n'.join(lines[1:]) if (lines := section.splitlines())[0].find('import') == -1 else section
  output_string = output_string.replace("plt.show()", "")

  return output_string

def debug_code(code_str, error_trace):
  debugger = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
  debugger_role = "You are a helpful assistant tasked with debugging Python code."
  debugger_prompt = f"Please help debug this Python code. The code and error trace are provided below, enclosed in ``` ``` tags as follows:  \n\
            Code: {code_str}\n\n\
            Error trace: {error_trace}\n\n\
            Instructions:\n\
            1. Return only the Python code with the error fixed enclosed in ``` ``` tags.\n\
            2. Do not return anything besides the delimited Python code."

  debugger_completion = debugger.chat.completions.create(
      model=os.environ["JUPYTERDEBUG_MODEL"],
      messages=[
          {"role": "developer", "content": f"{debugger_role}"},
          {
              "role": "user",
              "content": f"{debugger_prompt}"
          }
      ]
  )

  code = get_out_code(debugger_completion.choices[0].message.content)

  return code

def paste_code(code_str):
  if in_colab():
      from google.colab import _frontend
      _frontend.create_scratch_cell(code_str)
  else:
    #ip.set_next_input(code_str, replace=True)
    ip = get_ipython()
    
    payload = dict(
        source='set_next_input',
        text=code_str,
        replace=True,
    )
    ip.payload_manager.write_payload(payload, single=False)

def debug_all(new_code, max_tries = 3):
  iter_cnt = 0
  code_failed = True
  while code_failed and iter_cnt < max_tries:
    iter_cnt += 1
    ip = get_ipython()

    result = ip.run_cell(new_code)
    if result.error_in_exec:
      error_trace = traceback.format_exc()
      new_code = debug_code(new_code, error_trace)
    else:
      code_failed = False

  return new_code