import sys
from os import path
from PySide2.QtCore import QUrl, QObject
from PySide2.QtQml import QQmlApplicationEngine, qmlRegisterType
from test_run_controls.kafka_connector import KafkaConnector


qmlRegisterType(KafkaConnector, 'Kafka', 1, 0, 'KafkaConnector')


class Application(QQmlApplicationEngine):
    """
    Main UI class for the test run controls, responsible for loading the QML GUI.
    """

    def __init__(self, resource_folder):
        super().__init__()

        # Stop the application if Qt is unable to load the UI from qml
        # By default errors should be logged http://doc.qt.io/qt-5/qqmlapplicationengine.html#load
        # but these will not stop the application from running without a UI, and don't appear in the PyCharm console
        def load_listener(loaded_object: QObject, target_url: QUrl):
            if loaded_object is None:
                print("Unable to load from url: {0}\nExiting".format(target_url.toString()), file=sys.stderr)
                sys.exit(-1)

        url = QUrl.fromLocalFile(path.join(resource_folder, 'Main.qml'))
        self.objectCreated.connect(load_listener)
        self.load(url)
