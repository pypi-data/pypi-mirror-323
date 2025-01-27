import argparse
import os
import re
import socket
import requests
from datetime import datetime
import csv

def check_file(file_path):
    # Check if the file exists
    if not os.path.isfile(file_path):
        return False

    # Check if the file is not empty
    if os.path.getsize(file_path) == 0:
        return False

    return True

# Function to validate the domain name
def validate_domain(domain):
    # Regular expression for validating a domain name
    domain_regex = re.compile(
        r"^(?!-)(([A-Za-z0-9-]{1,63})\.)+[A-Za-z]{2,}$"
    )
    return bool(domain_regex.match(domain))

# Function to resolve domain to an IP address
def resolve_domain(domain):
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except socket.gaierror:
        return

import socket

# Function to resolve IP address to hostname
def resolve_ip(ip):
    try:
        ip_host = socket.gethostbyaddr(ip)
        return ip_host[0]
    except Exception:
        return

# Function to request domain website, resolving redirects
def get_redirect_url(domain):
    try:
        r = requests.head('http://' + domain, allow_redirects=True, timeout=5)
        return r.url
    except Exception:
        return


def main():
    # Create the argument parser
    parser = argparse.ArgumentParser(description="A script to demonstrate command-line argument parsing.")

    # Add arguments
    parser.add_argument("-f", "--file", type=str, help="File name for list of domain to analyse. One domain per line.", required=True)
    parser.add_argument("-o", "--output", type=str, help="File name for storing the domain results. Two files, CSV and text.", required=False)
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode")

    # Parse the arguments
    args = parser.parse_args()

    # Access the arguments
    print(f"File: {args.file}")
    print(f"Output: {args.output}")
    if args.verbose:
        print("Verbose mode enabled!")
    
    # Get the current timestamp
    timestamp = datetime.now()

    # Format it into a string
    formatted_timestamp = timestamp.strftime("%Y-%m-%d-%H:%M:%S")

    print(formatted_timestamp)

    # Validate input file
    default_input_file = "website_domains.txt"  # Replace with your desired file path

    input_file = args.file
    if not check_file(input_file):
        input_file = default_input_file
        if not check_file(input_file):
            print("Invalid file name: no such file")
            exit    

    # Define output file names
    output_file_name = None
    if args.output:
        output_file_name = args.output
    else:
        output_file_name = input_file

    # Trim off filename extensions which will be reset
    output_file_name = os.path.splitext(output_file_name)[0] + "_resolved"
    output_file_csv = output_file_name + ".csv" # CSV
    output_file = output_file_name + ".md" # Markdown

    # Load list of domains from file
    with open(input_file, "r") as file:
        domains = file.read().splitlines()

    # Storage for CSV data
    DEFAULT_DOMAIN_DATA = [None, None, None, None]
    data = [ [ "Domain", "IP", "Host", "Redirected URL" ] ]
    domain_data = DEFAULT_DOMAIN_DATA.copy()
    previous_data = None

    # Load previous data if it exists
    if check_file(output_file_csv):
        # Open and read the CSV file
        with open(output_file_csv, mode="r") as file:
            previous_data = list(csv.reader(file))

    # Open the output file for writing
    with open(output_file, "w") as file:

        # Write the Markdown header row
        file.write("| " + " | ".join(data[0]) + " |\n")
        file.write("|" + "|".join(["-" * len(column) for column in data[0]]) + "|\n")
        
        for domain in domains:
            if previous_data:
                # Loop through any previous results for matches
                for row in previous_data:
                    # Check for matches
                    if row[0] == domain:
                        # Populate empty domain_data with the row
                        domain_data = row
                        if args.verbose:
                            print(f"Previous results found for {domain}")
                        # Leave the previous_data lookup loop
                        break
            # Skip domains analysis if we have a match
            if domain_data[0]:
                data.append(domain_data)
                domain_data = DEFAULT_DOMAIN_DATA.copy()
                continue

            # If not a previous match and the domain is valid
            if validate_domain(domain):
                domain_ip = None
                ip_domain = None
                domain_url = None
                if domain_data[0]:
                    domain_ip = domain_data[1]
                    ip_domain = domain_data[2]
                    domain_url = domain_data[3]
                else:
                    domain_ip = resolve_domain(domain)
                    if domain_ip:
                        domain_url = get_redirect_url(domain)
                        ip_domain = resolve_ip(domain_ip)

                if args.verbose:
                    print(f"* [{domain}]({domain_url}) {domain_url} IP [{domain_ip}] HOST [{ip_domain}]")

                domain_data = [ domain, domain_ip, ip_domain, domain_url ]                

            else:
                domain_data[0] = domain
                if args.verbose:
                    print(f"\nEncountered invalid domain!! [{domain}]\n")
            
            data.append(domain_data)
            domain_data = DEFAULT_DOMAIN_DATA.copy()
        
        # Write the Markdown data rows
        # for row in data[1:]:
        #     print(row)
        #     file.write("| " + " | ".join(row) + " |\n")

    # Write the data to the CSV file
    with open(output_file_csv, mode="w", newline="") as file:
        writer = csv.writer(file)
        
        # Write each array as a row in the CSV
        writer.writerows(data)
    if args.verbose:
        print(f"RESULTS: {output_file} and {output_file_csv}")

if __name__ == "__main__":
    main()
