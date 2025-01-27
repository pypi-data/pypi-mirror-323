# core.py
import re 
import sys
import traceback

from openai import OpenAI
from IPython import get_ipython

import os
import getpass
from IPython.display import display
import ipywidgets as widgets

from JupyterDebug.utils import get_code_and_error_trace, debug_code, debug_all, paste_code

def init(api_key=None, model='gpt-4o-mini'):
    """
    Prompt the user to enter their OpenAI API key and choose a model.
    Works in both command-line and Jupyter notebook environments.
    """
    # Print instructions
    print("PyDebug: Logging into OpenAI.")
    print("You can find your API key in your browser here: https://platform.openai.com/account/api-keys")
    print("If you are using VS code and cannot paste into the text box, you can also provide the api key/model as parameters init(api_key='...', model='...')")
    print("Paste an API key from your profile and hit enter, or press ctrl+c to quit:")

    if api_key: 
        os.environ["OPENAI_API_KEY"] = api_key
        os.environ["JUPYTERDEBUG_MODEL"] = model
        print("API key succesfully set!")
        print(f"Model set to {os.environ['JUPYTERDEBUG_MODEL']}")
    else:
        # Check if running in a Jupyter notebook
        try:
            from IPython import get_ipython
            if get_ipython() is not None:
                # Use a text entry box in Jupyter for the API key
                api_key_input = widgets.Text(
                    placeholder='Enter your OpenAI API key here',
                    description='API Key:',
                    disabled=False
                )

                # Dropdown for model selection
                model_dropdown = widgets.Dropdown(
                    options=['gpt-4o-mini', 'gpt-4o', 'o1', 'o1-mini'],
                    value='gpt-4o-mini',  # Default model
                    description='Model:',
                    disabled=False
                )

                # Create a button to submit the API key and model
                submit_button = widgets.Button(description="Submit")
                output = widgets.Output()

                def on_submit_button_clicked(b):
                    with output:
                        api_key = api_key_input.value.strip()
                        model = model_dropdown.value
                        if api_key:
                            os.environ["OPENAI_API_KEY"] = api_key
                            os.environ["JUPYTERDEBUG_MODEL"] = model
                            print(f"API key set successfully! Selected model: {model}")
                        else:
                            print("No API key provided. Please try again.")

                submit_button.on_click(on_submit_button_clicked)
                display(api_key_input, model_dropdown, submit_button, output)
            else:
                # Use command-line input for the API key
                api_key = getpass.getpass("API Key: ")
                if api_key:
                    # Prompt for model selection in the command line
                    print("Select a model (default: gpt4o-mini):")
                    print("1. gpt-4o-mini")
                    print("2. gpt-4o")
                    print("3. o1")
                    print("4. o1-mini")
                    model_choice = input("Enter the number corresponding to your choice (1-4): ").strip()
                    model_map = {
                        '1': 'gpt-4o-mini',
                        '2': 'gpt-4o',
                        '3': 'o1',
                        '4': 'o1-mini'
                    }
                    model = model_map.get(model_choice, 'gpt4o-mini')  # Default to 'gpt4o-mini' if invalid choice
                    os.environ["OPENAI_API_KEY"] = api_key
                    os.environ["JUPYTERDEBUG_MODEL"] = model
                    print(f"API key set successfully! Selected model: {model}")
                else:
                    print("No API key provided. Please try again.")
        except Exception as e:
            print(f"An error occurred: {e}")

def debug(max_iter = 1):
  try:
    api_key = os.environ["OPENAI_API_KEY"]
  except:
    raise ValueError("OpenAI API Key not set, run 'jd.init()' first, then try again.")

  previous_cell_code, error_trace = get_code_and_error_trace()
  code = debug_code(previous_cell_code, error_trace)
  if max_iter > 1:
    code = debug_all(code, max_iter - 1)
  paste_code(code)