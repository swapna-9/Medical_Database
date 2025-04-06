# Medical Database Design
 
 #### Problem Statement
The goal of this project is to design and implement a data warehouse for a healthcare system to enable efficient analytical querying and reporting. The initial data is stored in an OLTP (Online Transaction Processing) system, represented by an Entity-Relationship Diagram (ERD) that captures patient-related transactions such as appointments, medical records, prescriptions, and diagnoses. The objective is to transform this OLTP model into an OLAP (Online Analytical Processing) model using both Star Schema and Snowflake Schema to support advanced analytics.

The project focuses on two key analytical areas:

#### Appointment Analysis: 
Understanding appointment trends, cancellation rates, and doctor workloads to improve operational efficiency.
Medical Diagnosis and Treatment Analysis: Analyzing diagnosis trends, medication prescription patterns, and symptom-diagnosis correlations to enhance patient care and resource allocation.
##### The deliverables include:

Designing Star and Snowflake schemas for the OLAP model.
Developing stored procedures for advanced trending analyses.
Creating views to simplify complex queries.
Writing a variety of SQL queries (simple, aggregate, joins, nested) to extract meaningful insights.

#### Key Analyses Focused
1. Appointment Analysis

The appointment analysis aims to provide insights into patient appointment patterns and operational efficiency. Key analyses include:

Rolling Average of Appointment Cancellations: Use a 3-month rolling average to smooth out cancellation rates and identify long-term trends.
Top Doctors by Appointment Growth Rate: Identify doctors with the highest year-over-year growth in appointment volume to balance workloads.

2. Medical Diagnosis and Treatment Analysis
This analysis focuses on understanding diagnosis and treatment patterns to improve patient care. Key analyses include:

Trending Diagnoses with Percentage Change: Identify diagnoses with the highest year-over-year percentage change to detect rising health issues.
Medication Prescription Trends with Ranking: Rank medications by prescription frequency each year to identify trending medications.
Symptom-Diagnosis Correlation Over Time: Analyze how the relationship between symptoms and diagnoses evolves over time to support clinical decision-making.

#### Initial OLTP Model (Entity-Relationship Diagram)
The initial OLTP model is represented by an Entity-Relationship Diagram (ERD) that captures the transactional data of the healthcare system. The ERD includes the following entities and relationships:

Entities and Attributes
DEPARTMENTS:
DepartmentID (PK), DepartmentName, Location
DEPARTMENT_SPECIALTY:
DepartmentID (FK), Specialty (PK)
DOCTORS:
DoctorID (PK), FirstName, LastName, License, HireDate, DepartmentID (FK)
PATIENTS:
PatientID (PK), FirstName, LastName, DateOfBirth, Gender, SSN
PATIENT_CONTACTINFO:
ContactID (PK), PatientID (FK), Address, City, State, Zipcode, Phone, Email
APPOINTMENTS:
AppointmentID (PK), PatientID (FK), DoctorID (FK), AppointmentDateTime, Status, Notes
MEDICALRECORDS:
RecordID (PK), AppointmentID (FK), Symptoms, DiagnosisID (FK)
DIAGNOSES:
DiagnosisID (PK), ICD10Code (FK), DiagnosisName
ICD10CODES:
ICD10Code (PK), DiagnosisCategory
PRESCRIPTIONS:
PrescriptionID (PK), MedicationID (FK), Dosage, Frequency, StartDate, EndDate
MEDICATIONS:
MedicationID (PK), MedicationName, Manufacturer, Description
PATIENT_ALLERGIES:
AllergyID (PK), PatientID (FK), AllergyName, Severity
INSURANCE:
InsuranceID (PK), PatientID (FK), CompanyName, PolicyNumber, CoverageDetails, EffectiveDate, ExpiryDate
Relationships
1:N Relationships:
DEPARTMENTS to DEPARTMENT_SPECIALTY
DEPARTMENTS to DOCTORS
PATIENTS to PATIENT_CONTACTINFO
PATIENTS to APPOINTMENTS
DOCTORS to APPOINTMENTS
APPOINTMENTS to MEDICALRECORDS
DIAGNOSES to MEDICALRECORDS
ICD10CODES to DIAGNOSES
MEDICATIONS to PRESCRIPTIONS
PATIENTS to PATIENT_ALLERGIES
PATIENTS to INSURANCE
This OLTP model is optimized for transactional operations (e.g., inserting new appointments, updating patient records) but is not ideal for analytical queries due to its normalized structure and complex relationships.

#### OLAP Models: Star Schema and Snowflake Schema
To support analytical querying, the OLTP model is transformed into OLAP models using a single fact table, Fact_PatientInteractions, which consolidates appointment, medical record, and prescription data. Two schemas are designed: Star Schema (denormalized) and Snowflake Schema (normalized).

#### Star Schema
The Star Schema is a denormalized structure with a central fact table surrounded by dimension tables. It minimizes joins for faster querying but may have redundant data.

Fact Table
Fact_PatientInteractions:
AppointmentID (PK)
PatientID (FK)
DoctorID (FK)
DiagnosisID (FK)
MedicationID (FK)
AppointmentDateTime
Status
Notes
RecordID (nullable)
Symptoms
Dosage
Frequency
StartDate
EndDate
Dimension Tables (Denormalized)
Dim_Patients:
PatientID (PK), FirstName, LastName, DateOfBirth, Gender, SSN, Address, City, State, Zipcode, Phone, Email
Dim_Doctors:
DoctorID (PK), FirstName, LastName, License, DepartmentName, Location, Specialty
Dim_Diagnoses:
DiagnosisID (PK), DiagnosisName, ICD10Code
Dim_Medications:
MedicationID (PK), MedicationName, Manufacturer, Description
Dim_Insurance:
InsuranceID (PK), PatientID, CompanyName, PolicyNumber, CoverageDetails, EffectiveDate, ExpiryDate
Dim_PatientAllergies:
AllergyID (PK), PatientID, AllergyName, Severity
Structure
Fact_PatientInteractions connects directly to all dimension tables.
Denormalized dimensions (e.g., Dim_Doctors includes DepartmentName and Specialty directly).

#### Snowflake Schema
The Snowflake Schema is a normalized version of the Star Schema, where dimension tables are broken into sub-dimensions to reduce redundancy, at the cost of more joins.

Fact Table
Fact_PatientInteractions (same as Star Schema)
Dimension Tables (Normalized)
Dim_Patients:
PatientID (PK), FirstName, LastName, DateOfBirth, Gender, SSN, ContactInfoID (FK)
Dim_PatientContactInfo: ContactInfoID (PK), Address, City, State, Zipcode, Phone, Email
Dim_Doctors:
DoctorID (PK), FirstName, LastName, License, DepartmentID (FK)
Dim_Departments: DepartmentID (PK), DepartmentName, Location, SpecialtyID (FK)
Dim_DepartmentSpecialty: SpecialtyID (PK), Specialty
Dim_Diagnoses:
DiagnosisID (PK), DiagnosisName, ICD10CodeID (FK)
Dim_ICD10Codes: ICD10CodeID (PK), ICD10Code
Dim_Medications (same as Star Schema)
Dim_Insurance (same as Star Schema)
Dim_PatientAllergies (same as Star Schema)
Structure
Fact_PatientInteractions connects to dimension tables, which are further normalized into sub-dimensions.
More joins are required (e.g., to get a doctor’s specialty, join Dim_Doctors → Dim_Departments → Dim_DepartmentSpecialty).

