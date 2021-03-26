from werkzeug.exceptions import HTTPException
import re

HTTP_Validation_codes = {
	200: "OK",
	201: "Created",
	400: "Bad Request",
	401: "Unauthorized",
    422: "Unprocessable Entity",
	404: "Not Found",
	500: "Internal Server Error"
}

def get_failed_response(status_code = 500,  message=None):
    failed_resp = {}
    failed_resp["status"] = "Failed"
    failed_resp["validation_code"] = status_code
    failed_resp["message"] =  message
    raise HTTPException(failed_resp)

def get_success_response(type_str, output = None, message = None , status_code = 200):
    succ_resp = {}
    succ_resp["status"] = "Success"
    succ_resp["validation_code"] = status_code
    succ_resp["message"] = message
    succ_resp[type_str] = output
    return succ_resp

def validate_payload(payload):
    pass