import struct
import time
import logging

from bluepy.btle import Peripheral, AssignedNumbers, DefaultDelegate, BTLEException

from uuids import UUIDS


class HW25P(Peripheral):

    def __init__(self, mac_address, timeout=0.5, isSecure=False, debug=False):
        FORMAT = '%(asctime)-15s %(name)s (%(levelname)s) > %(message)s'
        logging.basicConfig(format=FORMAT)
        log_level = logging.WARNING if not debug else logging.DEBUG
        self._log = logging.getLogger(self.__class__.__name__)
        self._log.setLevel(log_level)

        self._log.info('Connecting to ' + mac_address)
        if isSecure:
            Peripheral.__init__(self, mac_address)
        else:
            Peripheral.__init__(self, mac_address)

        self.cccid = AssignedNumbers.client_characteristic_configuration
        self.hrmid = AssignedNumbers.heart_rate
        self.hrmmid = AssignedNumbers.heart_rate_measurement

        self._log.info('Connected')

        self.timeout = timeout
        self.mac_address = mac_address

    def device_info(self):
        # device name
        self.device_name = self.readCharacteristic(int(UUIDS.DEVICE_NAME, 16))
        self.device_name = self.device_name.decode("utf-8")
        self._log.info(f"Device Name: {self.device_name}")

        # device apperance
        self.device_appearance_char = self.readCharacteristic(int(UUIDS.DEVICE_APPEARANCE, 16))
        self.device_appearance = struct.unpack("<BB", self.device_appearance_char)[0]
        self._log.info(f"Device Apperance: {UUIDS.APPERANCE_VALUE.get(self.device_appearance)}")

        #device manufacturer
        self.device_manufacturer = self.readCharacteristic(int(UUIDS.DEVICE_MANUFACTURER, 16))
        self.device_manufacturer = self.device_manufacturer.decode("utf-8")
        self._log.info(f"Device Manufacturer: {self.device_manufacturer}")

        #device MODEL_NUMBER
        self.model_number = self.readCharacteristic(int(UUIDS.MODEL_NUMBER, 16))
        self.model_number = self.model_number.decode("utf-8")
        self._log.info(f"Model Number: {self.model_number}")

        #device Serial Number
        self.serial_number = self.readCharacteristic(int(UUIDS.SERIAL_NUMBER, 16))
        self.serial_number = self.serial_number.decode("utf-8")
        self._log.info(f"Serial Number: {self.serial_number}")

        #device Hardware Revision
        self.hw_revision = self.readCharacteristic(int(UUIDS.HARDWARE_REVISION, 16))
        self.hw_revision = self.hw_revision.decode("utf-8")
        self._log.info(f"Hardware Revision: {self.hw_revision}")

        #device Software Revision
        self.sw_revision = self.readCharacteristic(int(UUIDS.SOFTWARE_REVISION, 16))
        self.sw_revision = self.sw_revision.decode("utf-8")
        self._log.info(f"Software Revision: {self.sw_revision}")

    def battery_data(self):
        self.battery_char = self.readCharacteristic(int(UUIDS.BATTERY_INFO_HND, 16))
        self.battery_level = struct.unpack("<B", self.battery_char)[0]
        self._log.info(f"Battery Level: {self.battery_level}")


    def heart_rate_data(self):
        self.hr_countdown = None
        try:
            service, = [s for s in self.getServices() if s.uuid == self.hrmid]
            _ = service.getCharacteristics(forUUID=str(self.hrmmid))

            desc = self.getDescriptors(service.hndStart, service.hndEnd)
            d, = [d for d in desc if d.uuid == self.cccid]

            self.writeCharacteristic(d.handle, b'\x01\00')

            def print_hr(cHandle, data):
                self.hr_countdown = time.perf_counter()
                self._log.info(data[1])

            self.delegate.handleNotification = print_hr
            self._log.info("Waiting for Heart Rate notification ...")

            while True:
                try:
                    if self.hr_countdown and (time.perf_counter() - self.hr_countdown) >= 3:
                        self._log.info("HRM completed")
                        break
                    else:
                        self.waitForNotifications(3.)

                except KeyboardInterrupt:
                    self._log.info("HRM operation closed by user")
                    self.writeCharacteristic(d.handle, b'\x00\00')
                    break

        except BTLEException as btlE:
            self._log.error(f"{btlE}")
