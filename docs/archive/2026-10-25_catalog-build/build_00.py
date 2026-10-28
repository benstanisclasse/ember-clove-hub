import json, csv, statistics, os
from collections import Counter

BASE = r"C:\Users\Administrator\Documents\EmberClove-Hub\research\tiktok\ads"
ids = open(os.path.join(BASE, "ids_part_00.txt"), encoding="utf-8").read().split()
meta = {}
with open(os.path.join(BASE, "topads_womens_clothing_US_180d_2026-10-25.tsv"), encoding="utf-8") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        meta[r["id"]] = r

STD_MISSING = "No conversion/ROAS/spend data; CTR is a percentile rank only (curated Top Ads sample, survivorship); audio not listened to (transcript + frames only)"

ADS = {}
def A(i, **kw):
    ADS[i] = kw

A("7199572939681972225",
  product="Adhesive stick-on push-up / 'invisible gathering' bra (nude silicone-style cups)", product_brand=None, category="bra",
  language="English", audience_apparent="Young women wearing off-shoulder/strapless tops who want lift without straps",
  format="product demo", presenter="creator face",
  first_frame="Woman in white off-shoulder crop top holds a pair of nude adhesive bra cups in front of her chest; doorway/indoor background; meme text at top",
  first_spoken_line="People always coming at me like, oh my god, you're gonna look really plastic.",
  opening_text_on_screen="When someone says they can tell I'm wearing a push up bra",
  initial_motion="subject movement", hook_category="trend/sound", hook_secondary="relatable frustration (meme framing)",
  audience_callout={"present": False, "words": None}, emotional_appeal="Humour / defiant confidence (embracing the 'fake' look)",
  product_visible_by_s=0.0, implied_problem="Wanting visible lift under strapless/off-shoulder tops; worry it looks fake",
  sequence="0-1.5s holds cups to chest under meme text; 1.5-4s peels/handles cups; 4-6s sticks them on under the top; 6-8.2s lifted result shown",
  cuts_per_10s=0.0, narration="creator talk (possibly a lip-synced trending sound; unclear)", captions="no", music="unclear",
  demonstration="Peeling and applying the adhesive cups on body, result under the top",
  curiosity_gap="Mild: how it looks once applied", payoff_timing_s=7.0, product_intro_s=0.0, brand_intro_s=None,
  benefits="Visible lift/cleavage; (caption) reusable, won't fall off", proof="try-on on body", objection_handling=None,
  offer="none", cta=None,
  observed="Single uncut 8 s take; product in hand from frame 1; meme text overlay; no offer or CTA in video.",
  interpretation="Ultra-short, one-take demo where the product is the first thing seen and the payoff arrives inside 8 s. The meme text turns a common objection (looks fake) into a joke, which may drive comments/shares. Mid-pack CTR rank (0.17) for a TikTok Shop seller account.",
  missing_extra="Caption truncated in TSV; whether audio is her own voice or a sound is unclear",
  transcript_flags=None, confidence="medium")

A("7242174026750885890",
  product="High-waist tummy-control shaping thong (black)", product_brand=None, category="shapewear",
  language="English", audience_apparent="Women ~30-45 bothered by lower-belly 'muffin top' in fitted dresses",
  format="before-after", presenter="creator face",
  first_frame="Cropped view of a woman's midsection: black floral crop top, low black briefs, bare belly; mouth open, face partly out of frame",
  first_spoken_line="Where has this sorcery been all my life?", opening_text_on_screen=None,
  initial_motion="subject movement", hook_category="visual transformation", hook_secondary="relatable frustration",
  audience_callout={"present": False, "words": None}, emotional_appeal="Relief + self-deprecating humour about muffin top",
  product_visible_by_s=1.5, implied_problem="Muffin top / belly bulge showing through fitted dresses",
  sequence="0-2.7s belly shown, pulls shaping thong up; 2.7-8.4s in blue ribbed midi dress talking about muffin top; 8.4-11s 'waist has disappeared'; 11-15s red off-shoulder dress + BOGO offer",
  cuts_per_10s=2.0, narration="creator talk", captions="no", music="unclear",
  demonstration="Pulling on the shaping thong, then wearing two fitted dresses over it",
  curiosity_gap="'Here's what to do about it' (6-8.4s) before reveal", payoff_timing_s=8.4, product_intro_s=1.5, brand_intro_s=None,
  benefits="Smooth waist under any outfit", proof="try-on on body (before/after)", objection_handling=None,
  offer="Buy one get one free (spoken ~12.5s); ad title 'only $9 today!'", cta="No explicit CTA; offer line at ~12.5s",
  observed="Bare-belly before shot at 0s, product on by 1.5s, two dress reveals, BOGO spoken at the end.",
  interpretation="Classic shapewear before/after with the 'problem' body shown in frame 1 and an honest, self-deprecating script. The offer arrives last, so viewers who drop early never hear it.",
  missing_extra=None,
  transcript_flags="'leaving it in a mile' garbled; 'waste'=waist; 'by one get one free'=buy one get one free", confidence="high")

A("7272762760945041409",
  product="High-waist tummy-control shaping brief (nude)", product_brand=None, category="shapewear",
  language="Malay (ad caption); no speech in video", audience_apparent="Women wanting a smooth silhouette under bodycon knitwear",
  format="before-after", presenter="creator face",
  first_frame="Young woman in taupe ribbed knit midi dress holds up a nude high-waist brief with both hands against a grey wall",
  first_spoken_line=None, opening_text_on_screen=None,
  initial_motion="subject movement", hook_category="visual transformation", hook_secondary="unexpected demo",
  audience_callout={"present": False, "words": None}, emotional_appeal="Aspirational silhouette / confidence",
  product_visible_by_s=0.0, implied_problem="Belly and bum shape under clingy dresses",
  sequence="0-1.4s holds the brief; 1.4-2.4s side profile, dress lifted, bare belly, pulls brief up; 2.4-3.4s dress back down, smoothed side profile; 3.4-6.9s rear view of dress silhouette",
  cuts_per_10s=4.37, narration="none", captions="no", music="yes (continuous non-speech audio; inferred, not listened)",
  demonstration="Putting the brief on under the knit dress and showing side/rear silhouette",
  curiosity_gap=None, payoff_timing_s=3.0, product_intro_s=0.0, brand_intro_s=None,
  benefits="(caption, Malay) high-waist tummy control, bum shaping", proof="try-on on body (before/after)", objection_handling=None,
  offer="none", cta=None,
  observed="6.9 s, no words on screen, no speech; product in hand at 0s; before/after done in ~3 s.",
  interpretation="The shortest ad in the batch and the second-best CTR rank (0.04) with the most likes of any apparel ad in the batch (119k; only the app ad has more) on the lowest budget level. The whole story is told visually in 3 s, so it works without language.",
  missing_extra="Caption is Malay but the ad was surfaced in the US women's clothing list; seller name is 'sale'",
  transcript_flags="Only segment (4.6-6.6s, no_speech_prob 0.72) is spurious; likely music", confidence="high")

A("7295590434121449474",
  product="Black lace bodysuit with nude lining", product_brand=None, category="top (bodysuit)",
  language="English", audience_apparent="Women 20-35 looking for going-out / office outfit ideas",
  format="UGC try-on/haul", presenter="creator face",
  first_frame="Woman in long grey ribbed knit holds a black lace bodysuit up by its straps in a white room with a plant; TikTok watermark",
  first_spoken_line="I'm going to be wearing this gorgeous, popular, body suit, I just got.",
  opening_text_on_screen=None, initial_motion="subject movement", hook_category="creator discovery", hook_secondary="styling listicle (caption: 3 ways to style)",
  audience_callout={"present": False, "words": None}, emotional_appeal="Aspiration / feeling sexy and put-together",
  product_visible_by_s=0.0, implied_problem="Basic outfits feel plain",
  sequence="0-5.6s holds bodysuit, shows back; 5.6-10s look 1 with beige wide pants + blazer; 10-13s look 2 burgundy leather pants + cream jacket; 13-19.8s look 3 navy pants + denim jacket, CTA",
  cuts_per_10s=3.03, narration="creator talk / voiceover over looks", captions="no", music="unclear",
  demonstration="Same bodysuit styled three ways",
  curiosity_gap="Implied by '3 ways to style' caption", payoff_timing_s=7.0, product_intro_s=0.0, brand_intro_s=None,
  benefits="Comfortable, elevates a basic outfit, sexy", proof="try-on on body", objection_handling=None,
  offer="none", cta="'you can actually shop now. There's a link at the bottom' (~17.5-19.7s)",
  observed="Product held at 0s, three outfit looks, spoken shop-now CTA at the end; repost with TikTok watermark.",
  interpretation="Versatility ('3 ways') gives one item multiple reasons to buy. The spoken hook is generic and the strongest promise sits in the caption rather than on screen.",
  missing_extra="Brand/seller not named in TSV or video",
  transcript_flags="'dressy post-traffitist' garbled (unclear)", confidence="medium")

A("7338465339167490050",
  product="Asymmetric knit sweater (shown with matching relaxed knit pants)", product_brand="JAKI (logo on screen)", category="top (knitwear)",
  language="English (on-screen text); no speech", audience_apparent="Women 25-45, premium/minimalist loungewear",
  format="brand/studio", presenter="creator face",
  first_frame="Model in tan vest and oatmeal wide-leg knit pants holds a grey asymmetric knit on a hanger (tag visible) against a pleated cream wall; JAKI logo and text block",
  first_spoken_line=None,
  opening_text_on_screen="Soft & luxurious / Our iconic Asymmetric knit is unbelievably flattering / Layer with our lace vests / Styled here with our matching Relaxed Pants",
  initial_motion="subject movement", hook_category="direct benefit", hook_secondary=None,
  audience_callout={"present": False, "words": None}, emotional_appeal="Comfort / understated luxury",
  product_visible_by_s=0.0, implied_problem=None,
  sequence="0-0.7s knit on hanger; 0.7-2.9s pulls it over her head; 2.9-9.5s turns and poses showing the drape",
  cuts_per_10s=2.11, narration="none", captions="no", music="yes (continuous non-speech audio; inferred, not listened)",
  demonstration="Putting the knit on and showing how it drapes",
  curiosity_gap=None, payoff_timing_s=3.0, product_intro_s=0.0, brand_intro_s=0.0,
  benefits="Soft, luxurious, flattering, layerable, matching set", proof="try-on on body", objection_handling=None,
  offer="none", cta=None,
  observed="9.5 s, static text block for the whole video, logo from frame 1, no CTA; ad title 'Most-wanted knits are back!' (restock framing).",
  interpretation="Clean brand lookbook: hanger-to-body in 3 s. Small static copy and no verbal hook make it closer to catalogue content; CTR rank 0.15 sits in the lower half of this batch.",
  missing_extra="Advertiser name blank in TSV",
  transcript_flags="No speech detected", confidence="high")

A("7343186537940090882",
  product="Tummy-control compression leggings", product_brand="Halara", category="leggings",
  language="English", audience_apparent="Mothers / women 30+ wanting stomach support",
  format="creator UGC talking", presenter="creator face",
  first_frame="Woman in brown fleece half-zip and navy leggings against a stone wall, talking; yellow down-arrow and text overlay",
  first_spoken_line="Guys, Halores, tummy control leggings just came in the mail, but let me just tell you this.",
  opening_text_on_screen="Limited Discounts ✨HALARA✨",
  initial_motion="subject movement", hook_category="creator discovery", hook_secondary="offer/price (on-screen text)",
  audience_callout={"present": True, "words": "I'm a mother of two from 2c section (~15.7s; self-identification aimed at mums)"},
  emotional_appeal="Relatability (post-pregnancy body) and comfort",
  product_visible_by_s=0.0, implied_problem="Post-pregnancy / C-section stomach needs support",
  sequence="0-15.7s praise: most flattering, comfortable compression leggings; 15.7-24s mother of two / C-section; 24-31s snaps waistband for 'sandwich compression' sound; 31-48.6s softness, back design, turns to show rear fit",
  cuts_per_10s=0.0, narration="creator talk", captions="no", music="unclear",
  demonstration="Snapping the waistband for sound; turning to show rear fit",
  curiosity_gap="'let me just tell you this' / 'Do you hear that?'", payoff_timing_s=29.0, product_intro_s=0.0, brand_intro_s=0.0,
  benefits="Flattering, comfortable, compression that 'sucks everything in', buttery soft, flattering back cut", proof="try-on on body; sound/compression demo", objection_handling=None,
  offer="'Limited Discounts' text (0-7s), no amount", cta="No spoken CTA; yellow arrow pointing down persists throughout",
  observed="Single uncut take, brand name in text and speech from 0s, discount text early, no spoken CTA.",
  interpretation="Native-looking creator testimonial with a personal credibility line (mother of two). The single 48 s take is slow, but the persistent arrow and discount text keep a shopping cue on screen. CTR rank 0.09 is upper half.",
  missing_extra=None,
  transcript_flags="'Halores'=Halara; '2c section' probably 'two C-sections'; 'have to cut in the back' unclear", confidence="high")

A("7348008745177251842",
  product="Zip-front long-sleeve waist-shaping bodysuit (cream and black)", product_brand=None, category="shapewear (bodysuit)",
  language="Spanish (on-screen text); no speech", audience_apparent="Spanish-speaking US women, curvy, fall outfits",
  format="UGC try-on/haul", presenter="creator face",
  first_frame="Woman in glasses, brown top, olive vest and jeans holds a cream bodysuit toward the camera in a living room with fairy lights; TikTok watermark",
  first_spoken_line=None, opening_text_on_screen="Body moldeador de cintura! Para este otoño 🍁",
  initial_motion="subject movement", hook_category="direct benefit", hook_secondary="seasonal",
  audience_callout={"present": False, "words": None}, emotional_appeal="Confidence / feeling sexy",
  product_visible_by_s=0.0, implied_problem="Waist definition",
  sequence="0-3s shows cream then black bodysuit with text; ~5s blurred transition; 7-15s wears black bodysuit, turns, close-up; 17-21s bodysuit with jeans and boots, text recommending it; 21-23s back view",
  cuts_per_10s=3.48, narration="none (song/music)", captions="no", music="yes (continuous non-speech audio; inferred, not listened)",
  demonstration="Transition from holding to wearing; styled with jeans",
  curiosity_gap="Transition reveal", payoff_timing_s=7.0, product_intro_s=0.0, brand_intro_s=None,
  benefits="Waist shaping, sexy, fall-ready", proof="try-on on body", objection_handling=None,
  offer="none", cta=None,
  observed="Spanish text overlays, no speech, transition reveal at ~5s, repost with TikTok watermark.",
  interpretation="Hold-up then transition-reveal format works without speech. Spanish copy targets a Spanish-speaking US segment; CTR rank 0.05 is among the best in the batch.",
  missing_extra="Advertiser name blank in TSV",
  transcript_flags="Transcript only 'and' / 'Thanks.' - no usable speech", confidence="medium")

A("7364141843464781840",
  product="'TikTok pocket leggings' (black, multipack)", product_brand=None, category="leggings",
  language="English", audience_apparent="Tall/curvy, budget-conscious women",
  format="creator UGC talking", presenter="creator face",
  first_frame="Woman in denim jacket and black leggings turned away from camera showing rear fit, looking back over her shoulder; bedroom; TikTok watermark",
  first_spoken_line="You guys loved these leggings last time I posted.",
  opening_text_on_screen="TikTok pocket leggings Q&A - I'm answering all your questions! (from ~2s; none at 0-1.5s)",
  initial_motion="subject movement", hook_category="social proof", hook_secondary="curiosity gap (Q&A)",
  audience_callout={"present": False, "words": None}, emotional_appeal="Trust / value",
  product_visible_by_s=0.0, implied_problem="Finding leggings that fit tall/curvy bodies and aren't see-through",
  sequence="0-1.6s rear-view turn; 1.6-12s Q&A intro + price ($20 for 3, free shipping text at ~9s); 12-21s height and size Q&A, squats; 23-27s see-through question, hands stretch fabric close-up; 28-31s summer/fleece-lined; 31-34s stack of ~15 pairs, 'Link below' text",
  cuts_per_10s=3.81, narration="creator talk", captions="partial (Q&A text overlays, not word-for-word)", music="unclear",
  demonstration="Bend/squat test, hand stretch close-up, showing a pile of owned pairs",
  curiosity_gap="Q&A answers", payoff_timing_s=23.0, product_intro_s=0.0, brand_intro_s=None,
  benefits="Stretchy, buttery soft, not see-through, true to size, works for tall and short, breathable",
  proof="try-on on body; squat/bend test; stretch test; numbers (owns ~15 pairs)",
  objection_handling="See-through ('pass the light and squat test'), size (XL, true to size), height (5'9\"), summer heat (fleece-lined option)",
  offer="'$20.36 for 3 pairs!! & Free Shipping!' (text ~9s; spoken '$20 for three pairs' ~8.2s)",
  cta="'Link below! Run while they're still on sale!!!' (text ~33s)",
  observed="FAQ structure answering objections one by one in text overlays, price shown early, CTA text at the end.",
  interpretation="Best CTR rank in the batch (0.03). It handles the main leggings objections (see-through, size, height) and gives a clear per-unit value in the first 10 s. Follow-up 'you asked' framing borrows social proof from an earlier viral post.",
  missing_extra="Advertiser name blank in TSV",
  transcript_flags="'payers'=pairs", confidence="high")

A("7369124804521115666",
  product="Vintage-style summer dresses (white polka-dot midi, red gingham mini, cream shift)", product_brand=None, category="dress",
  language="English (on-screen text); audio is a song", audience_apparent="Women 20-35 into vintage/retro aesthetic",
  format="UGC try-on/haul", presenter="creator face",
  first_frame="Close view of woman in a white satin lace robe holding a white red-polka-dot dress on a hanger; room with dress forms; text overlay",
  first_spoken_line=None, opening_text_on_screen="summer dresses but make it OLD HOLLYWOOD",
  initial_motion="handheld", hook_category="other", hook_secondary="aesthetic/era theme ('Old Hollywood')",
  audience_callout={"present": False, "words": None}, emotional_appeal="Nostalgia / glamour",
  product_visible_by_s=0.0, implied_problem=None,
  sequence="0-3.7s robe, dresses on hangers; 3.7-8.5s polka-dot midi with vintage photos on wall; 8.5-13s red gingham mini; 13-17.4s cream shift dress with camera prop",
  cuts_per_10s=4.03, narration="song", captions="no", music="yes",
  demonstration="Try-on of three dresses styled against vintage reference photos",
  curiosity_gap=None, payoff_timing_s=5.0, product_intro_s=0.0, brand_intro_s=None,
  benefits="Retro look", proof="try-on on body", objection_handling=None,
  offer="none in video (ad title 'up to 80% off')", cta=None,
  observed="Aesthetic try-on set to a song, no spoken claims, offer only in the caption.",
  interpretation="High-production aesthetic content; the theme is strong but there is no functional benefit or CTA in the video. CTR rank 0.19 is in the bottom third of the batch.",
  missing_extra=None,
  transcript_flags="Transcript repeats 'I'm a good player' - lyrics mis-transcribed; not usable", confidence="medium")

A("7380169202270552065",
  product="Scoop-neck shaping bodysuit (olive)", product_brand=None, category="shapewear (bodysuit)",
  language="English", audience_apparent="Women 18-30 wanting a snatched waist in jeans",
  format="creator UGC talking", presenter="creator face",
  first_frame="Close-up of woman in an olive shaping bodysuit with unbuttoned white jeans, talking to camera in a bedroom; bold headline text",
  first_spoken_line="I look small. I fit in like one little grid line.",
  opening_text_on_screen="THIS BODYSUIT ERASED MY WAIST😮 (emoji approximate)",
  initial_motion="handheld", hook_category="unexpected outcome", hook_secondary="visual transformation",
  audience_callout={"present": False, "words": None}, emotional_appeal="Surprise / excitement, exaggerated disbelief",
  product_visible_by_s=0.0, implied_problem="Jeans too tight at the waist / wanting a smaller waist",
  sequence="0-7s close-up talking under headline; 7-11s shocked reaction; 11-33s works the white jeans (claims size 00, fresh from the wash) up and buttons them; 33-50s turns, shows fit, repeated reactions",
  cuts_per_10s=2.0, narration="creator talk", captions="no", music="unclear",
  demonstration="Fitting into small jeans while wearing the bodysuit",
  curiosity_gap="Will the jeans fit?", payoff_timing_s=33.0, product_intro_s=0.0, brand_intro_s=None,
  benefits="Compresses waist so smaller jeans fit", proof="try-on on body; fitting into size-00 jeans (claimed)", objection_handling=None,
  offer="none", cta=None,
  observed="Headline promise at 0s, long jeans-fitting demo, no CTA or offer; ad caption compares the effect to Ozempic.",
  interpretation="Strong outcome-first headline plus a 'will it fit' tension that holds attention. Rank 0.06 with 78k likes. The weight-loss-drug comparison in the caption is a policy/brand-safety risk to avoid copying.",
  missing_extra="Exact garment brand not visible",
  transcript_flags="Opening lines and 32-51s heavily garbled ('brat. Says', 'isn't seen'); detector cuts_per_10s 1.0 corrected to ~2 because the sheet shows several jump cuts/reframings", confidence="medium")

A("7380329994080534544",
  product="Pull-on wide-leg jeans (elastic waist, no zip)", product_brand="Halara", category="jeans",
  language="English voiceover (ad caption German: 'Bis zu 50% Rabatt')", audience_apparent="Women 25-45 moving from skinny to wide-leg, comfort-first",
  format="voiceover b-roll", presenter="body only",
  first_frame="Close crop of torso/hips in black crop top and mid-blue wide-leg jeans walking toward the camera; text overlay",
  first_spoken_line="Good-bye skinny jeans. These are the new wide-leg jeans to wear.",
  opening_text_on_screen="Goodbye skinny jeans. These are the new wide leg jeans to wear :",
  initial_motion="subject movement", hook_category="contrarian", hook_secondary="trend",
  audience_callout={"present": False, "words": None}, emotional_appeal="Being on-trend + comfort",
  product_visible_by_s=0.0, implied_problem="Skinny jeans feel dated/uncomfortable",
  sequence="0-4.5s walking hook; 4.5-13s waist features (high waist, no zippers, pockets); 13-19s 4-way stretch, wide leg; 19-29s rear, elastic waistband, 'perfect for everyday wear'; 29-32.7s full-body + Halara end card 'SHOP NOW'",
  cuts_per_10s=3.5, narration="voiceover", captions="partial (feature labels)", music="unclear",
  demonstration="Close-ups of waistband, pockets, stretch pulled by hand, walking",
  curiosity_gap=None, payoff_timing_s=5.0, product_intro_s=0.0, brand_intro_s=31.0,
  benefits="High waist, no zippers, multiple pockets, 4-way stretch, wide leg, elastic waistband, everyday wear", proof="try-on on body; stretch shown by hand", objection_handling=None,
  offer="none in video (caption 'Bis zu 50% Rabatt' = up to 50% off)", cta="'Shop now' VO ~29s + end-card button ~31s",
  observed="Feature-list VO over faceless b-roll; brand only on the end card.",
  interpretation="Clear trend-shift hook but then a flat spec list with no person or proof beyond on-body shots. Same script reused in 7416283009659371536 with a different hook; this version ranks lower (0.15 vs 0.12).",
  missing_extra="Served from halara_europe with German caption; US relevance unclear",
  transcript_flags="'Fourth waist stretch'=4-way stretch; 'Facts for everyday wear'=Perfect for everyday wear; 'Shout now'=Shop now; detector 0.92 cuts/10s corrected to ~3.5 (sheet shows ~12 distinct shots)", confidence="high")

A("7382049390817558545",
  product="Cross-border shopping app for Japanese fashion (app icon letter 'D'; app name not visible)", product_brand=None, category="other (shopping app / marketplace)",
  language="English (on-screen text); no speech", audience_apparent="Fans of Japanese street styles (Harajuku, Lolita, Jirai-kei)",
  format="other", presenter="none",
  first_frame="Shop display of bows, hair accessories and pink/black lace items; large glowing pink text",
  first_spoken_line=None, opening_text_on_screen="Japanese Fashion / With One click / Harajuku style Lolita Jiraikei",
  initial_motion="fast cut", hook_category="callout of audience", hook_secondary="curiosity gap",
  audience_callout={"present": True, "words": "Harajuku style Lolita Jiraikei"}, emotional_appeal="Novelty / access to niche fashion",
  product_visible_by_s=1.5, implied_problem="Hard to buy Japanese fashion from abroad",
  sequence="0-1.2s 'Japanese Fashion' store shots; 1.5-2.1s app icon with tap cursor 'With One click'; 2.1-5.5s style names over racks; 5.5-8s 'Buy From Japan'; 8-9.2s 'Claim Your Perks Now'",
  cuts_per_10s=9.78, narration="none", captions="no", music="yes (continuous non-speech audio; inferred, not listened)",
  demonstration=None, curiosity_gap=None, payoff_timing_s=None, product_intro_s=1.5, brand_intro_s=None,
  benefits="Buy Japanese fashion with one click", proof="none", objection_handling=None,
  offer="'perks' (unspecified)", cta="'Claim Your Perks Now' (~7-9s)",
  observed="9 s fast-cut montage with large text only; traffic objective; 212k likes.",
  interpretation="Not an apparel brand ad - an app install/traffic ad placed in the category. Very fast cutting and niche style callouts; CTR rank 0.24 is near the bottom. Low relevance as a creative model for Ember & Clove.",
  missing_extra="App/brand name not visible; advertiser blank in TSV",
  transcript_flags="No speech detected", confidence="medium")

A("7383349441418870801",
  product="Teal/black mandala-print maxi cami dress", product_brand=None, category="dress",
  language="English", audience_apparent="Plus-size women, budget TikTok Shop buyers",
  format="UGC try-on/haul", presenter="creator face",
  first_frame="Mirror selfie: woman in teal mandala-print maxi dress holding her phone in a bedroom with a pink rug",
  first_spoken_line="Okay, so I also got this dress on the TikTok shop.",
  opening_text_on_screen=None, initial_motion="handheld", hook_category="creator discovery", hook_secondary=None,
  audience_callout={"present": True, "words": "'Click that link below, ladies' (~20.8s, CTA not hook)"}, emotional_appeal="Casual enthusiasm",
  product_visible_by_s=0.0, implied_problem=None,
  sequence="0-6s got it on TikTok Shop, accidentally ordered 2XL; 6-13s could size down, flowy, likes it; 13-20s four colours, wants the black; 20.8-24.4s CTA",
  cuts_per_10s=0.0, narration="creator talk", captions="no", music="unclear",
  demonstration="Mirror try-on, turning", curiosity_gap=None, payoff_timing_s=None, product_intro_s=0.0, brand_intro_s=None,
  benefits="Flowy, cute, four colours", proof="try-on on body", objection_handling="Sizing (ordered 2XL, could have gone down)",
  offer="none", cta="'Click that link below, ladies. Get yours today' (20.8-24.4s)",
  observed="Unpolished one-take mirror selfie with spoken CTA.",
  interpretation="Low-production, authentic haul. Sizing honesty may help plus-size buyers, but there is no hook beyond 'I got this'. CTR rank 0.12 is mid.",
  missing_extra="Advertiser name blank in TSV",
  transcript_flags="'within material'=unclear", confidence="high")

A("7385349613774143489",
  product="Double-lined fitted cami/tank top (blue, white)", product_brand=None, category="top",
  language="English (caption only); no speech", audience_apparent="Women 18-25, basics",
  format="UGC try-on/haul", presenter="creator face",
  first_frame="Young blonde woman in a blue fitted cami and grey sweatpants posing in a living room with a ceiling fan",
  first_spoken_line=None, opening_text_on_screen=None,
  initial_motion="subject movement", hook_category="other", hook_secondary="aesthetic try-on, no verbal or text hook",
  audience_callout={"present": False, "words": None}, emotional_appeal="Aspirational / playful",
  product_visible_by_s=0.0, implied_problem=None,
  sequence="0-1.6s full-body pose, blue cami; 1.6-4s close-up of fit; 4-7s full body, playful faces; 7-9s white cami full body; 9-10.6s white cami close-up",
  cuts_per_10s=6.59, narration="none", captions="no", music="yes (continuous non-speech audio; inferred, not listened)",
  demonstration="Try-on in two colours with fit close-ups", curiosity_gap=None, payoff_timing_s=2.0, product_intro_s=0.0, brand_intro_s=None,
  benefits="(caption only) double lined, soft, good quality, white not see-through, size down", proof="try-on on body (two colours)", objection_handling="(caption only) white isn't see-through; sizing advice",
  offer="none", cta=None,
  observed="10.6 s, no words in video, product worn from frame 1, fast cutting; all claims in the caption.",
  interpretation="Pure visual try-on; the close-ups at 2s and 9s answer quality/see-through questions visually. CTR rank 0.08 and 67.5k likes from a no-copy video suggest the look itself carries it.",
  missing_extra="Advertiser name blank in TSV",
  transcript_flags="No speech detected", confidence="medium")

A("7397326487299719185",
  product="Olive denim shacket with raw/fringed hem", product_brand=None, category="outerwear",
  language="English", audience_apparent="Women 30-45, teachers/school staff, budget-minded",
  format="creator UGC talking", presenter="creator face",
  first_frame="Woman in olive raw-hem denim jacket over a striped tee and jeans in a white-tiled bathroom, talking and gesturing",
  first_spoken_line="I'm already thinking about fall if you work in a school, you know, it's coming",
  opening_text_on_screen=None, initial_motion="handheld", hook_category="callout of audience", hook_secondary="offer/price (5s)",
  audience_callout={"present": True, "words": "if you work in a school"}, emotional_appeal="Seasonal anticipation / value",
  product_visible_by_s=0.0, implied_problem="Need a light layer for chilly fall days",
  sequence="0-5s fall/school hook; 5-11s under $30 + free shipping, raw hem; 11-25s stretch, size M, colours; 25-45s lightweight, quality, vs an $80 version; 45-62s use case for chilly/windy days; 63-80s colours, styling; 80-91s link below, 'they don't last'",
  cuts_per_10s=0.0, narration="creator talk", captions="no", music="unclear",
  demonstration="Wearing, rolling sleeves, showing hem and fit", curiosity_gap=None, payoff_timing_s=None, product_intro_s=0.0, brand_intro_s=None,
  benefits="Stretch, flattering, lightweight, soft, good quality, several colours", proof="try-on on body; comparison (similar jacket $80 vs ~$30)",
  objection_handling="Price/quality ('honestly better quality' than $80 one); sizing (wearing M)",
  offer="'less than $30 with free shipping' (~5.1s)", cta="'linking it down below, grab it while it's affordable' (~80.5s); scarcity 'They don't last'",
  observed="91 s single-location talk; price and free shipping in the first 11 s; anchor price comparison at ~36s.",
  interpretation="Niche callout (school staff) + early price + anchor comparison is a strong value pitch. Rank 0.08 despite 91 s length suggests the first seconds carry the click.",
  missing_extra="Advertiser name blank in TSV; contact sheet only covers to 39s (extra frames checked at 45-89s)",
  transcript_flags="'raw ham'=raw hem; 'Sable piece'=staple piece; 'shame brain top' and 'kick top top' garbled; detector 0 cuts but framing changes at 9s/11s/13s suggest jump cuts or zoom", confidence="high")

A("7406218796128632833",
  product="High-waist 'snatching' leggings (black)", product_brand="Halara (spoken)", category="leggings",
  language="English", audience_apparent="Women 20-35, back-to-school/activewear",
  format="creator UGC talking", presenter="creator face",
  first_frame="Woman in black tank and black leggings mid-movement in a living room; text overlay",
  first_spoken_line="If your leggings claim to succulent but you don't have to do all these movements...",
  opening_text_on_screen="The Viral SNATCHING leggings definitely do their job 🔥",
  initial_motion="subject movement", hook_category="contrarian", hook_secondary="mistake avoidance",
  audience_callout={"present": False, "words": None}, emotional_appeal="Humour (exaggerated wiggles to pull them on)",
  product_visible_by_s=0.0, implied_problem="'Sucking-in' leggings that don't actually compress",
  sequence="0-8s high kick, squats, wiggling to show effort of pulling them on; 8-17s 'leggings from Halara', waistband sucks in; 17-21s pockets, colours, rear view; 21-26s close to camera, CTA + sell-out urgency",
  cuts_per_10s=0.38, narration="creator talk", captions="no", music="unclear",
  demonstration="Exaggerated pull-on movements; waistband; rear view", curiosity_gap=None, payoff_timing_s=12.6, product_intro_s=0.0, brand_intro_s=8.1,
  benefits="Comfy, tummy compression band, pockets, many colours", proof="try-on on body; movement", objection_handling="Implicitly: 'other leggings claim to suck you in but don't'",
  offer="none in video (caption 'Under 29$ TODAY!!')", cta="'I'll link it here below in this orange card' (~21s); 'before they sell out for back to school' (~22.7s)",
  observed="Movement-heavy contrarian hook, brand named at 8s, orange-card CTA.",
  interpretation="The hook converts tightness (an objection) into proof of compression, with humour. Mid rank (0.11).",
  missing_extra=None,
  transcript_flags="'succulent'=suck you in", confidence="high")

A("7408075217421844481",
  product="Tummy-control leggings (navy)", product_brand=None, category="leggings",
  language="English (on-screen text); audio is a song", audience_apparent="Women 30-45, casual fitness",
  format="other", presenter="creator face",
  first_frame="Woman in white tank and navy leggings dancing in a stockroom/store with a rack of leggings on the right wall; text overlay",
  first_spoken_line=None,
  opening_text_on_screen="The perfect tummy control leggings that don't move even when you workout or just dance wildly like no one is watching 🖤",
  initial_motion="subject movement", hook_category="trend/sound", hook_secondary="relatable (caption: 'Do you randomly just start dancing like this?')",
  audience_callout={"present": False, "words": None}, emotional_appeal="Joy / playfulness",
  product_visible_by_s=0.0, implied_problem="Leggings that slip during movement",
  sequence="0-3s dancing full body; 3-7s close-up smile, hand at waistband; 7-15s more dancing and jumps",
  cuts_per_10s=2.67, narration="song", captions="no", music="yes",
  demonstration="Dancing to show leggings stay in place", curiosity_gap=None, payoff_timing_s=None, product_intro_s=0.0, brand_intro_s=None,
  benefits="Tummy control; stays put during movement", proof="try-on on body (movement)", objection_handling=None,
  offer="none", cta=None,
  observed="Dance clip to a pop song with one long text overlay; no speech, no CTA.",
  interpretation="Personality-led dance content where the benefit lives only in the text. Rank 0.10, upper half of the batch.",
  missing_extra="Song not identified (lyrics not reproduced)",
  transcript_flags="Transcript is song lyrics, not speech", confidence="medium")

A("7416283009659371536",
  product="Pull-on wide-leg jeans (light and dark wash)", product_brand="Halara", category="jeans",
  language="English", audience_apparent="Women 25-45, comfort-first denim",
  format="voiceover b-roll", presenter="multiple",
  first_frame="Close crop: hands holding light-wash wide-leg jeans up by the waistband in front of a person's legs; text overlay",
  first_spoken_line="I bought three of these this month. Let me tell you why.",
  opening_text_on_screen="I bought 3 of these this month, let me tell you why.",
  initial_motion="fast cut", hook_category="curiosity gap", hook_secondary="social proof (repeat purchase)",
  audience_callout={"present": False, "words": None}, emotional_appeal="Comfort / FOMO",
  product_visible_by_s=0.0, implied_problem="Uncomfortable zip jeans",
  sequence="0-0.7s jeans held up; 0.7-3.6s worn, leg kick, mirror selfie; 3.6-6.5s dark pair held up; 6.5-17s feature labels (high waist, no zipper, pockets, wide leg, four-way stretch); 17-19s full body 'You'll never want to take it off!'; 19-20s Halara end card 'SHOP NOW'",
  cuts_per_10s=5.5, narration="voiceover", captions="partial (feature labels + hook/closing lines)", music="unclear",
  demonstration="Waistband and fit close-ups", curiosity_gap="'let me tell you why'", payoff_timing_s=6.6, product_intro_s=0.0, brand_intro_s=19.0,
  benefits="High waist, no zipper, pockets, wide leg, four-way stretch", proof="try-on on body", objection_handling=None,
  offer="none", cta="'Shop now' VO ~18.5s + end-card button ~19s",
  observed="Same feature script as 7380329994080534544 but with a first-person 'bought 3' hook, multiple models and shorter (20 s).",
  interpretation="A natural A/B within Halara: the curiosity/repeat-purchase hook version ranks better (0.12, 34k likes) than the 'goodbye skinny jeans' version (0.15, 10.7k). Confounded by length and market.",
  missing_extra=None,
  transcript_flags="'I waste design. No slippers'=High waist design. No zippers; 'Just now'=Shop now", confidence="high")

A("7416290513684955153",
  product="Two-piece ribbed knit set: sleeveless midi dress + cropped V-neck sweater (multiple colours)", product_brand=None, category="dress (two-piece set)",
  language="German (ad caption); no speech", audience_apparent="Women 25-45, casual-chic fall outfits",
  format="UGC try-on/haul", presenter="creator face",
  first_frame="Woman in sunglasses wearing a beige ribbed sleeveless midi dress and white sneakers, carrying the matching cropped sweater, on a sunny street with white buildings and palms",
  first_spoken_line=None, opening_text_on_screen=None,
  initial_motion="subject movement", hook_category="other", hook_secondary="aspirational lookbook (no verbal/text hook)",
  audience_callout={"present": False, "words": None}, emotional_appeal="Aspiration / effortless style",
  product_visible_by_s=0.0, implied_problem=None,
  sequence="0-6.5s beige set, puts sweater on while walking; 6.5-11.5s pink set; 11.5-17s fuchsia set; 17-26s blue set at a glass terrace, sweater on; 26-31s mint set",
  cuts_per_10s=2.9, narration="none", captions="no", music="yes (continuous non-speech audio; inferred, not listened)",
  demonstration="Wearing and layering the set in five colours", curiosity_gap=None, payoff_timing_s=None, product_intro_s=0.0, brand_intro_s=None,
  benefits="(caption) new fall item, two-piece set", proof="try-on on body (colour range)", objection_handling=None,
  offer="none", cta=None,
  observed="Lookbook-style colour parade, no text or speech.",
  interpretation="Colour variety and a sunny lifestyle setting do the selling; there are no claims or CTA. German caption on a US list. Rank 0.11 mid.",
  missing_extra="Advertiser shown as stylised 'TikTok Shop'",
  transcript_flags="No speech detected", confidence="medium")

A("7427043163971387399",
  product="Forme Power Bra (posture-support sports bra)", product_brand="Forme", category="bra",
  language="English", audience_apparent="Women 35-50, larger chest, posture concerns",
  format="creator UGC talking", presenter="creator face",
  first_frame="Green-screen: woman in a black crop bra in a lower-left inset over black-and-white rehearsal footage of a performer; 'Shorts' logo visible; caption",
  first_spoken_line="So I bought the form science bra the one Taylor Swift where...",
  opening_text_on_screen="So I bought the Forme Science bra / the one that Taylor Swift wears",
  initial_motion="fast cut", hook_category="social proof", hook_secondary="creator discovery (sceptical buyer)",
  audience_callout={"present": False, "words": None}, emotional_appeal="Sceptic-turned-believer; humour about large chest",
  product_visible_by_s=5.0, implied_problem="Slouching shoulders, poor posture, large-chest support",
  sequence="0-4.2s green-screen celebrity footage hook; 4-17s 'best financial decision? Probably not', what it claims; 17-23s ready to hate it/return it; 23-32s side profile, 'it actually does'; 32-41s comparison in a regular sports bra (slumped); 41-56.7s back in Forme, fit, 'Click the link' text",
  cuts_per_10s=2.12, narration="creator talk", captions="yes", music="unclear",
  demonstration="Side-profile posture in Forme vs a regular sports bra", curiosity_gap="'was this my best financial decision?'", payoff_timing_s=23.4, product_intro_s=5.0, brand_intro_s=0.0,
  benefits="Holds shoulders back, better posture, secure fit", proof="comparison (regular sports bra vs Forme); try-on on body",
  objection_handling="Price ('crazy' for a bra), scepticism, initial tightness ('a bit tight at first, but now it fits')",
  offer="none", cta="'Click the link' text (~55s)",
  observed="Celebrity footage via green screen in the first 4 s, burned-in captions, on-body comparison.",
  interpretation="Celebrity association + sceptic story + visible comparison is a strong persuasion stack, yet it has the second-worst rank in the batch (0.27), possibly because the product is not clearly shown until ~5s and length is 57s. Uses third-party celebrity footage - rights risk; do not copy.",
  missing_extra="Price stated in audio is garbled; watermark 'TikTok Business Creative Center'",
  transcript_flags="'where'=wears; 'I don't name dollars' garbled (price unknown); 'power bra'/'form bra' = Forme Power Bra", confidence="high")

A("7437867036929851408",
  product="Stretch work pants (high-waist, button-front, straight/flare)", product_brand="Halara", category="pants (trousers)",
  language="English", audience_apparent="Office-working women 25-45",
  format="voiceover b-roll", presenter="body only",
  first_frame="Close crop of legs pulling up black wide pants on a fluffy rug, shelves behind; text overlay",
  first_spoken_line="3 compelling reasons to ditch your office pants for Halara.",
  opening_text_on_screen="3 Compelling Reasons to Ditch Your Office Pants for Halara!",
  initial_motion="fast cut", hook_category="contrarian", hook_secondary="listicle / comparison",
  audience_callout={"present": True, "words": "your office pants"}, emotional_appeal="Comfort + confidence at work",
  product_visible_by_s=0.0, implied_problem="Work pants that don't fit and feel uncomfortable",
  sequence="0-3.6s hook; 3.6-15.6s #1 They Look AMAZING (rear fit, sculpt); 15.6-32.8s #2 casual Friday every day, waistband stretch pulled wide ~29s; 32.8-47s #3 style & functionality, 4-way stretch, butt-lifting, pockets, flat lays; 47-51.2s CTA",
  cuts_per_10s=6.25, narration="voiceover", captions="yes", music="unclear",
  demonstration="Waistband stretched wide by hand; squat; rear-fit shots", curiosity_gap="3-reason listicle", payoff_timing_s=4.6, product_intro_s=0.0, brand_intro_s=0.0,
  benefits="Sculpting fit, comfortable, breathable, 4-way stretch, butt-lifting, pockets", proof="try-on on body; stretch test",
  objection_handling="Comfort vs professional look", offer="none", cta="'Get yours now and say goodbye to those boring work pants for good' (~47.2s)",
  observed="Numbered listicle with captions and fast cuts; faces mostly cropped out.",
  interpretation="Clear structure and a stretch test give proof, and the office callout is specific. Rank 0.08 is in the top third despite 51 s length.",
  missing_extra=None,
  transcript_flags="'but lifting'=butt-lifting; 'There might go to pants'=They're my go-to pants", confidence="high")

A("7438597543263731713",
  product="'Viral' stretchy jeans (grey wash; straight-leg also mentioned)", product_brand="Katch Me (per title tag)", category="jeans",
  language="English", audience_apparent="Women 20-35, tall-ish, comfort denim",
  format="UGC try-on/haul", presenter="creator face",
  first_frame="Woman in black tee buttoning grey jeans with tags still attached, walk-in wardrobe behind",
  first_spoken_line="Shock have ordered another pair of the viral stretchy jeans.",
  opening_text_on_screen=None, initial_motion="subject movement", hook_category="social proof", hook_secondary="creator discovery (repeat purchase)",
  audience_callout={"present": False, "words": None}, emotional_appeal="Enthusiasm / obsession",
  product_visible_by_s=0.0, implied_problem="Jeans that gape at the back or are too short",
  sequence="0-6s doing up a new pair; 6-15s comfiest, fits like a glove, stretchy; 15-19s rear, no gaping; 19-27s length at 5'7\", leg up on drawer at ~25s; 27-31s holds bagged pairs; 31-36.7s size 6 at 5'7\", 'Perfect'",
  cuts_per_10s=1.36, narration="creator talk", captions="no", music="unclear",
  demonstration="High leg lift to show stretch; showing back waist and hem length", curiosity_gap=None, payoff_timing_s=15.2, product_intro_s=0.0, brand_intro_s=None,
  benefits="Very stretchy, comfortable, no back-gap, long leg length", proof="try-on on body; stretch (leg lift); multiple purchases shown",
  objection_handling="Back gaping; length for 5'7\"; size (6)", offer="none", cta=None,
  observed="Tags-on try-on, 'viral' + repeat-purchase framing, fit specifics, no CTA.",
  interpretation="Fit objections for denim (gap, length, size) are answered with specific numbers. Rank 0.07 with 47k likes; there is no explicit CTA.",
  missing_extra="Advertiser name blank in TSV",
  transcript_flags="'Shock' likely mis-transcribed; 'manual obsession' garbled; 'Si 6'=size 6", confidence="high")

A("7441225809438670856",
  product="Fleece-lined pantyhose (tan, sheer-look)", product_brand=None, category="hosiery (tights)",
  language="English", audience_apparent="Women 25-45 wearing dresses in cold weather",
  format="product demo", presenter="creator face",
  first_frame="Top-down close-up of legs in sheer-look tan tights and black knee boots on a rug; text overlay",
  first_spoken_line="Don't be fooled by other brands that say that these are the same thing.",
  opening_text_on_screen="Fleece Lined Pantyhose", initial_motion="handheld", hook_category="contrarian", hook_secondary="comparison",
  audience_callout={"present": False, "words": None}, emotional_appeal="Trust / insider advice",
  product_visible_by_s=0.0, implied_problem="Cold legs in dresses; thin tights that tear or show skin",
  sequence="0-6s leg close-up, nail scratch, 'don't be fooled'; 6-15s creator in beige sweater dress explains warmth; 15-19s scratch test; 19-32s scissors poke test, no skin colour through; 33-38s foot close-up, fleece stops at ankle; 38-43s four colours, links below",
  cuts_per_10s=2.08, narration="creator talk", captions="no", music="unclear",
  demonstration="Scratching with nails and poking with scissors to show durability/opacity", curiosity_gap="Which ones are 'the good ones'?", payoff_timing_s=23.8, product_intro_s=0.0, brand_intro_s=None,
  benefits="Thick, warm, doesn't tear, looks like skin, normal-looking foot, four colours", proof="stretch/durability test (nail scratch, scissors); comparison vs other brands (verbal)",
  objection_handling="Tearing, see-through, visible fleece at the foot", offer="none", cta="'I will have these links below' (~38.4s)",
  observed="Product on legs at 0s, two physical tests, explicit competitor contrast.",
  interpretation="Hands-on stress test gives visible proof for an otherwise invisible quality claim; strong seasonal relevance. Rank 0.07 (top 6).",
  missing_extra="Advertiser name blank in TSV",
  transcript_flags=None, confidence="high")

A("7441491158156541969",
  product="Waist trainer (hook-and-zip compression corset belt)", product_brand=None, category="shapewear",
  language="English", audience_apparent="Women 20-35 on fitness/body-recomposition journeys",
  format="creator UGC talking", presenter="creator face",
  first_frame="Woman in sage bikini-style top and black leggings in a tiled gym bathroom, hands at her chin; reply-to-comment sticker top-left; centred text",
  first_spoken_line="Okay, so I'm gonna do my best to explain how why and when waste training works",
  opening_text_on_screen="how/why/when waist training works (plus a small reply-to-comment sticker, not fully readable)",
  initial_motion="subject movement", hook_category="curiosity gap", hook_secondary="social proof (reply to comment)",
  audience_callout={"present": False, "words": None}, emotional_appeal="Aspiration / motivation, personal results",
  product_visible_by_s=13.0, implied_problem="Wanting a smaller waist during weight change",
  sequence="0-13s explainer intro; 13-22s puts on waist trainer (text: hooks AND zipper); 23-35s older clips with comment sticker, 175 lbs vs 180 lbs comparison; 35-48s rear view, cardio clip; 48-62s 'after using it in the sauna'; 62-76s mirror selfies, 'just stay CONSISTENT!'",
  cuts_per_10s=1.8, narration="creator talk", captions="partial (summary text overlays)", music="unclear",
  demonstration="Fastening the waist trainer; wearing during cardio/sauna", curiosity_gap="How/why/when it works", payoff_timing_s=29.0, product_intro_s=13.0, brand_intro_s=None,
  benefits="Waist compression, core structure, (claimed) appetite suppression", proof="before/after photos with weights (175/180 lbs); try-on on body",
  objection_handling="'works best when you're already on a fitness and nutrition journey'", offer="none", cta=None,
  observed="Reply-to-comment explainer, product appears at 13s, body photos with weights, health claims spoken.",
  interpretation="Educational reply format plus personal 'receipts' builds credibility; 93.5k likes (third-highest in the batch), rank 0.08. Contains weight-loss/appetite claims - policy risk; not a model for Ember & Clove copy.",
  missing_extra="Advertiser name blank in TSV; sheet covers to 39s (extra frames checked to 75s)",
  transcript_flags="'waste'=waist; 'match'=mass?; detector 0.92 cuts/10s corrected to ~1.8 (sheet shows ~14 shot changes)", confidence="high")

A("7441503397314805768",
  product="Forme Power Bra (posture-support bra)", product_brand="Forme", category="bra",
  language="English", audience_apparent="Broad: women with back pain, moms, office workers, students, athletes",
  format="voiceover b-roll", presenter="multiple",
  first_frame="Hands pulling a pink bra out of a white 'Forme' branded mailer bag; caption",
  first_spoken_line="Ever wonder who the form power bra is truly for?",
  opening_text_on_screen="Ever wonder who the Forme Power Bra is truly for? (then split-screen labels 'Regular Sports Bra' / 'Forme Power Bra' at ~3s)",
  initial_motion="handheld", hook_category="curiosity gap", hook_secondary="callout of audience",
  audience_callout={"present": True, "words": "women with back conditions... busy moms, office workers, students, athletes"},
  emotional_appeal="Inclusion / health", product_visible_by_s=1.5, implied_problem="Hunched posture, upper-back pain",
  sequence="0-3s unboxing hook; 3-6s split-screen posture comparison; 6-20s audience list over different women; 20-31s 'designed by orthopedic experts', tension fabrics; 31-41s long-term health, 'for all of us'; 42-43.8s laptop product page, 'Click the link'",
  cuts_per_10s=7.08, narration="voiceover", captions="yes", music="unclear",
  demonstration="Side-by-side posture comparison; women wearing it in daily activities", curiosity_gap="'who is it truly for?'", payoff_timing_s=3.0, product_intro_s=0.0, brand_intro_s=0.0,
  benefits="Aligns spine, pulls shoulders back, comfort, no stiffness", proof="comparison (split screen); authority claim ('designed by orthopedic experts', unverified)",
  objection_handling="'No stiffness, no discomfort'", offer="none visible", cta="'Click the link' text (~42.5s)",
  observed="Multi-creator montage, captions, unboxing open, brand logo in frame 1.",
  interpretation="Broad 'for everyone' message spreads the callout thin; polished but less personal than the creator version. Rank 0.22 is fourth-worst in the batch.",
  missing_extra="Product-page text on laptop too small to read",
  transcript_flags="'form'=Forme; 'MSD' as heard (also on screen)", confidence="high")

A("7444641956200693768",
  product="Avery Bootcut curvy-fit jeans in Luxe Stretch denim", product_brand="Silver Jeans", category="jeans",
  language="English", audience_apparent="Curvy women 25-45",
  format="brand/studio", presenter="creator face",
  first_frame="Smiling woman in black cardigan, dark bootcut jeans and black heels standing in a styled living room; text overlay",
  first_spoken_line="Meet our newest Avery boot cut, the perfect curvy fit in our Lux stretch fabric.",
  opening_text_on_screen="Meet AVERY BOOTCUT", initial_motion="static", hook_category="direct benefit", hook_secondary="product launch",
  audience_callout={"present": False, "words": None}, emotional_appeal="Confidence ('look good & feel good')",
  product_visible_by_s=0.0, implied_problem="Jeans that don't fit curves",
  sequence="0-2.7s full-body intro; 2.7-8.4s high rise, contoured waistband close-ups; 8.4-12.9s flat-lay 'Luxe Stretch denim'; 12.9-17.5s 'Incredible softness', 'Look good & Feel good'; 17.5-21.9s split hem close-up, boots",
  cuts_per_10s=3.66, narration="voiceover", captions="partial (feature labels)", music="unclear",
  demonstration="Fit and detail close-ups", curiosity_gap=None, payoff_timing_s=None, product_intro_s=0.0, brand_intro_s=0.0,
  benefits="Curvy fit, high rise, contoured waistband, soft stretch denim, split hem, goes with flats/heels/boots", proof="try-on on body",
  objection_handling=None, offer="none", cta=None,
  observed="Brand-voice product intro ('Meet...'), static opening, no CTA, video_view objective.",
  interpretation="Catalogue-style launch video; no hook tension, no proof beyond on-body shots, no CTA. Worst CTR rank in batch (0.33), though the video_view objective makes CTR less comparable.",
  missing_extra=None,
  transcript_flags="'Lux stretch'=Luxe Stretch", confidence="high")

# ---------- build ----------
order = ["id","brand","product_brand","product","category","language","duration_s","ctr_top_pct","likes","objective","budget_level",
         "audience_apparent","format","presenter","first_frame","first_spoken_line","opening_text_on_screen","initial_motion",
         "hook_category","hook_secondary","audience_callout","emotional_appeal","product_visible_by_s","implied_problem","sequence",
         "cuts_per_10s","cuts_per_10s_detector","narration","captions","music","demonstration","curiosity_gap","payoff_timing_s",
         "product_intro_s","brand_intro_s","benefits","proof","objection_handling","offer","cta","facts_vs_interpretation",
         "transcript_flags","missing_data","confidence","source"]
rows = []
for i in ids:
    a = ADS[i]; m = meta[i]
    j = json.load(open(os.path.join(BASE, "analysis", f"{i}.json"), encoding="utf-8"))
    md = STD_MISSING + ("; " + a["missing_extra"] if a.get("missing_extra") else "")
    r = dict(a)
    r.pop("missing_extra", None); obs = r.pop("observed"); interp = r.pop("interpretation")
    r.update({
        "id": i, "brand": (m["brand"].strip() or None),
        "duration_s": round(j["duration_s"], 1), "ctr_top_pct": float(m["ctr_top_pct"]), "likes": int(m["likes"]),
        "objective": m["objective"], "budget_level": int(m["budget_level"]),
        "cuts_per_10s_detector": j["cuts_per_10s"],
        "facts_vs_interpretation": {"observed": obs, "interpretation": interp},
        "missing_data": md,
        "source": "TikTok Creative Center Top Ads, US, Apparel & Accessories > Women's Clothing, last 180 days, observed 2026-10-25 (curated top-ads sample; survivorship)",
    })
    assert set(r) <= set(order), set(r) - set(order)
    rows.append({k: r.get(k) for k in order})

with open(os.path.join(BASE, "analysis", "breakdowns_00.jsonl"), "w", encoding="utf-8", newline="\n") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

# ---------- summary ----------
def cnt(key, fn=lambda v: v):
    return Counter(fn(r[key]) for r in rows)
def tbl(c):
    return "\n".join(f"| {k} | {v} |" for k, v in c.most_common())

pv = [r["product_visible_by_s"] for r in rows if r["product_visible_by_s"] is not None]
offer_present = sum(1 for r in rows if not str(r["offer"]).startswith("none"))
offer_caption_only = sum(1 for r in rows if str(r["offer"]).startswith("none") and ("title" in str(r["offer"]) or "caption" in str(r["offer"])))
cap_c = cnt("captions", lambda v: v.split(" ")[0])
music_c = cnt("music", lambda v: v.split(" ")[0])
nonen = [r for r in rows if not r["language"].startswith("English")]
srt = sorted(rows, key=lambda r: (r["ctr_top_pct"], -r["likes"]))
best, worst = srt[:8], srt[-8:][::-1]

def line(r):
    return (f"| {r['id']} | {r['ctr_top_pct']} | {r['likes']:,} | {r['brand'] or '-'} | {r['category']} | {r['format']} | {r['presenter']} | "
            f"{r['hook_category']} | {r['duration_s']} | {r['cuts_per_10s']} | {r['product_visible_by_s']} | {r['captions'].split(' ')[0]} | "
            f"{'yes' if not str(r['offer']).startswith('none') else 'no'} | {'yes' if r['cta'] else 'no'} | {r['objective']} |")
hdr = "| id | CTR rank | likes | advertiser | category | format | presenter | hook | dur s | cuts/10s | product vis s | captions | offer in video | CTA | objective |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"

def grp(g):
    return {
        "median dur": round(statistics.median(r["duration_s"] for r in g),1),
        "median cuts": round(statistics.median(r["cuts_per_10s"] for r in g),2),
        "creator-face": sum(r["presenter"] == "creator face" for r in g),
        "UGC formats": sum(r["format"] in ("creator UGC talking", "UGC try-on/haul", "product demo", "before-after") for r in g),
        "brand advertiser named": sum(bool(r["brand"]) for r in g),
        "product_sales obj": sum(r["objective"] == "product_sales" for r in g),
        "offer": sum(not str(r["offer"]).startswith("none") for r in g),
        "cta": sum(bool(r["cta"]) for r in g),
        "captions yes": sum(r["captions"].startswith("yes") for r in g),
        "speech": sum(r["first_spoken_line"] is not None for r in g),
        "prod vis 0s": sum(r["product_visible_by_s"] == 0.0 for r in g),
        "median likes": statistics.median(r["likes"] for r in g),
    }
gb, gw = grp(best), grp(worst)

md = f"""# Breakdowns batch 00 - summary

Source: TikTok Creative Center Top Ads, US, Apparel & Accessories > Women's Clothing, last 180 days, observed 2026-10-25. Curated "top ads" sample (survivorship: these are already winners; no losers to compare against). CTR = percentile rank only (0.01 = top 1%, lower is better); no conversion, spend or ROAS data.
Method: transcript (faster-whisper base.en) + automatic scene cuts + contact sheets viewed for every ad; extra frames pulled for ads longer than the sheet coverage. Audio was not listened to; "music" is inferred from continuous non-speech audio or lyric-like transcripts. Per-ad detail: `breakdowns_00.jsonl`.

Ads in batch: **{len(rows)}**. Non-English: **{len(nonen)}** ({", ".join(r['id'] + ' ' + r['language'].split(' ')[0] for r in nonen)}). Also 7380329994080534544 has English VO but a German ad caption (halara_europe).

## Counts

**Format**
| format | n |
|---|---|
{tbl(cnt('format'))}

**Hook category (primary)**
| hook | n |
|---|---|
{tbl(cnt('hook_category'))}

**Presenter**
| presenter | n |
|---|---|
{tbl(cnt('presenter'))}

**Burned-in captions**: {dict(cap_c)} (yes = word-level captions of speech; partial = feature labels / Q&A / summary text only).

**Offer present in the video itself**: {offer_present}/{len(rows)}; a further {offer_caption_only} have an offer only in the ad caption/title.

**Explicit CTA in video**: {sum(bool(r['cta']) for r in rows)}/{len(rows)}.

**Music** (inferred): {dict(music_c)}.

**Product visible by**: median **{statistics.median(pv)} s** (n={len(pv)}); {sum(v == 0.0 for v in pv)}/{len(pv)} show the product in the very first frame; latest = {max(pv)} s.

Median duration {round(statistics.median(r["duration_s"] for r in rows),1)} s; median cuts/10 s {round(statistics.median(r["cuts_per_10s"] for r in rows),2)}.

## Best 8 vs worst 8 by CTR rank (within this batch)

Tie note: four ads share rank 0.08 at the cut-off; the two with most likes (7441491158156541969, 7385349613774143489) were taken, 7397326487299719185 and 7437867036929851408 (also 0.08) were left out.

**Best 8**
{hdr}
{chr(10).join(line(r) for r in best)}

**Worst 8**
{hdr}
{chr(10).join(line(r) for r in worst)}

| metric | best 8 | worst 8 |
|---|---|---|
""" + "\n".join(f"| {k} | {gb[k]} | {gw[k]} |" for k in gb) + """

### What differs (observations only)

1. **Objective / who is advertising (biggest split).** All 8 best are `product_sales` (TikTok Shop) creator posts; 6 of them have no advertiser name in the TSV. None of the worst 8 is `product_sales`: 6 conversion, 1 traffic (app, 7382049390817558545), 1 video_view (Silver Jeans, 7444641956200693768), and 6 of 8 run from named brand/seller accounts (Silver Jeans, Forme x2, rihoas, halara_europe, stylised TikTok Shop). CTR ranks may not be directly comparable across objectives, so this split may partly reflect the objective, not the creative.
2. **Presenter and format.** Best 8 are all one real person on camera in creator talking, try-on, before-after or demo formats (no voiceover b-roll, no brand/studio). Worst 8 include brand/studio with a model (7444641956200693768, 7338465339167490050), voiceover b-roll with body-only or multiple models (7380329994080534544, 7441503397314805768) and a no-person app montage (7382049390817558545); only 3 are creator-style (7427043163971387399, 7199572939681972225, 7369124804521115666).
3. **Product in frame 1 does not separate them.** 7/8 best and 5/8 worst show the product at 0.0 s. The latest product appearance in the batch is in the best group (7441491158156541969, waist trainer at ~13 s, after a talking explainer hook); in the worst group 7427043163971387399 opens on celebrity footage (~5 s).
4. **Brand voice vs first person.** 4 of the worst 8 open in brand voice or generic copy ("Meet our newest...", "Ever wonder who...", "Goodbye skinny jeans", a static brand copy block); the other worst openers are first-person (7427043163971387399), a meme (7199572939681972225), an aesthetic theme (7369124804521115666) and app text (7382049390817558545). Best-8 openers are first-person or a visual: "You guys loved these leggings...", "Don't be fooled by other brands...", "THIS BODYSUIT ERASED MY WAIST", holding up the shapewear then putting it on (7272762760945041409), or a silent try-on.
5. **Proof type.** Best 8 lean on physical proof on a real body: squat/see-through test (7364141843464781840), scratch + scissors test (7441225809438670856), fitting into small jeans (7380169202270552065), leg-lift stretch (7438597543263731713), shapewear before/after (7272762760945041409), body photos with weights (7441491158156541969). Worst 8 rely more on claims and labels; the exception is 7427043163971387399 (posture comparison), which still ranks 0.27.
6. **Offer/CTA are not what separates them.** Each group has one ad with an offer inside the video (best: 7364141843464781840 price + free shipping; worst: 7382049390817558545 unspecified "perks"). The worst 8 contain more explicit CTAs (4 vs 2: end cards, "Click the link").
7. **Length is not the separator either.** Best 8 range 6.9-76 s (median 35 s); worst 8 range 8.2-57 s (median 20 s), so the better-ranked ads are, if anything, longer. Silent / no-speech ads appear in both groups (best: 7272762760945041409, 7348008745177251842, 7385349613774143489; worst: 7338465339167490050, 7382049390817558545, 7369124804521115666).
8. **Same-script pair.** Halara wide-leg jeans: "I bought 3 of these this month, let me tell you why" (7416283009659371536, 0.12, 20 s) vs "Goodbye skinny jeans" (7380329994080534544, 0.15, 33 s, EU account). Same feature VO otherwise. Confounded by length and market.
9. **Forme pair.** Creator sceptic-story version (7427043163971387399, 0.27) vs brand montage (7441503397314805768, 0.22): both are in the worst 8, so in this batch neither Forme approach reached the top half.

### Caveats
- n = 26, single snapshot, curated winners only; CTR rank is the only performance signal.
- Several transcripts have errors (flagged per ad in `transcript_flags`); three detector cut counts were corrected from the sheets (7380169202270552065, 7380329994080534544, 7441491158156541969; detector value kept in `cuts_per_10s_detector`).
- Policy notes: 7380169202270552065 (Ozempic comparison in caption), 7441491158156541969 (appetite-suppression/weight claims), 7427043163971387399 (celebrity footage) carry compliance/rights risk; don't copy those elements.
"""
open(os.path.join(BASE, "analysis", "breakdowns_00_summary.md"), "w", encoding="utf-8", newline="\n").write(md)
print(len(rows), "rows"); print(gb); print(gw)
print([ (r['id'], r['ctr_top_pct']) for r in best]); print([(r['id'], r['ctr_top_pct']) for r in worst])
