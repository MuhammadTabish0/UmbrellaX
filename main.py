import pandas as pd

# Load your dataset
df = pd.read_csv("synthetic_covid19_data.csv", parse_dates=["date"])

# Clean/handle potential division by zero
def safe_divide(a, b):
    return a / b if b != 0 else 0

# Apply calculations row-wise
def calculate_metrics(row):
    metrics = {}
    
    # Positive test probability
    metrics['positive_rate_calc'] = safe_divide(row['new_cases'], row['new_tests'])
    
    # Case Fatality Rate
    metrics['case_fatality_rate'] = safe_divide(row['total_deaths'], row['total_cases'])
    
    # Mortality rate in population
    metrics['mortality_rate'] = safe_divide(row['total_deaths'], row['population'])
    
    # Hospitalization probability
    metrics['hospitalization_rate'] = safe_divide(row['hosp_patients'], row['total_cases'])
    
    # ICU rate
    metrics['icu_rate'] = safe_divide(row['icu_patients'], row['total_cases'])
    
    # Tests per case
    metrics['tests_per_case_calc'] = safe_divide(row['new_tests'], row['new_cases'])
    
    # Vaccination coverage (at least one dose)
    metrics['vaccination_coverage'] = safe_divide(row['people_vaccinated'], row['population'])
    
    # Full vaccination coverage
    metrics['full_vaccination_coverage'] = safe_divide(row['people_fully_vaccinated'], row['population'])

    # Reproduction rate (use as-is or estimate if not present)
    metrics['reproduction_rate'] = row.get('reproduction_rate', None)
    
    return pd.Series(metrics)

# Apply calculations
results = df.apply(calculate_metrics, axis=1)

# Combine with original data (optional)
final_df = pd.concat([df, results], axis=1)

# Print a preview of the new result
print(final_df[['date', 'location', 'positive_rate_calc', 'case_fatality_rate',
                'mortality_rate', 'hospitalization_rate', 'icu_rate',
                'tests_per_case_calc', 'vaccination_coverage', 'full_vaccination_coverage',
                'reproduction_rate']].head())
