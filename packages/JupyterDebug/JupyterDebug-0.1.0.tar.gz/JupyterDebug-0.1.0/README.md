## Documentation for `JupyterDebug`

### Package Overview
`JupyterDebug` is a Python package designed to help users debug Python code in Jupyter notebooks using OpenAI's language models. It provides two main methods:
1. `init()`: Initializes the package by prompting the user for their OpenAI API key and selecting a model.
2. `debug(max_iter=1)`: Automatically debugs the code in the previous cell by calling the selected language model iteratively to fix errors.

---

### Installation
To install `JupyterDebug`, use pip:
```bash
pip install JupyterDebug
```

---

### Usage

#### 1. `init()`
The `init()` method initializes the package by prompting the user for their OpenAI API key and selecting a model. It must be called before using the `debug()` method.

**Syntax**:
```python
import JupyterDebug as jd
jd.init()
```

**Behavior**:
- Prompts the user to enter their OpenAI API key.
- Asks the user to select a model from the following options:
  - `gpt-4o-mini` (default)
  - `gpt-4o`
  - `o1`
  - `o1-mini`
- Stores the API key and model selection in environment variables for use in the `debug()` method.

---

#### 2. `debug(max_iter=1)`
The `debug()` method automatically debugs the code in the previous cell by calling the selected language model iteratively to fix errors. It should be called in a new cell immediately after the cell that generated the error. 

**Syntax**:
```python
jd.debug(max_iter=1)
```

**Parameters**:
- `max_iter` (optional, default=1): The maximum number of times the language model is called to iteratively debug the code. If the first solution does not fix all errors, the method will retry up to `max_iter` times.

**Behavior**:
- Captures the code from the previous cell and the error trace.
- Calls the selected language model to generate a fix for the code.
- Replaces the code in the previous cell with the fixed version.
- If `max_iter > 1`, the process is repeated until all errors are fixed or the maximum number of iterations is reached.

**Example**:
```python
# Cell 1: Code with an error
x = 10
y = "20"
z = x + y  # This will raise a TypeError
```

```python
# Cell 2: Debug the error
jd.debug()
```

---

### Example Workflow
1. Install the package:
   ```bash
   pip install JupyterDebug
   ```

2. Initialize the package:
   ```python
   import JupyterDebug as jd
   jd.init()
   ```

3. Write and run code in a Jupyter notebook cell:
   ```python
   # Cell 1: Code with an error
   x = 10
   y = "20"
   z = x + y  # This will raise a TypeError
   ```

4. Debug the error in the next cell:
   ```python
   # Cell 2: Debug the error
   jd.debug(max_iter=2)
   ```
