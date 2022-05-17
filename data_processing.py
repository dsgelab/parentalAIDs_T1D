import numpy as np
import pandas as pd
import tqdm
import matplotlib.pyplot as plt
from basic_tools import load_data, eps

# load data
first_event_path = '/data/processed_data/endpointer/densified_first_events_DF8_all_endpoints_2021-09-04.txt'
info_path = '/data/processed_data/minimal_phenotype/minimal_phenotype_2022-03-28.csv'
pedigree_path = '/home/aliu/pedigree/output/Index_RelativePair_basic.txt'
geo_path = '/data/projects/project_akarvane/geo/living_province.csv'
df_events, df_info, pedigree = load_data(first_event_path, info_path, geo_path, pedigree_path)

# select variables that will be used to define study population
df = df_info[['ID', 'sex', 'ch_year', 'emigrated', 'emigration_date',
              'death_date', 'residence_type_last', 'residence_start_date_last', 'residence_end_date_last',
              'residence_type_first', 'residence_start_date_first', 'residence_end_date_first',
              'ever_married', 'mother_tongue', 'post_code_first', 'number_of_children', 'maakunta'
              'in_social_assistance_registries', 'in_vaccination_registry', 'in_infect_dis_registry',
              'in_malformations_registry', 'in_cancer_registry', 'ses', 'occupation', 'edulevel', 'edufield']]

# individuals with only 1 father id and 1 mother id
df = df.merge(pedigree[pedigree.relationship == 'index-father'][['ID', 'Relative_ID']], 'left', on='ID')
df = df.rename(columns={'Relative_ID': 'father_id'})
df = df.merge(pedigree[pedigree.relationship == 'index-mother'][['ID', 'Relative_ID']], 'left', on='ID')
df = df.rename(columns={'Relative_ID': 'mother_id'})
df = df[(~df.father_id.isna())&(~df.mother_id.isna())]
# individuals born 1960.1.1-1999.12.31
df = df[(df.ch_year >= 1960.0) & (df.ch_year < 2000.0)]
# add number of siblings to the data
pedigree_sib = pedigree[pedigree.relationship == 'index-fullsib'][['ID', 'Relative_ID']]
num_of_sib = pedigree_sib.groupby('ID').count()
num_of_sib = pd.DataFrame(num_of_sib.to_records())
df = df.merge(num_of_sib, 'left', on='ID').rename(columns={'Relative_ID': 'number_of_sib'})
df['number_of_sib'] = df.number_of_sib.fillna(0)
df['sib_number'] = np.select([
    (df['number_of_sib'] == 0), (df['number_of_sib'] == 1), (df['number_of_sib'] == 2),
    (df['number_of_sib'] == 3), (df['number_of_sib'] > 3)
    ], [0, 1, 2, 3, 4])
# add fathers' birth year and mothers' birth year
df = df.merge(df_info[['ID', 'ch_year']].rename(columns={'ID': 'father_id', 'ch_year': 'fa_year'}),
              'left', on='father_id')
df = df.merge(df_info[['ID', 'ch_year']].rename(columns={'ID': 'mother_id', 'ch_year': 'mo_year'}),
              'left', on='mother_id')
# df['mother_delivery_year'] = df.mo_year - df.ch_year
# df['father_delivery_year'] = df.fa_year - df.ch_year # as same as birth year, so no need to compute

# plot the number of individuals by birth year
df.ch_year.value_counts().sort_index().plot(kind='bar', figsize=(15, 6))
plt.xlabel("Birth year", labelpad=14)
plt.ylabel("Count", labelpad=14)
plt.show()

# Remove individuals who died or emigrated before 2019.12.31
df = df[df.death_date.isna()]
# min: 1975-05-06 max: 2019-12-31  ~34k
df = df[(df.emigration_date.isna()) | (df.emigration_date.str.startswith('2020'))]
# min: 2001-03-26 2010-01-03 max: 2020-05-19  ~35k

# f???
df['first_post'] = df.post_code_first.astype('str').str[:3]

# define fathers' birth year range
# plot the number of individuals by fathers' birth year
df.fa_year.value_counts().sort_index().plot(kind='bar', figsize=(15, 6))
plt.xlabel("Birth year", labelpad=14)
plt.ylabel("Count", labelpad=14)
plt.show()
# individuals' fathers who were born 1917-1976
df['fa_year'] = df.fa_year.astype(int)
df = df[(df.fa_year >= 1917) & (df.fa_year <= 1976)]

# define mothers' birth year range
# plot the number of individuals by mothers' birth year
df.mo_year.value_counts().sort_index().plot(kind='bar', figsize=(15, 6))
plt.xlabel("Birth year", labelpad=14)
plt.ylabel("Count", labelpad=14)
plt.show()
# individuals' fathers who were born 1922-1976
df['mo_year'] = df.mo_year.astype(int)
df = df[(df.mo_year >= 1922) & (df.mo_year <= 1976)]

# group birth years for individuals, their fathers and their mothers
df['ch_year'] = df.ch_year.astype(int)
df['fa_year_range'] = np.select([
    ((df['fa_year'] >= 1917) & (df['fa_year'] <= 1921)),
    ((df['fa_year'] >= 1922) & (df['fa_year'] <= 1926)), # 22 23 24 25 26
    ((df['fa_year'] >= 1927) & (df['fa_year'] <= 1931)), # 27 28 29 30 31
    ((df['fa_year'] >= 1932) & (df['fa_year'] <= 1936)), # 32-36
    ((df['fa_year'] >= 1937) & (df['fa_year'] <= 1941)), # 37-41
    ((df['fa_year'] >= 1942) & (df['fa_year'] <= 1946)), # 42-46
    ((df['fa_year'] >= 1947) & (df['fa_year'] <= 1951)), # 47-51
    ((df['fa_year'] >= 1952) & (df['fa_year'] <= 1956)), # 52-56
    ((df['fa_year'] >= 1957) & (df['fa_year'] <= 1961)), # 57-61
    ((df['fa_year'] >= 1962) & (df['fa_year'] <= 1966)), # 62-66
    ((df['fa_year'] >= 1967) & (df['fa_year'] <= 1971)), # 67-71
    ((df['fa_year'] >= 1972) & (df['fa_year'] <= 1976)), # 72-76
    ], ['1917', '1922', '1927', '1932', '1937', '1942', '1947', '1952', '1957', '1962', '1967', '1972'])
df['mo_year_range'] = np.select([
    ((df['mo_year'] >= 1922) & (df['mo_year'] <= 1926)), # 22 23 24 25 26
    ((df['mo_year'] >= 1927) & (df['mo_year'] <= 1931)), # 27 28 29 30 31
    ((df['mo_year'] >= 1932) & (df['mo_year'] <= 1936)), # 32-36
    ((df['mo_year'] >= 1937) & (df['mo_year'] <= 1941)), # 37-41
    ((df['mo_year'] >= 1942) & (df['mo_year'] <= 1946)), # 42-46
    ((df['mo_year'] >= 1947) & (df['mo_year'] <= 1951)), # 47-51
    ((df['mo_year'] >= 1952) & (df['mo_year'] <= 1956)), # 52-56
    ((df['mo_year'] >= 1957) & (df['mo_year'] <= 1961)), # 57-61
    ((df['mo_year'] >= 1962) & (df['mo_year'] <= 1966)), # 62-66
    ((df['mo_year'] >= 1967) & (df['mo_year'] <= 1971)), # 67-71
    ((df['mo_year'] >= 1972) & (df['mo_year'] <= 1976)), # 72-76
    ], ['1922', '1927', '1932', '1937', '1942', '1947', '1952', '1957', '1962', '1967', '1972'])
df['ch_year_range'] = np.select([
    ((df['ch_year'] >= 1960) & (df['ch_year'] <= 1964)), # 60-64
    ((df['ch_year'] >= 1965) & (df['ch_year'] <= 1969)), # 65-69
    ((df['ch_year'] >= 1970) & (df['ch_year'] <= 1974)), # 70-74
    ((df['ch_year'] >= 1975) & (df['ch_year'] <= 1979)), # 75-79
    ((df['ch_year'] >= 1980) & (df['ch_year'] <= 1984)), # 80-84
    ((df['ch_year'] >= 1985) & (df['ch_year'] <= 1989)), # 85-89
    ((df['ch_year'] >= 1990) & (df['ch_year'] <= 1994)), # 90-94
    ((df['ch_year'] >= 1995) & (df['ch_year'] <= 1999)), # 95-99
    ], ['1960', '1965', '1970', '1975', '1980', '1985', '1990', '1995'])

# add information for selected endpoints
# np.select faster & easier than df.merge faster than for loop
for i in tqdm.tqdm(range(len(eps))):
    df_events_sub = df_events[df_events.ENDPOINT == eps[i]]
    # currently, we only want to analyze T1D as outcome
    if i == 0:
        df = df.merge(df_events_sub[['ID', 'AGE']].rename(columns={'AGE': 'age_onset'}), 'left', on='ID')
        df['ch_ep' + str(i)] = np.select([
            (df['ID'].isin(df_events_sub.ID)), (~df['ID'].isin(df_events_sub.ID))
        ], [1, 0])
    df['mo_ep' + str(i)] = np.select([
        (df['mother_id'].isin(df_events_sub.ID)), (~df['mother_id'].isin(df_events_sub.ID))
    ], [1, 0])
    df['fa_ep' + str(i)] = np.select([
        (df['father_id'].isin(df_events_sub.ID)), (~df['father_id'].isin(df_events_sub.ID))
    ], [1, 0])

# in case we want to remove females who have GEST_DIABETES during pregnancy from cases
df_events_sub = df_events[df_events.ENDPOINT == 'GEST_DIABETES']
df['ch_gest_dm'] = np.select([(df['ID'].isin(df_events_sub.ID)), (~df['ID'].isin(df_events_sub.ID))], [1, 0])

# save the data
df.to_csv('df.csv', index=None)

