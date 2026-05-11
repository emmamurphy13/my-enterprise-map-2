import csv
import json
import math
import os
import re
import ssl
import time
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
DEFAULT_CSV_PATH = ROOT / 'ARPA_New_Construction_Projects_Q3_2025_Filtered.csv'
CSV_PATH = Path(os.environ.get('ARPA_CSV_PATH', str(DEFAULT_CSV_PATH))).expanduser()
COUNTY_GEOJSON_PATH = ROOT / 'static/data/us-counties.geojson'
OUTPUT_PATH = ROOT / 'static/data/arpa-project-points.geojson'
CACHE_PATH = ROOT / 'src/lib/data/city-geocode-cache.json'

STATE_FIPS = {
    'alabama': '01',
    'alaska': '02',
    'arizona': '04',
    'arkansas': '05',
    'california': '06',
    'colorado': '08',
    'connecticut': '09',
    'delaware': '10',
    'district of columbia': '11',
    'florida': '12',
    'georgia': '13',
    'hawaii': '15',
    'idaho': '16',
    'illinois': '17',
    'indiana': '18',
    'iowa': '19',
    'kansas': '20',
    'kentucky': '21',
    'louisiana': '22',
    'maine': '23',
    'maryland': '24',
    'massachusetts': '25',
    'michigan': '26',
    'minnesota': '27',
    'mississippi': '28',
    'missouri': '29',
    'montana': '30',
    'nebraska': '31',
    'nevada': '32',
    'new hampshire': '33',
    'new jersey': '34',
    'new mexico': '35',
    'new york': '36',
    'north carolina': '37',
    'north dakota': '38',
    'ohio': '39',
    'oklahoma': '40',
    'oregon': '41',
    'pennsylvania': '42',
    'rhode island': '44',
    'south carolina': '45',
    'south dakota': '46',
    'tennessee': '47',
    'texas': '48',
    'utah': '49',
    'vermont': '50',
    'virginia': '51',
    'washington': '53',
    'west virginia': '54',
    'wisconsin': '55',
    'wyoming': '56',
}

STATE_ABBREVIATIONS = {
    'alabama': 'AL',
    'alaska': 'AK',
    'arizona': 'AZ',
    'arkansas': 'AR',
    'california': 'CA',
    'colorado': 'CO',
    'connecticut': 'CT',
    'delaware': 'DE',
    'district of columbia': 'DC',
    'florida': 'FL',
    'georgia': 'GA',
    'hawaii': 'HI',
    'idaho': 'ID',
    'illinois': 'IL',
    'indiana': 'IN',
    'iowa': 'IA',
    'kansas': 'KS',
    'kentucky': 'KY',
    'louisiana': 'LA',
    'maine': 'ME',
    'maryland': 'MD',
    'massachusetts': 'MA',
    'michigan': 'MI',
    'minnesota': 'MN',
    'mississippi': 'MS',
    'missouri': 'MO',
    'montana': 'MT',
    'nebraska': 'NE',
    'nevada': 'NV',
    'new hampshire': 'NH',
    'new jersey': 'NJ',
    'new mexico': 'NM',
    'new york': 'NY',
    'north carolina': 'NC',
    'north dakota': 'ND',
    'ohio': 'OH',
    'oklahoma': 'OK',
    'oregon': 'OR',
    'pennsylvania': 'PA',
    'rhode island': 'RI',
    'south carolina': 'SC',
    'south dakota': 'SD',
    'tennessee': 'TN',
    'texas': 'TX',
    'utah': 'UT',
    'vermont': 'VT',
    'virginia': 'VA',
    'washington': 'WA',
    'west virginia': 'WV',
    'wisconsin': 'WI',
    'wyoming': 'WY',
}

STATE_CENTROIDS = {
    'AL': (-86.8, 32.8), 'AK': (-152.0, 64.0), 'AZ': (-111.6, 34.2), 'AR': (-92.4, 34.9),
    'CA': (-119.4, 37.2), 'CO': (-105.5, 39.0), 'CT': (-72.7, 41.6), 'DE': (-75.5, 39.0),
    'DC': (-77.0, 38.9), 'FL': (-81.5, 27.8), 'GA': (-83.6, 32.7), 'HI': (-157.5, 20.8),
    'ID': (-114.6, 44.2), 'IL': (-89.4, 40.0), 'IN': (-86.1, 40.0), 'IA': (-93.5, 42.1),
    'KS': (-98.2, 38.5), 'KY': (-85.0, 37.8), 'LA': (-92.0, 31.0), 'ME': (-69.0, 45.3),
    'MD': (-76.7, 39.0), 'MA': (-71.8, 42.3), 'MI': (-84.6, 44.3), 'MN': (-94.3, 46.3),
    'MS': (-89.7, 32.7), 'MO': (-92.5, 38.5), 'MT': (-110.9, 46.9), 'NE': (-99.8, 41.5),
    'NV': (-116.7, 39.4), 'NH': (-71.6, 43.9), 'NJ': (-74.5, 40.1), 'NM': (-106.1, 34.4),
    'NY': (-75.0, 43.0), 'NC': (-79.4, 35.6), 'ND': (-100.5, 47.5), 'OH': (-82.8, 40.3),
    'OK': (-97.5, 35.5), 'OR': (-120.6, 44.1), 'PA': (-77.7, 40.9), 'RI': (-71.5, 41.7),
    'SC': (-80.9, 33.9), 'SD': (-100.2, 44.4), 'TN': (-86.4, 35.8), 'TX': (-99.3, 31.4),
    'UT': (-111.6, 39.3), 'VT': (-72.7, 44.1), 'VA': (-78.7, 37.5), 'WA': (-120.5, 47.4),
    'WV': (-80.6, 38.6), 'WI': (-89.6, 44.6), 'WY': (-107.6, 43.0),
}

COUNTY_SUFFIXES = ('county', 'parish', 'borough', 'census area', 'municipality', 'city and borough')
CITY_PREFIXES = ('city of ', 'town of ', 'village of ', 'city ', 'town ', 'village ')


def slug(value: str) -> str:
    return re.sub(r'[^a-z0-9]+', ' ', value.lower()).strip()


def parse_money(value: str) -> int:
    cleaned = value.replace('$', '').replace(',', '').strip()
    if not cleaned:
        return 0
    try:
        return int(float(cleaned))
    except ValueError:
        return 0


def bbox_center(geometry: dict) -> tuple[float, float]:
    xs: list[float] = []
    ys: list[float] = []

    def walk(coords):
        if isinstance(coords, list) and coords:
            if isinstance(coords[0], (int, float)) and len(coords) >= 2:
                xs.append(float(coords[0]))
                ys.append(float(coords[1]))
            else:
                for child in coords:
                    walk(child)

    walk(geometry.get('coordinates', []))
    return ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)


def load_county_centroids() -> dict[tuple[str, str], tuple[float, float]]:
    geo = json.loads(COUNTY_GEOJSON_PATH.read_text())
    lookup: dict[tuple[str, str], tuple[float, float]] = {}
    for feature in geo['features']:
        state = feature['properties']['STATE']
        name = slug(feature['properties']['NAME'])
        lookup[(state, name)] = bbox_center(feature['geometry'])
    return lookup


def clean_name(name: str) -> str:
    value = name.lower().strip().strip('"').strip(', ')
    value = re.sub(r',\s*[a-z\.\s]+$', '', value).strip()
    value = value.replace('st.', 'st').replace('ste.', 'ste')
    return value


def county_candidates(recipient_name: str) -> list[str]:
    value = clean_name(recipient_name)
    value = re.sub(r'^(county of|parish of|borough of|municipality of)\s+', '', value)
    value = re.sub(r'\s+unified government$', '', value).strip()
    candidates = [value]
    for suffix in COUNTY_SUFFIXES:
        if suffix in value:
            base = value.replace(suffix, '').strip()
            candidates.extend([f'{base} {suffix}'.strip(), base])
            break
    dedup = []
    seen = set()
    for c in candidates:
        s = slug(c)
        if s not in seen:
            seen.add(s)
            dedup.append(s)
    return dedup


def city_name_from_recipient(recipient_name: str) -> str:
    value = clean_name(recipient_name)
    for prefix in CITY_PREFIXES:
        if value.startswith(prefix):
            return value[len(prefix):].strip()
    if ',' in value:
        return value.split(',')[0].strip()
    return value.strip()


def looks_like_county(recipient_name: str) -> bool:
    lower = recipient_name.lower()
    return any(term in lower for term in COUNTY_SUFFIXES) or 'county of' in lower


def looks_like_city(recipient_name: str) -> bool:
    lower = recipient_name.lower().strip()
    return lower.startswith('city ') or lower.startswith('city of ') or lower.startswith('town ') or lower.startswith('town of ') or lower.startswith('village ') or lower.startswith('village of ')


def load_cache() -> dict:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text())
    return {}


def save_cache(cache: dict) -> None:
    CACHE_PATH.write_text(json.dumps(cache, indent=2, sort_keys=True))


def geocode_city(city: str, state: str, cache: dict) -> tuple[float, float] | None:
    key = f'{city}|{state}'
    if key in cache:
        value = cache[key]
        if value is None:
            return None
        return tuple(value)

    query = quote(f'{city}, {state}, United States')
    url = f'https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=1'
    request = Request(url, headers={'User-Agent': 'coding-the-news-map-builder/1.0'})
    context = ssl._create_unverified_context()

    try:
        with urlopen(request, timeout=20, context=context) as response:
            payload = json.loads(response.read().decode('utf-8'))
        if payload:
            lng = float(payload[0]['lon'])
            lat = float(payload[0]['lat'])
            cache[key] = [lng, lat]
            time.sleep(0.8)
            return lng, lat
        cache[key] = None
        time.sleep(0.8)
        return None
    except Exception:
        cache[key] = None
        time.sleep(0.8)
        return None


def jitter(lng: float, lat: float, index: int) -> tuple[float, float]:
    if index == 0:
        return lng, lat
    ring = int(math.floor((math.sqrt(index - 1) + 1)))
    theta = (index * 137.5) * math.pi / 180.0
    radius_deg = 0.06 * ring
    return lng + radius_deg * math.cos(theta), lat + radius_deg * math.sin(theta)


def main() -> None:
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f'Input CSV not found at {CSV_PATH}. Set ARPA_CSV_PATH to your filtered CSV path.'
        )

    county_centroids = load_county_centroids()
    city_cache = load_cache()

    with CSV_PATH.open(newline='', encoding='utf-8-sig') as csv_file:
        rows = list(csv.DictReader(csv_file))

    features = []
    status_counts = defaultdict(int)

    for row in rows:
        recipient_name = row['Recipient Name']
        state_name = row['State/Territory'].lower().strip()
        state_abbr = STATE_ABBREVIATIONS.get(state_name)
        state_fips = STATE_FIPS.get(state_name)

        source_type = 'fallback'
        coordinate = None

        if row['Recipient Type'] == 'State/DC' and state_abbr in STATE_CENTROIDS:
            coordinate = STATE_CENTROIDS[state_abbr]
            source_type = 'state-centroid'
        elif looks_like_county(recipient_name) and state_fips:
            for candidate in county_candidates(recipient_name):
                key = (state_fips, candidate)
                if key in county_centroids:
                    coordinate = county_centroids[key]
                    source_type = 'county-centroid'
                    break

        if coordinate is None and state_abbr:
            if looks_like_city(recipient_name) or row['Recipient Type'] == 'Local Government':
                city_name = city_name_from_recipient(recipient_name)
                geocoded = geocode_city(city_name, state_abbr, city_cache)
                if geocoded:
                    coordinate = geocoded
                    source_type = 'city-geocode'

        if coordinate is None and state_abbr in STATE_CENTROIDS:
            coordinate = STATE_CENTROIDS[state_abbr]
            source_type = 'state-fallback'

        if coordinate is None:
            coordinate = (-98.5795, 39.8283)
            source_type = 'us-fallback'

        status_counts[source_type] += 1

        features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [coordinate[0], coordinate[1]],
            },
            'properties': {
                'projectId': row['Project ID'],
                'recipientId': row['Recipient-ID'],
                'recipientName': recipient_name,
                'state': state_abbr or row['State/Territory'],
                'recipientType': row['Recipient Type'],
                'projectName': row['Project Name'],
                'completionStatus': row['Completion Status'] or 'Not reported',
                'categoryGroup': row['Expenditure Category Group'],
                'category': row['Expenditure Category'],
                'description': row['Project Description'],
                'totalObligations': parse_money(row['Total Cumulative Obligations']),
                'totalExpenditures': parse_money(row['Total Cumulative Expenditures']),
                'coordinateSource': source_type,
            },
        })

    # De-stack identical/near-identical coordinates with deterministic spiral jitter.
    grouped = defaultdict(list)
    for feature in features:
        lng, lat = feature['geometry']['coordinates']
        grouped[(round(lng, 4), round(lat, 4))].append(feature)

    for group in grouped.values():
        for index, feature in enumerate(group):
            lng, lat = feature['geometry']['coordinates']
            j_lng, j_lat = jitter(lng, lat, index)
            feature['geometry']['coordinates'] = [j_lng, j_lat]
            feature['properties']['jitterIndex'] = index

    output = {'type': 'FeatureCollection', 'features': features}
    OUTPUT_PATH.write_text(json.dumps(output, indent=2))
    save_cache(city_cache)

    print(f'Wrote {len(features)} points to {OUTPUT_PATH}')
    print('Coordinate sources:', dict(status_counts))


if __name__ == '__main__':
    main()
