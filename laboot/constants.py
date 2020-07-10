# constants.py
from LWTest.common import oscomp
from LWTest.common.oscomp import OSBrand, QSettingsAdapter

TEMPERATURE_REFERENCE = 'C17'

SENSOR_1_REPORTING_RESULT = 'D7'
SENSOR_2_REPORTING_RESULT = 'E7'
SENSOR_3_REPORTING_RESULT = 'F7'
SENSOR_4_REPORTING_RESULT = 'G7'
SENSOR_5_REPORTING_RESULT = 'H7'
SENSOR_6_REPORTING_RESULT = 'I7'
REPORTING_RESULTS = (SENSOR_1_REPORTING_RESULT, SENSOR_2_REPORTING_RESULT, SENSOR_3_REPORTING_RESULT,
                     SENSOR_4_REPORTING_RESULT, SENSOR_5_REPORTING_RESULT, SENSOR_6_REPORTING_RESULT)

SENSOR_1_RSSI_RESULT = 'D8'
SENSOR_2_RSSI_RESULT = 'E8'
SENSOR_3_RSSI_RESULT = 'F8'
SENSOR_4_RSSI_RESULT = 'G8'
SENSOR_5_RSSI_RESULT = 'H8'
SENSOR_6_RSSI_RESULT = 'I8'
RSSI_RESULTS = (SENSOR_1_RSSI_RESULT, SENSOR_2_RSSI_RESULT, SENSOR_3_RSSI_RESULT,
                SENSOR_4_RSSI_RESULT, SENSOR_5_RSSI_RESULT, SENSOR_6_RSSI_RESULT)

SENSOR_1_CALIBRATION_RESULT = 'D16'
SENSOR_2_CALIBRATION_RESULT = 'E16'
SENSOR_3_CALIBRATION_RESULT = 'F16'
SENSOR_4_CALIBRATION_RESULT = 'G16'
SENSOR_5_CALIBRATION_RESULT = 'H16'
SENSOR_6_CALIBRATION_RESULT = 'I16'
CALIBRATIONS_RESULTS = (SENSOR_1_CALIBRATION_RESULT, SENSOR_2_CALIBRATION_RESULT, SENSOR_3_CALIBRATION_RESULT,
                        SENSOR_4_CALIBRATION_RESULT, SENSOR_5_CALIBRATION_RESULT, SENSOR_6_CALIBRATION_RESULT)

SENSOR_1_TEMPERATURE_RESULT = 'D17'
SENSOR_2_TEMPERATURE_RESULT = 'E17'
SENSOR_3_TEMPERATURE_RESULT = 'F17'
SENSOR_4_TEMPERATURE_RESULT = 'G17'
SENSOR_5_TEMPERATURE_RESULT = 'H17'
SENSOR_6_TEMPERATURE_RESULT = 'I17'
TEMPERATURE_RESULTS = (SENSOR_1_TEMPERATURE_RESULT, SENSOR_2_TEMPERATURE_RESULT, SENSOR_3_TEMPERATURE_RESULT,
                       SENSOR_4_TEMPERATURE_RESULT, SENSOR_5_TEMPERATURE_RESULT, SENSOR_6_TEMPERATURE_RESULT)

SENSOR_1_FAULT_CURRENT_RESULT = 'D18'
SENSOR_2_FAULT_CURRENT_RESULT = 'E18'
SENSOR_3_FAULT_CURRENT_RESULT = 'F18'
SENSOR_4_FAULT_CURRENT_RESULT = 'G18'
SENSOR_5_FAULT_CURRENT_RESULT = 'H18'
SENSOR_6_FAULT_CURRENT_RESULT = 'I18'
FAULT_CURRENT_RESULTS = (SENSOR_1_FAULT_CURRENT_RESULT, SENSOR_2_FAULT_CURRENT_RESULT, SENSOR_3_FAULT_CURRENT_RESULT,
                         SENSOR_4_FAULT_CURRENT_RESULT, SENSOR_5_FAULT_CURRENT_RESULT, SENSOR_6_FAULT_CURRENT_RESULT)

SENSOR_1_HIGH_VOLTAGE_RESULT = 'E26'
SENSOR_2_HIGH_VOLTAGE_RESULT = 'F26'
SENSOR_3_HIGH_VOLTAGE_RESULT = 'G26'
SENSOR_4_HIGH_VOLTAGE_RESULT = 'H26'
SENSOR_5_HIGH_VOLTAGE_RESULT = 'I26'
SENSOR_6_HIGH_VOLTAGE_RESULT = 'J26'
HIGH_VOLTAGE_RESULTS = (SENSOR_1_HIGH_VOLTAGE_RESULT, SENSOR_2_HIGH_VOLTAGE_RESULT, SENSOR_3_HIGH_VOLTAGE_RESULT,
                        SENSOR_4_HIGH_VOLTAGE_RESULT, SENSOR_5_HIGH_VOLTAGE_RESULT, SENSOR_6_HIGH_VOLTAGE_RESULT)

SENSOR_1_LOW_VOLTAGE_RESULT = 'E31'
SENSOR_2_LOW_VOLTAGE_RESULT = 'F31'
SENSOR_3_LOW_VOLTAGE_RESULT = 'G31'
SENSOR_4_LOW_VOLTAGE_RESULT = 'H31'
SENSOR_5_LOW_VOLTAGE_RESULT = 'I31'
SENSOR_6_LOW_VOLTAGE_RESULT = 'J31'
LOW_VOLTAGE_RESULTS = (SENSOR_1_LOW_VOLTAGE_RESULT, SENSOR_2_LOW_VOLTAGE_RESULT, SENSOR_3_LOW_VOLTAGE_RESULT,
                       SENSOR_4_LOW_VOLTAGE_RESULT, SENSOR_5_LOW_VOLTAGE_RESULT, SENSOR_6_LOW_VOLTAGE_RESULT)

SENSOR_1_RAW_CONFIG_RESULT = 'D37'
SENSOR_2_RAW_CONFIG_RESULT = 'E37'
SENSOR_3_RAW_CONFIG_RESULT = 'F37'
SENSOR_4_RAW_CONFIG_RESULT = 'G37'
SENSOR_5_RAW_CONFIG_RESULT = 'H37'
SENSOR_6_RAW_CONFIG_RESULT = 'I37'
RAW_CONFIG_RESULTS = (SENSOR_1_RAW_CONFIG_RESULT, SENSOR_2_RAW_CONFIG_RESULT, SENSOR_3_RAW_CONFIG_RESULT,
                      SENSOR_4_RAW_CONFIG_RESULT, SENSOR_5_RAW_CONFIG_RESULT, SENSOR_6_RAW_CONFIG_RESULT)

SENSOR_1_PERSISTENCE_RESULT = 'D39'
SENSOR_2_PERSISTENCE_RESULT = 'E39'
SENSOR_3_PERSISTENCE_RESULT = 'F39'
SENSOR_4_PERSISTENCE_RESULT = 'G39'
SENSOR_5_PERSISTENCE_RESULT = 'H39'
SENSOR_6_PERSISTENCE_RESULT = 'I39'
PERSISTENCE_RESULTS = (SENSOR_1_PERSISTENCE_RESULT, SENSOR_2_PERSISTENCE_RESULT, SENSOR_3_PERSISTENCE_RESULT,
                       SENSOR_4_PERSISTENCE_RESULT, SENSOR_5_PERSISTENCE_RESULT, SENSOR_6_PERSISTENCE_RESULT)

ALL_RESULTS = (RSSI_RESULTS, REPORTING_RESULTS, RAW_CONFIG_RESULTS, HIGH_VOLTAGE_RESULTS, LOW_VOLTAGE_RESULTS,
               CALIBRATIONS_RESULTS, PERSISTENCE_RESULTS, FAULT_CURRENT_RESULTS, TEMPERATURE_RESULTS)

TEST_TIMED_OUT = 1000

if oscomp.os_brand == OSBrand.MAC:
    CHROMEDRIVER_PATH = r"laboot/resources/drivers/chromedriver/macos/version_83-0-4103-39/chromedriver"
else:
    CHROMEDRIVER_PATH = r"laboot/resources/drivers/chromedriver/windows/version_83-0-4103-39/chromedriver.exe"

if QSettingsAdapter.value('DEBUG') == 'true':
    URL_CONFIGURATION = "http://10.211.55.18:5000/configuration"
    URL_MODEM_STATUS = "http://10.211.55.18:5000/modemstatus"

    REQUEST_TIMEOUT = 10
    TEST_TIME = 60
    LINK_CHECK_TIME = 10
else:
    URL_CONFIGURATION = "http://192.168.2.1/index.php/main/configuration"
    URL_MODEM_STATUS = "http://192.168.2.1/index.php/main/modem_status"

    REQUEST_TIMEOUT = 10
    TEST_TIME = 1500
    LINK_CHECK_TIME = 10

BLANK_SERIAL_NUMBER = "0"
