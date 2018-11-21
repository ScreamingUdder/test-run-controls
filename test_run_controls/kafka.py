from configparser import ConfigParser
import time
import flatbuffers
import det_spec_map.SpectraDetectorMapping
import run_info.InfoTypes
import run_info.RunInfo
import run_info.RunStart

import pykafka


config = ConfigParser()
config.read('./config.ini')
default_instrument_name = config['DefaultConnection']['Instrument']
default_broker_address = config['DefaultConnection']['Broker']
default_broker_version = config['DefaultConnection']['BrokerVersion']


def prepare_flatbuffer_message(builder: flatbuffers.Builder, file_identifier: bytes):
    """Builds a bytes object from the provided flatbuffers builder, containing the given file_identifier"""
    assert len(file_identifier) == 4
    buffer = builder.Output()
    # manually insert the file identifier. Once the next flatbuffers >1.10 comes out there should be an official
    # way to do this https://github.com/google/flatbuffers/pull/4892
    buffer[4:8] = file_identifier
    return bytes(buffer)


def send_message(message: bytes,
                 topic_name: bytes,
                 broker_address: str=default_broker_address,
                 broker_version: str=default_broker_version):
    """Send a message to a given topic on the given broker"""
    client = pykafka.KafkaClient(hosts=broker_address, broker_version=broker_version)
    topic = client.topics[topic_name]
    producer = topic.get_producer()
    producer.produce(message)


def send_detector_spectrum_map_message(detectors: list,
                                       spectra: list,
                                       instrument_name: str,
                                       broker_address: str=default_broker_address,
                                       broker_version: str=default_broker_version):
    """Send a detector spectrum map message to topic <instrument_name>_detSpecMap on the given broker"""
    builder = flatbuffers.Builder(0)

    det_spec_map.SpectraDetectorMapping.SpectraDetectorMappingStartDetectorIdVector(builder, len(detectors))
    for detector in reversed(detectors):
        builder.PrependInt32(detector)
    detector_vector = builder.EndVector(len(detectors))

    det_spec_map.SpectraDetectorMapping.SpectraDetectorMappingStartSpectrumVector(builder, len(spectra))
    for spectrum in reversed(spectra):
        builder.PrependInt32(spectrum)
    spectra_vector = builder.EndVector(len(spectra))

    det_spec_map.SpectraDetectorMapping.SpectraDetectorMappingStart(builder)
    det_spec_map.SpectraDetectorMapping.SpectraDetectorMappingAddDetectorId(builder, detector_vector)
    det_spec_map.SpectraDetectorMapping.SpectraDetectorMappingAddSpectrum(builder, spectra_vector)
    det_spec_map.SpectraDetectorMapping.SpectraDetectorMappingAddNSpectra(builder, len(spectra))
    mapping = det_spec_map.SpectraDetectorMapping.SpectraDetectorMappingEnd(builder)

    builder.Finish(mapping)

    message = prepare_flatbuffer_message(builder, b'df12')
    topic_name = "{}_detSpecMap".format(instrument_name).encode()
    send_message(message, topic_name, broker_address, broker_version)


def send_start_run_message(run_number: int,
                           instrument_name: str,
                           broker_address: str=default_broker_address,
                           broker_version: str=default_broker_version):
    """Send a run start message to topic <instrument_name>_runInfo on the given broker"""
    builder = flatbuffers.Builder(0)

    name = builder.CreateString(instrument_name)
    run_info.RunStart.RunStartStart(builder)
    # time.time_ns() isn't available in python < 3.7, and this targets 3.5
    current_time_ns = int(time.time() * (10 ** 9))
    run_info.RunStart.RunStartAddStartTime(builder, current_time_ns)
    run_info.RunStart.RunStartAddRunNumber(builder, run_number)
    run_info.RunStart.RunStartAddInstrumentName(builder, name)
    run_start = run_info.RunStart.RunStartEnd(builder)

    run_info.RunInfo.RunInfoStart(builder)
    run_info.RunInfo.RunInfoAddInfoTypeType(builder, run_info.InfoTypes.InfoTypes().RunStart)
    run_info.RunInfo.RunInfoAddInfoType(builder, run_start)
    info = run_info.RunInfo.RunInfoEnd(builder)

    builder.Finish(info)

    message = prepare_flatbuffer_message(builder, b'ba57')
    topic_name = "{}_runInfo".format(instrument_name).encode()
    send_message(message, topic_name, broker_address, broker_version)
