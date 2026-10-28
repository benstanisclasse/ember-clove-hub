"""Cycle 1, round 1 shortlist: generator specs in exactly the scripts/make_tryon.py SPECS format.

Source: research/tiktok/EMBER_CLOVE_CREATIVE_CONCEPTS.md (section 3.1) and HYPOTHESIS_REGISTRY_cycle1.md.
Written 2026-10-25. Nothing here calls an API or spends money; importing this module only defines data.

- 8 videos x 15 s x ~$0.324/s ~= $38.88 (estimate). Owner approval is required before any generation.
- Supersedes the never-generated drafts in make_tryon.py: EC-P01-A05-H01-V01, EC-P01-A06-H01-V01,
  EC-P02-A05-H01-V01, EC-P02-A06-H01-V01 (V02 here). make_tryon.py itself is not edited.
- Test (a), callout vs demo-first opening: each pair below differs ONLY in shot 1's spoken line and hook_type
  (P01: A05-H01 vs A05-H02; P02: A05-H01 vs A05-H02). Keep refs, presenter description, settings identical.
- To generate later (after approval), merge these entries into make_tryon.SPECS, e.g.
  `make_tryon.SPECS.update(concept_specs_cycle1.SPECS)` in a small runner, then call make_tryon.main().
- Check the live Shopify price before each run: the spoken prices are $52.99 (P01) and $44.99 (P02).
- Run `python -I scripts/concept_specs_cycle1.py` for a local self-check (word counts, banned terms). No network.

Concepts NOT in this file because they need new face-free reference crops (none created):
  EC-P01-A07 (Black)  - crop store image F2DBBAD28F9480BDB2430849E31F14A6.jpg
                         (local copy: assets/EC-P01-A02-H01-V01/src_F2DBBAD28F9480BDB2430849E31F14A6.jpg)
  EC-P01-A08 (Green)  - crop store image 30F9328D3C4BBDAAF666DAD820067D27.jpg (green per ICP-P01 B1; confirm)
  EC-P02-A09 (Khaki)  - crop store image 1A1043B235C30627DFD80E2CD435A129.jpg
                         (local copy: assets/EC-P02-A03-H01-V01/src_1A1043B235C30627DFD80E2CD435A129.jpg)
Backlog concepts that use existing refs but are not round 1: EC-P02-A08 (best as a 25 s test), all H03 hooks,
EC-P01-A06-H02/H03, EC-P01-A09-H02/H03, EC-P02-A06-H02/H03, EC-P02-A07-H02/H03.
"""

P01_ID = "gid://shopify/Product/9751656071407"
P02_ID = "gid://shopify/Product/9751655809263"
P01_NAME = "Cable Knit Mock Neck Midi Dress"
P02_NAME = "Turtleneck Rib Knit Sweater Dress"

PRESENTER = "the presenter (shoulder-length wavy dark-brown hair, small gold hoop earrings)"

P01_CARAMEL_REFS = ["assets/EC-P01-A02-H01-V01/ref1_dress_neck_down.jpg",
                    "assets/EC-P01-A02-H01-V01/ref2_cable_slit_closeup.jpg"]
P01_CARAMEL_SRC = "Shopify 1E3E6FA7B028205FCC94E89C7CF6CC63.jpg (caramel street shot)"
P01_RED_REFS = ["assets/EC-P01-A06-H01-V01/ref1_red_dress_neck_down.jpg",
                "assets/EC-P01-A06-H01-V01/ref2_red_cable_slit_closeup.jpg"]
P01_RED_SRC = "Shopify A02E524E5518B5581012D3C06BA3779B.jpg (red studio shot)"
P02_BURGUNDY_REFS = ["assets/EC-P02-A03-H01-V01/ref1_dress_neck_down.jpg",
                     "assets/EC-P02-A03-H01-V01/ref2_turtleneck_knit_closeup.jpg"]
P02_BURGUNDY_SRC = "Shopify EB40AEBD79AAF3FECCF037153E856C2F.jpg (burgundy studio shot)"


def _p01_dress(color, color_word):
    return (f"the exact {color_word} cable-knit mock neck midi sweater dress from the reference images: plain-knit "
            "fitted top with a mock neck, long sleeves with ribbed cuffs, a ribbed waistband at the natural waist, a "
            "vertical cable-knit skirt fitted through the hips with a diagonal wrap seam that opens into a front slit, "
            "midi length to mid-calf where the hem overlaps the top of black knee-high boots. Keep its "
            f"{color} color, the cable pattern (on the skirt only), the slit position and height (never higher than "
            "in the references) and the length identical to the references.")


def _p02_dress(legwear):
    return ("the exact burgundy chunky rib-knit turtleneck sweater dress from the reference images: loose slouchy fit "
            "that hangs straight from the shoulders with no waist seam, folded turtleneck, dropped shoulders, long "
            "full sleeves with ribbed cuffs, ribbed hem, mini length ending at upper-to-mid thigh. It is always worn "
            f"over {legwear} (never bare legs). Keep its burgundy color, chunky vertical rib, turtleneck and short "
            "length identical to the references; never lengthen it toward the knee and never add a waist or belt.")


# --- P01 A05: "Tall boots, finished" (AR-04 in the AR-02 frame). Shots 2-4 shared by H01 and H02. ---------------
_P01_A05_SHOT1_ACTION = (f"{PRESENTER} is already wearing the caramel dress with black knee-high boots; full-length "
                         "shot, she takes two steps toward the camera so the front slit opens over the boots, looking "
                         "straight into the lens")
_P01_A05_REST = [
    ("3-7 s", "cut to a mid-shot; her hands run down the cable-knit skirt and smooth the ribbed waistband, then touch "
     "the mock neck; her eyes follow her hands", "Cable knit, mock neck, fitted through the hips."),
    ("7-11 s", "cut to a full-length side-front shot; she walks past the arched mirror and the front slit opens over "
     "the boot shaft with each step", "The slit opens over your boots, so walking's easy."),
    ("11-15 s", "she walks up to the camera into a smiling chest-up close-up",
     "Seven colors, sizes small to XL. Link's right here."),
]
_P01_A05_BASE = {
    "experiment_id": "C1-P01-A05", "product_id": P01_ID, "product": P01_NAME, "color": "Caramel",
    "angle": "The dress your tall boots need (ICP-P01 A1) - AR-04 stride demo", "icp": "P01 S1 Boot-season outfit builder",
    "refs": P01_CARAMEL_REFS, "source_photo": P01_CARAMEL_SRC, "dress": _p01_dress("caramel", "caramel"),
    "opening_visual": "product-on-body-stride",
}

# --- P02 A05: "Whole outfit, three pieces" (AR-05). Shots 2-4 shared by H01 and H02. -------------------------------
_P02_A05_SHOT1_ACTION = (f"{PRESENTER} is already wearing the dress over opaque black tights with black knee-high "
                         "boots; full-length shot by the arched mirror, she turns from the mirror toward the camera "
                         "and looks into the lens")
_P02_A05_REST = [
    ("3-7 s", "cut to a mid-shot; she folds the turtleneck down once and pushes up the slouchy sleeves; her eyes on "
     "the knit", "Slouchy turtleneck, dropped shoulders, loose fit."),
    ("7-11 s", "cut to a full-length side view; she picks up a small crossbody bag and walks, the hem sitting at "
     "mid-thigh over the tights and clearly visible", "It's a short one, easy over tights and boots."),
    ("11-15 s", "she walks up to the camera into a smiling chest-up close-up",
     "It's Ember and Clove, in seven colors. Link's right here."),
]
_P02_A05_BASE = {
    "experiment_id": "C1-P02-A05", "product_id": P02_ID, "product": P02_NAME, "color": "Burgundy",
    "angle": "Whole outfit, three pieces (ICP-P02 A2) - AR-05 outfit build", "icp": "P02 S1 Outfit-formula seeker",
    "refs": P02_BURGUNDY_REFS, "source_photo": P02_BURGUNDY_SRC,
    "dress": _p02_dress("opaque black tights"), "opening_visual": "product-on-body-turn",
}

# Owner rule 2026-10-25: spoken lines never state the price or delivery times (they lock an ad to today's
# price/shipping). Lines below were updated; videos already made with them keep them until remade.
SPECS = {
    # Test (a) pair, P01. H01 = situation callout (HK-31); H02 = demo-first, no buyer callout (HK-35).
    "EC-P01-A05-H01-V02": {
        **_P01_A05_BASE,
        "shots": [("0-3 s", _P01_A05_SHOT1_ACTION, "Own knee-high boots? This dress is for you.")] + _P01_A05_REST,
        "hook_type": "callout",
    },
    "EC-P01-A05-H02-V02": {
        **_P01_A05_BASE,
        "shots": [("0-3 s", _P01_A05_SHOT1_ACTION, "Watch what this slit does with every step.")] + _P01_A05_REST,
        "hook_type": "demo-first",
    },
    # P01 A06: "Holiday plans, one dress" (AR-15), red. Time-boxed: launch by ~Nov 5, stop ~Nov 15-20. HK-19.
    "EC-P01-A06-H01-V02": {
        "experiment_id": "C1-P01-A06", "product_id": P01_ID, "product": P01_NAME, "color": "Red",
        "angle": "Holiday plans, one dress (ICP-P01 A2) - AR-15 occasion", "icp": "P01 S2 Holiday-gathering dresser",
        "refs": P01_RED_REFS, "source_photo": P01_RED_SRC,
        "dress": _p01_dress("bright coral-red", "red") + " Do not darken it to crimson or burgundy.",
        "setting": ("the same warm apartment in the evening, decorated for the holidays with warm string lights "
                    "around the front door and a small wreath"),
        "shots": [
            ("0-3 s", f"{PRESENTER} is already wearing the red dress with black knee-high boots, standing full-length "
             "by the front door framed with string lights; she fastens a small earring, then turns to the camera",
             "Holiday party coming? This is the whole outfit."),
            ("3-7 s", "cut to a mid-shot under the string lights; she turns slightly to show the mock neck, the long "
             "sleeves and the cable-knit skirt", "Ember and Clove's red cable knit, mock neck, long sleeves."),
            ("7-11 s", "cut to a full-length shot; she walks across the room and the front slit opens over the boots",
             "Fitted through the hips, with a slit to move in."),
            ("11-15 s", "she walks up to the camera into a friendly chest-up close-up",
             "Seven colors, sizes small to XL. Link's right here."),
        ],
        "hook_type": "callout", "opening_visual": "product-on-body-occasion",
    },
    # P01 A09: "Three honest things" (AR-14), caramel. HK-36 (new).
    "EC-P01-A09-H01-V01": {
        "experiment_id": "C1-P01-A09", "product_id": P01_ID, "product": P01_NAME, "color": "Caramel",
        "angle": "Three honest things before you order - AR-14 transparency",
        "icp": "P01 S1 comparison shopper / ad-store skeptic",
        "refs": P01_CARAMEL_REFS, "source_photo": P01_CARAMEL_SRC, "dress": _p01_dress("caramel", "caramel"),
        "shots": [
            ("0-3 s", f"{PRESENTER} is already wearing the caramel dress with black knee-high boots; full-length, she "
             "walks toward the camera holding up three fingers", "Before you order this midi, three honest things."),
            ("3-7 s", "cut to a full-length shot; she runs one hand from the ribbed waistband down to the hem, which "
             "overlaps the top of the boots at mid-calf", "One: it's a midi, about forty-four to forty-seven inches."),
            ("7-11 s", "cut to a close-up of her hand on the cable-knit skirt, then the camera rises to her face",
             "Two: acrylic-blend knit. Three: sizes small to XL only."),
            ("11-15 s", "she steps back into a mid-shot and smiles at the camera",
             "Seven colors, sizes small to XL. Link's right here."),
        ],
        "hook_type": "callout", "opening_visual": "product-on-body-walk",
    },
    # Test (a) pair, P02. H01 = situation callout (HK-39, new); H02 = demo-first formula line (HK-17).
    "EC-P02-A05-H01-V02": {
        **_P02_A05_BASE,
        "shots": [("0-3 s", _P02_A05_SHOT1_ACTION, "Tights and boots all winter? This is your dress.")] + _P02_A05_REST,
        "hook_type": "callout",
    },
    "EC-P02-A05-H02-V02": {
        **_P02_A05_BASE,
        "shots": [("0-3 s", _P02_A05_SHOT1_ACTION,
                   "Black tights, tall boots, and this. That's the whole outfit.")] + _P02_A05_REST,
        "hook_type": "demo-first",
    },
    # P02 A06: "Pajamas that pass" (AR-06 adapted: couch to door in the same dress). HK-03.
    "EC-P02-A06-H01-V02": {
        "experiment_id": "C1-P02-A06", "product_id": P02_ID, "product": P02_NAME, "color": "Burgundy",
        "angle": "Comfortable, still dressed (ICP-P02 A1) - AR-06 couch-to-door",
        "icp": "P02 S2 Comfort-first 'pajamas that pass'",
        "refs": P02_BURGUNDY_REFS, "source_photo": P02_BURGUNDY_SRC, "dress": _p02_dress("opaque black leggings"),
        "shots": [
            ("0-3 s", f"{PRESENTER} is already wearing the dress over opaque black leggings, sitting cross-legged on "
             "the couch holding a mug; she looks up at the camera", "Living in leggings, but want to look dressed?"),
            ("3-7 s", "cut to her standing, mid-shot; she pushes up the slouchy sleeves and lets the loose knit fall "
             "straight from her shoulders", "It's a loose, slouchy sweater dress with a folded turtleneck."),
            ("7-11 s", "cut to a full-length shot by the front door, now in black ankle boots; she grabs her keys and "
             "a tote bag", "Add leggings and boots, and you're out the door dressed."),
            ("11-15 s", "she walks up to the camera into a smiling close-up",
             "It's Ember and Clove, in seven colors. Link's right here."),
        ],
        "hook_type": "callout", "opening_visual": "product-on-body-couch",
    },
    # P02 A07: "Holiday dinner, nothing tight at the waist" (AR-15). HK-32. No "Thanksgiving" wording.
    "EC-P02-A07-H01-V01": {
        "experiment_id": "C1-P02-A07", "product_id": P02_ID, "product": P02_NAME, "color": "Burgundy",
        "angle": "Holiday dinner dress, nothing tight at the waist (ICP-P02 A4) - AR-15 occasion",
        "icp": "P02 S3 Holiday-season eater",
        "refs": P02_BURGUNDY_REFS, "source_photo": P02_BURGUNDY_SRC, "dress": _p02_dress("opaque black tights"),
        "setting": ("a warm dining room in the evening with a table set for a holiday dinner, candles and simple "
                    "greenery"),
        "shots": [
            ("0-3 s", f"{PRESENTER} is already wearing the dress over opaque black tights with black knee-high boots; "
             "full-length side view as she sets plates on the holiday table (the table does not hide the hem), then "
             "looks at the camera", "Hosting a holiday dinner this year? Look at this."),
            ("3-7 s", "cut to her sitting down at the table and reaching across for a dish; the loose knit hangs away "
             "from the waist; no eating", "Loose fit, nothing tight at the waist."),
            ("7-11 s", "cut to a full-length shot as she stands beside the table, the hem at mid-thigh over the tights",
             "Burgundy, slouchy turtleneck, with tights and boots."),
            ("11-15 s", "she walks up to the camera into a friendly close-up",
             "It's Ember and Clove, in seven colors. Link's right here."),
        ],
        "hook_type": "callout", "opening_visual": "product-on-body-occasion",
    },
}

EST_USD_PER_SECOND, DURATION = 0.324, 15
BANNED = ["warm", "100% wool", "wool dress", "not itchy", "best seller", "bestseller", "flattering", "guarantee",
          "selling out", "last chance", "hurry", "limited", "i bought", "i own", "i've worn", "my favorite",
          "looks expensive", "3x", "xl", "small to", "order now", "only today"]
BANNED_P02 = ["soft"]


def _check():
    """Local self-check: required keys, word counts, first-line length, banned terms. No network."""
    required = {"experiment_id", "product_id", "product", "color", "angle", "icp", "refs", "source_photo", "dress",
                "shots", "hook_type"}
    total = 0.0
    for cid, s in SPECS.items():
        missing = required - set(s)
        lines = [shot[2] for shot in s["shots"]]
        words = sum(len(x.split()) for x in lines)
        first = len(lines[0].split())
        spoken = " ".join(lines).lower()
        hits = [b for b in BANNED + (BANNED_P02 if s["product_id"] == P02_ID else []) if b in spoken]
        total += DURATION * EST_USD_PER_SECOND
        print(f"{cid}: shots={len(s['shots'])} words={words} first_line={first} banned={hits or '-'} "
              f"missing={sorted(missing) or '-'}")
    print(f"{len(SPECS)} videos, estimated ${total:.2f} at ${EST_USD_PER_SECOND}/s")


if __name__ == "__main__":
    _check()
