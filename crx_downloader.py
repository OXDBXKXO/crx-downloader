#!/usr/bin/env python3
"""Download a Chrome extension .crx file given its Chrome Web Store URL."""

import argparse
import re
import struct
import sys
import requests

# Matches the extension name and 32-char extension ID from Chrome Web Store URLs
CHROME_URL_PATTERN = re.compile(
    r"^https?://chromewebstore\.google\.com/detail/(?P<ext_name>[^/]+)/(?P<ext_id>[a-z]{32})(?=[/#?]|$)"
)

# Chrome version to spoof in the download request
# If you encounter issues, try updating this to a more recent stable version of Chrome.
# See: https://chromereleases.googleblog.com/ for the latest stable version.
CHROME_VERSION = "145.0.0.0"

def extract_extension_info(url: str) -> tuple[str, str] | None:
    match = CHROME_URL_PATTERN.search(url)
    if match:
        return match.group("ext_name"), match.group("ext_id")
    return None


def get_zip_offset(header: bytes) -> int:
    """Parse the CRX header to determine the offset where the ZIP archive starts."""
    if not header or len(header) < 16:
        raise ValueError("Invalid CRX file: header too short.")
    
    # Unpack the first 8 bytes using little-endian ('<'):
    # '4s' extracts 4 bytes for the magic number (should be 'Cr24')
    # 'I' extracts a 4-byte unsigned integer for the format version
    magic, version = struct.unpack('<4sI', header[:8])
    if magic != b'Cr24':
        raise ValueError("Not a valid CRX file: magic number mismatch.")
        
    if version == 2:
        # See: https://web.archive.org/web/20251203073424/https://www.dre.vanderbilt.edu/~schmidt/android/android-4.0/external/chromium/chrome/common/extensions/docs/crx.html
        pubkey_len, sig_len = struct.unpack('<II', header[8:16])
        return 16 + pubkey_len + sig_len
    elif version == 3:
        # See: https://web.archive.org/web/20260327102920/https://chromium.googlesource.com/chromium/src/+/refs/tags/148.0.7757.1/components/crx_file/crx3.proto
        # Version 3 is at least 12 bytes header + pubkey length.
        # Specifically, buf[8] to buf[11] is the header size.
        header_size = struct.unpack('<I', header[8:12])[0]
        return 12 + header_size
    else:
        raise ValueError(f"Unsupported CRX version: {version}.")


def download_extension(ext_name: str, ext_id: str, fmt: str, output: str | None = None):
    # This is the CRX download endpoint Google exposes for update checks.
    crx_url = (
        f"https://clients2.google.com/service/update2/crx"
        f"?response=redirect"
        f"&prodversion={CHROME_VERSION}"
        f"&acceptformat=crx2,crx3"
        f"&x=id%3D{ext_id}%26uc"
    )

    filename = output or f"{ext_name}.{fmt}"
    print(f"Downloading {ext_name} ({ext_id}) from Google CRX endpoint...")

    resp = requests.get(crx_url, stream=True)
    resp.raise_for_status()

    with open(filename, "wb") as f:
        # Write the file in 8KB chunks to keep memory usage low, 
        # even for very large extensions.
        if fmt == "crx":
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        elif fmt == "zip":
            # We need to strip the CRX header to extract the ZIP archive.
            try:
                header = resp.raw.read(16)
                zip_start_offset = get_zip_offset(header)
                # We already read 16 bytes. Read the remaining offset bytes.
                resp.raw.read(zip_start_offset - 16)
            except ValueError as e:
                print(f"Error: {e}")
                sys.exit(1)
            
            # Write the rest of the stream (the zip data)
            while True:
                chunk = resp.raw.read(8192)
                if not chunk:
                    break
                f.write(chunk)

    print(f"Saved to {filename}")


def main():
    parser = argparse.ArgumentParser(description="Download a Chrome extension from the Chrome Web Store.")
    parser.add_argument("url", help="Chrome Web Store URL of the extension")
    parser.add_argument("-f", "--format", choices=["crx", "zip"], default="crx", help="Target output format (crx or zip, defaults to crx)")
    parser.add_argument("-o", "--output", help="Name of the target file (defaults to the extension name)")

    args = parser.parse_args()

    info = extract_extension_info(args.url)
    if not info:
        print("Error: could not extract extension name and ID from URL.")
        sys.exit(1)

    ext_name, ext_id = info
    download_extension(ext_name, ext_id, args.format, args.output)


if __name__ == "__main__":
    main()
