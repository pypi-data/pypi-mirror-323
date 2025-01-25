"""Program that runs a query against the SLRAT API and creates inspections from information gathered
Changes last made by Jasper Sheeds 1/21/25"""

import json
import pyodbc
from jsonpath_ng.ext import parse
import requests
import datetime
import os
from dotenv import load_dotenv
from SupportFunctions import email_send, error_log, get_errors
import subprocess

load_dotenv()
base_url = os.getenv("baseurl")
cw_username = os.getenv("cw_username")
cw_password = os.getenv("cw_password")
sl_dog = os.getenv("sl_dog_key")
insp_template_id = 193793
entity_type = "SNGRAVITYMAIN"

class Inspection:
    """ Inspection class to hold individual readings from SL-DOG. """
    def __init__(self, inspection_id, date, inspected_by, record_num, device_num, test_duration, pipe_length, assessment, gps_assessment):
        self.id = str(inspection_id)
        self.date = str(date)
        self.inspectedby = str(inspected_by)
        self.recordnum = str(record_num)
        self.devicenum = str(device_num)
        self.testduration = str(test_duration)
        self.pipelength = str(pipe_length)
        self.assessment = str(assessment)
        self.gpsassessment = str(gps_assessment)

def return_token():
    """ Returns token for CW using login information stored in the env file. """
    url = base_url +  'General/Authentication/Authenticate?data={"LoginName":"' + cw_username + '","Password":"' + cw_password + '","Expires":null}'
    response = json.loads(requests.request("GET", url).text)
    if response['Status'] == 0:
        return response['Value']['Token']
    else:
        error_log("Error: Cityworks Authentication failed.\n")
        return 0

def check_current(date):
    """ Uses a date and gets a list of records already made into inspections in CityWorks from that date. """
    cw_cursor.execute(
        "SELECT (SELECT [Answer] FROM [cwdb].[azteca].[InspQuestion] WHERE [cwdb].[azteca].[InspQuestion].[InspectionID] = [cwdb].[azteca].[Inspection].[InspectionID] AND [QuestionID] = 198024) FROM [cwdb].[azteca].[Inspection] WHERE [InspTemplateName] = 'Sewer Acoustic Inspection' AND NOT [STATUS] = 'CANCEL' AND CONVERT(date, [InspDate]) = '" + date + "'")
    insp_list = cw_cursor.fetchall()
    return str(insp_list)

def find_entity(entity_uid):
    """ Uses entity id from SLDOG inspection and finds the facility id in CityWorks. """
    url = base_url + '/Ams/Entity/Search?data={"EntityType": "' + entity_type + '", "Uids": ["' + entity_uid + '"] }&token=' + cw_token
    response = requests.post(url).text
    data_dic = json.loads(response)
    if data_dic['Status'] == 0:
        match = parse("$.Value.Records..FACILITYID").find(data_dic)
        for entity in match[:1]:
            return entity.value
    else:
        return 0

def create_insps():
    """ Creates an Inspection based on InspectionTemplateID. """
    url = base_url + 'Ams/Inspection/Create?data={"InspTemplateId":' + str(insp_template_id) + ', "EntityType":"' + entity_type + '"}&token=' + cw_token
    response = requests.post(url).text
    data_dic = json.loads(response)
    if data_dic['Status'] == 0:
        match = parse("$.Value.InspectionId").find(data_dic)
        for insp in match[:1]:
            return insp.value
    else:
        error_log("Error: Error in creating an inspection\n")
        return 0

def add_entity(inspection_id, entity_id):
    """ Adds an entity to created inspection. """
    url = base_url + 'Ams/Inspection/AddEntity?data={"InspectionId": ' + str(inspection_id) + ', "EntityType": "' + entity_type + '", "EntityUid": "' + entity_id + '"}&token=' + cw_token
    response = requests.post(url).text
    data_dic = json.loads(response)
    if data_dic['Status'] == 0 and len(data_dic['WarningMessages']) == 0:
        return 1
    else:
        error_log("Error: Error in adding entity " + str(entity_id) + " to " + str(inspection_id) + " inspection\n")
        return 0

def get_emp_sid(emp_id):
    """ Gets employee sid by using employee get_emp_sid. """
    url = base_url + 'Ams/Employee/Search?data={"EmployeeId": ["' + str(emp_id) + '"]}&token=' + cw_token
    response = requests.post(url).text
    data_dic = json.loads(response)
    if data_dic['Status'] == 0:
        match = int((parse("$.Value").find(data_dic))[0].value[0])
        return match
    else:
        error_log("Error: Error in getting " + str(emp_id) + " employeesid\n")
        return 0

def update_insp(inspection):
    """ Updates inspection with details of record. """
    url = (base_url + 'Ams/Inspection/Update?data={"InspectionId": ' + inspection.id + ', "InspectedBySid": ' + inspection.inspectedby
           + ', "InspectionDate": "' + inspection.date + '", "ActualFinishDate": "' + inspection.date + '", "Answers":[{"AnswerValue":"'
           + inspection.recordnum + '","QuestionId":198024,"AnswerId":187935},{"AnswerValue":' + inspection.devicenum +
           ',"QuestionId":198018,"AnswerId":187909},{"AnswerValue":' + inspection.testduration + ',"QuestionId":198019,"AnswerId":187928},{"AnswerValue":' +
           inspection.pipelength + ',"QuestionId":198020,"AnswerId":187929},{"AnswerValue":' + inspection.assessment +
           ',"QuestionId":198021,"AnswerId":187930},{"AnswerValue":' + inspection.gpsassessment + ',"QuestionId":198022,"AnswerId":187931}]}&token=' + cw_token)
    response = requests.post(url).text

    data_dic = json.loads(response)
    if data_dic['Status'] == 0:
        return True
    else:
        error_log("Error: Error in updating inspection " + inspection.id + "\n")
        return False

def close_insp(insp_id):
    """ Closes the inspection. """
    url = base_url + "Ams/Inspection/Close?data={%20%20%20%20%20%22InspectionIds%22:%20[" + insp_id +"]%20}&token=" + cw_token
    response = requests.post(url).text
    data_dic = json.loads(response)
    if data_dic['Status'] == 0:
        return True
    else:
        error_log("Error: Error in closing inspection " + insp_id + "\n")
        return False

def get_rat_insp(date):
    """ Gets all the valid records from sldog for date. """
    url = 'https://www.sl-dog.com/API/SLDOGAPI/Measurements/Search'
    add_day = datetime.date.fromisoformat(date) + datetime.timedelta(days=1)
    payload = json.dumps({
        "draw": 1,
        "start": 0,
        "length": 5000,
        "columns": [
            {
                "data": "UTCTime",
                "search": {
                    "value": "",
                    "fixed": ["" + date + "","" + str(add_day) + ""]
                }
            },
            {
                "data": "MeasurementStatus",
                "search": {
                    "value": "",
                    "fixed": ["Valid"]
                }
            },
            {
                "data": "IsHidden",
                "search": {
                    "value": "",
                    "fixed": ["false"]
                }
            }
        ]
    })
    headers = {
        'x-api-key': sl_dog,
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Host': 'www.sl-dog.com',
        'Connection': 'keep-alive'
    }
    response = requests.post(url, headers=headers, data=payload).text
    data_dic = json.loads(response)
    global inspection_list
    inspection_list = []
    try:
        if data_dic['success']:
            match = parse("$.'data'.[*]").find(data_dic)
            for rec in match:
                if ("'" + str(rec.value['RecordNumber']) + "'") not in current_list:
                    try:
                        entityFID = find_entity(rec.value['UserField1'])
                        if entityFID is not None:
                            try:
                                insp_id = create_insps()
                                if add_entity(insp_id, entityFID) == 1:
                                    try:
                                        emp = get_emp_sid(rec.value['UserField3'])
                                    except:
                                        emp = 0

                                    datetz = datetime.datetime.fromisoformat(rec.value['UTCTime']) - datetime.timedelta(
                                        hours=5)
                                    tempinsp = Inspection(insp_id, datetz, emp, rec.value['RecordNumber'],
                                                          rec.value['RxDeviceNum'],
                                                          rec.value['TestDuration'], rec.value['EvalPipeLength'],
                                                          rec.value['Assessment'], rec.value['GPSAssessment'])
                                    if update_insp(tempinsp):
                                        close_insp(str(insp_id))

                                else:
                                    tempinsp = Inspection(insp_id, datetz, emp, rec.value['RecordNumber'],
                                                          rec.value['RxDeviceNum'],
                                                          rec.value['TestDuration'], rec.value['EvalPipeLength'],
                                                          rec.value['Assessment'], rec.value['GPSAssessment'])
                                    update_insp(tempinsp)
                            except:
                                error_log("Error: Could not find entity, inspection will not be created")


                    except:
                        error_log("Error: Error in creating Inspections in CWORKS\n")

    except:
        error_log("Error: Error in getting Rat Inspections\n")
        return 0

def main():
    try:
        today_date = datetime.date.today()
        global cw_token
        cw_token = return_token()
        try:
            cw_connection = pyodbc.connect('Driver={SQL Server};'
                                           'Server=cworks_prod;'
                                           'Database=cwdb;'
                                           'UID=' + os.getenv("sql_user") + ';'
                                            'PWD=' + os.getenv("sql_pass") + ';')
            global cw_cursor
            cw_cursor = cw_connection.cursor()
            global current_list
            current_list = check_current(str(today_date))
            get_rat_insp(str(today_date))
            subprocess.run('Notepad.exe')
        except:
            error_log("Error: Error creating CWORKS Prod SQL Connection.\n")
    finally:
        temp_error = get_errors()
        if len(temp_error) > 0:
            error_final_string = ''.join(str(x) for x in temp_error)
            email_send(error_final_string)