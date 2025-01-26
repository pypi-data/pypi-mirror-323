import http.client
import uuid
import json
from typing import Dict, List, Optional

class ValidationClient:
    def __init__(self, 
                 api_key: str, 
                 base_url: str = "127.0.0.1:8000", 
                 endpoint: str = "/validate"):

        self.api_key = api_key
        self.base_url = base_url
        self.endpoint = endpoint
        self._connection = None

    def _create_connection(self):
        self._connection = http.client.HTTPConnection(self.base_url)

    def _generate_boundary(self) -> str:
        return f"----WebKitFormBoundary{uuid.uuid4().hex}"

    def start_event(self, endpoint: str = "/start_event"):
        if not self._connection:
            self._create_connection()

        # Prepare multipart form data
        boundary = self._generate_boundary()
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        }

        try:
            self._connection.request("POST", endpoint, body="", headers=headers)
            response = self._connection.getresponse()
            response_data = response.read().decode("utf-8")
            self.event_id = json.loads(response_data)["event_id"]
        except Exception as e:
            print(f"Error: {e}")

    def validate(self, 
                 text: str,
                 type: str = "input",
                 system_prompt: str = "validate") -> Dict:

        if not self._connection:
            self._create_connection()

        self.type = type if type in {"input", "output"} else "input"
        # Prepare multipart form data
        boundary = self._generate_boundary()
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        }

        parts = [
            f"--{boundary}",
            'Content-Disposition: form-data; name="type"',
            "",
            type,
            f"--{boundary}",
            'Content-Disposition: form-data; name="userprompt"',
            "",
            text.encode("utf-8"),
            f"--{boundary}",
            'Content-Disposition: form-data; name="systemprompt"',
            "",
            system_prompt,
            f"--{boundary}",
            'Content-Disposition: form-data; name="eventId"',
            "",
            self.event_id,
            f"--{boundary}--",
            "",
        ]

        body = "\r\n".join(
            str(part, "utf-8") if isinstance(part, bytes) else part for part in parts
        )

        try:
            self._connection.request("POST", self.endpoint, body=body.encode("utf-8"), headers=headers)
            response = self._connection.getresponse()
            response_data = response.read().decode("utf-8")
            return response_data

        except Exception as e:
            print(f"Validation error: {e}")
            return {}

    def humaize_response(self, response_data: str):
        if(response_data is None): return
        return self._parse_validation_results(response_data)


    def _get_validators(self):
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            connection = http.client.HTTPConnection(self.base_url)
            connection.request("GET", "/validators", headers=headers)
            response = connection.getresponse()
            response_data = json.loads(response.read().decode('utf-8'))
            
            # Assuming backend returns a list of validator names
            return response_data.get('input_validators', []) if self.type=="input" else response_data.get('output_validators', [])
        
        except Exception as e:
            print(f"Error retrieving validators: {e}")
            return []
        finally:
            connection.close()

    def _parse_validation_results(self, validation_output: str) -> Dict:
        validators = self._get_validators() or [
            "DetectPII", "ProfanityFree", "WebSanitization", "GibberishText", 
            "NSFWText", "FinancialTone", "SecretsPresent", "MentionsDrugs", 
            "RedundantSentences", "ToxicLanguage", "ValidPython", 
            "DetectJailbreak", "ValidOpenApiSpec", "ValidJson", 
            "ValidSQL", "ValidURL", "HasUrl"
        ]
        try:
            validation_data = json.loads(validation_output)
            validation_summaries = validation_data.get("validation_outcome", {}).get("validation_summaries", [])
            
            results = {validator: 0 for validator in validators}
            
            for summary in validation_summaries:
                validator_name = summary.get("validator_name", "").lower()
                if summary.get("validator_status") == "fail":
                    matching_validator = next((v for v in validators if v.lower() == validator_name), None)
                    if matching_validator:
                        results[matching_validator] = 1
            
            return results
        
        except Exception as e:
            print(f"Error parsing validation results: {e}")
            return {}

    def close(self):
        if self._connection:
            self._connection.close()