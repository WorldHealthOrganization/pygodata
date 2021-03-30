# godata-pandas
A Python/Pandas interface for GoData

## Setup

### Editable install from source

If you want to be able to make changes to the package and maybe make a pull request:

```shell
pip install -r requirements.txt
./setup.py develop
```

## Example usage

```python
import datetime
from pygodata.api import GoDataAPI
from pygodata.util import dt_to_iso, explode_questionnaire, explode_address

api = GoDataAPI(
   api_url='https://your-godata-instance.org/api/',
   outbreak_id='9674db58-6ed9-496a-aaf8-96006c6ef3c0',
   username='test@example.org',
   password='12345',
)

# Download cases, contacts, events, and relationships from the past week
end_date = datetime.datetime.now().replace(microsecond=0)
start_date = end_date - datetime.timedelta(7)

params = {
    "where" : {
        "updatedAt": {
        "between": [
            dt_to_iso(start_date),
            dt_to_iso(end_date)
        ]
        }
    },
}

api.login()  # Get a new token. May need to be called again when the token is not valid anymore.
cases = api.get_items("cases", params=params)
contacts = api.get_items("contacts", params=params)
events = api.get_items("events", params=params)
relationships = api.get_items("relationships", params=params)


# Extract questionnaire answers as separate columns
cases = explode_questionnaire(cases)
contacts = explode_questionnaire(contacts)

# Extract address fields as separate columns (Assuming each person has no more than one address)
cases = explode_address(cases)
contacts = explode_address(contacts)

```


