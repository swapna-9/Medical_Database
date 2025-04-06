-- View: AppointmentSummary

CREATE VIEW AppointmentSummary AS
SELECT 
    p.PatientID,
    p.FirstName,
    p.LastName,
    COUNT(f.AppointmentID) AS TotalAppointments,
    SUM(CASE WHEN f.Status = 'Cancelled' THEN 1 ELSE 0 END) AS CancelledAppointments
FROM Fact_PatientInteractions f
JOIN Dim_Patients p ON f.PatientID = p.PatientID
GROUP BY p.PatientID, p.FirstName, p.LastName;


-- View: DiagnosisTreatmentSummary
CREATE VIEW DiagnosisTreatmentSummary AS
SELECT 
    f.PatientID,
    d.DiagnosisName,
    icd.ICD10Code,
    m.MedicationName,
    COUNT(f.AppointmentID) AS TreatmentCount
FROM Fact_PatientInteractions f
JOIN Dim_Diagnoses d ON f.DiagnosisID = d.DiagnosisID
JOIN Dim_ICD10Codes icd ON d.ICD10CodeID = icd.ICD10CodeID
JOIN Dim_Medications m ON f.MedicationID = m.MedicationID
GROUP BY f.PatientID, d.DiagnosisName, icd.ICD10Code, m.MedicationName;


-- Update Treatment Priority
-- This update sets the TreatmentPriority based on the number of appointments and treatment counts:

----High Priority: Patients with more than 5 total appointments or more than 3 treatments for a diagnosis.
----Medium Priority: Patients with 3–5 total appointments or 2–3 treatments.
---Low Priority: Otherwise.

UPDATE Fact_PatientInteractions f
JOIN AppointmentSummary a ON f.PatientID = a.PatientID
JOIN DiagnosisTreatmentSummary dts ON f.PatientID = dts.PatientID
SET f.TreatmentPriority = 
    CASE 
        WHEN a.TotalAppointments > 5 OR dts.TreatmentCount > 3 THEN 'High'
        WHEN a.TotalAppointments >= 3 OR dts.TreatmentCount >= 2 THEN 'Medium'
        ELSE 'Low'
    END
WHERE f.DiagnosisID = dts.DiagnosisID;