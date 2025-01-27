import re
import os
from pathlib import Path


class LogAnalyzer:
    """
    LogAnalyzer class to scan logs for malicious patterns.
    """

    MALICIOUS_PATTERNS = {
        "XSS": re.compile(r"<script>|onerror=|document\.cookie|<iframe>|<img\s+src=|javascript:|vbscript:|alert\(.*\)|eval\(.*\)", re.IGNORECASE),
        "SQL Injection": re.compile(r"(UNION SELECT|SELECT.*FROM|DROP TABLE|INSERT INTO|DELETE FROM|WHERE.*=.*|OR 1=1|--|;--|\" OR \"|\' OR \'|\"=\"|\'=\')", re.IGNORECASE),
        "Directory Traversal": re.compile(r"(\.\./|\.\.\\|%2e%2e%2f|%2e%2e%5c|\../|\..\\|\.\.[/\\])", re.IGNORECASE),
        "Remote Code Execution": re.compile(r"(wget|curl|bash -i|nc -e|/bin/sh|python -c|perl -e|ruby -e|php -r)", re.IGNORECASE),
        "Brute Force": re.compile(r"(Failed login attempt|Invalid password|Authorization failed|Login incorrect)", re.IGNORECASE),
        "File Upload Exploit": re.compile(r"(\.php|\.exe|\.sh|\.jsp|\.asp|\.aspx|\.bat|\.py|\.pl)$", re.IGNORECASE),
        "HTTP Method Abuse": re.compile(r"(TRACE|OPTIONS|CONNECT|HEAD|PUT|DELETE|PROPFIND|MKCOL|COPY|MOVE|LOCK|UNLOCK)", re.IGNORECASE),
    }

    BRUTE_FORCE_THRESHOLD = 50

    def __init__(self, directory):
        self.directory = directory

    def scan_log_file(self, log_file):
        """
        Scan a single log file for malicious activity patterns.

        Args:
            log_file (str): Path to the log file.

        Returns:
            dict: Detected malicious activities and their counts.
        """
        detections = {pattern_name: [] for pattern_name in self.MALICIOUS_PATTERNS}
        brute_force_count = 0

        try:
            with open(str(log_file), "r") as file:
                for line_number, line in enumerate(file, start=1):
                    for pattern_name, pattern in self.MALICIOUS_PATTERNS.items():
                        if pattern_name == "Brute Force":
                            if pattern.search(line):
                                brute_force_count += 1
                                detections[pattern_name].append((line_number, line.strip()))
                        elif pattern.search(line):
                            detections[pattern_name].append((line_number, line.strip()))

            # Check brute force threshold
            if brute_force_count >= self.BRUTE_FORCE_THRESHOLD:
                print(f"Brute force attack detected: {brute_force_count} failed attempts.")

        except FileNotFoundError:
            print(f"Log file not found: {log_file}")
        except Exception as e:
            print(f"An error occurred while scanning {log_file}: {e}")

        return detections

    def conduct_logs_analysis(self):
        """
        Recursively scan all .log files in the provided directory for malicious patterns.

        Returns:
            dict: A dictionary of log files and their detected patterns.
        """
        results = {}
        if not os.path.isdir(self.directory):
            return {"error": f"Invalid directory: {self.directory}"}

        log_files = list(Path(self.directory).rglob("*.log"))
        if not log_files:
            return {"info": "No .log files found in the directory."}

        for log_file in log_files:
            file_results = self.scan_log_file(str(log_file))
            results[log_file] = file_results

        return results
