#######################################
# Standard All of Us UBR functions
#######################################

import pandas as pd
import re 

#UBR Category 1: RaceEthnicity
def UBRRaceEthnicity(race_codes, hispanic):
    #Return 1 if age at consent  < 18 or >= 65. Otherwise, return 0.
    if hispanic == 1:
        return 1
    elif race_codes in ('White', 'PreferNotToAnswer', 'None', 'Skip'):
        return 0
    else: #Note this currently _counts_ as UBR people who answered "None of These"
        return 1

    
#UBR Category 2: Age
def UBRAge(ageAtConsent):
    #Return 1 if age at consent  < 18 or >= 65. Othersies, return 0.
    if ageAtConsent < 18:
        return 1
    elif ageAtConsent >= 65:
        return 1
    else:
        return 0

    
#UBR Category 3: Sex
def UBRSex(sex, countFemalesAsUBR):
    if sex in ('SexAtBirth_Intersex', 'SexAtBirth_SexAtBirthNoneOfThese'): #These sex values always count as UBR
        return 1
    elif (countFemalesAsUBR == True) and (sex == 'SexAtBirth_Female'): #Count Females if we're supposed to
        return 1
    else: #sex = null, male, PMI_Skip, or PMI_PreferNotToAnswer
        return 0

    
#UBR Category 4: Sexual & Gender Minorities    
def UBRSexualAndGenderMinorities(sexual_orientation, gender, sex, countFemalesAsUBR):
    
    #Handle Sexual Orientation
    #Anything but PreferNotToAnswer, Straight, or null counts as UBR
    if pd.notnull(sexual_orientation) and sexual_orientation not in ('SexualOrientation_Straight', 'PMI_PreferNotToAnswer'):
        return 1

    #Handle Gender Identity where gender ID does not match sex at birth
    #UBR True if gender ID does NOT match sex at birth
    if pd.notnull(sex) and (sex != 'PMI_Skip') and (sex != 'PMI_PreferNotToAnswer') and (gender == 'GenderIdentity_Man') and (sex != 'SexAtBirth_Male'): 
        return 1
    elif pd.notnull(sex) and (sex != 'PMI_Skip') and (sex != 'PMI_PreferNotToAnswer') and (gender == 'GenderIdentity_Woman') and (sex != 'SexAtBirth_Female'): 
        return 1
    
    #Note: this also catches: (sex in ('SexAtBirth_Intersex', 'SexAtBirth_SexAtBirthNoneOfThese') and
    #                         gender in ('GenderIdentity_Man', 'GenderIdentity_Woman')):
    
    #Handle various gender identities             
    if gender in ('GenderIdentity_Man', 'PMI_PreferNotToAnswer', 'PMI_Skip'): #These gender ID values always count as NOT UBR
        return 0
    elif (countFemalesAsUBR == True) and (gender == 'GenderIdentity_Woman'): #Count Females if we're supposed to
        return 1
    elif (countFemalesAsUBR == False) and (gender == 'GenderIdentity_Woman'): #Don't Count Females if we're not supposed to
        return 0
    elif pd.isnull(gender): #Don't count skipped (null) values
        return 0
    else: #all other gender identities count as UBR
        return 1
    
    
#UBR Category V: Income
def UBRIncome(income):
    if income == 'PMI_Skip':
        return 0
    elif income in ('AnnualIncome_less10k', 'AnnualIncome_10k25k'): #These income values always count as UBR
        return 1
    else: #nothing else counts right now
        return 0
    

#UBR Category VI: Educational Attainment
def UBREducation(education):
    if education == 'PMI_Skip':
        return 0
    elif education in ('HighestGrade_NeverAttended', 'HighestGrade_OneThroughFour', 'HighestGrade_FiveThroughEight', 'HighestGrade_NineThroughEleven'): #These education values always count as UBR
        return 1
    else: #nothing else counts
        return 0
    

#Load the lookup table for UBR zip codes
def LoadUBRZipCodes(zipsFilePath):
    #Load the UBR zip code list of rural zip codes
    zipCodeData = pd.read_csv(zipsFilePath)
    zip_codes = sorted(myData.zip_code())
    return zip_codes

#UBR Category VII: Geography
def UBRGeography(ppt_zip_code, rural_zip_codes):
    #Expects a participant zip code as a string and a bunch of UBR zip codes as a list
    
    #Search to see if the participant's zip code is in rural zip codes list
    #ToDo: This is the preliminary version. May refine later using more granular data. Fix pattern matching. 
    #  Currently throws an error if the code below is not commented out. 
    if pd.isnull(ppt_zip_code) or ppt_zip_code == '': #gracefully handle null(NaN) values or empty strings
        return 0  
    if re.match("\d{5}-\d{4}",ppt_zip_code)!=None: #gracefully handle 9-digit zip codes
         z=ppt_zip_code[0:5]
         if int(z) in rural_zip_codes:
             return 1
         else:
             return 0
    if re.match("^\d{5}",ppt_zip_code)==None: #Gracefully handle other malformed zip codes
         return 0
    if int(ppt_zip_code) in rural_zip_codes:
        return 1
    else:
        return 0


#UBR Category VIII: Access to Care
def UBRAccessToCare():
    #Placeholder for when we have access to care data
    return 0


#UBR Category IX: Disability
def UBRDisability():
    #Placeholder for when we have access to disability data
    return 0


def PrintUBR(df):
    print('UBR Percentages:')
    ancestryUBR = df[
        (df['UBR1_RaceEthnicity'] == 1)
        ].shape[0]
    print(' • Ancestry ', "{:,}%".format(round(ancestryUBR / df.shape[0] * 100, 2)), sep='')

    ageUBR = df[
        (df['UBR2_Age'] == 1)
        ].shape[0]
    print(' • Age ', "{:,}%".format(round(ageUBR / df.shape[0] * 100, 2)), sep='')

    sexUBR = df[
        (df['UBR3_Sex'] == 1)
        ].shape[0]
    print(' • Sex ', "{:,}%".format(round(sexUBR / df.shape[0] * 100, 2)), sep='')

    sGMUBR = df[
        (df['UBR4_SexualAndGenderMinorities'] == 1)
        ].shape[0]
    print(' • Sexual & Gender Minorities ', "{:,}%".format(round(sGMUBR / df.shape[0] * 100, 2)), sep='')

    incomeUBR = df[
        (df['UBR5_Income'] == 1)
        ].shape[0]
    print(' • Income ', "{:,}%".format(round(incomeUBR / df.shape[0] * 100, 2)), sep='')

    educationUBR = df[
        (df['UBR6_Education'] == 1)
        ].shape[0]
    print(' • Education ', "{:,}%".format(round(educationUBR / df.shape[0] * 100, 2)), sep='')

    geographicUBR = df[
        (df['UBR7_Geography'] == 1)
        ].shape[0]
    print(' • Geography ', "{:,}%".format(round(geographicUBR / df.shape[0] * 100, 2)), sep='')


    overallUBR = df[
        ((df['UBR1_RaceEthnicity'] == 1) |
        (df['UBR2_Age'] == 1) |
        (df['UBR3_Sex'] == 1) |
        (df['UBR4_SexualAndGenderMinorities'] == 1) |
        (df['UBR5_Income'] == 1) |
        (df['UBR6_Education'] == 1) |
        (df['UBR7_Geography'] == 1))
        ].shape[0]
    print(' • Overall ', "{:,}%".format(round(overallUBR / df.shape[0] * 100, 2)), sep='')
    
    return 0