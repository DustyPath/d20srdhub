from importer.paths import url_to_output_path


test_urls = [
    "https://www.d20srd.org/srd/combat/actionsInCombat.htm",
    "https://www.d20srd.org/srd/combat/attacksOfOpportunity.htm",
    "https://www.d20srd.org/srd/classes/sorcererWizard.htm",
    "https://www.d20srd.org/srd/conditionSummary.htm",
]

for url in test_urls:
    print(url)
    print("->", url_to_output_path(url))
    print()