import pandas as pd
import numpy as np
from faker import Faker
from faker.providers import ssn, person, address, phone_number, date_time
from datetime import datetime, timedelta
import random
import zipfile

# Initialize Faker with providers
fake = Faker()
fake.add_provider(ssn)
fake.add_provider(person)
fake.add_provider(address)
fake.add_provider(phone_number)
fake.add_provider(date_time)

# Configuration
NUM_PATIENTS = 10000
NUM_DOCTORS = 200
NUM_ALLERGIES = 150
NUM_MEDS = 300
START_DATE = datetime(2010, 1, 1)
END_DATE = datetime(2025, 3, 23)

# Initialize data storage
tables = {}

# ========== Lookup Tables ==========
departments = [
    'Cardiology', 'Oncology', 'Pediatrics', 'Neurology', 'Orthopedics',
    'Emergency', 'Surgery', 'Radiology', 'ICU', 'Labor & Delivery',
    'Dermatology', 'Gastroenterology', 'Endocrinology', 'Pulmonology',
    'Nephrology', 'Psychiatry', 'Urology', 'Ophthalmology', 'ENT', 'Hematology'
]
tables['Departments'] = pd.DataFrame({
    'DepartmentID': range(1, 21),
    'DepartmentName': departments,
    'Location': [fake.street_address() for _ in range(20)]
})

specialty_map = {
    'Cardiology': 'Cardiac Care', 'Oncology': 'Cancer Treatment', 'Pediatrics': 'Child Health',
    'Neurology': 'Nervous System', 'Orthopedics': 'Musculoskeletal', 'Emergency': 'Trauma Care',
    'Surgery': 'Surgical Services', 'Radiology': 'Medical Imaging', 'ICU': 'Critical Care',
    'Labor & Delivery': 'Obstetrics', 'Dermatology': 'Skin Disorders', 'Gastroenterology': 'Digestive Health',
    'Endocrinology': 'Hormonal Disorders', 'Pulmonology': 'Respiratory System', 'Nephrology': 'Kidney Diseases',
    'Psychiatry': 'Mental Health', 'Urology': 'Urinary System', 'Ophthalmology': 'Eye Care',
    'ENT': 'Ear/Nose/Throat', 'Hematology': 'Blood Disorders'
}
tables['DepartmentSpecialty'] = pd.DataFrame({
    'DepartmentID': tables['Departments'].DepartmentID,
    'Specialty': [specialty_map[name] for name in tables['Departments'].DepartmentName]
})

icd10_codes = [
    ('A00-B99', 'Certain infectious and parasitic diseases'), ('C00-D49', 'Neoplasms'),
    ('D50-D89', 'Diseases of the blood'), ('E00-E89', 'Endocrine, nutritional and metabolic diseases'),
    ('F01-F99', 'Mental, Behavioral and Neurodevelopmental disorders'), ('G00-G99', 'Diseases of the nervous system'),
    ('H00-H59', 'Diseases of the eye and adnexa'), ('H60-H95', 'Diseases of the ear and mastoid process'),
    ('I00-I99', 'Diseases of the circulatory system'), ('J00-J99', 'Diseases of the respiratory system')
]
tables['ICD10Codes'] = pd.DataFrame(icd10_codes, columns=['ICD10Code', 'DiagnosisCategory'])

# ========== Core Entities ==========
tables['Doctors'] = pd.DataFrame([{
    'DoctorID': i+1,
    'FirstName': fake.first_name(),
    'LastName': fake.last_name(),
    'License': f'MD{str(i+1).zfill(6)}',
    'HireDate': fake.date_between(start_date='-20y', end_date='-1y'),
    'DepartmentID': random.choice(tables['Departments'].DepartmentID.tolist())
} for i in range(NUM_DOCTORS)])

patient_data = []
ssn_set = set()
for i in range(NUM_PATIENTS):
    while True:
        ssn = fake.unique.ssn()
        if ssn not in ssn_set:
            ssn_set.add(ssn)
            break
    patient_data.append({
        'PatientID': i+1,
        'FirstName': fake.first_name(),
        'LastName': fake.last_name(),
        'DateOfBirth': fake.date_of_birth(minimum_age=1, maximum_age=100),
        'Gender': random.choice(['Male', 'Female', 'Other']),
        'SSN': ssn
    })
tables['Patients'] = pd.DataFrame(patient_data)

tables['PatientContactInfo'] = pd.DataFrame([{
    'ContactID': i+1,
    'PatientID': i+1,
    'Address': fake.street_address(),
    'City': fake.city(),
    'State': fake.state_abbr(),
    'ZipCode': fake.zipcode(),
    'Phone': fake.numerify(text='###-###-####'),  # Standardized to fit VARCHAR(15)
    'Email': fake.email()
} for i in range(NUM_PATIENTS)])

# ========== ALLERGY SECTION UPDATE ==========
# Real-world common allergies
real_allergies = [
    'Peanuts', 'Shellfish', 'Penicillin', 'Sulfa Drugs', 'Latex',
    'Eggs', 'Milk', 'Tree Nuts', 'Pollen', 'Dust Mites',
    'Mold', 'Pet Dander', 'Insect Stings', 'Soy', 'Wheat',
    'Fish', 'Aspirin', 'Ibuprofen', 'Codeine', 'Chemotherapy Drugs'
]

# Generate allergies with realistic distribution
allergy_distribution = {
    'Peanuts': 0.15, 'Shellfish': 0.12, 'Penicillin': 0.1,
    'Latex': 0.08, 'Eggs': 0.07, 'Milk': 0.06,
    'Tree Nuts': 0.05, 'Pollen': 0.04, 'Dust Mites': 0.03,
    'Other': 0.2
}

allergy_data = []
allergy_id = 1
for allergy, prob in allergy_distribution.items():
    count = int(NUM_ALLERGIES * prob)
    if allergy == 'Other':
        # Generate unique "Other" allergies
        for _ in range(count):
            other_allergy = random.choice(real_allergies[9:])  # Pick from less common ones
            allergy_data.append({
                'AllergyID': allergy_id,
                'AllergyName': other_allergy,
                'Severity': random.choices(['Low', 'Medium', 'High'], weights=[0.4, 0.35, 0.25])[0]
            })
            allergy_id += 1
    else:
        for _ in range(count):
            allergy_data.append({
                'AllergyID': allergy_id,
                'AllergyName': allergy,
                'Severity': random.choices(['Low', 'Medium', 'High'], weights=[0.4, 0.35, 0.25])[0]
            })
            allergy_id += 1
tables['Allergies'] = pd.DataFrame(allergy_data)

# ========== Relational Data ==========
patient_allergies = []
for patient in tables['Patients'].itertuples():
    num_allergies = np.random.choice([0, 1, 2, 3], p=[0.3, 0.4, 0.2, 0.1])
    allergies = random.sample(tables['Allergies'].AllergyID.tolist(), k=num_allergies)
    for allergy in allergies:
        birth_datetime = datetime.combine(patient.DateOfBirth, datetime.min.time())
        min_start_date = birth_datetime + timedelta(days=365*5)
        start_date = max(min_start_date, START_DATE)
        if start_date < END_DATE:
            patient_allergies.append({
                'PatientID': patient.PatientID,
                'AllergyID': allergy,
                'DateDiagnosed': fake.date_between(start_date=start_date, end_date=END_DATE)
            })
tables['PatientAllergies'] = pd.DataFrame(patient_allergies)

# ========== DIAGNOSES TABLE UPDATE ==========
diagnosis_map = {
    'A00-B99': ['Cholera', 'Salmonella Infection', 'Tuberculosis'],
    'C00-D49': ['Breast Cancer', 'Lung Cancer', 'Melanoma'],
    'D50-D89': ['Anemia', 'Hemophilia', 'Leukemia'],
    'E00-E89': ['Diabetes Mellitus', 'Hypothyroidism', 'Obesity'],
    'F01-F99': ['Depression', 'Anxiety Disorder', 'Schizophrenia'],
    'G00-G99': ['Migraine', 'Epilepsy', 'Alzheimer Disease'],
    'H00-H59': ['Cataracts', 'Glaucoma', 'Conjunctivitis'],
    'H60-H95': ['Otitis Media', 'Tinnitus', 'Hearing Loss'],
    'I00-I99': ['Hypertension', 'Coronary Artery Disease', 'Stroke'],
    'J00-J99': ['Asthma', 'Pneumonia', 'COPD']
}

diagnoses = []
diagnosis_id = 1
for code in tables['ICD10Codes'].itertuples():
    for disease in diagnosis_map[code.ICD10Code]:
        for _ in range(15):  # 15 variations per disease
            diagnoses.append({
                'DiagnosisID': diagnosis_id,
                'ICD10Code': code.ICD10Code,
                'DiagnosisName': f"{disease} - {fake.word().capitalize()} Type"
            })
            diagnosis_id += 1
tables['Diagnoses'] = pd.DataFrame(diagnoses)

# Pre-convert Doctors to a list once
doctors_list = list(tables['Doctors'].itertuples())

# ========== APPOINTMENTS TABLE UPDATE ==========
appointments = []
app_id = 1
for patient in tables['Patients'].itertuples():
    num_appointments = np.random.poisson(4) + 1
    for _ in range(num_appointments):
        doctor = random.choice(doctors_list)
        birth_datetime = datetime.combine(patient.DateOfBirth, datetime.min.time())
        hire_datetime = datetime.combine(doctor.HireDate, datetime.min.time())
        start_date = max(hire_datetime + timedelta(days=30), birth_datetime + timedelta(days=365*5))
        if start_date < END_DATE:  # Only add if valid range
            appointments.append({
                'AppointmentID': app_id,
                'PatientID': patient.PatientID,
                'DoctorID': doctor.DoctorID,
                'AppointmentDateTime': fake.date_time_between(start_date=start_date, end_date=END_DATE),
                'Status': random.choices(['Scheduled', 'Completed', 'Cancelled'], weights=[0.1, 0.8, 0.1])[0]
            })
            app_id += 1
tables['Appointments'] = pd.DataFrame(appointments)

# ========== MEDICAL RECORDS UPDATE ==========
symptom_list = ['Fever', 'Cough', 'Pain', 'Fatigue', 'Nausea', 'Rash', 'Headache']
treatment_list = ['Rest', 'Antibiotics', 'Surgery', 'Therapy', 'Medication']
tables['MedicalRecords'] = pd.DataFrame([{
    'RecordID': i+1,
    'AppointmentID': appt.AppointmentID,
    'Symptoms': ', '.join(random.sample(symptom_list, random.randint(1, 3))),
    'DiagnosisID': random.choice(tables['Diagnoses'].DiagnosisID.tolist()),
    'Treatment': random.choice(treatment_list)
} for i, appt in enumerate(tables['Appointments'].itertuples())])

# ========== MEDICATIONS UPDATE ==========
med_names = set()
while len(med_names) < NUM_MEDS:
    med_names.add(f"{fake.word().capitalize()}{random.choice(['cin', 'mycin', 'zol', 'pam', 'x'])}")
med_names = list(med_names)  # Convert to list for enumeration

med_descriptions = {
    'Paracetamol': 'Analgesic and antipyretic for pain relief and fever reduction',
    'Amoxicillin': 'Penicillin antibiotic for bacterial infections',
    'Lisinopril': 'ACE inhibitor for hypertension management',
    'Metformin': 'Biguanide antidiabetic for type 2 diabetes',
    'Atorvastatin': 'Statin for cholesterol management',
    'Omeprazole': 'Proton pump inhibitor for acid reflux',
    'Albuterol': 'Bronchodilator for asthma attacks',
    'Sertraline': 'SSRI antidepressant for depression and anxiety',
    'Gabapentin': 'Anticonvulsant for nerve pain management',
    'Hydrocodone': 'Opioid analgesic for severe pain'
}

tables['Medications'] = pd.DataFrame([{
    'MedicationID': i+1,
    'MedicationName': name,
    'Manufacturer': fake.company(),
    'Description': med_descriptions.get(name, 'Prescription medication')
} for i, name in enumerate(med_names)])

prescriptions = []
for appt in tables['Appointments'].itertuples():
    if appt.Status == 'Completed' and random.random() > 0.4:
        num_scripts = random.randint(0, 3)
        for _ in range(num_scripts):
            prescriptions.append({
                'PrescriptionID': len(prescriptions)+1,
                'MedicationID': random.choice(tables['Medications'].MedicationID.tolist()),
                'Dosage': f'{random.randint(1, 500)}mg',
                'Frequency': random.choice(['QD', 'BID', 'TID', 'QID']),
                'StartDate': appt.AppointmentDateTime.date(),
                'EndDate': (appt.AppointmentDateTime + timedelta(days=random.randint(7, 30))).date()
            })
tables['Prescriptions'] = pd.DataFrame(prescriptions)

# ========== INSURANCE COVERAGE UPDATE ==========
coverage_options = [
    "Covers 80% of in-network costs with $20 copay for primary care visits",
    "PPO plan with $1500 deductible and $30 specialist copay",
    "HMO plan requiring referrals, covers preventive care 100%",
    "High-deductible plan with HSA, covers 100% after $3000 deductible",
    "Medicare Advantage Plan with prescription drug coverage"
]

tables['Insurance'] = pd.DataFrame([{
    'InsuranceID': i+1,
    'PatientID': i+1,
    'CompanyName': random.choice(['UnitedHealthcare', 'Blue Cross', 'Aetna', 'Cigna', 'Kaiser']),
    'PolicyNumber': f'POL{str(i+1).zfill(6)}',
    'CoverageDetails': random.choice(coverage_options),
    'EffectiveDate': fake.date_between(start_date='-10y', end_date='-1y'),
    'ExpiryDate': fake.date_between(start_date='today', end_date='+5y')
} for i in range(NUM_PATIENTS)])

# ========== Validation ==========
assert tables['Patients'].SSN.nunique() == NUM_PATIENTS
assert tables['Doctors'].License.nunique() == NUM_DOCTORS
assert tables['Insurance'].PolicyNumber.nunique() == NUM_PATIENTS

for table in ['Doctors', 'DepartmentSpecialty']:
    assert tables[table]['DepartmentID'].isin(tables['Departments'].DepartmentID).all()

# ========== Export ==========
with zipfile.ZipFile('medical_data.zip', 'w') as zipf:
    for table_name, df in tables.items():
        filename = f'{table_name}.csv'
        df.to_csv(filename, index=False)
        zipf.write(filename)
        print(f'Generated {len(df)} records in {filename}')

print('Data generation complete. All files zipped to medical_data.zip')