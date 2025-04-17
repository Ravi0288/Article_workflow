from step4.update_journals import update_journal_model

# Journal Updater Documentation

## Overview

This documentation provides instructions on how to run the journal updater script. The script updates the journal model by pulling journal records from alma that were created or updated since a given date. This code is intended to run regularly through a cron job. This documentation describes how to run it manually through the django shell.

## Prerequisites

Activate the virtual environment and initiate a Django shell before running the journal updater.

```bash
source venv/bin/activate
python manage.py shell
```

## Running the Journal Updater via SRU

To run the journal updater via SRU, follow these steps:

1. **Import the necessary modules:**

    ```python
    from model.journal import Journal
    from step4.update_journals import update_journal_model
    ```

2. **Run the updater function:**

    ```python
    date = Journal.objects.filter(collection_status__in=('accepted', 'rejected')).latest('last_updated').last_updated
    update_journal_model(date)
    ```

This will update the `Journal` model with the latest data based on the `last_updated` field.

## Running the Journal Updater from a File

The `update_journal_model()` function is intended for small, regular updates to the journal model.
The Alma SRU service has a limit of 10K records per request, so the `update_journal_model()` function
is not designed to handle requests that involve more than 10K records. For large-scale updates,
or initial model populations, use the `update_journal_model_from_file()` function with a marcxml
file containing journal records. Ensure that all records in the file have a valid, 24 character
leader, otherwise `pymarc`, the package used to parse marcxml records, will fail to parse the file.

To run the updater function from a file, follow these steps:
1. **Import the necessary modules:**

    ```python
    from model.journal import Journal
    from step4.update_journals import update_journal_model_from_file
    ```
2. **Run the updater function:**

    ```python
    update_journal_model_from_file('path/to/your/file.marcxml')
    ```

## Notes

- You can also pass a specific date to the `update_journal_model()` function to update the journal model with records created or updated since that date. This can either be a `datetime.datetime` object, or a string in the format `YYYYMMDD`. For example:
   ```python
   update_journal_model('20250101')
   ```
- On July 11th, 2023, over 14K journal records were updated on Alma. Since the Alma SRU service will only
accommodate requests of up to 10K records, the `update_journal_model()` function will not be able to handle 
requests for dates on or after July 11th, 2023. For these requests, use the `update_journal_model_from_file()` 
function with a marcxml file containing journal records.