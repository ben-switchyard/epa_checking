"""EPA checking script for Ford Maverick models on fueleconomy.gov."""

import argparse
import os
import smtplib
import sys
import xml.etree.ElementTree as ET
from email.message import EmailMessage

import requests

BASE_URL = "https://www.fueleconomy.gov/ws/rest/vehicle"


def fetch_xml(url: str, params: dict | None = None) -> ET.Element:
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    return ET.fromstring(response.text)


def parse_menu_text(root: ET.Element) -> list[str]:
    return [item.text for item in root.findall('.//menuItem/text') if item.text]


def list_models(year: str, make: str) -> list[str]:
    root = fetch_xml(f"{BASE_URL}/menu/model", params={"year": year, "make": make})
    return parse_menu_text(root)


def choose_maverick_model(models: list[str], prefer_hybrid: bool = True) -> tuple[str | None, list[str]]:
    candidates = [model for model in models if "maverick" in model.lower()]
    hybrids = [model for model in candidates if "hev" in model.lower() or "hybrid" in model.lower()]

    if prefer_hybrid and hybrids:
        return hybrids[0], hybrids
    if candidates:
        return candidates[0], candidates
    return None, []


def get_option_id(year: str, make: str, model: str) -> str | None:
    root = fetch_xml(f"{BASE_URL}/menu/options", params={"year": year, "make": make, "model": model})
    option_values = [item.text for item in root.findall('.//menuItem/value') if item.text]
    return option_values[0] if option_values else None


def fetch_vehicle_data(vehicle_id: str) -> dict[str, str]:
    root = fetch_xml(f"{BASE_URL}/{vehicle_id}")
    return {child.tag: child.text or "" for child in root}


def build_email_body(vehicle_data: dict[str, str], model_list: list[str]) -> tuple[str, str]:
    lines = [f"EPA check for {vehicle_data.get('make')} {vehicle_data.get('model')} ({vehicle_data.get('year')})", ""]
    lines += [f"Transmission: {vehicle_data.get('trany')}"]
    lines += [f"City MPG: {vehicle_data.get('city08')}"]
    lines += [f"Highway MPG: {vehicle_data.get('highway08')}"]
    lines += [f"Combined MPG: {vehicle_data.get('comb08')}", ""]
    lines += ["Matching Maverick models found:", *model_list]
    body = "\n".join(lines)
    subject = f"EPA alert: {vehicle_data.get('make')} {vehicle_data.get('model')} ({vehicle_data.get('year')})"
    return subject, body


def send_notification(
    smtp_server: str,
    smtp_port: int,
    sender: str,
    password: str,
    recipients: list[str],
    subject: str,
    body: str,
) -> None:
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message.set_content(body)

    with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as conn:
        conn.ehlo()
        conn.starttls()
        conn.login(sender, password)
        conn.send_message(message)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check fueleconomy.gov for Ford Maverick EPA data.")
    parser.add_argument("--year", default="2022", help="Model year to check")
    parser.add_argument("--make", default="Ford", help="Vehicle make to check")
    parser.add_argument("--keyword", default="Maverick", help="Model keyword to search for")
    parser.add_argument(
        "--no-hybrid-fallback",
        action="store_true",
        help="Only accept HEV/hybrid Maverick models; do not fall back to non-hybrid Mavericks.",
    )
    parser.add_argument("--email-to", nargs="+", default=[], help="Send a notification email to these addresses")
    parser.add_argument("--smtp-server", default="smtp.gmail.com", help="SMTP server for sending email")
    parser.add_argument("--smtp-port", type=int, default=587, help="SMTP port for sending email")
    parser.add_argument("--smtp-user", default=os.environ.get("EPA_EMAIL_FROM"), help="SMTP login user/email")
    parser.add_argument("--password", default=os.environ.get("EPA_EMAIL_PASSWORD"), help="SMTP login password")
    parser.add_argument("--verbose", action="store_true", help="Print extra diagnostic output")

    args = parser.parse_args()

    try:
        all_models = list_models(args.year, args.make)
    except Exception as exc:
        print(f"Failed to fetch model list: {exc}", file=sys.stderr)
        return 1

    matching_models = [model for model in all_models if args.keyword.lower() in model.lower()]
    if not matching_models:
        print(f"No models found for {args.make} {args.year} containing '{args.keyword}'.")
        return 0

    if args.verbose:
        print("Found matching models:")
        for model in matching_models:
            print(f"  - {model}")

    model, candidates = choose_maverick_model(matching_models, prefer_hybrid=not args.no_hybrid_fallback)
    if not model:
        print("No Maverick model matched the search criteria.")
        return 0

    if args.verbose:
        print(f"Selected model: {model}")

    option_id = get_option_id(args.year, args.make, model)
    if not option_id:
        print(f"No vehicle option ID found for model '{model}'.")
        return 0

    try:
        vehicle_data = fetch_vehicle_data(option_id)
    except Exception as exc:
        print(f"Failed to fetch vehicle details: {exc}", file=sys.stderr)
        return 1

    print("EPA check result")
    print("--------------")
    print(f"Model: {vehicle_data.get('make')} {vehicle_data.get('model')} ({vehicle_data.get('year')})")
    print(f"Transmission: {vehicle_data.get('trany')}")
    print(f"City MPG: {vehicle_data.get('city08')}")
    print(f"Highway MPG: {vehicle_data.get('highway08')}")
    print(f"Combined MPG: {vehicle_data.get('comb08')}")
    print("")
    print("Matching Maverick models:")
    for model_text in candidates:
        print(f"  - {model_text}")

    if args.email_to:
        if not args.smtp_user or not args.password:
            print("Email notification requested, but SMTP user or password is not configured.", file=sys.stderr)
            return 1

        subject, body = build_email_body(vehicle_data, candidates)
        send_notification(
            args.smtp_server,
            args.smtp_port,
            args.smtp_user,
            args.password,
            args.email_to,
            subject,
            body,
        )
        print(f"Notification sent to: {', '.join(args.email_to)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
