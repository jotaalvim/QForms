## Name

qforms is a quick local google-forms-like generator tool. 


## Synopsis

```
qforms conf.yaml   -- starts a server
qforms -h          -- show this help                     (FIXME(not yet))
qforms -c          -- shown a configurarion file example (FIXME(not yet))
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
- title

- id: <name>
  t: <field>
  o:
    - <option1>
    - <option2>

  h: <description>   # Optional
  req: <True|False>  # Optional
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
  t:  str                                  # type
  h:  write first and last name here        # help (optional)
  req: True
  
- id: gender
  t:  radio
  o:                                        # available options
    - masculine
    - feminine
  req: False                                # when False, it's optional

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
  h: upload a photo of the animal            # help
  req: True
```

### Output Created

Upon form submission, a JSON file (`conf_out.json`) is generated with the responses collected from the form. The structure of the output will reflect the field IDs and their respective user inputs.
