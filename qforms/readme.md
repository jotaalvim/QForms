## Name

qforms - a quick local google-forms-like generator

## Synopsis

 qforms conf.yaml   -- starts a server; in the end generates a conf_out.json output
 qforms -h          -- show this help                     (FIXME(not yet))
 qforms -c          -- shown a configurarion file example (FIXME(not yet))

## Description

### Configuration file format:

A valid YAML file with the following struture:

```
configurationfile : title (field)*
field : f_str | f_file | f_radio | f_check | FIXME(outros?)
```
 
### title example:

```
- Torneio de xadrez viii edição Braga
```

### field str example:

```
- id: name
  t: str                                       ## type
  h: name to be used in final classification   ## help (optional)
  req: True                                    ## required (optional, def:False)
```

If a id value ends with an "!" this value is used as a key. Example

```
- id: name!
```
  
### field tradio example:

```
- id: sexo
  t: radio
  o:                                           ## options
     - masculino
     - feminino
  req: False                              
```

### field tcheck example:

```
- id: animais preferidos
  t: check
  o: 
     - vaca
     - gato
     - crocodilo
```
  
### field file example:
