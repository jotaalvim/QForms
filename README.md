
## QForms

Quick Forms, `qforms`, is a local tool for generating forms similar to Google Forms. It allows you to quickly create personal or custom forms **without relying on proprietary third-party services**, offering a simple and flexible solution for form generation and data collection. Perfect for those who value privacy and control over their data.


## Synopsis

To start the server do:

```
qforms [options] [config.yaml]
```

### Options

* -h : this help
* -c : export to csv
* -d <domain> : server host = domain (def: localhost) 
* -s <path>: allow user to load their own css style


## Description

### Configuration file format:

A valid YAML file with the following struture:

```
- title              # first line of config

- id: <name>
  t: <field>         # Type - indicates the html element 
  o:                 # Options - List of options 
    - <option1>
    - <option2>

  h: <description>   # Helper - provide a description
  r: <bool>          # Required - force user to fill this element
```

You can have 4 different types of fields that represent a
different html elemment.

```
str   : text box
file  : file input
radio : radio checkbox  (selection of 1 box  allowed)
check : normal checkbox (selection of n boxes allowed)
```

Most settings are optional. For instance, the form creator doesn’t need to provide a helper description or specify whether a field is required. Providing a list of options only makes sense for `radio` or `check`box types. If no type is specified for an HTML element, a text box will be used as the default.


## Example Configuration File

Here’s an example of a valid YAML configuration file for `qforms`:

```yaml
- Favorite Animal Form

- id: name!
  t:  str   # this line can be ommited, the text box will be used
  as the default
  default
  h:  write first and last name here
  req: True
  
- id: gender
  t:  radio
  o:
    - masculine
    - feminine
  req: False

- id: favourite animal
  t: check
  o:
    - cat
    - cow
    - dog
    - crocodile
    - guinea pig
    - zebra
  h: Select the animal(s) you like the most!

- id: Upload file
  t: file
  h: upload a photo of the animal
  r: True
```

### Output Created

From the example.yaml configuration, the following structure is generated:

```
example_uploads/
├── example.json
└── example_submitted_files/
```

When the form is submitted, a `.json` file is created to store the collected responses. If CSV output is enabled, a `.csv` file is also generated and updated with each submission.

The example_submitted_files folder stores any uploaded files. Each file is given a unique name to avoid conflicts.


## Another example

```
- Most Simple form

- id: name

- id: date

- id: observations

- id: Payment
  t: radio
  o:
    - cash
    - bank transfer
  h: Do you plan to pay cash or bank tranfer

- id: Payment Proof
  t: file
  h: If you selected bank transfer, please upload the proof of the tranfer 


```

## Dependencies 

FIXME 

Make sure you have [jjcli](https://pypi.org/project/jjcli) module instaled, you can install it by:


dependencies = [
    "flask_ngrok",
    "flask",
    "waitress",
    "pyyaml",
    "jjcli"
]

