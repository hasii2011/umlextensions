![](https://github.com/hasii2011/code-ally-basic/blob/master/developer/agpl-license-web-badge-version-2-256x48.png "AGPL")

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/hasii2011/umlextensions/tree/master.svg?style=shield)](https://dl.circleci.com/status-badge/redirect/gh/hasii2011/umlextensions/tree/master)
[![Build Status](https://app.travis-ci.com/hasii2011/umlextensions.svg?token=xLRFkv8yzJS4p9oSFs49&branch=master)](https://app.travis-ci.com/hasii2011/umlextensions)
[![PyPI version](https://badge.fury.io/py/umlextensions.svg)](https://badge.fury.io/py/umlextensions)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

# Introduction
This project is a library for generating UML diagrams from Python source code, and it includes a demonstration application.

# Overview
The `umlextensions` package provides a flexible way to reverse-engineer Python code into UML class diagrams. It is designed to be extensible, allowing for different input and output formats. The core of the project is a parser that analyzes Python source code and a layout engine that arranges the UML shapes for visualization. A demonstration application built with `wxPython` is included to showcase the library's capabilities.

# Installation

You can install the project using pip. It is recommended to do this in a virtual environment.

```bash
pip install umlextensions
```

### Dependencies

This project relies on several other packages. `pip` will handle the installation of these dependencies. They are listed here for your reference:

*   wxPython
*   codeallybasic
*   codeallyadvanced
*   umlmodel
*   umlshapes
*   umlio
*   antlr4-python3-runtime
*   PyPubSub

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
Written by Humberto A. Sanchez II <mailto@Humberto.A.Sanchez.II@gmail.com>, (C) 2025

# Note
For all kind of problems, requests, enhancements, bug reports, etc., please drop me an e-mail.

------
![Humberto's Modified Logo](https://raw.githubusercontent.com/wiki/hasii2011/gittodoistclone/images/SillyGitHub.png)

I am concerned about GitHub's Copilot project

I urge you to read about the
[Give up GitHub](https://GiveUpGitHub.org) campaign from[the Software Freedom Conservancy](https://sfconservancy.org).

While I do not advocate for all the issues listed there I do not like that a company like Microsoft may profit from open source projects.

I continue to use GitHub because it offers the services I need for free.  But, I continue to monitor their terms of service.

Any use of this project's code by GitHub Copilot, past or present, is done without my permission.  I do not consent to GitHub's use of this project's code in Copilot.
