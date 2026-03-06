# Configuration.py

from CyberSource import *
from CyberSource.logging.log_configuration import LogConfiguration
import os


class Configuration:
    def __init__(self):
        self.authentication_type = "http_signature"
        self.run_environment = "apitest.cybersource.com"
        self.use_metakey = False
        self.portfolio_id = ''

        self.IntermediateHost = "https://manage.windowsazure.com"
        self.request_json_path = ""

        # PRODUCTION
        # self.merchant_id = "tidal_vape_limited_cs"
        # self.merchant_id = "tidal_vape_api_cs"
        # self.merchant_keyid = 'f15c90c7-9416-4633-8f27-b200f94e95ca'
        # self.merchant_secretkey = 'ayOP5iew3zerMcZRzxkTwkiNJUkOVHEBtY6hIRsQDOw='
        # self.host = "https://api.cybersource.com"

        # SANDBOX
        self.merchant_id = "tidal_vape_test_cs"
        self.merchant_keyid = '319f108b-cdcf-4a35-9701-7c339d0983a4'
        self.merchant_secretkey = 'suJ3LZ9YQX4Thlnm5zJBbk9ilGnyTcXvTYsvlMXRLug='
        self.host = "https://apitest.cybersource.com"

        self.timeout = 1000
        self.enable_log = True
        self.log_file_name = "cybs"
        self.log_maximum_size = 10487560
        self.log_directory = os.path.join(os.getcwd(), "Logs")
        self.log_level = "Debug"
        self.enable_masking = False
        self.log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        self.log_date_format = "%Y-%m-%d %H:%M:%S"

    def get_configuration(self):
        configuration_dictionary = {}
        configuration_dictionary["authentication_type"] = self.authentication_type
        configuration_dictionary["merchantid"] = self.merchant_id
        configuration_dictionary["run_environment"] = self.host
        configuration_dictionary["request_json_path"] = self.request_json_path
        configuration_dictionary["merchant_keyid"] = self.merchant_keyid
        configuration_dictionary["merchant_secretkey"] = self.merchant_secretkey
        configuration_dictionary["use_metakey"] = self.use_metakey
        configuration_dictionary["portfolio_id"] = self.portfolio_id
        configuration_dictionary["timeout"] = self.timeout

        log_config = LogConfiguration()
        log_config.set_enable_log(self.enable_log)
        log_config.set_log_directory(self.log_directory)
        log_config.set_log_file_name(self.log_file_name)
        log_config.set_log_maximum_size(self.log_maximum_size)
        log_config.set_log_level(self.log_level)
        log_config.set_enable_masking(self.enable_masking)
        log_config.set_log_format(self.log_format)
        log_config.set_log_date_format(self.log_date_format)
        configuration_dictionary["log_config"] = log_config

        return configuration_dictionary


# api_key 2419b655-8148-4b59-a3da-8010c421be5d
# shared v9ACwZ3VeJN63Wfk45GZg0v2ikZ6/+4LE9N1L3JE3bw=
