#!/usr/bin/env python3
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime

PUBLIC = Path(__file__).resolve().parent.parent / "public"
SITE_URL = "https://fuelecon.pages.dev"

priority_map = {
    "/": ("daily", "1.0"),
    "/en-au/": ("weekly", "0.9"),
    "/en-ca/": ("weekly", "0.9"),
    "/en-gb/": ("weekly", "0.9"),
    "/about/": ("monthly", "0.5"),
    "/privacy/": ("monthly", "0.3"),
    "/terms/": ("monthly", "0.3"),
    "/disclosure/": ("monthly", "0.3"),
    "/contact/": ("monthly", "0.4"),
}


def path_to_url(path):
    rel_path = path.relative_to(PUBLIC)
    if rel_path.name == "index.html":
        parent = rel_path.parent
        if parent == Path("."):
            return "/"
        url_path = "/" + str(parent).replace("\\", "/") + "/"
        return url_path
    return None


def discover_urls():
    urls = []
    today = datetime.now().strftime("%Y-%m-%d")

    for index_file in PUBLIC.rglob("index.html"):
        rel_path = index_file.relative_to(PUBLIC)

        if any(part.startswith((".", "_")) for part in rel_path.parts):
            continue

        url_path = path_to_url(index_file)
        if url_path is None:
            continue

        if url_path in priority_map:
            changefreq, priority = priority_map[url_path]
        else:
            changefreq, priority = "weekly", "0.7"

        urls.append((url_path, changefreq, priority, today))

    urls.sort(key=lambda x: x[0])
    return urls


def build_sitemap():
    urls = discover_urls()

    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for loc, changefreq, priority, lastmod in urls:
        url = ET.SubElement(urlset, "url")
        ET.SubElement(url, "loc").text = f"{SITE_URL}{loc}"
        ET.SubElement(url, "lastmod").text = lastmod
        ET.SubElement(url, "changefreq").text = changefreq
        ET.SubElement(url, "priority").text = priority

    tree = ET.ElementTree(urlset)
    tree.write(PUBLIC / "sitemap.xml", encoding="utf-8", xml_declaration=True)
    print(f"✓ built public/sitemap.xml ({len(urls)} URLs)")
    for url_path, _, _, _ in urls:
        print(f"  {url_path}")


if __name__ == "__main__":
    build_sitemap()
