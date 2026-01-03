#!/usr/bin/env python3
"""
Script to extract URLs from sitemap and run the RAG pipeline
"""
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse

def extract_urls_from_sitemap(sitemap_url):
    """Extract all URLs from a sitemap XML."""
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()

        root = ET.fromstring(response.content)

        # Handle both regular sitemap and sitemap index
        urls = []

        # Default namespace for sitemap
        namespace = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        # Find all URL elements
        for url_elem in root.findall('sm:url', namespace):
            loc_elem = url_elem.find('sm:loc', namespace)
            if loc_elem is not None:
                urls.append(loc_elem.text)

        # Also look for sitemap references (in case it's a sitemap index)
        sitemap_namespace = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        for sitemap_elem in root.findall('sm:sitemap', sitemap_namespace):
            loc_elem = sitemap_elem.find('sm:loc', sitemap_namespace)
            if loc_elem is not None:
                # For now, just return the main URLs from the primary sitemap
                continue

        return urls
    except Exception as e:
        print(f"Error parsing sitemap: {e}")
        return []

if __name__ == "__main__":
    sitemap_url = "https://physical-ai-and-humanoid-robotics-rho.vercel.app/sitemap.xml"
    urls = extract_urls_from_sitemap(sitemap_url)

    print(f"Found {len(urls)} URLs in sitemap:")
    for i, url in enumerate(urls, 1):
        print(f"{i:2d}. {url}")

    # Print them in a format that can be used with the command line
    print(f"\nTotal URLs: {len(urls)}")
    if urls:
        print("For command line usage:")
        print("python main.py --urls " + " ".join(f"'{url}'" for url in urls[:5]) + " --store  # First 5 URLs")
        print("... or process in batches to avoid overwhelming the system")