import sys

from qt_gui.plugin import Plugin
from python_qt_binding import loadUi
from python_qt_binding.QtGui import QWidget
from python_qt_binding.QtGui import QVBoxLayout
from python_qt_binding.QtGui import QHBoxLayout
from python_qt_binding.QtGui import QPushButton
from python_qt_binding.QtGui import QCheckBox
from python_qt_binding.QtGui import QIcon

import rospy
import rosprofiler_adapter
from diarc import *
from diarc import topology
from diarc import qt_view

from blacklist import BlacklistDialog

TOPIC_BLACKLIST = ['/clock', '/topology', '/statistics']
NODE_BLACKLIST = ['/rosout']

class VisualizerPlugin(Plugin):
    def __init__(self, context):
        super(VisualizerPlugin, self).__init__(context)
        self.setObjectName('VisualizerPlugin')
        
        # Process standalone plugin command-line arguments
        from argparse import ArgumentParser
        parser = ArgumentParser()
        # Add argument(s) to the parser.
        parser.add_argument("-q", "--quiet", action="store_true",
                        dest="quiet", help="Put plugin in silent mode")
        args, unknowns = parser.parse_known_args(context.argv())

        context.add_widget(VisualizerWidget())

    def shutdown_plugin(self):
        pass

    def save_settings(self, plugin_settings, instance_settings):
        pass

    def restore_settings(self, plugin_settings, instance_settings):
        pass

class VisualizerWidget(QWidget):
    def __init__(self, parent=None):
        super(VisualizerWidget, self).__init__(parent)
        self.setWindowTitle('Graph Profiler Visualizer')
        vbox = QVBoxLayout()
        self.setLayout(vbox)

        toolbar_layout = QHBoxLayout()
        refresh_button = QPushButton()
        refresh_button.setIcon(QIcon.fromTheme('view-refresh'))
        auto_refresh_checkbox = QCheckBox("Auto Refresh")
        topic_blacklist_button = QPushButton("Topic Blacklist")
        node_blacklist_button = QPushButton("Node Blacklist")

        refresh_button.clicked.connect(self._refresh)
        topic_blacklist_button.clicked.connect(self._edit_topic_blacklist)
        node_blacklist_button.clicked.connect(self._edit_node_blacklist)
        auto_refresh_checkbox.setCheckState(2)
        auto_refresh_checkbox.stateChanged.connect(self._autorefresh_changed)

        toolbar_layout.addWidget(refresh_button)
        toolbar_layout.addWidget(auto_refresh_checkbox)
        toolbar_layout.addStretch(0)
        toolbar_layout.addWidget(topic_blacklist_button)
        toolbar_layout.addWidget(node_blacklist_button)
        vbox.addLayout(toolbar_layout)

        # Initialize the Visualizer
        self._view = qt_view.QtView()
        self._adapter = rosprofiler_adapter.ROSProfileAdapter(self._view)
        self._adapter.set_topic_quiet_list(TOPIC_BLACKLIST)
        self._adapter.set_node_quiet_list(NODE_BLACKLIST)
        vbox.addWidget(self._view)

    def _edit_topic_blacklist(self):
        """ Opens topic blacklist Dialog and modifies the blacklist """
        topics = self._adapter.get_topic_quiet_list()
        topic_blacklist = BlacklistDialog.get_blacklist(values=topics)
        self._adapter.set_topic_quiet_list(topic_blacklist)
        self._adapter.topology_update()
        
    def _edit_node_blacklist(self):
        """ Opens node blacklist Dialog and modifies the blacklist """
        nodes = self._adapter.get_node_quiet_list()
        node_blacklist = BlacklistDialog.get_blacklist(values=nodes)
        self._adapter.set_node_quiet_list(node_blacklist)
        self._adapter.topology_update()

    def _autorefresh_changed(self, value):
        if value == 2:
            print "Enabling Autorefresh"
            self._adapter.enable_auto_update()
            self._refresh()
        elif value == 0:
            print "Disabling Autorefresh"
            self._adapter.disable_auto_update()
        else:
            raise Exception()

    def _refresh(self):
        self._adapter.topology_update()
