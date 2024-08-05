import argparse
import json
import csv


def format_note_template(transaction, direction):
    """Create formatted note for transactions."""

    return (
        f"Transferred Balance\n"
        f"{transaction['fromAccountName']}→{transaction['toAccountName']}\n"
        f"{transaction.get('note', '') or ''}"
    )


def create_transaction(transaction, direction):
    """
    Create a transaction dictionary
    for a given direction (sent/received).
    """

    is_income = direction == "received"
    amount = (
        abs(transaction["amount"])
        if is_income
        else -abs(transaction["amount"])
    )
    account = (
        transaction["toAccountName"]
        if is_income
        else transaction["fromAccountName"]
    )
    title = account + (" Transfer In" if is_income else " Transfer Out")
    note = format_note_template(transaction, direction)

    return {
        "date": transaction["date"],
        "amount": amount,
        "category": "Balance Correction",
        "title": title,
        "note": note if note else "",
        "account": account,
        "income": is_income,
    }


def fix_transfers(transactions):
    updated_transactions = []

    for transaction in transactions:
        if transaction.get("type") == "transfer":
            updated_transactions.extend(
                [
                    create_transaction(transaction, "sent"),
                    create_transaction(transaction, "received"),
                ]
            )
        else:
            updated_transactions.append(transaction)

    return updated_transactions


def get_first_date(transactions):
    for transaction in transactions:
        if "date" in transaction:
            return transaction["date"]
    print("Cannot find the first transaction date")
    return None


def add_starting_balance(transactions, accounts):
    date = get_first_date(transactions)

    if not date:
        return transactions

    for account in accounts:
        balance_note = (
            f"Updated Total Balance\n{account['bankName']}: "
            f"{account['amount']}"
        )
        balance_correction_transaction = {
            "date": date,
            "amount": account["amount"],
            "category": "Balance Correction",
            "title": "",
            "note": balance_note,
            "account": account["bankName"],
            "income": True,
        }
        transactions.append(balance_correction_transaction)

    return transactions


def load_json_file(filepath):
    try:
        with open(filepath, "r") as file:
            data = json.load(file)
            print("Successfully loaded the JSON file")
            return data
    except FileNotFoundError:
        print(f"Error: The file {filepath} does not exist.")
    except json.JSONDecodeError:
        print(f"Error: The file {filepath} is not a valid JSON file.")
    return None


def adjust_amount(data_list):
    for data in data_list:
        if data.get("type") == "expense":
            data["amount"] = -abs(data.get("amount", 0))
        elif data.get("type") == "income":
            data["amount"] = abs(data.get("amount", 0))
    return data_list


def adjust_income(data_list):
    for data in data_list:
        if data.get("type") == "expense":
            data["income"] = False
        elif data.get("type") == "income":
            data["income"] = True
    return data_list


def print_pretty_json(json_data):
    print(json.dumps(json_data, indent=4))


def map_ids_to_names(data_list, id_field, name_field):
    return {item[id_field]: item[name_field] for item in data_list}


def add_names_to_transactions(
    transactions, id_to_name_map, transaction_field, name_field
):
    for transaction in transactions:
        if transaction.get(transaction_field) is not None:
            transaction[name_field] = id_to_name_map.get(
                transaction[transaction_field], "Unknown"
            )
    return transactions


def write_to_csv(filepath, transactions, fields):
    with open(filepath, "w", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(fields)
        for transaction in transactions:
            csv_writer.writerow(
                [transaction.get(field, "") for field in fields]
            )


def main():
    parser = argparse.ArgumentParser(
        description="Process and convert JSON transactions to CSV"
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        type=str,
        help="Path to the input JSON file",
    )
    args = parser.parse_args()

    data = load_json_file(args.input)
    if data is None:
        return

    transactions = data.get("expenses", [])
    accounts = data.get("accounts", [])
    categories = data.get("categories", [])

    account_id_to_name = map_ids_to_names(accounts, "superId", "bankName")
    category_id_to_name = map_ids_to_names(categories, "superId", "name")

    transactions = add_names_to_transactions(
        transactions, account_id_to_name, "accountId", "account"
    )
    transactions = add_names_to_transactions(
        transactions, category_id_to_name, "categoryId", "category"
    )
    transactions = add_names_to_transactions(
        transactions, account_id_to_name, "fromAccountId", "fromAccountName"
    )
    transactions = add_names_to_transactions(
        transactions, account_id_to_name, "toAccountId", "toAccountName"
    )

    for transaction in transactions:
        transaction["date"] = transaction.pop("time", None)
        transaction["amount"] = transaction.pop("currency", None)
        transaction["title"] = transaction.pop("name", None)
        transaction["note"] = transaction.pop("description", "")

    transactions = adjust_amount(transactions)
    transactions = adjust_income(transactions)
    transactions = add_starting_balance(transactions, accounts)
    transactions = fix_transfers(transactions)

    fields = [
        "date",
        "amount",
        "category",
        "title",
        "note",
        "account",
        "income",
    ]

    csv_output_path = "./paisa_backup_converted.csv"
    write_to_csv(csv_output_path, transactions, fields)
    print(f"CSV file has been written to {csv_output_path}")


if __name__ == "__main__":
    main()
