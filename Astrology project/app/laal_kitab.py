"""
laal_kitab.py -- Laal Kitab Prediction Engine
=============================================
Comprehensive Laal Kitab (Red Book) analysis system covering:
- Planet-in-House predictions (9 planets x 12 houses) with age triggers,
  conditions, financial, health, and family indicators
- Conjunction Effects for major planet pairs
- Planetary Debts (Rins) -- Pitru, Matru, Stri, Swa, Bhai
- Remedies (Upay) for afflicted planets
- Sleeping (Soya) / Blind (Andha) / Awake (Jaagta) planets
- LK Yogas: Dharmi, Kamini, Tabet, Panauti, Grahan, Mutual Exchange, Kayam
- Financial Analysis with sector-specific investment guidance
- Luck Activation by Ascendant sign
- Planet friendships & enmities (LK-specific)
- Teva (LK chart) analysis
"""
from __future__ import annotations

from typing import Dict, List, Optional


# =================================================================
# SIGN LIST & HOUSE MAPPING
# In Laal Kitab the Teva (chart) starts from the Ascendant sign.
# Ascendant sign = House 1, next sign = House 2, etc.
# =================================================================

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
SIGN_INDEX = {s: i for i, s in enumerate(SIGNS)}


def sign_to_house(sign: str, asc_sign: str) -> int:
    """
    Convert a zodiac sign to its Laal Kitab house number,
    counted from the ascendant sign.
    Ascendant sign = House 1, next sign = House 2, etc.
    """
    s_idx = SIGN_INDEX.get(sign, 0)
    a_idx = SIGN_INDEX.get(asc_sign, 0)
    return ((s_idx - a_idx) % 12) + 1


def house_to_sign(house: int, asc_sign: str) -> str:
    """Convert LK house number back to the zodiac sign for that house."""
    a_idx = SIGN_INDEX.get(asc_sign, 0)
    return SIGNS[(a_idx + house - 1) % 12]


# LK planet ownership (pakka ghar = permanent house)
PAKKA_GHAR = {
    "Sun": 1, "Moon": 4, "Mars": 3, "Mercury": 7,
    "Jupiter": 2, "Venus": 7, "Saturn": 8,
    "Rahu": 12, "Ketu": 6,
}

# LK exaltation houses
LK_EXALTED = {
    "Sun": 1, "Moon": 2, "Mars": 10, "Mercury": 4,
    "Jupiter": 4, "Venus": 12, "Saturn": 11,
    "Rahu": 3, "Ketu": 9,
}

# LK debilitation houses
LK_DEBILITATED = {
    "Sun": 7, "Moon": 8, "Mars": 4, "Mercury": 10,
    "Jupiter": 10, "Venus": 6, "Saturn": 5,
    "Rahu": 9, "Ketu": 3,
}

# Planet friendships in Laal Kitab
LK_FRIENDS = {
    "Sun":     ["Moon", "Mars", "Jupiter"],
    "Moon":    ["Sun", "Mercury"],
    "Mars":    ["Sun", "Moon", "Jupiter"],
    "Mercury": ["Sun", "Venus", "Rahu"],
    "Jupiter": ["Sun", "Moon", "Mars"],
    "Venus":   ["Mercury", "Saturn", "Ketu"],
    "Saturn":  ["Mercury", "Venus", "Rahu"],
    "Rahu":    ["Mercury", "Saturn", "Ketu"],
    "Ketu":    ["Venus", "Rahu"],
}

LK_ENEMIES = {
    "Sun":     ["Saturn", "Rahu", "Ketu"],
    "Moon":    ["Rahu", "Ketu"],
    "Mars":    ["Mercury", "Ketu"],
    "Mercury": ["Moon", "Ketu"],
    "Jupiter": ["Mercury", "Venus", "Rahu"],
    "Venus":   ["Sun", "Moon"],
    "Saturn":  ["Sun", "Moon", "Mars"],
    "Rahu":    ["Sun", "Moon", "Mars"],
    "Ketu":    ["Sun", "Moon"],
}


# =================================================================
# 1. PLANET-IN-HOUSE PREDICTIONS (108 combinations)
#    Enhanced with age_triggers, conditions, financial, health, family
# =================================================================

PLANET_IN_HOUSE: Dict[str, Dict[int, Dict]] = {
    # ----- SUN -----
    "Sun": {
        1: {
            "effect": "Excellent position. Person is authoritative, respected, government favor. Leadership qualities shine. Health is robust.",
            "good": "High self-confidence, administrative power, victory over enemies, good health, ancestral property benefits.",
            "bad": "Can be egoistic. If afflicted by Saturn/Rahu, headaches and bone issues.",
            "remedy": "Offer water to Sun at sunrise. Keep wheat or jaggery near bedside.",
            "age_triggers": ["Rise in authority after 22", "Government favor peaks 28-33", "Health caution at 45", "Full authority after 48"],
            "conditions": [
                "If Saturn is in H7, government penalties until 36",
                "If Moon conjoins, royal lifestyle confirmed",
                "If Rahu aspects from H7, sudden fall from power possible",
                "If Jupiter supports from H5 or H9, political career assured",
            ],
            "financial": "Wealth through government, authority, and gold. Property gains after 22. Income rises steadily. Avoid partnerships with Saturn-type people (oil, iron). Gold investments are highly favorable.",
            "health": "Head, eyes, bones, heart. Strong constitution. Headaches if Saturn aspects. Heart strong unless Mars is in H4. Bone issues after 45 if Rahu afflicts.",
            "family": "Father prospers and lives long. Mother is respectful. First son carries forward legacy. Wife respects husband. Father-son bond is strong.",
        },
        2: {
            "effect": "Family wealth comes through government or authority. Good speaker. May have strained relations with father if malefic influence.",
            "good": "Wealth through authority, good eyesight, family prosperity, respected speech.",
            "bad": "Arguments in family, eye problems if Moon is weak. Harsh speech.",
            "remedy": "Donate jaggery and wheat on Sundays. Do not accept free gifts.",
            "age_triggers": ["Family wealth accumulates after 24", "Eye issues possible at 30", "Property disputes at 36 if Saturn aspects", "Financial peak at 42"],
            "conditions": [
                "If Jupiter conjoins, massive family wealth and gold reserves",
                "If Saturn aspects, family disputes over inheritance",
                "If Rahu is in H8, hidden family debts surface",
                "If Moon is strong, sweet speech attracts wealth",
            ],
            "financial": "Family treasury grows through government connections. Gold and wheat trading profitable. Banking career favorable. Avoid lending money to friends. Ancestral property gives returns after 25.",
            "health": "Eyes, teeth, throat, right eye. Dental problems if Saturn is in H12. Throat issues if Mercury afflicts. Eye power decreases if Moon is debilitated.",
            "family": "Father brings wealth to family. Family name and honor important. Speech defines family standing. Wife manages finances well. Second child may face health issues.",
        },
        3: {
            "effect": "Brave and courageous. Good relations with siblings. Travel brings benefits. Active and energetic personality.",
            "good": "Courage, adventure, gains through travel, good siblings, name and fame.",
            "bad": "Can be overconfident. Strained relations with younger siblings if malefic.",
            "remedy": "Keep a solid gold piece. Offer water to Sun daily.",
            "age_triggers": ["Name and fame after 22", "Travel gains between 25-30", "Sibling property disputes at 35", "Peak courage at 40"],
            "conditions": [
                "If Mars conjoins, military or police career confirmed",
                "If Rahu is here, fame through unconventional means",
                "If Mercury aspects, writing or journalism brings fame",
                "If Saturn aspects from H9, brothers face hardship",
            ],
            "financial": "Income through courage, travel, and media. Publishing and writing can be profitable. Government travel allowances add income. Avoid getting into business with younger siblings.",
            "health": "Shoulders, arms, ears, nervous system. Ear problems if Saturn afflicts. Shoulder pain in later years. Energy levels remain high throughout life.",
            "family": "Siblings look up to the native. Younger brother benefits from native's authority. Father supports travels. Relations with neighbors are commanding.",
        },
        4: {
            "effect": "Owns property and vehicles. Mother's health may suffer. Inner restlessness despite outward prosperity.",
            "good": "Property gains, government favor, vehicles, authority at home.",
            "bad": "Mother's health issues, domestic unrest, heart problems possible.",
            "remedy": "Serve mother. Distribute sweets at religious places. Keep the house entrance neat.",
            "age_triggers": ["Vehicle at 24", "Property gains at 28", "Mother's health concern at 32", "Domestic peace after 40", "Heart caution after 48"],
            "conditions": [
                "If Moon conjoins, mother faces chronic health issues",
                "If Saturn aspects from H10, government property disputes",
                "If Jupiter supports, palatial house and multiple vehicles",
                "If Mars is in H4 too, domestic fire risk -- keep fire safety",
            ],
            "financial": "Real estate brings wealth. Government housing benefits. Vehicle trading profitable. Avoid water-related business. Land purchased in own name gives better results than joint property.",
            "health": "Heart, chest, lungs. Heart issues if Mars conjoins. Chest congestion in rainy season. Lungs affected if Rahu is in H4. Blood pressure after 45.",
            "family": "Mother may face health problems but remains devoted. Father may be authoritative at home. Domestic staff is loyal. Home has a regal atmosphere.",
        },
        5: {
            "effect": "Intelligent children, good education. Gains through speculation if Jupiter supports. Religious inclination.",
            "good": "Wise children, good education, speculation gains, spiritual growth, creative abilities.",
            "bad": "May face issues with first child. Too much ego in love matters.",
            "remedy": "Offer almonds in flowing water. Feed monkeys or give jaggery to cows.",
            "age_triggers": ["First child around 25-27", "Speculation gains at 33", "Children bring fame after 36", "Spiritual awakening at 45"],
            "conditions": [
                "If Jupiter conjoins, son becomes a high government official",
                "If Saturn aspects, first child delayed or faces obstacles",
                "If Rahu afflicts, adopted child or child through second marriage",
                "If Venus conjoins, love affair with person of authority",
            ],
            "financial": "Speculation gains through government stocks and gold ETFs. Children bring wealth. Education sector investments profitable. Avoid gambling. Stock market gains in government-sector companies.",
            "health": "Stomach, spine, heart. Stomach acidity. Spine issues if Saturn aspects. Heart remains strong. Children's health needs attention in their early years.",
            "family": "First son is authoritative and successful. Children are well-educated. Love affairs may create ego issues. Father guides children's education. Grandchildren bring joy.",
        },
        6: {
            "effect": "Victory over enemies, good health. Service sector brings benefits. May face legal issues but wins them.",
            "good": "Defeat enemies, good digestion, success in competition, service benefits.",
            "bad": "Maternal uncle may face problems. Conflicts with servants/subordinates.",
            "remedy": "Feed jaggery to monkeys. Keep almonds in pocket.",
            "age_triggers": ["Enemy defeat after 22", "Legal victory at 30", "Health peak at 33", "Service promotion at 36", "Maternal uncle issues at 40"],
            "conditions": [
                "If Mars conjoins, complete destruction of enemies",
                "If Saturn aspects, chronic legal disputes",
                "If Rahu conjoins, hidden enemies in government",
                "If Moon is weak, stomach and digestive issues",
            ],
            "financial": "Income through competitive exams, legal work, and health sector. Government service gives steady income. Debt recovery is swift. Avoid partnerships in food business. Legal practice is highly profitable.",
            "health": "Digestive system, intestines, immunity. Strong immunity unless Moon afflicts. Digestive fire is excellent. Kidney issues if Venus is debilitated. Regular health checkups after 40.",
            "family": "Maternal uncle faces hardships. Servants and employees are loyal but may create minor conflicts. Family health improves through native's efforts. Mother's brother needs support.",
        },
        7: {
            "effect": "Sun is debilitated here. Marriage may be delayed or troubled. Partnership issues. Government penalties possible.",
            "good": "Can gain through partnerships if Jupiter aspects. Foreign connections.",
            "bad": "Delayed marriage, spouse health issues, loss in partnerships, ego clashes.",
            "remedy": "Do not marry before 24. Offer wheat and jaggery at temple. Do not accept dowry.",
            "age_triggers": ["Marriage should not happen before 24", "Partnership losses at 28", "Government penalty risk at 32", "Spouse health concern at 36", "Stability after 42"],
            "conditions": [
                "If Jupiter aspects from H1, marriage saved and spouse brings fortune",
                "If Saturn conjoins, marriage extremely delayed till 32-35",
                "If Venus is strong, spouse is beautiful but ego clashes persist",
                "If Moon conjoins, wife from wealthy family but disputes continue",
            ],
            "financial": "Partnerships bring losses unless Jupiter aspects. Avoid business with government officials. Wife's family may demand money. Foreign trade has hidden penalties. Solo business is better than partnerships.",
            "health": "Lower back, kidneys, reproductive system. Kidney issues after 35. Lower back pain chronic. Spouse's health needs constant attention. Eye problems possible.",
            "family": "Wife may be dominant or face health issues. In-laws create problems. Marriage brings karmic lessons. Children born after marriage struggles bring stability. Second marriage possible if Venus is also weak.",
        },
        8: {
            "effect": "Health issues, especially related to bones and eyes. Inheritance disputes. Secretive nature develops.",
            "good": "Occult knowledge, insurance benefits, research abilities.",
            "bad": "Father's health suffers, eye problems, government penalties, sudden losses.",
            "remedy": "Throw copper coins in flowing water. Do not accept anything free of cost.",
            "age_triggers": ["Father's health concern at 22", "Sudden financial loss at 28", "Insurance matters at 33", "Eye issues at 40", "Inheritance dispute at 45"],
            "conditions": [
                "If Saturn conjoins, extremely long life but chronic bone diseases",
                "If Rahu conjoins, fear of government raids or penalties",
                "If Jupiter aspects, some inheritance comes through after legal battle",
                "If Mars conjoins, surgery related to head or eyes",
            ],
            "financial": "Sudden financial reversals. Insurance claims get delayed. Inheritance comes with legal fights. Government penalizes for tax issues. Hidden debts surface. Avoid property dealings between 28-35.",
            "health": "Eyes, bones, chronic ailments. Eye problems are almost certain. Bone degeneration after 40. Piles and fistula if Mars afflicts. Chronic headaches. Father's health deteriorates.",
            "family": "Father's health and fortune suffer. Family secrets related to property. In-laws may be hostile. Spouse's family has hidden debts. Children face obstacles in government matters.",
        },
        9: {
            "effect": "Religious and spiritual. Long-distance travel. Father may live separately. Good fortune after 25.",
            "good": "Spiritual growth, foreign travel, higher education, luck after struggles.",
            "bad": "Strained relations with father, religious extremism, arrogance in beliefs.",
            "remedy": "Offer water to Sun. Keep nose clean (do not smell flowers). Serve father.",
            "age_triggers": ["Foreign travel at 25", "Fortune rises after 27", "Father separates or ails at 33", "Spiritual peak at 45", "Pilgrimage at 50"],
            "conditions": [
                "If Jupiter conjoins, becomes a religious leader or judge",
                "If Saturn aspects, father's health suffers severely",
                "If Rahu conjoins, foreign settlement with government job abroad",
                "If Mars aspects, pilgrimage to hot/desert places",
            ],
            "financial": "Fortune through foreign lands, higher education, and religious institutions. Temple or trust management brings income. Export business favorable. Avoid domestic partnerships. Father's property comes late.",
            "health": "Thighs, hips, liver. Liver issues if Jupiter is weak. Hip joint problems after 45. Thigh injuries during travel. Blood pressure if Saturn afflicts.",
            "family": "Father may live separately or abroad. Guru replaces father figure. Wife is religious. Children pursue higher education abroad. Relations with father improve after 40.",
        },
        10: {
            "effect": "Excellent for career. Government job or high position. Authoritative and powerful. Respect in society.",
            "good": "Career success, government position, authority, social status, political power.",
            "bad": "Can become arrogant. Health issues after 48 if Saturn afflicts.",
            "remedy": "Offer water to Sun daily. Do not eat non-veg. Keep a copper vessel with water near bed.",
            "age_triggers": ["Career takes off at 22", "Government position by 28", "Political power at 33", "Peak authority at 40-45", "Health concerns after 48"],
            "conditions": [
                "If Saturn conjoins, delayed career but eventual ministerial position",
                "If Jupiter aspects from H2 or H6, judicial or educational authority",
                "If Mars conjoins, military or police top rank",
                "If Rahu conjoins, political career with scandals",
            ],
            "financial": "Highest income through government position. Career in administration brings wealth. Gold investments multiply. Property through government allotment. Pension and retirement benefits are strong.",
            "health": "Knees, bones, joints. Knee problems after 45. Bone density decreases if Saturn afflicts. Heart remains strong. Eye care needed after 50.",
            "family": "Father is proud of native. Family gains social status. Wife enjoys authority by association. Children follow father's career path. Family name rises in society.",
        },
        11: {
            "effect": "Gains from government and elder siblings. Wishes fulfilled. Social circle brings benefits.",
            "good": "Fulfillment of desires, gains through friends, elder sibling support, good income.",
            "bad": "May exploit friends. Son may face difficulties if Mars is weak.",
            "remedy": "Keep wheat and jaggery at home. Help orphans and poor.",
            "age_triggers": ["Income rises after 24", "Wishes fulfilled at 28", "Elder sibling helps at 33", "Social peak at 40", "Retirement benefits at 55"],
            "conditions": [
                "If Jupiter conjoins, massive wealth through ethical government connections",
                "If Saturn aspects, gains delayed but permanent",
                "If Rahu conjoins, sudden windfall from government lottery or scheme",
                "If Mars conjoins, income through defense or police",
            ],
            "financial": "Multiple income sources through government. Gains through elder siblings and influential friends. Network brings business opportunities. Gold and government bonds are best investments. Avoid speculative ventures.",
            "health": "Calves, ankles, circulatory system. Leg pain if Saturn afflicts. Circulation issues after 50. Overall health remains strong due to fulfilled desires reducing stress.",
            "family": "Elder siblings prosper and help native. Son may struggle initially but recovers. Friends become like family. Social gatherings bring joy. Adopted elder sibling relationship possible.",
        },
        12: {
            "effect": "Expenditure on good causes. Foreign settlement possible. Spiritual inclination. Sleep issues.",
            "good": "Spiritual growth, foreign gains, hospital/ashram work, peaceful old age.",
            "bad": "Loss of wealth, eye problems, poor sleep, father may suffer.",
            "remedy": "Throw jaggery in flowing water. Do not accept free items. Offer water to Sun.",
            "age_triggers": ["Foreign travel at 24", "Expenditure rises at 28", "Eye issues at 33", "Father's health concern at 38", "Spiritual awakening at 45", "Peaceful retirement after 55"],
            "conditions": [
                "If Saturn conjoins, long foreign stay but with hardship",
                "If Jupiter aspects, expenditure on charity brings hidden gains",
                "If Rahu conjoins, foreign government job or hospital work",
                "If Venus conjoins, luxury expenditure in foreign land",
            ],
            "financial": "Expenditure exceeds income in early life. Foreign currency dealings favorable. Hospital or ashram management brings hidden income. Avoid lending money. Investments in foreign markets may bring loss. Donate 1% of income to charity for wealth protection.",
            "health": "Feet, eyes, sleep disorders. Left eye problems. Insomnia or disturbed sleep. Foot injuries. Mental fatigue. Spiritual practices improve health.",
            "family": "Father may suffer or live far away. Family expenditure is high. Spouse adjusts to foreign life. Children may settle abroad. Family life improves with spiritual practices.",
        },
    },

    # ----- MOON -----
    "Moon": {
        1: {
            "effect": "Emotional and sensitive personality. Good intuition. Mother's influence is strong. Fluctuating health.",
            "good": "Good imagination, public popularity, mother's blessings, water-related gains.",
            "bad": "Over-emotional, changeable mind, respiratory issues if malefic.",
            "remedy": "Keep silver with you. Offer milk to Shivling. Respect mother.",
            "age_triggers": ["Public popularity at 24", "Mother's blessing peaks at 27", "Health fluctuation at 30-34", "Emotional stability after 40"],
            "conditions": [
                "If Sun conjoins, royal personality but inner turmoil",
                "If Rahu afflicts from H7, mental instability and deception",
                "If Jupiter aspects, blessed by mother and guru",
                "If Mars conjoins, emotional aggression and blood pressure",
            ],
            "financial": "Income through public dealings, water-related businesses, dairy, and hospitality. Silver investments are lucky. Avoid iron and oil business. Mother's blessings bring unexpected financial gains. Tourism sector is favorable.",
            "health": "Chest, lungs, mind, blood. Respiratory issues if afflicted. Blood impurities. Mental health needs attention. Cold and cough prone. Left eye issues possible.",
            "family": "Mother is the dominant influence. Father takes back seat. Wife is emotional and caring. First daughter brings luck. Family is emotionally close but fluctuating moods create drama.",
        },
        2: {
            "effect": "Moon is exalted here in LK. Wealthy family, sweet speech. Mother brings prosperity.",
            "good": "Family wealth, beautiful appearance, sweet speech, mother's prosperity, good eyes.",
            "bad": "Can be lazy. Over-indulgent in comforts.",
            "remedy": "Keep silver coin in wallet. Donate rice and milk on Mondays.",
            "age_triggers": ["Family wealth established by 24", "Best speech and influence at 27", "Prosperity peak at 30-36", "Comfort may lead to laziness at 40"],
            "conditions": [
                "If Jupiter conjoins, massive wealth -- banker or treasury role",
                "If Venus conjoins, family of artists and beauty",
                "If Rahu afflicts, sudden loss of family wealth",
                "If Sun conjoins, family connected to government wealth",
            ],
            "financial": "Excellent for family wealth accumulation. Banking, dairy, and pearl trading are highly profitable. Silver and rice trading brings gains. Family business flourishes. Savings come naturally. Real estate near water bodies is lucky.",
            "health": "Face, eyes, teeth, throat. Generally healthy appearance. Beautiful face. Eyes are attractive but sensitive. Throat issues if Saturn aspects. Sweet tooth leads to diabetes risk after 40.",
            "family": "Mother is wealthy and brings prosperity. Family is well-respected. Speech is the family's strength. Wife comes from good family. Children inherit wealth and good looks.",
        },
        3: {
            "effect": "Brave but unstable courage. Many short travels. Good relations with siblings mostly.",
            "good": "Adventurous spirit, gains through travel, writing ability, networking skills.",
            "bad": "Restless mind, inconsistent efforts, sibling disputes if Mars afflicts.",
            "remedy": "Donate white cloth. Keep rainwater in silver vessel at home.",
            "age_triggers": ["Travel begins at 22", "Writing gains at 25", "Sibling issues at 30", "Networking peak at 35", "Restlessness calms after 42"],
            "conditions": [
                "If Mars conjoins, blood-related sibling disputes",
                "If Mercury conjoins, excellent journalist or writer",
                "If Saturn aspects, travels bring hardship",
                "If Jupiter aspects, pilgrimage with siblings",
            ],
            "financial": "Income through short travels, writing, and communication. Courier or transport business favorable. Media earnings fluctuate. Tourism business near water bodies. Avoid committing large sums to any single venture.",
            "health": "Arms, shoulders, respiratory system. Asthma risk if afflicted. Shoulder tension. Nervous exhaustion from over-travel. Mental restlessness causes sleep issues.",
            "family": "Siblings have fluctuating relations. Younger sister benefits. Neighbors are helpful. Mother's siblings play a role. Family travels together frequently.",
        },
        4: {
            "effect": "Moon's permanent house. Very auspicious. Mother is long-lived. Domestic happiness. Property gains.",
            "good": "Domestic peace, mother's longevity, property gains, emotional stability, vehicles.",
            "bad": "Over-attachment to home and mother. Can neglect career for comfort.",
            "remedy": "Keep temple/prayer room clean. Offer milk at temple on Mondays.",
            "age_triggers": ["First property at 24", "Vehicle at 27", "Mother's health excellent till 40", "Domestic peak at 30-36", "Over-comfort risk after 42"],
            "conditions": [
                "If Jupiter conjoins, palatial home with temple",
                "If Saturn aspects from H10, property comes late but big",
                "If Mars conjoins, domestic discord despite property",
                "If Venus conjoins, luxurious home with garden",
            ],
            "financial": "Excellent for real estate, especially near water. Dairy farming, hotel business, and water purification industries are highly profitable. Property accumulates steadily. Mother's blessings protect wealth. Avoid selling ancestral property.",
            "health": "Heart, chest, breast, stomach. Strong heart. Chest congestion in cold weather. Stomach usually healthy. Emotional health is stable. Breast-related health for women needs monitoring.",
            "family": "Mother is long-lived and devoted. Home is peaceful and prosperous. Wife is homemaker by nature. Children are emotionally secure. Family gatherings are frequent and joyful.",
        },
        5: {
            "effect": "Intelligent and creative. Good children. Romantic nature. Gains through speculation possible.",
            "good": "Creative talent, good children, romance, speculation gains, artistic abilities.",
            "bad": "Too emotional in love. Children may cause worry if Saturn aspects.",
            "remedy": "Open a well or install water source. Donate milk products.",
            "age_triggers": ["Creative peak at 24-27", "First child at 27", "Romantic intensity at 30", "Speculation gains at 33-36", "Children stabilize after 40"],
            "conditions": [
                "If Venus conjoins, love marriage with beautiful person",
                "If Jupiter aspects, children are brilliant and spiritual",
                "If Rahu afflicts, heartbreak and children's health issues",
                "If Saturn aspects, children delayed and love becomes cold",
            ],
            "financial": "Speculation in dairy, water, and silver is profitable. Entertainment and creative industries bring income. Children's education sector. Film and music investments. Avoid dry-goods speculation.",
            "health": "Stomach, spine, emotional heart. Emotional eating leads to weight issues. Stomach acidity. Children's health needs attention. Romantic stress affects heart.",
            "family": "Children are emotionally close. Daughter is especially caring. Love life is intense but emotional. Mother guides in child-rearing. Family creativity is strong.",
        },
        6: {
            "effect": "Health issues related to chest and stomach. Enemies from maternal side. Service sector average.",
            "good": "Can overcome enemies through intelligence. Good for medical profession.",
            "bad": "Stomach issues, maternal uncle problems, servant troubles, anxiety.",
            "remedy": "Donate milk to temple. Keep silver items. Do not drink milk at night.",
            "age_triggers": ["Health issues surface at 24", "Enemy troubles at 27-30", "Stomach problems at 33", "Medical career peak at 36", "Health improves after 42 with remedies"],
            "conditions": [
                "If Mars conjoins, blood and stomach disorders",
                "If Saturn aspects, chronic digestive diseases",
                "If Mercury conjoins, skin allergies and nervous stomach",
                "If Jupiter aspects, enemies become friends through wisdom",
            ],
            "financial": "Medical profession is profitable. Avoid dairy business despite Moon's nature. Debt issues related to mother's side. Health insurance is essential. Service in nursing or caregiving brings steady income.",
            "health": "Stomach, intestines, chest, mental health. Chronic stomach disorders. Anxiety and depression risk. Water-borne diseases. Left lung issues. Mental health needs professional support.",
            "family": "Maternal uncle faces problems. Mother's health becomes a concern. Servants create emotional turmoil. Family health expenses rise. Children may inherit digestive weakness.",
        },
        7: {
            "effect": "Beautiful spouse. Marriage brings prosperity. Partnership gains. Good public relations.",
            "good": "Beautiful/handsome spouse, gains through marriage, public popularity, business success.",
            "bad": "Multiple attractions, spouse health issues if Rahu afflicts.",
            "remedy": "Keep silver items. Respect your spouse. Donate white items on Monday.",
            "age_triggers": ["Marriage around 24-27", "Spouse brings prosperity after marriage", "Public popularity at 30", "Partnership peak at 33-36", "Spouse health concern at 40"],
            "conditions": [
                "If Venus conjoins, extremely beautiful spouse and luxury through marriage",
                "If Saturn conjoins, marriage delayed but spouse is loyal and mature",
                "If Rahu afflicts, spouse deception or multiple marriages",
                "If Jupiter aspects from H1, spouse is religious and wealthy",
            ],
            "financial": "Partnership business, especially in hospitality, dairy, or tourism, is highly profitable. Wife's family supports financially. Public-facing business like restaurants. Import of water-related products. Silver jewelry business.",
            "health": "Kidneys, lower abdomen, reproductive organs. Kidney care essential. Reproductive health strong. Spouse's health needs monitoring. Water retention issues.",
            "family": "Wife is beautiful, caring, and brings prosperity. In-laws are supportive. Marriage is the turning point of life. Public respects the couple. Children resemble mother.",
        },
        8: {
            "effect": "Moon is debilitated in LK. Mother's health suffers. Emotional disturbances. Inheritance disputes.",
            "good": "Occult abilities, deep intuition, research skills.",
            "bad": "Mother's ill health, mental anxiety, sleep disorders, inheritance loss, depression.",
            "remedy": "Keep rainwater at home. Do not keep empty milk vessel at home. Serve mother.",
            "age_triggers": ["Mother's health concern at 24", "Mental anxiety peaks at 27-30", "Inheritance dispute at 33", "Depression risk at 36", "Occult interest develops at 40", "Stability after 48 with remedies"],
            "conditions": [
                "If Saturn conjoins, severe depression and mother's chronic illness",
                "If Rahu conjoins, Grahan Yoga -- mental breakdowns and deception",
                "If Jupiter aspects, some relief through spiritual practices",
                "If Sun conjoins, government inheritance dispute",
            ],
            "financial": "Financial losses through emotional decisions. Insurance claims delayed. Mother's medical expenses drain wealth. Inheritance comes with heavy legal costs. Avoid speculative investments entirely. Hidden debts surface unexpectedly.",
            "health": "Mental health, reproductive organs, chronic ailments. Depression is a serious risk. Sleep disorders and insomnia. Reproductive health weakened. Water-borne chronic diseases. Mother's health deteriorates significantly.",
            "family": "Mother suffers physically or emotionally. Family secrets cause pain. Emotional distance from family. In-laws create mental pressure. Children may inherit emotional instability.",
        },
        9: {
            "effect": "Spiritual and religious. Pilgrimage brings peace. Good luck through mother's blessings.",
            "good": "Spiritual growth, pilgrimage, guru's blessings, foreign travel, good fortune.",
            "bad": "Can become superstitious. Father-mother relations strained.",
            "remedy": "Install a water body at religious place. Keep silver square piece.",
            "age_triggers": ["Spiritual interest at 24", "Pilgrimage at 27", "Guru found at 30", "Fortune rises at 33-36", "Mother-father tensions at 40"],
            "conditions": [
                "If Jupiter conjoins, becomes spiritual teacher or healer",
                "If Sun conjoins, royal pilgrimage and religious authority",
                "If Rahu afflicts, false guru attachment",
                "If Saturn aspects, delayed pilgrimage and spiritual dryness",
            ],
            "financial": "Fortune through religious work, pilgrimage tourism, and dairy exports. Trust or temple management brings income. Water-related export business. Mother's blessings protect fortune. Avoid irreligious business.",
            "health": "Hips, thighs, liver. Generally healthy. Liver care needed if Jupiter is weak. Hip issues during pilgrimage. Water intake is crucial for health.",
            "family": "Mother is spiritual and religious. Father and mother may have different religious views. Wife supports spiritual pursuits. Children are religious. Family pilgrimages strengthen bonds.",
        },
        10: {
            "effect": "Public life is good. Career in nursing, hospitality, or public service. Fluctuating career progress.",
            "good": "Public popularity, career in service/hospitality, good reputation, medicines.",
            "bad": "Unstable career, too dependent on others' opinions, stress.",
            "remedy": "Keep water in silver vessel on terrace. Offer milk to Shiv temple.",
            "age_triggers": ["Career starts at 22 but fluctuates", "Public recognition at 27", "Career stability at 33", "Peak public role at 36-40", "Stress-related issues at 45"],
            "conditions": [
                "If Saturn conjoins, career in government hospital or welfare",
                "If Sun conjoins, government career with public fame",
                "If Rahu conjoins, career in foreign-facing public role",
                "If Mars aspects, nursing or emergency services career",
            ],
            "financial": "Income through hospitality, nursing, public service, and tourism. Hotel or restaurant business. Government welfare department. Water purification industry. Career earnings fluctuate with Moon phases. Silver investments stabilize income.",
            "health": "Knees, joints, skin. Stress affects skin. Joint issues from overwork. Career stress impacts sleep. Skin needs care especially in changing seasons.",
            "family": "Mother is proud of career. Public and family life balance is difficult. Wife supports career emotionally. Children see parent as public figure. Family reputation tied to career.",
        },
        11: {
            "effect": "Gains through mother and women. Wishes related to comfort fulfilled. Many friends.",
            "good": "Income through women, fulfilled desires, good friends, elder children prosper.",
            "bad": "Can be too dependent on friends. Waterborne diseases if weak.",
            "remedy": "Donate milk. Keep silver nails in the four corners of the house.",
            "age_triggers": ["Friends bring gains at 24", "Wishes start fulfilling at 27", "Mother helps financially at 30", "Elder child prospers at 33", "Friend circle peaks at 36-40"],
            "conditions": [
                "If Jupiter conjoins, wishes fulfilled through religious connections",
                "If Venus conjoins, gains through women and luxury business",
                "If Saturn aspects, gains delayed but permanent",
                "If Rahu conjoins, sudden windfall through female connection",
            ],
            "financial": "Gains through women-centric businesses, dairy, and hospitality. Networking brings business opportunities. Elder sister or daughter brings fortune. Silver and pearl investments. Women's products business is favorable.",
            "health": "Ankles, calves, lymphatic system. Water retention in legs. Lymphatic health needs attention. Emotional health tied to friend circle. Allergies possible.",
            "family": "Mother helps fulfill wishes. Elder daughter or sister is lucky. Friends become extended family. Social gatherings are frequent. Emotional bonds with friends are deep.",
        },
        12: {
            "effect": "Expenditure on mother's health. Sleep disturbances. Spiritual but confused. Foreign settlement.",
            "good": "Spiritual inclination, foreign settlement, hospital work, charitable nature.",
            "bad": "Insomnia, mother's health, unnecessary spending, mental confusion.",
            "remedy": "Keep a silver thali. Offer milk at Bhairav temple. Do not keep stagnant water.",
            "age_triggers": ["Sleep issues from 22", "Foreign travel at 25", "Mother's health expense at 30", "Spiritual confusion at 33", "Settlement abroad at 36", "Spiritual clarity after 45"],
            "conditions": [
                "If Saturn conjoins, chronic insomnia and foreign hardship",
                "If Rahu conjoins, severe Grahan yoga -- mental health crisis abroad",
                "If Jupiter aspects, spiritual hospital or ashram life",
                "If Venus conjoins, luxury abroad but emotional emptiness",
            ],
            "financial": "Expenditure exceeds income on health and foreign living. Hospital or ashram-related work brings hidden income. Avoid water business in foreign land. Charity protects wealth. Foreign currency speculations are risky.",
            "health": "Feet, left eye, sleep, mental health. Severe insomnia. Left eye problems. Foot injuries abroad. Mental health needs constant attention. Meditation helps more than medicine.",
            "family": "Mother's health is a constant expense. Family is far away causing emotional pain. Spouse adjusts to foreign life reluctantly. Children may be born abroad. Emotional distance from family.",
        },
    },

    # ----- MARS -----
    "Mars": {
        1: {
            "effect": "Brave, energetic, and aggressive. Leadership through action. Good health and vitality. Can be short-tempered.",
            "good": "Courage, physical strength, leadership, property gains, victory in competition.",
            "bad": "Aggressive nature, accidents, blood-related issues, marital discord (Manglik).",
            "remedy": "Keep deer skin at home. Feed sweet chapati to dogs. Serve brother.",
            "age_triggers": ["Physical peak at 22-28", "Property gains at 28", "Accident risk at 30-33", "Anger management needed at 36", "Leadership role after 40"],
            "conditions": [
                "If Sun conjoins, military commander or police chief",
                "If Saturn aspects from H7, accidents and marital discord",
                "If Jupiter supports, courage used for righteous causes",
                "If Rahu conjoins, sudden violent incidents possible",
            ],
            "financial": "Wealth through land, property, iron, steel, and construction. Self-made fortune through courage. Avoid partnerships. Real estate is the best investment. Military or police career gives good income. Red coral brings financial luck.",
            "health": "Head, blood, muscles, energy. Accidents and cuts. Blood pressure issues. Head injuries possible. Muscular health is excellent. Anger causes blood-related problems.",
            "family": "Dominates household. Younger brother prospers. Wife may find husband too aggressive. First child may face health issues. Property disputes with neighbors.",
        },
        2: {
            "effect": "Harsh speech but wealthy. Property through own efforts. Family disputes possible.",
            "good": "Self-made wealth, property gains, courageous speech, technical skills.",
            "bad": "Harsh words, family fights, dental/mouth problems, disputes over property.",
            "remedy": "Keep solid silver. Feed sweet bread to dogs. Do not take dowry.",
            "age_triggers": ["Property acquisition starts at 25", "Family dispute at 28", "Dental issues at 30", "Wealth accumulates at 33-36", "Speech softens after 42"],
            "conditions": [
                "If Jupiter conjoins, wealthy family with strong values",
                "If Saturn aspects, family poverty in early life then self-made wealth",
                "If Mercury conjoins, technical speech and engineering wealth",
                "If Moon conjoins, emotional family disputes",
            ],
            "financial": "Self-made wealth through property, construction, and engineering. Iron and steel trading. Land dealing is highly profitable. Avoid food-related business. Machinery and equipment trading. Wealth accumulates through harsh negotiations.",
            "health": "Mouth, teeth, jaw, blood. Dental problems frequent. Mouth ulcers. Jaw pain. Blood impurities. Facial injuries possible.",
            "family": "Harsh speech damages family bonds. Property disputes with family. Wife controls finances after arguments. Children inherit aggressive speech. Family wealth comes through struggle.",
        },
        3: {
            "effect": "Mars's permanent house. Very brave and adventurous. Excellent for military/police. Strong siblings.",
            "good": "Extreme courage, military success, adventure, strong siblings, writing ability.",
            "bad": "Over-aggressive, accidents during travel, blood pressure issues.",
            "remedy": "Keep a red handkerchief. Feed jaggery to monkeys.",
            "age_triggers": ["Extreme courage from 22", "Military/police entry at 24", "Adventure peak at 28", "Sibling bond strengthens at 30", "Blood pressure at 36", "Settled courage after 42"],
            "conditions": [
                "If Sun conjoins, national-level military honor",
                "If Mercury conjoins, technical writing or military engineering",
                "If Saturn aspects from H9, brother goes abroad with difficulty",
                "If Rahu conjoins, fame through unconventional bravery",
            ],
            "financial": "Income through defense services, sports, adventure tourism. Publishing and media in defense sector. Sibling partnerships work here. Transport and courier business. Arms and ammunition trading where legal.",
            "health": "Shoulders, arms, blood, nerves. Shoulder injuries in sports. Arms are strong. Blood donation is beneficial. Nerve damage from accidents possible.",
            "family": "Siblings are brave and supportive. Younger brother is like a warrior. Neighbors respect but fear. Family reputation built on courage. Wife of brother prospers.",
        },
        4: {
            "effect": "Mars is debilitated here. Property disputes. Mother's health may suffer. Domestic unrest.",
            "good": "Eventually gains land/property through struggle. Technical home setup.",
            "bad": "Property disputes, domestic discord, mother ill, blood pressure, anger at home.",
            "remedy": "Do not build house before 28. Feed sweet bread to dogs. Keep sindoor (vermilion) tilak.",
            "age_triggers": ["Domestic discord from 22-28", "Do NOT buy property before 28", "Mother's health concern at 30", "Property gains after 33", "Domestic peace after 40 with remedies"],
            "conditions": [
                "If Moon conjoins, mother's health severely affected",
                "If Saturn aspects from H10, property losses through government",
                "If Jupiter aspects, property through temple or religious institution",
                "If Sun conjoins, property through government allotment after delays",
            ],
            "financial": "Property brings problems before 28. Construction delays and cost overruns. Land disputes are common. After 33, property gains through persistent effort. Avoid building house on ancestral land until 28. Iron/steel fixtures in house cause problems.",
            "health": "Heart, chest, blood pressure. High blood pressure. Heart issues from anger. Chest pain episodes. Mother's health deteriorates. Domestic stress affects digestion.",
            "family": "Mother suffers health issues. Domestic life is turbulent. Wife and mother may clash. Property creates family rifts. Children feel tense at home. Peace comes only after remedies.",
        },
        5: {
            "effect": "Sharp mind but aggressive approach. Children may be troublesome. Good for sports and competition.",
            "good": "Competition success, sports ability, sharp intelligence, surgical skills.",
            "bad": "Children issues, miscarriage risk, aggressive in love, speculation losses.",
            "remedy": "Feed sweets to children. Donate red lentils. Keep saffron tilak.",
            "age_triggers": ["Sports peak at 22-28", "Competition wins at 25", "Child issues at 30", "Speculation loss at 33", "Surgical career peak at 36", "Children stabilize after 40"],
            "conditions": [
                "If Jupiter aspects, children succeed in competitive fields",
                "If Saturn aspects, severe delays in children and education",
                "If Venus conjoins, aggressive love affair leading to complications",
                "If Rahu afflicts, miscarriage or adoption",
            ],
            "financial": "Income through sports, competition, and surgery. Speculation is risky -- avoid. Children's education expenses are high. Coaching and training institutes profitable. Avoid gambling and race betting entirely.",
            "health": "Stomach, spine, reproductive. Stomach ulcers from competitive stress. Spine injuries in sports. Reproductive health needs attention. Miscarriage risk for women.",
            "family": "Children may be aggressive or troublesome. First child faces obstacles. Love affairs are intense and sometimes violent. Mother worries about children. Grandchildren through difficulty.",
        },
        6: {
            "effect": "Excellent for defeating enemies. Good health and immunity. Service in military/police/surgery benefits.",
            "good": "Enemy destruction, good health, legal victories, surgery success.",
            "bad": "Accidents, cuts/wounds, disputes with maternal relatives.",
            "remedy": "Keep red handkerchief. Donate blood or red lentils on Tuesday.",
            "age_triggers": ["Enemy defeat from 22", "Health peak at 25-30", "Legal victories at 28", "Maternal conflicts at 33", "Surgical career peak at 36", "Accident risk at 40"],
            "conditions": [
                "If Sun conjoins, complete enemy annihilation and government service",
                "If Saturn aspects, chronic health issues despite strong immunity",
                "If Jupiter aspects, healing profession brings fame",
                "If Rahu conjoins, mysterious enemies and hidden health issues",
            ],
            "financial": "Military, police, and surgical profession most profitable. Legal practice in criminal law. Debt recovery agencies. Fire safety equipment business. Avoid food and hospitality business.",
            "health": "Immune system, blood, injuries. Strong immunity but accident-prone. Cuts and wounds heal fast. Blood donation is recommended. Martial arts injuries. Iron in diet is essential.",
            "family": "Maternal uncle faces problems or conflicts arise. Servants fear and respect. Family health is strong due to native's influence. Brother helps in enemy matters.",
        },
        7: {
            "effect": "Manglik effects on marriage. Spouse may be aggressive. Partnership in business needs care.",
            "good": "Energetic spouse, property through marriage, business drive.",
            "bad": "Marital discord, spouse health/temper issues, partnership conflicts.",
            "remedy": "Marry after 28. Donate sweets on Tuesday. Keep silver in the house.",
            "age_triggers": ["Do NOT marry before 28", "Partnership disputes at 30", "Spouse temper issues at 33", "Property through spouse at 36", "Marital peace after 42"],
            "conditions": [
                "If Venus conjoins, extremely passionate but volatile marriage",
                "If Saturn conjoins, marriage severely delayed and cold relationship",
                "If Jupiter aspects from H1, marriage saved by wisdom",
                "If Moon conjoins, emotional volatility in marriage",
            ],
            "financial": "Partnership business brings conflict. Property through marriage after disputes. Spouse may earn through technical or defense work. Avoid 50-50 partnerships. Real estate partnership is especially dangerous.",
            "health": "Lower back, kidneys, reproductive system. Kidney stones possible. Lower back injuries. Reproductive health issues for both partners. Blood pressure affects marriage life.",
            "family": "Spouse is energetic but aggressive. In-laws have property disputes. Marriage is a karmic challenge. Children born after 30 are healthier. Partner's family involved in defense or technical fields.",
        },
        8: {
            "effect": "Mars is strong here (some LK texts say this is Mars's second Pakka Ghar). Inheritance gains but through conflict. Occult interests.",
            "good": "Inheritance, insurance gains, occult power, surgical ability.",
            "bad": "Accidents, operations, piles/fistula, sudden losses, blood disorders.",
            "remedy": "Keep deer skin at home. Float sindoor in river. Feed sweet bread to dogs.",
            "age_triggers": ["Surgery risk at 22-25", "Inheritance dispute at 28", "Occult interest at 30", "Insurance matters at 33", "Blood disorder at 36", "Transformation after 42"],
            "conditions": [
                "If Saturn conjoins, severe chronic diseases but very long life",
                "If Rahu conjoins, accidents and sudden violent events",
                "If Jupiter aspects, inheritance comes with spiritual transformation",
                "If Sun conjoins, government property inheritance dispute",
            ],
            "financial": "Insurance and inheritance are primary wealth sources but come with conflict. Surgery profession is very profitable. Occult services. Property through wills and disputes. Avoid real estate speculation.",
            "health": "Piles, fistula, reproductive, blood, accidents. Surgery is almost certain at some point. Piles and fistula common. Blood disorders. Accident-prone areas are legs and pelvis. Reproductive health concerns.",
            "family": "Family has property disputes. In-laws create problems. Spouse's family may have violent history. Children face health issues in childhood. Ancestral karma is strong.",
        },
        9: {
            "effect": "Religious through action. Brother in foreign land. Father may face health issues.",
            "good": "Religious actions, foreign travel, property abroad, pilgrimage.",
            "bad": "Father's health, religious fights, brother goes away, accidents during travel.",
            "remedy": "Serve brother. Keep honey at home. Do not cut trees.",
            "age_triggers": ["Foreign travel at 25", "Father's health concern at 28", "Brother settles abroad at 30", "Religious action at 33", "Property abroad at 36", "Travel accidents at 40"],
            "conditions": [
                "If Jupiter conjoins, religious warrior or legal authority",
                "If Saturn aspects, father's severe health issues",
                "If Sun conjoins, government posting abroad",
                "If Rahu conjoins, foreign settlement through aggressive means",
            ],
            "financial": "Foreign property and land. Export of iron, steel, and machinery. Defense exports. Legal practice abroad. Avoid religious business. Brother helps in foreign financial matters.",
            "health": "Hips, thighs, blood pressure. Hip injuries during travel. Thigh muscle issues. Blood pressure rises during religious debates. Liver function affected by anger.",
            "family": "Father's health suffers. Brother settles far away. Family has religious differences. Wife supports religious activities. Children may study abroad.",
        },
        10: {
            "effect": "Mars exalted in LK. Excellent career in uniformed services, engineering, surgery. Powerful authority.",
            "good": "Career peak, engineering/military success, property gains, authority, political power.",
            "bad": "Can be ruthless. Over-ambitious. Blood pressure in later years.",
            "remedy": "Keep red cloth in pocket. Feed jaggery to monkeys. Donate blood.",
            "age_triggers": ["Career launch at 22", "Engineering/military success at 25-28", "Authority peak at 33", "Property through career at 36", "Political power at 40", "Blood pressure caution at 45"],
            "conditions": [
                "If Sun conjoins, national-level defense position",
                "If Saturn conjoins, delayed career but reaches very top",
                "If Jupiter aspects, career in law enforcement with honor",
                "If Rahu conjoins, career through unconventional or controversial means",
            ],
            "financial": "Highest income through defense, engineering, surgery, and real estate. Government contracts for construction are very profitable. Career brings property. Iron and steel industry leadership. Political career brings financial power.",
            "health": "Knees, bones, blood pressure. Knee injuries from fieldwork. Blood pressure management crucial. Bones are strong. Overwork leads to burnout. Surgery-related occupational hazards.",
            "family": "Father is proud. Family gains property through career. Wife manages home while native is away on duty. Children follow defense or engineering career. Social status is high.",
        },
        11: {
            "effect": "Gains through property and brothers. Wishes fulfilled through courage. Friends in uniform.",
            "good": "Property income, brother's help, wish fulfillment, gains through courage.",
            "bad": "Friend disputes, elder sibling conflicts, blood-related health issues.",
            "remedy": "Keep red handkerchief. Feed sweet bread to dogs.",
            "age_triggers": ["Income through courage at 24", "Brother helps at 28", "Property gains at 30", "Wish fulfillment at 33-36", "Friend disputes at 40"],
            "conditions": [
                "If Jupiter conjoins, massive gains through ethical means",
                "If Saturn aspects, gains delayed but property income is permanent",
                "If Sun conjoins, gains through government and defense",
                "If Rahu conjoins, sudden property windfall",
            ],
            "financial": "Real estate income, rental properties, and construction business are highly profitable. Defense-related gains. Friends in uniform bring opportunities. Elder brother's help in financial matters. Avoid speculation.",
            "health": "Calves, ankles, blood circulation. Leg injuries possible. Blood circulation issues. Ankle sprains during physical activities. Overall health is strong.",
            "family": "Elder brother is supportive and brave. Friends are in defense or police. Wishes related to property are fulfilled. Children benefit from parent's courage.",
        },
        12: {
            "effect": "Expenditure through property disputes. Sleep disturbance. Foreign lands may bring loss.",
            "good": "Foreign settlement (with effort), hospital/military work abroad.",
            "bad": "Property losses, sleep issues, accidents abroad, brother suffers.",
            "remedy": "Keep honey and saffron. Feed sweet bread to dogs. Do not sell ancestral property.",
            "age_triggers": ["Foreign travel with difficulty at 25", "Property loss at 28", "Brother's suffering at 30", "Sleep issues at 33", "Hospital work at 36", "Settlement abroad after 40"],
            "conditions": [
                "If Saturn conjoins, imprisonment or hospital stay abroad",
                "If Rahu conjoins, accidents in foreign land",
                "If Jupiter aspects, military posting abroad with honor",
                "If Venus conjoins, expenditure on luxury abroad",
            ],
            "financial": "Expenditure exceeds income through property disputes and foreign living. Military or hospital work abroad. Avoid buying property abroad before 36. Ancestral property must not be sold. Hidden enemies cause financial loss.",
            "health": "Feet, injuries, sleep, accidents. Foot injuries abroad. Sleep disturbances. Accident risk in foreign land. Blood donation abroad is beneficial. Surgery possible away from home.",
            "family": "Brother suffers or lives far away. Family is far and native feels isolated. Spouse adjusts with difficulty. Children may be born abroad. Property in homeland creates disputes from distance.",
        },
    },

    # ----- MERCURY -----
    "Mercury": {
        1: {
            "effect": "Intelligent and youthful appearance. Good communication. Childlike nature. Trade and business acumen.",
            "good": "Intelligence, business skills, youthful looks, witty speech, writing ability.",
            "bad": "Childish behavior, skin issues, nervous disorders if afflicted.",
            "remedy": "Keep a green parrot or feed parrots. Wear emerald (if suitable). Keep nose clean.",
            "age_triggers": ["Intelligence peaks at 22-25", "Business skills at 28", "Youthful energy till 34", "Skin issues at 30", "Writing fame at 36", "Nervous issues after 42 if no remedy"],
            "conditions": [
                "If Jupiter aspects, becomes a scholar or professor",
                "If Venus conjoins, business in beauty, arts, or fashion",
                "If Rahu conjoins, technology business and foreign trade",
                "If Moon afflicts, nervous breakdowns and skin disorders",
            ],
            "financial": "Trade and commerce are primary wealth sources. IT and technology business. Publishing and writing income. Communication business -- telecom, media. Green vegetable and herbal trade. Avoid heavy industry.",
            "health": "Nervous system, skin, respiratory, speech. Skin allergies and eczema. Nervous disorders if overworked. Speech issues under stress. Respiratory sensitivity. Keep nose clean as LK remedy.",
            "family": "Youthful aura in family. Daughter is intelligent. Wife appreciates humor. Children are quick learners. Family communication is good. Maternal aunt plays important role.",
        },
        2: {
            "effect": "Sweet speech and wealthy through business. Good education. Multiple income sources.",
            "good": "Business wealth, educated family, multiple incomes, good teeth/mouth.",
            "bad": "Can be greedy. Skin problems if Rahu conjuncts.",
            "remedy": "Get nose pierced (women). Donate green moong dal. Keep teeth clean.",
            "age_triggers": ["Education completes by 24", "Business starts at 25", "Multiple incomes at 28", "Family wealth at 33", "Greed risk at 36", "Established wealth by 42"],
            "conditions": [
                "If Jupiter conjoins, banking or treasury role with massive wealth",
                "If Venus conjoins, jewelry or fashion business wealth",
                "If Saturn aspects, delayed but methodical wealth building",
                "If Rahu conjoins, foreign trade and technology wealth",
            ],
            "financial": "Multiple income streams through trade, banking, and communication. Jewelry and gem trading. Educational institutions. Publishing houses. Green goods -- vegetables, herbs, organic products. Financial advisory services.",
            "health": "Mouth, teeth, throat, skin. Dental hygiene is crucial. Throat infections. Skin issues near mouth. Good appetite but dietary discretion needed.",
            "family": "Educated and well-spoken family. Wife manages money well. Children are articulate. Family business traditions. Wealth passes through generations through business acumen.",
        },
        3: {
            "effect": "Excellent communication and writing. Many short trips. Good relations with siblings.",
            "good": "Writing talent, journalism, travel gains, sibling harmony, networking.",
            "bad": "Scattered thinking, too many small ventures, neck/shoulder issues.",
            "remedy": "Keep green cloth. Donate to orphanage. Wear copper ring.",
            "age_triggers": ["Writing career at 22", "Travel peaks at 25-30", "Sibling partnership at 28", "Publication at 33", "Scattered energy risk at 36", "Focus returns after 42"],
            "conditions": [
                "If Mars conjoins, technical writing or sports journalism",
                "If Moon conjoins, emotional writing and poetry",
                "If Saturn aspects, delayed publications but serious literature",
                "If Rahu conjoins, internet and digital media career",
            ],
            "financial": "Journalism, writing, and publishing are primary incomes. Short-distance trade and courier business. Sibling partnerships in communication. Digital media business. Tutoring and coaching centers.",
            "health": "Hands, arms, nervous system, lungs. Carpal tunnel from writing. Shoulder tension. Lung sensitivity. Nervous exhaustion from multitasking.",
            "family": "Siblings are communicative and supportive. Younger sister benefits. Neighborhood relations are excellent. Family known for intelligence. Mother's siblings are helpful.",
        },
        4: {
            "effect": "Mercury exalted here in LK. Educated family, good property. Mother is intelligent.",
            "good": "Property through intelligence, educated household, vehicles, domestic peace.",
            "bad": "Over-thinking, anxiety about home matters.",
            "remedy": "Bury a copper coin in the foundation of house. Keep green plants at home.",
            "age_triggers": ["Education peak at 22-25", "Property through intelligence at 28", "Vehicle at 30", "Domestic peace at 33", "Anxiety risk at 36-40", "Intellectual legacy after 45"],
            "conditions": [
                "If Moon conjoins, intelligent mother and emotional intelligence",
                "If Jupiter conjoins, library at home and scholarly family",
                "If Venus conjoins, beautifully designed intelligent home",
                "If Saturn aspects from H10, property through government education job",
            ],
            "financial": "Real estate through intelligent deals. Educational institution at home. Vehicle trading. IT business from home. Green technology investments. Property near educational institutions appreciates well.",
            "health": "Chest, lungs, nervous system. Overthinking causes anxiety. Chest congestion from AC. Nervous stomach from home worries. Plants at home improve health.",
            "family": "Mother is intelligent and educated. Home is a place of learning. Children grow up in intellectual environment. Wife appreciates intellectual partner. Family discussions are stimulating.",
        },
        5: {
            "effect": "Very intelligent children. Good in studies and speculation. Creative business mind.",
            "good": "Brilliant children, education success, speculation gains, creative business.",
            "bad": "Over-analysis, nervous stomach, daughter may face issues if Saturn afflicts.",
            "remedy": "Donate green items to students. Feed green grass to cows.",
            "age_triggers": ["Education excellence at 22-25", "Creative business at 28", "Children brilliance at 30-33", "Speculation gains at 33", "Daughter concern at 36 if Saturn present"],
            "conditions": [
                "If Jupiter aspects, children become scholars or doctors",
                "If Venus conjoins, creative arts business and love for intelligent person",
                "If Rahu conjoins, children in technology and foreign education",
                "If Saturn aspects, delays in children but eventually brilliant",
            ],
            "financial": "Education sector investments are best. Children's education businesses. Stock market through analytical approach. Creative writing and publishing. IT and technology speculation. Avoid emotional investments.",
            "health": "Stomach, spine, nervous. Nervous stomach from overthinking. Spine issues from prolonged sitting. Digestive sensitivity. Children's health needs attention.",
            "family": "Children are exceptionally intelligent. Daughter is creative and business-minded. Love life is intellectual. Mother guides children's education. Grandchildren inherit intelligence.",
        },
        6: {
            "effect": "Wins through intelligence. Good for legal profession. Health awareness is high.",
            "good": "Legal victories, medical/legal profession, enemy defeat through wit.",
            "bad": "Nervous disorders, skin issues, disputes with maternal relatives.",
            "remedy": "Keep a green parrot or picture. Donate green dal. Wear copper.",
            "age_triggers": ["Legal mind develops at 22", "Enemy defeat at 25-28", "Skin issues at 30", "Medical/legal peak at 33-36", "Nervous health at 40"],
            "conditions": [
                "If Jupiter aspects, healing through intelligence -- doctor or healer",
                "If Mars conjoins, forensic science or criminal investigation",
                "If Saturn aspects, chronic skin diseases but legal career",
                "If Moon afflicts, nervous breakdown and maternal disputes",
            ],
            "financial": "Legal profession is highly profitable. Medical data analysis. Health-tech business. Accounting and auditing in health sector. Avoid food business. Debt recovery through legal means.",
            "health": "Intestines, nervous system, skin. Irritable bowel syndrome. Skin allergies and eczema. Nervous disorders from legal stress. Keep immune system strong through diet.",
            "family": "Maternal uncle has disputes. Family health consciousness is high. Wife supports through legal battles. Children inherit analytical mind. Servants need intelligent management.",
        },
        7: {
            "effect": "Mercury's permanent house. Excellent for business partnerships. Intelligent spouse.",
            "good": "Business success, smart spouse, trade partnerships, foreign trade.",
            "bad": "Too calculating in relationships, multiple attractions, skin issues.",
            "remedy": "Keep green things. Donate to girls' education. Wear emerald (if suitable).",
            "age_triggers": ["Partnership success at 24", "Intelligent spouse found at 25-28", "Foreign trade at 30", "Business peak at 33-36", "Relationship calculation at 40"],
            "conditions": [
                "If Venus conjoins, spouse in beauty or fashion business",
                "If Jupiter aspects from H1, spouse is highly educated and ethical",
                "If Rahu conjoins, foreign spouse in technology",
                "If Saturn conjoins, business partner is older and experienced",
            ],
            "financial": "Partnership business is the primary wealth source. Import-export trading. IT consulting. Matchmaking or matrimonial business. Jewelry design. Accounting firm partnerships. Foreign trade is exceptionally profitable.",
            "health": "Kidneys, lower back, skin. Kidney function needs monitoring. Skin issues from partnerships stress. Lower back from sitting in business. Reproductive health awareness needed.",
            "family": "Spouse is intelligent, articulate, and business-minded. Marriage is a business partnership in many ways. In-laws are educated. Children are socially intelligent. Business and family intertwine.",
        },
        8: {
            "effect": "Hidden intelligence. Research ability. Nervous health issues. Sudden changes in fortune.",
            "good": "Research skills, detective ability, occult intelligence, insurance gains.",
            "bad": "Nervous breakdown, skin diseases, sudden financial reversals.",
            "remedy": "Wear copper ring. Donate green items. Keep teeth clean.",
            "age_triggers": ["Research interest at 22", "Hidden gains at 25", "Nervous breakdown risk at 28-30", "Insurance matters at 33", "Skin disease at 36", "Occult intelligence after 40"],
            "conditions": [
                "If Saturn conjoins, deep research but chronic nervous issues",
                "If Rahu conjoins, technology in occult or hidden sciences",
                "If Jupiter aspects, transformation through knowledge",
                "If Mars conjoins, forensic investigation career",
            ],
            "financial": "Insurance and investigation work. Research grants. Tax consulting. Hidden income through intelligence. Avoid surface-level business. Data science and analysis. Cryptocurrency research (cautious approach).",
            "health": "Nervous system, skin, reproductive. Severe nervous disorders. Chronic skin diseases. Reproductive complications. Mental health needs professional care. Sudden health reversals.",
            "family": "Family secrets involve intelligence or deception. Spouse's family has hidden matters. Children have deep analytical minds. In-laws may be deceptive. Inheritance through legal battles.",
        },
        9: {
            "effect": "Higher education and philosophy. Foreign education possible. Good luck through intelligence.",
            "good": "Higher education, foreign study, guru's blessings through intellect, publishing.",
            "bad": "Over-intellectual in spiritual matters, nervous father.",
            "remedy": "Donate to educational institutions. Keep copper coins. Feed green dal to birds.",
            "age_triggers": ["Higher education at 22-25", "Foreign study at 25", "Publishing at 28-30", "Guru connection at 33", "Intellectual peak at 36-40", "Father's nervousness at 42"],
            "conditions": [
                "If Jupiter conjoins, professor or educational leader",
                "If Sun conjoins, government scholarship and foreign deputation",
                "If Rahu conjoins, technology education abroad",
                "If Saturn aspects, delayed higher education but deep wisdom",
            ],
            "financial": "Income through education, publishing, and foreign academic positions. University investments. Book publishing. Online education platforms. Green technology exports. Travel writing income.",
            "health": "Hips, liver, nervous system. Hip issues from prolonged study. Liver care if Jupiter is weak. Nervous exhaustion from academics. Travel fatigue.",
            "family": "Father is intellectual but nervous. Family values education highly. Wife supports academic career. Children pursue higher education. Family reputation in academic circles.",
        },
        10: {
            "effect": "Mercury debilitated here in LK. Career fluctuations. Business needs more effort.",
            "good": "Can succeed through persistent effort. Multiple career changes lead to right path.",
            "bad": "Career instability, business losses, skin issues, nerve problems.",
            "remedy": "Wear copper. Do not keep birds caged. Donate to orphans. Get nose pierced (women).",
            "age_triggers": ["Career confusion at 22-25", "Multiple changes at 28", "Business loss at 30", "Career stability at 33-36", "Skin issues at 38", "Right path found after 40"],
            "conditions": [
                "If Saturn conjoins, career in government clerical or accounting role",
                "If Jupiter aspects, teaching career despite obstacles",
                "If Venus conjoins, career in design or fashion with fluctuations",
                "If Mars conjoins, engineering career with instability",
            ],
            "financial": "Career income fluctuates significantly. Business ventures fail before finding the right one. Accounting or clerical work is steady. Avoid entrepreneurship before 33. Multiple small incomes better than one big venture.",
            "health": "Knees, skin, nervous system. Knee pain from career stress. Chronic skin conditions. Nervous disorders from career uncertainty. Dental problems. Regular health routines essential.",
            "family": "Family worried about career. Wife supports through career changes. Children may inherit career indecision. Father's career was also unstable. Family reputation fluctuates.",
        },
        11: {
            "effect": "Gains through business and intelligence. Friends in trade. Wishes fulfilled through wit.",
            "good": "Business income, intelligent friends, wish fulfillment, elder daughter prospers.",
            "bad": "Can be too shrewd with friends. Nervous health if overworked.",
            "remedy": "Donate green items. Keep emerald or green stone.",
            "age_triggers": ["Business gains at 24", "Intelligent network at 28", "Wishes fulfilled at 30-33", "Elder daughter success at 36", "Nervous overwork at 40"],
            "conditions": [
                "If Jupiter conjoins, wealth through ethical business and education",
                "If Venus conjoins, gains through beauty and fashion network",
                "If Rahu conjoins, technology network and sudden business gains",
                "If Saturn aspects, delayed gains but permanent business network",
            ],
            "financial": "Multiple business income streams. Trading network is the greatest asset. Technology investments. Education sector gains. Friends bring business opportunities. Green and organic products trading.",
            "health": "Calves, ankles, nervous system. Leg cramps from overwork. Nervous exhaustion. Anxiety from business pressure. Friends help in health matters.",
            "family": "Elder daughter is intelligent and prosperous. Friends become family. Business network extends family influence. Wife participates in social network. Children benefit from parent's connections.",
        },
        12: {
            "effect": "Expenditure on education and health. Foreign settlement through education. Sleep talking possible.",
            "good": "Foreign education, research abroad, spiritual intelligence.",
            "bad": "Money loss through bad decisions, sleep issues, nervous breakdown, skin diseases.",
            "remedy": "Keep a green parrot. Donate to orphanage. Wear copper ring in little finger.",
            "age_triggers": ["Foreign education at 22-25", "Money loss at 28", "Sleep issues at 30", "Research abroad at 33", "Nervous breakdown risk at 36", "Spiritual intelligence after 42"],
            "conditions": [
                "If Rahu conjoins, foreign technology career with mental stress",
                "If Jupiter aspects, research in spiritual or philosophical field",
                "If Saturn conjoins, chronic skin diseases and foreign hardship",
                "If Venus conjoins, foreign fashion or beauty career with expenditure",
            ],
            "financial": "Foreign education expenses are high. Research grants abroad. Publishing income from foreign publishers. Avoid business in foreign land. Mental health treatment expenses. Online income from abroad possible.",
            "health": "Feet, nervous system, skin, sleep. Insomnia and sleep talking. Foot problems. Chronic skin diseases abroad. Nervous breakdown from isolation. Mental health requires active management.",
            "family": "Family is far away. Education takes native abroad. Spouse adjusts to foreign life. Children born abroad may have identity issues. Family communication through technology.",
        },
    },

    # ----- JUPITER -----
    "Jupiter": {
        1: {
            "effect": "Most auspicious placement. Wise, generous, and respected. Teacher/guide to others. Long life.",
            "good": "Wisdom, longevity, respect, teacher role, health, prosperity, spiritual growth.",
            "bad": "Over-generous, taken advantage of. Weight gain.",
            "remedy": "Apply saffron tilak. Keep gold. Serve saints and teachers.",
            "age_triggers": ["Wisdom shines from 16", "Teacher role at 22", "Respect and honor at 28", "Prosperity peak at 33-36", "Weight gain caution at 40", "Spiritual mastery after 48"],
            "conditions": [
                "If Sun conjoins, government advisor or minister",
                "If Moon conjoins, compassionate healer and wise counselor",
                "If Rahu afflicts from H7, false accusations from rivals",
                "If Saturn aspects, delayed recognition but eventually grand",
            ],
            "financial": "Wealth through teaching, banking, gold, and religious institutions. Gold investments are best. Banking career. Educational trust management. Avoid iron and alcohol business. Saffron and turmeric trade. Temple donations return manifold.",
            "health": "Liver, fat, obesity. Weight management essential. Liver function strong. Diabetes risk after 40. Overall robust health. Long life is almost certain.",
            "family": "Father prospers. Children are well-educated. Wife respects husband deeply. Family is religious and harmonious. Grandchildren bring joy. Family name is honored in society.",
        },
        2: {
            "effect": "Jupiter's permanent house in LK. Extremely wealthy and family-oriented. Voice of wisdom.",
            "good": "Great wealth, wise speech, family prosperity, gold accumulation, teaching.",
            "bad": "Can be preachy. Weight issues. Over-spending on family.",
            "remedy": "Apply saffron tilak on forehead. Keep gold piece. Donate saffron to temple.",
            "age_triggers": ["Family wealth grows from 22", "Gold accumulation at 25", "Wise speech recognized at 28", "Wealth peak at 33-42", "Weight concern at 36", "Family legacy at 48"],
            "conditions": [
                "If Sun conjoins, family connected to government and royalty",
                "If Venus conjoins, massive luxury and jewelry collection",
                "If Saturn aspects, family wealth built slowly through discipline",
                "If Rahu afflicts, sudden loss of family wealth through fraud",
            ],
            "financial": "Greatest wealth accumulation position. Gold, banking, treasury. Family business thrives across generations. Saffron and religious items trade. Educational institution ownership. Avoid non-vegetarian food business. Financial advisory is excellent.",
            "health": "Face, throat, eyes, liver. Throat issues from too much speaking. Weight gain from good food. Liver needs turmeric support. Eyes remain strong. Diabetes monitoring after 40.",
            "family": "Family is the center of life. Wife manages vast household. Children inherit wealth and wisdom. Family voice in community matters. Ancestral property well-maintained. Generous to family members.",
        },
        3: {
            "effect": "Wise and philosophical siblings. Gains through religious travel. Courageous through knowledge.",
            "good": "Wise siblings, religious travel, philosophical writing, guru-like courage.",
            "bad": "Lazy in action, too much theory, brothers may be far.",
            "remedy": "Apply saffron tilak. Serve guru. Donate yellow items.",
            "age_triggers": ["Philosophical interest at 22", "Religious travel at 25", "Writing career at 28", "Guru-like courage at 33", "Brothers separate at 36", "Philosophical maturity at 45"],
            "conditions": [
                "If Mars conjoins, courageous religious teacher",
                "If Mercury conjoins, scholarly writer and publisher",
                "If Saturn aspects, siblings face hardship despite wisdom",
                "If Moon conjoins, emotional religious writing",
            ],
            "financial": "Income through religious travel, publishing, and teaching. Philosophical writing brings royalties. Pilgrimage tour business. Sibling partnerships in education. Yellow items trading.",
            "health": "Shoulders, lungs, nerves. Shoulder tension from desk work. Lung health strong. Nervous system protected by wisdom. Arms may develop issues from writing.",
            "family": "Siblings are philosophical and wise. Younger brother may become a teacher. Neighbors seek advice. Family known for scholarly tradition. Wife supports religious travels.",
        },
        4: {
            "effect": "Jupiter exalted here in LK. Maximum domestic happiness. Mother is religious. Great property.",
            "good": "Property wealth, mother's blessings, domestic harmony, vehicles, temples at home.",
            "bad": "Too comfortable, spiritual pride, weight gain.",
            "remedy": "Apply saffron tilak. Worship at home temple. Keep gold at home.",
            "age_triggers": ["Property acquisition at 24", "Home temple at 27", "Mother's blessings peak at 30", "Domestic harmony at 33-36", "Comfort zone trap at 40", "Spiritual home after 48"],
            "conditions": [
                "If Moon conjoins, mother is saintly and home is an ashram",
                "If Venus conjoins, palatial home with gardens and luxury",
                "If Sun conjoins, government allotment of large property",
                "If Rahu afflicts, property dispute through fraud",
            ],
            "financial": "Real estate wealth at its maximum. Temple or ashram land. Agricultural land. Gold stored at home. Property near religious institutions. Educational institution on own property. Avoid selling any property -- it brings bad luck.",
            "health": "Heart, chest, liver, weight. Heart is strong and generous. Weight gain from comfort. Liver needs care with rich diet. Chest health excellent. Mother's health is a blessing.",
            "family": "Mother is religious and long-lived. Home has a temple or sacred space. Wife is homemaker and devotee. Children grow in spiritual environment. Family reputation for generosity.",
        },
        5: {
            "effect": "Excellent children, religious and well-educated. Gains through wise speculation. Spiritual teacher.",
            "good": "Brilliant children, education, speculation gains, spiritual teaching, guru role.",
            "bad": "Over-protective of children. Religious rigidity.",
            "remedy": "Apply saffron tilak. Offer saffron at temple. Teach children spiritual values.",
            "age_triggers": ["Teaching begins at 22", "First child around 25-28", "Children's brilliance at 30", "Speculation gains at 33", "Guru role at 36-40", "Religious rigidity at 45"],
            "conditions": [
                "If Sun conjoins, child becomes a government leader",
                "If Moon conjoins, emotionally wise children",
                "If Venus conjoins, children in arts and creative fields",
                "If Saturn aspects, children delayed but eventually very successful",
            ],
            "financial": "Education sector is the best investment. Children bring wealth. Religious teaching income. Gold and saffron speculation. Temple trust management. Scholarship funds. Avoid non-ethical speculation.",
            "health": "Stomach, spine, liver. Stomach health good. Liver function strong but watch diet. Spine needs care. Children's health is generally excellent.",
            "family": "Children are the pride of the family. Sons and daughters both bring honor. Love life is ethical and leads to marriage. Mother guides spiritual education. Grandchildren are scholars.",
        },
        6: {
            "effect": "Wins through wisdom and dharma. Good health through ayurveda. Enemy defeat through knowledge.",
            "good": "Health through knowledge, enemy defeat, legal wins, ayurvedic healing.",
            "bad": "Weight gain, liver issues, disputes with maternal uncle.",
            "remedy": "Apply saffron tilak. Donate turmeric. Serve at temple.",
            "age_triggers": ["Ayurvedic health at 22", "Enemy defeat at 25", "Legal wins at 28-30", "Liver concern at 33", "Healing career at 36", "Weight management at 40"],
            "conditions": [
                "If Mars conjoins, surgeon or military doctor",
                "If Sun conjoins, government health officer",
                "If Saturn aspects, chronic but manageable health issues",
                "If Rahu afflicts, false accusations and mysterious health problems",
            ],
            "financial": "Ayurvedic and health sector most profitable. Temple medicine. Turmeric and herbal product business. Legal practice in family law. Health advisory services. Avoid debt-based businesses.",
            "health": "Intestines, liver, immune system. Liver function needs monitoring. Digestive health through ayurveda. Weight gain from liver imbalance. Turmeric in daily diet essential. Immune system strong.",
            "family": "Maternal uncle has disputes or health issues. Family health consciousness is high. Wife interested in natural healing. Children are health-conscious. Family follows ayurvedic lifestyle.",
        },
        7: {
            "effect": "Spouse is religious and wise. Marriage brings fortune. Partnership in spiritual ventures.",
            "good": "Religious spouse, fortune through marriage, spiritual partnerships, foreign spouse possible.",
            "bad": "Can be too dominating in marriage. Spouse health if Venus is weak.",
            "remedy": "Apply saffron tilak. Keep gold with spouse. Worship together.",
            "age_triggers": ["Marriage after 24", "Spouse brings fortune at 27", "Partnership success at 30", "Spiritual partnership at 33", "Domination issues at 36", "Harmonious marriage after 40"],
            "conditions": [
                "If Venus conjoins, extremely fortunate and beautiful marriage",
                "If Saturn conjoins, marriage delayed but to a wise mature person",
                "If Moon conjoins, emotional and deeply bonded marriage",
                "If Rahu afflicts, foreign spouse but marriage instability",
            ],
            "financial": "Partnership in educational or religious ventures. Spouse brings family wealth. Temple or trust partnership. Gold and jewelry through marriage. Advisory partnerships. Foreign spouse brings foreign wealth.",
            "health": "Kidneys, lower back. Generally healthy marriage life. Spouse's health needs attention if Venus is weak. Lower back from sedentary religious lifestyle. Weight management through partnership.",
            "family": "Spouse is religious, wise, and from good family. In-laws are respected in society. Marriage is the foundation of prosperity. Children born into blessed union. Family worship is central.",
        },
        8: {
            "effect": "Spiritual transformation. Occult knowledge. Inheritance from religious family. Longevity.",
            "good": "Long life, occult wisdom, inheritance, transformation, insurance.",
            "bad": "Liver/diabetes issues, spiritual crisis, hidden enemies in religion.",
            "remedy": "Apply saffron tilak. Donate gold at temple. Keep saffron water at home.",
            "age_triggers": ["Occult interest at 22", "Spiritual crisis at 25", "Inheritance matter at 28", "Transformation at 33", "Diabetes risk at 36", "Longevity confirmed after 42"],
            "conditions": [
                "If Saturn conjoins, extremely long life with chronic religious doubts",
                "If Mars conjoins, surgery related to liver or abdomen",
                "If Rahu conjoins, deep occult powers but spiritual confusion",
                "If Sun conjoins, government inheritance and spiritual authority",
            ],
            "financial": "Inheritance from religious family or institution. Insurance benefits. Gold from ancestors. Temple trust inheritance. Avoid speculative investments. Occult healing can bring income. Estate management.",
            "health": "Liver, diabetes, reproductive. Liver function critical to monitor. Diabetes risk increases with age. Reproductive health tied to spiritual practices. Long life if liver is maintained.",
            "family": "Family has religious inheritance. Spouse's family has spiritual background. Children face transformation early. In-laws have temple or trust connections. Family secrets related to spiritual practices.",
        },
        9: {
            "effect": "Best house for Jupiter in LK. Maximum spiritual blessings. Father is guru-like. Pilgrimage.",
            "good": "Spiritual mastery, guru status, father's blessings, pilgrimage, fortune, temple building.",
            "bad": "Spiritual pride, can be dogmatic.",
            "remedy": "Apply saffron tilak. Serve guru and father. Build or donate to temple.",
            "age_triggers": ["Spiritual awakening at 16", "Guru found at 22", "Father's blessings at 25", "Fortune rises at 28", "Temple building at 33", "Guru status at 36-45", "Dogmatism risk at 48"],
            "conditions": [
                "If Sun conjoins, religious and political leader",
                "If Moon conjoins, compassionate spiritual healer",
                "If Mars conjoins, religious warrior for dharma",
                "If Rahu afflicts, false guru tendency or deception in religion",
            ],
            "financial": "Fortune through religion, education, and spiritual teaching. Temple trust management. Gold and saffron business. Pilgrimage industry. University or school founding. Export of religious items. Father's wealth continues.",
            "health": "Hips, liver, thighs. Generally excellent health. Liver is strong with spiritual diet. Hip issues from sitting in meditation. Thighs strong from pilgrimage walking. Long and healthy life.",
            "family": "Father is guru-like and long-lived. Family has religious authority. Wife is devoted and religious. Children follow spiritual path. Family builds temples and educational institutions across generations.",
        },
        10: {
            "effect": "Jupiter debilitated here in LK. Career in teaching/religion but with obstacles. Needs effort.",
            "good": "Teaching career (with effort), judicial/religious roles, eventually gains respect.",
            "bad": "Career obstacles, delayed success, liver issues, children may suffer.",
            "remedy": "Apply saffron tilak. Donate gold to temple. Serve elders and gurus.",
            "age_triggers": ["Career obstacles at 22-28", "Teaching career starts at 28", "Gradual respect at 33", "Judicial role at 36", "Children suffer at 38", "Career stability after 42"],
            "conditions": [
                "If Sun conjoins, government education department with struggles",
                "If Saturn conjoins, very delayed but eventually judicial or spiritual authority",
                "If Mars aspects, career in military education or training",
                "If Moon conjoins, career in counseling or social welfare",
            ],
            "financial": "Career income comes with delays. Teaching salary is modest. Judicial career after prolonged struggle. Avoid business -- stick to service. Temple or trust management after 36. Gold investments face delays in returns.",
            "health": "Knees, liver, weight. Knee problems from career stress. Liver function compromised. Weight fluctuations. Career worries affect digestive health. Diabetes monitoring essential.",
            "family": "Children may face career obstacles. Wife worries about career. Father's career was also challenging. Family reputation built through perseverance. Recognition comes late but is lasting.",
        },
        11: {
            "effect": "Gains through wisdom and religion. Wealthy through ethical means. Wise friends and elder children.",
            "good": "Wealth through dharma, wise friends, fulfilled wishes, elder children prosper.",
            "bad": "Can attract false friends. Over-generosity with wrong people.",
            "remedy": "Apply saffron tilak. Keep gold. Donate to temple on Thursday.",
            "age_triggers": ["Wise friends at 22", "Income through dharma at 25", "Wishes fulfilled at 28-33", "Elder child prospers at 30", "False friends at 36", "Wealth established by 42"],
            "conditions": [
                "If Sun conjoins, gains through government and religious authority",
                "If Moon conjoins, gains through women and public religious work",
                "If Saturn aspects, delayed gains but ethically earned wealth",
                "If Rahu conjoins, sudden wealth through foreign religious connections",
            ],
            "financial": "Ethical wealth accumulation. Gold and banking investments. Religious institution income. Friends bring investment opportunities. Educational trust returns. Avoid lending to friends. Thursday donations bring returns.",
            "health": "Ankles, calves, liver. Generally healthy. Liver function good. Ankle swelling from sitting. Calves need exercise. Social life keeps mental health positive.",
            "family": "Elder child prospers and brings honor. Friends are wise and supportive. Family gains through ethical connections. Wife appreciates generous nature. Grandchildren are well-placed.",
        },
        12: {
            "effect": "Excellent for spiritual liberation. Foreign spiritual journey. Expenditure on pilgrimage and charity.",
            "good": "Moksha, foreign spiritual travel, ashram life, charitable nature, peaceful death.",
            "bad": "Excessive expenditure, away from family, liver issues.",
            "remedy": "Apply saffron tilak. Offer saffron at Vishnu temple. Donate to charity.",
            "age_triggers": ["Spiritual journey begins at 22", "Foreign spiritual travel at 25", "Ashram connection at 30", "Charitable work at 33-36", "Family distance at 40", "Moksha path after 48"],
            "conditions": [
                "If Venus conjoins, luxury ashram and spiritual love",
                "If Saturn conjoins, austere spiritual life in foreign land",
                "If Rahu conjoins, foreign spiritual confusion then clarity",
                "If Moon conjoins, emotional spiritual journey and foreign temples",
            ],
            "financial": "Expenditure on spiritual causes and foreign pilgrimage. Ashram management abroad. Charity brings hidden returns. Foreign temple trust. Avoid material investments. Spiritual healing practice abroad. Donations are the best investment.",
            "health": "Feet, liver, sleep. Foot issues during pilgrimage. Liver needs spiritual diet. Sleep is deep and peaceful with meditation. Foreign health care may be needed. Spiritual practices heal chronic conditions.",
            "family": "Family is secondary to spiritual mission. Wife accepts spiritual lifestyle. Children may feel neglected. Foreign ashram becomes second home. Family reunites for spiritual events.",
        },
    },

    # ----- VENUS -----
    "Venus": {
        1: {
            "effect": "Attractive and charming personality. Love for luxury. Creative and artistic. Good married life.",
            "good": "Beauty, charm, artistic talent, luxury, good marriage prospects, creative career.",
            "bad": "Over-indulgent, lazy, too focused on appearance.",
            "remedy": "Donate white items on Friday. Keep silver. Respect spouse.",
            "age_triggers": ["Charm peaks at 22-25", "Marriage prospects at 24", "Luxury lifestyle at 28", "Creative career at 30", "Laziness trap at 33", "Artistic maturity at 40"],
            "conditions": [
                "If Jupiter aspects, beauty combined with wisdom -- very fortunate",
                "If Mars conjoins, passionate personality but prone to conflicts",
                "If Saturn conjoins, beauty with discipline -- modeling or fashion",
                "If Rahu conjoins, unconventional beauty and foreign admiration",
            ],
            "financial": "Wealth through beauty, arts, fashion, and luxury items. Creative career income. Diamond and jewelry business. Fashion industry. Cosmetics trading. Avoid heavy industry. Silver and platinum investments.",
            "health": "Face, skin, reproductive, kidneys. Beautiful complexion. Reproductive health strong. Kidney function needs care. Skin sensitivity. Over-indulgence leads to weight gain.",
            "family": "Spouse is attractive and loving. Marriage is beautiful. Children inherit good looks. Mother is charming. Family life is luxurious. Home is aesthetically decorated.",
        },
        2: {
            "effect": "Wealthy through beauty and arts. Sweet voice. Luxury in family. Jewelry collection.",
            "good": "Family wealth, beautiful voice/singing, jewelry, luxury items, happy family.",
            "bad": "Over-spending on luxury, lazy speech, eye problems if Sun afflicts.",
            "remedy": "Donate ghee/curd on Friday. Keep diamond/opal. Respect women in family.",
            "age_triggers": ["Voice develops at 22", "Jewelry collection at 25", "Family wealth at 28", "Singing career at 30", "Luxury overspending at 33", "Established wealth by 40"],
            "conditions": [
                "If Jupiter conjoins, massive family wealth and beautiful voice",
                "If Mercury conjoins, business in luxury goods and sweet speech",
                "If Saturn aspects, delayed but elegant wealth building",
                "If Sun afflicts, eye problems and family ego disputes",
            ],
            "financial": "Jewelry and luxury goods business. Singing and voice-over career. Dairy and ghee business. Family banking and savings. Diamond and gem investments. Beauty parlor chain. Fashion retail.",
            "health": "Throat, face, eyes, teeth. Sweet tooth leads to dental issues. Throat needs care for singers. Eye problems if Sun afflicts. Facial skin is beautiful but sensitive.",
            "family": "Family is wealthy and cultured. Wife brings jewelry and beauty to family. Children have artistic talents. Family voice in society. Wealth through women in family.",
        },
        3: {
            "effect": "Artistic communication. Beautiful siblings or spouse of siblings. Creative writing.",
            "good": "Creative writing, artistic siblings, short travels for pleasure, good neighbors.",
            "bad": "Too many romantic distractions, shallow relationships.",
            "remedy": "Donate white items. Keep cream-colored cloth.",
            "age_triggers": ["Creative writing at 22", "Artistic travels at 25", "Romantic distractions at 28", "Sibling marriage at 30", "Creative maturity at 36"],
            "conditions": [
                "If Mercury conjoins, beautiful writing and journalism in arts",
                "If Mars conjoins, passionate but aggressive creative expression",
                "If Moon conjoins, poetry and emotional creative work",
                "If Saturn aspects, serious artistic discipline",
            ],
            "financial": "Creative writing, arts journalism, fashion media. Beauty travel blogging. Sibling partnerships in creative fields. Short-distance luxury trade. Greeting card and gift business.",
            "health": "Arms, shoulders, skin. Skin on arms needs care. Shoulder tension from creative work. Throat infections from travel. Nervous system sensitivity.",
            "family": "Siblings are attractive or artistic. Younger sister is beautiful. Neighbors are friendly. Family known for creativity. Sibling's spouse is attractive.",
        },
        4: {
            "effect": "Beautiful home. Luxury vehicles. Mother is beautiful. Domestic comforts.",
            "good": "Luxury home, beautiful vehicles, mother's beauty, domestic harmony, interior decoration.",
            "bad": "Over-attachment to comforts, laziness at home.",
            "remedy": "Keep the home beautiful and clean. Donate white cows/cow products.",
            "age_triggers": ["Home beautification at 24", "Luxury vehicle at 27", "Mother's grace at 28", "Interior design at 30", "Comfort trap at 33", "Settled luxury after 40"],
            "conditions": [
                "If Moon conjoins, extremely beautiful and comfortable home",
                "If Jupiter conjoins, luxury home with spiritual space",
                "If Mars conjoins, home with garden and outdoor space",
                "If Saturn aspects from H10, luxury home through career achievement",
            ],
            "financial": "Real estate in premium locations. Interior design business. Luxury car dealership. Home decor and furnishing. Dairy farming on beautiful land. Flower nursery business. Avoid industrial property.",
            "health": "Heart, chest, skin. Heart health through emotional contentment. Chest health good. Skin benefits from comfortable lifestyle. Over-comfort leads to lethargy and weight issues.",
            "family": "Mother is beautiful and graceful. Home is the pride of the family. Wife excels at homemaking and decoration. Children grow in luxury. Family entertaining is frequent and lavish.",
        },
        5: {
            "effect": "Romantic and creative. Love marriage possible. Artistic children. Gains in entertainment.",
            "good": "Romance, love marriage, artistic children, entertainment gains, cinema/music.",
            "bad": "Multiple love affairs, heartbreak, children may be spoiled.",
            "remedy": "Donate curd/ghee on Friday. Respect wife/women. Feed white cow.",
            "age_triggers": ["Romance at 22-25", "Love marriage at 25-28", "Artistic children at 28", "Entertainment gains at 30-33", "Heartbreak risk at 36", "Creative wisdom after 42"],
            "conditions": [
                "If Mars conjoins, passionate love affair -- may cause problems",
                "If Jupiter aspects, love marriage with wealthy educated person",
                "If Saturn aspects, delayed love fulfillment and children",
                "If Rahu conjoins, unconventional love -- may be scandalous",
            ],
            "financial": "Entertainment industry -- cinema, music, drama. Creative arts income. Children's artistic education. Speculation in beauty and luxury stocks. Fashion shows and events. Love-based enterprises like matchmaking.",
            "health": "Stomach, reproductive, spine. Reproductive health strong but romantic stress. Stomach issues from emotional eating. Spine care for performers. Children's health generally good.",
            "family": "Children are artistic and beautiful. Love life is central to happiness. Daughter is especially talented. Wife and children share creative interests. Family attends cultural events.",
        },
        6: {
            "effect": "Venus debilitated here in LK. Health issues related to reproductive system. Service in beauty sector.",
            "good": "Beauty industry work, cosmetics, fashion design.",
            "bad": "Reproductive health issues, divorce risk, disputes with women, diabetes.",
            "remedy": "Donate white items on Friday. Keep curd at home. Respect all women.",
            "age_triggers": ["Beauty career at 22", "Reproductive health concern at 25", "Divorce risk at 28-30", "Diabetes caution at 33", "Service career peak at 36", "Health stabilizes at 42 with remedies"],
            "conditions": [
                "If Saturn conjoins, chronic reproductive health issues",
                "If Mars conjoins, severe marital discord and disputes",
                "If Jupiter aspects, some protection through wisdom and dharma",
                "If Rahu conjoins, mysterious reproductive issues and deception in love",
            ],
            "financial": "Beauty service industry -- not luxury but service level. Cosmetics manufacturing. Fashion at affordable level. Avoid luxury business. Health and beauty combined services. Debt issues related to marriage expenses.",
            "health": "Reproductive organs, kidneys, diabetes. Serious reproductive health concerns. Diabetes risk high. Kidney function compromised. Urinary tract infections. Skin disorders. Sugar intake must be controlled.",
            "family": "Marriage faces serious challenges. Spouse's health suffers. Women in family face health issues. Divorce or separation risk. Children born with health concerns. Mother-in-law creates disputes.",
        },
        7: {
            "effect": "Venus in its permanent house. Best for marriage. Beautiful and loving spouse. Business success.",
            "good": "Perfect marriage, beautiful spouse, business success, luxury, foreign trade.",
            "bad": "Too much pleasure-seeking, multiple attractions.",
            "remedy": "Keep diamond/opal. Respect spouse. Donate white sweets on Friday.",
            "age_triggers": ["Marriage ideally at 24-27", "Spouse brings beauty and wealth", "Business success at 28", "Luxury peak at 30-33", "Multiple attractions at 36", "Settled marriage after 40"],
            "conditions": [
                "If Jupiter aspects from H1, perfect marriage with religious educated spouse",
                "If Mercury conjoins, spouse in business -- dual income",
                "If Saturn conjoins, mature marriage with older spouse",
                "If Rahu conjoins, foreign spouse -- beautiful but unstable",
            ],
            "financial": "Partnership business in luxury, beauty, and fashion is extremely profitable. Import-export of luxury goods. Jewelry business with partner. Foreign trade in beauty products. Diamond investments through marriage wealth.",
            "health": "Kidneys, reproductive, lower back. Kidneys need regular care. Reproductive health excellent. Lower back from luxury lifestyle. Over-indulgence affects health.",
            "family": "Spouse is beautiful, loving, and brings wealth. Marriage is the foundation of life. In-laws are wealthy and supportive. Children are attractive and well-mannered. Family life revolves around love and luxury.",
        },
        8: {
            "effect": "Hidden beauty and talents. Spouse's family wealth. Insurance through marriage. Tantric attraction.",
            "good": "Spouse's wealth, insurance gains, hidden artistic talents, transformation through love.",
            "bad": "Reproductive health issues, spouse's health, marriage secrets.",
            "remedy": "Donate white cow. Keep cream/white items. Respect in-laws.",
            "age_triggers": ["Hidden talents emerge at 22", "Spouse's wealth at 25", "Insurance matters at 28", "Marriage secrets at 30", "Reproductive concern at 33", "Tantric interest at 36", "Transformation after 42"],
            "conditions": [
                "If Saturn conjoins, spouse's family has old wealth but chronic health",
                "If Rahu conjoins, hidden affairs and spouse's deception",
                "If Jupiter aspects, transformation through spiritual love",
                "If Mars conjoins, surgery related to reproductive system",
            ],
            "financial": "Spouse's family wealth is the primary financial source. Insurance and inheritance through marriage. Hidden artistic talents bring income. Beauty treatments and surgery. Avoid open business -- hidden or behind-the-scenes work better.",
            "health": "Reproductive organs, kidneys, chronic ailments. Reproductive health issues are serious. Kidney complications. Chronic conditions emerge after marriage. Spouse's health needs attention. Surgery possible.",
            "family": "Spouse's family has wealth but secrets. Marriage has hidden dynamics. In-laws control wealth. Children inherit hidden talents. Family transformation through crisis.",
        },
        9: {
            "effect": "Love for travel and religion. Foreign spouse possible. Beauty in spiritual pursuits.",
            "good": "Foreign spouse, spiritual arts, pilgrimage, beauty in faith, guru's wife blesses.",
            "bad": "Extra-marital attractions during travel, religious hypocrisy.",
            "remedy": "Donate ghee at temple. Respect women at religious places.",
            "age_triggers": ["Spiritual beauty at 22", "Foreign spouse at 25-28", "Pilgrimage at 30", "Artistic spirituality at 33", "Travel temptations at 36", "Settled faith after 42"],
            "conditions": [
                "If Jupiter conjoins, marriage to spiritual scholar or healer",
                "If Rahu conjoins, foreign spouse from completely different culture",
                "If Saturn aspects, delayed marriage but to a spiritual person",
                "If Mars conjoins, passionate religious expression",
            ],
            "financial": "Foreign beauty products export. Spiritual arts business. Pilgrimage tourism luxury segment. Fashion exports. Religious jewelry and artifacts. Luxury spiritual retreat business.",
            "health": "Hips, thighs, kidneys. Hip issues from travel. Thigh beauty maintained. Kidney care during foreign travel. Reproductive health during pilgrimage needs attention.",
            "family": "Foreign spouse brings different culture. Father appreciates beauty and arts. Wife is spiritual and beautiful. Children enjoy foreign and spiritual environments. Family pilgrimages are luxurious.",
        },
        10: {
            "effect": "Career in arts, beauty, luxury, fashion, or entertainment. Government favor through charm.",
            "good": "Career in arts/beauty/fashion, government favor, luxury through career, public charm.",
            "bad": "Office romance issues, lazy at work, too focused on appearance at job.",
            "remedy": "Donate white items. Keep opal/diamond. Respect female colleagues.",
            "age_triggers": ["Career in beauty/arts at 22", "Government favor at 25", "Public charm at 28", "Career peak at 33-36", "Office romance risk at 30", "Established luxury career at 42"],
            "conditions": [
                "If Sun conjoins, government cultural department or ambassador",
                "If Saturn conjoins, fashion industry with discipline",
                "If Mercury conjoins, business management in luxury sector",
                "If Rahu conjoins, foreign fashion or film career",
            ],
            "financial": "Fashion industry leadership. Beauty brand management. Government cultural department. Luxury car or real estate career. Entertainment industry management. Public relations career. Diamond and jewelry career.",
            "health": "Knees, skin, reproductive. Knee issues from high heels. Skin care is career essential. Reproductive health from work stress. Career stress affects beauty.",
            "family": "Family gains status through career. Wife or husband in same industry possible. Children inspired by parent's glamorous career. Public sees family as attractive.",
        },
        11: {
            "effect": "Gains through women and arts. Wishes related to luxury fulfilled. Beautiful friends.",
            "good": "Luxury gains, artistic income, beautiful friends, wishes fulfilled, elder daughter.",
            "bad": "Wrong friendships with women, spending on luxury.",
            "remedy": "Keep white items. Donate to women's causes. Keep silver.",
            "age_triggers": ["Artistic gains at 24", "Beautiful friend circle at 27", "Luxury wishes fulfilled at 30", "Elder daughter success at 33", "Wrong friendships at 36", "Established luxury at 42"],
            "conditions": [
                "If Jupiter conjoins, gains through ethical luxury and educational arts",
                "If Mercury conjoins, business gains through beauty trade network",
                "If Rahu conjoins, sudden gains through foreign beauty connection",
                "If Saturn aspects, delayed but permanent luxury wealth",
            ],
            "financial": "Women's product businesses. Luxury brand networking. Beauty industry gains. Elder daughter brings financial opportunity. Fashion events and shows. Jewelry networking. Social media beauty influence.",
            "health": "Ankles, calves, kidneys. Ankle pain from fashion footwear. Calves need exercise. Kidney function from social lifestyle. Allergies from cosmetics.",
            "family": "Elder daughter is beautiful and successful. Friends become like family. Social network is attractive and influential. Wife enjoys social life. Family known for style and grace.",
        },
        12: {
            "effect": "Venus exalted here in LK. Foreign luxury. Bed pleasures. Spiritual love. Expenditure on beauty.",
            "good": "Foreign luxury, spiritual love, bedroom happiness, artistic liberation, charity.",
            "bad": "Over-expenditure on pleasure, foreign losses, secret affairs.",
            "remedy": "Donate white cow. Keep diamond/opal. Respect spouse's family.",
            "age_triggers": ["Foreign luxury at 24", "Spiritual love at 27", "Bed pleasures peak at 30", "Artistic liberation at 33", "Secret affair risk at 36", "Charitable beauty after 42"],
            "conditions": [
                "If Jupiter conjoins, spiritual love and moksha through beauty",
                "If Saturn conjoins, austere beauty and disciplined spiritual love",
                "If Rahu conjoins, foreign affair and luxury with deception",
                "If Moon conjoins, emotional luxury and foreign comfort",
            ],
            "financial": "Foreign luxury goods import. Spiritual arts abroad. Bed linen and comfort business. Foreign fashion career. Charity in beauty sector. Hospitality industry abroad. Hidden luxury income.",
            "health": "Feet, reproductive, sleep. Feet are beautiful but sensitive. Reproductive health strong but secret matters. Sleep is luxurious and deep. Foreign health treatments are beneficial.",
            "family": "Spouse enjoys foreign life. Marriage has spiritual dimension. Children may settle abroad in luxury. In-laws benefit from foreign connection. Family expenditure on beauty and comfort.",
        },
    },

    # ----- SATURN -----
    "Saturn": {
        1: {
            "effect": "Disciplined but hard life initially. Success comes late. Health issues in early life. Serious personality.",
            "good": "Discipline, longevity, patience, eventual success, iron will, self-made.",
            "bad": "Early hardships, delayed marriage, bone/joint issues, pessimistic nature.",
            "remedy": "Donate mustard oil on Saturday. Feed crows. Keep iron nail in pocket.",
            "age_triggers": ["Hardship period 0-22", "Discipline builds at 25", "Self-made start at 28", "Marriage after 30", "Success begins at 36", "Iron will established at 42", "Peak success at 48-55"],
            "conditions": [
                "If Sun afflicts from H7, government enmity and career blocks",
                "If Jupiter aspects, discipline combined with wisdom -- saint-like",
                "If Mars conjoins, accidents and aggressive hardship",
                "If Rahu conjoins, foreign hardship but eventual foreign success",
            ],
            "financial": "Wealth comes late but stays permanently. Iron, steel, oil, and construction business. Government service after struggle. Real estate after 36. Avoid speculation entirely. Savings in iron and land.",
            "health": "Bones, joints, legs, chronic ailments. Bone and joint problems from youth. Chronic issues managed through discipline. Knee pain. Dark circles and aged appearance. Long life despite health issues.",
            "family": "Father may have faced hardship. Marriage is delayed. Spouse is mature and disciplined. Children learn patience. Family rises through generations of hard work.",
        },
        2: {
            "effect": "Family struggles. Harsh speech. Wealth comes slowly but stays. Dental issues.",
            "good": "Long-lasting wealth, iron/steel business, practical speech, savings.",
            "bad": "Family hardships, dental problems, harsh voice, delayed wealth.",
            "remedy": "Donate black dal on Saturday. Keep iron. Do not drink milk at night.",
            "age_triggers": ["Family struggle 0-25", "Harsh speech at 25", "Dental issues at 28", "Wealth starts at 33", "Savings grow at 36", "Established family at 42", "Wealth peak at 48"],
            "conditions": [
                "If Jupiter conjoins, disciplined family wealth through banking",
                "If Moon afflicts, family emotional coldness and mother's suffering",
                "If Mars conjoins, harsh speech causes family rifts",
                "If Mercury conjoins, practical business speech and accounting wealth",
            ],
            "financial": "Family wealth through iron, steel, and hardware. Slow but permanent savings. Banking in conservative instruments. Fixed deposits over speculation. Real estate after 33. Avoid food and luxury business.",
            "health": "Teeth, jaw, throat, eyes. Chronic dental problems. Jaw pain. Throat dryness. Eye strain from hard work. Cold food and drink cause issues.",
            "family": "Family faces poverty or hardship initially. Speech is harsh but truthful. Wife manages frugal household. Children learn value of money. Family wealth accumulates over generations.",
        },
        3: {
            "effect": "Patient and persistent. Siblings may suffer. Travel for work. Writing on serious topics.",
            "good": "Persistent courage, serious writing, work travel, eventual sibling harmony.",
            "bad": "Sibling troubles, shoulder/arm issues, delayed communications.",
            "remedy": "Donate mustard oil. Feed crows. Keep iron.",
            "age_triggers": ["Sibling issues at 22-25", "Work travel at 28", "Serious writing at 30", "Communication delay resolved at 33", "Persistent courage at 36", "Sibling harmony at 42"],
            "conditions": [
                "If Mars conjoins, sibling suffers accident or health issues",
                "If Mercury conjoins, serious research writing career",
                "If Rahu conjoins, foreign work travel with hardship",
                "If Jupiter aspects, wisdom through persistent effort",
            ],
            "financial": "Income through disciplined hard work and travel. Serious writing and documentation work. Iron and hardware trading. Courier and logistics in heavy goods. Sibling partnerships need patience.",
            "health": "Shoulders, arms, nervous system. Chronic shoulder pain. Arm numbness. Nervous tension from overwork. Travel fatigue. Cold-related illnesses during travel.",
            "family": "Siblings face initial hardship. Younger brother may struggle. Neighbors are distant. Family communication is limited but meaningful. Hard work defines family culture.",
        },
        4: {
            "effect": "Late property gains. Mother may suffer. Domestic life is serious. Old house or inherited property.",
            "good": "Inherited property, old buildings, mines, eventually peaceful home.",
            "bad": "Mother's suffering, domestic coldness, heart issues, late property.",
            "remedy": "Offer milk to Shivling. Keep iron nails in foundation. Serve mother.",
            "age_triggers": ["Domestic coldness 0-28", "Mother's health concern at 25", "Old property at 30", "Heart caution at 33", "Domestic peace at 36", "Property gains at 42", "Settled home at 48"],
            "conditions": [
                "If Moon conjoins, mother suffers severely -- serve mother as remedy",
                "If Mars conjoins, property through construction and engineering",
                "If Jupiter aspects, temple-like discipline at home",
                "If Sun afflicts from H10, government property dispute",
            ],
            "financial": "Property comes late but is permanent. Old buildings, mines, and industrial land. Renovation business. Ancestral property after legal battles. Avoid buying property before 30. Iron foundry on own land.",
            "health": "Heart, chest, bones. Heart issues from domestic stress. Chest coldness. Bone density issues. Chronic joint pain at home. Cold home affects health.",
            "family": "Mother suffers physically or emotionally. Domestic life is serious and disciplined. Wife is patient but cold. Children grow up in strict environment. Home feels heavy but stable.",
        },
        5: {
            "effect": "Saturn debilitated in LK. Children issues. Education delayed. Speculation losses. Pessimistic in love.",
            "good": "Eventually wise children, deep study, serious romance leading to stable marriage.",
            "bad": "Children delays/issues, education obstacles, speculation losses, pessimism.",
            "remedy": "Donate almonds. Give milk to snakes (Nag). Feed crows on Saturday.",
            "age_triggers": ["Education struggles 16-25", "Children delayed till 30+", "Speculation loss at 28", "Pessimism in love at 30", "Children bring wisdom at 36", "Education success at 40", "Children stabilize at 45"],
            "conditions": [
                "If Jupiter aspects, children delayed but become scholars",
                "If Venus conjoins, love life is cold and delayed",
                "If Mars conjoins, children face health issues and aggression",
                "If Rahu conjoins, children in foreign land with difficulties",
            ],
            "financial": "Never speculate. Children's education is expensive and delayed. Avoid gambling, stock market, and lottery entirely. Slow and steady savings only. Income through serious academic work. Coal or mining investments.",
            "health": "Stomach, spine, reproductive. Chronic stomach issues. Spine deterioration. Reproductive difficulties. Pessimism affects all organ systems. Almond and milk diet recommended.",
            "family": "Children are delayed and face obstacles. First child may have health issues. Love life is serious and painful before joy. Wife patient during difficult parenting. Grandchildren bring the joy children didn't.",
        },
        6: {
            "effect": "Victory over enemies through patience. Good for labor/factory work. Health improves after 36.",
            "good": "Enemy defeat, labor success, factory work, health through discipline.",
            "bad": "Chronic health issues before 36, disputes with servants, joint pain.",
            "remedy": "Feed dogs. Donate black items on Saturday. Keep iron.",
            "age_triggers": ["Health issues 0-36", "Enemy defeat at 28", "Factory/labor career at 25", "Joint pain at 30", "Health turns around at 36", "Enemy completely defeated at 42"],
            "conditions": [
                "If Mars conjoins, working in heavy industry or mining",
                "If Mercury conjoins, accounting in factory or labor union",
                "If Rahu conjoins, foreign labor and industrial work",
                "If Jupiter aspects, health improves through disciplined lifestyle",
            ],
            "financial": "Factory and labor sector income. Heavy industry. Mining and quarrying. Health sector through discipline. Debt recovery (slow but certain). Avoid lending money. Iron and steel service businesses.",
            "health": "Joints, intestines, immune system. Chronic joint pain. Intestinal issues before 36. Immune system weakens then strengthens. Arthritis risk. Cold and damp conditions worsen health.",
            "family": "Maternal uncle faces severe hardship. Servants are troublesome but manageable. Family health consciousness is forced by circumstances. Children learn discipline from health management.",
        },
        7: {
            "effect": "Delayed marriage. Older or mature spouse. Marriage brings discipline. Partnership in iron/steel.",
            "good": "Stable marriage (after delay), mature spouse, iron/steel business, long marriage.",
            "bad": "Delayed marriage, cold relationship, spouse health, partnership delays.",
            "remedy": "Do not marry before 28. Donate black dal. Keep iron in bedroom.",
            "age_triggers": ["Do NOT marry before 28", "Marriage between 28-33", "Cold period at 33", "Partnership gains at 36", "Marriage warms at 40", "Stable long marriage at 48"],
            "conditions": [
                "If Venus conjoins, marriage delayed but eventually luxurious",
                "If Moon conjoins, emotional coldness in marriage",
                "If Jupiter aspects from H1, wise marriage decision",
                "If Mars afflicts, severe marital discord and separation risk",
            ],
            "financial": "Iron and steel partnership business. Marriage brings slow financial stability. Avoid business partnerships before 28. Mature business partners are best. Hardware and construction partnerships.",
            "health": "Lower back, kidneys, reproductive. Chronic lower back pain. Kidney function decreases. Reproductive delays. Spouse's chronic health issues. Cold conditions worsen symptoms.",
            "family": "Spouse is older, mature, and disciplined. In-laws face hardship. Marriage is karmic and serious. Children born late are more stable. Family life improves dramatically after 40.",
        },
        8: {
            "effect": "Saturn's permanent house. Longevity but chronic health issues. Inheritance after long delays. Occult depth.",
            "good": "Very long life, deep occult knowledge, eventual inheritance, transformation.",
            "bad": "Chronic diseases, piles, joint pain, delayed inheritance, depression.",
            "remedy": "Donate mustard oil on Saturday. Feed crows. Keep iron items.",
            "age_triggers": ["Chronic health from 22", "Depression risk at 28", "Occult interest at 30", "Inheritance fight at 33", "Piles/joint issues at 36", "Transformation at 42", "Long life confirmed at 48+"],
            "conditions": [
                "If Mars conjoins, surgery and chronic blood disorders",
                "If Rahu conjoins, accidents and mysterious chronic diseases",
                "If Jupiter aspects, long life with spiritual depth",
                "If Moon afflicts, severe depression and mother's suffering",
            ],
            "financial": "Inheritance comes after long legal battles. Insurance claims delayed for years. Mining and underground resources. Oil and petroleum long-term investments. Avoid quick-return schemes. Estate management after 42.",
            "health": "Chronic diseases, piles, joints, depression. Piles and fistula common. Chronic joint degeneration. Depression is a serious risk. Skin darkening. Slow healing. Very long life despite all issues.",
            "family": "Family has heavy karma. Inheritance disputes across generations. Spouse faces chronic health. Children inherit endurance. In-laws have old property with legal issues.",
        },
        9: {
            "effect": "Hard work in religious/spiritual life. Father may suffer. Late pilgrimage brings peace.",
            "good": "Disciplined spirituality, hard-earned guru blessings, eventually religious.",
            "bad": "Father's hardships, delayed fortune, spiritual dryness, pessimism in faith.",
            "remedy": "Serve old people. Donate black blankets. Feed crows.",
            "age_triggers": ["Father suffers from 22", "Spiritual dryness at 25-30", "Fortune delayed till 33", "Pilgrimage at 36", "Guru found late at 40", "Spiritual depth at 45", "Peace at 50"],
            "conditions": [
                "If Sun afflicts, father suffers government penalties",
                "If Jupiter conjoins, disciplined spiritual teacher after 40",
                "If Rahu conjoins, foreign spiritual hardship",
                "If Mars conjoins, aggressive spiritual journey",
            ],
            "financial": "Fortune comes very late. Father's wealth is blocked. Pilgrimage expenses are high. Religious charity is the investment. Old-age home or service business. Avoid foreign speculation.",
            "health": "Hips, thighs, chronic pain. Hip joint deterioration. Thigh muscle weakness. Chronic pain during travel. Cold weather worsens conditions. Pilgrimage walking is therapeutic.",
            "family": "Father suffers significantly. Family fortune is blocked by karma. Wife is patient and religious. Children eventually find spiritual path. Family pilgrimage heals old wounds.",
        },
        10: {
            "effect": "Excellent career after 36. Government job in administration/judiciary. Slow but steady rise.",
            "good": "Government career, judiciary, administration, iron/steel industry, political rise.",
            "bad": "Early career struggles, delayed recognition, knee/bone problems.",
            "remedy": "Keep iron. Donate mustard oil on Saturday. Feed crows. Serve workers.",
            "age_triggers": ["Career struggle 0-36", "Government entry at 28", "Slow rise at 30-36", "Authority at 42", "Judiciary/admin peak at 48", "Political power at 50-55"],
            "conditions": [
                "If Sun conjoins, government career with authority but delays",
                "If Jupiter aspects, judicial career with dharmic authority",
                "If Mars conjoins, engineering or construction career",
                "If Rahu conjoins, foreign government or MNC career",
            ],
            "financial": "Government salary and pension. Iron and steel industry leadership. Real estate after 36. Administrative position brings steady wealth. Construction contracts. Avoid quick-money schemes. Long-term government bonds.",
            "health": "Knees, bones, joints. Knee problems are almost certain. Bone density loss. Joint pain from overwork. Career stress affects bones. Regular calcium and exercise essential.",
            "family": "Father is proud after initial struggles. Family rises through career. Wife supports career patiently. Children benefit from parent's late success. Family name established in government circles.",
        },
        11: {
            "effect": "Saturn exalted here in LK. Gains through hard work. Iron/steel brings wealth. Persistent friends.",
            "good": "Wealth through discipline, iron/steel income, loyal friends, wishes fulfilled.",
            "bad": "Can be miserly. Cold friendships. Elder children may struggle initially.",
            "remedy": "Donate iron items. Feed crows. Keep mustard oil at home.",
            "age_triggers": ["Gains start at 25", "Iron/steel income at 28", "Friends help at 30", "Wishes fulfilled at 33-36", "Elder child struggles then succeeds at 40", "Miserly tendency at 42", "Wealthy by 48"],
            "conditions": [
                "If Jupiter conjoins, ethical wealth through discipline and banking",
                "If Mercury conjoins, business gains through iron and technology",
                "If Venus conjoins, luxury through disciplined wealth-building",
                "If Mars conjoins, construction and defense industry gains",
            ],
            "financial": "Iron, steel, and oil business is the best investment. Real estate in industrial zones. Gains through persistent hard work. Friends in industry bring opportunities. Long-term investments outperform short-term. Government bonds and fixed deposits.",
            "health": "Calves, ankles, joints. Leg pain from standing work. Ankle issues. Joint pain managed through discipline. Overall health improves with wealth. Cold weather affects legs.",
            "family": "Elder child struggles then succeeds. Friends are loyal and hardworking. Family gains respect through discipline. Wife appreciates steady financial growth. Children inherit disciplined wealth.",
        },
        12: {
            "effect": "Expenditure through health and karma. Foreign lands bring work but hardship. Sleep issues.",
            "good": "Foreign work, karmic clearing, deep meditation, hospital/prison work.",
            "bad": "Health expenditure, foot problems, sleep issues, loneliness, exile feeling.",
            "remedy": "Donate black blankets. Feed crows on Saturday. Keep iron under pillow.",
            "age_triggers": ["Health expenditure from 22", "Foreign hardship at 25", "Sleep issues at 28", "Foot problems at 30", "Karmic clearing at 33-36", "Meditation depth at 40", "Loneliness at 42", "Peace after 48"],
            "conditions": [
                "If Rahu conjoins, foreign imprisonment or hospital stay",
                "If Jupiter aspects, spiritual monastery or ashram life",
                "If Mars conjoins, foot surgery or foreign accident",
                "If Moon afflicts, severe insomnia and mental health crisis",
            ],
            "financial": "Expenditure exceeds income on health and karmic debts. Foreign work pays but expenses are high. Hospital or prison administration. Avoid all speculation. Iron exports. Charity is the best investment for karmic returns.",
            "health": "Feet, chronic diseases, sleep, mental health. Chronic foot problems. Severe sleep disorders. Mental health needs attention. Chronic diseases worsen abroad. Cold conditions are dangerous.",
            "family": "Family is far away. Loneliness is the main challenge. Spouse adjusts with difficulty. Children feel absence. Karmic debts from past lives affect family. Meditation brings family peace eventually.",
        },
    },

    # ----- RAHU -----
    "Rahu": {
        1: {
            "effect": "Unconventional personality. Sudden rise and fall. Foreign influence. Magnetic personality but unpredictable.",
            "good": "Magnetic charm, foreign connections, sudden fame, unconventional success.",
            "bad": "Mental confusion, head diseases, unpredictable behavior, deception.",
            "remedy": "Keep silver ball. Donate barley (jau). Do not keep elephants (even idols with trunk up).",
            "age_triggers": ["Sudden rise at 22", "Foreign connection at 25", "Mental confusion at 28", "Fame at 30", "Fall risk at 33", "Stability after 42 with remedies"],
            "conditions": [
                "If Jupiter aspects, wisdom moderates Rahu's extremes",
                "If Sun conjoins, government favor then sudden downfall",
                "If Saturn conjoins, disciplined unconventional success",
                "If Moon conjoins, severe mental instability",
            ],
            "financial": "Sudden wealth through technology, foreign trade, and unconventional means. Cryptocurrency and digital assets. Import business. Sudden losses are equally possible. Keep 50% in safe assets. Electronics and IT sector.",
            "health": "Head, nervous system, mental health. Head diseases and headaches. Mental health disorders. Nervous system imbalance. Mysterious ailments. Foreign diseases. Avoid intoxicants completely.",
            "family": "Family finds native unpredictable. Foreign spouse possible. Children are unconventional. Father confused by native's choices. Mother supports despite not understanding.",
        },
        2: {
            "effect": "Sudden wealth and sudden losses. Family may have secrets. Speech can be deceptive.",
            "good": "Sudden wealth, in-laws' property, foreign trade, electronics business.",
            "bad": "Family secrets, deceptive speech, eye problems, sudden financial reversals.",
            "remedy": "Keep barley in the house. Donate to in-laws. Keep silver.",
            "age_triggers": ["Sudden wealth at 24", "Family secret revealed at 28", "Eye problems at 30", "In-laws wealth at 33", "Financial reversal at 36", "Stability after 42"],
            "conditions": [
                "If Jupiter conjoins, family wealth through foreign ethical sources",
                "If Mercury conjoins, electronics and technology business",
                "If Saturn aspects, slow but steady foreign income",
                "If Moon afflicts, deceptive speech and family emotional turmoil",
            ],
            "financial": "Electronics, technology, and foreign trade are primary income. In-laws' property brings sudden wealth. Cryptocurrency trading. Import of foreign goods. Sudden financial reversals need hedging. Keep emergency savings equal to 6 months income.",
            "health": "Eyes, face, throat. Eye problems including vision changes. Facial skin disorders. Throat infections from deceptive speech. Allergies to foreign foods.",
            "family": "Family has secrets or unconventional background. In-laws play significant role. Speech can be misleading. Children have foreign influence. Family wealth fluctuates dramatically.",
        },
        3: {
            "effect": "Rahu exalted here in LK. Extremely powerful communication. Media/technology success.",
            "good": "Media success, technology gains, powerful writing, foreign travel, internet business.",
            "bad": "Manipulation through communication, sibling estrangement, nervous issues.",
            "remedy": "Keep silver. Donate barley. Wear sapphire (if suitable).",
            "age_triggers": ["Media career at 22", "Technology success at 25", "Internet business at 28", "Powerful communication at 30", "Sibling issues at 33", "Peak media at 36", "Nervous issues at 40"],
            "conditions": [
                "If Mercury conjoins, technology mogul potential",
                "If Mars conjoins, aggressive media and technology",
                "If Jupiter aspects, ethical technology and media leadership",
                "If Saturn aspects, delayed but massive technology empire",
            ],
            "financial": "Technology, media, and internet businesses are extremely profitable. Social media and digital marketing. Telecommunications. Foreign communication business. Sibling partnerships in tech. Software development and AI.",
            "health": "Arms, shoulders, nervous system. Carpal tunnel from technology use. Shoulder tension. Nervous exhaustion from screens. Hearing issues from devices.",
            "family": "Siblings may be estranged or in foreign lands. Younger brother in technology. Family communication through digital means. Mother's siblings involved in foreign affairs.",
        },
        4: {
            "effect": "Domestic disturbances. Foreign property. Mother may be unconventional. Electronics at home.",
            "good": "Foreign property, electronics business from home, unconventional domestic setup.",
            "bad": "Domestic confusion, mother's strange behavior, property disputes, mental unrest.",
            "remedy": "Keep barley under bed. Donate silver items. Do not keep pets (especially dogs).",
            "age_triggers": ["Domestic confusion from 22", "Foreign property at 28", "Mother's behavior at 30", "Electronics at home at 33", "Mental unrest at 36", "Domestic peace after 42 with remedies"],
            "conditions": [
                "If Moon conjoins, severe mental disturbance at home",
                "If Saturn aspects from H10, foreign property through difficult career",
                "If Jupiter aspects, unconventional but wise home setup",
                "If Mars conjoins, fire or electrical hazard at home",
            ],
            "financial": "Foreign property investment. Electronics business from home office. Online business. Smart home technology business. Avoid traditional real estate. Property in foreign land appreciates better.",
            "health": "Heart, chest, mental health. Mental unrest affects heart. Chest congestion from home environment. Electromagnetic sensitivity. Mental health needs attention. Sleep aids with technology.",
            "family": "Mother is unconventional or has foreign connections. Home has unusual setup. Wife from different background. Children grow up with technology. Family moves frequently or has multiple homes.",
        },
        5: {
            "effect": "Unusual children. Unconventional education. Sudden speculation gains/losses. Foreign education.",
            "good": "Foreign education, technology-based speculation, unconventional children.",
            "bad": "Children issues, speculation losses, heartbreak, miscarriage risk.",
            "remedy": "Donate barley. Keep silver square. Do not gamble.",
            "age_triggers": ["Foreign education at 22", "Speculation at 25", "Children issues at 28", "Heartbreak at 30", "Unconventional children at 33", "Education success abroad at 36"],
            "conditions": [
                "If Jupiter aspects, children succeed in foreign education",
                "If Venus conjoins, love affair with foreigner",
                "If Saturn aspects, children delayed and education disrupted",
                "If Mars conjoins, aggressive children and speculation fights",
            ],
            "financial": "Technology stocks and foreign market speculation. Cryptocurrency (extremely volatile). Foreign education investments. Children's unconventional education expenses. Avoid traditional speculation. Online trading platforms.",
            "health": "Stomach, reproductive, nervous. Mysterious stomach ailments. Reproductive complications. Nervous stomach from speculation stress. Children's unusual health issues.",
            "family": "Children are unconventional and possibly in foreign lands. Love affairs are unusual. First child may face challenges. Education path is non-traditional. Family creativity through technology.",
        },
        6: {
            "effect": "Powerful over enemies through manipulation. Foreign health treatments. Electronics service.",
            "good": "Enemy defeat, foreign medicine, technology service, legal wins through tricks.",
            "bad": "Chronic mysterious diseases, skin issues, maternal uncle suffers.",
            "remedy": "Keep barley in pocket. Donate coal. Feed dogs.",
            "age_triggers": ["Enemy defeat at 24", "Foreign medicine at 28", "Technology service at 30", "Skin issues at 33", "Mysterious disease at 36", "Health management after 42"],
            "conditions": [
                "If Mercury conjoins, technology in healthcare",
                "If Saturn conjoins, chronic diseases managed through foreign treatment",
                "If Jupiter aspects, healing through unconventional means",
                "If Mars conjoins, surgery through foreign techniques",
            ],
            "financial": "Healthcare technology business. Foreign medical services. Electronics repair and service. Debt recovery through clever means. Avoid traditional healthcare business. Medical tourism facilitation.",
            "health": "Immune system, skin, mysterious ailments. Mysterious diseases difficult to diagnose. Skin disorders from unknown causes. Immune system behaves unpredictably. Foreign medicine helps. Allergies to local environment.",
            "family": "Maternal uncle involved in foreign affairs or suffers. Servants from foreign background. Family health managed through unconventional means. Wife supports health management.",
        },
        7: {
            "effect": "Foreign or unconventional spouse. Sudden marriage. Partnership in technology/foreign trade.",
            "good": "Foreign spouse, technology business, sudden partnership gains.",
            "bad": "Marriage instability, spouse deception, partnership fraud, foreign disputes.",
            "remedy": "Keep silver with spouse. Donate barley on Saturday. Keep onion near bed.",
            "age_triggers": ["Sudden marriage at 24-27", "Foreign spouse connection at 25", "Partnership gains at 28", "Spouse deception at 30", "Business through partner at 33", "Marriage stabilizes at 40"],
            "conditions": [
                "If Venus conjoins, beautiful foreign spouse but instability",
                "If Saturn conjoins, delayed marriage to foreign person",
                "If Jupiter aspects from H1, marriage guided by wisdom despite foreignness",
                "If Mars afflicts, violent marriage disputes",
            ],
            "financial": "Technology partnership business. Import-export with foreign partner. Online business partnerships. Spouse brings foreign income. Avoid 50-50 partnerships. Keep financial control separate from partner.",
            "health": "Kidneys, reproductive, mysterious ailments. Kidney issues from foreign food. Reproductive complications. Mysterious partner-related health issues. Foreign STDs risk.",
            "family": "Spouse is foreign or from very different background. In-laws from abroad. Marriage is unconventional. Children have mixed cultural identity. Partnership defines family fortune.",
        },
        8: {
            "effect": "Sudden transformations. Hidden wealth from foreign sources. Occult fascination. Mysterious events.",
            "good": "Hidden wealth, occult power, sudden inheritance, foreign insurance.",
            "bad": "Mysterious diseases, accidents, sudden losses, black magic fears, mental health.",
            "remedy": "Keep barley in the house. Donate coal on Saturday. Keep silver items.",
            "age_triggers": ["Mysterious events from 22", "Sudden transformation at 25", "Hidden wealth at 28", "Occult interest at 30", "Accident risk at 33", "Mental health concern at 36", "Deep occult after 42"],
            "conditions": [
                "If Saturn conjoins, extremely long but mysterious life",
                "If Mars conjoins, severe accidents and surgery",
                "If Jupiter aspects, occult wisdom and spiritual transformation",
                "If Moon afflicts, severe mental health crisis and paranoia",
            ],
            "financial": "Hidden foreign wealth. Cryptocurrency and dark market finance (avoid illegal). Insurance from foreign sources. Sudden inheritance. Underground resources. Avoid visible investments. Hidden assets protection strategies.",
            "health": "Reproductive, chronic, mysterious, mental. Mysterious diseases. Reproductive organ complications. Chronic ailments with unknown causes. Mental health paranoia. Accidents from unknown sources.",
            "family": "Family has deep secrets. In-laws involved in mysterious activities. Spouse's family has hidden wealth. Children may have unusual births. Ancestral karma is heavy and foreign-origin.",
        },
        9: {
            "effect": "Rahu debilitated here in LK. Father may have foreign connections. Unconventional religion.",
            "good": "Foreign spiritual experiences, father abroad, unconventional guru.",
            "bad": "Father suffers, religious confusion, fake gurus, foreign failures.",
            "remedy": "Keep barley at home. Donate to father. Do not follow unverified gurus.",
            "age_triggers": ["Religious confusion at 22", "Father issues at 25", "Fake guru risk at 28", "Foreign failure at 30", "Spiritual clarity at 36", "Father reconciliation at 40", "True guru after 42"],
            "conditions": [
                "If Jupiter conjoins, eventually finds true spiritual path despite confusion",
                "If Sun conjoins, father in foreign government but suffers",
                "If Saturn aspects, severe spiritual dryness and father's hardship",
                "If Moon afflicts, emotional religious manipulation",
            ],
            "financial": "Foreign ventures fail initially. Father's money goes abroad. Avoid religious business investments. Fake spiritual schemes cause losses. Genuine spiritual work after 36 brings income. Pilgrimage tourism with caution.",
            "health": "Hips, liver, mental confusion. Hip pain during foreign travel. Liver affected by foreign diet. Mental confusion about health choices. Follow traditional medicine not fads.",
            "family": "Father has foreign connections but suffers. Family religion is confused. Wife helps with spiritual grounding. Children may reject family religion. Foreign religious influence causes family tension.",
        },
        10: {
            "effect": "Career in technology, foreign companies, politics. Sudden career changes. Government through manipulation.",
            "good": "Technology career, MNC jobs, political rise, foreign career, sudden promotions.",
            "bad": "Career scandals, sudden demotion, political downfall, using wrong means.",
            "remedy": "Keep silver. Donate barley. Do not take bribes.",
            "age_triggers": ["Technology career at 22", "MNC job at 25", "Sudden promotion at 28", "Political entry at 30", "Scandal risk at 33", "Career peak at 36", "Downfall risk at 40", "Stability at 45"],
            "conditions": [
                "If Saturn conjoins, slow but massive technology career",
                "If Sun conjoins, government technology department or diplomatic service",
                "If Jupiter aspects, ethical technology leadership",
                "If Mars conjoins, defense technology or aggressive business tactics",
            ],
            "financial": "Technology sector career. MNC salaries. Foreign company positions. Political funding. Sudden career gains and losses. Keep retirement savings separate from risky ventures. IT consulting.",
            "health": "Knees, nervous system, mental. Knee problems from career stress. Nervous exhaustion. Mental health from career uncertainty. Foreign work environment health issues.",
            "family": "Family gains through career but faces instability. Wife adjusts to career changes. Children in technology fields. Family reputation tied to volatile career. Father's career may have similar pattern.",
        },
        11: {
            "effect": "Sudden gains and windfalls. Technology friends. Foreign income. Wishes fulfilled suddenly.",
            "good": "Sudden wealth, lottery, technology income, foreign gains, powerful network.",
            "bad": "Sudden losses after gains, false friends, elder children in foreign land.",
            "remedy": "Keep silver ball. Donate barley on Wednesday. Feed birds.",
            "age_triggers": ["Technology network at 22", "Sudden gains at 25", "Windfall at 28", "Foreign income at 30", "False friends at 33", "Wishes fulfilled at 36", "Sudden loss risk at 40", "Net gains positive by 45"],
            "conditions": [
                "If Jupiter conjoins, ethical technology wealth and genuine friends",
                "If Saturn conjoins, delayed but massive technology gains",
                "If Mercury conjoins, IT business and digital marketing wealth",
                "If Mars conjoins, technology in defense sector gains",
            ],
            "financial": "Technology stocks and startups. Foreign income streams. Digital marketing and social media income. Lottery and windfall possible but unreliable. Network marketing. Cryptocurrency gains (hedge 50%). Electronic goods trading.",
            "health": "Calves, ankles, circulation. Leg issues from sedentary tech work. Circulation problems. Nerve compression from devices. Eye strain from screens.",
            "family": "Elder children settle abroad. Friends are in technology and foreign countries. Network is the family's greatest asset. Wife supports foreign connections. Wishes fulfilled through technology.",
        },
        12: {
            "effect": "Rahu's permanent house. Foreign settlement. Expenditure on foreign items. Spiritual confusion.",
            "good": "Foreign settlement, international career, expenditure brings returns, occult.",
            "bad": "Foreign losses, sleep disorders, mental confusion, spiritual manipulation.",
            "remedy": "Keep barley under pillow. Donate coal. Keep silver.",
            "age_triggers": ["Foreign travel at 22", "Settlement abroad at 25", "Expenditure rises at 28", "Sleep issues at 30", "Spiritual confusion at 33", "Occult depth at 36", "Settled foreign life at 42"],
            "conditions": [
                "If Saturn conjoins, long foreign stay with chronic health issues",
                "If Jupiter aspects, spiritual clarity in foreign land eventually",
                "If Moon afflicts, severe mental health crisis abroad",
                "If Venus conjoins, luxury abroad but spiritual emptiness",
            ],
            "financial": "Foreign currency earnings. International career income. Expenditure on foreign luxury. Hidden income from abroad. Occult healing practice. Avoid investments in homeland from abroad. Foreign real estate.",
            "health": "Feet, sleep, mental health, mysterious. Severe sleep disorders. Mental confusion and paranoia abroad. Foot problems. Mysterious foreign diseases. Spiritual practices help more than medicine.",
            "family": "Family left behind in homeland. Spouse adjusts to foreign life. Children grow up in foreign culture. Family visits are emotional. Spiritual confusion affects family dynamics.",
        },
    },

    # ----- KETU -----
    "Ketu": {
        1: {
            "effect": "Spiritual and detached personality. Mysterious aura. Health issues related to spine. Past life karma strong.",
            "good": "Spiritual depth, mystical ability, past life wisdom, liberation path.",
            "bad": "Health issues, spine/joint pain, confusion in identity, detachment from world.",
            "remedy": "Keep saffron. Donate blankets. Feed dogs with sweet bread.",
            "age_triggers": ["Spiritual awakening at 16", "Identity confusion at 22", "Health issues at 25", "Mystical abilities at 28", "Detachment at 30", "Spiritual depth at 36", "Liberation path after 42"],
            "conditions": [
                "If Jupiter aspects, spiritual master in the making",
                "If Sun conjoins, authority combined with detachment",
                "If Saturn conjoins, extremely austere and disciplined spiritual life",
                "If Moon conjoins, emotional spiritual crisis",
            ],
            "financial": "Income through spiritual work, healing, and alternative medicine. Avoid material business pursuits. Dog shelters and animal welfare. Saffron and herbal business. Donation-based income. Spiritual counseling.",
            "health": "Spine, joints, mysterious ailments. Spine issues are chronic. Joint pain without clear cause. Mysterious fevers. Skin marks or birthmarks. Past life health patterns repeat.",
            "family": "Family feels native is different. Detached from worldly family concerns. Father puzzled by spiritual nature. Wife accepts spiritual path. Children may be spiritual or detached.",
        },
        2: {
            "effect": "Speech issues or spiritual speech. Family karmic patterns. Hidden wealth. Eye problems possible.",
            "good": "Hidden family wealth, spiritual voice, past life family connections.",
            "bad": "Speech disorders, family karma, eye issues, secret family problems.",
            "remedy": "Donate saffron. Keep gold in ear. Feed dogs.",
            "age_triggers": ["Speech development issues in childhood", "Family karma surfaces at 22", "Hidden wealth at 25", "Eye problems at 28", "Spiritual speech at 30", "Family secrets at 33"],
            "conditions": [
                "If Jupiter conjoins, spiritual wealth and mantra power",
                "If Venus conjoins, hidden beauty and artistic family wealth",
                "If Saturn aspects, delayed but karmic family wealth",
                "If Rahu in H8, family has deep occult connections",
            ],
            "financial": "Hidden wealth sources. Spiritual teaching income. Mantra healing. Antique and heritage items. Gold ear ornaments bring luck. Avoid open business. Spiritual counseling fees.",
            "health": "Eyes, speech, throat. Eye problems including vision issues. Speech impediments or unusual voice. Throat infections. Right eye needs care. Vocal cord issues for speakers.",
            "family": "Family has karmic patterns repeating across generations. Hidden family wealth. Speech defines family fortune. Past life family connections. Children inherit spiritual speech.",
        },
        3: {
            "effect": "Ketu debilitated here in LK. Siblings may be detached. Spiritual writing. Pilgrimage travels.",
            "good": "Spiritual writing, pilgrimage, detached courage, occult communication.",
            "bad": "Sibling estrangement, ear/neck issues, communication gaps.",
            "remedy": "Donate saffron and blanket. Feed dogs. Keep gold in ear (ring).",
            "age_triggers": ["Sibling distance at 22", "Communication gaps at 25", "Spiritual writing at 28", "Ear issues at 30", "Pilgrimage at 33", "Occult communication at 36"],
            "conditions": [
                "If Mercury conjoins, confused but eventually spiritual writer",
                "If Mars conjoins, aggressive spiritual communication",
                "If Jupiter aspects, published spiritual author",
                "If Saturn aspects, delayed but deep spiritual writing",
            ],
            "financial": "Spiritual writing and publishing. Pilgrimage tour organizing. Occult bookshop. Herbal medicine courier. Avoid technology business. Neighborhood healing practice.",
            "health": "Ears, neck, arms, nervous. Ear infections and hearing issues. Neck stiffness. Arm numbness. Nervous system issues. Headphones should be avoided.",
            "family": "Siblings are spiritually inclined or distant. Younger brother may renounce worldly life. Neighbors seek spiritual guidance. Family communication through spiritual means.",
        },
        4: {
            "effect": "Detachment from home. Spiritual home setup. Mother may be very spiritual or absent.",
            "good": "Spiritual home, meditation room, detached peace, past life property.",
            "bad": "Mother detachment, domestic emptiness, heart issues, property disputes.",
            "remedy": "Keep saffron at home. Feed dogs. Donate blankets to poor.",
            "age_triggers": ["Mother distance at 22", "Spiritual home at 25", "Heart caution at 28", "Property dispute at 30", "Meditation room at 33", "Detached peace at 36", "Past life property at 42"],
            "conditions": [
                "If Moon conjoins, mother is absent or extremely spiritual",
                "If Saturn conjoins, cold and austere home life",
                "If Jupiter aspects, ashram-like home atmosphere",
                "If Mars conjoins, property disputes with spiritual dimension",
            ],
            "financial": "Property through past life karma or spiritual connections. Meditation and yoga center at home. Ashram property. Avoid commercial property. Spiritual retreat business. Herbal garden income.",
            "health": "Heart, chest, emotional. Heart issues from emotional detachment. Chest emptiness feeling. Emotional numbness. Meditation heals heart conditions. Dogs at home improve health.",
            "family": "Mother may be absent, deceased early, or extremely spiritual. Home feels empty despite possessions. Spouse accepts spiritual home. Children grow up in meditative environment.",
        },
        5: {
            "effect": "Spiritual children or issues with children. Past life karmic children. Occult education.",
            "good": "Spiritual children, occult study, past life wisdom, meditation gains.",
            "bad": "Children issues, miscarriage, detachment from children, stomach issues.",
            "remedy": "Feed dogs. Donate saffron. Keep gold. Serve Brahmins.",
            "age_triggers": ["Past life wisdom surfaces at 22", "Children issues at 25-28", "Occult study at 28", "Miscarriage risk at 30", "Spiritual children at 33", "Meditation gains at 36"],
            "conditions": [
                "If Jupiter aspects, spiritually gifted children",
                "If Saturn aspects, severe delays in children",
                "If Rahu afflicts from H11, children settle in foreign lands",
                "If Mars conjoins, aggressive spiritual education",
            ],
            "financial": "Spiritual education income. Past life knowledge monetization. Occult teaching. Yoga instructor income. Avoid gambling and speculation entirely. Spiritual retreat for children.",
            "health": "Stomach, reproductive, spine. Stomach disorders. Reproductive difficulties. Spine alignment issues. Children's mysterious health issues. Meditation heals digestive system.",
            "family": "Children are spiritual or face karmic challenges. First child has past life connection. Love life is karmic. Mother guides spiritual education. Grandchildren may be very evolved souls.",
        },
        6: {
            "effect": "Ketu's permanent house. Spiritual victory over enemies. Detached from disease. Service to animals.",
            "good": "Enemy defeat through karma, health through spirituality, animal service, surgery.",
            "bad": "Mysterious diseases, dog bites, urinary issues.",
            "remedy": "Feed dogs sweet bread. Donate saffron blanket. Keep brown/saffron dog.",
            "age_triggers": ["Animal connection at 22", "Enemy karmic defeat at 25", "Mysterious disease at 28", "Surgical ability at 30", "Dog bite risk at 33", "Spiritual health at 36", "Detachment from disease at 42"],
            "conditions": [
                "If Mars conjoins, powerful healer or surgeon",
                "If Saturn conjoins, chronic mysterious diseases",
                "If Jupiter aspects, ayurvedic or spiritual healing mastery",
                "If Mercury conjoins, veterinary or alternative medicine",
            ],
            "financial": "Animal shelter and veterinary income. Spiritual healing practice. Alternative medicine. Dog breeding and care. Herbal medicine business. Avoid lending money. Service to disabled brings karmic wealth.",
            "health": "Urinary system, mysterious diseases, dog-related. Urinary tract infections. Mysterious fevers and ailments. Dog bites or dog-related incidents. Stomach parasites. Spiritual healing is more effective than allopathic.",
            "family": "Dogs are part of family. Maternal uncle has karmic connection. Servants need spiritual management. Family health through alternative means. Children love animals.",
        },
        7: {
            "effect": "Spouse may be very spiritual or detached. Marriage brings karmic lessons. Late or unusual marriage.",
            "good": "Spiritual spouse, karmic marriage, partnership in spiritual work.",
            "bad": "Marriage detachment, spouse health, multiple marriages, partnership karma.",
            "remedy": "Keep saffron. Feed dogs. Donate blankets. Respect spouse's spiritual needs.",
            "age_triggers": ["Marriage delay till 27-30", "Karmic spouse at 28", "Spiritual partnership at 30", "Spouse health at 33", "Marriage lessons at 36", "Acceptance at 42"],
            "conditions": [
                "If Venus conjoins, beautiful but detached spouse",
                "If Saturn conjoins, very late marriage to spiritual person",
                "If Jupiter aspects from H1, wise spiritual marriage",
                "If Mars afflicts, karmic marital conflicts",
            ],
            "financial": "Spiritual partnership business. Yoga and meditation centers. Spouse brings karmic wealth. Herbal and spiritual product business. Avoid materialistic partnerships.",
            "health": "Kidneys, reproductive, mysterious. Kidney function needs spiritual remedies. Reproductive karmic issues. Mysterious health of spouse. Joint meditation improves health.",
            "family": "Spouse is spiritual, detached, or from unusual background. Marriage has past life connections. In-laws are spiritually inclined. Children born after spiritual remedies. Family karma resolved through marriage.",
        },
        8: {
            "effect": "Deep spiritual transformation. Past life occult powers. Mysterious health events. Long life.",
            "good": "Occult mastery, kundalini awakening, longevity, spiritual transformation.",
            "bad": "Mysterious diseases, accidents, surgery, black magic vulnerability.",
            "remedy": "Feed dogs. Keep saffron. Donate blankets on Tuesday. Keep gold.",
            "age_triggers": ["Past life memories at 22", "Occult awakening at 25", "Mysterious health at 28", "Kundalini activation at 30", "Surgery risk at 33", "Deep transformation at 36", "Mastery after 42"],
            "conditions": [
                "If Saturn conjoins, extremely long life with chronic spiritual transformation",
                "If Mars conjoins, surgery and blood-related spiritual healing",
                "If Jupiter aspects, highest spiritual transformation",
                "If Rahu in H2, complete axis of hidden spiritual wealth",
            ],
            "financial": "Occult and spiritual healing income. Past life regression therapy. Kundalini yoga teaching. Tantric healing (ethical). Inheritance from spiritual family. Hidden spiritual wealth. Avoid material investments.",
            "health": "Reproductive, chronic, mysterious, spiritual. Kundalini-related health experiences. Mysterious chronic conditions. Surgery with spiritual recovery. Reproductive karmic patterns. Very long life through spiritual practice.",
            "family": "Family has deep occult roots. Spouse's family has spiritual inheritance. Children inherit spiritual powers. Ancestral karma resolved through spiritual practice. In-laws have mysterious backgrounds.",
        },
        9: {
            "effect": "Ketu exalted here in LK. Maximum spiritual blessings. Past life guru connection. Moksha path.",
            "good": "Spiritual mastery, guru connection, moksha, pilgrimage, father spiritual.",
            "bad": "Detachment from worldly religion, father may be absent or very spiritual.",
            "remedy": "Feed dogs. Apply saffron tilak. Donate to spiritual causes.",
            "age_triggers": ["Guru connection at 16", "Moksha inclination at 22", "Pilgrimage at 25", "Spiritual mastery at 28", "Father's spiritual journey at 30", "Teaching begins at 33", "Full spiritual authority at 42"],
            "conditions": [
                "If Jupiter conjoins, highest spiritual attainment possible in this life",
                "If Sun conjoins, spiritual authority recognized by government",
                "If Saturn aspects, austere spiritual discipline",
                "If Rahu in H3, spiritual communication and writing",
            ],
            "financial": "Spiritual teaching and ashram income. Pilgrimage organization. Donation-based wealth. Temple trust management. Spiritual publishing. Father's spiritual wealth. Avoid commercial ventures entirely.",
            "health": "Hips, liver, spiritual. Generally excellent spiritual health. Liver strong through spiritual diet. Hip issues from meditation posture. Long and peaceful life through spiritual practice.",
            "family": "Father is spiritual or absent in worldly sense. Family has guru lineage. Wife accepts spiritual mission. Children on moksha path. Family legacy is spiritual, not material.",
        },
        10: {
            "effect": "Career in spiritual/occult/healing fields. Detachment from worldly ambition. Late career stability.",
            "good": "Spiritual career, healing profession, detached authority, past life career karma.",
            "bad": "Career confusion, lack of ambition, knee/joint issues, sudden career changes.",
            "remedy": "Feed dogs. Keep saffron. Donate blankets. Serve at temple.",
            "age_triggers": ["Career confusion at 22-28", "Healing interest at 25", "Detached authority at 30", "Spiritual career at 33", "Joint issues at 36", "Career stability at 42", "Spiritual authority at 48"],
            "conditions": [
                "If Saturn conjoins, very late but powerful spiritual career",
                "If Jupiter aspects, teaching and healing career",
                "If Sun conjoins, government recognition of spiritual work",
                "If Mars conjoins, martial arts or energy healing career",
            ],
            "financial": "Spiritual profession income. Temple or ashram management. Healing center. Alternative medicine practice. Dog shelter management. Career income stabilizes late. Avoid corporate career.",
            "health": "Knees, joints, bones, spiritual. Knee problems. Joint pain from meditation posture. Spiritual healing of chronic conditions. Career stress affects joints. Dogs near workspace improve health.",
            "family": "Family concerned about lack of worldly ambition. Wife supports healing career. Children respect spiritual authority. Father's career pattern may repeat spiritually. Family reputation in spiritual circles.",
        },
        11: {
            "effect": "Spiritual gains. Detachment from desires paradoxically fulfills them. Unusual friends.",
            "good": "Spiritual wealth, detachment brings gains, mystical friends, elder children spiritual.",
            "bad": "Material desires unfulfilled, friends deceive, elder children detached.",
            "remedy": "Feed dogs sweet bread. Keep saffron. Donate to spiritual causes.",
            "age_triggers": ["Unusual friends at 22", "Spiritual gains at 25", "Desires unfulfilled at 28", "Paradoxical fulfillment at 30", "Elder child spiritual at 33", "Detachment brings wealth at 36", "Spiritual network at 42"],
            "conditions": [
                "If Jupiter conjoins, massive spiritual wealth and genuine friends",
                "If Saturn aspects, delayed gains through spiritual discipline",
                "If Rahu in H5, children in foreign spiritual pursuits",
                "If Venus conjoins, spiritual love circle",
            ],
            "financial": "Spiritual community income. Donation-based wealth. Elder child in spiritual business. Mystical friends bring opportunities. Detachment from money paradoxically attracts it. Ashram networking.",
            "health": "Ankles, calves, circulation. Ankle pain from spiritual practices. Circulation through spiritual energy work. Elder child's health needs attention. Dogs improve circulation.",
            "family": "Elder child is spiritual or detached. Friends are unusual or mystical. Family gains through spiritual network. Wife supports spiritual socializing. Community becomes extended family.",
        },
        12: {
            "effect": "Excellent for moksha. Foreign spiritual journey. Expenditure on spirituality. Complete detachment.",
            "good": "Moksha path, foreign ashram, spiritual liberation, past life clearing.",
            "bad": "Total worldly loss, foot problems, sleep disturbances, isolation.",
            "remedy": "Feed dogs. Keep saffron at home. Donate blankets to poor.",
            "age_triggers": ["Spiritual journey at 22", "Foreign ashram at 25", "Worldly losses at 28", "Complete detachment at 30", "Past life clearing at 33", "Moksha path at 36", "Liberation after 42"],
            "conditions": [
                "If Jupiter aspects, highest moksha potential in this lifetime",
                "If Saturn conjoins, austere foreign spiritual life",
                "If Rahu in H6, spiritual healing of enemies and diseases",
                "If Moon afflicts, emotional spiritual crisis then liberation",
            ],
            "financial": "Expenditure on spiritual causes. Foreign ashram expenses. Donation-based living. No material wealth accumulation. Spiritual healing as only income. Past life karmic debts cleared through charity.",
            "health": "Feet, sleep, spiritual, liberation. Foot problems in spiritual travel. Sleep is deep meditation. Spiritual health is excellent. Physical body detaches. Dogs near bed improve sleep.",
            "family": "Family accepts spiritual path. Spouse may follow or separate. Children raised in ashram. Father's karma resolved. Family line may end or transform into spiritual lineage.",
        },
    },
}


# =================================================================
# 2. CONJUNCTION EFFECTS -- Major 2-planet combinations
# =================================================================

CONJUNCTION_EFFECTS = {
    ("Sun", "Moon"): {
        "effect": "Amavasya Yoga in LK. Mind and soul unite but ego overpowers emotions. Government connections with emotional intelligence. Person appears royal but internally conflicted. Mother and father may have differences.",
        "financial": "Government contracts with public-facing component. Gold and silver combined investments. Banking with government ties. Dairy business with government supply contracts.",
        "remedy": "Offer water to Sun at sunrise and milk to Shivling on Monday. Keep gold and silver together in worship place. Do not drink milk at night.",
    },
    ("Sun", "Saturn"): {
        "effect": "Bitter father-son relationship in LK. Government penalties and career blocks if in same house. Person works extremely hard but recognition comes late. Authority through discipline. Bones and eyes both suffer.",
        "financial": "Government iron and steel contracts. Career in government labor department. Heavy industry with government contracts. Income rises after 36 significantly. Avoid partnerships -- solo work only.",
        "remedy": "Offer water to Sun at sunrise. Donate mustard oil on Saturday. Keep iron and copper separate. Serve father and poor people equally.",
    },
    ("Sun", "Rahu"): {
        "effect": "Grahan Yoga on Sun -- eclipse of authority. Government position snatched suddenly. Father faces sudden downfall. Person has magnetic authority but unpredictable results. Foreign government connections.",
        "financial": "Government technology contracts. Foreign government income. Sudden financial rises and falls. Avoid government speculation. Keep 60% in safe assets. Electronics with government supplies.",
        "remedy": "Throw copper coins in flowing water. Donate barley and wheat together. Do not accept free gifts. Offer water to Sun strictly at sunrise.",
    },
    ("Sun", "Jupiter"): {
        "effect": "Raja Yoga in LK when together in good houses. Government with wisdom. High authority with dharmic guidance. Children succeed in government. Gold and saffron bring immense fortune.",
        "financial": "Government education and judiciary. Gold and saffron business with government backing. Temple trust with government recognition. Banking at highest level. Father's wealth multiplies.",
        "remedy": "Apply saffron tilak daily. Offer water to Sun. Keep gold and saffron together. Serve guru and father both.",
    },
    ("Sun", "Mars"): {
        "effect": "Extreme authority and aggression. Military or police leadership. Property through government. Blood runs hot -- anger is the weakness. Father and brother may have conflicts.",
        "financial": "Defense contracts. Government construction and engineering. Real estate with government backing. Iron and gold combined business. Property through courage and authority.",
        "remedy": "Offer water to Sun. Feed sweet chapati to dogs. Keep copper and red coral together. Donate blood on Tuesday and water to Sun on Sunday.",
    },
    ("Moon", "Mars"): {
        "effect": "Laxmi-Narayan Yoga in some LK texts when well-placed. Property and comfort combined. Mother suffers if in bad houses. Blood pressure and emotional aggression. Land near water is lucky.",
        "financial": "Dairy farming on own land. Water-related property. Hospitality with property. Construction near water bodies. Real estate and dairy combined. Silver and coral investments.",
        "remedy": "Keep silver and red coral together. Feed dogs sweet chapati. Offer milk at temple. Donate red items on Tuesday and white on Monday.",
    },
    ("Moon", "Rahu"): {
        "effect": "Grahan Yoga on Moon -- mental eclipse. Severe mental disturbance, anxiety, depression. Mother's health suffers drastically. Deceptive emotional patterns. Foreign mother or mother lives abroad.",
        "financial": "Foreign dairy or hospitality with extreme instability. Technology in water or food sector. Avoid speculation. Mental health expenses drain wealth. Foreign currency causes anxiety.",
        "remedy": "Keep silver and barley together under pillow. Offer milk mixed with barley at Shivling. Do not keep stagnant water. Serve mother as highest remedy.",
    },
    ("Moon", "Saturn"): {
        "effect": "Vish Yoga in LK (Poison combination). Mother suffers terribly. Depression and emotional coldness. Career in public service but with emotional burden. Chronic health from 22-36.",
        "financial": "Government welfare department. Iron dairy equipment. Slow wealth through public service. Chronic health expenses. Savings come after 36. Hotel or hospital management.",
        "remedy": "Do not drink milk at night. Keep iron and silver together. Donate mustard oil on Saturday and milk on Monday. Serve mother and old people.",
    },
    ("Moon", "Ketu"): {
        "effect": "Spiritual but emotionally disturbed. Mother may be very spiritual or absent. Past life emotional karma. Mystical intuition but worldly confusion. Insomnia and emotional detachment.",
        "financial": "Spiritual healing income. Dairy alternative products (herbal, almond). Ashram kitchen management. Avoid materialistic business. Dogs and dairy combined service.",
        "remedy": "Feed dogs with milk and sweet bread. Keep saffron and silver together. Offer milk to Shivling on Monday. Serve mother through spiritual service.",
    },
    ("Mars", "Saturn"): {
        "effect": "Angarak-Shani Yoga -- fire meets cold. Extreme hardship followed by extreme power. Property after immense struggle. Accidents and chronic bone issues. Brother suffers.",
        "financial": "Iron, steel, and heavy construction after 36. Mining and quarrying. Real estate through brutal struggle. Avoid business before 33. Heavy machinery. Government construction contracts.",
        "remedy": "Feed dogs and crows on Saturday and Tuesday. Keep iron items. Donate red and black items. Do not sell ancestral property. Serve brother and workers.",
    },
    ("Mars", "Rahu"): {
        "effect": "Angarak Yoga -- explosive combination. Sudden accidents, violence, and property disputes. Foreign property with danger. Technology in construction or defense. Brother in foreign land suffers.",
        "financial": "Defense technology. Foreign construction. Real estate technology platforms. Extremely volatile financial results. Fire or electrical accidents cause property loss. Keep insurance on everything.",
        "remedy": "Keep red coral and silver separate. Float coconut in river. Feed dogs on Tuesday and Saturday. Donate barley and red lentils together. Do not keep sharp weapons at home.",
    },
    ("Mars", "Jupiter"): {
        "effect": "Guru-Mangal Yoga -- courage with wisdom. Property through dharmic means. Children in defense or law. Religious warrior. Red coral and gold bring fortune.",
        "financial": "Legal profession with property expertise. Religious property trusts. Defense with judicial backing. Education in engineering. Gold and coral combined investments.",
        "remedy": "Apply saffron tilak. Feed sweet chapati to dogs. Keep gold and red coral together. Serve guru and brother. Donate to temples and military families.",
    },
    ("Jupiter", "Venus"): {
        "effect": "Guru-Shukra battle in LK -- wisdom vs pleasure. Marriage and finances both abundant but conflicted. Religious luxury. Children artistic but confused about dharma.",
        "financial": "Luxury education business. Religious art and jewelry. Temple decoration. Fashion with ethical sourcing. Gold and diamond combined investments. Beauty parlor chain with educational component.",
        "remedy": "Apply saffron tilak. Donate curd and saffron on Friday and Thursday. Keep gold and diamond separate in worship. Respect guru and spouse equally.",
    },
    ("Jupiter", "Saturn"): {
        "effect": "Dharma-Karma Yoga -- religion meets discipline. Massive success after prolonged struggle. Government education or judiciary. Children face delays but great eventual success.",
        "financial": "Government banking. Judicial investments. Educational institutions with discipline. Iron and gold combined business. Wealth comes after 36 but is permanent. Temple trust with government backing.",
        "remedy": "Apply saffron tilak. Donate mustard oil and saffron. Feed crows on Saturday and Brahmins on Thursday. Serve guru and old people.",
    },
    ("Jupiter", "Rahu"): {
        "effect": "Guru Chandal Yoga in LK -- wisdom corrupted. False guru tendencies. Foreign religion or philosophy. Children in foreign lands. Wealth through foreign education but religious confusion.",
        "financial": "Foreign education business. Technology in education. Online teaching platforms. Cryptocurrency in educational tokens. Avoid religious business. Foreign university partnerships.",
        "remedy": "Apply saffron tilak strictly. Donate barley and saffron together. Do not follow unverified gurus. Keep gold and silver separate. Feed birds and Brahmins on Thursday.",
    },
    ("Venus", "Saturn"): {
        "effect": "Luxury through discipline in LK. Late marriage to mature person. Beauty industry with hard work. Artistic career after 30. Marriage cold initially then warms.",
        "financial": "Fashion industry with disciplined management. Beauty in hardware -- bathroom fittings, tiles. Diamond and iron combined investments. Luxury car servicing. Slow luxury brand building.",
        "remedy": "Donate white items on Friday and black on Saturday. Keep diamond and iron separate. Respect spouse and workers. Feed crows on Saturday.",
    },
    ("Venus", "Rahu"): {
        "effect": "Foreign luxury and beauty. Unconventional love affairs. Foreign spouse in beauty or technology. Sudden marriage or sudden divorce. Material indulgence.",
        "financial": "Foreign luxury brand imports. Online beauty business. Technology in fashion. Social media beauty influencing. Foreign spouse brings foreign wealth. Electronics in beauty sector.",
        "remedy": "Donate white items and barley together. Keep diamond and silver separate. Respect all women. Do not accept beauty products as free gifts.",
    },
    ("Saturn", "Rahu"): {
        "effect": "Shani-Rahu combination -- karmic foreigner. Foreign hardship that builds character. Technology in heavy industry. Chronic mysterious diseases. Extremely delayed success in foreign land.",
        "financial": "Foreign heavy industry. Technology in mining or oil. Government technology contracts abroad. Extremely slow foreign wealth. Iron and electronics combined. Underground resource technology.",
        "remedy": "Donate mustard oil and barley together on Saturday. Keep iron and silver separate. Feed crows and dogs together. Serve the foreign poor and disabled.",
    },
    ("Mercury", "Venus"): {
        "effect": "Business and beauty combined. Sweet speech in business. Trade in luxury goods. Spouse is business partner. Fashion design and communication.",
        "financial": "Fashion retail business. Luxury goods trading. Beauty blogging and writing. Jewelry design and marketing. Green and white items combined trading. Communication in beauty industry.",
        "remedy": "Keep emerald and diamond together in worship. Donate green and white items on Wednesday and Friday. Respect spouse in business. Feed parrots and cows.",
    },
    ("Mercury", "Jupiter"): {
        "effect": "Saraswati Yoga possibility in LK -- intelligence with wisdom. Scholarly writing. Banking and education combined. Publishing religious texts. Children are brilliant scholars.",
        "financial": "Educational publishing. Banking advisory. Scholarly writing royalties. Religious text publishing. Gold and emerald investments. Educational banking products. Financial literacy business.",
        "remedy": "Apply saffron tilak. Keep emerald and gold together. Donate to educational institutions and temples. Feed parrots and cows on Thursday.",
    },
    ("Mercury", "Mars"): {
        "effect": "Technical intelligence. Engineering mind. Harsh but precise speech. Property through technical skills. Sibling partnerships in technical fields.",
        "financial": "Engineering consulting. Technical writing. Real estate technology. Construction management. IT in property. Hardware and software combined business. Technical training institutes.",
        "remedy": "Keep copper and red coral together. Feed dogs and parrots. Donate green and red items on Tuesday and Wednesday. Serve brother and students.",
    },
    ("Venus", "Ketu"): {
        "effect": "Spiritual beauty. Detachment in marriage. Past life love karma. Artistic spiritual expression. Wife may be very spiritual or marriage has karmic purpose.",
        "financial": "Spiritual art business. Yoga and beauty combined. Meditation retreat with luxury. Herbal beauty products. Dogs and beauty combined charity. Spiritual jewelry design.",
        "remedy": "Feed dogs with curd. Keep saffron and diamond together. Donate white items and blankets. Respect spiritual women and artists.",
    },
    ("Ketu", "Saturn"): {
        "effect": "Extreme austerity. Spiritual discipline. Past life karmic debts through hardship. Healing through suffering. Very late liberation from material bonds.",
        "financial": "Dog shelter and old age home. Spiritual labor services. Mining with spiritual purpose. Charitable organizations. Iron and saffron items. Avoid all material accumulation.",
        "remedy": "Feed dogs and crows together. Keep saffron and iron together. Donate black blankets and saffron. Serve old people and dogs. Keep Wednesday and Saturday fasts.",
    },
    ("Rahu", "Ketu"): {
        "effect": "Complete nodal axis in one house -- extremely rare and powerful. Past and future karma collide. Extreme spiritual or material results. Foreign spiritual journey. Dogs and technology combined.",
        "financial": "Technology in spiritual healing. Foreign spiritual business. Online spiritual platforms. Cryptocurrency in spiritual tokens. Extremely unpredictable financial results. Dog technology (GPS, health monitors).",
        "remedy": "Feed dogs with sweet bread daily. Keep silver and saffron together. Donate barley and blankets. Do not follow any extreme path. Balance material and spiritual strictly.",
    },
}


# =================================================================
# 3. PLANETARY DEBTS (RINS)
# =================================================================

DEBT_DEFINITIONS = {
    "pitru_rin": {
        "label": "Pitru Rin (Father's Debt)",
        "trigger_planets": ["Sun", "Jupiter"],
        "trigger_houses": [1, 2, 5, 9, 10],
        "description": "Debt towards father and ancestors. Triggered when Sun/Jupiter are afflicted in houses 1, 2, 5, 9, 10.",
        "symptoms": "Father's health issues, career obstacles, government penalties, sons face problems.",
        "remedy": "Offer water to Sun daily. Serve father and elders. Donate wheat and jaggery. Do not cut Peepal tree.",
    },
    "matru_rin": {
        "label": "Matru Rin (Mother's Debt)",
        "trigger_planets": ["Moon", "Venus"],
        "trigger_houses": [4, 6, 8, 12],
        "description": "Debt towards mother. Triggered when Moon/Venus are afflicted in houses 4, 6, 8, 12.",
        "symptoms": "Mother's suffering, domestic unrest, mental anxiety, property losses, heart/chest issues.",
        "remedy": "Serve mother. Donate milk, rice, and silver. Keep silver square piece. Offer milk at Shivling.",
    },
    "stri_rin": {
        "label": "Stri Rin (Wife's/Women's Debt)",
        "trigger_planets": ["Venus", "Moon"],
        "trigger_houses": [2, 4, 7, 12],
        "description": "Debt towards wife and women. Triggered when Venus is afflicted or debilitated.",
        "symptoms": "Marital discord, wife's health issues, lack of domestic peace, reproductive problems.",
        "remedy": "Respect all women. Donate white items on Friday. Keep diamond/opal. Donate to women's causes.",
    },
    "swa_rin": {
        "label": "Swa Rin (Self Debt)",
        "trigger_planets": ["Saturn", "Rahu"],
        "trigger_houses": [1, 6, 8, 10, 12],
        "description": "Self-inflicted karmic debt. When Saturn/Rahu afflict key houses.",
        "symptoms": "Chronic health issues, career blocks despite effort, loneliness, depression, karmic loops.",
        "remedy": "Feed crows and dogs. Donate mustard oil on Saturday. Keep iron. Serve the poor and disabled.",
    },
    "bhai_rin": {
        "label": "Bhai Rin (Brother's/Sibling's Debt)",
        "trigger_planets": ["Mars", "Mercury"],
        "trigger_houses": [3, 6, 11],
        "description": "Debt towards siblings. When Mars/Mercury are afflicted in sibling houses.",
        "symptoms": "Sibling estrangement, no help from brothers, loss through relatives, disputes.",
        "remedy": "Serve brothers. Donate red lentils. Feed sweet bread to dogs. Keep honey at home.",
    },
}


def _is_afflicted(planet_name: str, house: int, planet_house_map: Dict[str, int]) -> bool:
    """
    Check if a planet is afflicted in Laal Kitab terms:
    - Placed in debilitation house
    - Conjunct with enemies
    - In 6, 8, or 12
    """
    if LK_DEBILITATED.get(planet_name) == house:
        return True
    if house in (6, 8, 12):
        return True
    enemies = LK_ENEMIES.get(planet_name, [])
    for enemy in enemies:
        if planet_house_map.get(enemy) == house:
            return True
    return False


def analyze_debts(planet_house_map: Dict[str, int]) -> List[Dict]:
    """Analyze which planetary debts are active based on placements."""
    active_debts = []
    for debt_key, debt_info in DEBT_DEFINITIONS.items():
        is_active = False
        triggers_found = []
        for planet in debt_info["trigger_planets"]:
            house = planet_house_map.get(planet)
            if house and house in debt_info["trigger_houses"]:
                if _is_afflicted(planet, house, planet_house_map):
                    is_active = True
                    triggers_found.append(f"{planet} in H{house} (afflicted)")
        if is_active:
            active_debts.append({
                "debt": debt_key,
                "label": debt_info["label"],
                "active": True,
                "triggers": triggers_found,
                "description": debt_info["description"],
                "symptoms": debt_info["symptoms"],
                "remedy": debt_info["remedy"],
            })
    return active_debts


# =================================================================
# 4. SLEEPING / BLIND / AWAKE PLANETS
# =================================================================

def analyze_planet_state(planet_house_map: Dict[str, int]) -> List[Dict]:
    """
    Determine if each planet is Sleeping (Soya), Blind (Andha), or Awake (Jaagta).

    - Sleeping (Soya): Planet in a house where it has no strength and no
      friendly planet supports it. It gives delayed or no results.
    - Blind (Andha): Planet in enemy's house with no support from friends.
      It gives wrong/reversed results.
    - Awake (Jaagta): Planet in its own/exalted house or supported by
      friends. Gives full positive results.
    """
    states = []
    for planet, house in planet_house_map.items():
        friends = LK_FRIENDS.get(planet, [])
        enemies = LK_ENEMIES.get(planet, [])
        pakka = PAKKA_GHAR.get(planet, 0)
        exalted = LK_EXALTED.get(planet, 0)
        debilitated = LK_DEBILITATED.get(planet, 0)

        # Check for friends and enemies in same house
        friends_in_house = [f for f in friends if planet_house_map.get(f) == house]
        enemies_in_house = [e for e in enemies if planet_house_map.get(e) == house]

        # Check for friends and enemies aspecting (LK uses 7th aspect primarily)
        opp_house = ((house - 1 + 6) % 12) + 1  # 7th from current
        friends_aspecting = [f for f in friends if planet_house_map.get(f) == opp_house]
        enemies_aspecting = [e for e in enemies if planet_house_map.get(e) == opp_house]

        has_friend_support = len(friends_in_house) > 0 or len(friends_aspecting) > 0
        has_enemy_influence = len(enemies_in_house) > 0 or len(enemies_aspecting) > 0

        if house == pakka or house == exalted:
            state = "Jaagta (Awake)"
            state_desc = "Planet is in its own/exalted house. Gives full positive results."
            strength = "Strong"
        elif house == debilitated and not has_friend_support:
            state = "Andha (Blind)"
            state_desc = "Planet is debilitated without friend support. Gives wrong/reversed results."
            strength = "Very Weak"
        elif has_enemy_influence and not has_friend_support:
            state = "Andha (Blind)"
            state_desc = "Planet is under enemy influence without friend support. Results may be reversed."
            strength = "Weak"
        elif not has_friend_support and house not in (pakka, exalted):
            state = "Soya (Sleeping)"
            state_desc = "Planet has no friend support. Results are delayed or minimal."
            strength = "Dormant"
        elif has_friend_support:
            state = "Jaagta (Awake)"
            state_desc = "Planet has friend support. Gives positive results."
            strength = "Active"
        else:
            state = "Soya (Sleeping)"
            state_desc = "Planet gives delayed results."
            strength = "Dormant"

        states.append({
            "planet": planet,
            "house": house,
            "pakka_ghar": pakka,
            "state": state,
            "strength": strength,
            "description": state_desc,
            "friends_supporting": friends_in_house + friends_aspecting,
            "enemies_affecting": enemies_in_house + enemies_aspecting,
            "is_exalted": house == exalted,
            "is_debilitated": house == debilitated,
            "is_pakka_ghar": house == pakka,
        })

    return states


# =================================================================
# 5. LK YOGAS ANALYSIS
# =================================================================

def analyze_lk_yogas(planet_house_map: Dict[str, int]) -> Dict[str, List[Dict]]:
    """
    Detect Laal Kitab-specific yogas (combinations):
    - Dharmi planets: Planet in Pakka Ghar or exalted (very strong, dharmic results)
    - Kamini planets: Planet supported by Venus or in Venus-related houses (luxury/pleasure)
    - Tabet (Destroyed) planets: Debilitated + conjunct enemy + no friend support
    - Panauti: Saturn's influence on Moon (7th from or conjunct)
    - Grahan Yoga: Sun/Moon conjunct Rahu/Ketu (eclipse effects)
    - Mutual Exchange: Two planets in each other's Pakka Ghar
    - Kayam (Established) planets: In own Pakka Ghar and supported by friend
    """
    yogas: Dict[str, List[Dict]] = {
        "dharmi": [],
        "kamini": [],
        "tabet": [],
        "panauti": [],
        "grahan": [],
        "mutual_exchange": [],
        "kayam": [],
    }

    # --- Dharmi Planets ---
    for planet, house in planet_house_map.items():
        pakka = PAKKA_GHAR.get(planet, 0)
        exalted = LK_EXALTED.get(planet, 0)
        if house == pakka or house == exalted:
            yogas["dharmi"].append({
                "planet": planet,
                "house": house,
                "type": "Pakka Ghar" if house == pakka else "Exalted",
                "description": (
                    f"{planet} is Dharmi (righteous) in House {house}. "
                    f"It gives full positive results with dharmic foundation. "
                    f"The native benefits from {planet}'s significations in the most authentic LK manner. "
                    f"This planet acts as a pillar of the Teva."
                ),
                "effect": (
                    f"{planet} in its {'Pakka Ghar' if house == pakka else 'exaltation house'} "
                    f"bestows authority, respect, and dharmic results. "
                    f"Career, family, and spiritual matters related to {planet} flourish."
                ),
            })

    # --- Kamini Planets ---
    venus_house = planet_house_map.get("Venus")
    venus_related_houses = [7, 2, 12]  # Venus's Pakka Ghar, wealth, and exaltation
    for planet, house in planet_house_map.items():
        if planet == "Venus":
            continue
        is_kamini = False
        reason = ""
        if venus_house and venus_house == house:
            is_kamini = True
            reason = f"{planet} conjoins Venus in House {house}"
        elif house in venus_related_houses:
            is_kamini = True
            reason = f"{planet} in Venus-related House {house}"
        # Venus aspecting (7th from Venus)
        if venus_house:
            venus_opp = ((venus_house - 1 + 6) % 12) + 1
            if house == venus_opp:
                is_kamini = True
                reason = f"Venus aspects {planet} from House {venus_house}"
        if is_kamini:
            yogas["kamini"].append({
                "planet": planet,
                "house": house,
                "reason": reason,
                "description": (
                    f"{planet} has Kamini (pleasure/luxury) influence. {reason}. "
                    f"The native experiences comfort, luxury, and pleasure through "
                    f"{planet}'s significations. Material enjoyment is heightened but "
                    f"spiritual growth may be compromised."
                ),
                "effect": (
                    f"Luxury and comfort through {planet}. Marriage and partnership "
                    f"matters are influenced. Creative and artistic expression enhanced. "
                    f"Risk of over-indulgence and laziness."
                ),
            })

    # --- Tabet (Destroyed) Planets ---
    for planet, house in planet_house_map.items():
        debilitated = LK_DEBILITATED.get(planet, 0)
        if house != debilitated:
            continue
        enemies = LK_ENEMIES.get(planet, [])
        friends = LK_FRIENDS.get(planet, [])
        enemies_in_house = [e for e in enemies if planet_house_map.get(e) == house]
        friends_in_house = [f for f in friends if planet_house_map.get(f) == house]
        opp_house = ((house - 1 + 6) % 12) + 1
        friends_aspecting = [f for f in friends if planet_house_map.get(f) == opp_house]
        has_enemy = len(enemies_in_house) > 0
        has_friend = len(friends_in_house) > 0 or len(friends_aspecting) > 0
        if has_enemy and not has_friend:
            yogas["tabet"].append({
                "planet": planet,
                "house": house,
                "enemies": enemies_in_house,
                "description": (
                    f"{planet} is Tabet (destroyed) in House {house}. "
                    f"It is debilitated, conjunct enemy planet(s) {', '.join(enemies_in_house)}, "
                    f"and has no friend support. This planet gives extremely bad results. "
                    f"Its significations are essentially destroyed in this life."
                ),
                "effect": (
                    f"All matters related to {planet} suffer severely. "
                    f"Immediate and persistent remedies are essential. "
                    f"Without remedies, {planet}'s house and significations bring ruin."
                ),
                "urgency": "Critical",
                "remedy": PLANET_IN_HOUSE.get(planet, {}).get(house, {}).get("remedy", "Perform planet-specific remedies urgently."),
            })

    # --- Panauti (Saturn's affliction on Moon) ---
    moon_house = planet_house_map.get("Moon")
    saturn_house = planet_house_map.get("Saturn")
    if moon_house is not None and saturn_house is not None:
        moon_7th = ((moon_house - 1 + 6) % 12) + 1
        is_panauti = False
        reason = ""
        if saturn_house == moon_house:
            is_panauti = True
            reason = f"Saturn conjunct Moon in House {moon_house}"
        elif saturn_house == moon_7th:
            is_panauti = True
            reason = f"Saturn in House {saturn_house} aspects Moon in House {moon_house} (7th aspect)"
        if is_panauti:
            yogas["panauti"].append({
                "planet": "Moon",
                "afflicting": "Saturn",
                "moon_house": moon_house,
                "saturn_house": saturn_house,
                "reason": reason,
                "description": (
                    f"Panauti active: {reason}. This is one of the most dreaded combinations "
                    f"in Laal Kitab. Saturn's cold influence on Moon causes depression, "
                    f"mother's suffering, mental anxiety, and emotional numbness. "
                    f"Career faces obstacles and domestic life feels cold. "
                    f"This is also called Vish Yoga (Poison Yoga)."
                ),
                "effect": (
                    "Severe emotional disturbance. Mother's health deteriorates. "
                    "Depression and anxiety. Career feels stuck. Marriage becomes cold. "
                    "Financial stagnation. Mental health needs professional support."
                ),
                "remedy": (
                    "Do not drink milk at night. Keep iron and silver together. "
                    "Donate mustard oil on Saturday and milk on Monday. "
                    "Serve mother and old people. Offer milk to Shivling."
                ),
                "duration": "Active between ages 22-42 most intensely. Eases after 48.",
            })

    # --- Grahan Yoga (Eclipse) ---
    sun_house = planet_house_map.get("Sun")
    rahu_house = planet_house_map.get("Rahu")
    ketu_house = planet_house_map.get("Ketu")
    if sun_house is not None:
        if rahu_house == sun_house:
            yogas["grahan"].append({
                "luminaries": "Sun",
                "shadow": "Rahu",
                "house": sun_house,
                "description": (
                    f"Grahan Yoga: Sun eclipsed by Rahu in House {sun_house}. "
                    f"Authority and father are suddenly eclipsed. Government position snatched. "
                    f"Father faces mysterious downfall. Ego is inflated then destroyed. "
                    f"Foreign influence corrupts authority."
                ),
                "effect": "Sudden loss of authority, father's suffering, government penalties, mental confusion about identity.",
                "remedy": "Throw copper coins in flowing water. Donate barley and wheat together. Do not accept free gifts.",
            })
        if ketu_house == sun_house:
            yogas["grahan"].append({
                "luminaries": "Sun",
                "shadow": "Ketu",
                "house": sun_house,
                "description": (
                    f"Grahan Yoga: Sun eclipsed by Ketu in House {sun_house}. "
                    f"Authority dissolves into spirituality. Father may be absent or extremely spiritual. "
                    f"Career in government shifts to spiritual or healing work."
                ),
                "effect": "Detachment from authority, father's spiritual journey, career confusion then spiritual career.",
                "remedy": "Feed dogs with jaggery. Keep saffron and copper together. Offer water to Sun at sunrise strictly.",
            })
    if moon_house is not None:
        if rahu_house == moon_house:
            yogas["grahan"].append({
                "luminaries": "Moon",
                "shadow": "Rahu",
                "house": moon_house,
                "description": (
                    f"Grahan Yoga: Moon eclipsed by Rahu in House {moon_house}. "
                    f"This is the most dangerous Grahan in LK. Mind is completely eclipsed. "
                    f"Severe mental health issues -- anxiety, depression, paranoia. "
                    f"Mother suffers terribly. Deceptive emotional patterns."
                ),
                "effect": "Severe mental health crisis, mother's extreme suffering, emotional deception, insomnia, anxiety, depression.",
                "remedy": "Keep silver and barley under pillow. Offer milk mixed with barley at Shivling. Serve mother as highest priority. Professional mental health support essential.",
                "urgency": "Critical",
            })
        if ketu_house == moon_house:
            yogas["grahan"].append({
                "luminaries": "Moon",
                "shadow": "Ketu",
                "house": moon_house,
                "description": (
                    f"Grahan Yoga: Moon eclipsed by Ketu in House {moon_house}. "
                    f"Emotional detachment and spiritual confusion. Mother may be extremely "
                    f"spiritual or emotionally absent. Past life emotional karma surfaces."
                ),
                "effect": "Emotional numbness, mother's spiritual or physical absence, past life dreams, mystical experiences.",
                "remedy": "Feed dogs with milk and sweet bread. Keep saffron and silver together. Serve mother through spiritual service.",
            })

    # --- Mutual Exchange ---
    planets_list = list(planet_house_map.keys())
    for i in range(len(planets_list)):
        for j in range(i + 1, len(planets_list)):
            p1, p2 = planets_list[i], planets_list[j]
            h1, h2 = planet_house_map[p1], planet_house_map[p2]
            pakka1 = PAKKA_GHAR.get(p1, 0)
            pakka2 = PAKKA_GHAR.get(p2, 0)
            if h1 == pakka2 and h2 == pakka1:
                yogas["mutual_exchange"].append({
                    "planet_1": p1,
                    "planet_2": p2,
                    "house_1": h1,
                    "house_2": h2,
                    "description": (
                        f"Mutual Exchange: {p1} (in H{h1}, Pakka Ghar of {p2}) and "
                        f"{p2} (in H{h2}, Pakka Ghar of {p1}) exchange Pakka Ghar positions. "
                        f"Both planets exchange results -- {p1} gives results of {p2} and vice versa. "
                        f"This creates a unique LK combination where significations blend."
                    ),
                    "effect": (
                        f"{p1} and {p2} exchange their powers. Career, family, and health matters "
                        f"of both planets interchange. Remedies for one affect the other."
                    ),
                })

    # --- Kayam (Established) Planets ---
    for planet, house in planet_house_map.items():
        pakka = PAKKA_GHAR.get(planet, 0)
        if house != pakka:
            continue
        friends = LK_FRIENDS.get(planet, [])
        friends_in_house = [f for f in friends if planet_house_map.get(f) == house]
        opp_house = ((house - 1 + 6) % 12) + 1
        friends_aspecting = [f for f in friends if planet_house_map.get(f) == opp_house]
        if friends_in_house or friends_aspecting:
            supporters = friends_in_house + friends_aspecting
            yogas["kayam"].append({
                "planet": planet,
                "house": house,
                "supporters": supporters,
                "description": (
                    f"{planet} is Kayam (permanently established) in its Pakka Ghar House {house}, "
                    f"supported by friend(s) {', '.join(supporters)}. "
                    f"This planet's results are permanent, unwavering, and deeply beneficial. "
                    f"It acts as the strongest pillar of the Teva chart."
                ),
                "effect": (
                    f"{planet} gives its best results permanently throughout life. "
                    f"All significations of {planet} and House {house} flourish. "
                    f"This is one of the most auspicious conditions in Laal Kitab."
                ),
            })

    return yogas


# =================================================================
# 6. FINANCIAL ANALYSIS
# =================================================================

# Sector mapping for planets
PLANET_SECTORS = {
    "Sun": ["government", "gold", "wheat", "authority", "administrative services", "copper", "power sector"],
    "Moon": ["dairy", "water", "silver", "hospitality", "tourism", "nursing", "pearl", "rice"],
    "Mars": ["real estate", "construction", "iron", "steel", "defense", "surgery", "sports", "engineering"],
    "Mercury": ["IT", "trade", "communication", "publishing", "emerald", "green goods", "accounting", "education technology"],
    "Jupiter": ["banking", "education", "gold", "saffron", "religious institutions", "judiciary", "turmeric", "consulting"],
    "Venus": ["luxury", "fashion", "beauty", "diamond", "entertainment", "arts", "jewelry", "hospitality luxury"],
    "Saturn": ["iron", "oil", "labor", "heavy industry", "mining", "construction materials", "leather", "coal"],
    "Rahu": ["technology", "foreign trade", "electronics", "cryptocurrency", "social media", "telecommunications", "import-export"],
    "Ketu": ["spiritual healing", "alternative medicine", "herbal products", "dog-related services", "saffron", "occult services", "ashram"],
}


def analyze_financial_indicators(
    planet_house_map: Dict[str, int],
    predictions: List[Dict],
) -> Dict:
    """
    Comprehensive Laal Kitab financial analysis based on planet placements.
    Returns wealth houses analysis, property, business, debt risk,
    best periods for wealth, wealth/blocking planets, and investment advice.
    """
    result: Dict = {}

    # --- Wealth Houses ---
    h2_planets = [p for p, h in planet_house_map.items() if h == 2]
    h11_planets = [p for p, h in planet_house_map.items() if h == 11]
    h6_planets = [p for p, h in planet_house_map.items() if h == 6]

    wealth_houses = {
        "h2_family_wealth": {
            "planets": h2_planets,
            "analysis": _analyze_wealth_house(2, h2_planets, planet_house_map),
        },
        "h11_gains": {
            "planets": h11_planets,
            "analysis": _analyze_wealth_house(11, h11_planets, planet_house_map),
        },
        "h6_debts": {
            "planets": h6_planets,
            "analysis": _analyze_wealth_house(6, h6_planets, planet_house_map),
        },
    }
    result["wealth_houses"] = wealth_houses

    # --- Property Indicators ---
    h4_planets = [p for p, h in planet_house_map.items() if h == 4]
    mars_house = planet_house_map.get("Mars", 0)
    property_analysis = []
    if "Jupiter" in h4_planets:
        property_analysis.append("Jupiter in H4 (exalted in LK) -- massive property and real estate. Best property yoga in LK.")
    if "Moon" in h4_planets:
        property_analysis.append("Moon in Pakka Ghar H4 -- property near water, dairy farm land, peaceful home.")
    if "Venus" in h4_planets:
        property_analysis.append("Venus in H4 -- luxury property, beautiful home, premium location.")
    if "Saturn" in h4_planets:
        property_analysis.append("Saturn in H4 -- old/inherited property, delayed but permanent. Mines and industrial land.")
    if "Mars" in h4_planets:
        property_analysis.append("Mars debilitated in H4 -- property disputes. Do not buy before 28.")
    if "Rahu" in h4_planets:
        property_analysis.append("Rahu in H4 -- foreign property, electronic smart home, domestic disturbances.")
    if mars_house == 10:
        property_analysis.append("Mars exalted in H10 -- property through career and government allotment.")
    if not property_analysis:
        if mars_house:
            property_analysis.append(f"Mars in H{mars_house} -- property results through House {mars_house} significations.")
        else:
            property_analysis.append("No strong property indicators. Focus on career income rather than property.")
    result["property_indicators"] = property_analysis

    # --- Business Indicators ---
    h7_planets = [p for p, h in planet_house_map.items() if h == 7]
    h10_planets = [p for p, h in planet_house_map.items() if h == 10]
    business_analysis = []
    for p in h7_planets:
        sectors = PLANET_SECTORS.get(p, [])
        business_analysis.append(f"{p} in H7 -- partnership business in {', '.join(sectors[:3])}.")
    for p in h10_planets:
        sectors = PLANET_SECTORS.get(p, [])
        business_analysis.append(f"{p} in H10 -- career in {', '.join(sectors[:3])}.")
    if not business_analysis:
        business_analysis.append("No planets in H7 or H10. Business requires extra effort. Focus on service career.")
    result["business_indicators"] = business_analysis

    # --- Debt Risk ---
    h8_planets = [p for p, h in planet_house_map.items() if h == 8]
    h12_planets = [p for p, h in planet_house_map.items() if h == 12]
    debt_risk = []
    risk_level = "Low"
    afflicted_count = 0
    for p in h6_planets:
        if _is_afflicted(p, 6, planet_house_map):
            debt_risk.append(f"{p} afflicted in H6 -- chronic debt risk through {p}'s significations.")
            afflicted_count += 1
    for p in h8_planets:
        debt_risk.append(f"{p} in H8 -- hidden debts and sudden financial reversals through {p}.")
        afflicted_count += 1
    for p in h12_planets:
        debt_risk.append(f"{p} in H12 -- expenditure through {p}'s significations.")
        afflicted_count += 1
    if afflicted_count >= 3:
        risk_level = "High"
    elif afflicted_count >= 1:
        risk_level = "Medium"
    result["debt_risk"] = {"level": risk_level, "details": debt_risk}

    # --- Best Period for Wealth ---
    age_triggers_all = []
    for pred in predictions:
        planet = pred.get("planet", "")
        house = pred.get("house", 0)
        pdata = PLANET_IN_HOUSE.get(planet, {}).get(house, {})
        triggers = pdata.get("age_triggers", [])
        financial = pdata.get("financial", "")
        for t in triggers:
            t_lower = t.lower()
            if any(kw in t_lower for kw in ["wealth", "gain", "income", "property", "peak", "fortune", "prosperi"]):
                age_triggers_all.append({"planet": planet, "house": house, "trigger": t})
    result["best_period_for_wealth"] = age_triggers_all if age_triggers_all else [
        {"planet": "General", "house": 0, "trigger": "Focus on slow wealth building. Remedies for afflicted planets will unlock financial potential."}
    ]

    # --- Wealth Planets vs Blocking Planets ---
    wealth_planets = []
    blocking_planets = []
    for planet, house in planet_house_map.items():
        pakka = PAKKA_GHAR.get(planet, 0)
        exalted = LK_EXALTED.get(planet, 0)
        debilitated = LK_DEBILITATED.get(planet, 0)
        if house in (2, 11) or house == pakka or house == exalted:
            sectors = PLANET_SECTORS.get(planet, [])
            wealth_planets.append({
                "planet": planet,
                "house": house,
                "reason": "In wealth house" if house in (2, 11) else "In Pakka Ghar/Exalted",
                "sectors": sectors,
            })
        if house == debilitated or (house in (6, 8, 12) and _is_afflicted(planet, house, planet_house_map)):
            blocking_planets.append({
                "planet": planet,
                "house": house,
                "reason": "Debilitated" if house == debilitated else f"Afflicted in H{house}",
                "blocked_sectors": PLANET_SECTORS.get(planet, []),
            })
    result["wealth_planets"] = wealth_planets
    result["blocking_planets"] = blocking_planets

    # --- Investment Advice ---
    strong_sectors = set()
    avoid_sectors = set()
    for wp in wealth_planets:
        strong_sectors.update(wp.get("sectors", []))
    for bp in blocking_planets:
        avoid_sectors.update(bp.get("blocked_sectors", []))
    # Remove overlaps -- strong wins
    avoid_sectors -= strong_sectors
    result["investment_advice"] = {
        "invest_in": sorted(strong_sectors) if strong_sectors else ["Conservative fixed deposits and government bonds"],
        "avoid": sorted(avoid_sectors) if avoid_sectors else ["No specific sectors to avoid based on current placements"],
        "general": (
            "In Laal Kitab, the strongest financial gains come from sectors ruled by "
            "planets in Pakka Ghar, exalted houses, or wealth houses (H2, H11). "
            "Always avoid sectors ruled by debilitated or afflicted planets. "
            "Charity and remedies unlock blocked financial potential."
        ),
    }

    return result


def _analyze_wealth_house(house: int, planets: List[str], planet_house_map: Dict[str, int]) -> str:
    """Helper to analyze a wealth-related house."""
    if not planets:
        if house == 2:
            return "H2 is empty. Family wealth depends on Jupiter's and Moon's placement elsewhere. Focus on speech and savings discipline."
        elif house == 11:
            return "H11 is empty. Gains come through extra effort. Build strong networks and friendships for income growth."
        elif house == 6:
            return "H6 is empty. Generally favorable -- no strong debt indicators. Enemies are manageable."
    analyses = []
    for p in planets:
        is_aff = _is_afflicted(p, house, planet_house_map)
        if house == 2:
            if is_aff:
                analyses.append(f"{p} in H2 (afflicted) -- family wealth faces obstacles through {p}'s negative influence.")
            else:
                analyses.append(f"{p} in H2 -- family wealth grows through {p}'s significations: {', '.join(PLANET_SECTORS.get(p, [])[:3])}.")
        elif house == 11:
            if is_aff:
                analyses.append(f"{p} in H11 (afflicted) -- gains are delayed or through wrong means. Remedies needed for {p}.")
            else:
                analyses.append(f"{p} in H11 -- gains through {p}'s sectors: {', '.join(PLANET_SECTORS.get(p, [])[:3])}.")
        elif house == 6:
            if is_aff:
                analyses.append(f"{p} in H6 (afflicted) -- debt through {p}'s significations. Chronic financial drain.")
            else:
                analyses.append(f"{p} in H6 -- competitive advantage in {', '.join(PLANET_SECTORS.get(p, [])[:3])}. Enemies defeated.")
    return " ".join(analyses)


# =================================================================
# 7. LUCK ACTIVATION BY ASCENDANT
# =================================================================

LK_ASCENDANT_GUIDE = {
    "Aries": {
        "lucky_planets": ["Sun", "Mars", "Jupiter"],
        "dangerous_planets": ["Saturn", "Rahu", "Venus"],
        "activation_remedies": [
            "Offer water to Sun at sunrise daily",
            "Keep red coral and copper on your person",
            "Feed jaggery to monkeys on Tuesdays",
            "Wear saffron tilak on forehead",
        ],
        "lucky_colors": ["Red", "Orange", "Saffron", "Copper"],
        "lucky_numbers": [1, 3, 9],
        "lucky_days": ["Sunday", "Tuesday", "Thursday"],
        "lucky_metals": ["Copper", "Gold"],
        "lucky_stones": ["Red Coral", "Ruby"],
        "career_directions": [
            "Government administration and leadership",
            "Military, police, and defense services",
            "Engineering and construction",
            "Sports and competitive fields",
            "Surgery and emergency medicine",
        ],
        "wealth_activation": "Wealth comes through authority and courage. Keep copper items in the east. Offer water to Sun before any financial decision. Red coral activates Mars for property. Gold investments are most auspicious.",
        "relationship_tips": "Marry after 24. Partner should be gentle to balance fire energy. Respect spouse to activate Venus. Avoid domination in relationships. Love strengthens through generosity.",
        "health_watch": "Head, blood pressure, eyes. Anger management is crucial. Blood donation on Tuesdays. Morning exercise before sunrise. Avoid excessive heat exposure.",
    },
    "Taurus": {
        "lucky_planets": ["Venus", "Mercury", "Saturn"],
        "dangerous_planets": ["Sun", "Mars", "Rahu"],
        "activation_remedies": [
            "Donate white items on Fridays",
            "Keep silver coin in wallet",
            "Wear diamond or opal after expert guidance",
            "Respect all women in your life",
        ],
        "lucky_colors": ["White", "Cream", "Green", "Silver"],
        "lucky_numbers": [2, 6, 7],
        "lucky_days": ["Friday", "Wednesday", "Saturday"],
        "lucky_metals": ["Silver", "Platinum"],
        "lucky_stones": ["Diamond", "Emerald"],
        "career_directions": [
            "Banking and financial services",
            "Fashion, beauty, and luxury goods",
            "Agriculture and dairy farming",
            "Jewelry and gem trading",
            "Hotel and hospitality management",
        ],
        "wealth_activation": "Wealth comes through beauty, luxury, and patient accumulation. Silver in the north-east. Dairy and farm investments. Venus activation through respecting women. Diamond brings luxury wealth.",
        "relationship_tips": "Marriage is central to life prosperity. Choose a beautiful and cultured partner. Home aesthetics matter. Physical comfort in relationship is important. Loyalty attracts wealth.",
        "health_watch": "Throat, neck, face, diabetes. Sweet tooth needs control. Thyroid function monitoring. Neck exercises daily. Skin care routine essential.",
    },
    "Gemini": {
        "lucky_planets": ["Mercury", "Venus", "Rahu"],
        "dangerous_planets": ["Jupiter", "Moon", "Ketu"],
        "activation_remedies": [
            "Feed parrots or keep green parrot picture",
            "Wear copper ring on little finger",
            "Donate green items on Wednesdays",
            "Keep nose clean as LK remedy",
        ],
        "lucky_colors": ["Green", "Parrot Green", "Grey", "Mixed Colors"],
        "lucky_numbers": [3, 5, 6],
        "lucky_days": ["Wednesday", "Friday", "Saturday"],
        "lucky_metals": ["Copper", "Brass"],
        "lucky_stones": ["Emerald", "Green Tourmaline"],
        "career_directions": [
            "IT and software development",
            "Journalism and media",
            "Trading and commerce",
            "Publishing and writing",
            "Telecommunications and networking",
        ],
        "wealth_activation": "Wealth through intelligence and communication. Multiple income streams are natural. Technology investments thrive. Publishing and media income. Network is your net worth. Green emerald activates business luck.",
        "relationship_tips": "Intellectual compatibility matters most. Avoid too many relationships. Communication is the key to marriage success. Partner should be adaptable. Keep conversations interesting.",
        "health_watch": "Nervous system, skin, lungs, hands. Anxiety management essential. Skin allergies common. Breathing exercises daily. Wrist and hand care for writers and tech workers.",
    },
    "Cancer": {
        "lucky_planets": ["Moon", "Jupiter", "Mars"],
        "dangerous_planets": ["Saturn", "Rahu", "Mercury"],
        "activation_remedies": [
            "Offer milk to Shivling on Mondays",
            "Keep silver items at home",
            "Install water source or fountain at home",
            "Serve mother as highest dharma",
        ],
        "lucky_colors": ["White", "Silver", "Light Blue", "Cream"],
        "lucky_numbers": [2, 4, 7],
        "lucky_days": ["Monday", "Thursday", "Tuesday"],
        "lucky_metals": ["Silver", "White Gold"],
        "lucky_stones": ["Pearl", "Moonstone"],
        "career_directions": [
            "Hospitality and tourism",
            "Dairy and water-related industries",
            "Nursing and caregiving",
            "Real estate near water bodies",
            "Food and restaurant business",
        ],
        "wealth_activation": "Wealth through mother's blessings and water elements. Silver in the north. Pearl brings emotional stability and wealth. Property near water appreciates. Dairy business thrives. Mother's blessings are the greatest wealth activator.",
        "relationship_tips": "Emotional bonding is essential. Home is the center of relationship. Cook together to strengthen bonds. Mother's approval of partner matters. Nurturing nature attracts love.",
        "health_watch": "Chest, stomach, breast, emotions. Emotional eating control needed. Stomach acidity management. Breast health monitoring. Water intake must be pure and adequate.",
    },
    "Leo": {
        "lucky_planets": ["Sun", "Mars", "Jupiter"],
        "dangerous_planets": ["Saturn", "Venus", "Rahu"],
        "activation_remedies": [
            "Offer water to Sun at sunrise",
            "Keep solid gold piece on person",
            "Apply saffron tilak on forehead",
            "Feed jaggery to cows on Sundays",
        ],
        "lucky_colors": ["Gold", "Orange", "Red", "Royal Blue"],
        "lucky_numbers": [1, 5, 9],
        "lucky_days": ["Sunday", "Tuesday", "Thursday"],
        "lucky_metals": ["Gold", "Copper"],
        "lucky_stones": ["Ruby", "Red Coral"],
        "career_directions": [
            "Government and administrative services",
            "Politics and leadership",
            "Gold and jewelry business",
            "Entertainment and performing arts",
            "Hospital and healthcare administration",
        ],
        "wealth_activation": "Wealth through authority and leadership. Gold investments are most favorable. Government connections bring fortune. Sun worship activates all wealth channels. Avoid oil and iron business. Royal treatment of others brings returns.",
        "relationship_tips": "Partner should respect native's authority. Marriage brings status. Avoid ego in love. Generosity in relationship is key. Royal treatment of spouse activates Venus.",
        "health_watch": "Heart, spine, eyes, blood pressure. Heart health is priority. Regular eye checkups. Spine care through yoga. Blood pressure management after 40.",
    },
    "Virgo": {
        "lucky_planets": ["Mercury", "Venus", "Saturn"],
        "dangerous_planets": ["Mars", "Jupiter", "Moon"],
        "activation_remedies": [
            "Keep green plants at home and office",
            "Wear copper ring",
            "Donate to orphanages on Wednesdays",
            "Keep emerald or green stone after expert advice",
        ],
        "lucky_colors": ["Green", "Olive", "Earth tones", "Grey"],
        "lucky_numbers": [5, 6, 8],
        "lucky_days": ["Wednesday", "Friday", "Saturday"],
        "lucky_metals": ["Copper", "Silver"],
        "lucky_stones": ["Emerald", "Peridot"],
        "career_directions": [
            "Healthcare and medicine",
            "Accounting and auditing",
            "IT and data analysis",
            "Quality control and inspection",
            "Herbal and natural products",
        ],
        "wealth_activation": "Wealth through analytical skills and service. Health sector investments. Green products and organic business. Detailed financial planning brings results. Mercury activation through education and commerce. Emerald opens business luck.",
        "relationship_tips": "Intellectual and health-conscious partner ideal. Avoid over-criticism in relationships. Service to partner strengthens bond. Cleanliness in relationship matters. Practical love over romantic gestures.",
        "health_watch": "Intestines, nervous system, skin, digestion. Digestive health is foundational. Nervous exhaustion management. Skin care routine. Diet control essential. Regular health screenings.",
    },
    "Libra": {
        "lucky_planets": ["Venus", "Saturn", "Mercury"],
        "dangerous_planets": ["Sun", "Mars", "Jupiter"],
        "activation_remedies": [
            "Donate white sweets on Fridays",
            "Keep diamond or opal after expert guidance",
            "Maintain balance in all life areas",
            "Respect spouse above all else",
        ],
        "lucky_colors": ["White", "Pastel shades", "Light Blue", "Pink"],
        "lucky_numbers": [6, 7, 8],
        "lucky_days": ["Friday", "Saturday", "Wednesday"],
        "lucky_metals": ["Silver", "Platinum", "White Gold"],
        "lucky_stones": ["Diamond", "Opal", "White Sapphire"],
        "career_directions": [
            "Law and judiciary",
            "Fashion design and beauty",
            "Diplomacy and public relations",
            "Partnership business",
            "Art galleries and cultural events",
        ],
        "wealth_activation": "Wealth through partnerships and beauty. Marriage is the wealth activator. Diamond attracts luxury wealth. Partnership business flourishes. Art and beauty investments. Balance in finance is key -- never go extreme.",
        "relationship_tips": "Marriage is life's foundation. Beautiful partner brings prosperity. Equal partnership in love. Avoid dominance or submission. Joint decisions strengthen bonds.",
        "health_watch": "Kidneys, lower back, reproductive. Kidney function monitoring essential. Lower back care through exercise. Skin beauty maintenance. Sugar and salt balance in diet.",
    },
    "Scorpio": {
        "lucky_planets": ["Mars", "Moon", "Jupiter"],
        "dangerous_planets": ["Mercury", "Venus", "Rahu"],
        "activation_remedies": [
            "Keep red coral on person",
            "Feed sweet chapati to dogs on Tuesdays",
            "Float sindoor in flowing river",
            "Practice intense meditation",
        ],
        "lucky_colors": ["Red", "Maroon", "Dark Crimson", "Black-Red"],
        "lucky_numbers": [3, 9, 2],
        "lucky_days": ["Tuesday", "Monday", "Thursday"],
        "lucky_metals": ["Copper", "Iron (for Saturn management)"],
        "lucky_stones": ["Red Coral", "Bloodstone"],
        "career_directions": [
            "Surgery and emergency medicine",
            "Investigation and research",
            "Mining and underground resources",
            "Insurance and inheritance management",
            "Occult sciences and psychology",
        ],
        "wealth_activation": "Wealth through transformation and hidden resources. Insurance and inheritance sectors. Mining investments. Red coral activates Mars for property. Property in own name only. Avoid visible speculation -- hidden investments better.",
        "relationship_tips": "Deep emotional bonding essential. Trust is non-negotiable. Intensity in love -- all or nothing. Transformation through relationship. Forgiveness strengthens bonds more than revenge.",
        "health_watch": "Reproductive organs, piles, accidents, blood. Surgery risk management. Blood health monitoring. Piles prevention through diet. Accident-prone -- take precautions. Reproductive health checkups regular.",
    },
    "Sagittarius": {
        "lucky_planets": ["Jupiter", "Sun", "Mars"],
        "dangerous_planets": ["Mercury", "Venus", "Rahu"],
        "activation_remedies": [
            "Apply saffron tilak on forehead daily",
            "Keep gold in the house",
            "Serve guru and father",
            "Donate saffron at temple on Thursdays",
        ],
        "lucky_colors": ["Yellow", "Saffron", "Gold", "Orange"],
        "lucky_numbers": [3, 9, 1],
        "lucky_days": ["Thursday", "Sunday", "Tuesday"],
        "lucky_metals": ["Gold", "Brass"],
        "lucky_stones": ["Yellow Sapphire", "Topaz"],
        "career_directions": [
            "Education and teaching",
            "Law and judiciary",
            "Banking and finance",
            "Religious and spiritual leadership",
            "Publishing and philosophy",
        ],
        "wealth_activation": "Wealth through wisdom, education, and dharma. Gold investments are supreme. Yellow sapphire activates Jupiter for fortune. Banking career brings wealth. Temple donations return manifold. Father's blessings are the wealth key.",
        "relationship_tips": "Religious and wise partner ideal. Marriage with educated person. Travel together strengthens bonds. Freedom in relationship important. Philosophical compatibility matters.",
        "health_watch": "Liver, hips, thighs, diabetes. Liver function is critical -- turmeric daily. Hip joint care. Diabetes risk after 40. Thigh muscle maintenance. Pilgrimage walking is therapeutic.",
    },
    "Capricorn": {
        "lucky_planets": ["Saturn", "Venus", "Mercury"],
        "dangerous_planets": ["Mars", "Moon", "Jupiter"],
        "activation_remedies": [
            "Donate mustard oil on Saturdays",
            "Feed crows regularly",
            "Keep iron items in the house",
            "Serve workers and the underprivileged",
        ],
        "lucky_colors": ["Black", "Dark Blue", "Navy", "Grey"],
        "lucky_numbers": [8, 6, 5],
        "lucky_days": ["Saturday", "Friday", "Wednesday"],
        "lucky_metals": ["Iron", "Steel"],
        "lucky_stones": ["Blue Sapphire (with extreme caution)", "Amethyst"],
        "career_directions": [
            "Government administration (senior levels)",
            "Iron, steel, and heavy industry",
            "Mining and natural resources",
            "Real estate development",
            "Judiciary and law enforcement",
        ],
        "wealth_activation": "Wealth comes late but permanently. Iron and steel investments. Real estate after 36. Government career brings pension wealth. Saturn worship through service to poor. Patience is the wealth mantra. Oil sector investments.",
        "relationship_tips": "Marriage after 28 for best results. Mature and patient partner ideal. Relationship deepens with time. Avoid cold behavior -- show warmth. Discipline in love, not rigidity.",
        "health_watch": "Bones, joints, knees, chronic diseases. Calcium and Vitamin D essential. Knee protection crucial. Joint care from young age. Chronic condition management. Cold weather precautions.",
    },
    "Aquarius": {
        "lucky_planets": ["Saturn", "Rahu", "Mercury"],
        "dangerous_planets": ["Sun", "Moon", "Mars"],
        "activation_remedies": [
            "Keep iron and silver in the house",
            "Donate barley and mustard oil",
            "Feed crows and dogs",
            "Work with technology for dharmic purposes",
        ],
        "lucky_colors": ["Dark Blue", "Electric Blue", "Black", "Multi-colored"],
        "lucky_numbers": [4, 8, 7],
        "lucky_days": ["Saturday", "Wednesday", "Friday"],
        "lucky_metals": ["Iron", "Mixed metals"],
        "lucky_stones": ["Blue Sapphire (with caution)", "Gomed"],
        "career_directions": [
            "Technology and software",
            "Social welfare and NGOs",
            "Telecommunications",
            "Foreign companies and MNCs",
            "Innovation and startups",
        ],
        "wealth_activation": "Wealth through technology and foreign connections. Startup investments. Cryptocurrency with caution. Social media income. Foreign MNC careers. Iron and technology combined businesses. Innovation is the wealth key.",
        "relationship_tips": "Unconventional partner accepted. Freedom in relationship essential. Technology connects relationships. Community involvement strengthens bonds. Avoid possessiveness completely.",
        "health_watch": "Calves, ankles, circulation, nervous system. Leg care essential. Circulatory health monitoring. Screen time management for nerves. Ankle support during exercise. Cold extremities treatment.",
    },
    "Pisces": {
        "lucky_planets": ["Jupiter", "Moon", "Ketu"],
        "dangerous_planets": ["Mercury", "Venus", "Sun"],
        "activation_remedies": [
            "Apply saffron tilak daily",
            "Offer milk at Shivling on Mondays",
            "Feed dogs with sweet bread",
            "Keep gold and saffron at home",
        ],
        "lucky_colors": ["Yellow", "Saffron", "Sea Green", "White"],
        "lucky_numbers": [3, 7, 9],
        "lucky_days": ["Thursday", "Monday", "Tuesday"],
        "lucky_metals": ["Gold", "Silver"],
        "lucky_stones": ["Yellow Sapphire", "Pearl", "Cat's Eye"],
        "career_directions": [
            "Spiritual healing and counseling",
            "Hospital and healthcare",
            "Art and music",
            "Foreign services",
            "Charity and NGO work",
        ],
        "wealth_activation": "Wealth through spirituality and healing. Hospital or ashram management. Gold and saffron investments. Pearl brings emotional balance for financial decisions. Foreign spiritual work. Charity unlocks hidden wealth. Dog shelters bring karmic returns.",
        "relationship_tips": "Spiritual partner brings peace. Marriage has karmic dimensions. Emotional depth in love. Dreams guide relationship decisions. Compassion is the foundation of lasting love.",
        "health_watch": "Feet, immune system, sleep, mental health. Foot care essential -- especially for spiritual practitioners. Immune system support through diet. Sleep hygiene crucial. Mental health through meditation. Lymphatic drainage important.",
    },
}


def analyze_luck_activation(asc_sign: str, planet_house_map: Dict[str, int]) -> Dict:
    """
    Ascendant-specific luck activation based on Laal Kitab principles.
    Returns comprehensive guidance for the given ascendant sign.
    """
    guide = LK_ASCENDANT_GUIDE.get(asc_sign, LK_ASCENDANT_GUIDE.get("Aries"))
    if guide is None:
        guide = list(LK_ASCENDANT_GUIDE.values())[0]

    # Personalize based on actual planet positions
    lucky_active = []
    lucky_dormant = []
    for p in guide.get("lucky_planets", []):
        h = planet_house_map.get(p)
        if h is not None:
            pakka = PAKKA_GHAR.get(p, 0)
            exalted = LK_EXALTED.get(p, 0)
            debilitated = LK_DEBILITATED.get(p, 0)
            if h == pakka or h == exalted:
                lucky_active.append({
                    "planet": p,
                    "house": h,
                    "status": "Strongly Active",
                    "note": f"{p} is in its {'Pakka Ghar' if h == pakka else 'exaltation'} -- luck flows naturally through {p}.",
                })
            elif h == debilitated or _is_afflicted(p, h, planet_house_map):
                lucky_dormant.append({
                    "planet": p,
                    "house": h,
                    "status": "Blocked -- needs remedies",
                    "note": f"{p} is {'debilitated' if h == debilitated else 'afflicted'} in H{h}. Luck through {p} is blocked. Perform {p}-specific remedies immediately.",
                })
            else:
                lucky_active.append({
                    "planet": p,
                    "house": h,
                    "status": "Active",
                    "note": f"{p} in H{h} is reasonably placed. Luck flows with some effort.",
                })

    danger_status = []
    for p in guide.get("dangerous_planets", []):
        h = planet_house_map.get(p)
        if h is not None:
            pakka = PAKKA_GHAR.get(p, 0)
            exalted = LK_EXALTED.get(p, 0)
            if h == pakka or h == exalted:
                danger_status.append({
                    "planet": p,
                    "house": h,
                    "status": "Dangerous but strong -- gives mixed results",
                    "note": f"{p} is strong in H{h} but dangerous for {asc_sign} ascendant. Results come with complications.",
                })
            elif _is_afflicted(p, h, planet_house_map):
                danger_status.append({
                    "planet": p,
                    "house": h,
                    "status": "Actively Harmful",
                    "note": f"{p} afflicted in H{h} is actively causing problems for {asc_sign} native. Urgent remedies needed.",
                })

    return {
        "ascendant": asc_sign,
        "guide": guide,
        "lucky_planets_status": lucky_active,
        "lucky_planets_blocked": lucky_dormant,
        "dangerous_planets_status": danger_status,
        "personalized_activation": (
            f"For {asc_sign} ascendant, activate {', '.join(guide.get('lucky_planets', []))} "
            f"through the prescribed remedies. Colors {', '.join(guide.get('lucky_colors', [])[:2])} "
            f"and metals {', '.join(guide.get('lucky_metals', []))} should be worn/kept. "
            f"Career focus on {guide.get('career_directions', ['general service'])[0]} "
            f"will yield best results."
        ),
    }


# =================================================================
# 8. FULL LAAL KITAB ANALYSIS (Main Entry Point)
# =================================================================

def calculate_laal_kitab_analysis(
    planets: List[Dict],
    ascendant: Dict,
) -> Dict:
    """
    Complete Laal Kitab analysis.

    In Laal Kitab the Teva (birth chart) places the ascendant sign
    as House 1. Houses are counted sequentially from there:
    e.g. if Asc = Gemini -> Gemini = H1, Cancer = H2, Leo = H3 ...
    """

    asc_sign = ascendant.get("sign", "Aries")

    # Build planet -> LK house mapping (from Ascendant)
    planet_house_map: Dict[str, int] = {}
    for p in planets:
        sign = p.get("sign", "")
        house = sign_to_house(sign, asc_sign)
        if house:
            planet_house_map[p["planet"]] = house

    # 1. Planet-in-house predictions (enhanced)
    predictions = []
    for planet_name, house in planet_house_map.items():
        planet_data = PLANET_IN_HOUSE.get(planet_name, {}).get(house, {})
        if planet_data:
            # Find conjunctions (other planets in same house)
            conjunctions = [
                p for p, h in planet_house_map.items()
                if h == house and p != planet_name
            ]
            # Determine dignity
            is_exalted = LK_EXALTED.get(planet_name) == house
            is_debilitated = LK_DEBILITATED.get(planet_name) == house
            is_pakka = PAKKA_GHAR.get(planet_name) == house
            dignity = "Exalted" if is_exalted else "Debilitated" if is_debilitated else "Pakka Ghar" if is_pakka else "Normal"

            predictions.append({
                "planet": planet_name,
                "house": house,
                "sign": house_to_sign(house, asc_sign),
                "dignity": dignity,
                "effect": planet_data.get("effect", ""),
                "good_results": planet_data.get("good", ""),
                "bad_results": planet_data.get("bad", ""),
                "remedy": planet_data.get("remedy", ""),
                "conjunctions": conjunctions,
                # Enhanced fields
                "age_triggers": planet_data.get("age_triggers", []),
                "conditions": planet_data.get("conditions", []),
                "financial": planet_data.get("financial", ""),
                "health": planet_data.get("health", ""),
                "family": planet_data.get("family", ""),
            })

    # 2. Planetary debts
    debts = analyze_debts(planet_house_map)

    # 3. Planet states (sleeping/blind/awake)
    planet_states = analyze_planet_state(planet_house_map)

    # 4. Remedies summary -- collect all remedies for afflicted planets
    remedies = []
    for pred in predictions:
        if pred["dignity"] == "Debilitated" or _is_afflicted(
            pred["planet"], pred["house"], planet_house_map
        ):
            remedies.append({
                "planet": pred["planet"],
                "house": pred["house"],
                "issue": pred["bad_results"],
                "remedy": pred["remedy"],
                "urgency": "High" if pred["dignity"] == "Debilitated" else "Medium",
            })

    # 5. House-wise summary (which planets are in which LK house)
    house_summary = {}
    for h in range(1, 13):
        planets_in_house = [p for p, ph in planet_house_map.items() if ph == h]
        house_summary[h] = {
            "house": h,
            "sign": house_to_sign(h, asc_sign),
            "planets": planets_in_house,
            "is_empty": len(planets_in_house) == 0,
        }

    # 6. Conjunction effects
    conjunction_effects = []
    for h in range(1, 13):
        planets_in_h = [p for p, ph in planet_house_map.items() if ph == h]
        if len(planets_in_h) >= 2:
            for i in range(len(planets_in_h)):
                for j in range(i + 1, len(planets_in_h)):
                    p1, p2 = planets_in_h[i], planets_in_h[j]
                    key = (p1, p2)
                    reverse_key = (p2, p1)
                    effect_data = CONJUNCTION_EFFECTS.get(key) or CONJUNCTION_EFFECTS.get(reverse_key)
                    if effect_data:
                        conjunction_effects.append({
                            "planet_1": p1,
                            "planet_2": p2,
                            "house": h,
                            "effect": effect_data.get("effect", ""),
                            "financial": effect_data.get("financial", ""),
                            "remedy": effect_data.get("remedy", ""),
                        })

    # 7. LK Yogas
    yogas = analyze_lk_yogas(planet_house_map)

    # 8. Financial analysis
    financial_analysis = analyze_financial_indicators(planet_house_map, predictions)

    # 9. Luck activation
    luck_activation = analyze_luck_activation(asc_sign, planet_house_map)

    return {
        "type": "laal_kitab",
        "ascendant_sign": asc_sign,
        "ascendant_lk_house": 1,  # Ascendant is always House 1 in LK
        "planet_houses": planet_house_map,
        "predictions": predictions,
        "debts": debts,
        "planet_states": planet_states,
        "remedies": remedies,
        "house_summary": house_summary,
        # New enhanced sections
        "conjunction_effects": conjunction_effects,
        "yogas": yogas,
        "financial_analysis": financial_analysis,
        "luck_activation": luck_activation,
    }
