-- Adapted from "/Volumes/SHARE/DSS/IDR Data Requests/DataRequestsProcess/commonScripts/LADMF.sql"
USE DWS_PROD
SELECT Distinct
  Table__94.IDENT_ID_INT as 'MRN ({<PYTHON_PLACEHOLDER : LOCATION_NAME>})',
  dbo.ALL_PATIENTS.PATNT_SSN_DTH_IND,
  dbo.ALL_PATIENTS.PATNT_SSN_DTH_DATE,
  dbo.ALL_PATIENTS.PATNT_DTH_IND,
  dbo.ALL_PATIENTS.PATNT_DTH_DATE
FROM
  dbo.ALL_PATIENTS 
  RIGHT OUTER JOIN dbo.ALL_PATIENT_SNAPSHOTS  ALL_PT_SNAPSHOTS_ENCOUNTER ON (ALL_PT_SNAPSHOTS_ENCOUNTER.PATNT_KEY=dbo.ALL_PATIENTS.PATNT_KEY)
  LEFT OUTER JOIN ( 
    SELECT * 
    FROM dbo.ALL_PATIENT_IDENTITIES 
    WHERE dbo.ALL_PATIENT_IDENTITIES.LOOKUP_IND = 'Y'
    AND dbo.ALL_PATIENT_IDENTITIES.IDENT_ID_TYPE = {<PYTHON_PLACEHOLDER : LOCATION_TYPE>}  -- Use 110 for Jax or 101 for UF
  )  Table__94 ON (Table__94.PATNT_KEY=ALL_PT_SNAPSHOTS_ENCOUNTER.PATNT_KEY)
  
WHERE
  (
   Table__94.IDENT_ID_INT  IN  ({<PYTHON_PLACEHOLDER : LIST_OF_MRNS>})  -- List of MRNs 
   AND
   ( dbo.ALL_PATIENTS.TEST_IND='N'  )
  )
