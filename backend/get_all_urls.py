#!/usr/bin/env python3
"""
Script to process all remaining URLs from the sitemap
"""
import requests
import xml.etree.ElementTree as ET

def get_all_sitemap_urls():
    """Get all URLs from the sitemap."""
    sitemap_url = "https://physical-ai-and-humanoid-robotics-rho.vercel.app/sitemap.xml"
    response = requests.get(sitemap_url)
    response.raise_for_status()

    root = ET.fromstring(response.content)
    namespace = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

    urls = []
    for url_elem in root.findall('sm:url', namespace):
        loc_elem = url_elem.find('sm:loc', namespace)
        if loc_elem is not None:
            urls.append(loc_elem.text)

    return urls

if __name__ == "__main__":
    all_urls = get_all_sitemap_urls()
    print(f"Total URLs found: {len(all_urls)}")
    for i, url in enumerate(all_urls, 1):
        print(f"{i:2d}. {url}")