# Domain Analysis Reporter

The **Domain Analysis Reporter** is a Python script designed to analyze a list of domains and generate detailed reports, including IP resolution, redirection URLs, parent domain, and domain registration information. The output is saved in both Markdown (`.md`) and CSV formats for easy sharing and analysis.

A corresponding CSV file

---

## Features

- Validate domain names using regular expressions.
- Resolve domains to IP addresses.
- Resolve IP addresses to hostnames.
- Follow and capture HTTP redirects for domains.
- Store results in:
  - **Markdown (.md)** for human-readable reports.
  - **CSV (.csv)** for structured data analysis.
- Automatically detects and avoids re-processing previously analyzed domains by loading prior results from CSV.

---

## Prerequisites

Ensure the following are installed on your system:

- **Python 3.6+**
- Required Python packages:
  - `requests`
  - `boilerpy3` - Currently unused


## **Usage**

### **Command-Line Arguments**

| Argument | Description | Required |
| ----- | ----- | ----- |
| `-f`, `--file` | Path to the input file containing domains to analyze. One domain per line. | Yes |
| `-o`, `--output` | Path to the output file (optional). Defaults to the input file name with `_resolved` suffix. | No |
| `-t`, `--time` | Expiration time in days for previous results. Defaults to 30 day. Specifiy 0 to force new analysis. | No |
| `-v`, `--verbose` | Enable verbose mode to display detailed processing information in the console. | No |

---

### **Running the Script**

#### **Example 1: Basic Usage**

```bash
python domain_analysis_reporter.py -f website_domains.txt
```

This processes the domains in `website_domains.txt` and generates:

* `website_domains_resolved.md`
* `website_domains_resolved.csv`

#### **Example 2: Specify Output File**

```bash
domain-analysis-reporter -f website_domains.txt -o custom_output
```

This generates:

* `custom_output_resolved.md`  
* `custom_output_resolved.csv`

#### **Example 3: Verbose Mode**

```bash
domain-analysis-reporter -f website_domains.txt -v
```

This displays detailed processing information in the terminal.

---

## **Input File Format**

The input file should contain one domain per line. Example:

```
example.com
google.com
invalid_domain
```

---

## **Output**

### **Markdown Report (.md)**

A table summarizing the analysis:

| Domain       | Host IPs       | Redirected URL             | Registered Domain | Registrar  | Domain Registration Date  | Domain Expiration Date  | Nameservers  | Timestamp         |
|--------------|----------------|----------------------|------------------------|
| example.com  | 93.184.216.34  | https://example.com     | example-host.com    | NAMECHEAP INC | 2022-11-14 21:49:33 | 2025-01-27 12:35:58 | 2025-11-27 21:49:33 |


### **CSV File (.csv)**

A structured file containing the same data as the Markdown report.

---

## **How It Works**

1. **File Validation**:  
   * Ensures the input file exists and is non-empty.  
2. **Domain Validation**:  
   * Validates domains using a regex pattern.  
3. **Previous Results**:  
   * If a previous `.csv` file exists for the same input, avoids re-processing matching domains.  
4. **Domain Analysis**:  
   * Resolves the domain to an IP address.
   * Captures any redirect URL.
5. **Whois Lookup**:
   * Find the domain registrar
   * Find the domain creation and expiration date
   * Find the domain nameservers
6. **Report Generation**:  
   * Saves the results in both Markdown and CSV formats.

---

## **Error Handling**

* **Invalid Domains**:  
  * Logs invalid domains in the output.  
* **Network Issues**:  
  * Skips domains if unable to resolve or retrieve data within the timeout period.

---

## **Example Output**

### **Console Output (Verbose Mode)**

```
File: domain_analysis_reporter/test/domains-test-small.txt
Output: None
Time: 30
Verbose mode enabled!
Timestamp: 2025-01-27 12:46:54
Previous [2025-01-27 12:35:58] results found for smallercircle.com
Previous [2025-01-27 12:35:58] results found for mail.smallercircle.com
Previous [2025-01-27 12:35:58] results found for ilgili.net
Previous [2025-01-27 12:35:58] results found for cchvac.us
Previous [2025-01-27 12:35:58] results found for heysay.app
Previous [2025-01-27 12:35:58] results found for dfeia-3asdf1.com
Previous [2025-01-27 12:35:58] results found for 4223.ad.gadf.ad.accountmanager.co
Previous [] results found for u7&234.a3.com
Previous [] results found for invalid.d
* [google.com](http://www.google.com/) http://www.google.com/ Domain [google.com] IPs [2607:f8b0:4023:1009::8b 2607:f8b0:4023:1009::71 2607:f8b0:4023:1009::64 2607:f8b0:4023:1009::65 142.251.116.139 142.251.116.102 142.251.116.113 142.251.116.138 142.251.116.101 142.251.116.100]
Results saved to:
        domain_analysis_reporter/test/domains-test-small_resolved.md
        domain_analysis_reporter/test/domains-test-small_resolved.csv
```

### **Markdown Report**

```markdown
| Domain | Host IPs | Redirected URL | Registered Domain | Registrar | Domain Registration Date | Domain Expiration Date | Nameservers | Timestamp |
|------|--------|--------------|-----------------|---------|------------------------|----------------------|-----------|---------|
| smallercircle.com | 190.92.190.113 | http://smallercircle.com/ | smallercircle.com | GoDaddy.com, LLC | 2002-07-09 06:43:30 | 2025-07-09 01:49:07 | NS35.DOMAINCONTROL.COM NS36.DOMAINCONTROL.COM | 2025-01-27 12:35:58 |
| mail.smallercircle.com | 190.92.190.113 | http://mail.smallercircle.com/ | smallercircle.com | GoDaddy.com, LLC | 2002-07-09 06:43:30 | 2025-07-09 01:49:07 | NS35.DOMAINCONTROL.COM NS36.DOMAINCONTROL.COM | 2025-01-27 12:35:58 |
| ilgili.net | 66.102.132.177 | http://ilgili.net/ | ilgili.net | GoDaddy.com, LLC | 2004-05-07 05:00:58 | 2026-05-07 00:00:58 | NS1.HOSTPAPA.COM NS2.HOSTPAPA.COM | 2025-01-27 12:35:58 |
| cchvac.us | 190.92.190.113 | https://cchvac.us/ | cchvac.us | GoDaddy.com, LLC | 2021-11-29 00:05:20 | 2026-11-29 00:05:20 | ns52.domaincontrol.com ns51.domaincontrol.com | 2025-01-27 12:35:58 |
| heysay.app | 190.92.190.113 | http://heysay.app/ | heysay.app | GoDaddy.com, LLC | 2022-11-14 21:49:33 | 2025-11-14 21:49:33 | ns29.domaincontrol.com ns30.domaincontrol.com | 2025-01-27 12:35:58 |
| dfeia-3asdf1.com |  |  | dfeia-3asdf1.com |  |  |  |  | 2025-01-27 12:35:58 |
| 4223.ad.gadf.ad.accountmanager.co |  |  | accountmanager.co | NAMECHEAP INC | 2012-10-16 21:52:39 | 2025-10-15 23:59:59 | dns1.supremedns.com dns2.supremedns.com dns3.supremedns.com | 2025-01-27 12:35:58 |
| u7&234.a3.com |  |  |  |  |  |  |  |  |
| invalid.d |  |  |  |  |  |  |  |  |
| google.com | 2607:f8b0:4023:1009::8b 2607:f8b0:4023:1009::71 2607:f8b0:4023:1009::64 2607:f8b0:4023:1009::65 142.251.116.139 142.251.116.102 142.251.116.113 142.251.116.138 142.251.116.101 142.251.116.100 | http://www.google.com/ | google.com | MarkMonitor, Inc. | 1997-09-15 04:00:00 | 2028-09-13 07:00:00 | NS1.GOOGLE.COM NS2.GOOGLE.COM NS3.GOOGLE.COM NS4.GOOGLE.COM | 2025-01-27 12:46:54 |
```

---

## **Development Notes**

* **Default Input File**: If no valid file is provided, the script uses `website_domains.txt` as the default.  
* **Dependencies**: The script depends on Python libraries:  
  * `os`  
  * `re`  
  * `socket`  
  * `requests`  
  * `argparse`  
  * `csv`
  * `boilerpy3`

---

## **License**

This project is licensed under the Creative Commons License. See the [CC License](https://github.com/benmathat/domain_analysis_reporter/blob/main/LICENSE "View LICENSE on GitHub") file for details.

---

## **Contributions**

Contributions are welcome\! If you find any issues or have suggestions for improvements, feel free to open a pull request or file an issue in the repository.

---

## **Contact**

For questions or support, contact:

* **Author**: Ben Thomas
* **Email**: <ben@smallercircle.com>
