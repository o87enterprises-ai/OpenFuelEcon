#!/usr/bin/env python3
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

PUBLIC = Path(__file__).resolve().parent.parent / "public"
SITE_URL = "https://fuelecon.pages.dev"

def build_sitemap():
    urls = [
        ("/", "daily", "1.0"),
        ("/en-au/", "weekly", "0.9"),
        ("/en-ca/", "weekly", "0.9"),
        ("/en-gb/", "weekly", "0.9"),
        ("/about/", "monthly", "0.5"),
        ("/privacy/", "monthly", "0.3"),
        ("/terms/", "monthly", "0.3"),
        ("/disclosure/", "monthly", "0.3"),
        ("/contact/", "monthly", "0.4"),
    ]
    
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    
    for loc, changefreq, priority in urls:
        url = ET.SubElement(urlset, "url")
        ET.SubElement(url, "loc").text = f"{SITE_URL}{loc}"
        ET.SubElement(url, "lastmod").text = datetime.now().strftime("%Y-%m-%d")
        ET.SubElement(url, "changefreq").text = changefreq
        ET.SubElement(url, "priority").text = priority
    
    tree = ET.ElementTree(urlset)
    tree.write(PUBLIC / "sitemap.xml", encoding="utf-8", xml_declaration=True)
    print(f"✓ built public/sitemap.xml ({len(urls)} URLs)")

if __name__ == "__main__":
    build_sitemap()