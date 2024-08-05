# paisa-to-cashew
Convert the json backup data from the [Paisa](https://github.com/h4h13/paisa-app) expense manager to a CSV format compatible with [Cashew](https://github.com/jameskokoska/Cashew)

## Installation
```bash
git clone https://github.com/FosRexx/paisa-to-cashew
cd paisa-to-cashew
```

## Usage
```bash
python paisa-to-cashew.py --input path/to/backup.json
```
Replace `path/to/backup.json` with the path to your JSON backup file.

## Instructions
1. Go to the Paisa app, then Settings > Backup and Restore. On "Export data as JSON file" click Export and save the json file. The CSV Export will not work because it does not contain enough information.
2. Run the python script with the backup json file as an argument. As shown in [Usage](https://github.com/FosRexx/paisa-to-cashew/README.md#usage)
3. The converted CSV file will be saved in the `paisa-to-cashew` folder.
4. Launch Cashew ideally a fresh install. Then Settings and Customization > Import CSV. Select the converted csv, Import.

Note: 
- Transfers are divided into expenses and income, and so when you import the converted csv into Cashew transfers will not act as the native transfers of Cashew but will be divided into Income and Expenses with "Budget Correction" as the category. I treid to make transfers look as the native Cashew transfers as much as possible but this was the best solution I could come up with.
- Accounts starting balance are automatically imported with the time and date of the first ever transaction.
