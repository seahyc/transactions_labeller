# Bank Transaction Labeler

## Overview
This project is a command-line tool for labeling bank transactions extracted from PDF statements. It allows users to categorize transactions into predefined categories, making it easier to analyze personal or company finances.

## Features
- Parse bank statements from PDF files.
- Display transactions with an interactive console interface.
- Categorize transactions into various predefined categories.
- Save labeled transactions to a CSV file for further analysis.

## Requirements
- Python 3.x
- Required Python packages:
  - pandas
  - termcolor
  - ocbc_dbs_statement_parser
  - getch

## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the Python version:
   ```bash
   echo "3.x" > .python-version
   ```

## Usage
To run the application, use the following command:
