

all: resources.py ui_qgswps.py ui_qgswpsdescribeprocess.py ui_qgsnewhttpconnectionbase.py


clean:
	rm -f ui_qgswps.py ui_qgswpsdescribeprocess.py resources.py ui_newhttpconnectionbase.py
	rm -f *.pyc


ui_qgswps.py: qgswpsgui.ui
	pyuic4 -o ui_qgswps.py qgswpsgui.ui

ui_qgswpsdescribeprocess.py: qgswpsdescribeprocessgui.ui
	pyuic4 -o ui_qgswpsdescribeprocess.py qgswpsdescribeprocessgui.ui

ui_qgsnewhttpconnectionbase.py: qgsnewhttpconnectionbase.ui
	pyuic4 -o ui_qgsnewhttpconnectionbase.py qgsnewhttpconnectionbase.ui

resources.py: resources.qrc
	pyrcc4 -o resources.py resources.qrc

