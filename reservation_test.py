import unittest
import datetime
import requests

URL = "https://wcg-apis.herokuapp.com"
RESERVE_DATABASE = URL + "/reservation_database"
PATH = URL + "/reservation"
CITIZEN_PATH = URL + "/registration"
FEEDBACK = {
    'success': 'reservation success!',
    'missing_key': 'reservation failed: missing some attribute',
    'invalid_id': 'reservation failed: invalid citizen ID',
    'not_registered': 'reservation failed: citizen ID is not registered',
    'reserved': 'reservation failed: there is already a reservation for this citizen',
    'invalid_vaccine': 'report failed: invalid vaccine name'
}

class ReservationTest(unittest.TestCase):
    """
    Class of unittests for the Reservation API from World Class Government group

    @author Nutta Sittipongpanich
    """
    def setUp(self):
        # Delete if citizen already made a reservation
        requests.delete(RESERVE_DATABASE, data=self.create_payload())

        # Register valid citizen to test reservation
        requests.post(CITIZEN_PATH, data=self.create_citizen())

        # default payload to make a reservation
        self.reservation = self.create_payload()

        # payload that missing parameters
        self.missing_key_payloads = [
            self.create_payload(citizen_id=""),
            self.create_payload(site_name=""),
            self.create_payload(vaccine_name="")
        ]

        # citizen_id is not the number of 13 digits
        self.invalid_citizen_id_payloads = [
            self.create_payload(citizen_id="625648"),             # less than 13
            self.create_payload(citizen_id="1122334455667788"),   # more than 13
            self.create_payload(citizen_id="12abc567กข890"),      # contain alphabets
        ]

        # vaccine names that are not in these avaiable vaccines [Pfizer, Astra, Sinofarm, or Sinovac]
        self.invalid_vaccine_payloads = [
            self.create_payload(vaccine_name="P"),
            self.create_payload(vaccine_name="PFIZER"),
            self.create_payload(vaccine_name="Moderna"),
        ]

    def tearDown(self):
        # Delete reservation from reservation database
        requests.delete(RESERVE_DATABASE, data=self.reservation)

    def create_payload(
            self,
            citizen_id="1234567890123",
            site_name="OGYH",
            vaccine_name="Pfizer"):
        """Return dict of reservation with requested attributes.

        Args:
            citizen_id (str, optional): Citizen's identification number, set default value as "1234567891234"
            site_name (str, optional): Vaccination site name, set default value as "OGYH"
            vaccine_name (str, optional): The COVID-19 vaccine name that user wants to reserve, set default value as "Pfizer"

        Return:
            Dict: payload of Reservation API
        """
        return {
            'citizen_id': citizen_id,
            'site_name': site_name,
            'vaccine_name': vaccine_name
        }

    def create_citizen(
            self,
            citizen_id="1234567891234",
            firstname="John",
            lastname="Doe",
            birthdate="01/01/2001",
            occupation="Student",
            address="1/53 Ngamwongwaan, Laksi, Bangkok 10210"):
        """Return dict of valid citizen reservation with requested attributes.

        Args:
            citizen_id (str, optional): Citizen's identification number, set default value as "1234567891234"
            firstname (str, optional): Firstname of the Citizen, set default value as "John"
            lastname (str, optional): Lastname of the Citizen, set default value as "Doe"
            birthdate (str, optional): Birthdate of the Citizen, set default value as "01/01/2001"
            occupation (str, optional): Occupation of the Citizen, set default value as "Student"
            address (str, optional): Address of the Citizen, set default value as "1/53 Ngamwongwaan, Laksi, Bangkok 10210"

        Return:
            Dict: payload of Registration API
        """
        return {
            'citizen_id': citizen_id,
            'name': firstname,
            'surname': lastname,
            'birth_date': birthdate,
            'occupation': occupation,
            'address': address
        }

    def return_feedback(self, response):
        """Return feedback of the response

        Args:
            response (Response): response from a request

        Return:
            str: feedback
        """
        return response.json()['feedback']

    def test_make_reservation(self):
        """Test making a reservation
        """        
        response = requests.post(PATH, data=self.reservation)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.get_feedback(response), FEEDBACK['success'])

    def test_reserve_missing_key(self):
        """Test making a reservation with missing attributes
        """
        for payload in self.missing_key_payloads:
            response = requests.post(PATH, data=payload)
            self.assertEqual(self.get_feedback(response), FEEDBACK['missing_key'])

    def test_reserve_invalid_citizen_id(self):
        """Test making a reservation with invalid citizen_id
        """
        for payload in self.invalid_citizen_id_payloads:
            response = requests.post(PATH, data=payload)
            self.assertEqual(self.get_feedback(response), FEEDBACK['invalid_id'])

    def test_reserve_unregistered_citizen_id(self):
        """Test making a reservation with unregistered citizen_id
        """
        response = requests.post(PATH, data=self.create_payload(citizen_id="1111111111111"))
        self.assertEqual(self.get_feedback(response), FEEDBACK['invalid_id'])

    def test_reserve_same_id(self):
        """Test making a reservation with citizen_id that already made a reservation
        """
        response_1 = requests.post(PATH, data=self.reservation)
        self.assertEqual(self.get_feedback(response_1), FEEDBACK['success'])

        response_2 = requests.post(PATH, data=self.reservation)
        self.assertEqual(self.get_feedback(response_2), FEEDBACK['reserved'])

    def test_reserve_invalid_vaccine(self):
        """Test making a reservation with invalid vaccine names
        """
        for payload in self.invalid_vaccine_payloads:
            response = requests.post(PATH, data=payload)
            self.assertEqual(self.get_feedback(response), FEEDBACK['invalid_vaccine'])

if __name__ == '__main__':
    unittest.main()
