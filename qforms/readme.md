qforms - quick google forms maker

## Synopsis

 qforms conf.yaml   -- in the end generates a conf_out.json output
 qforms -h          -- show this help
 qforms -c          -- shown a econfigurarion file example

## Description

### Configuration file format:

A valid YAML file with the following struture:

 configurationfile : title (field)*
 field : f_str | f_file | f_radio | f_check | FIXME(outros?)
 
### title example:

  - Torneio de xadrez viii edição Braga

### field str example:

  - id: name
    t: str 
    h: name to be used in final classification   ## optional
    req: True                                    ## optional

If a id value ends with an "!" this value is used as a key. Example

  - id: name!
  
### field tradio example:

  - id: sexo
    t: radio
    o: 
       - masculino
       - feminino
       - not provided
    h:                                           ## optional
    req: False                                   ## optional

### field tcheck example:

  - id: animais preferidos
    t: check
    o: 
       - vaca
       - gato
       - crocodilo
       - bicho pau
  
### field file example:
