from importer.crawler import discover_srd_links


links = discover_srd_links()

print()
print("Found", len(links), "SRD links")
print()

for link in links[:25]:
    print(link)