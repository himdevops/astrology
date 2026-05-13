"""
tarot.py — Tarot Card Reading Engine
=====================================
Full 78-card deck (22 Major Arcana + 56 Minor Arcana).
Random draw of 1-5 cards with upright/reversed.
Automatic combination analysis for multi-card spreads.
"""
from __future__ import annotations

import random
from typing import Dict, List, Optional


# ═══════════════════════════════════════════════════════════════
# 22 MAJOR ARCANA
# ═══════════════════════════════════════════════════════════════

MAJOR_ARCANA = [
    {
        "number": 0, "name": "The Fool", "arcana": "major",
        "keywords_up": ["new beginnings", "innocence", "adventure", "leap of faith", "spontaneity"],
        "keywords_rev": ["recklessness", "fear", "holding back", "naivety", "poor judgment"],
        "upright": "A new journey begins. Trust the universe and take the leap. Fresh start, unlimited potential, childlike wonder. The universe supports your bold moves.",
        "reversed": "Reckless behavior, fear of the unknown holding you back. Poor decisions due to naivety. Look before you leap. Not the time for blind risks.",
        "love_up": "Exciting new romance or fresh energy in existing relationship. Be open to unexpected connections.",
        "love_rev": "Fear of commitment. Rushing into relationships without thinking. Instability in love.",
        "career_up": "New job, career change, or entrepreneurial venture. Take the risk — it will pay off.",
        "career_rev": "Quitting without a plan. Unreliable at work. Avoid impulsive career moves.",
        "money_up": "Unexpected financial opportunities. Don't overthink — invest in your future.",
        "money_rev": "Foolish spending. Financial risks without research. Protect your savings.",
        "health_up": "Fresh start in health routines. High energy and vitality. Try something new.",
        "health_rev": "Ignoring health warnings. Reckless behavior affecting wellbeing.",
        "element": "Air", "planet": "Uranus",
    },
    {
        "number": 1, "name": "The Magician", "arcana": "major",
        "keywords_up": ["manifestation", "willpower", "skill", "resourcefulness", "power"],
        "keywords_rev": ["manipulation", "trickery", "untapped potential", "deception", "illusion"],
        "upright": "You have everything you need to succeed. Channel your willpower and manifest your desires. Skill, talent, and resources are aligned. Make it happen NOW.",
        "reversed": "Manipulation or being manipulated. Wasted talent. Trickery and deception around you. You're not using your full potential.",
        "love_up": "Magnetic attraction. You can manifest the love you desire. Strong chemistry and communication.",
        "love_rev": "Deception in love. Partner may be manipulative. Don't use charm to deceive.",
        "career_up": "Skills perfectly aligned for success. Launch that project. You have the Midas touch right now.",
        "career_rev": "Conning or being conned at work. Misusing talents. Workplace manipulation.",
        "money_up": "Financial manifestation power is high. Smart investments pay off. Create wealth.",
        "money_rev": "Financial scams. Too-good-to-be-true deals. Someone may be cheating you financially.",
        "health_up": "Healing power is strong. Mind-body connection works in your favor.",
        "health_rev": "Ignoring symptoms. Self-deception about health. Seek proper diagnosis.",
        "element": "Air", "planet": "Mercury",
    },
    {
        "number": 2, "name": "The High Priestess", "arcana": "major",
        "keywords_up": ["intuition", "mystery", "subconscious", "inner voice", "wisdom"],
        "keywords_rev": ["secrets", "disconnection", "withdrawal", "repressed feelings", "silence"],
        "upright": "Trust your intuition — it knows the truth. Hidden knowledge is being revealed. Go within for answers. The subconscious mind is your greatest ally now.",
        "reversed": "Ignoring your inner voice. Secrets being kept from you or by you. Disconnected from intuition. Information is hidden.",
        "love_up": "Deep spiritual connection with partner. Trust your gut about someone. Hidden feelings surfacing.",
        "love_rev": "Secrets in relationship. Partner hiding something. Emotional withdrawal.",
        "career_up": "Trust instincts about career decisions. Hidden opportunities revealing themselves.",
        "career_rev": "Office secrets and politics. Information being withheld. Don't trust surface appearances.",
        "money_up": "Intuitive financial decisions pay off. Hidden assets or income sources emerge.",
        "money_rev": "Financial secrets. Hidden debts or losses. Someone hiding financial truth from you.",
        "health_up": "Listen to your body's signals. Holistic and intuitive healing favored.",
        "health_rev": "Undiagnosed conditions. Ignoring body's warning signs. Get a thorough checkup.",
        "element": "Water", "planet": "Moon",
    },
    {
        "number": 3, "name": "The Empress", "arcana": "major",
        "keywords_up": ["abundance", "fertility", "nurturing", "nature", "beauty"],
        "keywords_rev": ["dependence", "smothering", "emptiness", "creative block", "neglect"],
        "upright": "Abundance flows to you. Fertility in all forms — creative, financial, physical. Mother energy nurtures your growth. Beauty and luxury surround you.",
        "reversed": "Creative block or stagnation. Smothering others or being smothered. Neglecting self-care. Dependence on others for validation.",
        "love_up": "Deeply nurturing love. Pregnancy possible. Sensual, abundant romantic energy.",
        "love_rev": "Overbearing in love. Codependency. Neglecting your own needs for partner.",
        "career_up": "Creative projects flourish. Business growth and abundance. Nurturing leadership style succeeds.",
        "career_rev": "Creative burnout. Overgiving at work without receiving. Stagnant projects.",
        "money_up": "Financial abundance and growth. Investments bear fruit. Luxury purchases justified.",
        "money_rev": "Overspending on luxury. Financial dependence on others. Growth stalled.",
        "health_up": "Excellent fertility and vitality. Natural remedies work well. Pregnancy favorable.",
        "health_rev": "Neglecting health for others. Reproductive issues. Need more self-care.",
        "element": "Earth", "planet": "Venus",
    },
    {
        "number": 4, "name": "The Emperor", "arcana": "major",
        "keywords_up": ["authority", "structure", "control", "father figure", "stability"],
        "keywords_rev": ["tyranny", "rigidity", "domination", "inflexibility", "lack of discipline"],
        "upright": "Take charge and establish order. Authority, leadership, and structure are your allies. The father energy brings stability, protection, and wise governance.",
        "reversed": "Abuse of power. Excessive control or complete lack of it. Tyrannical behavior. Rigid thinking blocks progress.",
        "love_up": "Stable, protective partnership. Strong commitment. Traditional relationship values succeed.",
        "love_rev": "Controlling partner. Power struggles in relationship. Emotional rigidity.",
        "career_up": "Leadership role suits you. Establish systems and structures. Authority recognized.",
        "career_rev": "Micromanaging boss or being one. Power struggles at work. Bureaucratic obstacles.",
        "money_up": "Financial stability through discipline. Build structures for long-term wealth.",
        "money_rev": "Financial control issues. Either too rigid or too loose with money.",
        "health_up": "Disciplined health routines pay off. Structural health (bones, posture) good.",
        "health_rev": "Stress from overcontrol. Rigidity causing physical tension. Delegate and relax.",
        "element": "Fire", "planet": "Aries",
    },
    {
        "number": 5, "name": "The Hierophant", "arcana": "major",
        "keywords_up": ["tradition", "spiritual wisdom", "conformity", "mentorship", "education"],
        "keywords_rev": ["rebellion", "subversion", "new approaches", "freedom", "challenging norms"],
        "upright": "Seek wisdom from tradition and established systems. A mentor or teacher appears. Spiritual education and conventional paths bring success. Follow the established way.",
        "reversed": "Challenge tradition. Think outside the box. Rebel against outdated systems. Personal spiritual path over organized religion.",
        "love_up": "Traditional relationship milestones — engagement, marriage, ceremonies. Conventional courtship.",
        "love_rev": "Unconventional relationship. Breaking from traditional expectations. Freedom in love.",
        "career_up": "Education, training, mentorship advance career. Traditional career paths succeed.",
        "career_rev": "Rebel against corporate culture. Innovative approaches needed. Reject outdated methods.",
        "money_up": "Conservative financial strategies work. Traditional investments. Seek financial advisor.",
        "money_rev": "Alternative financial strategies may work better. Cryptocurrency, unconventional investments.",
        "health_up": "Traditional medicine and established treatments work well. Follow doctor's advice.",
        "health_rev": "Alternative healing methods may help. Question conventional medical advice if not working.",
        "element": "Earth", "planet": "Taurus",
    },
    {
        "number": 6, "name": "The Lovers", "arcana": "major",
        "keywords_up": ["love", "harmony", "choices", "alignment", "union"],
        "keywords_rev": ["disharmony", "imbalance", "misalignment", "bad choices", "indecision"],
        "upright": "Major choice ahead — choose with your heart aligned to your values. Deep love and union possible. Harmony between opposites. A soulmate connection or critical life decision.",
        "reversed": "Misaligned values. Relationship disharmony. Wrong choice being made. Inner conflict between head and heart.",
        "love_up": "POWERFUL love card. Soulmate energy. Deep union and harmony. Choose love.",
        "love_rev": "Relationship conflict. Values misaligned with partner. Temptation or infidelity risk.",
        "career_up": "Partnership or collaboration succeeds. Choose career aligned with your values.",
        "career_rev": "Business partnership conflicts. Career choice misaligned with true self.",
        "money_up": "Financial decisions made from aligned values succeed. Partnership income.",
        "money_rev": "Financial disagreements with partner. Wrong investment choices.",
        "health_up": "Mind-body harmony. Balanced approach to health works beautifully.",
        "health_rev": "Health choices misaligned with body's needs. Inner conflict manifesting physically.",
        "element": "Air", "planet": "Gemini",
    },
    {
        "number": 7, "name": "The Chariot", "arcana": "major",
        "keywords_up": ["victory", "determination", "willpower", "control", "triumph"],
        "keywords_rev": ["aggression", "lack of direction", "defeat", "scattered energy", "loss of control"],
        "upright": "Victory through determination and willpower. You WILL succeed if you stay focused. Harness opposing forces and drive forward. Triumph over obstacles is assured.",
        "reversed": "Loss of direction or control. Aggression without purpose. Scattered energy defeats you. You're trying to force what can't be forced.",
        "love_up": "Determined pursuit of love succeeds. Overcoming relationship obstacles. Victory in love.",
        "love_rev": "Forcing love that isn't meant to be. Controlling behavior in relationships.",
        "career_up": "Career victory! Promotion, recognition, competitive wins. Drive forward with confidence.",
        "career_rev": "Career stalled. Aggression backfires at work. Lack of clear direction.",
        "money_up": "Financial victories. Determined effort pays off financially. Win competitions.",
        "money_rev": "Financial direction lost. Aggressive investing fails. Rein in spending.",
        "health_up": "Willpower overcomes health challenges. Victory over illness. Strong vitality.",
        "health_rev": "Pushing body too hard. Road/travel accidents possible. Slow down.",
        "element": "Water", "planet": "Cancer",
    },
    {
        "number": 8, "name": "Strength", "arcana": "major",
        "keywords_up": ["inner strength", "courage", "patience", "compassion", "soft power"],
        "keywords_rev": ["self-doubt", "weakness", "insecurity", "raw emotion", "lack of confidence"],
        "upright": "True strength is gentle. Tame your inner beasts with patience and compassion, not force. Courage comes from inner conviction. You are stronger than you think.",
        "reversed": "Self-doubt and insecurity. Inner strength depleted. Letting fear control you. Need to rebuild confidence from within.",
        "love_up": "Gentle strength attracts love. Patience with partner pays off. Compassionate love.",
        "love_rev": "Insecurity damaging relationship. Lack of confidence in love. Fear of vulnerability.",
        "career_up": "Gentle persistence wins at work. Leadership through compassion, not force.",
        "career_rev": "Feeling powerless at work. Self-doubt holding back career progress.",
        "money_up": "Patient financial approach succeeds. Inner confidence attracts abundance.",
        "money_rev": "Financial insecurity. Fear-based money decisions. Rebuild financial confidence.",
        "health_up": "Inner strength aids recovery. Immune system strong. Mental resilience high.",
        "health_rev": "Depleted energy. Anxiety and self-doubt affecting health. Restore inner balance.",
        "element": "Fire", "planet": "Leo",
    },
    {
        "number": 9, "name": "The Hermit", "arcana": "major",
        "keywords_up": ["solitude", "inner guidance", "wisdom", "soul searching", "reflection"],
        "keywords_rev": ["isolation", "loneliness", "withdrawal", "lost", "anti-social"],
        "upright": "Go within. Solitude brings wisdom. The answers you seek are inside you. Take time for deep reflection and soul-searching. A wise mentor may appear.",
        "reversed": "Excessive isolation or loneliness. Withdrawal from life. Refusing to seek or accept guidance. Lost and directionless.",
        "love_up": "Need time alone to understand what you truly want in love. Wisdom about relationships.",
        "love_rev": "Isolating from partner. Loneliness. Refusing to open up emotionally.",
        "career_up": "Solo work or research excels. Mentorship opportunity. Deep expertise development.",
        "career_rev": "Too isolated at work. Need to collaborate. Career feels purposeless.",
        "money_up": "Wise, researched financial decisions. Conservative approach works. Seek expert advice.",
        "money_rev": "Financial isolation. Not seeking help when needed. Hoarding or miserliness.",
        "health_up": "Meditation and retreat heal. Inner peace restores health. Spiritual healing.",
        "health_rev": "Depression from isolation. Mental health needs attention. Seek support.",
        "element": "Earth", "planet": "Virgo",
    },
    {
        "number": 10, "name": "Wheel of Fortune", "arcana": "major",
        "keywords_up": ["luck", "destiny", "turning point", "cycles", "fate"],
        "keywords_rev": ["bad luck", "resistance to change", "broken cycles", "setbacks", "delays"],
        "upright": "The wheel turns in your favor! Destiny, luck, and fate align. A major turning point. Cycles of life bringing opportunity. What goes around comes around — positively.",
        "reversed": "Bad luck phase or resistance to natural change. Karmic setbacks. Fighting against destiny. The wheel will turn again — be patient.",
        "love_up": "Fated love encounter. Relationship reaching a positive turning point. Destiny at work.",
        "love_rev": "Relationship setback. Feeling stuck in love cycle. Bad luck in romance — temporary.",
        "career_up": "Lucky career break! Promotion, opportunity, or destiny-level career shift.",
        "career_rev": "Career setback or delay. Bad timing. Wait for the wheel to turn again.",
        "money_up": "Financial luck! Windfall, lottery, unexpected gains. Fortune favors you.",
        "money_rev": "Financial downturn — temporary. Losses or setbacks. Don't gamble now.",
        "health_up": "Health improving as cycle shifts. Recovery from illness. Positive turning point.",
        "health_rev": "Health setback. Chronic cycle returning. Patience needed for recovery.",
        "element": "Fire", "planet": "Jupiter",
    },
    {
        "number": 11, "name": "Justice", "arcana": "major",
        "keywords_up": ["fairness", "truth", "law", "cause and effect", "accountability"],
        "keywords_rev": ["unfairness", "dishonesty", "lack of accountability", "bias", "legal problems"],
        "upright": "Truth and fairness prevail. Legal matters resolve in your favor. Karmic justice — you reap what you sowed. Make balanced, fair decisions.",
        "reversed": "Injustice, unfairness, or dishonesty. Legal complications. Avoiding accountability. Biased judgment.",
        "love_up": "Fair and balanced relationship. Honest communication. Legal union (marriage).",
        "love_rev": "Unfair treatment in love. Dishonesty discovered. Legal separation possible.",
        "career_up": "Fair outcome in workplace disputes. Contracts and legal matters favor you.",
        "career_rev": "Workplace injustice. Legal issues at work. Unfair treatment by boss.",
        "money_up": "Financial justice — debts repaid, fair deals. Legal financial win.",
        "money_rev": "Financial injustice. Legal money problems. Unfair contracts. Read fine print.",
        "health_up": "Balance restored. Cause-and-effect approach to health works. Proper diagnosis.",
        "health_rev": "Misdiagnosis. Unfair health outcome. Seek second opinion.",
        "element": "Air", "planet": "Libra",
    },
    {
        "number": 12, "name": "The Hanged Man", "arcana": "major",
        "keywords_up": ["surrender", "new perspective", "pause", "letting go", "sacrifice"],
        "keywords_rev": ["stalling", "resistance", "indecision", "needless sacrifice", "stuck"],
        "upright": "Surrender and see from a new angle. Pause is productive. Let go of control to gain true understanding. Voluntary sacrifice brings spiritual reward.",
        "reversed": "Stalling without purpose. Resisting necessary change. Martyrdom without reason. Stuck in limbo by choice.",
        "love_up": "See relationship from partner's perspective. Surrender control. New understanding of love.",
        "love_rev": "Relationship in limbo. Neither moving forward nor ending. Unnecessary sacrifice.",
        "career_up": "Pause and reassess career. New perspective needed. Voluntary step back leads to leap forward.",
        "career_rev": "Career in limbo. Refusing to adapt. Sacrificing too much for job.",
        "money_up": "Financial pause is wise. Let investments mature. Don't force money outcomes.",
        "money_rev": "Financial stagnation. Money stuck in bad investments. Cut losses.",
        "health_up": "Rest and recovery. Let body heal naturally. New health perspective helpful.",
        "health_rev": "Health in limbo. Treatment not progressing. Try different approach.",
        "element": "Water", "planet": "Neptune",
    },
    {
        "number": 13, "name": "Death", "arcana": "major",
        "keywords_up": ["transformation", "endings", "rebirth", "change", "transition"],
        "keywords_rev": ["resistance to change", "stagnation", "decay", "fear of endings", "limbo"],
        "upright": "NOT literal death. Powerful transformation. Something must end for something better to begin. Embrace the change — rebirth follows. Old self dies, new self is born.",
        "reversed": "Resisting necessary endings. Stagnation from fear of change. Holding onto what should be released. Personal transformation delayed.",
        "love_up": "Relationship transformation. Old patterns dying. Deeper love emerging from the ashes.",
        "love_rev": "Refusing to let go of dead relationship. Fear of change in love. Stagnation.",
        "career_up": "Career transformation. Old job ending, new one beginning. Major shift for the better.",
        "career_rev": "Resisting necessary career change. Staying in dead-end job out of fear.",
        "money_up": "Financial transformation. Old income source ending, better one emerging.",
        "money_rev": "Clinging to failing financial strategies. Fear of financial change.",
        "health_up": "Major health transformation. Recovery. End of illness cycle. Renewed vitality.",
        "health_rev": "Refusing to change unhealthy habits. Health stagnation from resistance.",
        "element": "Water", "planet": "Scorpio",
    },
    {
        "number": 14, "name": "Temperance", "arcana": "major",
        "keywords_up": ["balance", "moderation", "patience", "harmony", "healing"],
        "keywords_rev": ["imbalance", "excess", "impatience", "discord", "self-healing needed"],
        "upright": "Balance and moderation are your path. Blend opposing forces harmoniously. Patience brings perfect results. A healing angel watches over you.",
        "reversed": "Life out of balance. Excess in one area draining another. Impatience sabotaging results. Harmony disrupted.",
        "love_up": "Balanced, harmonious love. Patience in relationship pays off. Soul-level harmony.",
        "love_rev": "Relationship imbalanced. One person giving more. Impatience causing fights.",
        "career_up": "Work-life balance achieved. Harmonious workplace. Patient career growth.",
        "career_rev": "Work-life imbalance. Overworking or underperforming. No moderation.",
        "money_up": "Balanced financial approach. Moderate spending, steady saving. Financial harmony.",
        "money_rev": "Financial excess or restriction. No balance in spending/saving.",
        "health_up": "Healing energy strong. Balanced health approach works. Recovery through moderation.",
        "health_rev": "Health imbalance. Excess (eating, drinking, work) harming body. Find middle path.",
        "element": "Fire", "planet": "Sagittarius",
    },
    {
        "number": 15, "name": "The Devil", "arcana": "major",
        "keywords_up": ["shadow self", "attachment", "addiction", "materialism", "bondage"],
        "keywords_rev": ["release", "breaking free", "detachment", "reclaiming power", "freedom"],
        "upright": "Face your shadow. Addictions, unhealthy attachments, or materialism binding you. The chains are self-imposed — you CAN break free. Confront what controls you.",
        "reversed": "Breaking free from addiction, toxic relationship, or unhealthy pattern. Reclaiming power. Liberation from self-imposed chains. Freedom!",
        "love_up": "Intense physical attraction but possibly toxic. Codependency. Passionate but unhealthy bond.",
        "love_rev": "Breaking free from toxic relationship. Ending codependency. Reclaiming self in love.",
        "career_up": "Trapped in unfulfilling job. Golden handcuffs. Materialism over purpose.",
        "career_rev": "Breaking free from soul-crushing job. Reclaiming career purpose.",
        "money_up": "Material obsession. Making money your master. Financial greed or gambling.",
        "money_rev": "Breaking free from financial bondage. Debt release. Healthier money relationship.",
        "health_up": "Addiction warning. Unhealthy habits controlling you. Face the shadow.",
        "health_rev": "Recovery from addiction. Breaking unhealthy cycles. Health freedom.",
        "element": "Earth", "planet": "Capricorn",
    },
    {
        "number": 16, "name": "The Tower", "arcana": "major",
        "keywords_up": ["sudden change", "upheaval", "revelation", "destruction", "awakening"],
        "keywords_rev": ["fear of change", "averting disaster", "prolonged turmoil", "resisting collapse"],
        "upright": "Sudden upheaval destroys false structures. Shocking revelation. What's built on lies must fall. Painful but necessary destruction clears the way for truth. Awakening through crisis.",
        "reversed": "Narrowly averting disaster. Prolonging inevitable collapse. Fear of necessary destruction. Personal crisis delayed but still coming.",
        "love_up": "Relationship shakeup. Truth bomb. Breakup that needed to happen. Liberation through destruction.",
        "love_rev": "Trying to save a relationship that should end. Avoiding the inevitable breakup.",
        "career_up": "Job loss or sudden career upheaval. Company restructuring. Shocking work news.",
        "career_rev": "Narrowly avoiding job loss. Prolonged workplace instability.",
        "money_up": "Sudden financial loss or shock. Market crash affecting you. Emergency expenses.",
        "money_rev": "Narrowly avoiding financial disaster. Build emergency fund NOW.",
        "health_up": "Sudden health crisis. Accident or acute illness. Emergency. Wake-up call.",
        "health_rev": "Health crisis narrowly avoided. Don't ignore warning signs.",
        "element": "Fire", "planet": "Mars",
    },
    {
        "number": 17, "name": "The Star", "arcana": "major",
        "keywords_up": ["hope", "faith", "renewal", "inspiration", "serenity"],
        "keywords_rev": ["despair", "disconnection", "hopelessness", "lack of faith", "discouragement"],
        "upright": "Hope renewed! After the storm comes the star. Faith in the universe restored. Inspiration flows. Healing, serenity, and cosmic blessing. You are guided and protected.",
        "reversed": "Lost hope and faith. Feeling disconnected from purpose. Despair and discouragement. The star still shines — you just can't see it yet.",
        "love_up": "Renewed hope in love. Soulmate energy. Healing after heartbreak. Wish fulfillment.",
        "love_rev": "Hopelessness in love. Disconnected from partner. Faith in love shaken.",
        "career_up": "Inspired career path. Hope for dream job. Creative inspiration flowing.",
        "career_rev": "Lost faith in career. Feeling disconnected from work purpose.",
        "money_up": "Financial hope and renewal. Wishes for abundance being answered.",
        "money_rev": "Financial hopelessness. Feeling like prosperity will never come.",
        "health_up": "Healing and renewal. Hope for recovery. Spiritual healing works beautifully.",
        "health_rev": "Losing hope in treatment. Disconnect from healing process. Keep faith.",
        "element": "Air", "planet": "Aquarius",
    },
    {
        "number": 18, "name": "The Moon", "arcana": "major",
        "keywords_up": ["illusion", "fear", "subconscious", "intuition", "dreams"],
        "keywords_rev": ["clarity", "truth revealed", "overcoming fear", "release of anxiety"],
        "upright": "Things are not as they seem. Illusions, fears, and subconscious patterns active. Trust your dreams and intuition but verify facts. Navigate the darkness carefully.",
        "reversed": "Illusions clearing. Truth being revealed. Overcoming deep fears. Anxiety releasing. Clarity emerging from confusion.",
        "love_up": "Hidden truths in relationship. Trust intuition about partner. Dreams revealing love truths.",
        "love_rev": "Clarity about partner's true nature. Overcoming relationship fears. Truth in love.",
        "career_up": "Workplace deception or confusion. Trust gut about job situations. Creative/artistic inspiration.",
        "career_rev": "Workplace truth revealed. Confusion clearing. Career clarity emerging.",
        "money_up": "Financial deception possible. Don't trust surface appearances. Hidden costs.",
        "money_rev": "Financial clarity. Hidden money matters coming to light. Scam avoided.",
        "health_up": "Mental health focus. Anxiety, insomnia, hormonal issues. Trust intuitive healing.",
        "health_rev": "Mental fog clearing. Overcoming health anxiety. Proper diagnosis finally.",
        "element": "Water", "planet": "Pisces",
    },
    {
        "number": 19, "name": "The Sun", "arcana": "major",
        "keywords_up": ["joy", "success", "vitality", "confidence", "positivity"],
        "keywords_rev": ["temporary setback", "inner child wounded", "overconfidence", "delayed success"],
        "upright": "The BEST card in the deck! Pure joy, success, vitality, and confidence. Everything shines brightly. Happiness, achievement, and positive energy in abundance. YES to everything!",
        "reversed": "Temporary cloud over the sun. Slightly delayed success. Inner child needs healing. Overconfidence may lead to minor setback. Still positive — just dimmed.",
        "love_up": "HAPPIEST love card! Joyful relationship. Engagement, wedding, pregnancy. Pure love and happiness.",
        "love_rev": "Happiness in love delayed but coming. Small relationship clouds. Keep positive.",
        "career_up": "Career success and recognition! Achievement, awards, promotion. You SHINE at work.",
        "career_rev": "Career success slightly delayed. Keep confidence up. It's coming.",
        "money_up": "Financial success! Abundance, profits, windfalls. Everything you touch turns to gold.",
        "money_rev": "Financial success delayed but not denied. Minor setback. Stay optimistic.",
        "health_up": "Peak vitality! Excellent health. Recovery. Energy and joy restore the body.",
        "health_rev": "Minor health delay. Vitality slightly low. Restore through joy and positivity.",
        "element": "Fire", "planet": "Sun",
    },
    {
        "number": 20, "name": "Judgement", "arcana": "major",
        "keywords_up": ["rebirth", "inner calling", "absolution", "reckoning", "purpose"],
        "keywords_rev": ["self-doubt", "refusing the call", "ignoring purpose", "harsh self-judgment"],
        "upright": "A higher calling awakens you. Judgement day — not punishment but rebirth. Answer your soul's call. Past actions reviewed and absolved. Rise to your purpose.",
        "reversed": "Ignoring your true calling. Harsh self-judgment. Refusing to evolve. Stuck in past guilt instead of rising above.",
        "love_up": "Relationship reaching higher purpose. Past relationship karma resolved. Soul-level love decision.",
        "love_rev": "Judging partner too harshly. Stuck in past relationship pain. Forgive to move forward.",
        "career_up": "True calling revealed. Career purpose aligned with soul mission. Major positive evaluation.",
        "career_rev": "Ignoring career calling. Self-doubt blocking purpose. Poor self-evaluation.",
        "money_up": "Financial reckoning — positively. Debts cleared, karma balanced. Reward for past efforts.",
        "money_rev": "Avoiding financial accountability. Past money mistakes haunting you.",
        "health_up": "Health rebirth. Recovery. Answering body's call for change. Spiritual healing.",
        "health_rev": "Refusing to change unhealthy patterns. Self-judgment worsening health.",
        "element": "Fire", "planet": "Pluto",
    },
    {
        "number": 21, "name": "The World", "arcana": "major",
        "keywords_up": ["completion", "achievement", "fulfillment", "wholeness", "travel"],
        "keywords_rev": ["incompletion", "shortcuts", "delayed success", "emptiness", "unfinished"],
        "upright": "COMPLETION! The highest achievement. A major cycle ends in triumph. Fulfillment, wholeness, and celebration. Travel, global success, and cosmic accomplishment. You made it!",
        "reversed": "So close but not quite complete. Shortcuts leaving things unfinished. Delayed completion. Need one more step to reach the finish line.",
        "love_up": "Relationship fulfillment. Long-term love commitment. Feeling complete with partner.",
        "love_rev": "Relationship feels incomplete. Almost there but something missing. More work needed.",
        "career_up": "Career milestone achieved! Global recognition. Project completed triumphantly.",
        "career_rev": "Career goal almost reached. Final steps remaining. Don't take shortcuts now.",
        "money_up": "Financial goal achieved! Investments matured. Wealth cycle complete.",
        "money_rev": "Financial goal nearly there. Last mile effort needed. Don't settle for less.",
        "health_up": "Full health restored. Wellness cycle complete. Holistic health achieved.",
        "health_rev": "Health recovery almost complete. Don't stop treatment early.",
        "element": "Earth", "planet": "Saturn",
    },
]


# ═══════════════════════════════════════════════════════════════
# 56 MINOR ARCANA (generated by suit)
# ═══════════════════════════════════════════════════════════════

SUIT_INFO = {
    "Wands": {
        "element": "Fire", "domain": "Career, Passion, Action, Energy",
        "color": "#FF6F00",
    },
    "Cups": {
        "element": "Water", "domain": "Emotions, Love, Relationships, Intuition",
        "color": "#1565C0",
    },
    "Swords": {
        "element": "Air", "domain": "Mind, Conflict, Truth, Decisions",
        "color": "#607D8B",
    },
    "Pentacles": {
        "element": "Earth", "domain": "Money, Material, Health, Work",
        "color": "#2E7D32",
    },
}

# Card rank meanings per suit (condensed for all 14 ranks × 4 suits = 56 cards)
MINOR_CARDS = {
    "Wands": [
        ("Ace of Wands", "New creative spark, inspiration, bold beginning, enterprise",
         "Delays, lack of motivation, false start, creative block"),
        ("Two of Wands", "Future planning, progress, decisions, discovery",
         "Fear of unknown, poor planning, indecision, playing it safe"),
        ("Three of Wands", "Expansion, foresight, overseas opportunities, growth",
         "Delays in plans, frustration, obstacles to expansion"),
        ("Four of Wands", "Celebration, harmony, homecoming, community",
         "Lack of harmony, instability, cancelled celebration"),
        ("Five of Wands", "Competition, conflict, disagreement, rivalry",
         "Avoiding conflict, inner conflict, resolution of disputes"),
        ("Six of Wands", "Victory, recognition, success, public acclaim",
         "Ego, fall from grace, lack of recognition, private achievement"),
        ("Seven of Wands", "Defiance, courage, standing ground, perseverance",
         "Giving up, overwhelmed, yielding, losing position"),
        ("Eight of Wands", "Speed, action, movement, swift change, travel",
         "Delays, frustration, waiting, stalled projects"),
        ("Nine of Wands", "Resilience, grit, persistence, last stand, courage",
         "Exhaustion, paranoia, giving up, overwhelmed, burnout"),
        ("Ten of Wands", "Burden, responsibility, hard work, overcommitment",
         "Release burden, delegation, breakdown, too much pressure"),
        ("Page of Wands", "Adventure, excitement, new ideas, free spirit",
         "Lack of direction, haste, procrastination, immaturity"),
        ("Knight of Wands", "Energy, passion, adventure, impulsiveness",
         "Reckless, impatient, scattered, delayed travel"),
        ("Queen of Wands", "Confidence, independence, warmth, determination",
         "Jealousy, insecurity, selfishness, demanding nature"),
        ("King of Wands", "Leadership, vision, entrepreneur, bold action",
         "Impulsiveness, tyranny, vicious temper, unrealistic"),
    ],
    "Cups": [
        ("Ace of Cups", "New love, compassion, emotional beginning, creativity",
         "Blocked emotions, emptiness, repressed feelings"),
        ("Two of Cups", "Partnership, unity, mutual love, connection",
         "Breakup, imbalance, disconnection, trust issues"),
        ("Three of Cups", "Celebration, friendship, community, joy",
         "Overindulgence, gossip, isolation, cancelled event"),
        ("Four of Cups", "Apathy, contemplation, discontent, missed opportunity",
         "Awakening, new motivation, acceptance, seizing chance"),
        ("Five of Cups", "Loss, grief, regret, disappointment, focusing on negative",
         "Moving on, acceptance, forgiveness, finding peace"),
        ("Six of Cups", "Nostalgia, childhood, innocence, reunion, past memories",
         "Stuck in past, unrealistic nostalgia, moving forward"),
        ("Seven of Cups", "Fantasy, illusion, many choices, wishful thinking",
         "Clarity, focus, making a choice, grounding dreams"),
        ("Eight of Cups", "Walking away, abandonment, seeking deeper meaning",
         "Fear of leaving, stagnation, aimless drifting"),
        ("Nine of Cups", "Wishes fulfilled, contentment, satisfaction, luxury",
         "Greed, dissatisfaction, materialism, unfulfilled wishes"),
        ("Ten of Cups", "Happiness, family, emotional fulfillment, harmony",
         "Broken family, domestic strife, misalignment of values"),
        ("Page of Cups", "Creative opportunity, intuitive message, inner child",
         "Emotional immaturity, insecurity, creative block"),
        ("Knight of Cups", "Romance, charm, imagination, beauty, idealism",
         "Unrealistic, jealousy, moodiness, unreliable lover"),
        ("Queen of Cups", "Compassion, calm, intuitive, nurturing, empathic",
         "Insecurity, codependency, emotional manipulation"),
        ("King of Cups", "Emotional balance, diplomacy, wisdom, compassion",
         "Emotional manipulation, moodiness, cold detachment"),
    ],
    "Swords": [
        ("Ace of Swords", "Clarity, breakthrough, truth, new idea, mental power",
         "Confusion, chaos, miscommunication, destructive force"),
        ("Two of Swords", "Difficult decision, stalemate, avoidance, blocked emotions",
         "Indecision broken, confusion, information overload"),
        ("Three of Swords", "Heartbreak, sorrow, grief, betrayal, pain",
         "Recovery, healing, forgiveness, releasing pain"),
        ("Four of Swords", "Rest, recovery, contemplation, meditation, retreat",
         "Burnout, restlessness, refusal to rest, stagnation"),
        ("Five of Swords", "Conflict, defeat, hostility, winning at all costs",
         "Reconciliation, moving on, forgiveness, picking battles"),
        ("Six of Swords", "Transition, moving on, leaving trouble behind, journey",
         "Stuck, resisting transition, unresolved baggage"),
        ("Seven of Swords", "Deception, strategy, stealth, cunning, theft",
         "Coming clean, confession, getting caught, conscience"),
        ("Eight of Swords", "Trapped, restricted, victim mentality, self-limiting",
         "Freedom, new perspective, release, empowerment"),
        ("Nine of Swords", "Anxiety, nightmares, worry, despair, mental anguish",
         "Hope, recovery, reaching out, releasing anxiety"),
        ("Ten of Swords", "Rock bottom, ending, betrayal, hitting the wall",
         "Recovery, regeneration, worst is over, new dawn"),
        ("Page of Swords", "Curiosity, new ideas, thirst for knowledge, vigilance",
         "Gossip, haste, all talk no action, deception"),
        ("Knight of Swords", "Ambition, fast action, determination, charge ahead",
         "Reckless, impatient, scattered thoughts, aggression"),
        ("Queen of Swords", "Independent, unbiased, clear boundaries, direct",
         "Cold, cruel, bitter, overly critical, isolated"),
        ("King of Swords", "Intellectual power, authority, truth, ethical leadership",
         "Manipulative, tyranny, abuse of power, cold logic"),
    ],
    "Pentacles": [
        ("Ace of Pentacles", "New financial opportunity, prosperity, abundance, manifestation",
         "Lost opportunity, poor planning, financial instability"),
        ("Two of Pentacles", "Balance, adaptability, time management, juggling priorities",
         "Overwhelmed, disorganized, financial imbalance"),
        ("Three of Pentacles", "Teamwork, collaboration, skill, craftsmanship",
         "Lack of teamwork, poor quality, disharmony at work"),
        ("Four of Pentacles", "Security, conservation, control, possessiveness",
         "Greed, hoarding, financial insecurity, letting go"),
        ("Five of Pentacles", "Financial loss, poverty, hardship, isolation, worry",
         "Recovery from loss, spiritual wealth, finding help"),
        ("Six of Pentacles", "Generosity, charity, giving and receiving, balance",
         "Debt, one-sided generosity, strings attached, greed"),
        ("Seven of Pentacles", "Patience, long-term view, perseverance, investment",
         "Impatience, bad investment, lack of growth, frustration"),
        ("Eight of Pentacles", "Mastery, skill development, diligence, craftsmanship",
         "Perfectionism, lack of ambition, sloppy work, boredom"),
        ("Nine of Pentacles", "Luxury, independence, self-sufficiency, abundance",
         "Financial setback, overinvestment, living beyond means"),
        ("Ten of Pentacles", "Wealth, inheritance, family fortune, long-term success",
         "Financial failure, family disputes over money, debt"),
        ("Page of Pentacles", "Ambition, desire to learn, new venture, opportunity",
         "Laziness, missed opportunity, procrastination, lack of progress"),
        ("Knight of Pentacles", "Hard work, routine, responsibility, reliability",
         "Boredom, laziness, stuck in routine, perfectionism"),
        ("Queen of Pentacles", "Nurturing, practical, financial security, homebody",
         "Financial insecurity, work-home imbalance, neglecting self"),
        ("King of Pentacles", "Wealth, business, leadership, security, discipline",
         "Greed, materialism, stubbornness, financial loss"),
    ],
}


def _build_minor_arcana() -> List[Dict]:
    """Build the 56 Minor Arcana card dicts."""
    cards = []
    for suit, card_list in MINOR_CARDS.items():
        info = SUIT_INFO[suit]
        for i, (name, up_meaning, rev_meaning) in enumerate(card_list):
            cards.append({
                "number": i + 1,
                "name": name,
                "arcana": "minor",
                "suit": suit,
                "element": info["element"],
                "domain": info["domain"],
                "upright": up_meaning,
                "reversed": rev_meaning,
                "keywords_up": [w.strip() for w in up_meaning.split(",")[:4]],
                "keywords_rev": [w.strip() for w in rev_meaning.split(",")[:4]],
            })
    return cards


# Build full 78-card deck
FULL_DECK = MAJOR_ARCANA + _build_minor_arcana()


# ═══════════════════════════════════════════════════════════════
# COMBINATION ANALYSIS
# ═══════════════════════════════════════════════════════════════

def _analyze_combination(cards: List[Dict]) -> Dict:
    """Analyze the combination of drawn cards."""
    num_cards = len(cards)
    # Count arcana types (needed for single card too)
    majors = [c for c in cards if c["arcana"] == "major"]
    minors = [c for c in cards if c["arcana"] == "minor"]
    major_pct = len(majors) / num_cards * 100

    # Count suits
    suits = {}
    for c in minors:
        s = c.get("suit", "Unknown")
        suits[s] = suits.get(s, 0) + 1
    dominant_suit = max(suits, key=suits.get) if suits else None

    # Count elements
    elements = {}
    for c in cards:
        e = c.get("element", "Unknown")
        elements[e] = elements.get(e, 0) + 1
    dominant_element = max(elements, key=elements.get) if elements else None

    # Count reversals
    reversals = sum(1 for c in cards if c.get("is_reversed"))
    reversal_pct = reversals / num_cards * 100

    # Overall energy
    energy_msgs = []
    if major_pct >= 60:
        energy_msgs.append("Heavy Major Arcana presence — this is a DESTINY-LEVEL reading. Major life forces at work. Pay close attention.")
    elif major_pct == 0 and num_cards >= 3:
        energy_msgs.append("All Minor Arcana — this is about day-to-day situations. Practical matters and personal choices.")

    SUIT_ENERGY = {
        "Wands": "Dominant Wands energy — Focus is on CAREER, PASSION, and ACTION. Creative fire is burning. Take bold steps.",
        "Cups": "Dominant Cups energy — Focus is on EMOTIONS, LOVE, and RELATIONSHIPS. Heart matters take priority. Feel deeply.",
        "Swords": "Dominant Swords energy — Focus is on MIND, CONFLICT, and DECISIONS. Mental clarity needed. Truth must be faced.",
        "Pentacles": "Dominant Pentacles energy — Focus is on MONEY, MATERIAL MATTERS, and HEALTH. Practical concerns dominate. Build wealth.",
    }
    if dominant_suit and suits.get(dominant_suit, 0) >= 2:
        energy_msgs.append(SUIT_ENERGY.get(dominant_suit, ""))

    ELEMENT_ENERGY = {
        "Fire": "Fire dominant — Passion, energy, action, ambition. Move fast and be bold.",
        "Water": "Water dominant — Emotions, intuition, dreams, healing. Trust your feelings.",
        "Air": "Air dominant — Thinking, communication, ideas, decisions. Use your mind.",
        "Earth": "Earth dominant — Material, practical, financial, health. Stay grounded.",
    }
    if dominant_element and elements.get(dominant_element, 0) >= 2:
        energy_msgs.append(ELEMENT_ENERGY.get(dominant_element, ""))

    if reversal_pct >= 60:
        energy_msgs.append("Many reversals — Internal work needed. Blockages, delays, or shadow aspects active. Look within before acting.")
    elif reversal_pct == 0 and num_cards >= 3:
        energy_msgs.append("All upright — Positive flow! Energies are aligned and moving forward. Green light.")

    # Special combos
    card_names = [c["name"] for c in cards]
    special = []
    if "The Sun" in card_names:
        special.append("The Sun is present — Overall positive reading regardless of other cards. Joy and success guaranteed.")
    if "The Tower" in card_names and "The Star" in card_names:
        special.append("Tower + Star combo — Destruction leads to hope. After the crisis, beautiful renewal awaits.")
    if "Death" in card_names and "The World" in card_names:
        special.append("Death + World — End of a major cycle leading to ultimate fulfillment. Transformation complete.")
    if "The Lovers" in card_names and any("Cups" in c.get("suit", "") for c in cards):
        special.append("Lovers + Cups — Very strong love energy. Romantic fulfillment highly likely.")
    if "Wheel of Fortune" in card_names:
        special.append("Wheel of Fortune present — Fate and destiny are actively at work. Lucky timing.")
    if "The Devil" in card_names and "Strength" in card_names:
        special.append("Devil + Strength — You have the inner power to break free from what binds you.")
    if "The Magician" in card_names:
        special.append("The Magician present — You have ALL the tools to manifest your desires. Use them.")

    # Positional meanings
    positions = {}
    if num_cards == 1:
        positions = {"card_1": "Your Card"}
    elif num_cards == 2:
        positions = {"card_1": "Situation/Challenge", "card_2": "Advice/Outcome"}
    elif num_cards == 3:
        positions = {"card_1": "Past", "card_2": "Present", "card_3": "Future"}
    elif num_cards == 4:
        positions = {"card_1": "Past", "card_2": "Present", "card_3": "Advice", "card_4": "Outcome"}
    elif num_cards == 5:
        positions = {"card_1": "Past", "card_2": "Present", "card_3": "Hidden Influences",
                     "card_4": "Advice", "card_5": "Outcome"}

    return {
        "num_cards": num_cards,
        "major_count": len(majors),
        "minor_count": len(minors),
        "major_percentage": round(major_pct),
        "suits": suits,
        "dominant_suit": dominant_suit,
        "elements": elements,
        "dominant_element": dominant_element,
        "reversals": reversals,
        "reversal_percentage": round(reversal_pct),
        "energy_analysis": energy_msgs,
        "special_combos": special,
        "positions": positions,
        "summary": " ".join(energy_msgs) if energy_msgs else (
            "Single card reading — focus entirely on this card's message." if num_cards == 1
            else "Balanced energy spread. Take each card's message individually."
        ),
    }


# ═══════════════════════════════════════════════════════════════
# MAIN DRAW FUNCTION
# ═══════════════════════════════════════════════════════════════

def draw_tarot(num_cards: int = 3, question: Optional[str] = None) -> Dict:
    """
    Draw 1-5 random tarot cards with upright/reversed determination.
    Returns cards with full meanings + automatic combination analysis.
    """
    num_cards = max(1, min(5, num_cards))

    # Shuffle and draw
    deck_indices = list(range(len(FULL_DECK)))
    random.shuffle(deck_indices)
    drawn_indices = deck_indices[:num_cards]

    cards = []
    for idx in drawn_indices:
        card = dict(FULL_DECK[idx])  # copy
        # 30% chance of reversal (traditional probability)
        is_reversed = random.random() < 0.30
        card["is_reversed"] = is_reversed
        card["orientation"] = "reversed" if is_reversed else "upright"
        card["active_meaning"] = card["reversed"] if is_reversed else card["upright"]
        card["active_keywords"] = card.get("keywords_rev", []) if is_reversed else card.get("keywords_up", [])
        cards.append(card)

    # Combination analysis
    combo = _analyze_combination(cards)

    # Add position labels
    for i, card in enumerate(cards):
        pos_key = f"card_{i+1}"
        card["position"] = combo["positions"].get(pos_key, f"Card {i+1}")

    # Spread type
    SPREAD_NAMES = {
        1: "Single Card — Quick Guidance",
        2: "Two Card — Situation & Advice",
        3: "Three Card — Past, Present, Future",
        4: "Four Card — Situation, Present, Advice, Outcome",
        5: "Five Card — Celtic Cross Mini",
    }

    return {
        "spread_type": SPREAD_NAMES.get(num_cards, f"{num_cards}-Card Spread"),
        "num_cards": num_cards,
        "question": question,
        "cards": cards,
        "combination_analysis": combo,
        "deck_size": len(FULL_DECK),
    }
