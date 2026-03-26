import pandas as pd
import numpy as np
import re
from rapidfuzz import fuzz


# ---------------------------
# LOAD
# ---------------------------
def load_data(path):
    return pd.read_csv(path, skipinitialspace=True)


# ---------------------------
# FILTER UUID
# ---------------------------
def filter_valid_uuid(df):
    pattern = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
    df['user_id'] = df['user_id'].astype(str).str.lower().str.strip()
    before = len(df)
    df = df[df['user_id'].str.match(pattern, na=False)]
    print(f"Rimosse {before - len(df)} righe con ID non validi")
    return df


# ---------------------------
# TEXT CLEANING
# ---------------------------
def clean_text_columns(df):
    cols = ['name', 'email', 'city', 'category', 'discount_code']

    for col in cols:
        df[col] = df[col].astype(str)
        df[col] = df[col].str.replace(r'NULL|n/a|xxx', '', flags=re.IGNORECASE, regex=True)
        df[col] = df[col].str.replace(r'[^a-zA-Z0-9@\.\-\s]', '', regex=True)
        df[col] = df[col].str.replace(r'\s+', ' ', regex=True)
        df[col] = df[col].str.strip()
        df[col] = df[col].replace('', np.nan)

    return df


# ---------------------------
# COUNTRY
# ---------------------------
def clean_country(df):
    df['country'] = df['country'].astype(str).str.lower().str.strip()
    df['country'] = df['country'].map({'italia': 'IT', 'italy': 'IT', 'it': 'IT'})
    return df


# ---------------------------
# NUMERIC
# ---------------------------
def clean_numeric(df):
    df['age'] = pd.to_numeric(df['age'], errors='coerce')
    df.loc[(df['age'] < 0) | (df['age'] > 120), 'age'] = np.nan

    df['reviews_count'] = df['reviews_count'].replace('many', np.nan)
    df['reviews_count'] = pd.to_numeric(df['reviews_count'], errors='coerce')

    df['rating'] = df['rating'].replace({'five': 5, 'four': 4, 'three': 3, 'two': 2, 'one': 1})
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')

    df['returned'] = df['returned'].astype(str).str.lower().map(
        {'yes': True, 'no': False, 'true': True, 'false': False}
    )

    return df


# ---------------------------
# PURCHASE
# ---------------------------
def clean_purchase(df):
    df['is_free'] = df['purchase_amount'].astype(str).str.lower().str.strip() == 'free'

    def convert(x):
        if pd.isna(x):
            return np.nan
        x = str(x).strip().lower()
        if x == 'free':
            return 0.0
        x = x.replace(',', '.')
        try:
            return float(x)
        except:
            return np.nan

    df['purchase_amount'] = df['purchase_amount'].apply(convert)
    return df


# ---------------------------
# DATE
# ---------------------------
def clean_dates(df):
    df['signup_date'] = pd.to_datetime(df['signup_date'], errors='coerce', dayfirst=True, format='mixed')
    df['last_login'] = pd.to_datetime(df['last_login'], errors='coerce', dayfirst=True, format='mixed')

    df = df[df['last_login'].isna() | (df['last_login'] >= df['signup_date'])]
    return df


# ---------------------------
# CATEGORY
# ---------------------------
def clean_category(df):
    df['category'] = df['category'].str.lower().str.strip()
    df['category'] = df['category'].map({'tech': 'Tech', 'tec': 'Tech', 'home': 'Home', 'fashion': 'Fashion'})
    return df


# ---------------------------
# DEDUP
# ---------------------------
def deduplicate(df):
    df = df.drop_duplicates()

    df['block'] = (
            df['name'].fillna('').str[0].str.lower() + '_' +
            df['email'].fillna('').str.split('@').str[-1].str.lower()
    )

    to_drop = set()

    for _, group in df.groupby('block'):
        idx = group.index.tolist()
        strings = group[['name', 'email']].fillna('').agg(' '.join, axis=1).tolist()
        completeness = group.notna().sum(axis=1).tolist()

        for i in range(len(strings)):
            if idx[i] in to_drop:
                continue
            for j in range(i + 1, len(strings)):
                if idx[j] in to_drop:
                    continue

                if fuzz.token_sort_ratio(strings[i], strings[j]) >= 85:
                    if completeness[i] >= completeness[j]:
                        to_drop.add(idx[j])
                    else:
                        to_drop.add(idx[i])
                        break

    df = df.drop(index=list(to_drop)).drop(columns=['block']).reset_index(drop=True)
    return df


# ---------------------------
# FEATURES
# ---------------------------
def add_features(df):
    today = pd.Timestamp.today()

    df['days_since_signup'] = (today - df['signup_date']).dt.days
    df['days_since_last_login'] = (today - df['last_login']).dt.days
    df['is_active_user'] = df['days_since_last_login'] <= 30

    return df


# ---------------------------
# ERRORI
# ---------------------------
def detect_errors(df):
    df['error_type'] = ''

    df.loc[df['age'].isna(), 'error_type'] += 'age_invalid;'
    df.loc[~df['email'].str.contains(r'^[^@]+@[^@]+\.[^@]+$', na=False), 'error_type'] += 'email_invalid;'
    df.loc[df['rating'].isna(), 'error_type'] += 'rating_invalid;'

    df['error_type'] = df['error_type'].str.rstrip(';')
    df['error_type'] = df['error_type'].replace('', np.nan)

    return df


# ---------------------------
# SCORE
# ---------------------------
def compute_score(df):
    def normalize(x):
        return (x - x.min()) / (x.max() - x.min())

    purchase = normalize(df['purchase_amount'].fillna(0))
    login = normalize(1 / (df['days_since_last_login'] + 1))
    reviews = normalize(df['reviews_count'].fillna(0))
    rating = normalize(df['rating'].fillna(0))

    df['user_score'] = (purchase * 0.4 + login * 0.3 + reviews * 0.2 + rating * 0.1) * 100

    return df


# ---------------------------
# MAIN PIPELINE
# ---------------------------
def main():
    df = load_data('dirty_dataset.csv')

    df = filter_valid_uuid(df)
    df = clean_text_columns(df)
    df = clean_country(df)
    df = clean_numeric(df)
    df = clean_purchase(df)
    df = clean_dates(df)
    df = clean_category(df)
    df = deduplicate(df)
    df = add_features(df)
    df = detect_errors(df)
    df = compute_score(df)

    print("\nNaN per country:\n", df.isna().groupby(df['country']).mean() * 100)
    print("\nNaN per category:\n", df.isna().groupby(df['category']).mean() * 100)

    df['age'] = df['age'].astype('Int64')
    df['reviews_count'] = df['reviews_count'].astype('Int64')

    df.to_csv('clean_dataset_final.csv', index=False, decimal=',')

    print("\nDONE")
    print(df.info())


# ---------------------------
# RUN
# ---------------------------
if __name__ == "__main__":
    main()