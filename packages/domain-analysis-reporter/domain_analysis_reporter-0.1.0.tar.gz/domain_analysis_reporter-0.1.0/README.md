# Domain Analysis Reporter

The **Domain Analysis Reporter** is a Python script designed to analyze a list of domains and generate detailed reports, including IP resolution, hostname resolution, and redirection URLs. The output is saved in both Markdown (`.md`) and CSV formats for easy sharing and analysis.

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

| Domain       | IP Address     | Hostname             | Redirected URL         |
|--------------|----------------|----------------------|------------------------|
| example.com  | 93.184.216.34  | example-host.com     | https://example.com    |


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
   * Resolves the IP address to a hostname (if available).  
   * Captures any redirect URL.  
5. **Report Generation**:  
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
File: website_domains.txt
Output: website_domains_resolved
Verbose mode enabled!
2025-01-26-12:30:00  
* [example.com](https://example.com) https://example.com IP [93.184.216.34] HOST [example-host.com]
```

### **Markdown Report**

```markdown
| Domain       | IP Address     | Hostname             | Redirected URL         |
|--------------|----------------|----------------------|------------------------|
| example.com  | 93.184.216.34  | example-host.com     | https://example.com    |
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

This project is licensed under the Creative Commons License. See the [CC License](LICENSE) file for details.

---

## **Contributions**

Contributions are welcome\! If you find any issues or have suggestions for improvements, feel free to open a pull request or file an issue in the repository.

---

## **Contact**

For questions or support, contact:

* **Author**: \[Ben Thomas\]
* **Email**: <ben@smallercircle.com>
