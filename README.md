# QForms

**QuickForms** (`qforms`) is a local form generation tool designed as an alternative to proprietary services like Google Forms. It empowers users to maintain complete control over their data while providing a simple, command-line interface for creating forms.

This tool comes to me as quite useful because of how simple and quick it is to make a form. One of the difficulties that appear is sharing the form’s link with other people. We recommend using ngrok so that other people can access your local machine. Ngrok used to be an embedded feature in qforms, but it stopped working for some reason and is no longer included.


This tool is in a very early stage, so we always welcome contributions to the project!

## Features

- Keep your data local - no third-party services involved
- Generate forms from simple YAML configuration files
- Automatically creates a web form accessible via browser
- Support for file submissions
- JSON and CSV output options


## Installation

Install QForms using pip:

```bash
pip install qforms
```

## Quick Start

1. Create a YAML configuration file (see examples below)
2. Start the server:

```bash
qforms [options] [config.yaml]
```

3. Open your browser and navigate to the displayed URL
4. Fill out and submit your form
5. View collected data in the generated output files

## Command Line Options

| Option | Description |
|--------|-------------|
| `-h` | Display help message |
| `-c` | Export submissions to CSV format |
| `-d <domain>` | Set server host domain (default: localhost) |
| `-s <path>` | Load custom CSS stylesheet for form styling |

## Configuration File Format

QForms uses YAML configuration files with the following structure:

```yaml
- title              # Form title (first line of config)

- id: <field_name>   # Unique identifier for the field 
  t: <field_type>    # Type - specifies the HTML input element  (Optinoal, textbox is the default
  o:                 # Options - list of choices (for radio/checkbox)
    - <option1>
    - <option2>
  h: <description>   # Helper - descriptive text for the field  (Optional)
  r: <boolean>       # Required - whether field must be filled  (Optional)
```

Helper descriptions (`h`) and required flags (`r`) are optional. If no type is specified, a text input (`str`) is used by default. Only`radio` and `check` types require the options (`o`) list


### Field Types

QForms supports four field types that correspond to different HTML input elements:

| Type | HTML Element | Description | Selection |
|------|-------------|-------------|-----------|
| `str` | Text input | Single-line text box | N/A |
| `file` | File input | File upload field | N/A |
| `radio` | Radio buttons | Multiple choice (single selection) | 1 option |
| `check` | Checkboxes | Multiple choice (multiple selections) | N options |



## Example Configuration File

Here’s an example of a valid YAML configuration file for `qforms`

A minimal form for payment processing:

```yaml
- Payment Information

- id: name
  h: Full name as it appears on your ID
  r: true

- id: date
  h: Transaction date (YYYY-MM-DD)
  r: true

- id: observations
  h: Additional notes or comments

- id: Payment Method
  t: radio
  o:
    - cash
    - bank transfer
  h: How do you plan to pay?
  r: true

- id: Payment Proof
  t: file
  h: If you selected bank transfer, please upload proof of transfer
```

or a more causal form:

```yaml
- Favorite Animal Form

- id: name!
  t:  str   # this line can be ommited, the text box will be used as the default
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

- id: animal photo
  t: file
  h: Upload a photo of your favorite animal
  r: false
```

## Data Storage and Output

Here's an example of what running the first example looks like from the point of view of a user:

![example1](https://raw.githubusercontent.com/jotaalvim/QForms/refs/heads/master/assets/form1.png?token=GHSAT0AAAAAADLLFCCTYKNXFNNJ3MKCYW6M2GZLQ5Q)

Here's the confirmation menu after submission
![example2](https://raw.githubusercontent.com/jotaalvim/QForms/refs/heads/master/assets/form2.png?token=GHSAT0AAAAAADLLFCCSBF6D746ZGOUZKFB42GZLQXQ)


### Generated File Structure

When you run QForms with a configuration file, the following structure is automatically created:

```
<config_name>_uploads/
├── <config_name>.json      # JSON format responses
├── <config_name>.csv       # CSV format (when -c flag is used)
└── <config_name>_submitted_files/  # Uploaded files directory
    ├── file1_unique_hash.ext
    └── file2_unique_hash.ext
```

## Dependencies

QForms requires the following packages (automatically installed with pip):
- **flask**: Web framework for serving forms
- **waitress**: Production WSGI server
- **pyyaml**: YAML configuration file parsing
- **jjcli**: Command-line interface utilities



