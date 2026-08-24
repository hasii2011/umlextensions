![](https://github.com/hasii2011/code-ally-basic/blob/master/developer/agpl-license-web-badge-version-2-256x48.png "AGPL")

[![CI](https://github.com/hasii2011/umlextensions/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/hasii2011/umlextensions/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/umlextensions.svg)](https://badge.fury.io/py/umlextensions)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/hasii2011/umlextensions/graphs/commit-activity)

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

# Introduction
This project is a library for generating UML diagrams from Python source code, and it includes a demonstration application.

# Overview

The `umlextensions` module provides a flexible way to add capabilities to the core UML Diagrammer.  There are extensions that read external data and convert it to a UML class diagram.  An example is the `InputPython` extension that reads Python source code and generates an appropriate UML Diagram.  There are extensions that take an existing UML diagram and convert it to a different structure format.   For example, the `OutputGML` extension produces [GML](https://grokipedia.com/page/Graph_Modelling_Language) files.

Finally, there are tool extensions that manipulate a UML diagram.  Examples of this are:

-   [ToolOrthogonalLayout](https://github.com/hasii2011/orthogonal) - Lays out shapes in a manner to minimize link crossings and link bends.
-   [ToolOrthogonalRouting](https://github.com/hasii2011/py-orthogonal-routing) - Lays out links such that link bends are orthogonal.
-   [ToolSugiyama](https://www.linkedin.com/pulse/understanding-sugiyama-framework-sanskar-tyagi-anh3c/) - Lays out shapes and links in a pleasing manner.



# Installation

You can install the project using pip. It is recommended to do this in a virtual environment.

```bash
pip install umlextensions
```

### Dependencies

This project relies on several other packages. `pip` will handle the installation of these dependencies. They are listed here for your reference:

*   [wxPython](https://wxpython.org)
*   [codeallybasic](https://github.com/hasii2011/code-ally-basic)
*   [codeallyadvanced](https://github.com/hasii2011/code-ally-advanced)
*   [umlmodel](https://github.com/hasii2011/umlmodel)
*   [umlshapes](https://github.com/hasii2011/umlshapes)
*   [umlio](https://github.com/hasii2011/umlio)
*   [antlr4-python3-runtime](https://pypi.org/project/antlr4-python3-runtime/)
*   [pypubsub](https://github.com/schollii/pypubsub)

# Usage

The primary way to use this project is as a library within a larger application. However, a demonstration application is included to showcase the functionality.

### Running the Demo Application

To run the demo application, follow these steps:

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone https://github.com/hasii2011/umlextensions.git
    cd umlextensions
    ```

2.  **Install dependencies (it is recommended to use a virtual environment):**
    ```bash
    pip install -e .
    ```

3.  **Run the demo application:**
    ```bash
    python tests/extensiondemo/ExtensionDemoApp.py
    ```
    This will open a window titled "Demo UML Extensions".

### Generating a UML Diagram

1.  In the "Demo UML Extensions" window, navigate to the menu bar and click **Extensions -> Input -> Python File(s)**.

2.  A file dialog will appear, allowing you to select one or more Python files. Select the files you want to include in your UML diagram and click **Open**.

3.  After parsing the files, a dialog titled "Shape Layout Parameters" may appear, allowing you to adjust the layout of the UML shapes. You can accept the defaults or modify them as needed and click **OK**.

4.  The application will then generate and display the UML class diagram based on the Python code in the selected files.

### As a Library

The project is designed to be used as a library. The `umlextensions` package can be imported into your own `wxPython` application. The `ExtensionsManager` class is the main entry point for discovering and running extensions. You can integrate it into your application by providing an implementation of the `IExtensionsFacade`.
___

Written by <a href="mailto:humberto.a.sanchez.ii@gmail.com?subject=Hello Humberto">Humberto A. Sanchez II</a>  ©2026

---

## Note
For all kinds of problems, requests, enhancements, bug reports, etc., please drop me an e-mail.


[Copilot Statement](https://github.com/hasii2011/code-ally-basic/wiki/GitHub-Copilot).
