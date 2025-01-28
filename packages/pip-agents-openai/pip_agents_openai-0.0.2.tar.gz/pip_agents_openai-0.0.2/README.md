# <img src="https://uploads-ssl.webflow.com/5ea5d3315186cf5ec60c3ee4/5edf1c94ce4c859f2b188094_logo.svg" alt="Pip.Agents Logo" width="200"> <br/> Access to Open.AI LLMs for Python

This module is a part of the [Pip.Agents](https://www.pipservices.org/) polyglot AI agents toolkit.
It provides a set of basic patterns used in AI applications and AI agents.

The module contains the following packages:
- **Content** - data content
- **Streams**- content streams with transformations
- **Flows** - AI information flows
- **Models** - access to knowledge bases / LLMs
- **Memory** -  memory components to retain short-term, long-term and semantic memory
- **Strategy** - strategizing / goal setting components
- **Planning** - planning components
- **Execution** - execution components
- **Tools** - perception and actuation tools
- **Sequence** - sequential process integration
- **Network** - multi-agent collaboration
- **Hierarchy** - hierarchical composition

<a name="links"></a> Quick links:

* [API Reference](https://pip-agents-python.github.io/pip-agents-openai-python/index.html)
* [Change Log](CHANGELOG.md)
* [Get Help](http://docs.pipservices.org/get_help/)
* [Contribute](http://docs.pipservices.org/contribute/)

## Use

Install the Python package as
```bash
pip install pip_agents_openai
```

## Develop

For development you shall install the following prerequisites:
* Python 3.7+
* Visual Studio Code or another IDE of your choice
* Docker

Install dependencies:
```bash
pip install -r requirements.txt
```

Run automated tests:
```bash
python test.py
```

Generate API documentation:
```bash
./docgen.ps1
```

Before committing changes run dockerized build and test as:
```bash
./build.ps1
./test.ps1
./clear.ps1
```

## Contacts

The library is created and maintained by:
- **Sergey Seroukhov**
- **Michael Seroukhov**
