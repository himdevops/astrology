"""
deity_analysis.py — Divisional Chart Deity Engine
==================================================
Comprehensive deity mappings for D3, D7, D9, D10, D12, D60
with career, fortune, karma predictions per deity.
Dasha-deity timeline integration.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

SIGNS = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
]

# ============================================================================
# D10 DASHAMSHA DEITIES (10 per sign cycle, mapped to degree divisions)
# Each 3° division within a sign maps to a deity
# Based on Brihat Parashara Hora Shastra
# ============================================================================

D10_DEITIES = {
    0:  {"name": "Indra",       "nature": "benefic",  "domain": "Authority & Leadership",
         "career": "Government, administration, CEO, director, politics. Commands respect and wields institutional power.",
         "result": "Rise to prominence through established institutions. Natural leader who earns loyalty."},
    1:  {"name": "Agni",        "nature": "benefic",  "domain": "Energy & Transformation",
         "career": "Engineering, energy sector, metallurgy, fire services, surgery. Transformative professional roles.",
         "result": "Career marked by intensity and purification. Rises through competitive fire."},
    2:  {"name": "Yama",        "nature": "malefic",  "domain": "Justice & Discipline",
         "career": "Law, judiciary, police, audit, compliance, forensics. Roles enforcing order and accountability.",
         "result": "Career in justice/regulation. Strict professional reputation. Delayed but lasting success."},
    3:  {"name": "Nirriti",     "nature": "malefic",  "domain": "Destruction & Dissolution",
         "career": "Demolition, crisis management, restructuring, debt recovery, insolvency. Breaking down old structures.",
         "result": "Career through upheaval or dismantling. Profits from others' losses. Volatile professional life."},
    4:  {"name": "Varuna",      "nature": "benefic",  "domain": "Oceans & Cosmic Order",
         "career": "Navy, shipping, maritime, water resources, diplomacy, international affairs, import-export.",
         "result": "Career connected to water/overseas. Success through maintaining cosmic/social order."},
    5:  {"name": "Vayu",        "nature": "benefic",  "domain": "Wind & Communication",
         "career": "Aviation, telecom, media, broadcasting, logistics, courier, public speaking, writing.",
         "result": "Career in movement/communication fields. Quick professional changes. Versatile and adaptable."},
    6:  {"name": "Kubera",      "nature": "benefic",  "domain": "Wealth & Treasury",
         "career": "Banking, finance, treasury, accounting, wealth management, real estate investment.",
         "result": "Excellent for accumulating professional wealth. Career brings financial abundance."},
    7:  {"name": "Ishana",      "nature": "benefic",  "domain": "Supreme Knowledge",
         "career": "Research, academia, philosophy, spiritual teaching, higher education, think tanks.",
         "result": "Career in wisdom/knowledge fields. Respected as authority in intellectual domain."},
    8:  {"name": "Padmaja",     "nature": "benefic",  "domain": "Creation & Creativity",
         "career": "Arts, design, architecture, content creation, advertising, innovation, startups.",
         "result": "Career flourishes through creative output. Born creator who monetizes talent."},
    9:  {"name": "Ananta",      "nature": "benefic",  "domain": "Infinite & Sustaining",
         "career": "IT infrastructure, sustainable business, long-term projects, pension/insurance, maintenance.",
         "result": "Enduring career with no retirement. Professional relevance that never fades."},
}

# ============================================================================
# D9 NAVAMSHA DEITIES (Navamsha-sign based deity association)
# The deity is linked to the Navamsha sign's ruling deity
# ============================================================================

D9_DEITIES = {
    "Aries":       {"name": "Mangala (Mars deity)", "nature": "fierce",
                    "fortune": "Fortune through courage, competition, and pioneering action. Wealth via real estate, defense, sports.",
                    "dharma": "Dharma path of the warrior — protect, compete, lead from the front.",
                    "marriage": "Passionate but fiery partnerships. Spouse is independent and action-oriented."},
    "Taurus":      {"name": "Shukra (Venus deity)", "nature": "benefic",
                    "fortune": "Fortune through luxury, arts, beauty, food industry. Steady wealth accumulation.",
                    "dharma": "Dharma of enjoyment — experience material beauty as divine expression.",
                    "marriage": "Devoted, sensual partner. Marriage brings material comfort and stability."},
    "Gemini":      {"name": "Budha (Mercury deity)", "nature": "neutral",
                    "fortune": "Fortune through intellect, trade, writing, media, communication. Quick gains.",
                    "dharma": "Dharma of knowledge — learn, teach, connect, translate wisdom for others.",
                    "marriage": "Intellectual compatibility key. Spouse is communicative and youthful."},
    "Cancer":      {"name": "Chandra (Moon deity)", "nature": "benefic",
                    "fortune": "Fortune through nurturing, hospitality, real estate, food, public service. Emotional intelligence brings wealth.",
                    "dharma": "Dharma of care — protect the vulnerable, nourish community.",
                    "marriage": "Deep emotional bond. Spouse is nurturing, domestic, maternal/paternal."},
    "Leo":         {"name": "Surya (Sun deity)", "nature": "benefic",
                    "fortune": "Fortune through authority, government, leadership, self-expression. Wealth from position of power.",
                    "dharma": "Dharma of sovereignty — lead with integrity, illuminate others' paths.",
                    "marriage": "Spouse is dignified, proud, possibly in government/authority. Royal partnerships."},
    "Virgo":       {"name": "Budha (Mercury deity)", "nature": "neutral",
                    "fortune": "Fortune through service, health, analytics, accounting, detail work. Wealth from precision.",
                    "dharma": "Dharma of service — heal, organize, perfect, serve with skill.",
                    "marriage": "Practical, service-oriented partner. Marriage built on mutual support and health."},
    "Libra":       {"name": "Shukra (Venus deity)", "nature": "benefic",
                    "fortune": "Fortune through partnerships, law, diplomacy, fashion, beauty. Wealth through others.",
                    "dharma": "Dharma of balance — create harmony, mediate, bring justice and beauty.",
                    "marriage": "Ideal placement. Beautiful partnerships, mutual respect, artistic spouse."},
    "Scorpio":     {"name": "Mangala (Mars deity)", "nature": "fierce",
                    "fortune": "Fortune through transformation, insurance, occult, research, inheritance. Hidden wealth.",
                    "dharma": "Dharma of transformation — destroy ego, regenerate, access hidden power.",
                    "marriage": "Intense, transformative marriages. Spouse has depth and mystery. Power dynamics."},
    "Sagittarius": {"name": "Guru (Jupiter deity)", "nature": "benefic",
                    "fortune": "Fortune through teaching, law, religion, publishing, foreign travel. Dharmic wealth.",
                    "dharma": "Dharma of wisdom — teach truth, expand consciousness, uphold law.",
                    "marriage": "Philosophical, adventurous partner. Spouse from different culture/background possible."},
    "Capricorn":   {"name": "Shani (Saturn deity)", "nature": "strict",
                    "fortune": "Fortune through discipline, government, mining, construction. Late but lasting wealth.",
                    "dharma": "Dharma of duty — work hard, build structures, serve time-bound obligations.",
                    "marriage": "Mature, responsible partner. Marriage may be delayed but is stable and enduring."},
    "Aquarius":    {"name": "Shani (Saturn deity)", "nature": "strict",
                    "fortune": "Fortune through technology, social causes, networks, innovation. Unconventional wealth.",
                    "dharma": "Dharma of humanity — serve the collective, innovate for social good.",
                    "marriage": "Unconventional partnerships. Spouse is progressive, independent, humanitarian."},
    "Pisces":      {"name": "Guru (Jupiter deity)", "nature": "benefic",
                    "fortune": "Fortune through spirituality, healing, charity, film, imagination. Divine grace brings wealth.",
                    "dharma": "Dharma of surrender — dissolve ego, serve the divine, heal through compassion.",
                    "marriage": "Spiritual connection with spouse. Soulmate energy. Sacrificial love."},
}

# ============================================================================
# D3 DREKKANA DEITIES (3 deities per sign = 36 total)
# Each 10° of a sign maps to a Drekkana with a specific deity
# Based on Varahamihira's Brihat Jataka
# ============================================================================

D3_DEITIES = {
    # (sign_index, drekkana 0/1/2) → deity
    (0,0): {"name": "Narada",      "nature": "benefic",  "domain": "Divine Messenger",
            "result": "Courage through communication. Siblings are helpful. Success in short journeys and writing."},
    (0,1): {"name": "Agastya",     "nature": "benefic",  "domain": "Sage of the South",
            "result": "Efforts rewarded through discipline. Business partners are reliable. Travels south benefit."},
    (0,2): {"name": "Durvasa",     "nature": "malefic",  "domain": "Sage of Anger",
            "result": "Courage through intensity. Conflict with siblings possible. Efforts need anger management."},
    (1,0): {"name": "Agni",        "nature": "benefic",  "domain": "Sacred Fire",
            "result": "Wealth through efforts. Business partnerships bring material gains. Artistic collaborations."},
    (1,1): {"name": "Vayu",        "nature": "benefic",  "domain": "Wind God",
            "result": "Success through movement and trade. Import-export with partners. Quick business gains."},
    (1,2): {"name": "Indra",       "nature": "benefic",  "domain": "King of Gods",
            "result": "Leadership in partnerships. Dominant role in collaborations. Government contracts."},
    (2,0): {"name": "Kubera",      "nature": "benefic",  "domain": "Lord of Wealth",
            "result": "Wealthy business partners. Financial collaborations succeed. Banking partnerships."},
    (2,1): {"name": "Varuna",      "nature": "benefic",  "domain": "Lord of Waters",
            "result": "Overseas business connections. Partners from foreign lands. Maritime trade."},
    (2,2): {"name": "Yama",        "nature": "malefic",  "domain": "Lord of Death",
            "result": "Difficult partnerships. Legal battles with co-workers. Effort brings karmic debts."},
    (3,0): {"name": "Chandra",     "nature": "benefic",  "domain": "Moon God",
            "result": "Nurturing partnerships. Emotional business connections. Hospitality ventures succeed."},
    (3,1): {"name": "Shukra",      "nature": "benefic",  "domain": "Venus deity",
            "result": "Beautiful collaborations. Arts and luxury partnerships. Female business partners help."},
    (3,2): {"name": "Brihaspati",  "nature": "benefic",  "domain": "Jupiter deity",
            "result": "Wise counsel from partners. Educational collaborations. Dharmic business ventures."},
    (4,0): {"name": "Surya",       "nature": "benefic",  "domain": "Sun God",
            "result": "Powerful alliances. Government partnerships. Father-figure business mentors."},
    (4,1): {"name": "Karttikeya",  "nature": "benefic",  "domain": "War God",
            "result": "Competitive partnerships win. Military/sports collaborations. Sibling in defense."},
    (4,2): {"name": "Vishwakarma", "nature": "benefic",  "domain": "Divine Architect",
            "result": "Engineering partnerships. Construction business. Partners in technical fields."},
    (5,0): {"name": "Budha",       "nature": "neutral",  "domain": "Mercury deity",
            "result": "Analytical partnerships. Accounting/audit collaborations. Detail-oriented co-workers."},
    (5,1): {"name": "Kamadeva",    "nature": "benefic",  "domain": "God of Love",
            "result": "Passionate collaborations. Beauty industry partnerships. Romantic business ventures."},
    (5,2): {"name": "Vishnu",      "nature": "benefic",  "domain": "The Preserver",
            "result": "Sustained partnerships. Long-term business alliances. Protective co-workers."},
    (6,0): {"name": "Shukra",      "nature": "benefic",  "domain": "Venus deity",
            "result": "Balanced partnerships. Legal collaborations. Fashion and beauty business."},
    (6,1): {"name": "Lakshmi",     "nature": "benefic",  "domain": "Goddess of Wealth",
            "result": "Wealthy partnerships. Fortune through female partners. Luxury business ventures."},
    (6,2): {"name": "Saraswati",   "nature": "benefic",  "domain": "Goddess of Knowledge",
            "result": "Educational partnerships. Publishing collaborations. Knowledge-based business."},
    (7,0): {"name": "Rudra",       "nature": "malefic",  "domain": "The Destroyer",
            "result": "Intense partnerships. Research collaborations. Partners in occult/hidden sciences."},
    (7,1): {"name": "Kali",        "nature": "malefic",  "domain": "Goddess of Time",
            "result": "Transformative partnerships. Crisis management together. Insurance/death-related business."},
    (7,2): {"name": "Yamuna",      "nature": "benefic",  "domain": "Sacred River",
            "result": "Purifying partnerships. Healing business collaborations. Water-related ventures."},
    (8,0): {"name": "Brihaspati",  "nature": "benefic",  "domain": "Divine Teacher",
            "result": "Teaching partnerships. Religious collaborations. Publishing and law."},
    (8,1): {"name": "Dhanvantari", "nature": "benefic",  "domain": "Divine Physician",
            "result": "Medical partnerships. Healing business. Pharmaceutical collaborations."},
    (8,2): {"name": "Ganesha",     "nature": "benefic",  "domain": "Remover of Obstacles",
            "result": "Partnerships overcome obstacles. Lucky collaborations. Business starts succeed."},
    (9,0): {"name": "Shani",       "nature": "strict",   "domain": "Saturn deity",
            "result": "Disciplined partnerships. Government contracts. Mining/construction collaborations."},
    (9,1): {"name": "Hanuman",     "nature": "benefic",  "domain": "Divine Devotee",
            "result": "Devoted partners. Service-oriented collaborations. Selfless business allies."},
    (9,2): {"name": "Bhairava",    "nature": "malefic",  "domain": "Fierce Shiva",
            "result": "Fearless partnerships. Security business. Tantra/occult collaborations."},
    (10,0):{"name": "Varuna",      "nature": "benefic",  "domain": "Cosmic Order",
            "result": "Orderly partnerships. Technology collaborations. Innovative business alliances."},
    (10,1):{"name": "Vayu",        "nature": "benefic",  "domain": "Wind God",
            "result": "Fast-moving partnerships. Aviation/logistics collaborations. Network-based business."},
    (10,2):{"name": "Prajapati",   "nature": "benefic",  "domain": "Lord of Creation",
            "result": "Creative partnerships. Startup collaborations. Birthing new business ventures."},
    (11,0):{"name": "Vishnu",      "nature": "benefic",  "domain": "The Preserver",
            "result": "Protective partnerships. Charitable collaborations. Spiritual business ventures."},
    (11,1):{"name": "Chandra",     "nature": "benefic",  "domain": "Moon deity",
            "result": "Intuitive partnerships. Creative collaborations. Imaginative business."},
    (11,2):{"name": "Brahma",      "nature": "benefic",  "domain": "The Creator",
            "result": "Expansive partnerships. Philosophical collaborations. Universe-building business."},
}

# ============================================================================
# D7 SAPTAMSHA DEITIES (7 per sign cycle)
# Based on Parashara — linked to Sapta Matrikas and planetary deities
# ============================================================================

D7_DEITIES = {
    0: {"name": "Brahmani",    "nature": "benefic",  "domain": "Creative Power",
        "result": "Children bring wisdom and creative power. Progeny connected to knowledge and teaching."},
    1: {"name": "Maheshwari",  "nature": "benefic",  "domain": "Divine Feminine Power",
        "result": "Children bring transformative energy. Strong-willed progeny with leadership qualities."},
    2: {"name": "Kaumari",     "nature": "benefic",  "domain": "Youthful Warrior",
        "result": "Children are competitive and brave. Progeny excels in sports, military, or competition."},
    3: {"name": "Vaishnavi",   "nature": "benefic",  "domain": "Preservation",
        "result": "Children are protectors and sustainers. Progeny maintains family legacy and traditions."},
    4: {"name": "Varahi",      "nature": "fierce",   "domain": "Earth Power",
        "result": "Children have hidden strength. Progeny connected to land, agriculture, or resources."},
    5: {"name": "Indrani",     "nature": "benefic",  "domain": "Royal Consort",
        "result": "Children achieve high status. Progeny connected to authority and institutional power."},
    6: {"name": "Chamunda",    "nature": "malefic",  "domain": "Fierce Destroyer",
        "result": "Children face challenges but emerge transformed. Progeny breaks family patterns."},
}

# ============================================================================
# D12 DWADASHAMSHA DEITIES (12 per sign = Adityas)
# The 12 Adityas rule the 12 divisions — sons of Aditi
# ============================================================================

D12_DEITIES = {
    0:  {"name": "Dhata",      "nature": "benefic",  "domain": "Creator/Establisher",
         "result": "Ancestral blessing of creation. Parents established family wealth. Lineage of builders."},
    1:  {"name": "Aryaman",    "nature": "benefic",  "domain": "Nobility & Hospitality",
         "result": "Noble ancestral lineage. Parents known for generosity. Inherited social connections."},
    2:  {"name": "Mitra",      "nature": "benefic",  "domain": "Friendship & Contracts",
         "result": "Friendly parental relationship. Ancestral alliances benefit. Inherited trustworthiness."},
    3:  {"name": "Varuna",     "nature": "benefic",  "domain": "Cosmic Order",
         "result": "Orderly family lineage. Parents maintained dharma. Inherited sense of justice."},
    4:  {"name": "Indra",      "nature": "benefic",  "domain": "King of Gods",
         "result": "Powerful ancestral lineage. Parents held authority. Inherited leadership ability."},
    5:  {"name": "Vivasvan",   "nature": "benefic",  "domain": "Radiant Sun",
         "result": "Luminous family heritage. Parents were respected/famous. Inherited charisma."},
    6:  {"name": "Bhaga",      "nature": "benefic",  "domain": "Fortune & Inheritance",
         "result": "Lucky ancestral karma. Parents leave wealth. Inherited fortune and property."},
    7:  {"name": "Parjanya",   "nature": "benefic",  "domain": "Rain & Fertility",
         "result": "Fertile family lineage. Large family. Parents connected to agriculture/nature."},
    8:  {"name": "Tvashta",    "nature": "benefic",  "domain": "Divine Craftsman",
         "result": "Artistic ancestral lineage. Parents were skilled craftsmen/artists. Inherited talent."},
    9:  {"name": "Pushan",     "nature": "benefic",  "domain": "Nourisher & Guide",
         "result": "Nourishing family heritage. Parents were guides/mentors. Inherited teaching ability."},
    10: {"name": "Savitar",    "nature": "benefic",  "domain": "Impeller/Motivator",
         "result": "Motivating ancestral energy. Parents inspired action. Inherited entrepreneurial spirit."},
    11: {"name": "Vishnu",     "nature": "benefic",  "domain": "The Preserver",
         "result": "Preserving family heritage. Parents maintained traditions. Inherited spiritual lineage."},
}

# ============================================================================
# D60 SHASHTIAMSHA DEITIES — Extended with karmic results
# 60 deities with detailed karmic past-life indications
# ============================================================================

D60_DEITY_DETAILS = {
    "Ghora":          {"nature": "malefic",  "karma": "Past-life violence. Current life tests through fear and aggression. Need to cultivate peace.",
                       "fortune": "Wealth through overcoming fears. Career in security, defense, crisis management."},
    "Rakshasa":       {"nature": "malefic",  "karma": "Past-life demonic tendencies. Current life faces deception and betrayal. Trust issues to resolve.",
                       "fortune": "Wealth through unconventional or underground means. Night-shift professions benefit."},
    "Deva":           {"nature": "benefic",  "karma": "Past-life divine merit. Current life blessed with grace, good fortune, and spiritual inclination.",
                       "fortune": "Wealth comes easily through divine grace. Temple, charity, or spiritual profession benefits."},
    "Kubera":         {"name": "Kubera", "nature": "benefic",  "karma": "Past-life generosity. Current life rewarded with material abundance and financial wisdom.",
                       "fortune": "Excellent wealth karma. Banking, treasure, gold, finance — all prosper."},
    "Yaksha":         {"nature": "benefic",  "karma": "Past-life nature guardianship. Current life connected to forests, nature, hidden treasures.",
                       "fortune": "Hidden wealth emerges unexpectedly. Real estate, mining, natural resources."},
    "Kinnara":        {"nature": "benefic",  "karma": "Past-life artistic devotion. Current life gifted with music, dance, and performing arts.",
                       "fortune": "Wealth through arts, entertainment, music, film. Creative fortune."},
    "Bhrashta":       {"nature": "malefic",  "karma": "Past-life moral fall. Current life faces reputation challenges. Need to rebuild integrity.",
                       "fortune": "Wealth unstable. Gains followed by losses until karmic debt is cleared."},
    "Kulaghna":       {"nature": "malefic",  "karma": "Past-life family destruction. Current life may face family conflicts or lineage disruption.",
                       "fortune": "Wealth separated from family. Self-made but estranged from ancestral property."},
    "Garala":         {"nature": "malefic",  "karma": "Past-life poisoning (literal or metaphorical). Current life faces toxicity — substances, people, environments.",
                       "fortune": "Wealth through pharmaceuticals, chemicals, detoxification, poison management."},
    "Agni":           {"nature": "fierce",   "karma": "Past-life fire sacrifice. Current life has purifying intensity. Burns away impurities.",
                       "fortune": "Wealth through energy, fire, cooking, engineering, metallurgy."},
    "Maya":           {"nature": "neutral",  "karma": "Past-life illusion mastery. Current life navigates between reality and illusion.",
                       "fortune": "Wealth through entertainment, VFX, magic, illusion-based professions."},
    "Purishaka":      {"nature": "malefic",  "karma": "Past-life material excess. Current life challenged with greed/hoarding tendencies.",
                       "fortune": "Wealth through waste management, recycling, sanitation, storage."},
    "Apampathi":      {"nature": "benefic",  "karma": "Past-life water devotion. Current life connected to healing waters and emotional purification.",
                       "fortune": "Wealth through water — shipping, beverages, fisheries, hydro-power."},
    "Marut":          {"nature": "benefic",  "karma": "Past-life wind/prana mastery. Current life has tremendous vital force and energy.",
                       "fortune": "Wealth through movement — aviation, logistics, wind energy, sports."},
    "Kaala":          {"nature": "malefic",  "karma": "Past-life time-related karma. Current life highly time-sensitive. Punctuality and deadlines crucial.",
                       "fortune": "Wealth through time-bound services — insurance, astrology, antiques."},
    "Sarpa":          {"nature": "malefic",  "karma": "Past-life serpent karma (Naga dosha). Current life faces sudden strikes and hidden enemies.",
                       "fortune": "Wealth through research, underground resources, kundalini healing."},
    "Amrita":         {"nature": "benefic",  "karma": "Past-life nectar of immortality earned. Current life blessed with longevity and vitality.",
                       "fortune": "Excellent fortune. Wealth flows like nectar — healing, Ayurveda, life-extension."},
    "Indu":           {"nature": "benefic",  "karma": "Past-life lunar devotion. Current life blessed with emotional intelligence and public love.",
                       "fortune": "Wealth through public-facing roles. Popularity brings fortune."},
    "Mridu":          {"nature": "benefic",  "karma": "Past-life gentleness. Current life soft-natured and compassionate. Gentle personality.",
                       "fortune": "Wealth through soft goods — textiles, silk, cosmetics, spa, wellness."},
    "Komala":         {"nature": "benefic",  "karma": "Past-life beauty creation. Current life surrounded by beauty and refinement.",
                       "fortune": "Wealth through beauty, fashion, flowers, fragrance, luxury goods."},
    "Heramba":        {"nature": "benefic",  "karma": "Past-life Ganesha devotion. Current life obstacles removed divinely. Protected by grace.",
                       "fortune": "Fortune after initial obstacles. Every blocked path opens a better one."},
    "Brahma":         {"nature": "benefic",  "karma": "Past-life creative power. Current life blessed with original ideas and creative genius.",
                       "fortune": "Wealth through creation — startups, invention, writing, architecture."},
    "Vishnu":         {"nature": "benefic",  "karma": "Past-life preservation karma. Current life sustains and maintains what others create.",
                       "fortune": "Steady, preserved wealth. Long-term investments prosper. Mutual funds, real estate."},
    "Maheshwara":     {"nature": "benefic",  "karma": "Past-life Shiva devotion. Current life has power to destroy and recreate. Ascetic tendencies.",
                       "fortune": "Wealth through destruction of old and creation of new. Transformation consulting."},
    "Ardra":          {"nature": "malefic",  "karma": "Past-life storm karma. Current life faces emotional storms and sudden upheavals.",
                       "fortune": "Wealth after storms pass. Rebuilding businesses. Disaster management."},
    "Kalinasa":       {"nature": "benefic",  "karma": "Past-life time-conquest. Current life transcends normal time limitations. Ageless quality.",
                       "fortune": "Wealth through timeless things — art, antiques, gold, classical knowledge."},
    "Kshitisa":       {"nature": "benefic",  "karma": "Past-life earth rulership. Current life has authority over land and territory.",
                       "fortune": "Wealth through land, real estate, agriculture, mining, geography."},
    "Kamalaakara":    {"nature": "benefic",  "karma": "Past-life lotus garden karma. Current life blooms from muddy circumstances into beauty.",
                       "fortune": "Fortune from humble beginnings. Self-made wealth. Rags to riches."},
    "Gulika":         {"nature": "malefic",  "karma": "Past-life Saturn-poison karma. Current life faces chronic delays and toxic situations.",
                       "fortune": "Wealth through patience in toxic environments. Detoxification professions."},
    "Mrityu":         {"nature": "malefic",  "karma": "Past-life death-dealing. Current life faces mortality fears and near-death experiences.",
                       "fortune": "Wealth through death-related — insurance, mortuary, end-of-life care, hospice."},
    "Davagni":        {"nature": "malefic",  "karma": "Past-life forest fire. Current life faces uncontrollable destructive forces.",
                       "fortune": "Wealth through fire services, wildfire management, controlled burns, renewables."},
    "Yama":           {"nature": "malefic",  "karma": "Past-life justice karma. Current life is judge and judged. Strict moral code required.",
                       "fortune": "Wealth through law, justice, judiciary, compliance, ethics consulting."},
    "Kantaka":        {"nature": "malefic",  "karma": "Past-life thorn karma. Current life has persistent irritants and small but constant obstacles.",
                       "fortune": "Wealth through removing others' obstacles. Consulting, troubleshooting, IT support."},
    "Sudha":          {"nature": "benefic",  "karma": "Past-life nectar karma. Current life sweet-natured with healing touch.",
                       "fortune": "Wealth through sugar, sweetness, confectionery, healing, Ayurveda."},
    "Poornachandra":  {"nature": "benefic",  "karma": "Past-life full moon karma. Current life at peak — everything comes to fruition.",
                       "fortune": "Full fortune realized. Peak career and wealth in this lifetime. Complete success."},
    "Vishagdha":      {"nature": "malefic",  "karma": "Past-life poison consumption. Current life processes toxins — environmental or emotional.",
                       "fortune": "Wealth through purification, water treatment, environmental cleanup."},
    "Kulanashana":    {"nature": "malefic",  "karma": "Past-life dynasty destruction. Current life may end or transform family lineage.",
                       "fortune": "Wealth through breaking traditions. Disruptive innovation. New family path."},
    "Vamshakshaya":   {"nature": "malefic",  "karma": "Past-life lineage extinction. Current life rebuilds from nothing. Self-made person.",
                       "fortune": "Wealth created from scratch. No inheritance but builds empire independently."},
    "Utpata":         {"nature": "malefic",  "karma": "Past-life calamity. Current life faces unexpected upheavals and natural disasters.",
                       "fortune": "Wealth through disaster preparedness, emergency services, insurance."},
    "Saumya":         {"nature": "benefic",  "karma": "Past-life gentility. Current life blessed with grace, beauty, and social charm.",
                       "fortune": "Wealth through charm, diplomacy, social connections, hospitality."},
    "Sheetala":       {"nature": "benefic",  "karma": "Past-life cooling karma. Current life brings peace and calm to heated situations.",
                       "fortune": "Wealth through cooling — AC, refrigeration, ice cream, meditation, spa."},
    "Karala":         {"nature": "malefic",  "karma": "Past-life fierce karma. Current life has intense, frightening experiences to transcend.",
                       "fortune": "Wealth through facing fears. Horror, thriller, security, extreme sports."},
    "Chandramukhi":   {"nature": "benefic",  "karma": "Past-life moon-face beauty. Current life beautiful and charismatic with public appeal.",
                       "fortune": "Wealth through beauty, modeling, acting, public facing, social media."},
    "Praveena":       {"nature": "benefic",  "karma": "Past-life expertise. Current life naturally skilled and proficient in chosen field.",
                       "fortune": "Wealth through expertise and mastery. Consulting, specialist roles, niche skills."},
    "Kalapavaka":     {"nature": "malefic",  "karma": "Past-life time-fire karma. Burning urgency and time pressure in current life.",
                       "fortune": "Wealth through time-critical services — emergency, trading, deadline-driven work."},
    "Dandayudha":     {"nature": "malefic",  "karma": "Past-life weapon/punishment karma. Current life faces authority and discipline themes.",
                       "fortune": "Wealth through authority, military, police, security, weapons industry."},
    "Nirmala":        {"nature": "benefic",  "karma": "Past-life purity. Current life pristine and uncorrupted. Clean reputation.",
                       "fortune": "Wealth through purity — organic food, clean energy, purification, spiritual services."},
    "Kroora":         {"nature": "malefic",  "karma": "Past-life cruelty. Current life faces harsh treatment to balance karma. Need compassion.",
                       "fortune": "Wealth through tough industries — mining, demolition, surgery, debt recovery."},
    "Atisheetala":    {"nature": "benefic",  "karma": "Past-life extreme cooling. Current life has profound calming effect on surroundings.",
                       "fortune": "Wealth through cold storage, frozen goods, winter tourism, cryogenics."},
    "Payodhi":        {"nature": "benefic",  "karma": "Past-life ocean karma. Current life vast and deep like the ocean. Infinite potential.",
                       "fortune": "Wealth through ocean — maritime, pearls, seafood, offshore, navy."},
    "Bhramana":       {"nature": "neutral",  "karma": "Past-life wandering. Current life of travel and movement. Nomadic tendencies.",
                       "fortune": "Wealth through travel — tourism, pilgrimage, transport, global trade."},
    "Chandrarekha":   {"nature": "benefic",  "karma": "Past-life crescent moon karma. Current life of gradual growth and waxing fortune.",
                       "fortune": "Fortune grows steadily like waxing moon. Best years are ahead. Patient accumulation."},
}

# D60 deity name list (used for index lookup)
D60_DEITY_NAMES = [
    "Ghora","Rakshasa","Deva","Kubera","Yaksha","Kinnara","Bhrashta","Kulaghna",
    "Garala","Agni","Maya","Purishaka","Apampathi","Marut","Kaala","Sarpa",
    "Amrita","Indu","Mridu","Komala","Heramba","Brahma","Vishnu","Maheshwara",
    "Deva","Ardra","Kalinasa","Kshitisa","Kamalaakara","Gulika","Mrityu","Kaala",
    "Davagni","Ghora","Yama","Kantaka","Sudha","Amrita","Poornachandra","Vishagdha",
    "Kulanashana","Vamshakshaya","Utpata","Kaala","Saumya","Komala","Sheetala",
    "Karala","Chandramukhi","Praveena","Kalapavaka","Dandayudha","Nirmala","Saumya",
    "Kroora","Atisheetala","Amrita","Payodhi","Bhramana","Chandrarekha"
]


# ============================================================================
# CALCULATION FUNCTIONS
# ============================================================================

def _sign_from_degree(lon: float):
    """Return (sign_name, degree_in_sign) from absolute longitude."""
    idx = int(lon / 30) % 12
    return SIGNS[idx], lon % 30


def _d3_part(lon: float):
    """Return (sign_index, drekkana_part 0-2) for D3."""
    sign_idx = int(lon / 30) % 12
    deg = lon % 30
    part = min(int(deg / 10.0), 2)
    return sign_idx, part


def _d7_part(lon: float, sign_idx: int):
    """Return D7 deity index 0-6, with even-sign reversal per BPHS.
    Odd signs (Aries=0, Gemini=2...): deity order 0→6 forward.
    Even signs (Taurus=1, Cancer=3...): deity order 6→0 reversed.
    """
    deg = lon % 30
    span = 30.0 / 7.0
    part = min(int(deg / span), 6)
    if sign_idx % 2 == 1:       # even sign → reverse deity order
        return 6 - part
    return part


def _d9_sign(lon: float):
    """Return D9 Navamsha sign name."""
    NAVAMSHA_START = [0, 9, 6, 3, 0, 9, 6, 3, 0, 9, 6, 3]
    sign_idx = int(lon / 30) % 12
    deg = lon % 30
    pada = min(int(deg / (10.0 / 3.0)), 8)
    nav_idx = (NAVAMSHA_START[sign_idx] + pada) % 12
    return SIGNS[nav_idx]


def _d10_part(lon: float):
    """Return D10 deity index 0-9, with even-sign reversal per BPHS.
    Odd signs (Aries=0, Gemini=2...): deity 0→9 forward (Indra→Ananta).
    Even signs (Taurus=1, Cancer=3, Virgo=5...): deity 9→0 reversed (Ananta→Indra).
    E.g. Sun at Virgo 7° → division 2 → deity = 9-2 = 7 (Ishana).
    """
    sign_idx = int(lon / 30) % 12
    deg = lon % 30
    division = min(int(deg / 3.0), 9)
    if sign_idx % 2 == 1:       # even sign → reverse deity order
        return 9 - division
    return division


def _d12_part(lon: float):
    """Return D12 division index 0-11."""
    deg = lon % 30
    return min(int(deg / 2.5), 11)


def _d60_part(lon: float):
    """Return D60 division index 0-59."""
    deg = lon % 30
    span = 30.0 / 60.0
    return min(int(deg / span), 59)


def calculate_deity_analysis(planets: list, ascendant: dict) -> dict:
    """
    Complete deity analysis across D3, D7, D9, D10, D12, D60
    for all planets. Returns per-planet deity breakdown.
    """
    results = []

    for p in planets:
        pname = p.get("planet", "")
        lon = p.get("longitude", 0.0)
        sign_idx = int(lon / 30) % 12

        # D3 Drekkana deity
        d3_sign_idx, d3_part = _d3_part(lon)
        d3_deity_data = D3_DEITIES.get((d3_sign_idx, d3_part), {})

        # D7 Saptamsha deity
        d7_part = _d7_part(lon, sign_idx)
        d7_deity_data = D7_DEITIES.get(d7_part, {})

        # D9 Navamsha deity
        d9_sign = _d9_sign(lon)
        d9_deity_data = D9_DEITIES.get(d9_sign, {})

        # D10 Dashamsha deity
        d10_part = _d10_part(lon)
        d10_deity_data = D10_DEITIES.get(d10_part, {})

        # D12 Dwadashamsha deity
        d12_part = _d12_part(lon)
        d12_deity_data = D12_DEITIES.get(d12_part, {})

        # D60 Shashtiamsha deity
        d60_part = _d60_part(lon)
        d60_name = D60_DEITY_NAMES[d60_part] if d60_part < len(D60_DEITY_NAMES) else ""
        d60_deity_data = D60_DEITY_DETAILS.get(d60_name, {})

        results.append({
            "planet": pname,
            "longitude": round(lon, 4),
            "d1_sign": SIGNS[sign_idx],
            "d3": {
                "deity": d3_deity_data.get("name", ""),
                "nature": d3_deity_data.get("nature", ""),
                "domain": d3_deity_data.get("domain", ""),
                "result": d3_deity_data.get("result", ""),
            },
            "d7": {
                "deity": d7_deity_data.get("name", ""),
                "nature": d7_deity_data.get("nature", ""),
                "domain": d7_deity_data.get("domain", ""),
                "result": d7_deity_data.get("result", ""),
            },
            "d9": {
                "sign": d9_sign,
                "deity": d9_deity_data.get("name", ""),
                "nature": d9_deity_data.get("nature", ""),
                "fortune": d9_deity_data.get("fortune", ""),
                "dharma": d9_deity_data.get("dharma", ""),
                "marriage": d9_deity_data.get("marriage", ""),
            },
            "d10": {
                "deity": d10_deity_data.get("name", ""),
                "nature": d10_deity_data.get("nature", ""),
                "domain": d10_deity_data.get("domain", ""),
                "career": d10_deity_data.get("career", ""),
                "result": d10_deity_data.get("result", ""),
            },
            "d12": {
                "deity": d12_deity_data.get("name", ""),
                "nature": d12_deity_data.get("nature", ""),
                "domain": d12_deity_data.get("domain", ""),
                "result": d12_deity_data.get("result", ""),
            },
            "d60": {
                "deity": d60_name,
                "nature": d60_deity_data.get("nature", ""),
                "karma": d60_deity_data.get("karma", ""),
                "fortune": d60_deity_data.get("fortune", ""),
            },
        })

    return {
        "type": "deity_analysis",
        "planet_deities": results,
    }


# ============================================================================
# DASHA LORD ATTRIBUTES — for combined interpretation with deities
# ============================================================================

DASHA_LORD_ATTRS: Dict[str, Dict] = {
    "Sun": {
        "energy": "authority, ego, government, power, father, leadership",
        "style": "commanding, confident, institutional",
        "career_flavor": "government, PSU, administration, politics, authority roles",
        "wealth_style": "through position of power, government grants, patronage",
        "risk": "ego conflicts, power struggles, burnout from over-ambition",
    },
    "Moon": {
        "energy": "emotion, public, nurturing, mother, liquidity, travel",
        "style": "intuitive, caring, public-facing, fluctuating",
        "career_flavor": "public service, hospitality, FMCG, healthcare, nursing",
        "wealth_style": "through public popularity, emotional intelligence, retail",
        "risk": "mood swings affecting career, over-sensitivity, instability",
    },
    "Mars": {
        "energy": "action, courage, aggression, competition, land, surgery",
        "style": "aggressive, competitive, pioneering, risk-taking",
        "career_flavor": "defense, police, surgery, sports, real estate, engineering",
        "wealth_style": "through bold action, competition, land deals, technical skill",
        "risk": "accidents, conflicts, legal battles, impulsive decisions",
    },
    "Mercury": {
        "energy": "intellect, communication, trade, data, analysis, youth",
        "style": "analytical, communicative, versatile, quick-thinking",
        "career_flavor": "IT, accounting, media, writing, teaching, trading, logistics",
        "wealth_style": "through intelligence, multiple income streams, trading",
        "risk": "overthinking, scattered focus, nervous energy, fraud risk",
    },
    "Jupiter": {
        "energy": "wisdom, expansion, dharma, teaching, finance, law",
        "style": "wise, generous, optimistic, expansive, righteous",
        "career_flavor": "banking, education, law, consulting, spiritual leadership",
        "wealth_style": "through wisdom, righteous means, expansion, teaching fees",
        "risk": "over-expansion, over-optimism, weight gain, complacency",
    },
    "Venus": {
        "energy": "luxury, beauty, art, love, pleasure, creativity",
        "style": "artistic, refined, pleasure-seeking, diplomatic",
        "career_flavor": "fashion, entertainment, luxury goods, hospitality, arts",
        "wealth_style": "through beauty, art, luxury market, entertainment industry",
        "risk": "over-indulgence, relationship distractions, excessive spending",
    },
    "Saturn": {
        "energy": "discipline, karma, delay, structure, labor, service",
        "style": "slow, methodical, disciplined, karmic, enduring",
        "career_flavor": "mining, oil, construction, judiciary, government service",
        "wealth_style": "through persistent effort, delayed but lasting rewards",
        "risk": "delays, depression, chronic issues, over-work, isolation",
    },
    "Rahu": {
        "energy": "obsession, foreign, technology, illusion, unconventional",
        "style": "obsessive, innovative, rule-breaking, foreign-influenced",
        "career_flavor": "IT, foreign companies, research, aviation, pharmaceuticals",
        "wealth_style": "through unconventional means, foreign sources, technology",
        "risk": "deception, addiction, sudden reversals, scandal",
    },
    "Ketu": {
        "energy": "detachment, spirituality, past-life, moksha, sudden",
        "style": "detached, spiritual, sudden, unpredictable, mystical",
        "career_flavor": "research, occult, spirituality, programming, diagnostics",
        "wealth_style": "through spiritual pursuits, sudden gains, past-life merit",
        "risk": "confusion, aimlessness, sudden losses, health issues",
    },
}


def _generate_combined_interpretation(
    dasha_lord: str,
    d10_deity_name: str,
    d10_domain: str,
    d10_career: str,
    d60_deity_name: str,
    d60_karma: str,
    d60_fortune: str,
    d9_deity_name: str,
    d9_fortune: str,
) -> Dict[str, str]:
    """
    Generate blended interpretation combining dasha lord energy
    with D10 career deity, D60 karmic deity, and D9 fortune deity.
    """
    lord_info = DASHA_LORD_ATTRS.get(dasha_lord, {})
    lord_energy = lord_info.get("energy", "")
    lord_style = lord_info.get("style", "")
    lord_career = lord_info.get("career_flavor", "")
    lord_wealth = lord_info.get("wealth_style", "")
    lord_risk = lord_info.get("risk", "")

    # Combined career interpretation
    career_interp = (
        f"During {dasha_lord} Mahadasha, the planet's {lord_style} energy "
        f"activates {d10_deity_name} ({d10_domain}). "
        f"Career direction: {d10_career} "
        f"The {dasha_lord} flavor adds {lord_career} tendencies. "
        f"Best approach: combine {dasha_lord}'s {lord_energy.split(',')[0].strip()} "
        f"with {d10_deity_name}'s {d10_domain.lower()} for maximum professional impact."
    )

    # Combined karma interpretation
    karma_interp = (
        f"D60 deity {d60_deity_name} reveals the karmic undercurrent: {d60_karma} "
        f"Under {dasha_lord}'s influence, this karma manifests through "
        f"{lord_energy.split(',')[0].strip()} and {lord_energy.split(',')[1].strip() if ',' in lord_energy else 'life events'}. "
        f"Fortune pathway: {d60_fortune}"
    )

    # Combined fortune interpretation
    fortune_interp = (
        f"D9 deity {d9_deity_name} guides fortune during {dasha_lord} period. "
        f"{d9_fortune} "
        f"Wealth comes {lord_wealth}. "
        f"The dharmic alignment of {dasha_lord} + {d9_deity_name} determines "
        f"whether fortune flows freely or faces resistance."
    )

    # Practical advice
    advice = (
        f"Focus: {d10_deity_name}'s domain ({d10_domain}) filtered through {dasha_lord}'s nature. "
        f"Favorable sectors: {lord_career}. "
        f"Watch for: {lord_risk}. "
        f"Karmic lesson from {d60_deity_name}: {d60_karma.split('.')[0]}."
    )

    return {
        "career_interpretation": career_interp,
        "karma_interpretation": karma_interp,
        "fortune_interpretation": fortune_interp,
        "practical_advice": advice,
    }


def _generate_antar_interpretation(
    maha_lord: str,
    antar_lord: str,
    d10_deity_name: str,
    d10_career: str,
    d60_deity_name: str,
    d60_karma: str,
) -> str:
    """Short combined interpretation for antardasha level."""
    maha_info = DASHA_LORD_ATTRS.get(maha_lord, {})
    antar_info = DASHA_LORD_ATTRS.get(antar_lord, {})

    maha_style = maha_info.get("style", "").split(",")[0].strip()
    antar_style = antar_info.get("style", "").split(",")[0].strip()
    antar_career = antar_info.get("career_flavor", "").split(",")[0].strip()

    return (
        f"{maha_lord}-{antar_lord} period: {maha_style} meets {antar_style}. "
        f"D10 {d10_deity_name} activates — {d10_career.split('.')[0]}. "
        f"D60 {d60_deity_name} karma: {d60_karma.split('.')[0]}. "
        f"{antar_lord} sub-period adds {antar_career} flavor to career."
    )


def build_dasha_deity_timeline(dasha_data: dict, planets: list, ascendant: dict) -> list:
    """
    Map every Mahadasha period to its deity rulers across D9, D10, D60.
    Returns timeline of dasha periods with deity predictions.
    """
    if not dasha_data or "dashas" not in dasha_data:
        return []

    # Build planet → deity lookup
    planet_deity_map = {}
    for p in planets:
        pname = p.get("planet", "")
        lon = p.get("longitude", 0.0)

        d9_sign = _d9_sign(lon)
        d9_deity = D9_DEITIES.get(d9_sign, {})

        d10_part = _d10_part(lon)
        d10_deity = D10_DEITIES.get(d10_part, {})

        d60_part = _d60_part(lon)
        d60_name = D60_DEITY_NAMES[d60_part] if d60_part < len(D60_DEITY_NAMES) else ""
        d60_deity = D60_DEITY_DETAILS.get(d60_name, {})

        planet_deity_map[pname] = {
            "d9_deity": d9_deity.get("name", ""),
            "d9_fortune": d9_deity.get("fortune", ""),
            "d9_dharma": d9_deity.get("dharma", ""),
            "d10_deity": d10_deity.get("name", ""),
            "d10_domain": d10_deity.get("domain", ""),
            "d10_career": d10_deity.get("career", ""),
            "d10_result": d10_deity.get("result", ""),
            "d60_deity": d60_name,
            "d60_karma": d60_deity.get("karma", ""),
            "d60_fortune": d60_deity.get("fortune", ""),
        }

    timeline = []
    for dasha in dasha_data.get("dashas", []):
        lord = dasha.get("mahadasha_lord", "")
        deity_info = planet_deity_map.get(lord, {})

        # Antardasha deity mapping
        antar_deities = []
        for antar in dasha.get("antardashas", []):
            antar_lord = antar.get("antardasha_lord", "")
            antar_deity = planet_deity_map.get(antar_lord, {})
            antar_interp = _generate_antar_interpretation(
                maha_lord=lord,
                antar_lord=antar_lord,
                d10_deity_name=antar_deity.get("d10_deity", ""),
                d10_career=antar_deity.get("d10_career", ""),
                d60_deity_name=antar_deity.get("d60_deity", ""),
                d60_karma=antar_deity.get("d60_karma", ""),
            )
            antar_deities.append({
                "antardasha_lord": antar_lord,
                "start_date": antar.get("start_date", ""),
                "end_date": antar.get("end_date", ""),
                "d10_deity": antar_deity.get("d10_deity", ""),
                "d10_career": antar_deity.get("d10_career", ""),
                "d60_deity": antar_deity.get("d60_deity", ""),
                "d60_karma": antar_deity.get("d60_karma", ""),
                "interpretation": antar_interp,
            })

        # Determine overall nature of this dasha
        d10_nature = "unknown"
        for _, dd in D10_DEITIES.items():
            if dd["name"] == deity_info.get("d10_deity", ""):
                d10_nature = dd["nature"]
                break

        # Generate combined interpretation
        combined = _generate_combined_interpretation(
            dasha_lord=lord,
            d10_deity_name=deity_info.get("d10_deity", ""),
            d10_domain=deity_info.get("d10_domain", ""),
            d10_career=deity_info.get("d10_career", ""),
            d60_deity_name=deity_info.get("d60_deity", ""),
            d60_karma=deity_info.get("d60_karma", ""),
            d60_fortune=deity_info.get("d60_fortune", ""),
            d9_deity_name=deity_info.get("d9_deity", ""),
            d9_fortune=deity_info.get("d9_fortune", ""),
        )

        timeline.append({
            "mahadasha_lord": lord,
            "start_date": dasha.get("start_date", ""),
            "end_date": dasha.get("end_date", ""),
            "duration_years": dasha.get("duration_years", 0),
            "d9_deity": deity_info.get("d9_deity", ""),
            "d9_fortune": deity_info.get("d9_fortune", ""),
            "d9_dharma": deity_info.get("d9_dharma", ""),
            "d10_deity": deity_info.get("d10_deity", ""),
            "d10_domain": deity_info.get("d10_domain", ""),
            "d10_career": deity_info.get("d10_career", ""),
            "d10_result": deity_info.get("d10_result", ""),
            "d60_deity": deity_info.get("d60_deity", ""),
            "d60_karma": deity_info.get("d60_karma", ""),
            "d60_fortune": deity_info.get("d60_fortune", ""),
            "career_nature": d10_nature,
            "interpretation": combined,
            "antardashas": antar_deities,
        })

    return timeline
