import requests


class ExternalAPIError(Exception):
    def __init__(self, api_name):
        self.api_name = api_name
        super().__init__(f'{api_name} returned an invalid response')


def fetch_genderize(name):
    try:
        resp = requests.get(f'https://api.genderize.io', params={'name': name}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        raise ExternalAPIError('Genderize')

    if not data.get('gender') or data.get('count', 0) == 0:
        raise ExternalAPIError('Genderize')

    return {
        'gender': data['gender'],
        'gender_probability': data['probability'],
        'sample_size': data['count'],
    }


def fetch_agify(name):
    try:
        resp = requests.get('https://api.agify.io', params={'name': name}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        raise ExternalAPIError('Agify')

    if data.get('age') is None:
        raise ExternalAPIError('Agify')

    return {'age': data['age']}


def fetch_nationalize(name):
    try:
        resp = requests.get('https://api.nationalize.io', params={'name': name}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        raise ExternalAPIError('Nationalize')

    countries = data.get('country') or []
    if not countries:
        raise ExternalAPIError('Nationalize')

    top = max(countries, key=lambda c: c['probability'])
    return {
        'country_id': top['country_id'],
        'country_probability': top['probability'],
    }


def classify_age(age):
    if age <= 12:
        return 'child'
    elif age <= 19:
        return 'teenager'
    elif age <= 59:
        return 'adult'
    return 'senior'
