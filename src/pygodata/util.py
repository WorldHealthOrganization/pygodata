import pandas as pd

def explode_questionnaire(df):
    df.reset_index(drop=True, inplace=True)

    def to_dict(row):
        out = {}
        if isinstance(row.questionnaireAnswers, dict):
            for k, v in row.questionnaireAnswers.items():
                out[k] = next(iter(v or []), {}).get('value', None)
        return out

    df_new_cols = pd.json_normalize(df.apply(to_dict, axis=1))

    return pd.concat([df, df_new_cols], axis=1)


def explode_address(df):
    def explode_address_row(row):
        if 'addresses' in row and isinstance(row.addresses, list) and len(row.addresses) >= 1:
            row['addressLine1'] = row.addresses[0].get("addressLine1")
            row['city'] = row.addresses[0].get("city")
            row['postalCode'] = row.addresses[0].get("postalCode")
            row['country'] = row.addresses[0].get("country")
            row['phoneNumber'] = row.addresses[0].get("phoneNumber")
        return row
    df = df.apply(explode_address_row, axis=1)
    return df


def dt_to_iso(dt):
    if dt is not None:
        if hasattr(dt, 'tzinfo'):
            dt = dt.replace(tzinfo=None)
        return dt.isoformat() + 'Z'