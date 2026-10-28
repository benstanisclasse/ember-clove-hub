"""Create the Hub's folders and empty record files. Safe to rerun: never overwrites existing data."""
import hubdata as hd

LEARNINGS_TEMPLATE = """# Ember & Clove — learnings playbook

Running conclusions drawn from the Hub's records. Update after every cycle.
Evidence levels: **controlled** (one-change duplicate test) · **repeated** (seen in 2+ cycles) · **tentative** (one cycle) · **contradicted**.

## What works
_(none yet)_

## What doesn't
_(none yet)_

## Open questions to test next
_(none yet)_

## Cycle notes
"""


def main():
    for folder in (hd.DATA, hd.INBOX, hd.REPORTS, hd.RECIPES, hd.ASSETS):
        folder.mkdir(parents=True, exist_ok=True)
    for name in hd.SCHEMAS:
        if not hd.csv_path(name).exists():
            hd.write(name, [])
            print(f"created data/{name}.csv")
    if not hd.LOG.exists():
        hd.LOG.write_text("# Hub log — approvals, actions, decisions\n\n", encoding="utf-8")
        print("created log.md")
    if not hd.LEARNINGS.exists():
        hd.LEARNINGS.write_text(LEARNINGS_TEMPLATE, encoding="utf-8")
        print("created learnings.md")
    print("Hub structure ready.")


if __name__ == "__main__":
    main()
