"""
cities.py — City database with coordinates and timezone.
==========================================================
Embedded database of major world cities. No external API needed.
Covers all Indian cities + major global cities.
Lookup by partial name match (case-insensitive).
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from core.types import LocationInfo

# Format: "City, State/Country": (latitude, longitude, tz_offset_hours, country)
CITY_DB: Dict[str, Tuple[float, float, float, str]] = {
    # ─── India (Major + Tier-2) ──────────────────────────────
    "Mumbai, Maharashtra": (19.0760, 72.8777, 5.5, "India"),
    "Delhi": (28.6139, 77.2090, 5.5, "India"),
    "New Delhi": (28.6139, 77.2090, 5.5, "India"),
    "Bengaluru, Karnataka": (12.9716, 77.5946, 5.5, "India"),
    "Bangalore": (12.9716, 77.5946, 5.5, "India"),
    "Chennai, Tamil Nadu": (13.0827, 80.2707, 5.5, "India"),
    "Kolkata, West Bengal": (22.5726, 88.3639, 5.5, "India"),
    "Hyderabad, Telangana": (17.3850, 78.4867, 5.5, "India"),
    "Ahmedabad, Gujarat": (23.0225, 72.5714, 5.5, "India"),
    "Pune, Maharashtra": (18.5204, 73.8567, 5.5, "India"),
    "Jaipur, Rajasthan": (26.9124, 75.7873, 5.5, "India"),
    "Ujjain, Madhya Pradesh": (23.1765, 75.7885, 5.5, "India"),
    "Ujjain": (23.1765, 75.7885, 5.5, "India"),
    "Varanasi, Uttar Pradesh": (25.3176, 82.9739, 5.5, "India"),
    "Varanasi": (25.3176, 82.9739, 5.5, "India"),
    "Lucknow, Uttar Pradesh": (26.8467, 80.9462, 5.5, "India"),
    "Lucknow": (26.8467, 80.9462, 5.5, "India"),
    "Kanpur, Uttar Pradesh": (26.4499, 80.3319, 5.5, "India"),
    "Nagpur, Maharashtra": (21.1458, 79.0882, 5.5, "India"),
    "Indore, Madhya Pradesh": (22.7196, 75.8577, 5.5, "India"),
    "Bhopal, Madhya Pradesh": (23.2599, 77.4126, 5.5, "India"),
    "Patna, Bihar": (25.6093, 85.1376, 5.5, "India"),
    "Surat, Gujarat": (21.1702, 72.8311, 5.5, "India"),
    "Coimbatore, Tamil Nadu": (11.0168, 76.9558, 5.5, "India"),
    "Madurai, Tamil Nadu": (9.9252, 78.1198, 5.5, "India"),
    "Thiruvananthapuram, Kerala": (8.5241, 76.9366, 5.5, "India"),
    "Kochi, Kerala": (9.9312, 76.2673, 5.5, "India"),
    "Visakhapatnam, Andhra Pradesh": (17.6868, 83.2185, 5.5, "India"),
    "Chandigarh": (30.7333, 76.7794, 5.5, "India"),
    "Guwahati, Assam": (26.1445, 91.7362, 5.5, "India"),
    "Amritsar, Punjab": (31.6340, 74.8723, 5.5, "India"),
    "Dehradun, Uttarakhand": (30.3165, 78.0322, 5.5, "India"),
    "Raipur, Chhattisgarh": (21.2514, 81.6296, 5.5, "India"),
    "Ranchi, Jharkhand": (23.3441, 85.3096, 5.5, "India"),
    "Bhubaneswar, Odisha": (20.2961, 85.8245, 5.5, "India"),
    "Mysuru, Karnataka": (12.2958, 76.6394, 5.5, "India"),
    "Jodhpur, Rajasthan": (26.2389, 73.0243, 5.5, "India"),
    "Udaipur, Rajasthan": (24.5854, 73.7125, 5.5, "India"),
    "Agra, Uttar Pradesh": (27.1767, 78.0081, 5.5, "India"),
    "Nashik, Maharashtra": (19.9975, 73.7898, 5.5, "India"),
    "Aurangabad, Maharashtra": (19.8762, 75.3433, 5.5, "India"),
    "Goa": (15.2993, 74.1240, 5.5, "India"),
    "Shimla, Himachal Pradesh": (31.1048, 77.1734, 5.5, "India"),
    "Srinagar, Jammu & Kashmir": (34.0837, 74.7973, 5.5, "India"),
    "Rishikesh, Uttarakhand": (30.0869, 78.2676, 5.5, "India"),
    "Haridwar, Uttarakhand": (29.9457, 78.1642, 5.5, "India"),
    "Tirupati, Andhra Pradesh": (13.6288, 79.4192, 5.5, "India"),
    "Prayagraj, Uttar Pradesh": (25.4358, 81.8463, 5.5, "India"),
    "Allahabad": (25.4358, 81.8463, 5.5, "India"),
    "Gwalior, Madhya Pradesh": (26.2183, 78.1828, 5.5, "India"),
    "Jabalpur, Madhya Pradesh": (23.1815, 79.9864, 5.5, "India"),
    "Thane, Maharashtra": (19.2183, 72.9781, 5.5, "India"),
    "Noida, Uttar Pradesh": (28.5355, 77.3910, 5.5, "India"),
    "Gurugram, Haryana": (28.4595, 77.0266, 5.5, "India"),
    "Faridabad, Haryana": (28.4089, 77.3178, 5.5, "India"),
    "Mangalore, Karnataka": (12.9141, 74.8560, 5.5, "India"),
    "Hubli, Karnataka": (15.3647, 75.1240, 5.5, "India"),

    # ─── Nepal / Sri Lanka / Bangladesh / Pakistan ───────────
    "Kathmandu, Nepal": (27.7172, 85.3240, 5.75, "Nepal"),
    "Colombo, Sri Lanka": (6.9271, 79.8612, 5.5, "Sri Lanka"),
    "Dhaka, Bangladesh": (23.8103, 90.4125, 6.0, "Bangladesh"),
    "Karachi, Pakistan": (24.8607, 67.0011, 5.0, "Pakistan"),
    "Lahore, Pakistan": (31.5204, 74.3587, 5.0, "Pakistan"),
    "Islamabad, Pakistan": (33.6844, 73.0479, 5.0, "Pakistan"),

    # ─── Middle East ─────────────────────────────────────────
    "Dubai, UAE": (25.2048, 55.2708, 4.0, "UAE"),
    "Abu Dhabi, UAE": (24.4539, 54.3773, 4.0, "UAE"),
    "Riyadh, Saudi Arabia": (24.7136, 46.6753, 3.0, "Saudi Arabia"),
    "Doha, Qatar": (25.2854, 51.5310, 3.0, "Qatar"),
    "Kuwait City, Kuwait": (29.3759, 47.9774, 3.0, "Kuwait"),
    "Muscat, Oman": (23.5880, 58.3829, 4.0, "Oman"),
    "Bahrain": (26.0667, 50.5577, 3.0, "Bahrain"),
    "Tehran, Iran": (35.6892, 51.3890, 3.5, "Iran"),
    "Istanbul, Turkey": (41.0082, 28.9784, 3.0, "Turkey"),

    # ─── Southeast Asia ──────────────────────────────────────
    "Singapore": (1.3521, 103.8198, 8.0, "Singapore"),
    "Bangkok, Thailand": (13.7563, 100.5018, 7.0, "Thailand"),
    "Kuala Lumpur, Malaysia": (3.1390, 101.6869, 8.0, "Malaysia"),
    "Jakarta, Indonesia": (-6.2088, 106.8456, 7.0, "Indonesia"),
    "Manila, Philippines": (14.5995, 120.9842, 8.0, "Philippines"),
    "Hanoi, Vietnam": (21.0278, 105.8342, 7.0, "Vietnam"),
    "Yangon, Myanmar": (16.8661, 96.1951, 6.5, "Myanmar"),

    # ─── East Asia ───────────────────────────────────────────
    "Tokyo, Japan": (35.6762, 139.6503, 9.0, "Japan"),
    "Beijing, China": (39.9042, 116.4074, 8.0, "China"),
    "Shanghai, China": (31.2304, 121.4737, 8.0, "China"),
    "Hong Kong": (22.3193, 114.1694, 8.0, "China"),
    "Seoul, South Korea": (37.5665, 126.9780, 9.0, "South Korea"),
    "Taipei, Taiwan": (25.0330, 121.5654, 8.0, "Taiwan"),

    # ─── Europe ──────────────────────────────────────────────
    "London, UK": (51.5074, -0.1278, 0.0, "UK"),
    "Paris, France": (48.8566, 2.3522, 1.0, "France"),
    "Berlin, Germany": (52.5200, 13.4050, 1.0, "Germany"),
    "Frankfurt, Germany": (50.1109, 8.6821, 1.0, "Germany"),
    "Amsterdam, Netherlands": (52.3676, 4.9041, 1.0, "Netherlands"),
    "Zurich, Switzerland": (47.3769, 8.5417, 1.0, "Switzerland"),
    "Rome, Italy": (41.9028, 12.4964, 1.0, "Italy"),
    "Madrid, Spain": (40.4168, -3.7038, 1.0, "Spain"),
    "Moscow, Russia": (55.7558, 37.6173, 3.0, "Russia"),
    "Stockholm, Sweden": (59.3293, 18.0686, 1.0, "Sweden"),
    "Vienna, Austria": (48.2082, 16.3738, 1.0, "Austria"),
    "Brussels, Belgium": (50.8503, 4.3517, 1.0, "Belgium"),
    "Dublin, Ireland": (53.3498, -6.2603, 0.0, "Ireland"),
    "Lisbon, Portugal": (38.7223, -9.1393, 0.0, "Portugal"),
    "Athens, Greece": (37.9838, 23.7275, 2.0, "Greece"),
    "Warsaw, Poland": (52.2297, 21.0122, 1.0, "Poland"),
    "Prague, Czech Republic": (50.0755, 14.4378, 1.0, "Czech Republic"),
    "Budapest, Hungary": (47.4979, 19.0402, 1.0, "Hungary"),
    "Helsinki, Finland": (60.1699, 24.9384, 2.0, "Finland"),
    "Oslo, Norway": (59.9139, 10.7522, 1.0, "Norway"),
    "Copenhagen, Denmark": (55.6761, 12.5683, 1.0, "Denmark"),
    "Edinburgh, UK": (55.9533, -3.1883, 0.0, "UK"),
    "Manchester, UK": (53.4808, -2.2426, 0.0, "UK"),

    # ─── Americas ────────────────────────────────────────────
    "New York, USA": (40.7128, -74.0060, -5.0, "USA"),
    "Los Angeles, USA": (34.0522, -118.2437, -8.0, "USA"),
    "Chicago, USA": (41.8781, -87.6298, -6.0, "USA"),
    "Houston, USA": (29.7604, -95.3698, -6.0, "USA"),
    "San Francisco, USA": (37.7749, -122.4194, -8.0, "USA"),
    "Washington DC, USA": (38.9072, -77.0369, -5.0, "USA"),
    "Toronto, Canada": (43.6532, -79.3832, -5.0, "Canada"),
    "Vancouver, Canada": (49.2827, -123.1207, -8.0, "Canada"),
    "Mexico City, Mexico": (19.4326, -99.1332, -6.0, "Mexico"),
    "Sao Paulo, Brazil": (-23.5505, -46.6333, -3.0, "Brazil"),
    "Buenos Aires, Argentina": (-34.6037, -58.3816, -3.0, "Argentina"),
    "Lima, Peru": (-12.0464, -77.0428, -5.0, "Peru"),
    "Bogota, Colombia": (4.7110, -74.0721, -5.0, "Colombia"),
    "Santiago, Chile": (-33.4489, -70.6693, -4.0, "Chile"),

    # ─── Africa ──────────────────────────────────────────────
    "Cairo, Egypt": (30.0444, 31.2357, 2.0, "Egypt"),
    "Nairobi, Kenya": (-1.2921, 36.8219, 3.0, "Kenya"),
    "Lagos, Nigeria": (6.5244, 3.3792, 1.0, "Nigeria"),
    "Johannesburg, South Africa": (-26.2041, 28.0473, 2.0, "South Africa"),
    "Cape Town, South Africa": (-33.9249, 18.4241, 2.0, "South Africa"),
    "Addis Ababa, Ethiopia": (9.0250, 38.7469, 3.0, "Ethiopia"),
    "Casablanca, Morocco": (33.5731, -7.5898, 1.0, "Morocco"),

    # ─── Oceania ─────────────────────────────────────────────
    "Sydney, Australia": (-33.8688, 151.2093, 10.0, "Australia"),
    "Melbourne, Australia": (-37.8136, 144.9631, 10.0, "Australia"),
    "Auckland, New Zealand": (-36.8485, 174.7633, 12.0, "New Zealand"),
    "Perth, Australia": (-31.9505, 115.8605, 8.0, "Australia"),
}


def search_city(query: str, limit: int = 10) -> List[Dict]:
    """
    Search cities by partial name match.
    Returns list of matching cities with coordinates.
    """
    q = query.lower().strip()
    if not q:
        return []

    results = []
    for name, (lat, lon, tz, country) in CITY_DB.items():
        if q in name.lower():
            results.append({
                "name": name,
                "country": country,
                "latitude": lat,
                "longitude": lon,
                "tz_offset": tz,
                "display": f"{name}, {country}" if country not in name else name,
            })
            if len(results) >= limit:
                break

    # Sort: exact start match first, then alphabetical
    results.sort(key=lambda x: (0 if x["name"].lower().startswith(q) else 1, x["name"]))
    return results


def resolve_city(query: str) -> Optional[LocationInfo]:
    """
    Resolve a city name to LocationInfo.
    First tries exact match, then partial match (returns best).
    """
    q = query.strip()

    # Exact match (case-insensitive)
    for name, (lat, lon, tz, country) in CITY_DB.items():
        if name.lower() == q.lower():
            return LocationInfo(name=name, latitude=lat, longitude=lon, tz_offset=tz)

    # Partial match — return first hit
    results = search_city(q, limit=1)
    if results:
        r = results[0]
        return LocationInfo(
            name=r["display"],
            latitude=r["latitude"],
            longitude=r["longitude"],
            tz_offset=r["tz_offset"],
        )

    return None
