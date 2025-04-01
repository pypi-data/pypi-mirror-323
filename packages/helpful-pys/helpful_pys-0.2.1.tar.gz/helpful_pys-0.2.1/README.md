# Helpful Helper
A (so far) little package that contains commonly used and useful functions. Good for team morale as they say.

# About
Contents include functions for connecting to redshift and using gspread, a py library for writing and reading from google sheets. For help with what functions are available, please run `get_help()` after importing helpful-pys.

[Official pypi](https://pypi.org/project/helpful-pys/)

# Installation
To install functional-functions, you can install it using pip:
````python
pip install helpful-pys
````

Within your jupyter lab/notebook setup:
````python
from helpful_pys import helpers

helpers.get_help()
````

# Additional Prequisites
The package will install `gspread` but will require further setup to get it running. I recommend using the [gspread documentation for Authentication](https://docs.gspread.org/en/v6.1.3/oauth2.html) which will allow you to authorize the google sheets API and generate a service account key.

Don't forget the client-email in your key, it will be constantly needed to give share access to sheets for usage with gspread.

I have included a creds.py.sample file in the package to allow the user to input their personal creds to use. If there are better access/security storage policies like AWS Secrets Manager, this repo can be updated to accommodate such.

# Usage
This package is intended for usage with local py setups and local jupyter notebook/lab setups. It is not intended for production script usage.

````python
q = "select * from that_table limit 100"

result_df = helpers.query_redshift(q)
````

````python
gc = helper.gsheets_start()

workbook = gc.open_by_url('googlesheetsurlhere')

workbook.update_title("Really Cool and Helpful Workbook")

ws = test.worksheet('Sheet1')
ws.update_title("The coolest worksheet")


data_formatted = data[['id','helpful_id','cool_id']].copy()

ws.update([data_formatted.columns.values.tolist()] + data_formatted.values.tolist())
````

More [gspread example use cases](https://docs.gspread.org/en/v6.1.3/user-guide.html)