# Introduction

First off, thank you for your enthusiasm for the META system! It's people like you that will make META a better tool for metagenomic analysis.

These guidelines will tell you how to submit issues, what code styling standards to use, and how to package management is done.

## Summary

  - [Contributions](#what-kind-of-contributions-are-we-looking-for)
  - [How to submit issues](#how-to-submit-an-issue)
  - [Package management](#package-management)
  - [Style Guide](#style-guide)
    - [Vue Code Style](#vue-code-style)
    - [Python Code Style](#python-code-style)


### What kind of contributions are we looking for?

We seek to improve META through bug handling and new feature requests. More specifically, we are looking for improvements to the following area:

| Area | How you can help |
| --- | --- |
| **DevOps** | report deployment issues, improve cross-platform deployments, improve our instructions and documentation, write unit tests |
| **User Interface** | report bugs, point out confusing features, suggest workflow improvements, develop new features |
| **Data Analysis and Visualizations** | report bugs in visualizations, report peculiarities in the data analysis and metrics, suggest new visualizations and metrics, develop new features |
| **System Performance** | report bugs related to the Python server, suggest improvements in implementation, help comment and document ambiguous logic |
| **Metagenomic Tools** | suggest new Biocontainer or tool to support, implement parsing scripts for new metagenomic tools | 

#### Roadmap 

Keep in mind our roadmap for the future! Here are some planned improvements:

- Add ability to compare between select job results
- Add prediction model to determine the runtime of a job prior to executing
- Add metagenomic assemblers
- Add configurable read counts for simulated reads
- Add configurable thread counts for metagenomic classifiers
- Add export capability for graphs and visualizations as PNG, JPEG, PDF, etc.
- Add ability to construct abundance profile for simulation within the user interface
- Add user management

# How to submit an issue

When you create an issue in the Git project, you will be provided with the following template. Please answer all appropriate questions with a helpful level of description. Screenshots, links to suggested implementations, video demos are welcome.

> # I'm submitting a...
>   - [ ] Bug report
>   - [ ] Feature request
> 
> ### For Bug Report
> - **What is the current behavior?**
> 
> - **If the current behavior is a bug, please provide the steps to reproduce it and if possible a minimal demo of the problem**.
> 
> - **What is the expected behavior?**
> 
> #### For Feature Request
> - **What is the motivation / use case for changing the behavior?**
> 
> # Other information 
> _**For example:** detailed explanation, stacktraces, console log outputs, related issues, suggestions how to fix, links for us to have context_
> 
> # Please tell us about your environment (if necessary)
> | Environment information | Your response |
> | --- | --- |
> | Operating System        |               |
> | META Version            |               |
> | Browser (if applicable) |               |
> 
> ## Related to...
> _Check all that apply. Descriptions can be found in [CONTRIBUTING.md]_
>   - [ ] Devops
>   - [ ] User Interface
>   - [ ] Interactive Visualizations
>   - [ ] System performance
>   - [ ] Metagenomic tools

# Package Management

### Python Dependencies
Python packages are managed by [Poetry](https://github.com/python-poetry/poetry). Prior to installing or adding new dependencies, you must run `pip install poetry`. Once you have poetry installed, you may:
* **Install** the relevant Python packages by running `poetry install`.
* **Add** new Python dependencies by running `poetry add <package-name>`. This will update the _pyproject.toml_ file.
* **Remove** Python dependencies by running `poetry add <existing-package-name>`. This will update the _pyproject.toml_ file.
* **Export** dependencies to a _requirements.txt_ file by running `poetry export --without-hashes --dev -f requirements.txt > requirements.txt`

Run `poetry` to see additional interfaces.

**NOTE: If Python dependencies have been modified,** commit the _pyproject.toml_, _requirements.txt_, and _poetry.lock_ files.

### Vue Dependencies
Vue packages are managed by [npm](https://www.npmjs.com/). To install new Vue dependencies,
1. `cd app` where the _package.json_ file is located.
2. `npm install <package-name>`. This will update the _package.json_file.
3. **Commit** the _package.json_ and the _package-lock.json_ files.

# Style Guide

## `.editorconfig` file
```
indent_style = space
indent_size = 2
continuation_indent_size = 4
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true
```
* The `.editorconfig` file is used to enforce some of these settings on common development IDE's, see [EditorConfig](http://editorconfig.org/).

## Vue Code Style
* VueJS code should adhere as best as possible to the following style guidelines:
  * [Vue JS Style Guide](https://vuejs.org/v2/style-guide/)
  * [Vue JS Training](https://www.fullstack.io/30-days-of-vue)

## Python Code Style
The following is derived from [PEP8](https://www.python.org/dev/peps/pep-0008/).

### Imports
Imports should usually be on separate lines and sorted (lexically).

##### YES
```python
import os
import sys
from subprocess import PIPE, Popen
```

##### NO
```python
import os, sys
```

Order imports in the following order (with blank line in between):
1. Standard library imports
2. Related third-party imports
3. Local application specific imports

Use absolute imports for predictable behavior. Relative imports should branch off a common root path.
##### YES
```python
import mypkg.sibling 
from mypkg import sibling 
from mypkg.sibling import example
```
##### NO
```python
from . import sibling 
from .sibling import example
```

Avoid wildcard (*) imports. 

### Naming Convention
| Type of Structure | Description | Convention |
| ------ | ------ | ------ |
| Classes | `CapWords` | Bundles data and functions together to form a new “type” of object) |
| Protected methods and internal functions | `_single_leading_underscore(...)` | Indicates that this should be accessed from within the class and it’s subclasses |
| Constants | `ALL_CAP_WITH_UNDERSCORES` | A type of variable whose value should not be changed. You can spot a constant by seeing if its value is a literal, i.e. numeric, string, or Boolean. Note: Constants should be defined at the top of a file or class.|
| Variables, functions, methods, packages, modules | `lower_case_with_underscores` | everything else! |

Do **not** name variables using single-letters unless it is an index for an iterator (e.g. `i`, `j`) or a commonly-used mathematical or domain-specific symbol (e.g. `r`, `x`, `y`, `m`, `n`).

### Code Headers
Start every file with
```python
    #!/usr/bin/env python3
    # -*- coding: utf-8 -*
```

And include the appropriate copywrite statement. If code is copied, include the author’s copywrite as well.

### String Quotes
Use double quotes (`“`) for all strings. Use `\` to escape a double quote.  
**YES** `“\””`, `“’”`  
**NO** `'”’`  

### Comments
Inline comments should be separated by at least two spaces from the statement (PEP8).
Comments should be used to:
* Explain non-trivial code (e.g. math equations, complex IF-ELSE statements)
* Provide context to domain specific terms. Explanatory permalinks are welcome!
    ```python
    # UTM approximates distance along surface of earth in meters https://helpfullinkhere.org
    ```
* State rationale for constants
    ```python
    x = x * 1.9  # Adds 90% buffer
    ```
    
### Documentation
Use triple quotes (`“””`) to provide documentation for public methods.
Use one-line docstrings for obvious functions:
   ```python
   “””Return the pathname of foo.“””
   ```
Use multiline docstrings for complex functions. They should include: summary, use case (if appropriate), arguments and their types, and return type.
```python
"""Train a model to classify Foos. 
Usage:: 
   >>> import mypkg 
   >>> data = [(”a", 1), (”b", 0)] 
   >>> classifier = mypkg.train(data) 
:param train_data: A list of tuples of the form ``(color, label)``. 
:return: A :class:`Classifier <Classifier>` 
"""
```

### Exception Handling via TRY-EXCEPT
Use try-except-finally blocks to handle exceptions and errors at runtime.  
```python
try:
    <do something>
except (OSError, TypeError) as e:
    logger.error("Your Msg",exc_info=e)
finally:
    <cleanup that is always executed>
```

Only use when you are unsure about:
* The input type or shape into a function
* The value received for arithmetic
* The existence of a file
* The integration points between outside services (e.g. reaching out over the network, service uptime)
* Always use exception handling when making library calls or system calls

### Validation via IF-ELSE
Use if-else blocks to validate inputs and states prior to executing functions. Some examples of when to do validation are shown below:
###### Check if a variable is empty or None
```python
 if x: ...  # checks if truth-y
 if x is None: ...  # checks if None
```
###### Check if a value has the proper shape (e.g. array dimensions, keys in a dictionary)
```python
if len(x) > 5: ...
if “mykey” in x.keys(): ...
```
###### Check if a value has the proper type
```python
if isinstance(x, dict): ...
```
###### Check if a variable has a desired states or modes (e.g. true/false, Enum equivalence)
```python
if x == EnumExample.MODE_0: ...
```

### Type Hinting
Specify type of input and output variables when declaring a function. Use the syntax 
```python
def foo(in_var: int) -> (str): 
```
Type annotations can be:
* Simple built-in types (e.g. `int`, `float`, `bool`, `str`, `bytes`)
* Using Python typing library (e.g. `Mapping`, `MutableMapping`, `Sequence`, `Iterable`, `List`, `Set`)
* Imported (e.g. `numpy.array`) and local classes (e.g. `MyClass`)

### Data Structures
* _**List**_: holds a ordered collection of items `x=[a, b, c]`
    * Mutable; Can add, remove, or search for items
* _**Dictionary**_: associates key and values `x={key: value}`
    * Can only use immutable objects for keys; Can use immutable or mutable objects for values
    * Key-value pairs are not ordered
* _**Set**_: unordered collection of unique, immutable objects
    * Use when the existence of an object is more important than the order or how many times it occurs
* _**Tuple**_: hold multiple objects together `x=(a, b)`
    * Immutable; Use when you can safely assume that collection of values will not change
* _**NamedTuple**_: assign a name to each position in a tuple
    * Names are immutable strings; Elements are iterable
    * Can access values by name or index
    * Use when needing to make many instances of a class that only contain attributes (not methods)
    ``` python
    >>> Point=collections.namedtuple(”Point”, 
    [“x”, ”y”])
    >>> p = Point(x=11, y=22)
    ```
* _**Enum**_: set of names bound to unique, constant values that can be symbolically compared
    * Use if you want to compare predefined list of constants by a symbolic name (instead of using the value itself)
    * Use when a variable can only take one out of a small set of possible values (e.g. status, modes, flags)

### Logs
Log for the purpose of documenting important behaviors/milestones that the code has reached during runtime. Some scenarios where a log is important:
* When entering/exiting a complex function
* When receiving a message from an external service (Print the contents of the message or a subset of the message that is important for validation of success)
* When an important mutable object has been updated
* When an exception or rare behavior has occurred  

Use the proper severity levels for logs—
* **CRITICAL**: For messages that require immediate attention
* **ERROR**: Wraps exceptions and errors thrown from code
* **WARNING**: An event that caused a rare, notable behavior
* **INFO**: Normal code execution, messages received
* **DEBUG**: Logs that are only important during debugging




