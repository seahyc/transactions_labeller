import os
import sys
import argparse
import pandas as pd
from ocbc_dbs_statement_parser import parse_bank_statement
from termcolor import colored
import getch  # Use getch to capture individual keypresses
from typing import Optional, Tuple, List, Literal

# Define categories as a list without numbering
categories = [
    'Income - Salary',
    'Income - Repayments',
    'Income - Bank Interests',
    'Personal Expenses - Food',
    'Personal Expenses - Transport',
    'Personal Expenses - Phone Bills/ Online Services',
    "Personal Expenses - Parents' Allowance",
    'Personal Expenses - Personal Development',
    'Personal Expenses - Retail',
    'Personal Expenses - Donations/ Gifts',
    'Personal Expenses - Gym/Sports',
    'Personal Expenses - Medical Bills',
    'Personal Expenses - Entertainment',
    'Personal Expenses - Personal Overseas Travel',
    'Personal Expenses - Local Cash Expenditure',
    'Personal Expenses - Investment Fees',
    'Personal Expenses - Insurance Premiums/ Bills',
    'Personal Expenses - Housing',
    'Company Expenses - Company Travel',
    'Company Expenses - Company Software Subscriptions',
    'Others'
]

def colorize_category(category_name: str, highlight: bool = False, match_text: Optional[str] = None) -> str:
    """Add color to categories based on their parent type and match typed input."""
    parent, subcategory = category_name.split(' - ') if ' - ' in category_name else ('Others', category_name)
    attrs: List[Literal['bold', 'underline', 'dark', 'blink']] = []

    # Determine the base color based on the parent category 
    bg_color = None
    if parent == "Income":
        base_color = 'green'
    elif parent == "Personal Expenses":
        base_color = 'yellow'
    elif parent == "Company Expenses":
        base_color = 'cyan'
    else:
        base_color = 'white'
        
    if highlight:
        bg_color = 'on_red'

    # Highlight matched text within the subcategory
    if match_text and match_text.lower() in subcategory.lower():
        start_index = subcategory.lower().index(match_text.lower())
        end_index = start_index + len(match_text)
        highlighted_subcategory = (
            colored(subcategory[:start_index], base_color, bg_color, attrs=attrs) +
            colored(subcategory[start_index:end_index], base_color, bg_color, attrs=attrs + ['underline', 'bold']) +
            colored(subcategory[end_index:], base_color, bg_color, attrs=attrs)
        )
        return f"{colored(parent + ' - ', base_color, bg_color, attrs=attrs)}{highlighted_subcategory}" if parent != 'Others' else highlighted_subcategory

    # If no match or highlight, return the whole category colored
    return colored(category_name, base_color, bg_color, attrs=attrs)

def compute_best_match(match_text: str) -> Optional[int]:
    """Compute the best matching category index based on match_text."""
    best_match_index: Optional[int] = None
    best_match_score: int = -1

    for i, category in enumerate(categories):
        subcategory = category.split(' - ')[1] if ' - ' in category else category

        # Compute match score: number of contiguous characters and position (left-aligned is better)
        if match_text and match_text.lower() in subcategory.lower():
            start_index = subcategory.lower().find(match_text.lower())
            contiguous_chars = len(match_text)
            score = contiguous_chars * 10 - start_index  # Prioritize by number of matches and left-alignment
            if score > best_match_score:
                best_match_index = i
                best_match_score = score

    return best_match_index

def display_categories(
    highlight_index: Optional[int] = None,
    selected_category_index: Optional[int] = None,
    match_text: str = ''
) -> Optional[int]:
    """Displays categories and highlights the one at `highlight_index`.
       If a `selected_category` exists, highlight it initially."""
    print("\nCategories:")

    for i, category in enumerate(categories):
        # Adjust colorization based on whether it's the selected category or has a match
        if selected_category_index is not None and categories[selected_category_index] == category and highlight_index is None:
            colored_category = colorize_category(category, highlight=True, match_text=match_text)
        elif highlight_index is not None and i == highlight_index:
            colored_category = colorize_category(category, highlight=True, match_text=match_text)
        else:
            colored_category = colorize_category(category, match_text=match_text)
        print(f"- {colored_category}")

    print(colored("[q] Quit", 'red'))

def display_transaction(index: int, transactions_df: pd.DataFrame) -> None:
    """Display the transaction with index and show progress."""
    # Only clear the part of the screen that needs updating
    os.system('clear')  # Clear the screen to avoid showing previous transactions
    transaction = transactions_df.iloc[index]
    total_transactions = len(transactions_df)
    progress = (index + 1) / total_transactions * 100

    # Check if Withdrawal, Deposit, or Amount is available and show all that are not null
    details = {
        'Date': transaction.get('Date', 'N/A'),
        'Description': transaction.get('Description', 'N/A')
    }
    
    if pd.notna(transaction.get('Withdrawal')):
        details['Withdrawal'] = f"{transaction['Withdrawal']:.2f}"
    if pd.notna(transaction.get('Deposit')):
        details['Deposit'] = f"{transaction['Deposit']:.2f}"
    if pd.notna(transaction.get('Amount')):
        details['Amount'] = f"{transaction['Amount']:.2f}"
    
    # If none are present, set Amount to 'N/A'
    if not any(pd.notna(transaction.get(key)) for key in ['Withdrawal', 'Deposit', 'Amount']):
        details['Amount'] = 'N/A'
    
    # Format output for left-aligned keys and values
    max_key_len = max(len(key) for key in list(details.keys()) + ['Transaction']) + 2
    print(f"{colored('Transaction'.ljust(max_key_len), 'light_magenta', attrs=['bold'])}: {index + 1} of {total_transactions}, {progress:.1f}%")
    for key, value in details.items():
        # Adjust the formatting to align colons
        print(f"{colored(key.ljust(max_key_len), 'light_magenta', attrs=['bold'])}: {value}")

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Label bank transactions from a PDF statement.')
    parser.add_argument('pdf_file', help='Path to the bank statement PDF file.')
    return parser.parse_args()

def validate_pdf_file(pdf_file_path: str) -> None:
    """Verify that the PDF file exists."""
    if not os.path.isfile(pdf_file_path):
        print(f"Error: The file '{pdf_file_path}' does not exist.")
        sys.exit(1)

def parse_transactions(pdf_file_path: str) -> pd.DataFrame:
    """Parse the bank statement and extract transactions."""
    try:
        parsed_data = parse_bank_statement(pdf_file_path)
    except Exception as e:
        print(f"Error parsing the bank statement: {e}")
        sys.exit(1)
    
    transactions = parsed_data.get('transactions')
    if not transactions:
        print("No transactions found in the statement.")
        sys.exit(1)
    
    return pd.DataFrame(transactions)

def initialize_labels(num_transactions: int) -> list:
    """Initialize an empty list to store labels for each transaction."""
    return [""] * num_transactions

def handle_user_input(
    current_transaction_index: int,
    transactions_df: pd.DataFrame,
    labels: list,
    highlight_index: Optional[int],
    match_text: str
) -> Tuple[int, Optional[int], str, list]:
    """Handle the user input and return updated state."""
    display_transaction(current_transaction_index, transactions_df)

    selected_category = None
    if labels[current_transaction_index]:
        selected_category = categories.index(labels[current_transaction_index])
        highlight_index = highlight_index if highlight_index is not None else selected_category

    display_categories(highlight_index, selected_category_index=selected_category, match_text=match_text)

    print(f"Search text: {match_text}")

    keypress = getch.getch()

    new_labels = labels.copy()  # Create a copy of labels to modify

    if keypress.lower() == 'q':
        print("Exiting labeling process.")
        sys.exit(0)
    elif keypress == '\x1b':  # Handle arrow keys
        next_key = getch.getch() + getch.getch()
        if next_key == '[A':  # Up arrow
            highlight_index = (highlight_index - 1) % len(categories) if highlight_index is not None else len(categories) - 1
            match_text = ''  # Clear match text
        elif next_key == '[B':  # Down arrow
            highlight_index = (highlight_index + 1) % len(categories) if highlight_index is not None else 0
            match_text = ''  # Clear match text
        elif next_key == '[C':  # Right arrow (Next transaction)
            if current_transaction_index < len(transactions_df) - 1:
                current_transaction_index += 1
            match_text = ''  # Clear match text
            highlight_index = None
        elif next_key == '[D':  # Left arrow (Previous transaction)
            if current_transaction_index > 0:
                current_transaction_index -= 1
            match_text = ''  # Clear match text
            highlight_index = None
    elif keypress.isalpha():  # Match category by subcategory letters
        match_text += keypress
        best_match_index = compute_best_match(match_text)
        if best_match_index is not None:
            highlight_index = best_match_index
    elif keypress == '\x7f':  # Handle backspace
        match_text = match_text[:-1]  # Remove the last character
    elif keypress == '\n':  # Enter key to confirm category selection
        if highlight_index is not None:
            selected_category = categories[highlight_index]
            new_labels[current_transaction_index] = selected_category
        if current_transaction_index < len(transactions_df) - 1:
            current_transaction_index += 1
        highlight_index = None  # Reset highlight index for new transaction
        match_text = ''  # Clear match text
    else:
        print(colored("Invalid input. Use arrow keys to navigate, or type to match subcategories.", 'red'))
    
    return current_transaction_index, highlight_index, match_text, new_labels

def save_labeled_transactions(transactions_df: pd.DataFrame, labels: list, pdf_file_path: str) -> None:
    """Save labeled transactions to a CSV file."""
    # Add labels to the DataFrame
    transactions_df['Label'] = labels
    
    # Sort transactions by label frequency and transaction amount
    label_counts = transactions_df['Label'].value_counts()
    transactions_df['Label_Frequency'] = transactions_df['Label'].map(label_counts)
    
    # Determine which column to use for sorting (Withdrawal, Deposit, or Amount)
    amount_column = next((col for col in ['Withdrawal', 'Deposit', 'Amount'] if col in transactions_df.columns), None)
    
    if amount_column:
        transactions_df['Sort_Amount'] = transactions_df[amount_column].abs()
    else:
        transactions_df['Sort_Amount'] = 0  # Default to 0 if no amount column is found
    
    # Sort the DataFrame
    sorted_df = transactions_df.sort_values(
        by=['Label_Frequency', 'Sort_Amount'],
        ascending=[False, False]
    )
    
    # Remove temporary columns used for sorting
    sorted_df = sorted_df.drop(columns=['Label_Frequency', 'Sort_Amount'])
    
    # Create the output directory if it doesn't exist
    output_dir = './labelled_data'
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate the output file name
    pdf_name = os.path.splitext(os.path.basename(pdf_file_path))[0]
    output_file = os.path.join(output_dir, f"{pdf_name}_labeled.csv")
    
    # Save to CSV
    sorted_df.to_csv(output_file, index=False)
    print(f"Labeled transactions saved to: {output_file}")

def main() -> None:
    args = parse_arguments()
    pdf_file_path = args.pdf_file

    # Verify that the PDF file exists
    validate_pdf_file(pdf_file_path)

    # Parse the bank statement and extract transactions
    transactions_df = parse_transactions(pdf_file_path)

    # Initialize labels and state variables
    labels = initialize_labels(len(transactions_df))
    current_transaction_index = 0
    highlight_index = None  # No default highlight
    match_text = ''  # For matching typed characters

    while True:
        current_transaction_index, highlight_index, match_text, labels = handle_user_input(
            current_transaction_index, transactions_df, labels, highlight_index, match_text
        )
        
        # Check if all transactions have been labeled
        if all(labels):
            break
    
    # Save labeled transactions to CSV
    save_labeled_transactions(transactions_df, labels, pdf_file_path)

if __name__ == '__main__':
    main()

