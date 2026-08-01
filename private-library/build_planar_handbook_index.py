"""Build the Planar Handbook spell index from visually verified scan metadata."""
from pathlib import Path
import json
from build_spell_index import comparison_key, parse_class_and_level_filters, public_spell_slugs, slugify

SPELLS = [
 (10,"Axiomatic Storm","Conjuration","Cleric 3, Paladin 4"),(10,"Axiomatic Water","Transmutation","Cleric 1, Paladin 1"),(10,"Babau Slime","Transmutation","Druid 3, Sor/Wiz 3"),(10,"Balor Nimbus","Transmutation","Cleric 4, Sor/Wiz 4"),(10,"Barghest's Feast","Necromancy","Cleric 6, Sor/Wiz 7"),(10,"Beastland Ferocity","Enchantment","Bard 1, Druid 1"),
 (11,"Belker Claws","Transmutation","Sor/Wiz 2"),(11,"Bodak's Glare","Necromancy","Cleric 8"),(11,"Call Kolyarut","Conjuration","Cleric 7, Sor/Wiz 7"),(11,"Call Marut","Conjuration","Cleric 9, Sor/Wiz 9"),(11,"Call Zelekhut","Conjuration","Cleric 5, Sor/Wiz 5"),(11,"Cloak Pool","Illusion","Bard 2, Sor/Wiz 2"),
 (12,"Corporeal Instability","Transmutation","Sor/Wiz 4"),(12,"Death Throes","Necromancy","Cleric 5, Sor/Wiz 5"),(12,"Demon Dirge","Transmutation","Cleric 4, Sor/Wiz 4"),(12,"Devil Blight","Transmutation","Cleric 3, Sor/Wiz 3"),(12,"Discolor Pool","Illusion","Bard 2, Sor/Wiz 2"),
 (13,"Evil Glare","Necromancy","Cleric 4, Sor/Wiz 4"),(13,"False Gravity","Transmutation","Sor/Wiz 4"),(13,"Fierce Pride of the Beastlands","Conjuration","Cleric 8, Sor/Wiz 8"),(13,"Focus Touchstone Energy","Transmutation","Cleric 4, Druid 5"),(13,"Hamatula Barbs","Transmutation","Cleric 3, Sor/Wiz 3"),
 (14,"Heavenly Host","Conjuration","Cleric 9, Sor/Wiz 9"),(14,"Hellish Horde","Conjuration","Cleric 9, Sor/Wiz 9"),(14,"Holy Storm","Conjuration","Cleric 3, Paladin 3"),(14,"Hunters of Hades","Conjuration","Cleric 9"),(14,"Infernal Wound","Transmutation","Cleric 4, Sor/Wiz 4"),
 (15,"Lay of the Land","Divination","Bard 4, Druid 4, Ranger 1"),(15,"Light of Lunia","Evocation","Cleric 1, Sor/Wiz 1"),(15,"Light of Mercuria","Evocation","Cleric 2, Sor/Wiz 2"),(15,"Light of Venya","Evocation","Cleric 3, Sor/Wiz 3"),(15,"Locate Touchstone","Divination","Bard 1, Cleric 2, Druid 1, Sor/Wiz 1"),(15,"Mantle of Chaos","Abjuration","Cleric 3"),(15,"Mantle of Evil","Abjuration","Blackguard 3, Cleric 3"),(15,"Mantle of Good","Abjuration","Cleric 3, Paladin 3"),
 (16,"Mantle of Law","Abjuration","Cleric 3, Paladin 3"),(16,"Mechanus Mind","Enchantment","Sor/Wiz 2"),(16,"Miasma of Entropy","Necromancy","Druid 6, Sor/Wiz 7"),(16,"Negative Energy Aura","Necromancy","Cleric 4"),(16,"Opalescent Glare","Necromancy","Cleric 5, Sor/Wiz 5"),(16,"Perinarch","Transmutation","Druid 4, Sor/Wiz 4"),
 (17,"Perinarch, Planar","Transmutation","Druid 9, Sor/Wiz 9"),(17,"Planar Bubble","Abjuration","Cleric 7, Sor/Wiz 7"),(17,"Planar Exchange","Conjuration","Cleric 6"),
 (18,"Planar Exchange, Greater","Conjuration","Cleric 8"),(18,"Planar Exchange, Lesser","Conjuration","Cleric 4"),(18,"Planar Tolerance","Abjuration","Cleric 4, Druid 4, Ranger 4, Sor/Wiz 3"),(18,"Plane Shift, Greater","Conjuration","Cleric 7, Sor/Wiz 8"),(18,"Positive Energy Aura","Conjuration","Cleric 4"),(18,"Precipitate Breach","Conjuration","Sor/Wiz 5"),
 (19,"Precipitate Complete Breach","Conjuration","Sor/Wiz 9"),(19,"Protection from Negative Energy","Abjuration","Cleric 3"),(19,"Protection from Positive Energy","Abjuration","Cleric 3"),(19,"Rary's Interplanar Telepathic Bond","Divination","Sor/Wiz 6"),(19,"Resist Planar Alignment","Abjuration","Cleric 1, Druid 1, Paladin 1, Ranger 1, Sor/Wiz 1"),(19,"Seal Portal","Abjuration","Sor/Wiz 6"),(19,"Spell Vulnerability","Transmutation","Cleric 4, Sor/Wiz 3"),(19,"Summon Babau Demon","Conjuration","Cleric 6"),
 (20,"Summon Bearded Devil","Conjuration","Cleric 4"),(20,"Summon Bralani Eladrin","Conjuration","Cleric 5"),(20,"Summon Elementite Swarm","Conjuration","Druid 4"),(20,"Summon Elysian Thrush","Conjuration","Bard 2, Cleric 2"),(20,"Summon Greater Elemental","Conjuration","Druid 6"),
 (21,"Summon Hound Archon","Conjuration","Cleric 4"),(21,"Touchstone Lightning","Transmutation","Druid 4, Sor/Wiz 4"),(21,"Unholy Storm","Conjuration","Blackguard 4, Cleric 3"),(21,"Wall of Gears","Conjuration","Sor/Wiz 6"),
]

def build(output: Path, public_dir: Path) -> dict:
    existing = public_spell_slugs(public_dir)
    spells=[]
    for page,name,school,levels in SPELLS:
        if slugify(name) in existing or comparison_key(name) in existing:
            continue
        classes, spell_levels = parse_class_and_level_filters(levels)
        spells.append({"name":name,"page":page,"school":school,"levels":levels,"classes":classes,"spell_levels":spell_levels})
    spells.sort(key=lambda spell: spell["name"].casefold())
    payload={"book":"Planar Handbook","private":True,"public_srd_duplicates_excluded":True,"spell_count":len(spells),"spells":spells}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(payload,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    return payload

if __name__ == "__main__":
    root=Path(__file__).parents[1]
    output=Path(__file__).parent/"generated"/"planar-handbook-index.json"
    payload=build(output,root/"public")
    print(f"Indexed {payload['spell_count']} private, non-SRD spells: {output}")
