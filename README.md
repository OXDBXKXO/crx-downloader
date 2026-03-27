# CRX Downloader

A simple Python script to download Chrome extensions directly from the Chrome Web Store. It can save the extension in its native `.crx` format or extract its contents as a standard `.zip` archive.

## Prerequisites

This script requires Python 3 and the `requests` library.

Install the required library using pip:

```bash
pip install requests
```

## Usage

```bash
python crx_downloader.py [-h] [-f {crx,zip}] [-o OUTPUT] url
```

### Arguments

*   `url`: **(Required)** The Chrome Web Store URL of the extension you want to download.

### Options

*   `-h`, `--help`: Show the help message and exit.
*   `-f {crx,zip}`, `--format {crx,zip}`: The target output format. You can choose to save the file as a raw Chrome Extension (`crx`) or extract it as a standard ZIP archive (`zip`). Defaults to `crx`.
*   `-o OUTPUT`, `--output OUTPUT`: Custom name for the target file. If not provided, it defaults to the extension's name extracted from the URL.

## Examples

**Download an extension as a `.crx` file (default):**

```bash
python crx_downloader.py "https://chromewebstore.google.com/detail/example-extension/abcdefghijklmnopabcdefghijklmnop"
```

**Download and extract the extension as a `.zip` archive:**

```bash
python crx_downloader.py -f zip "https://chromewebstore.google.com/detail/example-extension/abcdefghijklmnopabcdefghijklmnop"
```

**Download and save with a custom filename:**

```bash
python crx_downloader.py -o custom_name.crx "https://chromewebstore.google.com/detail/example-extension/abcdefghijklmnopabcdefghijklmnop"
```
