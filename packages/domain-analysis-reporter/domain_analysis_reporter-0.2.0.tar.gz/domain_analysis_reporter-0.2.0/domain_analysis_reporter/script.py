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

def timestamp_age_days(previous_timestamp):
    # Convert the string timestamp to a datetime object
    resolved_timestamp_dt = datetime.strptime(previous_timestamp, "%Y-%m-%d %H:%M:%S")
    # Get the current datetime
    now = datetime.now()

    # Calculate days (integer) relative to today
    days_since = (now - resolved_timestamp_dt).days
    return days_since

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
    parser = argparse.ArgumentParser(description="Analyze a file of domain names")

    # Add arguments
    parser.add_argument("-f", "--file", type=str, help="File name for list of domain to analyse. One domain per line.", required=True)
    parser.add_argument("-o", "--output", type=str, help="File name for storing the domain results. Defaults to input file name with '_resolved' appended in the present working directory.", required=False)
    parser.add_argument("-t", "--time", type=int, help="Ignore previous results older than N days and re-analyze the domain. Default 30 days. Use 0 force new analysis.", required=False, default=30)
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode")

    # Parse the arguments
    args = parser.parse_args()

    # Access the arguments
    if args.verbose:
        print(f"File: {args.file}")
        print(f"Output: {args.output}")
        print(f"Time: {args.time}")
        print("Verbose mode enabled!")

    # Uses 30 days by default
    cache_expire_days = args.time
    
    # Get the current timestamp
    timestamp = datetime.now()

    # Format it into a string
    formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    if args.verbose:
        print(f"Timestamp: {formatted_timestamp}")

    input_file = args.file
    if not check_file(input_file):
        print(f"Invalid file name [{input_file}]: no such file")
        exit

    # Define output file names
    output_file_name = input_file
    if args.output:
        output_file_name = args.output


    # Trim off filename extensions which will be reset
    if output_file_name == input_file:
        output_file_name = os.path.splitext(output_file_name)[0] + "_resolved"
    else:
        output_file_name = os.path.splitext(output_file_name)[0]
    
    output_file_csv = output_file_name + ".csv" # CSV
    output_file = output_file_name + ".md" # Markdown

    # Load list of domains from file
    with open(input_file, "r") as file:
        domains = file.read().splitlines()

    # Storage for CSV data
    DEFAULT_DOMAIN_DATA = [None, None, None, None, None ]
    data = [ [ "Domain", "IP", "Host", "Redirected URL", "Timestamp" ] ]
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
            # Setting "time" or the cache_expire_days to "0" will force all new lookups
            if cache_expire_days and previous_data:
                # Loop through any previous results for matches
                for row in previous_data:
                    # Check for matches
                    if row[0] == domain:
                        # Populate empty domain_data with the row
                        domain_data = row
                        if args.verbose:
                            print(f"Previous [{row[4]}] results found for {domain}")
                        # Leave the previous_data lookup loop
                        break

            if domain_data[4]:
                if timestamp_age_days(domain_data[4]) > cache_expire_days:
                    # Expired results fetch from previous analysis are ignored
                    domain_data = DEFAULT_DOMAIN_DATA.copy()

            # Skip domains analysis if we have a valid match
            if domain_data[0]:
                data.append(domain_data)
                domain_data = DEFAULT_DOMAIN_DATA.copy()
                continue

            # If not a previous match and the domain is valid
            if validate_domain(domain):
                domain_ip = None
                ip_domain = None
                domain_url = None
                resolved_timestamp = None
                if domain_data[0]:
                    domain_ip = domain_data[1]
                    ip_domain = domain_data[2]
                    domain_url = domain_data[3]
                    resolved_timestamp = domain_data[4]
                
                if not resolved_timestamp:
                    domain_ip = resolve_domain(domain)
                    resolved_timestamp = formatted_timestamp
                    if domain_ip:
                        domain_url = get_redirect_url(domain)
                        ip_domain = resolve_ip(domain_ip)

                if args.verbose:
                    print(f"* [{domain}]({domain_url}) {domain_url} IP [{domain_ip}] HOST [{ip_domain}]")

                domain_data = [ domain, domain_ip, ip_domain, domain_url, resolved_timestamp ]                

            else:
                domain_data[0] = domain
                if args.verbose:
                    print(f"!! Encountered invalid domain !! [{domain}]\n\n")
            
            data.append(domain_data)
            domain_data = DEFAULT_DOMAIN_DATA.copy()
        
        # Write the Markdown data rows
        for row in data[1:]:
            file.write("| " + " | ".join(str(item) if item is not None else "" for item in row) + " |\n")

    # Write the data to the CSV file
    with open(output_file_csv, mode="w", newline="") as file:
        writer = csv.writer(file)
        
        # Write each array as a row in the CSV
        writer.writerows(data)
    if args.verbose:
        print(f"Results saved to:\n\t{output_file}\n\t{output_file_csv}")

if __name__ == "__main__":
    main()
