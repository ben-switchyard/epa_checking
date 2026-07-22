# epa_checking

A simple Python utility written in Oct 2021 to query the EPA fuel economy web service and detect Ford Maverick model data. Originally built while I was waiting on my ordered 2022 Ford Maverick Hybrid. I ordered it in Aug 2021 and didn't recieve it till March 2024. There was lots of online chat about waiting for it to officially be anounced, we didn't know exactly what it would be called, and this was hoping to catch it before the news hit. 

This was built in one night and was pretty messy, but figured its a good history. 

This repository contains a script that:
- queries `fueleconomy.gov` for Ford model menu items by year
- searches for Maverick model names, including hybrid variants
- fetches detailed EPA MPG records for the selected vehicle
- optionally sends an email alert when the target vehicle is available

## Files

- `epa_checking_code.ipynb`: Original Python script for EPA checking and notification (DELETED)
- `epa_check_verbatum.py`: No changes extract from the ipynb, had Colab specific code in it.
- `epa_check.py`: main and updated Python script for EPA checking and notification
- `requirements.txt`: required dependency list

## How it works

The script uses the official EPA REST XML endpoints under `https://www.fueleconomy.gov/ws/rest/vehicle`.
It first loads the model menu for a given year and make, then filters by the configured keyword (default: `Maverick`).
If a matching model is found, it loads the vehicle option details and prints MPG values for city, highway, and combined economy.

## Usage

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the script for the default `2022 Ford` search:

```bash
python epa_check.py
```

Search a different year or make:

```bash
python epa_check.py --year 2024 --make Ford
```

Enable email notifications:

```bash
EPA_EMAIL_FROM=you@example.com EPA_EMAIL_PASSWORD=yourpassword python epa_check.py --email-to recipient@example.com
```

## Configuration

The script supports environment variables for SMTP credentials:

- `EPA_EMAIL_FROM`: email address used to log in to SMTP
- `EPA_EMAIL_PASSWORD`: SMTP account password

Command line options include:

- `--year`: model year to check (default: `2022`)
- `--make`: manufacturer name (default: `Ford`)
- `--keyword`: model keyword to search for (default: `Maverick`)
- `--email-to`: one or more recipient email addresses
- `--smtp-server`: SMTP host (default: `smtp.gmail.com`)
- `--smtp-port`: SMTP port (default: `587`)
- `--smtp-user`: SMTP login user/email
- `--password`: SMTP password
- `--verbose`: print extra debug output

## Notes

- This script is designed for demonstration and personal alerting.
- Do not commit real passwords to GitHub; use environment variables or secrets instead.
- The EPA service may change over time or may rate-limit requests.
