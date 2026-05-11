import csv
import json
import os
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_CSV_PATH = ROOT / 'ARPA_New_Construction_Projects_Q3_2025_Filtered.csv'
CSV_PATH = Path(os.environ.get('ARPA_CSV_PATH', str(DEFAULT_CSV_PATH))).expanduser()
COUNTY_GEOJSON_PATH = ROOT / 'static/data/us-counties.geojson'
OUTPUT_PATH = ROOT / 'src/lib/data/county-projects.json'
UNMATCHED_PATH = ROOT / 'src/lib/data/county-projects-unmatched.json'

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
    'american samoa': '60',
    'guam': '66',
    'northern mariana islands': '69',
    'puerto rico': '72',
    'u.s. virgin islands': '78',
    'us virgin islands': '78',
    'virgin islands': '78',
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

COUNTY_SUFFIXES = (
    'county',
    'parish',
    'borough',
    'census area',
    'city and borough',
    'municipality',
)

STATE_TOKENS = sorted(
    {
        *STATE_FIPS.keys(),
        *STATE_ABBREVIATIONS.keys(),
        *STATE_ABBREVIATIONS.values(),
    },
    key=len,
    reverse=True,
)


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


def clean_recipient_name(name: str) -> str:
    value = name.lower().strip().strip('"')
    value = value.rstrip(', ').strip()
    value = re.sub(r',\s*[a-z\.\s]+$', '', value).strip()
    value = value.replace('st.', 'st').replace('ste.', 'ste')
    value = re.sub(r'^(county of|parish of|borough of|municipality of)\s+', '', value)
    value = re.sub(r'^(city and borough of)\s+', '', value)
    value = re.sub(r'\s+unified government$', '', value).strip()
    return value


def strip_state_suffix(value: str) -> str:
    cleaned = value.strip()

    for token in STATE_TOKENS:
        if cleaned.endswith(f' {token}'):
            return cleaned[: -len(token) - 1].strip()

    return cleaned


def county_candidate_names(recipient_name: str) -> list[str]:
    value = strip_state_suffix(clean_recipient_name(recipient_name))
    candidates = []

    for suffix in COUNTY_SUFFIXES:
        if suffix in value:
            base = value.replace(suffix, '').strip()
            base = strip_state_suffix(base)
            candidates.append(f'{base} {suffix}'.strip())
            candidates.append(base)
            break

    if value.startswith('county of '):
        base = strip_state_suffix(value.removeprefix('county of ').strip())
        candidates.append(f'{base} county')

    if ' county' in value:
        candidates.append(value)

    if ' parish' in value:
        candidates.append(value)

    if ' borough' in value:
        candidates.append(value)

    candidates.append(value)

    normalized = []
    seen = set()
    for candidate in candidates:
        normalized_candidate = slug(candidate)
        if normalized_candidate not in seen:
            seen.add(normalized_candidate)
            normalized.append(normalized_candidate)

    return normalized


def load_county_lookup() -> dict[tuple[str, str], dict]:
    geojson = json.loads(COUNTY_GEOJSON_PATH.read_text())
    lookup: dict[tuple[str, str], dict] = {}

    for feature in geojson['features']:
        state_fips = feature['properties']['STATE']
        county_name = slug(feature['properties']['NAME'])
        lookup[(state_fips, county_name)] = {
            'id': feature['id'],
            'name': feature['properties']['NAME'],
        }

    return lookup


def main() -> None:
    county_lookup = load_county_lookup()

    with CSV_PATH.open(newline='', encoding='utf-8-sig') as csv_file:
        rows = list(csv.DictReader(csv_file))

    grouped = defaultdict(lambda: {
        'countyFips': None,
        'countyName': '',
        'state': '',
        'projects': [],
        'totalObligations': 0,
        'totalExpenditures': 0,
    })
    unmatched = []

    for row in rows:
        recipient_name = row['Recipient Name']
        lower_name = recipient_name.lower()
        if not any(term in lower_name for term in COUNTY_SUFFIXES) and 'county of' not in lower_name:
            continue

        state_name = row['State/Territory'].lower().strip()
        state_fips = STATE_FIPS.get(state_name)
        if not state_fips:
            unmatched.append({
                'recipientName': recipient_name,
                'state': row['State/Territory'],
                'reason': 'Unknown state',
            })
            continue

        county_match = None
        for candidate in county_candidate_names(recipient_name):
            county_match = county_lookup.get((state_fips, candidate))
            if county_match:
                break

        if not county_match:
            unmatched.append({
                'recipientName': recipient_name,
                'state': row['State/Territory'],
                'candidates': county_candidate_names(recipient_name),
            })
            continue

        county_id = county_match['id']
        state_abbr = STATE_ABBREVIATIONS[state_name]
        county_label = county_match['name']
        obligations = parse_money(row['Total Cumulative Obligations'])
        expenditures = parse_money(row['Total Cumulative Expenditures'])

        bucket = grouped[county_id]
        bucket['countyFips'] = county_id
        bucket['countyName'] = county_label
        bucket['state'] = state_abbr
        bucket['totalObligations'] += obligations
        bucket['totalExpenditures'] += expenditures
        bucket['projects'].append({
            'projectId': row['Project ID'],
            'recipientId': row['Recipient-ID'],
            'recipientName': recipient_name,
            'projectName': row['Project Name'],
            'state': state_abbr,
            'completionStatus': row['Completion Status'] or 'Not reported',
            'expenditureCategoryGroup': row['Expenditure Category Group'],
            'expenditureCategory': row['Expenditure Category'],
            'description': row['Project Description'],
            'totalObligations': obligations,
            'totalExpenditures': expenditures,
        })

    counties = sorted(
        grouped.values(),
        key=lambda item: (item['totalObligations'], item['totalExpenditures']),
        reverse=True,
    )

    for county in counties:
        county['projects'] = sorted(
            county['projects'],
            key=lambda item: (item['totalObligations'], item['totalExpenditures']),
            reverse=True,
        )
        county['projectCount'] = len(county['projects'])

    OUTPUT_PATH.write_text(json.dumps(counties, indent=2))
    UNMATCHED_PATH.write_text(json.dumps(unmatched, indent=2))

    print(f'Wrote {len(counties)} county groups to {OUTPUT_PATH}')
    print(f'Wrote {len(unmatched)} unmatched county-like rows to {UNMATCHED_PATH}')


if __name__ == '__main__':
    main()
