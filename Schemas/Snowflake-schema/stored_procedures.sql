-- Medical Diagnosis and Treatment Analysis Stored Procedures
-- Trending Diagnoses with Percentage Change
DELIMITER //

CREATE PROCEDURE GetTrendingDiagnoses(
    IN start_date DATE,
    IN end_date DATE
)
BEGIN
    WITH YearlyDiagnoses AS (
        SELECT 
            d.DiagnosisName,
            icd.ICD10Code,
            YEAR(f.AppointmentDateTime) AS DiagnosisYear,
            COUNT(*) AS DiagnosisCount
        FROM Fact_PatientInteractions f
        JOIN Dim_Diagnoses d ON f.DiagnosisID = d.DiagnosisID
        JOIN Dim_ICD10Codes icd ON d.ICD10CodeID = icd.ICD10CodeID
        WHERE f.AppointmentDateTime BETWEEN start_date AND end_date
        GROUP BY d.DiagnosisName, icd.ICD10Code, YEAR(f.AppointmentDateTime)
    )
    SELECT 
        DiagnosisName,
        ICD10Code,
        DiagnosisYear,
        DiagnosisCount,
        LAG(DiagnosisCount) OVER (PARTITION BY DiagnosisName ORDER BY DiagnosisYear) AS PreviousYearCount,
        ROUND(
            ((DiagnosisCount - LAG(DiagnosisCount) OVER (PARTITION BY DiagnosisName ORDER BY DiagnosisYear)) * 100.0) / 
            LAG(DiagnosisCount) OVER (PARTITION BY DiagnosisName ORDER BY DiagnosisYear), 
            2
        ) AS YoYChangePercentage
    FROM YearlyDiagnoses
    WHERE LAG(DiagnosisCount) OVER (PARTITION BY DiagnosisName ORDER BY DiagnosisYear) IS NOT NULL
    ORDER BY YoYChangePercentage DESC;
END //

DELIMITER ;

-- Medication Prescription Trends with Ranking
-- This procedure is the same as in the Star Schema because Dim_Medications is not further normalized

DELIMITER //

CREATE PROCEDURE GetMedicationPrescriptionTrends(
    IN start_date DATE,
    IN end_date DATE
)
BEGIN
    WITH YearlyPrescriptions AS (
        SELECT 
            m.MedicationName,
            m.Manufacturer,
            YEAR(f.AppointmentDateTime) AS PrescriptionYear,
            COUNT(*) AS PrescriptionCount,
            RANK() OVER (PARTITION BY YEAR(f.AppointmentDateTime) ORDER BY COUNT(*) DESC) AS RankInYear
        FROM Fact_PatientInteractions f
        JOIN Dim_Medications m ON f.MedicationID = m.MedicationID
        WHERE f.AppointmentDateTime BETWEEN start_date AND end_date
        GROUP BY m.MedicationName, m.Manufacturer, YEAR(f.AppointmentDateTime)
    )
    SELECT 
        MedicationName,
        Manufacturer,
        PrescriptionYear,
        PrescriptionCount,
        RankInYear,
        LAG(PrescriptionCount) OVER (PARTITION BY MedicationName ORDER BY PrescriptionYear) AS PreviousYearCount,
        ROUND(
            ((PrescriptionCount - LAG(PrescriptionCount) OVER (PARTITION BY MedicationName ORDER BY PrescriptionYear)) * 100.0) / 
            LAG(PrescriptionCount) OVER (PARTITION BY MedicationName ORDER BY PrescriptionYear), 
            2
        ) AS YoYChangePercentage
    FROM YearlyPrescriptions
    ORDER BY PrescriptionYear, RankInYear;
END //

DELIMITER ;


-- Symptom-Diagnosis Correlation Over Time
-- This procedure is similar to the Star Schema but includes the join with Dim_Diagnoses.

DELIMITER //

CREATE PROCEDURE GetSymptomDiagnosisCorrelation(
    IN start_date DATE,
    IN end_date DATE
)
BEGIN
    WITH SymptomDiagnosisPairs AS (
        SELECT 
            DATE_FORMAT(f.AppointmentDateTime, '%Y-%m') AS DiagnosisMonth,
            f.Symptoms,
            d.DiagnosisName,
            COUNT(*) AS PairCount
        FROM Fact_PatientInteractions f
        JOIN Dim_Diagnoses d ON f.DiagnosisID = d.DiagnosisID
        WHERE f.AppointmentDateTime BETWEEN start_date AND end_date
        AND f.Symptoms IS NOT NULL
        GROUP BY DATE_FORMAT(f.AppointmentDateTime, '%Y-%m'), f.Symptoms, d.DiagnosisName
    )
    SELECT 
        DiagnosisMonth,
        Symptoms,
        DiagnosisName,
        PairCount,
        SUM(PairCount) OVER (PARTITION BY Symptoms, DiagnosisName) AS TotalPairCount,
        ROUND(
            (PairCount * 100.0) / SUM(PairCount) OVER (PARTITION BY DiagnosisMonth),
            2
        ) AS PercentageOfMonth
    FROM SymptomDiagnosisPairs
    ORDER BY DiagnosisMonth, PairCount DESC;
END //

DELIMITER ;

-- Rolling Average of Appointment Cancellations

DELIMITER //

CREATE PROCEDURE GetRollingAvgCancellations(
    IN start_date DATE,
    IN end_date DATE
)
BEGIN
    WITH MonthlyCancellations AS (
        SELECT 
            DATE_FORMAT(AppointmentDateTime, '%Y-%m') AS AppointmentMonth,
            SUM(CASE WHEN Status = 'Cancelled' THEN 1 ELSE 0 END) AS CancelledCount,
            COUNT(*) AS TotalAppointments,
            (SUM(CASE WHEN Status = 'Cancelled' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) AS CancellationRate
        FROM Fact_PatientInteractions
        WHERE AppointmentDateTime BETWEEN start_date AND end_date
        GROUP BY DATE_FORMAT(AppointmentDateTime, '%Y-%m')
    )
    SELECT 
        AppointmentMonth,
        CancellationRate,
        AVG(CancellationRate) OVER (
            ORDER BY AppointmentMonth
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS RollingAvgCancellationRate
    FROM MonthlyCancellations
    ORDER BY AppointmentMonth;
END //

DELIMITER ;

-- Top Doctors by Appointment Growth Rate

DELIMITER //

CREATE PROCEDURE GetTopDoctorsByGrowthRate(
    IN start_date DATE,
    IN end_date DATE,
    IN top_n INT
)
BEGIN
    WITH DoctorYearlyAppointments AS (
        SELECT 
            d.DoctorID,
            d.FirstName,
            d.LastName,
            dept.DepartmentName,
            ds.Specialty,
            YEAR(f.AppointmentDateTime) AS AppointmentYear,
            COUNT(*) AS AppointmentCount
        FROM Fact_PatientInteractions f
        JOIN Dim_Doctors d ON f.DoctorID = d.DoctorID
        JOIN Dim_Departments dept ON d.DepartmentID = dept.DepartmentID
        JOIN Dim_DepartmentSpecialty ds ON dept.SpecialtyID = ds.SpecialtyID
        WHERE f.AppointmentDateTime BETWEEN start_date AND end_date
        GROUP BY d.DoctorID, d.FirstName, d.LastName, dept.DepartmentName, ds.Specialty, YEAR(f.AppointmentDateTime)
    )
    SELECT 
        DoctorID,
        FirstName,
        LastName,
        DepartmentName,
        Specialty,
        AppointmentYear,
        AppointmentCount,
        LAG(AppointmentCount) OVER (PARTITION BY DoctorID ORDER BY AppointmentYear) AS PreviousYearCount,
        ROUND(
            ((AppointmentCount - LAG(AppointmentCount) OVER (PARTITION BY DoctorID ORDER BY AppointmentYear)) * 100.0) / 
            LAG(AppointmentCount) OVER (PARTITION BY DoctorID ORDER BY AppointmentYear), 
            2
        ) AS YoYGrowthPercentage
    FROM DoctorYearlyAppointments
    WHERE LAG(AppointmentCount) OVER (PARTITION BY DoctorID ORDER BY AppointmentYear) IS NOT NULL
    ORDER BY YoYGrowthPercentage DESC
    LIMIT top_n;
END //

DELIMITER ;