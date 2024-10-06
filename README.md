
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
* -s <path>: allow user to load their own css file


## Description

### Configuration file format:

A valid YAML file with the following struture:

```
- title              # first line of config

- id: <name>
  t: <field>
  o:                 # Optional - List of options
    - <option1>
    - <option2>

  h: <description>   # Optional - Helper, description
  r: <bool>          # Optional - Required, force user to fill this element
```

You can have 4 different types of `field` that represent a
different html elemment 

```
str   : text box
file  : file input
radio : radio checkbox  (selection of 1 box  allowed)
check : normal checkbox (selection of n boxes allowed)
```

## Example Configuration File

Here’s an example of a valid YAML configuration file for `qforms`:

```yaml
- Favorite Animal Form

- id: name!
  t:  str
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

From the `example.yaml` config the following structure is created:
```
example_uploads/
├── example.csv
├── example.json
└── example_submitted_files
```


Upon a form submission, a JSON file is generated with the responses collected from the form. 





## Dependencies 

FIXME 

Make sure you have [jjcli](https://pypi.org/project/jjcli) module instaled, you can install it by:
```
pip install jjcli
```
waitress
