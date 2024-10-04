## QForms


## QForms

Quick Forms, `qforms`, is a local tool for generating forms similar to Google Forms. It allows you to quickly create personal or custom forms **without relying on proprietary third-party services**, offering a simple and flexible solution for form generation and data collection. Perfect for those who value privacy and control over their data.


## Synopsis

To start the server do:

```
qforms [options] [config.yaml]

```

### Options
-j : export to json
-c : export to csv
-d <domain> : server host = domain (def: localhost) 
-h : this help



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

You can have 4 different types of fields that represent a
different html elemment 

```
str   -> text box
file  -> file input
radio -> radio checkbox  (selection of 1 box  allowed)
check -> normal checkbox (selection of n boxes allowed)
```


This is our standard: If a id value ends with an "!" this value is used as a key. 


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

Upon form submission, a JSON file (`conf_out.json`) is generated with the responses collected from the form. The structure of the output will reflect the field IDs and their respective user inputs.





## Dependencies 

FIXME 

Make sure you have [jjcli](https://pypi.org/project/jjcli) module instaled, you can install it by:
```
pip install jjcli
```
waitress
