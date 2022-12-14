import sys
import re
from datetime import datetime as dt
from datetime import timedelta

analyse_at_bay_level = True

staff_input_file = 'data_from_chris/patientstaff_data_for_haplotype_network.csv'
metadata_input_file = 'cog_metadata.exet.with-header.csv'

patient_stays_input_filename = 'data_from_chris_reformatted/V2-patient_stays.csv'
if analyse_at_bay_level:
    patient_stays_input_filename = 'data_from_chris_reformatted/V2-patient_stays.at-bay-level.csv'

sys.stderr.write('Using infile:')
sys.stderr.write(patient_stays_input_filename)

### Read the COG-UK metadata spreadsheet
with open(metadata_input_file) as fh:
    lines = fh.readlines()
    lines = [line.rstrip() for line in lines]
fh.close()

### Remove the header line
header = lines.pop(0) 
#sys.stderr.write(header)

class Patient:
    pass

class Stay:
    pass

patients = []

for readline in lines:
    headings = readline.split(',')
    sequence_name, country, adm1, is_pillar_2, sample_date, epi_week, lineage, lineages_version, lineage_conflict, lineage_ambiguity_score, scorpio_call, scorpio_support, scorpio_conflict, del_1605_3, ambiguities, n501y, a222v, n439k, e484k, q27stop, p323l, t1001i, mutations, y453f, p681h, del_21765_6, d614g = headings
    
    ### Remove prefix and suffix from COG-UK ID
    p = re.compile('EXET-[\w\d]{6}')
    m = p.search(sequence_name)
    if m:
        coguk_id = m.group()
    
       ### Create a new Patient object and add it to the list of all Patient objects
        patient = Patient()
        patients.append(patient)
    
        ### Populate attributes of this Patient object
        patient.sequence_name = coguk_id
        patient.country = country 
        patient.adm1 = adm1
        patient.is_pillar_2 = is_pillar_2 
        patient.sample_date = sample_date
        patient.epi_week = epi_week
        patient.lineage = lineage
        patient.lineages_version = lineages_version 
        patient.lineage_conflict = lineage_conflict
        patient.lineage_ambiguity_score = lineage_ambiguity_score
        patient.scorpio_call = scorpio_call
        patient.scorpio_support = scorpio_support
        patient.scorpio_conflict = scorpio_conflict
        patient.del_1605_3 = del_1605_3
        patient.ambiguities = ambiguities
        patient.n501y = n501y
        patient.a222v = a222v
        patient.n439k = n439k
        patient.e484k = e484k
        patient.q27stop = q27stop
        patient.p323l = p323l
        patient.t1001i = t1001i
        patient.mutations = mutations
        patient.y453f = y453f
        patient.p681h = p681h
        patient.del_21765_6 = del_21765_6
        patient.d614g = d614g
        patient.stays = []
        patient.contacts = []

### Read the patient stays spreadsheet
with open(patient_stays_input_filename) as fh:
    lines = fh.readlines()
    lines = [line.rstrip() for line in lines]
fh.close()

### Remove the header line
header = lines.pop(0) 
#sys.stderr.write(header)
     
for readline in lines:
    headings = readline.split(',')

    coguk_id, covid_date, last_infectious_date, start_date, end_date, ward = headings[0:6]

    stay = Stay()
    
    ### Get the appropriate patient
    for patient in patients:
        if patient.sequence_name == coguk_id:
            patient.covid_date = covid_date
            stay.start_date = start_date
            stay.end_date = end_date
            stay.ward = ward
            patient.stays.append(stay)
    
### Now that we have populated the Patient objects with attributes and lists of Stay objects, we can analyse overlapping stays
for patient1 in patients:
    for patient2 in patients:
            if patient1.sequence_name < patient2.sequence_name:
                for stay1 in patient1.stays:
                    for stay2 in patient2.stays:
                        #print(patient1.sequence_name, " versus ", patient2.sequence_name)
                        if stay1.ward == stay2.ward and stay1.ward != "":
                            
                            overlap = False 
                            start_date1 = dt.strptime(stay1.start_date, "%d/%m/%Y")
                            start_date2 = dt.strptime(stay2.start_date, "%d/%m/%Y")
                            end_date1 = dt.strptime(stay1.end_date, "%d/%m/%Y")
                            end_date2 = dt.strptime(stay2.end_date, "%d/%m/%Y")
                            covid_date1 = dt.strptime(patient1.covid_date,"%d/%m/%Y")
                            covid_date2 = dt.strptime(patient2.covid_date,"%d/%m/%Y")
                            if start_date1 >= start_date2 and start_date1 <= end_date2:
                                overlap = True
                            elif end_date1 >= start_date2 and end_date1 <= end_date2:
                                 overlap = True

                            within_14_days = True
                            if covid_date1 < covid_date2:
                                if covid_date1 + timedelta(days=14) < covid_date2:
                                    within_14_days = False
                            elif covid_date2 < covid_date1:
                                if covid_date2 + timedelta(days=14) < covid_date1:
                                    within_14_days = False
                                    
                            if overlap and within_14_days:
                                if covid_date1 < covid_date2:
                                    patient1.contacts.append(patient2)
                                else:
                                    patient2.contacts.append(patient1)

### print the contacts
print('From ID', 'From lineage', 'To ID', 'To lineage')
for patient in patients:
    for contact in set(patient.contacts):
        print(patient.sequence_name, patient.lineage,
              contact.sequence_name, contact.lineage)
    

                                
