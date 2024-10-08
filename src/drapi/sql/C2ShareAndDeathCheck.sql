USE dws_prod
/*
ANALYST: TP, 6/4/2024
DATABASE SERVER: EDW.shands.ufl.edu
TITLE: C2Share MRN- Consent and Death check
DESCRIPTION: Shows only patients who have not given consent or who have passed away.
INSTRUCTIONS:
	- Insert FacilityID on line 16
	- Insert all MRNs on line 17
*/

DECLARE @SQLString NVARCHAR(MAX) 
DECLARE @Facility varchar(10)
DECLARE @MRNs NVARCHAR(MAX) 

SET @Facility = $facility 
SET @MRNs = '$MRNs' 


SET @SQLString=('
IF ((SELECT count(*) FROM  (
			SELECT distinct
			  Table__1308.IDENT_ID_INT as MRN,
			  dbo.ALL_PATIENTS.CONSENT_SHARE_IND as CONSENT_SHARE_INDICATOR,
			  dbo.ALL_PATIENTS.CONSENT_SHARE_DATE
			FROM dbo.ALL_PATIENTS 
			RIGHT OUTER JOIN dbo.ALL_PATIENT_SNAPSHOTS ALL_PT_SNAPSHOTS_ENCOUNTER ON ALL_PT_SNAPSHOTS_ENCOUNTER.PATNT_KEY=dbo.ALL_PATIENTS.PATNT_KEY
			LEFT OUTER JOIN 
			( 
			  SELECT * 
			  FROM dbo.ALL_PATIENT_IDENTITIES 
			  WHERE dbo.ALL_PATIENT_IDENTITIES.LOOKUP_IND = ''Y''
			  AND dbo.ALL_PATIENT_IDENTITIES.IDENT_ID_TYPE = ' + @Facility + ' --Facility ID
			) Table__1308 ON (Table__1308.PATNT_KEY=ALL_PT_SNAPSHOTS_ENCOUNTER.PATNT_KEY)  
			WHERE
			(
			  Table__1308.IDENT_ID_INT  IN  ('
			+ @MRNs +
			')  --List of all MRNs
			  AND dbo.ALL_PATIENTS.TEST_IND=''N''
			 )
			--check if patient is still consented
			--and dbo.ALL_PATIENTS.CONSENT_SHARE_IND = ''N''
			--order by 2
		  )C2S
	WHERE C2S.CONSENT_SHARE_INDICATOR !=''Y'' or  C2S.CONSENT_SHARE_INDICATOR is null 
	) > 0 )
	SELECT   C2S.MRN,
	  C2S.CONSENT_SHARE_INDICATOR,
	  C2S.CONSENT_SHARE_DATE
	FROM (
			SELECT distinct
			  Table__1308.IDENT_ID_INT as MRN,
			  dbo.ALL_PATIENTS.CONSENT_SHARE_IND as CONSENT_SHARE_INDICATOR,
			  dbo.ALL_PATIENTS.CONSENT_SHARE_DATE
			FROM dbo.ALL_PATIENTS 
			RIGHT OUTER JOIN dbo.ALL_PATIENT_SNAPSHOTS ALL_PT_SNAPSHOTS_ENCOUNTER ON ALL_PT_SNAPSHOTS_ENCOUNTER.PATNT_KEY=dbo.ALL_PATIENTS.PATNT_KEY
			LEFT OUTER JOIN 
			( 
			  SELECT * 
			  FROM dbo.ALL_PATIENT_IDENTITIES 
			  WHERE dbo.ALL_PATIENT_IDENTITIES.LOOKUP_IND = ''Y''
			  AND dbo.ALL_PATIENT_IDENTITIES.IDENT_ID_TYPE = ' + @Facility + ' --Facility ID
			) Table__1308 ON (Table__1308.PATNT_KEY=ALL_PT_SNAPSHOTS_ENCOUNTER.PATNT_KEY)  
			WHERE
			(
			  Table__1308.IDENT_ID_INT  IN  ('
			+ @MRNs +
			')  --List of all MRNs
			  AND dbo.ALL_PATIENTS.TEST_IND=''N''
			 )
			--check if patient is still consented
			--and dbo.ALL_PATIENTS.CONSENT_SHARE_IND = ''N''
			--order by 2
		  )C2S
	WHERE C2S.CONSENT_SHARE_INDICATOR !=''Y'' or  C2S.CONSENT_SHARE_INDICATOR is null 
ELSE
	SELECT ''ALL PATIENTS HAVE CONSENTED.''  AS RESULTS
	')
EXEC (@SQLString)
 
 
SET @SQLString=('
IF ((SELECT count(*) FROM  (
		SELECT Distinct Table__94.IDENT_ID_INT  AS MRN,
		dbo.ALL_PATIENTS.PATNT_SSN_DTH_IND,
		dbo.ALL_PATIENTS.PATNT_SSN_DTH_DATE,
		dbo.ALL_PATIENTS.PATNT_DTH_IND,
		dbo.ALL_PATIENTS.PATNT_DTH_DATE
		FROM
			dbo.ALL_PATIENTS 
			RIGHT OUTER JOIN dbo.ALL_PATIENT_SNAPSHOTS  ALL_PT_SNAPSHOTS_ENCOUNTER ON (ALL_PT_SNAPSHOTS_ENCOUNTER.PATNT_KEY=dbo.ALL_PATIENTS.PATNT_KEY)
			LEFT OUTER JOIN 
			( 
				SELECT * 
				FROM dbo.ALL_PATIENT_IDENTITIES 
				WHERE dbo.ALL_PATIENT_IDENTITIES.LOOKUP_IND = ''Y''
				AND dbo.ALL_PATIENT_IDENTITIES.IDENT_ID_TYPE = ' + @Facility + ' --use 110 for Jax patients
			) Table__94 ON (Table__94.PATNT_KEY=ALL_PT_SNAPSHOTS_ENCOUNTER.PATNT_KEY)
		WHERE
		  (
		   Table__94.IDENT_ID_INT  IN  ('
		+ @MRNs +
		  ')  --List of MRNs 
		   AND dbo.ALL_PATIENTS.TEST_IND=''N'' 
		 )
		  --order by 5
	  )DeathCheck
	WHERE DeathCheck.PATNT_SSN_DTH_IND != ''N'' or DeathCheck.PATNT_DTH_IND != ''N'' or DeathCheck.PATNT_SSN_DTH_IND is null)>0)
 
	SELECT  DeathCheck.MRN,
		DeathCheck.PATNT_SSN_DTH_IND,
		DeathCheck.PATNT_SSN_DTH_DATE,
		DeathCheck.PATNT_DTH_IND,
		DeathCheck.PATNT_DTH_DATE
	FROM (
		SELECT Distinct Table__94.IDENT_ID_INT  AS MRN,
		dbo.ALL_PATIENTS.PATNT_SSN_DTH_IND,
		dbo.ALL_PATIENTS.PATNT_SSN_DTH_DATE,
		dbo.ALL_PATIENTS.PATNT_DTH_IND,
		dbo.ALL_PATIENTS.PATNT_DTH_DATE
		FROM
			dbo.ALL_PATIENTS 
			RIGHT OUTER JOIN dbo.ALL_PATIENT_SNAPSHOTS  ALL_PT_SNAPSHOTS_ENCOUNTER ON (ALL_PT_SNAPSHOTS_ENCOUNTER.PATNT_KEY=dbo.ALL_PATIENTS.PATNT_KEY)
			LEFT OUTER JOIN 
			( 
				SELECT * 
				FROM dbo.ALL_PATIENT_IDENTITIES 
				WHERE dbo.ALL_PATIENT_IDENTITIES.LOOKUP_IND = ''Y''
				AND dbo.ALL_PATIENT_IDENTITIES.IDENT_ID_TYPE = ' + @Facility + ' --use 110 for Jax patients
			) Table__94 ON (Table__94.PATNT_KEY=ALL_PT_SNAPSHOTS_ENCOUNTER.PATNT_KEY)
		WHERE
		  (
		   Table__94.IDENT_ID_INT  IN  ('
		+ @MRNs +
		  ')  --List of MRNs 
		   AND dbo.ALL_PATIENTS.TEST_IND=''N'' 
		 )
		  --order by 5
	  )DeathCheck
	WHERE DeathCheck.PATNT_SSN_DTH_IND != ''N'' or DeathCheck.PATNT_DTH_IND != ''N'' or DeathCheck.PATNT_SSN_DTH_IND is null	
ELSE
	SELECT ''ALL PATIENTS ARE ALIVE.'' AS RESULTS
	')
	EXEC (@SQLString)
