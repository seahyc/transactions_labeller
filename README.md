# Bank Transaction Labeler

## Overview
This project is a command-line tool for labeling bank transactions extracted from PDF statements. It allows users to categorize transactions into predefined categories, making it easier to analyze personal or company finances. This works with another module ocbc_dbs_statement_parser

## Features
- Parse bank statements from PDF files.
- Display transactions with an interactive console interface.
- Categorize transactions into various predefined categories.
- Save labeled transactions to a CSV file for further analysis.

## Requirements
- Python <3.9
- Required Python packages:
  - ocbc_dbs_statement_parser
  - pandas
  - termcolor
  - getch


## Usage
To run the application, use the following command:

```bash
python3 labeller.py <path_to_pdf_file>
```
