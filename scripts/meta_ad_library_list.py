"""Build research/meta/ad_library_100_2026-10-27.csv from Meta Ad Library search results (Meta Ads connector,
ads_library_search, US, active ads, pulled 2026-10-27). Rows were filtered by hand to clothing/shoe sellers; the API
gives only these fields, so the rest (days running, copies per page) is derived here."""
import csv
import datetime as dt
from collections import Counter
from pathlib import Path

PULLED = dt.datetime(2026, 10, 27, 23, 59, tzinfo=dt.timezone.utc)
OUT = Path(__file__).resolve().parents[1] / "research" / "meta" / "ad_library_100_2026-10-27.csv"

# (ad_id, page_id, page_name, headline, created_unix, delivery_start_unix, currency, search)
ADS = [
    ("1659480719298306", "340498052986285", "Simply Simpson Boutique", "Don't Wait On Your Favorite Color!", 1793140571, 1793146638, "USD", "boutique sweater"),
    ("3212334042295884", "537564306105495", "Char Lee", "Live Sale!", 1793139468, 1793144748, "USD", "boutique sweater"),
    ("1844359596721088", "106243122515100", "Whimsical Mimsy", "", 1793137281, 1793142704, "USD", "boutique sweater"),
    ("1771618044054238", "301812516559736", "The Mint Julep Boutique", "", 1793135033, 1793140144, "USD", "boutique sweater"),
    ("1770651734165651", "301812516559736", "The Mint Julep Boutique", "", 1793135033, 1793140000, "USD", "boutique sweater"),
    ("987111457780295", "301812516559736", "The Mint Julep Boutique", "", 1793135002, 1793140306, "USD", "boutique sweater"),
    ("1748203836275132", "301812516559736", "The Mint Julep Boutique", "", 1793134478, 1793139551, "USD", "boutique sweater"),
    ("1698232778383409", "301812516559736", "The Mint Julep Boutique", "", 1793134403, 1793140214, "USD", "boutique sweater"),
    ("1598292525107394", "301812516559736", "The Mint Julep Boutique", "", 1793134399, 1793139797, "USD", "boutique sweater"),
    ("1847932573029709", "535298206561001", "RubyClaire Boutique", "", 1793134213, 1793143505, "USD", "boutique sweater"),
    ("29263428659917114", "100740336727314", "Bloom Consignment Boutique", "", 1793132398, 1793137986, "USD", "boutique sweater"),
    ("1855374305657258", "1309824288884792", "Sorevia", "ALL 8 COLORS FOR $29.99", 1793132360, 1793138092, "USD", "boutique sweater"),
    ("1702893901536570", "100740336727314", "Bloom Consignment Boutique", "", 1793132273, 1793137402, "USD", "boutique sweater"),
    ("1165709922634605", "905926132597599", "State of Reign Boutique", "Lola Jean + Mallard Sweater, limited sizes", 1793131863, 1793137148, "USD", "boutique sweater"),
    ("1631964115394269", "1046190988822354", "Urban Threads Clothing Boutique", "", 1793130853, 1793137811, "USD", "boutique sweater"),
    ("1812828756588864", "194650683903854", "Mainstream Boutique Omaha", "We're LIVE and the outfits are 🔥!", 1793129749, 1793134955, "USD", "boutique sweater"),
    ("2351416272339658", "102722736071021", "Dahlia's Downtown Boutique", "Neutral Cable Knit Zip Up Cardigan | Long Sleeve Lightweight Ribbed Sweater | Dark Mauve Sweater | Leopard Print Long Sleeve Sweater", 1793127549, 1793135976, "USD", "boutique sweater"),
    ("2219186889025608", "112527798161383", "The Scarlett Boutique", "", 1793127188, 1793134309, "USD", "boutique sweater"),
    ("1797178101402584", "147608472998", "Broadway Boutique", "", 1793127059, 1793132249, "USD", "boutique sweater"),
    ("2961514300885906", "1864909327070824", "Bluff Creek Boutique", "", 1793126885, 1793131772, "USD", "boutique sweater"),
    ("1801681254477476", "204657176383358", "Reign Boutique", "", 1793126834, 1793136185, "USD", "boutique sweater"),
    ("4648984712087391", "204657176383358", "Reign Boutique", "", 1793126686, 1793131937, "USD", "boutique sweater"),
    ("1822194992309250", "704271176307437", "Bleu", "Shop Flower Power", 1793126448, 1793131673, "USD", "boutique sweater"),
    ("1142217081648001", "639592746233669", "Shabby2Chic Boutiques", "Christmas Came Early", 1793126024, 1793135405, "USD", "boutique sweater"),
    ("2200026094266294", "949002841892556", "MOCO Boutique", "📲 Use Code: DENIM30", 1793125079, 1793130428, "USD", "boutique sweater"),
    ("1350229513711310", "949002841892556", "MOCO Boutique", "📲 Use Code: DENIM30", 1793125074, 1793129849, "USD", "boutique sweater"),
    ("1108616114907278", "103085761271547", "Trendy Trunk", "It's Officially Sweater Weather! 🍂", 1793124899, 1793138534, "USD", "boutique sweater"),
    ("1831237824811129", "106094504558141", "Different Flavas Boutique", "", 1793123356, 1793132328, "USD", "boutique sweater"),
    ("2095679061076736", "949002841892556", "MOCO Boutique", "ALL NEW WORK TO WEEKEND TOPS plus a DENIM DEAL!", 1793123260, 1793128213, "USD", "boutique sweater"),
    ("1615878932710119", "153170381969243", "Lizard Thicket Boutique", "", 1793121504, 1793128219, "USD", "boutique sweater"),
    ("940147942282774", "301812516559736", "The Mint Julep Boutique", "School Style Gets Festive", 1793120668, 1793127641, "USD", "boutique sweater"),
    ("1698646321869987", "535298206561001", "RubyClaire Boutique", "", 1793120251, 1793125424, "USD", "boutique sweater"),
    ("1118539287541367", "581380695347388", "Mainstream Boutique Ponte Vedra", "Start Your Day with Top Picks!", 1793119897, 1793125847, "USD", "boutique sweater"),
    ("4658627937728682", "186654118761", "Josie's Boutique", "Day After Day Stripe Two Piece Set | Soft Escape Oversized V-Neck Sweater", 1793119585, 1793124855, "USD", "boutique sweater"),
    ("2207983177263373", "186654118761", "Josie's Boutique", "Day After Day Stripe Two Piece Set | Soft Escape Oversized V-Neck Sweater", 1793119582, 1793125407, "USD", "boutique sweater"),
    ("1140323931902102", "186654118761", "Josie's Boutique", "Day After Day Stripe Two Piece Set | Soft Escape Oversized V-Neck Sweater", 1793119545, 1793125006, "USD", "boutique sweater"),
    ("1425524932454172", "102748892186607", "Belles and Whistles Boutique", "NEW SWEATER 🙌", 1793118634, 1793134106, "USD", "boutique sweater"),
    ("1810605654128171", "102748892186607", "Belles and Whistles Boutique", "NEW SWEATER 🙌", 1793118606, 1793128244, "USD", "boutique sweater"),
    ("1534130868473193", "102748892186607", "Belles and Whistles Boutique", "NEW SWEATER 🙌", 1793118606, 1793125276, "USD", "boutique sweater"),
    ("1662446785407336", "102748892186607", "Belles and Whistles Boutique", "NEW SWEATER 🙌", 1793118461, 1793123374, "USD", "boutique sweater"),
    ("1853504985808051", "178311352989067", "The Vintage Emmie Boutique", "The Ballinger Fleece Pullover (Green) | The Pecos Duck Sweater (Green) | The Rocksprings Camo Sweatshirt | The Calloway Wide Leg Denim Jeans | The Frisco Long Sleeve Stripe Top", 1793117168, 1793122590, "USD", "boutique sweater"),
    ("4537407389857499", "100411506391567", "Buck Mason Women's", "California Cashmere", 1793137217, 1793141967, "USD", "cardigan knit"),
    ("2572304859900942", "100411506391567", "Buck Mason Women's", "Herdsman Shawl Cardigan", 1793137216, 1793141405, "USD", "cardigan knit"),
    ("2863110470728045", "658333367538539", "The Pulse Boutique", "Brisk Morning Lightweight Zip Up Jacket | Comfortable With Myself Knit Cardigan | Be A Star Drawstring Hoodie | Campfire Nights Plaid Jacket", 1793136913, 1793141967, "USD", "cardigan knit"),
    ("1817864392729980", "658333367538539", "The Pulse Boutique", "Brisk Morning Lightweight Zip Up Jacket | Comfortable With Myself Knit Cardigan | Be A Star Drawstring Hoodie | Campfire Nights Plaid Jacket", 1793136892, 1793141718, "USD", "cardigan knit"),
    ("1898960657865854", "101207349266417", "Pinklaura", "Casual Striped 3/4 Sleeve Knit Cardigan", 1793134207, 1793139511, "USD", "cardigan knit"),
    ("2148133662459712", "101207349266417", "Pinklaura", "Casual Striped 3/4 Sleeve Knit Cardigan", 1793134197, 1793139698, "USD", "cardigan knit"),
    ("1596535894939697", "101207349266417", "Pinklaura", "Casual Striped 3/4 Sleeve Knit Cardigan", 1793134196, 1793140695, "USD", "cardigan knit"),
    ("2375330043004998", "291119246072", "Coldwater Creek", "Hollyberry Cardigan", 1793133801, 1793138149, "USD", "cardigan knit"),
    ("1668294068221194", "291119246072", "Coldwater Creek", "Shaker Detail Button Cardigan", 1793133794, 1793138953, "USD", "cardigan knit"),
    ("968186079687018", "291119246072", "Coldwater Creek", "Hollyberry Cardigan", 1793133772, 1793138130, "USD", "cardigan knit"),
    ("3567392440100660", "291119246072", "Coldwater Creek", "Hollyberry Cardigan", 1793133733, 1793137785, "USD", "cardigan knit"),
    ("3981263332016521", "291119246072", "Coldwater Creek", "Shaker Detail Button Cardigan", 1793133728, 1793140597, "USD", "cardigan knit"),
    ("947724704814727", "224761807732013", "Z SUPPLY", "A Best Seller for a Reason", 1793133184, 1793138992, "USD", "cardigan knit"),
    ("2969962073349226", "157632231087765", "THE UPSIDE", "New Arrivals | The Upside", 1793131368, 1793136609, "USD", "cardigan knit"),
    ("2338911383608080", "901407303052187", "Kenneth Washington", "Shimmering Beige and Gold Metallic Open Front Knit Cardigan Women's 20W", 1793131362, 1793136893, "USD", "cardigan knit"),
    ("28565880883034969", "112081614743231", "Copper & Cloth", "1 Pant, 5 Ways to Style It", 1793130661, 1793139452, "USD", "cardigan knit"),
    ("5483579281867098", "154704514572585", "Gretchen Scott Designs", "Breakfast at Tiffany's Cardigan | Cable Car Sweater | Sneek A Peek Knit Sweater | Knit Knit Sweater | Sumptuous Blouse", 1793130605, 1793135806, "USD", "cardigan knit"),
    ("1450275983956782", "1292170753980007", "Casual Fashion Outlet", "🔥 TLB Flash Sale — Save Up To 50%", 1793128862, 1793137110, "USD", "cardigan knit"),
    ("28534311259604946", "1292170753980007", "Casual Fashion Outlet", "🔥 TLB Flash Sale — Save Up To 50%", 1793128864, 1793136941, "USD", "cardigan knit"),
    ("1039978885774832", "1783400318558077", "Discount Divas", "$36 Waffle Cardigan in S-3XL", 1793124645, 1793129863, "USD", "cardigan knit"),
    ("1808491220286834", "104432294433315", "Liwisi", "Get Yours Now!", 1793113197, 1793134516, "USD", "cardigan knit"),
    ("1271516398475436", "58413319536", "www.jbandme.com", "Outfit Inspo | Opal Cardigan | Back 70 Velvet Sneaker | Blessed Brocade Hat", 1793123451, 1793129587, "USD", "cardigan knit"),
    ("4849338678670429", "389899910882524", "SYRN by Sydney Sweeney", "", 1793122713, 1793128396, "USD", "cardigan knit"),
    ("1788600799058262", "389899910882524", "SYRN by Sydney Sweeney", "Shop Now", 1793122381, 1793127561, "USD", "cardigan knit"),
    ("1125916913478529", "291119246072", "Coldwater Creek", "Hollyberry Cardigan", 1793122012, 1793127564, "USD", "cardigan knit"),
    ("1597717004915844", "291119246072", "Coldwater Creek", "Hollyberry Cardigan", 1793122006, 1793129667, "USD", "cardigan knit"),
    ("2109093993053645", "291119246072", "Coldwater Creek", "Hollyberry Cardigan", 1793122002, 1793129639, "USD", "cardigan knit"),
    ("1084987887868845", "291119246072", "Coldwater Creek", "Hollyberry Cardigan", 1793121998, 1793129694, "USD", "cardigan knit"),
    ("1480726680602154", "100296078875911", "BloomChic US", "SIZES 10 TO 30", 1793121485, 1793140728, "USD", "cardigan knit"),
    ("1604877490618982", "1184957578031242", "Tina Bella", "vintage hollister knit cardigan", 1793120973, 1793135241, "CAD", "cardigan knit"),
    ("2039410726762467", "389899910882524", "SYRN by Sydney Sweeney", "", 1793119908, 1793125044, "USD", "cardigan knit"),
    ("1105594039027670", "100842618611379", "BloomChic", "", 1793119762, 1793130523, "USD", "cardigan knit"),
    ("4465194927065072", "113211405384039", "Joyfolie", "The Fall Cardigan You'll Live In", 1793119012, 1793129061, "USD", "cardigan knit"),
    ("2913317399043037", "113211405384039", "Joyfolie", "The Fall Cardigan You'll Live In", 1793119012, 1793126339, "USD", "cardigan knit"),
    ("1859966815445600", "113211405384039", "Joyfolie", "The Fall Cardigan You'll Live In", 1793119011, 1793128278, "USD", "cardigan knit"),
    ("1046928415077392", "1292170753980007", "Casual Fashion Outlet", "The Cardigan That Makes Outfits Easy", 1793118236, 1793124784, "USD", "cardigan knit"),
    ("29208728742091099", "250028769065387", "Alpa", "100 % Alpaca. Made in EU. Designed in Finland.", 1793118340, 1793123622, "EUR", "cardigan knit"),
    ("XXX", "1097556193447695", "CAKO-Cashmere", "100% Cashmere | Timeless Everyday Elegance", 1793079531, 1793134855, "USD", "cardigan knit"),
    ("1925212232182110", "101425486252633", "Previousn", "", 1793118075, 1793127265, "USD", "cardigan knit"),
    ("1099344326194954", "116809425000883", "Cyrus", "The Pointelle Button Cardigan | The Sleeveless Polo Knit", 1793117954, 1793123061, "USD", "cardigan knit"),
    ("2599511217183181", "1097556193447695", "CAKO-Cashmere", "100% Cashmere Cardigan | Timeless Fall Style", 1793067815, 1793124796, "USD", "cardigan knit"),
    ("3416557831856432", "195828260501505", "M.M.LaFleur", "Structured. Stretchy. Always Sharp.", 1793117380, 1793122946, "USD", "cardigan knit"),
    ("1468701941828045", "380039845369159", "SHEIN", "Floral Boho Maxi Dress | Dark Grey Round Neck Cardigan | Black Sequin Mini Skirt | Pleated Maxi Dress | Straight Leg Jeans | Mini Shirt Dress", 1793021520, 1793123671, "USD", "cardigan knit"),
    ("1842669363556247", "1138829009319029", "Nurestia", "Still Looks New A Year Later", 1792896080, 1792930536, "USD", "fall outfit boots"),
    ("1523718129568321", "107330521849008", "Emily Ash Rawlings", "Vintage Sag Harbor 100% Wool 1990's Oversized Blazer – Classic Camel Tan – Size 12", 1793136396, 1793142543, "USD", "fall outfit boots"),
    ("1453120983626029", "107330521849008", "Emily Ash Rawlings", "Vintage Sag Harbor 100% Wool 1990's Oversized Blazer – Gray – Size 12", 1793136192, 1793144125, "USD", "fall outfit boots"),
    ("1099484936392853", "92544812222", "Ellie Clothing", "Live Sale!", 1793135896, 1793140856, "USD", "fall outfit boots"),
    ("1542949847589072", "223704297783884", "Image Boutique", "The Denim Dress of the Season", 1793135375, 1793146157, "USD", "fall outfit boots"),
    ("1135897368963697", "132855737420", "Overland Sheepskin Co.", "", 1793130889, 1793142665, "USD", "fall outfit boots"),
    ("953422817470466", "255910574521332", "Hello Jenna Wood", "Under $20 Fall Find", 1793125980, 1793131018, "USD", "fall outfit boots"),
    ("942167375643298", "216801006201", "Super Shoes", "Boots Worth Coming Back For", 1793125712, 1793130978, "USD", "fall outfit boots"),
    ("1133681259165498", "216801006201", "Super Shoes", "Boots Worth Coming Back For", 1793125683, 1793131036, "USD", "fall outfit boots"),
    ("1058413400552412", "821976434323597", "Shapecurve", "💖One pair, way fewer outfit changes.", 1793122137, 1793141254, "USD", "fall outfit boots"),
    ("2251472722064093", "920789787775166", "Cart Ritual", "sweater dresses for thanksgiving dinner", 1793139422, 1793144900, "USD", "sweater dress"),
    ("1649097090081319", "218728444963600", "Glamour Farms", "Mixed Emotions Washed Crocheted Detail Pullover", 1793138070, 1793142811, "USD", "sweater dress"),
    ("1656604856083934", "1481590761693607", "Festève", "Candy-Cane Beaded Trim Mini · $150 | Mistle-Bow Frill Mini Dress · $125 | Snowflake Fair Isle Two-Piece · $130", 1793137687, 1793144841, "USD", "sweater dress"),
    ("1869360707391712", "1010103632410348", "Cuts", "The Only Long Sleeve Worth Wearing", 1793136335, 1793142273, "USD", "sweater dress"),
    ("1427941959494174", "268510116493233", "Mixology Clothing Co.", "The Main Line Covered Button Sweater", 1793136028, 1793140814, "USD", "sweater dress"),
    ("29316677711258577", "1138829009319029", "Nurestia", "Cozy From Every Angle", 1792896020, 1792916748, "USD", "cozy knit"),
    ("1632398571947068", "1138829009319029", "Nurestia", "Fall's Coziest Pair Of Boots", 1792896002, 1792915866, "USD", "cozy knit"),
    ("1418067733270037", "103371331147676", "IdPearl Boutique", "Eleven Six Mina Cardigan | Eleven Six Ada Cable Vest | Cara & The Sky Candice Cardigan | Shop all new fall arrivals", 1792611363, 1792691370, "USD", "boutique new arrivals cardigan"),
]


def main():
    seen, rows = set(), []
    for a in ADS:
        if a[0] not in seen:
            seen.add(a[0])
            rows.append(a)
    rows.sort(key=lambda a: a[5])  # longest running first
    rows = rows[:100]
    per_page = Counter(a[2] for a in rows)
    same_head = Counter((a[2], a[3]) for a in rows)
    fmt = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["rank", "ad_id", "page_name", "page_id", "headline", "created", "started_running", "days_running",
                    "ads_from_page_in_list", "copies_same_headline", "currency", "found_by_search", "snapshot_url"])
        for i, (aid, pid, page, head, created, start, cur, search) in enumerate(rows, 1):
            days = round((PULLED - dt.datetime.fromtimestamp(start, dt.timezone.utc)).total_seconds() / 86400, 1)
            w.writerow([i, aid, page, pid, head, fmt(created), fmt(start), days, per_page[page], same_head[(page, head)],
                        cur, search, f"https://www.facebook.com/ads/library/?id={aid}"])
    print(f"{len(rows)} ads, {len(per_page)} pages -> {OUT}")
    for r in rows[:5]:
        print(r[0], r[2], "|", r[3][:60], "|", fmt(r[5]))


if __name__ == "__main__":
    main()
