"""
numerology.py — Advanced Vedic + Western Numerology Engine
==========================================================
Comprehensive numerology analysis:
 1. Core Numbers: Life Path, Destiny/Expression, Soul Urge, Personality,
    Birthday, Maturity, Karmic Debt, Master Numbers
 2. Loshu Grid (Lo Shu Magic Square) with planes & arrows analysis
 3. Name correction suggestions
 4. Mobile number analysis & correction
 5. Car/Vehicle number analysis
 6. Password numerology suggestions
 7. Detailed characteristics, behavior, personality per number
 8. Both Pythagorean & Chaldean systems
 9. Lucky colors, days, gems, compatible numbers
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple


# ═══════════════════════════════════════════════════════════════
# NUMBER MAPPINGS
# ═══════════════════════════════════════════════════════════════

# Pythagorean: A=1..I=9, J=1..R=9, S=1..Z=8
PYTHAGOREAN = {
    'A':1,'B':2,'C':3,'D':4,'E':5,'F':6,'G':7,'H':8,'I':9,
    'J':1,'K':2,'L':3,'M':4,'N':5,'O':6,'P':7,'Q':8,'R':9,
    'S':1,'T':2,'U':3,'V':4,'W':5,'X':6,'Y':7,'Z':8,
}

# Chaldean: ancient Babylonian system (no 9 assigned to any letter)
CHALDEAN = {
    'A':1,'B':2,'C':3,'D':4,'E':5,'F':8,'G':3,'H':5,'I':1,
    'J':1,'K':2,'L':3,'M':4,'N':5,'O':7,'P':8,'Q':1,'R':2,
    'S':3,'T':4,'U':6,'V':6,'W':6,'X':5,'Y':1,'Z':7,
}

VOWELS = set('AEIOU')

# Loshu Grid positions: digit → (row, col) in the 3×3 grid
# Standard Lo Shu:
#   4 | 9 | 2
#   3 | 5 | 7
#   8 | 1 | 6
LOSHU_POSITIONS = {
    4: (0, 0), 9: (0, 1), 2: (0, 2),
    3: (1, 0), 5: (1, 1), 7: (1, 2),
    8: (2, 0), 1: (2, 1), 6: (2, 2),
}

LOSHU_LAYOUT = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]

# Loshu Planes
LOSHU_PLANES = {
    "mental":       {"numbers": [4, 9, 2], "name": "Mental Plane (Top Row)",
                     "desc": "Thinking, imagination, memory, analysis. Strong = sharp mind."},
    "emotional":    {"numbers": [3, 5, 7], "name": "Emotional Plane (Middle Row)",
                     "desc": "Feelings, intuition, sensitivity, spiritual depth. Strong = emotionally rich."},
    "practical":    {"numbers": [8, 1, 6], "name": "Practical Plane (Bottom Row)",
                     "desc": "Material world, organization, physical action. Strong = grounded & productive."},
    "thought":      {"numbers": [4, 3, 8], "name": "Thought Plane (Left Column)",
                     "desc": "Ideas, planning, creation. Strong = creative thinker."},
    "will":         {"numbers": [9, 5, 1], "name": "Will Plane (Center Column)",
                     "desc": "Determination, perseverance, drive. Strong = strong willpower."},
    "action":       {"numbers": [2, 7, 6], "name": "Action Plane (Right Column)",
                     "desc": "Implementation, results, finishing. Strong = gets things done."},
    "mind_spirit":  {"numbers": [4, 5, 6], "name": "Mind-Spirit Diagonal",
                     "desc": "Balance of intellect and spirit. Strong = wisdom."},
    "matter_soul":  {"numbers": [2, 5, 8], "name": "Matter-Soul Diagonal",
                     "desc": "Material success with emotional depth. Strong = prosperity."},
}

# Loshu Arrows (3 consecutive numbers present)
LOSHU_ARROWS = {
    "determination": {"numbers": [1, 5, 9], "type": "success",
                      "desc": "Arrow of Determination — Extremely strong willpower, never gives up. Natural leader."},
    "spirituality":  {"numbers": [3, 5, 7], "type": "success",
                      "desc": "Arrow of Spirituality — Deep inner peace, intuition, and spiritual connection."},
    "intellect":     {"numbers": [4, 9, 2], "type": "success",
                      "desc": "Arrow of Intellect — Brilliant mind, good memory, sharp thinking."},
    "emotional_balance": {"numbers": [2, 5, 8], "type": "success",
                          "desc": "Arrow of Emotional Balance — Strong emotional core, good judgment."},
    "prosperity":    {"numbers": [8, 1, 6], "type": "success",
                      "desc": "Arrow of Prosperity — Material success, practical ability, financial security."},
    "planner":       {"numbers": [4, 3, 8], "type": "success",
                      "desc": "Arrow of the Planner — Excellent at organizing, creating plans, systematic thinking."},
    "activity":      {"numbers": [2, 7, 6], "type": "success",
                      "desc": "Arrow of Activity — Energetic, action-oriented, always doing."},

    # Arrows of weakness (all 3 numbers MISSING)
    "frustration":   {"numbers": [1, 5, 9], "type": "weakness",
                      "desc": "Arrow of Frustration — Lacks determination, gives up easily. Needs motivation."},
    "skepticism":    {"numbers": [3, 5, 7], "type": "weakness",
                      "desc": "Arrow of Skepticism — Struggles with faith and intuition. Needs proof for everything."},
    "poor_memory":   {"numbers": [4, 9, 2], "type": "weakness",
                      "desc": "Arrow of Poor Memory — Forgetfulness, scattered thinking, needs notes."},
    "sensitivity":   {"numbers": [2, 5, 8], "type": "weakness",
                      "desc": "Arrow of Hypersensitivity — Emotionally fragile, takes things personally."},
    "struggle":      {"numbers": [8, 1, 6], "type": "weakness",
                      "desc": "Arrow of Struggle — Financial difficulties, material insecurity."},
    "confusion":     {"numbers": [4, 3, 8], "type": "weakness",
                      "desc": "Arrow of Confusion — Disorganized thinking, poor planning."},
    "passivity":     {"numbers": [2, 7, 6], "type": "weakness",
                      "desc": "Arrow of Passivity — Low energy, procrastination, avoids action."},
}


# ═══════════════════════════════════════════════════════════════
# NUMBER CHARACTERISTICS (1-9 + Master 11, 22, 33)
# ═══════════════════════════════════════════════════════════════

NUMBER_CHARACTERISTICS = {
    1: {
        "ruler": "Sun",
        "element": "Fire",
        "traits": "Leadership, independence, ambition, originality, pioneering spirit",
        "strengths": "Natural leader, innovative, courageous, self-reliant, determined",
        "weaknesses": "Ego, stubbornness, impatience, domineering, isolation",
        "career": "CEO, entrepreneur, politician, military, inventor, freelancer",
        "personality": "Born leaders who prefer to forge their own path. They are original thinkers with a strong desire for independence. Confident, ambitious, and creative. Can be headstrong and prefer to work alone. Natural pioneers who inspire others.",
        "behavior": "Authoritative, direct, decisive. Dislikes taking orders. First to start things. Self-motivated, sometimes lonely. Gets restless in routine jobs.",
        "lucky_colors": ["Red", "Gold", "Orange", "Yellow"],
        "lucky_days": ["Sunday", "Monday"],
        "lucky_gems": ["Ruby", "Garnet"],
        "compatible": [1, 2, 3, 9],
        "incompatible": [6, 8],
        "vedic_deity": "Surya (Sun God)",
        "health": "Heart, eyes, blood circulation. Should avoid overwork and stress.",
        "best_dates": [1, 10, 19, 28],
    },
    2: {
        "ruler": "Moon",
        "element": "Water",
        "traits": "Diplomacy, sensitivity, cooperation, intuition, partnership",
        "strengths": "Peacemaker, tactful, patient, supportive, detail-oriented, empathetic",
        "weaknesses": "Over-sensitive, indecisive, shy, moody, dependent, easily hurt",
        "career": "Counselor, diplomat, mediator, artist, musician, healer, partner roles",
        "personality": "Gentle souls who thrive in harmony. Extremely intuitive and sensitive to others' feelings. Natural mediators who avoid conflict. Deeply emotional and imaginative. Work best in pairs or supportive roles.",
        "behavior": "Soft-spoken, emotional, accommodating. Avoids confrontation. Mood swings with lunar cycles. Needs emotional security. Very loyal in relationships.",
        "lucky_colors": ["White", "Cream", "Silver", "Light Green"],
        "lucky_days": ["Monday", "Friday"],
        "lucky_gems": ["Pearl", "Moonstone"],
        "compatible": [1, 2, 7, 9],
        "incompatible": [4, 8],
        "vedic_deity": "Chandra (Moon God)",
        "health": "Stomach, digestion, mental health. Prone to anxiety and water retention.",
        "best_dates": [2, 11, 20, 29],
    },
    3: {
        "ruler": "Jupiter",
        "element": "Fire",
        "traits": "Creativity, expression, optimism, joy, social charm, communication",
        "strengths": "Creative, expressive, charismatic, optimistic, talented, inspirational",
        "weaknesses": "Scattered energy, superficial, extravagant, gossip, ego, moody",
        "career": "Writer, artist, actor, teacher, motivational speaker, advertising, media",
        "personality": "The life of the party — creative, expressive, and magnetic. Natural entertainers who bring joy. Gifted with words and imagination. Can be scattered but incredibly talented. Attract attention effortlessly.",
        "behavior": "Talkative, cheerful, dramatic. Loves being center of attention. Generous but can overspend. Artistic temperament. Gets bored easily without stimulation.",
        "lucky_colors": ["Yellow", "Purple", "Violet", "Mauve"],
        "lucky_days": ["Thursday", "Wednesday"],
        "lucky_gems": ["Yellow Sapphire", "Amethyst", "Topaz"],
        "compatible": [1, 3, 5, 6, 9],
        "incompatible": [4, 8],
        "vedic_deity": "Brihaspati (Jupiter/Guru)",
        "health": "Liver, skin, nervous system. Prone to overindulgence.",
        "best_dates": [3, 12, 21, 30],
    },
    4: {
        "ruler": "Rahu (Vedic) / Uranus (Western)",
        "element": "Earth",
        "traits": "Stability, hard work, discipline, structure, unconventionality",
        "strengths": "Systematic, reliable, hardworking, practical, patient, builder",
        "weaknesses": "Rigid, stubborn, pessimistic, workaholic, resistant to change, rebellious",
        "career": "Engineer, architect, accountant, IT, real estate, builder, researcher",
        "personality": "Hardworking builders who create lasting foundations. Think differently from the crowd. Disciplined yet unconventional in approach. May face more obstacles than others but persevere. Strong sense of duty and responsibility.",
        "behavior": "Methodical, disciplined, serious. Questions authority. Often feels like an outsider. Works extremely hard but may struggle for recognition. Sudden unexpected changes in life.",
        "lucky_colors": ["Blue", "Grey", "Khaki", "Electric Blue"],
        "lucky_days": ["Saturday", "Sunday"],
        "lucky_gems": ["Hessonite (Gomed)", "Blue Sapphire"],
        "compatible": [1, 4, 5, 7],
        "incompatible": [2, 3, 6, 9],
        "vedic_deity": "Rahu (North Node)",
        "health": "Back pain, depression, unusual ailments. Prone to stress-related issues.",
        "best_dates": [4, 13, 22, 31],
    },
    5: {
        "ruler": "Mercury",
        "element": "Air",
        "traits": "Freedom, adaptability, curiosity, versatility, adventure, wit",
        "strengths": "Quick thinker, adaptable, communicative, magnetic, resourceful, versatile",
        "weaknesses": "Restless, inconsistent, impulsive, overindulgent, scattered, nervous",
        "career": "Sales, marketing, travel, media, trading, astrology, public relations",
        "personality": "The adventurer and communicator. Quick-witted, charming, and always on the move. Loves variety and hates routine. Natural salesperson. Can talk their way into or out of anything. Multi-talented jack of all trades.",
        "behavior": "Energetic, curious, changeable. Needs constant stimulation. Excellent with money and business. Loves travel and new experiences. Flirtatious and social.",
        "lucky_colors": ["Green", "Light Grey", "White"],
        "lucky_days": ["Wednesday", "Friday"],
        "lucky_gems": ["Emerald", "Green Tourmaline"],
        "compatible": [1, 3, 5, 6, 7, 9],
        "incompatible": [2, 4],
        "vedic_deity": "Budha (Mercury)",
        "health": "Nerves, lungs, hands. Prone to anxiety, insomnia, overthinking.",
        "best_dates": [5, 14, 23],
    },
    6: {
        "ruler": "Venus",
        "element": "Earth",
        "traits": "Love, beauty, harmony, responsibility, nurturing, domesticity",
        "strengths": "Loving, responsible, artistic, nurturing, loyal, magnetic, harmonious",
        "weaknesses": "Worry, possessiveness, jealousy, self-sacrificing, controlling, vanity",
        "career": "Fashion, beauty, interior design, hospitality, counseling, luxury goods, film",
        "personality": "The nurturer and lover of beauty. Drawn to harmony, art, and family. Takes responsibility for others. Magnetic and attractive. Has refined taste and love for luxury. Most loving and caring of all numbers.",
        "behavior": "Warm, caring, protective of family. Loves beauty and comfort. Romantic and devoted. Can be possessive. Worries about loved ones excessively. Excellent host.",
        "lucky_colors": ["Pink", "Blue", "White", "Turquoise"],
        "lucky_days": ["Friday", "Wednesday"],
        "lucky_gems": ["Diamond", "Opal", "White Sapphire"],
        "compatible": [3, 5, 6, 9],
        "incompatible": [1, 4, 8],
        "vedic_deity": "Shukra (Venus)",
        "health": "Throat, kidneys, reproductive system. Loves food — weight issues.",
        "best_dates": [6, 15, 24],
    },
    7: {
        "ruler": "Ketu (Vedic) / Neptune (Western)",
        "element": "Water",
        "traits": "Spirituality, introspection, analysis, wisdom, mystery, research",
        "strengths": "Analytical, spiritual, intuitive, intellectual, independent thinker, researcher",
        "weaknesses": "Aloof, secretive, skeptical, isolated, pessimistic, escapist",
        "career": "Researcher, scientist, philosopher, occultist, astrologer, healer, writer",
        "personality": "The seeker and mystic. Deep thinkers who question everything. Naturally drawn to spirituality and hidden knowledge. Prefer solitude over crowds. Highly intuitive and often psychic. The most spiritual number.",
        "behavior": "Reserved, introspective, private. Needs alone time. Questions conventional wisdom. Drawn to metaphysics and occult. Dreams are often prophetic. Uncomfortable in large groups.",
        "lucky_colors": ["White", "Light Yellow", "Light Green", "Grey"],
        "lucky_days": ["Monday", "Sunday"],
        "lucky_gems": ["Cat's Eye (Lehsuniya)", "Moonstone"],
        "compatible": [2, 4, 5, 7],
        "incompatible": [1, 8, 9],
        "vedic_deity": "Ketu (South Node)",
        "health": "Nervous system, skin, psychosomatic issues. Prone to mysterious ailments.",
        "best_dates": [7, 16, 25],
    },
    8: {
        "ruler": "Saturn",
        "element": "Earth",
        "traits": "Power, authority, karma, material success, discipline, ambition",
        "strengths": "Powerful, ambitious, authoritative, excellent judgment, business mind, resilient",
        "weaknesses": "Ruthless, materialistic, workaholic, lonely, controlling, karmic delays",
        "career": "Finance, banking, law, real estate, politics, corporate leadership, judge",
        "personality": "The powerhouse. Born for material achievement and authority. Life is a series of karmic lessons — struggles early but achieves greatly. Understands money and power. Either very rich or faces severe financial tests. Commanding presence.",
        "behavior": "Serious, ambitious, commanding. Attracts both wealth and obstacles. Late bloomer — success comes after 35. Judges people quickly. Respects hierarchy but aims for the top. Strong sense of justice.",
        "lucky_colors": ["Black", "Dark Blue", "Dark Grey", "Purple"],
        "lucky_days": ["Saturday", "Thursday"],
        "lucky_gems": ["Blue Sapphire (Neelam)", "Amethyst"],
        "compatible": [4, 8],
        "incompatible": [1, 2, 3, 5, 6, 9],
        "vedic_deity": "Shani (Saturn)",
        "health": "Bones, joints, teeth, chronic conditions. Prone to depression and fatigue.",
        "best_dates": [8, 17, 26],
    },
    9: {
        "ruler": "Mars",
        "element": "Fire",
        "traits": "Compassion, courage, universal love, completion, warrior spirit, selflessness",
        "strengths": "Courageous, compassionate, generous, visionary, magnetic, humanitarian",
        "weaknesses": "Aggressive, impulsive, impatient, temperamental, egotistical, possessive",
        "career": "Military, sports, surgery, social work, firefighter, activist, martial arts",
        "personality": "The warrior-humanitarian. Fiery, passionate, and generous. Fights for the underdog. Natural athlete and leader. Life is about giving back. Most selfless number when evolved. Intense in everything they do.",
        "behavior": "Bold, direct, passionate. Quick to anger, quick to forgive. Generous to a fault. Competitive and athletic. Protective of loved ones. Drawn to causes larger than themselves.",
        "lucky_colors": ["Red", "Scarlet", "Crimson", "Pink"],
        "lucky_days": ["Tuesday", "Thursday"],
        "lucky_gems": ["Red Coral (Moonga)", "Garnet", "Bloodstone"],
        "compatible": [1, 2, 3, 5, 6, 9],
        "incompatible": [4, 7, 8],
        "vedic_deity": "Mangal (Mars)",
        "health": "Head, blood, muscles, accidents. Prone to fevers and injuries.",
        "best_dates": [9, 18, 27],
    },
    11: {
        "ruler": "Moon (Amplified)",
        "element": "Air/Spirit",
        "traits": "Master Intuition, spiritual illumination, visionary, inspiration, enlightenment",
        "strengths": "Highly intuitive, visionary, inspirational, idealistic, inventive, spiritual leader",
        "weaknesses": "Nervous energy, anxiety, self-doubt, impractical, inner tension, overwhelm",
        "career": "Spiritual teacher, psychic, inventor, inspirational speaker, artist, diplomat",
        "personality": "MASTER NUMBER — The Illuminator. Possesses extraordinary intuition and spiritual insight. Channel for higher wisdom. Can inspire millions. Lives between the spiritual and material worlds. Immense potential but heavy karmic responsibility.",
        "behavior": "Idealistic, nervous energy, inspiring. Lives with constant inner tension between 11 and 2. Highly sensitive to energies. Often feels 'different' from childhood. Can be a spiritual beacon or crippled by anxiety.",
        "lucky_colors": ["Silver", "White", "Violet"],
        "lucky_days": ["Monday", "Sunday"],
        "lucky_gems": ["Pearl", "Moonstone", "White Opal"],
        "compatible": [2, 4, 6, 8, 11, 22],
        "incompatible": [5, 9],
        "vedic_deity": "Chandra (Moon) — elevated consciousness",
        "health": "Extreme nervous system sensitivity. Must guard against anxiety and depression.",
        "best_dates": [2, 11, 20, 29],
    },
    22: {
        "ruler": "Rahu (Amplified)",
        "element": "Earth/Spirit",
        "traits": "Master Builder, manifesting dreams into reality, large-scale achievement",
        "strengths": "Visionary builder, turns impossible into possible, massive practical achievement, global impact",
        "weaknesses": "Overwhelming pressure, workaholism, manipulation, enormous self-doubt",
        "career": "Architect, global leader, nation builder, infrastructure, UN/NGO leadership",
        "personality": "MASTER NUMBER — The Master Builder. Can turn the grandest vision into concrete reality. The most powerful number in numerology. Combines spiritual vision (11) with practical mastery (4). Destined for massive achievement but carries immense karmic weight.",
        "behavior": "Thinks in terms of legacy and large-scale impact. Tireless worker on a mission. Either achieves the extraordinary or crumbles under the pressure. Carries the weight of destiny.",
        "lucky_colors": ["Red", "Gold", "Cream"],
        "lucky_days": ["Saturday", "Sunday"],
        "lucky_gems": ["Hessonite", "Red Coral"],
        "compatible": [4, 6, 8, 11, 22, 33],
        "incompatible": [3, 5],
        "vedic_deity": "Rahu — destiny force",
        "health": "Chronic stress, burnout, nervous breakdown risk. Must rest.",
        "best_dates": [4, 13, 22, 31],
    },
    33: {
        "ruler": "Jupiter (Amplified)",
        "element": "Fire/Spirit",
        "traits": "Master Teacher, cosmic compassion, selfless service, healing",
        "strengths": "Profound healer, utterly selfless, master communicator, cosmic love, uplifts all",
        "weaknesses": "Martyrdom, self-neglect, emotional burden, unrealistic idealism",
        "career": "Spiritual healer, guru, humanitarian leader, teacher of teachers",
        "personality": "MASTER NUMBER — The Master Teacher. Rarest and most spiritually evolved number. Embodies unconditional love and cosmic compassion. Born to heal and teach. Operates at the highest vibration possible. Life is pure service.",
        "behavior": "Radiates warmth and healing energy. Attracts those in need. Puts everyone before self. May suffer greatly to transmute karma for others. The living embodiment of compassion.",
        "lucky_colors": ["Violet", "Rose", "Turquoise"],
        "lucky_days": ["Thursday", "Monday"],
        "lucky_gems": ["Yellow Sapphire", "Amethyst", "Rose Quartz"],
        "compatible": [3, 6, 9, 22, 33],
        "incompatible": [1, 8],
        "vedic_deity": "Brihaspati — supreme guru",
        "health": "Heart, emotional exhaustion. Must learn self-care.",
        "best_dates": [3, 6, 12, 21, 30],
    },
}

# Karmic Debt numbers
KARMIC_DEBT_NUMBERS = {
    13: "Karmic Debt 13 — Laziness in past life. Must work hard this life. Temptation to take shortcuts. Success comes only through sustained effort and focus.",
    14: "Karmic Debt 14 — Abuse of freedom in past life. Must learn moderation and commitment. Prone to addictions and excess. Freedom comes through discipline.",
    16: "Karmic Debt 16 — Ego and vanity in past life. Will face ego-shattering events. Tower moment of destruction and rebuilding. Spiritual rebirth through humility.",
    19: "Karmic Debt 19 — Selfishness in past life. Must learn to help others. Self-reliance is a strength but isolation is the trap. Success through service.",
}


# ═══════════════════════════════════════════════════════════════
# CORE CALCULATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def _digit_sum(n: int) -> int:
    """Sum digits of a number."""
    s = 0
    n = abs(n)
    while n > 0:
        s += n % 10
        n //= 10
    return s


def reduce_to_single(n: int, keep_master: bool = True) -> int:
    """Reduce number to single digit, optionally keeping master numbers 11, 22, 33."""
    while n > 9:
        if keep_master and n in (11, 22, 33):
            return n
        n = _digit_sum(n)
    return n


def _sum_digits_of_string(s: str) -> int:
    """Sum all digits in a string."""
    return sum(int(ch) for ch in s if ch.isdigit())


def _get_dob_digits(date_str: str) -> List[int]:
    """Extract all individual digits from a date string (DD-MM-YYYY or YYYY-MM-DD)."""
    return [int(ch) for ch in date_str if ch.isdigit()]


def _parse_dob(date_str: str) -> Tuple[int, int, int]:
    """Parse DOB string → (day, month, year). Supports DD-MM-YYYY, YYYY-MM-DD, DD/MM/YYYY."""
    date_str = date_str.strip()
    parts = None
    for sep in ('-', '/'):
        if sep in date_str:
            parts = date_str.split(sep)
            break
    if not parts or len(parts) != 3:
        raise ValueError(f"Invalid DOB format: {date_str}")
    a, b, c = [int(p) for p in parts]
    if a > 31:  # YYYY-MM-DD
        return c, b, a
    return a, b, c  # DD-MM-YYYY


# ═══════════════════════════════════════════════════════════════
# NUMEROLOGY CORE NUMBERS
# ═══════════════════════════════════════════════════════════════

def calc_life_path(day: int, month: int, year: int) -> Dict:
    """
    Life Path Number — most important number in numerology.
    Method: Reduce day, month, year separately, then sum & reduce.
    Also track if intermediate sum is a karmic debt number.
    """
    d = reduce_to_single(day, keep_master=True)
    m = reduce_to_single(month, keep_master=True)
    # Year: sum all digits first
    y_sum = _digit_sum(year)
    y = reduce_to_single(y_sum, keep_master=True)

    total = d + m + y
    # Check karmic debt before final reduction
    karmic = None
    if total in KARMIC_DEBT_NUMBERS:
        karmic = KARMIC_DEBT_NUMBERS[total]
    # Also check if the two-digit number before reduction is karmic
    temp = total
    while temp > 9 and temp not in (11, 22, 33):
        if temp in KARMIC_DEBT_NUMBERS:
            karmic = KARMIC_DEBT_NUMBERS[temp]
        temp = _digit_sum(temp)

    life_path = reduce_to_single(total, keep_master=True)

    return {
        "number": life_path,
        "calculation": f"Day({day}→{d}) + Month({month}→{m}) + Year({year}→{y}) = {d+m+y} → {life_path}",
        "karmic_debt": karmic,
        "is_master": life_path in (11, 22, 33),
    }


def calc_birthday_number(day: int) -> Dict:
    """Birthday Number — your natural talent and gift."""
    raw = day
    reduced = reduce_to_single(day, keep_master=True)
    return {
        "number": reduced,
        "raw_day": raw,
        "calculation": f"Birth day {raw} → {reduced}",
    }


def calc_name_number(name: str, system: str = "pythagorean") -> Dict:
    """
    Destiny/Expression Number — from full name.
    Also calculates Soul Urge (vowels) and Personality (consonants).
    """
    mapping = PYTHAGOREAN if system == "pythagorean" else CHALDEAN
    name_upper = name.upper().strip()

    total = 0
    vowel_total = 0
    consonant_total = 0
    letter_values = []

    for ch in name_upper:
        if ch.isalpha():
            val = mapping.get(ch, 0)
            letter_values.append({"letter": ch, "value": val})
            total += val
            if ch in VOWELS:
                vowel_total += val
            else:
                consonant_total += val

    destiny = reduce_to_single(total, keep_master=True)
    soul_urge = reduce_to_single(vowel_total, keep_master=True)
    personality = reduce_to_single(consonant_total, keep_master=True)

    # Check karmic debt in destiny
    karmic = None
    temp = total
    while temp > 9 and temp not in (11, 22, 33):
        if temp in KARMIC_DEBT_NUMBERS:
            karmic = KARMIC_DEBT_NUMBERS[temp]
        temp = _digit_sum(temp)

    return {
        "system": system,
        "name": name,
        "destiny_number": destiny,
        "destiny_total": total,
        "soul_urge_number": soul_urge,
        "soul_urge_total": vowel_total,
        "personality_number": personality,
        "personality_total": consonant_total,
        "letter_values": letter_values,
        "karmic_debt": karmic,
        "calculation": f"Total={total}→{destiny}, Vowels={vowel_total}→{soul_urge}, Consonants={consonant_total}→{personality}",
    }


def calc_maturity_number(life_path: int, destiny: int) -> Dict:
    """Maturity Number = Life Path + Destiny, reduced."""
    total = life_path + destiny
    maturity = reduce_to_single(total, keep_master=True)
    return {
        "number": maturity,
        "calculation": f"Life Path({life_path}) + Destiny({destiny}) = {total} → {maturity}",
        "meaning": "This energy activates after age 35-40 and represents your mature self.",
    }


# ═══════════════════════════════════════════════════════════════
# LOSHU GRID
# ═══════════════════════════════════════════════════════════════

def calc_loshu_grid(day: int, month: int, year: int) -> Dict:
    """
    Build the Loshu Grid from DOB using the traditional Chinese method.

    Three sets of numbers are placed in the grid:
    1. All individual digits of DOB (zeros excluded)
    2. Driver Number (Moolank) — birth day reduced to single digit
    3. Conductor Number (Bhagyank/Life Path) — full DOB sum reduced to single digit

    Example: DOB 23-09-1992
      DOB digits: 2, 3, 9, 1, 9, 9, 2 (zeros excluded)
      Driver: 2+3 = 5
      Conductor: 2+3+0+9+1+9+9+2 = 35 → 3+5 = 8
      Grid uses: 2, 3, 9, 1, 9, 9, 2, 5, 8
    """
    # 1. All individual digits from DOB (zeros excluded)
    dob_str = f"{day:02d}{month:02d}{year}"
    dob_digits = [int(ch) for ch in dob_str if ch.isdigit() and ch != '0']

    # 2. Driver Number (Moolank) — birth day reduced to single digit
    driver = reduce_to_single(day, keep_master=False)

    # 3. Conductor Number (Bhagyank/Life Path) — full DOB digit sum reduced
    full_sum = sum(int(ch) for ch in dob_str if ch.isdigit())
    conductor = reduce_to_single(full_sum, keep_master=False)

    # Combine all three sets
    all_digits = dob_digits[:]
    if driver != 0:
        all_digits.append(driver)
    if conductor != 0:
        all_digits.append(conductor)

    # Count occurrences
    counts = {}
    for d in range(1, 10):
        counts[d] = all_digits.count(d)

    # Build grid with counts
    grid = []
    for row in LOSHU_LAYOUT:
        grid_row = []
        for num in row:
            grid_row.append({
                "number": num,
                "count": counts[num],
                "present": counts[num] > 0,
                "repeated": counts[num] > 1,
            })
        grid.append(grid_row)

    # Present and missing numbers
    present = sorted([d for d in range(1, 10) if counts[d] > 0])
    missing = sorted([d for d in range(1, 10) if counts[d] == 0])
    repeated = {d: counts[d] for d in range(1, 10) if counts[d] > 1}

    # Analyze planes
    planes = []
    for key, plane in LOSHU_PLANES.items():
        nums = plane["numbers"]
        present_in_plane = [n for n in nums if counts[n] > 0]
        total_count = sum(counts[n] for n in nums)
        strength = "empty" if len(present_in_plane) == 0 else \
                   "weak" if len(present_in_plane) == 1 else \
                   "moderate" if len(present_in_plane) == 2 else "strong"
        planes.append({
            "key": key,
            "name": plane["name"],
            "desc": plane["desc"],
            "numbers": nums,
            "present_count": len(present_in_plane),
            "total_digit_count": total_count,
            "strength": strength,
        })

    # Analyze arrows
    arrows_found = []
    for key, arrow in LOSHU_ARROWS.items():
        nums = arrow["numbers"]
        all_present = all(counts[n] > 0 for n in nums)
        all_missing = all(counts[n] == 0 for n in nums)

        if arrow["type"] == "success" and all_present:
            arrows_found.append({
                "key": key,
                "type": "strength",
                "desc": arrow["desc"],
                "numbers": nums,
            })
        elif arrow["type"] == "weakness" and all_missing:
            arrows_found.append({
                "key": key,
                "type": "weakness",
                "desc": arrow["desc"],
                "numbers": nums,
            })

    # Repeated number meanings
    repeated_meanings = {}
    REPEAT_MEANING = {
        1: {2: "Double confidence and independence", 3: "Extreme self-focus, needs balance", 4: "Overpowering ego"},
        2: {2: "Heightened sensitivity and intuition", 3: "Over-emotional, hypersensitive", 4: "Emotional overload"},
        3: {2: "Strong imagination and creativity", 3: "Scattered creative energy", 4: "Living in fantasy"},
        4: {2: "Very methodical and organized", 3: "Excessive rigidity, inflexible"},
        5: {2: "Extremely versatile and free-spirited", 3: "Excessive restlessness"},
        6: {2: "Very caring and nurturing", 3: "Worrying too much about others", 4: "Possessive love"},
        7: {2: "Deep spiritual seeker", 3: "Extreme isolation tendency"},
        8: {2: "Strong material ambition", 3: "Obsession with money/power"},
        9: {2: "Very generous and compassionate", 3: "Idealistic to the point of impractical", 4: "Extreme selflessness"},
    }
    for d, cnt in repeated.items():
        if d in REPEAT_MEANING and cnt in REPEAT_MEANING[d]:
            repeated_meanings[d] = {"count": cnt, "meaning": REPEAT_MEANING[d][cnt]}
        elif d in REPEAT_MEANING:
            max_key = max(REPEAT_MEANING[d].keys())
            if cnt > max_key:
                repeated_meanings[d] = {"count": cnt, "meaning": REPEAT_MEANING[d][max_key] + f" (×{cnt} — extremely amplified)"}

    return {
        "dob_raw_digits": dob_digits,
        "driver_number": driver,
        "conductor_number": conductor,
        "all_digits": all_digits,
        "grid": grid,
        "counts": counts,
        "present_numbers": present,
        "missing_numbers": missing,
        "repeated_numbers": repeated,
        "repeated_meanings": repeated_meanings,
        "planes": planes,
        "arrows": arrows_found,
        "missing_remedies": _missing_number_remedies(missing),
    }


def _missing_number_remedies(missing: List[int]) -> List[Dict]:
    """Suggest remedies for missing numbers in Loshu grid."""
    REMEDIES = {
        1: {"remedy": "Wear Ruby or Garnet. Chant Surya mantra. Develop self-confidence. Practice leadership.", "color": "Red"},
        2: {"remedy": "Wear Pearl or Moonstone. Chant Chandra mantra. Practice patience and cooperation.", "color": "White"},
        3: {"remedy": "Wear Yellow Sapphire. Chant Guru mantra. Take up creative hobbies. Express yourself.", "color": "Yellow"},
        4: {"remedy": "Wear Hessonite. Practice discipline and organization. Create routines.", "color": "Blue-Grey"},
        5: {"remedy": "Wear Emerald. Travel more. Learn new skills. Embrace change.", "color": "Green"},
        6: {"remedy": "Wear Diamond or White Sapphire. Focus on relationships. Beautify surroundings.", "color": "Pink/Blue"},
        7: {"remedy": "Wear Cat's Eye. Meditate daily. Study spiritual texts. Spend time in nature.", "color": "Grey/White"},
        8: {"remedy": "Wear Blue Sapphire (carefully). Practice financial discipline. Set long-term goals.", "color": "Black/Dark Blue"},
        9: {"remedy": "Wear Red Coral. Practice generosity. Exercise regularly. Channel aggression into sports.", "color": "Red/Scarlet"},
    }
    return [{"number": n, **REMEDIES[n]} for n in missing if n in REMEDIES]


# ═══════════════════════════════════════════════════════════════
# NAME CORRECTION
# ═══════════════════════════════════════════════════════════════

def suggest_name_correction(name: str, life_path: int, system: str = "chaldean") -> Dict:
    """
    Analyze current name number vs life path compatibility.
    Suggest letter additions/changes to make the name number
    compatible with the life path number.
    """
    mapping = PYTHAGOREAN if system == "pythagorean" else CHALDEAN
    name_data = calc_name_number(name, system)
    current_destiny = name_data["destiny_number"]

    # Compatibility chart: which name numbers are good for which life paths
    COMPATIBLE_NAME_NUMBERS = {
        1: [1, 2, 3, 5, 9],
        2: [1, 2, 3, 6, 9],
        3: [1, 3, 5, 6, 9],
        4: [1, 4, 5, 6, 7],
        5: [1, 3, 5, 6, 9],
        6: [1, 3, 5, 6, 9],
        7: [2, 4, 5, 7],
        8: [1, 4, 5, 8],
        9: [1, 2, 3, 5, 6, 9],
        11: [2, 3, 6, 9, 11],
        22: [4, 6, 8, 22],
        33: [3, 6, 9, 33],
    }

    lp_key = life_path if life_path in COMPATIBLE_NAME_NUMBERS else reduce_to_single(life_path, False)
    good_numbers = COMPATIBLE_NAME_NUMBERS.get(lp_key, [1, 5, 6, 9])

    is_compatible = current_destiny in good_numbers
    target_numbers = good_numbers if not is_compatible else [current_destiny]

    # Generate suggestions by adding/changing letters
    suggestions = []
    if not is_compatible:
        for target in target_numbers:
            diff = target - reduce_to_single(name_data["destiny_total"] % 9 or 9, False)
            if diff <= 0:
                diff += 9
            # Find letters that have this value
            letters_for_val = [ch for ch, val in mapping.items() if val == diff]
            if letters_for_val:
                suggestions.append({
                    "target_number": target,
                    "action": f"Add letter '{letters_for_val[0]}' (value {diff}) to make name number {target}",
                    "letters": letters_for_val,
                    "value_needed": diff,
                })

        # Suggest spelling variations
        name_upper = name.upper()
        spelling_suggestions = []
        for target in target_numbers:
            current_total = name_data["destiny_total"]
            # Try adding common letters
            for letter in "AEIOULNRS":
                new_total = current_total + mapping[letter]
                new_reduced = reduce_to_single(new_total, keep_master=True)
                if new_reduced == target:
                    spelling_suggestions.append({
                        "modified_name": name + letter.lower(),
                        "added_letter": letter,
                        "new_number": new_reduced,
                        "target": target,
                    })
            # Try doubling last letter
            if name_upper and name_upper[-1].isalpha():
                last = name_upper[-1]
                new_total = current_total + mapping.get(last, 0)
                new_reduced = reduce_to_single(new_total, keep_master=True)
                if new_reduced in target_numbers:
                    spelling_suggestions.append({
                        "modified_name": name + last.lower(),
                        "added_letter": last,
                        "new_number": new_reduced,
                        "target": new_reduced,
                    })
        suggestions_dedup = {}
        for s in spelling_suggestions:
            key = s["modified_name"].lower()
            if key not in suggestions_dedup:
                suggestions_dedup[key] = s
        spelling_suggestions = list(suggestions_dedup.values())[:10]
    else:
        spelling_suggestions = []

    return {
        "current_name": name,
        "system": system,
        "current_destiny_number": current_destiny,
        "life_path_number": life_path,
        "compatible_name_numbers": good_numbers,
        "is_compatible": is_compatible,
        "verdict": "Your name number is compatible with your life path!" if is_compatible
                   else f"Name number {current_destiny} is NOT ideal for life path {life_path}. Consider correction.",
        "suggestions": suggestions,
        "spelling_suggestions": spelling_suggestions,
    }


# ═══════════════════════════════════════════════════════════════
# MOBILE / CAR / PASSWORD ANALYSIS
# ═══════════════════════════════════════════════════════════════

def analyze_number_string(number_str: str, life_path: int, label: str = "Number") -> Dict:
    """
    Analyze any number string (mobile, car, etc.) for numerological compatibility.
    """
    # Clean the string
    clean = ''.join(ch for ch in number_str if ch.isdigit())
    if not clean:
        return {"error": f"No digits found in {label}"}

    digits = [int(ch) for ch in clean]
    total = sum(digits)
    reduced = reduce_to_single(total, keep_master=True)

    # Compound number meaning (two-digit before reduction)
    compound = total
    while compound > 99:
        compound = _digit_sum(compound)

    COMPOUND_MEANINGS = {
        10: "Wheel of Fortune — success, good luck, rise and fall",
        11: "Master Intuition — hidden dangers, anxiety but great potential",
        12: "Sacrifice — victim mentality or spiritual growth through suffering",
        13: "Transformation — death & rebirth, powerful change energy",
        14: "Movement — risk, speculation, travel, magnetic personality",
        15: "Magic — charisma, material comfort, occult abilities",
        16: "Tower — ego destruction, spiritual awakening through crisis",
        17: "Star — hope, fame, spiritual insight, immortality",
        18: "Moon — deception, hidden enemies, but also psychic ability",
        19: "Sun — success, happiness, achievement, honor",
        20: "Awakening — delays, then sudden transformation",
        21: "World — assured success, advancement, victory",
        22: "Master Builder — illusion or massive achievement",
        23: "Royal Star — success, help from superiors, protection",
        24: "Love & Money — favored by love and finances",
        25: "Strength through trial — wisdom gained from experience",
        26: "Partnerships — warnings about business partners and associates",
        27: "Command — authority, leadership, reward for courage",
        28: "Opposition — great promise, great loss, must be careful",
        29: "Grace under pressure — uncertainties, trust intuition",
        30: "Loner — intellectual, retrospective, powerful mind",
        31: "Isolation — similar to 30 but more lonely",
        32: "Communication — magnetic personality, good for marketing",
        33: "Master Teacher — cosmic responsibility, healing power",
        34: "Similar to 7 — innovation, creative approaches",
        35: "Similar to 8 — business success through unique methods",
        36: "Similar to 9 — humanitarian vision, creative expansion",
        37: "Divine friendship — good relationships, family love",
        38: "Similar to 11 — hard work under difficult conditions",
        39: "Similar to 3 — creativity with humanitarian goals",
        40: "Similar to 4 — organized, disciplined, systematic",
        41: "Similar to 5 — versatile, good for new ventures",
        42: "Similar to 6 — nurturing, domestic success",
        43: "Revolution — unfortunate, losses and reversals",
        44: "Similar to 8 — material success through effort",
        45: "Similar to 9 — aggressive pursuit of goals",
        46: "Similar to 1 — leadership through service",
        47: "Similar to 11 — spiritual seeking, partnerships",
        48: "Similar to 3 — counseling and teaching",
        49: "Similar to 4 — reform and transformation",
        50: "Similar to 5 — freedom, travel, communication",
        51: "Warrior — powerful, forceful, military energy",
        52: "Similar to 7 — mystic, magic number",
    }

    compound_meaning = COMPOUND_MEANINGS.get(compound, f"Compound {compound} — energy of {reduce_to_single(compound, False)}")

    # Compatibility with life path
    lp_single = life_path if life_path <= 9 else reduce_to_single(life_path, False)
    GOOD_COMBOS = {
        1: [1, 3, 5, 9], 2: [2, 6, 7, 9], 3: [1, 3, 5, 6, 9],
        4: [4, 5, 7, 8], 5: [1, 3, 5, 6, 9], 6: [2, 3, 5, 6, 9],
        7: [2, 4, 5, 7], 8: [4, 5, 8], 9: [1, 2, 3, 5, 6, 9],
    }
    good_for_lp = GOOD_COMBOS.get(lp_single, [1, 5, 9])
    reduced_single = reduced if reduced <= 9 else reduce_to_single(reduced, False)
    is_good = reduced_single in good_for_lp

    return {
        "label": label,
        "original": number_str,
        "clean_digits": clean,
        "digit_count": len(clean),
        "digit_sum": total,
        "compound_number": compound,
        "compound_meaning": compound_meaning,
        "final_number": reduced,
        "is_master": reduced in (11, 22, 33),
        "life_path": life_path,
        "compatible_with_life_path": is_good,
        "ideal_numbers_for_you": good_for_lp,
        "verdict": f"{'Excellent' if is_good else 'Not ideal'} for Life Path {life_path}. "
                   f"This {label.lower()} vibrates at {reduced}.",
        "calculation": f"Digits: {'+'.join(clean)} = {total} → {reduced}",
    }


def suggest_mobile_correction(current: str, life_path: int) -> Dict:
    """Suggest mobile numbers or changes for better compatibility."""
    analysis = analyze_number_string(current, life_path, "Mobile Number")

    lp_single = life_path if life_path <= 9 else reduce_to_single(life_path, False)
    GOOD_COMBOS = {
        1: [1, 3, 5, 9], 2: [2, 6, 7, 9], 3: [1, 3, 5, 6, 9],
        4: [4, 5, 7, 8], 5: [1, 3, 5, 6, 9], 6: [2, 3, 5, 6, 9],
        7: [2, 4, 5, 7], 8: [4, 5, 8], 9: [1, 2, 3, 5, 6, 9],
    }
    good_nums = GOOD_COMBOS.get(lp_single, [1, 5, 9])

    tips = []
    if not analysis["compatible_with_life_path"]:
        tips.append(f"Your mobile number reduces to {analysis['final_number']}, which is not ideal for Life Path {life_path}.")
        tips.append(f"Look for a number whose digits sum to one of: {good_nums}")
        tips.append("When choosing a new number, ensure the last 4 digits sum to a favorable single digit.")
        tips.append("If changing the full number isn't possible, you can set a favorable number as your screen lock PIN or secondary number.")
    else:
        tips.append(f"Your mobile number {analysis['final_number']} is compatible with Life Path {life_path}.")

    analysis["tips"] = tips
    analysis["favorable_total_digits"] = good_nums
    return analysis


def suggest_password(life_path: int, birthday: int, name: str) -> Dict:
    """
    Suggest password structures based on numerology.
    Not actual passwords — but numerological patterns for creating them.
    """
    lp_single = life_path if life_path <= 9 else reduce_to_single(life_path, False)

    LUCKY_NUMBERS = {
        1: [1, 10, 19, 28, 37, 46, 55], 2: [2, 11, 20, 29, 38, 47],
        3: [3, 12, 21, 30, 39, 48], 4: [4, 13, 22, 31, 40, 49],
        5: [5, 14, 23, 32, 41, 50], 6: [6, 15, 24, 33, 42, 51],
        7: [7, 16, 25, 34, 43, 52], 8: [8, 17, 26, 35, 44, 53],
        9: [9, 18, 27, 36, 45, 54],
    }

    lucky = LUCKY_NUMBERS.get(lp_single, [1, 5, 9])
    char_data = NUMBER_CHARACTERISTICS.get(lp_single, {})
    lucky_colors = char_data.get("lucky_colors", ["Blue"])

    # Password length suggestions
    good_lengths = [n for n in lucky if 8 <= n <= 20]
    if not good_lengths:
        good_lengths = [n for n in lucky if n >= 8]
    if not good_lengths:
        good_lengths = [12, 14, 16]  # safe defaults

    tips = [
        f"Ideal password length: {good_lengths[:3]} characters (your lucky numbers).",
        f"Include digits that sum to {lp_single} or {birthday if birthday <= 9 else reduce_to_single(birthday, False)}.",
        f"Use initials from your name '{name[:3]}' for personal connection.",
        f"Your lucky colors are {', '.join(lucky_colors[:2])} — can be part of password.",
        "Always mix uppercase, lowercase, numbers, and symbols for security.",
        f"Avoid numbers that reduce to {[n for n in range(1,10) if n not in char_data.get('compatible', [lp_single])]}.",
        f"Best digits to include: {char_data.get('best_dates', [lp_single])[:4]}",
    ]

    # Example pattern (not an actual password)
    patterns = [
        f"{name[:2].title()}@{lucky[0]:02d}#{lucky_colors[0][:3]}",
        f"{lucky_colors[0][:4]}${birthday:02d}!{name[:3].lower()}",
        f"{name[:3].title()}{birthday:02d}@{lp_single}!",
    ]

    return {
        "life_path": life_path,
        "birthday_number": birthday,
        "ideal_lengths": good_lengths[:5],
        "lucky_digits": [d for d in lucky if d < 10],
        "tips": tips,
        "example_patterns": patterns,
        "note": "These are pattern suggestions — always create your own unique secure password.",
    }


# ═══════════════════════════════════════════════════════════════
# PERSONAL YEAR / MONTH / DAY CYCLES
# ═══════════════════════════════════════════════════════════════

def calc_personal_cycles(day: int, month: int, year: int, current_year: int = 2026) -> Dict:
    """
    Calculate Personal Year, Month, and Day cycles.
    Personal Year = birth day + birth month + current year, reduced.
    """
    py_sum = reduce_to_single(day, False) + reduce_to_single(month, False) + reduce_to_single(_digit_sum(current_year), False)
    personal_year = reduce_to_single(py_sum, keep_master=True)

    PY_MEANINGS = {
        1: "New beginnings, independence, leadership. Start fresh projects. Plant seeds.",
        2: "Patience, partnerships, diplomacy. Wait. Let things grow. Cooperate.",
        3: "Creativity, expression, social expansion. Write, speak, create. Joy year.",
        4: "Hard work, foundation building, discipline. Build structures. No shortcuts.",
        5: "Change, freedom, adventure. Expect the unexpected. Travel. Adapt.",
        6: "Home, family, responsibility. Marriage, children, domestic duties. Nurture.",
        7: "Introspection, spirituality, rest. Study, meditate, research. Withdraw.",
        8: "Power, money, achievement. Harvest what you sowed. Financial decisions.",
        9: "Completion, release, endings. Let go of the old. Prepare for new cycle.",
        11: "Spiritual awakening, illumination. High-vibration year. Trust intuition.",
        22: "Master building, large-scale achievement. Build something that lasts.",
        33: "Master teaching, compassion. Serve humanity. Healing year.",
    }

    return {
        "current_year": current_year,
        "personal_year_number": personal_year,
        "calculation": f"Day({day}) + Month({month}) + Year({current_year}) reduced = {personal_year}",
        "meaning": PY_MEANINGS.get(personal_year, f"Energy of {personal_year}"),
        "cycle_position": f"Year {personal_year} of 9-year cycle",
    }


# ═══════════════════════════════════════════════════════════════
# RAJ YOGAS — Golden, Silver, and all Numerological Yogas
# ═══════════════════════════════════════════════════════════════

RAJ_YOGAS = {
    # ── GOLDEN RAJ YOGA (4-5-6 diagonal) ──
    "golden_raj_yoga": {
        "name": "Golden Raj Yoga (Suvarna Raj Yoga)",
        "numbers": [4, 5, 6],
        "type": "golden",
        "rarity": "2-3% of people",
        "desc": "The most powerful yoga in numerology. Brings extraordinary name, fame, wealth, and authority. The person is destined for greatness and commands respect naturally.",
        "career": "Top leadership, politics, royal/corporate authority, entrepreneurship at massive scale",
        "wealth": "Exceptional wealth accumulation. Midas touch for finances. Multi-source income.",
        "health": "Generally good vitality. Must guard against overwork and ego-related stress.",
        "relationships": "Attracts powerful partners. Marriage brings social elevation.",
    },
    # ── SILVER RAJ YOGA (2-5-8 diagonal) ──
    "silver_raj_yoga": {
        "name": "Silver Raj Yoga (Rajat Yoga / Property Yoga)",
        "numbers": [2, 5, 8],
        "type": "silver",
        "rarity": "5-7% of people",
        "desc": "The prosperity yoga. Blesses with property, real estate success, and material abundance. Person acquires own house early in life. Patient approach leads to great wealth.",
        "career": "Real estate, property dealing, construction, banking, material industries",
        "wealth": "Strong property accumulation. Success in land and real estate. Steady wealth growth.",
        "health": "Good stamina but may face bone/joint issues. Patient constitution.",
        "relationships": "Emotionally balanced partnerships. Material security in marriage.",
    },
    # ── DETERMINATION YOGA (1-5-9 center column) ──
    "determination_yoga": {
        "name": "Determination Yoga (Sankalp Yoga)",
        "numbers": [1, 5, 9],
        "type": "power",
        "rarity": "8-10% of people",
        "desc": "The willpower yoga. Gives incredible determination and never-give-up attitude. Person overcomes all obstacles through sheer will. Born fighter and leader.",
        "career": "Military, sports, politics, activism, entrepreneurship",
        "wealth": "Self-made wealth. Earns through determination and courage. Risk-taking pays off.",
        "health": "Strong physical constitution. High energy. Must manage anger and blood pressure.",
        "relationships": "Passionate but dominant. Needs equally strong partner.",
    },
    # ── INTELLECT YOGA (4-9-2 top row) ──
    "intellect_yoga": {
        "name": "Intellect Yoga (Buddhi Yoga)",
        "numbers": [4, 9, 2],
        "type": "mental",
        "rarity": "10-12% of people",
        "desc": "The thinking yoga. Sharp mind, excellent memory, brilliant analysis. Person excels in academic and intellectual pursuits. Deep analytical ability.",
        "career": "Research, science, academics, technology, consulting, analysis",
        "wealth": "Wealth through intellectual property, innovations, and patents.",
        "health": "Mental strain risk. Overthinking. Needs mental rest and nature time.",
        "relationships": "Intellectual connection is must. Needs mentally stimulating partner.",
    },
    # ── SPIRITUALITY YOGA (3-5-7 middle row) ──
    "spirituality_yoga": {
        "name": "Spirituality Yoga (Adhyatmik Yoga)",
        "numbers": [3, 5, 7],
        "type": "spiritual",
        "rarity": "7-9% of people",
        "desc": "The spiritual yoga. Deep inner peace, extraordinary intuition, psychic ability. Person is naturally drawn to occult, astrology, and healing. Inner knowing guides life.",
        "career": "Astrology, healing, counseling, spiritual teaching, meditation, occult sciences",
        "wealth": "Moderate material wealth. True riches are spiritual. May monetize spiritual gifts.",
        "health": "Sensitive constitution. Must protect from negative energies. Meditation is medicine.",
        "relationships": "Needs spiritually aware partner. Deep soul connections.",
    },
    # ── PROSPERITY YOGA (8-1-6 bottom row) ──
    "prosperity_yoga": {
        "name": "Prosperity Yoga (Dhan Yoga)",
        "numbers": [8, 1, 6],
        "type": "wealth",
        "rarity": "8-10% of people",
        "desc": "The material success yoga. Natural ability to create financial security. Practical, organized approach to wealth building. Steady and reliable prosperity.",
        "career": "Finance, banking, real estate, luxury goods, administration",
        "wealth": "Consistent wealth building. Good financial judgment. Multiple income streams.",
        "health": "Generally robust. May face lifestyle-related issues later in life.",
        "relationships": "Stable, secure partnerships. Provides well for family.",
    },
    # ── PLANNER YOGA (4-3-8 left column) ──
    "planner_yoga": {
        "name": "Planner Yoga (Yojana Yoga)",
        "numbers": [4, 3, 8],
        "type": "organizational",
        "rarity": "9-11% of people",
        "desc": "The organizer yoga. Exceptional planning ability, systematic thinking, project management mastery. Can create order from chaos and build complex systems.",
        "career": "Project management, architecture, engineering, systems design, consulting",
        "wealth": "Wealth through methodical planning. Long-term investment success.",
        "health": "Must avoid overthinking. Physical exercise essential to balance mental focus.",
        "relationships": "Structured approach to relationships. Reliable and dependable partner.",
    },
    # ── ACTIVITY YOGA (2-7-6 right column) ──
    "activity_yoga": {
        "name": "Activity Yoga (Kriya Yoga)",
        "numbers": [2, 7, 6],
        "type": "action",
        "rarity": "9-11% of people",
        "desc": "The action yoga. Energetic, productive, always accomplishing. Turns ideas into results. Natural doer who gets things done efficiently.",
        "career": "Operations, event management, logistics, sports, manufacturing",
        "wealth": "Wealth through action and productivity. Earns well from hands-on work.",
        "health": "High energy but risk of burnout. Needs scheduled rest.",
        "relationships": "Active, adventurous partnerships. Keeps the relationship dynamic.",
    },
}

# Driver-Conductor compatibility yogas
DRIVER_CONDUCTOR_YOGAS = {
    (1, 1): {"name": "Supreme Leader Yoga", "desc": "Double Sun energy. Born to lead. Extraordinary independence and authority."},
    (1, 9): {"name": "Surya-Mangal Yoga", "desc": "Leadership + courage. Military or political success. Fearless achiever."},
    (9, 1): {"name": "Mangal-Surya Yoga", "desc": "Courage leads to leadership. Warrior who becomes king."},
    (1, 5): {"name": "Surya-Budh Yoga", "desc": "Leadership + intellect. Business mogul energy. Quick decisions."},
    (5, 1): {"name": "Budh-Surya Yoga", "desc": "Intelligence serves leadership. Natural CEO."},
    (2, 7): {"name": "Chandra-Ketu Yoga", "desc": "Intuition + spirituality. Psychic ability. Spiritual healer."},
    (7, 2): {"name": "Ketu-Chandra Yoga", "desc": "Spiritual depth + emotional intelligence. Mystic healer."},
    (3, 6): {"name": "Guru-Shukra Yoga", "desc": "Wisdom + beauty. Creative genius. Success in arts and luxury."},
    (6, 3): {"name": "Shukra-Guru Yoga", "desc": "Beauty + wisdom. Film, fashion, or luxury industry success."},
    (3, 9): {"name": "Guru-Mangal Yoga", "desc": "Wisdom + action. Righteous warrior. Dharmic success."},
    (9, 3): {"name": "Mangal-Guru Yoga", "desc": "Courage guided by wisdom. Spiritual warrior."},
    (4, 8): {"name": "Rahu-Shani Yoga", "desc": "Unconventional + disciplined. Late but massive success. Karmic breakthroughs."},
    (8, 4): {"name": "Shani-Rahu Yoga", "desc": "Discipline + innovation. Breaks old systems to build new ones."},
    (5, 5): {"name": "Double Mercury Yoga", "desc": "Supreme communicator. Trading genius. Multi-talented polymath."},
    (1, 3): {"name": "Surya-Guru Yoga", "desc": "Leadership + wisdom. Natural teacher-leader. Commands respect."},
    (3, 1): {"name": "Guru-Surya Yoga", "desc": "Wisdom in leadership. Spiritual leader or mentor-CEO."},
    (2, 6): {"name": "Chandra-Shukra Yoga", "desc": "Emotions + beauty. Artistic genius. Success in creative fields."},
    (6, 2): {"name": "Shukra-Chandra Yoga", "desc": "Beauty + intuition. Fashion, design, luxury success."},
    (5, 9): {"name": "Budh-Mangal Yoga", "desc": "Intellect + courage. Daring entrepreneur. Risk-smart achiever."},
    (9, 5): {"name": "Mangal-Budh Yoga", "desc": "Action + intelligence. Strategic warrior. Sports + business."},
    (8, 8): {"name": "Double Saturn Yoga", "desc": "Extreme karmic intensity. Either massive success or deep lessons. Power after 40."},
    (1, 2): {"name": "Surya-Chandra Yoga", "desc": "Authority + sensitivity. Balanced leader. Public appeal."},
    (2, 1): {"name": "Chandra-Surya Yoga", "desc": "Emotional depth fuels leadership. People's leader."},
    (6, 9): {"name": "Shukra-Mangal Yoga", "desc": "Beauty + fire. Passionate achiever. Arts or sports success."},
    (9, 6): {"name": "Mangal-Shukra Yoga", "desc": "Courage + harmony. Military artist. Creative warrior."},
    (5, 6): {"name": "Budh-Shukra Yoga", "desc": "Intelligence + beauty. Business + arts fusion. Marketing genius."},
    (6, 5): {"name": "Shukra-Budh Yoga", "desc": "Creativity + intellect. Design thinking. Innovation in luxury."},
    (3, 5): {"name": "Guru-Budh Yoga", "desc": "Wisdom + communication. Author, speaker, teacher. Media success."},
    (5, 3): {"name": "Budh-Guru Yoga", "desc": "Intellect + expansion. Academic success. Publishing, education."},
    (4, 7): {"name": "Rahu-Ketu Yoga", "desc": "Nodal axis yoga. Extreme karmic life. Sudden rises and falls. Past-life driven."},
    (7, 4): {"name": "Ketu-Rahu Yoga", "desc": "Spiritual detachment + material ambition. Inner conflict but potential greatness."},
}


def calc_raj_yogas(loshu_counts: Dict, driver: int, conductor: int) -> Dict:
    """
    Detect all Raj Yogas from Loshu Grid and Driver-Conductor combination.
    """
    grid_yogas = []
    for key, yoga in RAJ_YOGAS.items():
        nums = yoga["numbers"]
        all_present = all(loshu_counts.get(n, 0) > 0 for n in nums)
        if all_present:
            # Calculate strength based on total count of these numbers
            total_hits = sum(loshu_counts.get(n, 0) for n in nums)
            strength = "strong" if total_hits >= 5 else ("moderate" if total_hits >= 3 else "present")
            grid_yogas.append({
                **yoga,
                "key": key,
                "strength": strength,
                "total_occurrences": total_hits,
            })

    # Driver-Conductor yoga
    dc_key = (driver, conductor)
    dc_yoga = None
    if dc_key in DRIVER_CONDUCTOR_YOGAS:
        dc_yoga = {
            "driver": driver,
            "conductor": conductor,
            **DRIVER_CONDUCTOR_YOGAS[dc_key],
        }

    # Determine overall yoga status
    has_golden = any(y["type"] == "golden" for y in grid_yogas)
    has_silver = any(y["type"] == "silver" for y in grid_yogas)
    yoga_count = len(grid_yogas)

    status = "ordinary"
    if has_golden and has_silver:
        status = "double_raj_yoga"
    elif has_golden:
        status = "golden_raj_yoga"
    elif has_silver:
        status = "silver_raj_yoga"
    elif yoga_count >= 3:
        status = "multi_yoga"
    elif yoga_count >= 1:
        status = "yoga_present"

    return {
        "status": status,
        "grid_yogas": grid_yogas,
        "grid_yoga_count": yoga_count,
        "has_golden": has_golden,
        "has_silver": has_silver,
        "driver_conductor_yoga": dc_yoga,
    }


# ═══════════════════════════════════════════════════════════════
# YEARLY LOSHU GRID PREDICTIONS (Multi-Year Forecast)
# ═══════════════════════════════════════════════════════════════

YEARLY_PREDICTIONS = {
    1: {
        "theme": "New Beginnings & Leadership",
        "career": "Excellent year to start new ventures, launch projects, or seek promotion. Take initiative. Leadership opportunities arise.",
        "money": "Good year to invest in new opportunities. Fresh income sources appear. Don't be afraid to spend on self-improvement.",
        "health": "High energy. Start a new fitness routine. Watch for stress from new responsibilities.",
        "relationships": "New relationships form. Independence is highlighted. Balance self with others.",
        "advice": "Be bold. Start what you've been planning. This is YOUR year to shine.",
        "rating": 8,
    },
    2: {
        "theme": "Patience & Partnerships",
        "career": "Not the year for solo action. Collaborate, partner up, and support others. Details matter. Patience brings rewards.",
        "money": "Slow but steady financial growth. Avoid risky investments. Save and plan. Partnership income possible.",
        "health": "Emotional sensitivity high. Watch for anxiety and digestive issues. Gentle exercise best.",
        "relationships": "Deep connections form. Marriage favorable. Existing relationships deepen. Be a good listener.",
        "advice": "Wait. Cooperate. Let things develop naturally. Don't force anything.",
        "rating": 5,
    },
    3: {
        "theme": "Creativity & Expression",
        "career": "Express yourself! Writing, speaking, artistic projects succeed. Social networking brings opportunities. Media and communication favored.",
        "money": "Money comes through creative work and social connections. Avoid overspending on entertainment.",
        "health": "Good vitality. Social energy high. Watch throat and respiratory issues.",
        "relationships": "Social butterfly year. New friendships. Romance through social events. Fun and joy in relationships.",
        "advice": "Create, express, socialize. Your words have extra power this year. Use them wisely.",
        "rating": 7,
    },
    4: {
        "theme": "Hard Work & Foundation",
        "career": "Build solid foundations. Hard work year — no shortcuts. Discipline, organization, and persistence are required. Structure your career.",
        "money": "Tight but stable. Focus on budgeting and saving. Property investments favored. Avoid speculation.",
        "health": "Physical body needs attention. Back, joints, bones. Establish healthy routines.",
        "relationships": "Serious commitments. Building family foundations. Less fun, more responsibility.",
        "advice": "Work hard. Build systems. This year's effort creates next year's harvest. Don't complain — build.",
        "rating": 4,
    },
    5: {
        "theme": "Change & Freedom",
        "career": "Major changes ahead! Job changes, travel, unexpected opportunities. Adaptability is key. Go with the flow.",
        "money": "Variable finances. Windfall and loss both possible. Trading and speculation may work if cautious. Travel expenses high.",
        "health": "Nervous energy. Watch for restlessness, insomnia. Stay grounded. Avoid addictions.",
        "relationships": "Exciting but unstable. New attractions. Freedom vs. commitment tension. Travel brings romance.",
        "advice": "Embrace change. Don't cling to the old. Adventure awaits but stay disciplined.",
        "rating": 6,
    },
    6: {
        "theme": "Home, Family & Love",
        "career": "Home-based work favored. Family business grows. Creative and beauty industries thrive. Counseling and healing roles.",
        "money": "Good for home/property investments. Family financial support. Luxury expenses increase but manageable.",
        "health": "Generally good. Weight gain possible from comfort eating. Throat and kidney attention needed.",
        "relationships": "BEST year for love, marriage, and family. Deep bonds form. Wedding bells likely. Harmony at home.",
        "advice": "Focus on home and loved ones. Beautify your space. Give and receive love.",
        "rating": 8,
    },
    7: {
        "theme": "Spirituality & Introspection",
        "career": "Slow down. Research, study, and analyze. Not ideal for aggressive business moves. Spiritual or healing career boost.",
        "money": "Not a big money year. Avoid risky investments. Good for intellectual property. Income from research/consulting.",
        "health": "Mental health focus. Rest is essential. Mysterious ailments possible. Meditation and nature heal.",
        "relationships": "Need for solitude. Relationships feel distant. Spiritual connections deepen. Inner work is priority.",
        "advice": "Go inward. Study, meditate, research. The answers are within. Don't force external results.",
        "rating": 4,
    },
    8: {
        "theme": "Power, Money & Karma",
        "career": "PEAK YEAR for career and finance. Authority, promotion, power. Business expansion. Legal matters favor you.",
        "money": "Strongest money year! Major financial gains, property deals, inheritance. Karma rewards past hard work.",
        "health": "Strong but watch for blood pressure and bone issues. Power and stress go together.",
        "relationships": "Power dynamics in relationships. Commanding presence attracts. Material security strengthens bonds.",
        "advice": "Seize the power. This is harvest time. What you sowed in years 1-7 comes to fruition. Be ethical — karma is instant in year 8.",
        "rating": 9,
    },
    9: {
        "theme": "Completion & Release",
        "career": "Wrap up old projects. Endings that make room for new beginnings. Humanitarian work succeeds. Teaching and mentoring.",
        "money": "Loose ends in finances tied up. Unexpected money from old sources. Generosity brings more. Donate for karma.",
        "health": "Detox year — physical and emotional. Release old habits. May feel drained. Rest and recover.",
        "relationships": "Some relationships end naturally. Universal love expands. Forgiveness is key. Let go of grudges.",
        "advice": "Release what no longer serves you. Clean, donate, forgive. The old cycle ends — prepare for the new.",
        "rating": 6,
    },
}


def calc_yearly_loshu_predictions(day: int, month: int, year: int,
                                   start_year: int = None, num_years: int = 15) -> Dict:
    """
    Generate multi-year Loshu Grid predictions.
    For each year: build a temporary Loshu grid using DOB + year digits,
    detect yogas, and provide career/money/health/relationship forecast.
    """
    from datetime import datetime
    if start_year is None:
        start_year = datetime.now().year - 2  # Show 2 years back + current + future

    driver = reduce_to_single(day, keep_master=False)
    conductor_base = sum(int(ch) for ch in f"{day:02d}{month:02d}{year}" if ch.isdigit())
    conductor = reduce_to_single(conductor_base, keep_master=False)

    yearly = []
    for yr in range(start_year, start_year + num_years):
        # Personal year number
        py_sum = reduce_to_single(day, False) + reduce_to_single(month, False) + reduce_to_single(_digit_sum(yr), False)
        personal_year = reduce_to_single(py_sum, keep_master=False)

        # Year Loshu grid: DOB digits + driver + conductor + current year digits
        dob_str = f"{day:02d}{month:02d}{year}"
        dob_digits = [int(ch) for ch in dob_str if ch.isdigit() and ch != '0']
        year_digits = [int(ch) for ch in str(yr) if ch.isdigit() and ch != '0']

        all_digits = dob_digits + [driver, conductor] + year_digits
        counts = {}
        for d in range(1, 10):
            counts[d] = all_digits.count(d)

        present = sorted([d for d in range(1, 10) if counts[d] > 0])
        missing = sorted([d for d in range(1, 10) if counts[d] == 0])

        # Detect yogas in this year's grid
        year_yogas = []
        for key, yoga in RAJ_YOGAS.items():
            nums = yoga["numbers"]
            if all(counts.get(n, 0) > 0 for n in nums):
                year_yogas.append(key)

        has_golden = "golden_raj_yoga" in year_yogas
        has_silver = "silver_raj_yoga" in year_yogas

        # Year rating based on personal year + yogas
        base_pred = YEARLY_PREDICTIONS.get(personal_year, YEARLY_PREDICTIONS[1])
        rating = base_pred["rating"]
        # Boost for yogas
        if has_golden:
            rating = min(10, rating + 2)
        if has_silver:
            rating = min(10, rating + 1)
        if len(year_yogas) >= 3:
            rating = min(10, rating + 1)
        # Penalty for many missing numbers
        if len(missing) >= 5:
            rating = max(1, rating - 1)

        # Year classification
        if rating >= 9:
            classification = "golden_year"
            class_label = "Golden Year"
        elif rating >= 7:
            classification = "excellent"
            class_label = "Excellent Year"
        elif rating >= 5:
            classification = "good"
            class_label = "Good Year"
        elif rating >= 4:
            classification = "average"
            class_label = "Average Year"
        else:
            classification = "challenging"
            class_label = "Challenging Year"

        yearly.append({
            "year": yr,
            "personal_year": personal_year,
            "theme": base_pred["theme"],
            "career": base_pred["career"],
            "money": base_pred["money"],
            "health": base_pred["health"],
            "relationships": base_pred["relationships"],
            "advice": base_pred["advice"],
            "rating": rating,
            "classification": classification,
            "class_label": class_label,
            "year_digits": year_digits,
            "present_numbers": present,
            "missing_numbers": missing,
            "year_yogas": year_yogas,
            "has_golden": has_golden,
            "has_silver": has_silver,
            "yoga_count": len(year_yogas),
        })

    return {
        "driver": driver,
        "conductor": conductor,
        "start_year": start_year,
        "num_years": num_years,
        "yearly_predictions": yearly,
    }


# ═══════════════════════════════════════════════════════════════
# MASTER FUNCTION
# ═══════════════════════════════════════════════════════════════

def calculate_numerology(
    name: str,
    dob: str,
    mobile: Optional[str] = None,
    car_number: Optional[str] = None,
    password: Optional[str] = None,
    system: str = "both",
) -> Dict:
    """
    Complete numerology analysis.
    system: "pythagorean", "chaldean", or "both"
    """
    day, month, year = _parse_dob(dob)

    # ── Core Numbers ──
    life_path_data = calc_life_path(day, month, year)
    life_path = life_path_data["number"]

    birthday_data = calc_birthday_number(day)

    # Name analysis in both systems
    if system == "both":
        pyth_name = calc_name_number(name, "pythagorean")
        chal_name = calc_name_number(name, "chaldean")
        name_analysis = {"pythagorean": pyth_name, "chaldean": chal_name}
        destiny = pyth_name["destiny_number"]
    elif system == "chaldean":
        chal_name = calc_name_number(name, "chaldean")
        name_analysis = {"chaldean": chal_name}
        destiny = chal_name["destiny_number"]
    else:
        pyth_name = calc_name_number(name, "pythagorean")
        name_analysis = {"pythagorean": pyth_name}
        destiny = pyth_name["destiny_number"]

    maturity_data = calc_maturity_number(life_path, destiny)

    # ── Date additions (user requested) ──
    # "Life path date addition" = day reduction
    # "Total addition" = full DOB digit sum
    full_dob_sum = sum(_get_dob_digits(dob))
    full_dob_reduced = reduce_to_single(full_dob_sum, keep_master=True)
    date_addition = {
        "day_number": reduce_to_single(day, keep_master=True),
        "day_calculation": f"{day} → {reduce_to_single(day, keep_master=True)}",
        "total_dob_sum": full_dob_sum,
        "total_dob_reduced": full_dob_reduced,
        "total_calculation": f"All DOB digits: {'+'.join(str(d) for d in _get_dob_digits(dob))} = {full_dob_sum} → {full_dob_reduced}",
        "day_traits": NUMBER_CHARACTERISTICS.get(reduce_to_single(day, keep_master=True), {}),
        "total_traits": NUMBER_CHARACTERISTICS.get(full_dob_reduced, {}),
    }

    # ── Loshu Grid ──
    loshu = calc_loshu_grid(day, month, year)

    # ── Characteristics ──
    lp_chars = NUMBER_CHARACTERISTICS.get(life_path, {})
    dest_chars = NUMBER_CHARACTERISTICS.get(destiny, {})
    bday_chars = NUMBER_CHARACTERISTICS.get(birthday_data["number"], {})

    # ── Name Correction ──
    name_correction_pyth = suggest_name_correction(name, life_path, "pythagorean")
    name_correction_chal = suggest_name_correction(name, life_path, "chaldean")

    # ── Mobile Analysis ──
    mobile_analysis = None
    if mobile:
        mobile_analysis = suggest_mobile_correction(mobile, life_path)

    # ── Car Number Analysis ──
    car_analysis = None
    if car_number:
        car_analysis = analyze_number_string(car_number, life_path, "Car/Vehicle Number")

    # ── Password Analysis ──
    password_analysis = None
    password_current = None
    if password:
        password_current = analyze_number_string(password, life_path, "Current Password")
    password_suggestions = suggest_password(life_path, day, name)

    # ── Personal Year ──
    from datetime import datetime
    current_year = datetime.now().year
    personal_cycles = calc_personal_cycles(day, month, year, current_year)

    # ── Raj Yogas ──
    raj_yogas = calc_raj_yogas(
        loshu["counts"],
        loshu["driver_number"],
        loshu["conductor_number"],
    )

    # ── Yearly Loshu Predictions (15 years: 2 back + current + 12 forward) ──
    yearly_predictions = calc_yearly_loshu_predictions(day, month, year)

    return {
        "name": name,
        "dob": dob,
        "day": day,
        "month": month,
        "year": year,

        "core_numbers": {
            "life_path": life_path_data,
            "birthday": birthday_data,
            "maturity": maturity_data,
            "date_addition": date_addition,
        },

        "name_analysis": name_analysis,

        "characteristics": {
            "life_path": lp_chars,
            "destiny": dest_chars,
            "birthday": bday_chars,
        },

        "loshu_grid": loshu,
        "raj_yogas": raj_yogas,

        "name_correction": {
            "pythagorean": name_correction_pyth,
            "chaldean": name_correction_chal,
        },

        "mobile_analysis": mobile_analysis,
        "car_analysis": car_analysis,
        "password_current": password_current,
        "password_suggestions": password_suggestions,
        "personal_cycles": personal_cycles,
        "yearly_predictions": yearly_predictions,
    }
