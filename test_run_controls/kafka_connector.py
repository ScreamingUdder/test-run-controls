from PySide2.QtCore import QObject, QUrl, Property, Signal, Slot
import test_run_controls.kafka as kafka


class KafkaConnector(QObject):

    def __init__(self):
        super().__init__()
        self.instrument_name = kafka.default_instrument_name
        self.broker_address = kafka.default_broker_address
        self.broker_version = kafka.default_broker_version

    def get_instrument(self):
        return self.instrument_name

    def set_instrument(self, val: str):
        self.instrument_name = val

    instrument_changed = Signal()

    instrument = Property(str, get_instrument, set_instrument, notify=instrument_changed)

    def get_broker(self):
        return self.broker_address

    def set_broker(self, val: str):
        self.broker_address = val

    broker_changed = Signal()

    broker = Property(str, get_broker, set_broker, notify=broker_changed)

    def get_broker_version(self):
        return self.broker_version

    def set_broker_version(self, val: str):
        self.broker_version = val

    version_changed = Signal()

    version = Property(str, get_broker_version, set_broker_version, notify=version_changed)

    @Slot(int, QUrl)
    def start_run(self, run_number: int, spectrum_mapping_file_url: QUrl):
        print("start run called")
        # Send a detector spectrum map message to topic <INSTRUMENT>_detSpecMap
        detectors, spectra = self.load_spectrum_file(spectrum_mapping_file_url)
        kafka.send_detector_spectrum_map_message(detectors, spectra, self.instrument_name, self.broker_address)
        # Send a run start message to <INSTRUMENT>_runInfo
        kafka.send_start_run_message(run_number, self.instrument_name, self.broker_address)

    @staticmethod
    def load_spectrum_file(file_url: QUrl):
        """returns a list of detector numbers, and a list of spectrum numbers"""
        filename = file_url.toString(options=QUrl.PreferLocalFile)

        with open(filename, 'r') as file:
            lines = file.readlines()

        detectors = []
        spectra = []
        for line in lines[3:]:
            detector, spectrum = line.split()
            detectors.append(int(detector))
            spectra.append(int(spectrum))

        return detectors, spectra
