## Individual_Family_Information.txt columns are described below:
- **Column 1 - ExID** is the sample ID in your study
- **Column 2 - Family** is the family ID of your study
- **COlumn 3 - Sex** could be male denoted by "M" or female denoted by "F"
- **Column 4 - Status** which is 1 for affected and 0 for unaffected
- **Column 5 - Age Dx** is the age of diagnosis
- **Column 6 - Relationship** are famialial relationships with the proband
- **Column 7 - Health status** can be affected or unaffected for the sample
- **Column 8 - Final Subtype** is the type of disorder/ cancer under investigation
- **Column 9-11** represents the source of DNA, which could be blood, saliva or Tumour. These columns can be left empty
- **Column 12 - Total Affected** number of affected individuals in a family irrespective if they were sequenced or not OR are dead or alive
- **Column 13 - Range of age** is the convertion of Age Dx column into a range based on the ages in the Incidence_Information.txt

## Incidence_Information.txt columns are described below:
- **Column 1 - Subtype1** is the combination of disease/cancer type (required in column 2) under investigation, sex and ethinicity (required in column 3). Both are separated by space. For instance "Cancer Type Male white" or "Cancer Type Female white"
- **Column 2 - Subtype** is the disease/cancer type from the selected incidence database
- **Column 3 - Subtype** is the sex and ethinicity obtained from the selected incidence database. The sex and ethinicity are separated by a space
- **Column 4 onwards** are the age range provided by the incidence database

## Sharing_Information.txt columns are described below:
- **Column 1 - FamilyID** should be the same as in the Individual_Family_Information.txt column 2 family 
- **Column 2 - Sharing weight** which is the sharing between the sequenced individuals. For example in Fam1 the sharing weight is 1/2 as the father and the proband (son) are affected with the cancer type
- **Column 3 - 1/sw** is the inverse of column 2. For instance, for Fam1 it will be 2
