# Micro YNAB

Micro YNAB is a small SDK for the YNAB budgeting app. It provides a simple interface to interact with the YNAB API, 
allowing you to manage budgets, categories, transactions, and more.

## Features

- Manage budgets and budget settings
- Handle categories and category groups
- Work with payees and transactions
- Simple and easy-to-use interface

## Installation

To install the package, use pip:

```sh
pip install uynab
```

## Usage

### Code

Here's a basic example of how to use the SDK:

```python
from uynab.client import YNABClient

client = YNABClient(api_token="YOUR_YNAB_API_TOKEN")

# Get all budgets
budgets = client.budget.get_all_budgets()
print(budgets)
```

### Standalone

```sh
python -m uynab budget list
```

## Documentation

For detailed documentation, visit the [docs](https://ajwalkiewicz.github.io/uynab/).

## Contributing

Contributions are welcome! Please see the [contribution guidelines](https://ajwalkiewicz.github.io/uynab/contribution/) for more information.

## License

This project is licensed under the MIT License. See the [LICENSE](https://ajwalkiewicz.github.io/uynab/license/) file for details.
