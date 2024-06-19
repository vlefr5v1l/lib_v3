from PyQt5 import QtCore, QtGui, QtWidgets
from kafs import kaf_dict, years
import res_rc

class Button(QtWidgets.QPushButton):
	dropSignal = QtCore.pyqtSignal(str)
	def __init__(self, parent):
		super().__init__(parent)
		self.setAcceptDrops(True)

	def dragEnterEvent(self, e):
		if e.mimeData().urls()[0].path()[-4:] == '.pdf':
			e.accept()
		else:
			e.ignore()

	def dropEvent(self, e):
		self.dropSignal.emit(e.mimeData().urls()[0].path()[1:])

class myStyle(QtWidgets.QCommonStyle):
	def __init__(self, angl=0, point=QtCore.QPoint(0, 0)):
		super(myStyle, self).__init__()
		self.angl = angl
		self.point = point

	def drawItemText(self, painter, rect, flags, pal, enabled, text, textRole):
		if not text:
			return
		savedPen = painter.pen()
		if textRole != QtGui.QPalette.NoRole:
			painter.setPen(QtGui.QPen(pal.brush(textRole), savedPen.widthF()))
		if not enabled:
			pen = painter.pen()
			painter.setPen(pen)
		painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
		painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing, True)
		painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)
		painter.translate(self.point)
		painter.rotate(self.angl)
		painter.drawText(rect, flags, text)
		painter.setPen(savedPen)


class Ui_MainWindow(object):
	def setupUi(self, MainWindow):
		MainWindow.setObjectName("MainWindow")
		MainWindow.resize(500, 700)
		MainWindow.setMinimumSize(QtCore.QSize(500, 700))
		MainWindow.setMaximumSize(QtCore.QSize(500, 700))
		self.centralwidget = QtWidgets.QWidget(MainWindow)
		self.centralwidget.setObjectName("centralwidget")

		self.current_app_section = None

		#COLORS
		self.btnBG = '#2B5278'		#button BG
		self.btnTxt = '#FFFFFF'		#button text
		self.BG = '#0E1621'			#BG
		self.lblBG = '#17212B'		#label BG
		self.lblTxt = '#83CAFF'		#label text
		self.lblBorder = '#2B5278'	#label border
		self.err = '#FF7785'		#error

		#FONTS
		self.fontButton = QtGui.QFont()
		self.fontButton.setFamily("MS Reference Sans Serif")
		self.fontButton.setPointSize(11)

		self.fontLabel = QtGui.QFont()
		self.fontLabel.setFamily("MS Reference Sans Serif")
		self.fontLabel.setPointSize(10)
		self.fontLabel.setBold(True)
		self.fontLabel.setWeight(75)

		self.fontBox = QtGui.QFont()
		self.fontBox.setFamily("MS Reference Sans Serif")
		self.fontBox.setPointSize(10)

		self.fontTinyLabel = QtGui.QFont()
		self.fontBox.setFamily("MS Reference Sans Serif")
		self.fontTinyLabel.setPointSize(11)
		self.fontTinyLabel.setBold(False)
		self.fontTinyLabel.setWeight(50)
		self.fontTinyLabel.setStyleStrategy(QtGui.QFont.PreferAntialias)

		self.fontPreview = QtGui.QFont()
		self.fontBox.setFamily("MS Reference Sans Serif")
		self.fontPreview.setPointSize(10)

		self.fontTiny = QtGui.QFont()
		self.fontTiny.setFamily("MS Reference Sans Serif")
		self.fontTiny.setPointSize(8)
		#####################/FONTS

		self.headerFrame = QtWidgets.QFrame(self.centralwidget)
		self.headerFrame.setObjectName("headerFrame")
		self.headerFrame.setGeometry(0, 0, 500, 160)
		self.headerFrame.setStyleSheet(f"background-color: {self.BG};")


		self.menuFrame = QtWidgets.QFrame(self.centralwidget)
		self.menuFrame.setObjectName("menuFrame")
		self.menuFrame.setGeometry(0, 0, 500, 42)
		self.menuFrame.setStyleSheet(f"background-color: {self.BG}; border-bottom: 2px solid {self.btnBG}")

		self.menuButtonExpand = QtWidgets.QPushButton(self.menuFrame)
		self.menuButtonExpand.setObjectName("menuButtonExpand")
		self.menuButtonExpand.setGeometry(500-40, 0, 40, 40)
		self.menuButtonExpand.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.menuButtonExpand.setStyleSheet(f"background: {self.BG}; background-image: url(ico/expand.png); border: none;")

		self.menuButtonUpload = QtWidgets.QPushButton(self.menuFrame)
		self.menuButtonUpload.setObjectName("menuButtonUpload")
		self.menuButtonUpload.setGeometry(0, 0, 500-40-40-40, 40)
		self.menuButtonUpload.setFont(self.fontButton)
		self.menuButtonUpload.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.menuButtonUpload.setStyleSheet(f"background: {self.btnBG}; color: {self.btnTxt}; border: none; border-top-right-radius: 5px;")
		self.menuButtonUpload.setText('Upload')
		self.menuButtonUpload.setEnabled(False)

		self.menuButtonImageUpload = QtWidgets.QPushButton(self.menuFrame)
		self.menuButtonImageUpload.setObjectName("menuButtonImageUpload")

		self.menuButtonDelete = QtWidgets.QPushButton(self.menuFrame)
		self.menuButtonDelete.setObjectName("menuButtonDelete")
		self.menuButtonDelete.setGeometry(40, 0, 500-40-40-40, 40)
		self.menuButtonDelete.setFont(self.fontButton)
		self.menuButtonDelete.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.menuButtonDelete.setStyleSheet(f"background: {self.btnBG}; color: {self.btnTxt}; border: none; border-top-left-radius: 5px; border-top-right-radius: 5px")
		self.menuButtonDelete.setText('Delete')
		self.menuButtonDelete.setEnabled(False)

		self.menuButtonImageDelete = QtWidgets.QPushButton(self.menuFrame)
		self.menuButtonImageDelete.setObjectName("menuButtonImageDelete")

		self.menuButtonEdit = QtWidgets.QPushButton(self.menuFrame)
		self.menuButtonEdit.setObjectName("menuButtonEdit")
		self.menuButtonEdit.setGeometry(80, 0, 500-40-40-40, 40)
		self.menuButtonEdit.setFont(self.fontButton)
		self.menuButtonEdit.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.menuButtonEdit.setStyleSheet(f"background: {self.btnBG}; color: {self.btnTxt}; border: none; border-top-left-radius: 5px; border-top-right-radius: 5px")
		self.menuButtonEdit.setText('Edit')
		self.menuButtonEdit.setEnabled(False)

		self.menuButtonImageEdit = QtWidgets.QPushButton(self.menuFrame)
		self.menuButtonImageEdit.setObjectName("menuButtonImageEdit")


		self.progressBarLabel = QtWidgets.QLabel(self.menuFrame)
		self.progressBarLabel.setObjectName('progressBarLabel')
		self.progressBarLabel.setGeometry(-500, 40, 500, 2)
		self.progressBarLabel.setStyleSheet(f'border-bottom: 2px solid {self.lblTxt}; background: transparent')

		self.sectionLabel = QtWidgets.QLabel(self.headerFrame)
		self.sectionLabel.setObjectName("sectionLabel")
		self.sectionLabel.setGeometry(20, 60, 150, 30)
		self.sectionLabel.setFont(self.fontLabel)
		self.sectionLabel.setStyleSheet(f'background: {self.lblBG}; border: 2px solid {self.lblBorder}; border-radius: 5px; color: {self.lblTxt}')
		self.sectionLabel.setAlignment(QtCore.Qt.AlignCenter)
		self.sectionLabel.setText('Section')

		self.kafLabel = QtWidgets.QLabel(self.headerFrame)
		self.kafLabel.setObjectName("kafLabel")
		self.kafLabel.setGeometry(20, 60+30+20, 150, 30)
		self.kafLabel.setFont(self.fontLabel)
		self.kafLabel.setStyleSheet(f'background: {self.lblBG}; border: 2px solid {self.lblBorder}; border-radius: 5px; color: {self.lblTxt}')
		self.kafLabel.setAlignment(QtCore.Qt.AlignCenter)
		self.kafLabel.setText('Kafedra')

		self.yearLabel = QtWidgets.QLabel(self.headerFrame)
		self.yearLabel.setObjectName("yearLabel")
		self.yearLabel.setGeometry(20, 60+30+20, 150, 30)
		self.yearLabel.setFont(self.fontLabel)
		self.yearLabel.setStyleSheet(f'background: {self.lblBG}; border: 2px solid {self.lblBorder}; border-radius: 5px; color: {self.lblTxt}')
		self.yearLabel.setAlignment(QtCore.Qt.AlignCenter)
		self.yearLabel.setText('Year')

		self.sectionBox = QtWidgets.QComboBox(self.headerFrame)
		self.sectionBox.setObjectName("sectionBox")
		self.sectionBox.setEnabled(True)
		self.sectionBox.setGeometry(20+150+20, 60, 500-190-20, 30)
		self.sectionBox.setFont(self.fontBox)
		self.sectionBox.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.sectionBox.setLayoutDirection(QtCore.Qt.LeftToRight)
		self.sectionBox.setStyleSheet("""
			QComboBox {
				outline: none;
			}
			QComboBox:!on {
				background: #2B5278;
				color: white;
				border: none;
				border-radius: 5px;
				padding: 7px;
			}
			QComboBox:on {
				background: #2B5278;
				color: white;
				border: none;
				border-top-left-radius: 5px;
				border-top-right-radius: 5px;
				padding: 7px;
			}
			QComboBox::drop-down {
				border: none;
				width: 25px;
			}
			QComboBox::down-arrow {
				image: url(:/images/arrow.png);
				width: 10px;
			}
		""")
		self.sectionBox.view().setStyleSheet('''
			QListView {
				outline: none;
				border: none;
				background: #2B5278;
				color: #FFFFFF;
				border-bottom-left-radius: 5px;
				border-bottom-right-radius: 5px;
			}
			''')
		self.sectionBox.view().verticalScrollBar().setStyleSheet("""
			QScrollBar:vertical {
				border: none;
				border-radius: 3px;
				background: #242A33;
				width: 6px;
				margin: -1px 0 -1px 0;
			}
			QScrollBar::handle:vertical {
				background: #4F555C;
				height: 12px;
				border-radius: 3px;
			}
			QScrollBar::add-line:vertical {
				height: 0px;
			}
			QScrollBar::sub-line:vertical {
				height: 0px;
			}
			QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
				height: 0px;
			}
			QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
				background: none;
			}
		""")
		self.sectionBox.setEditable(False)
		self.sectionBox.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToMinimumContentsLength)
		self.sectionBox.addItem('Публикации преподавателей')
		self.sectionBox.addItem('Методические пособия')

		self.kafBox = QtWidgets.QComboBox(self.headerFrame)
		self.kafBox.setObjectName("kafBox")
		self.kafBox.setEnabled(True)
		self.kafBox.setGeometry(20+150+20, 60+30+20, 500-190-20, 30)
		self.kafBox.setFont(self.fontBox)
		self.kafBox.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.kafBox.setLayoutDirection(QtCore.Qt.LeftToRight)
		self.kafBox.setStyleSheet("""
			QComboBox {
				outline: none;
			}
			QComboBox:!on {
				background: #2B5278;
				color: white;
				border: none;
				border-radius: 5px;
				padding: 7px;
			}
			QComboBox:on {
				background: #2B5278;
				color: white;
				border: none;
				border-top-left-radius: 5px;
				border-top-right-radius: 5px;
				padding: 7px;
			}
			QComboBox::drop-down {
				border: none;
				width: 25px;
			}
			QComboBox::down-arrow {
				image: url(:/images/arrow.png);
				width: 10px;
			}
		""")
		self.kafBox.view().setStyleSheet('''
			QListView {
				outline: none;
				border: none;
				background: #2B5278;
				color: #FFFFFF;
				border-bottom-left-radius: 5px;
				border-bottom-right-radius: 5px;
			}
			''')
		self.kafBox.view().verticalScrollBar().setStyleSheet("""
			QScrollBar:vertical {
				border: none;
				border-radius: 3px;
				background: #242A33;
				width: 6px;
				margin: -1px 0 -1px 0;
			}
			QScrollBar::handle:vertical {
				background: #4F555C;
				height: 12px;
				border-radius: 3px;
			}
			QScrollBar::add-line:vertical {
				height: 0px;
			}
			QScrollBar::sub-line:vertical {
				height: 0px;
			}
			QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
				height: 0px;
			}
			QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
				background: none;
			}
		""")
		self.kafBox.setEditable(False)
		self.kafBox.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToMinimumContentsLength)
		for item in kaf_dict:
			self.kafBox.addItem(item)

		self.yearBox = QtWidgets.QComboBox(self.headerFrame)
		self.yearBox.setObjectName("yearBox")
		self.yearBox.setEnabled(True)
		self.yearBox.setGeometry(20+150+20, 60+30+20, 500-190-20, 30)
		self.yearBox.setFont(self.fontBox)
		self.yearBox.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.yearBox.setLayoutDirection(QtCore.Qt.LeftToRight)
		self.yearBox.setStyleSheet("""
			QComboBox {
				outline: none;
			}
			QComboBox:!on {
				background: #2B5278;
				color: white;
				border: none;
				border-radius: 5px;
				padding: 7px;
			}
			QComboBox:on {
				background: #2B5278;
				color: white;
				border: none;
				border-top-left-radius: 5px;
				border-top-right-radius: 5px;
				padding: 7px;
			}
			QComboBox::drop-down {
				border: none;
				width: 25px;
			}
			QComboBox::down-arrow {
				image: url(:/images/arrow.png);
				width: 10px;
			}
		""")
		self.yearBox.view().setStyleSheet('''
			QListView {
				outline: none;
				border: none;
				background: #2B5278;
				color: #FFFFFF;
				border-bottom-left-radius: 5px;
				border-bottom-right-radius: 5px;
			}
			''')
		self.yearBox.view().verticalScrollBar().setStyleSheet("""
			QScrollBar:vertical {
				border: none;
				border-radius: 3px;
				background: #242A33;
				width: 6px;
				margin: -1px 0 -1px 0;
			}
			QScrollBar::handle:vertical {
				background: #4F555C;
				height: 12px;
				border-radius: 3px;
			}
			QScrollBar::add-line:vertical {
				height: 0px;
			}
			QScrollBar::sub-line:vertical {
				height: 0px;
			}
			QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
				height: 0px;
			}
			QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
				background: none;
			}
		""")
		self.yearBox.setEditable(False)
		self.yearBox.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToMinimumContentsLength)
		for item in years:
			self.yearBox.addItem(item)

		self.uploadFrame = QtWidgets.QFrame(self.centralwidget)
		self.uploadFrame.setObjectName("uploadFrame")
		self.uploadFrame.setGeometry(0, 160, 500, 700-160)
		self.uploadFrame.setStyleSheet(f"background-color: {self.BG};")

		self.fileLabel = QtWidgets.QLabel(self.uploadFrame)
		self.fileLabel.setObjectName("fileLabel")
		self.fileLabel.setGeometry(20, 0, 150, 30)
		self.fileLabel.setFont(self.fontLabel)
		self.fileLabel.setStyleSheet(f'background: {self.lblBG}; border: 2px solid {self.lblBorder}; border-radius: 5px; color: {self.lblTxt}')
		self.fileLabel.setAlignment(QtCore.Qt.AlignCenter)
		self.fileLabel.setText('PDF-file')

		self.fileButton = Button(self.uploadFrame)
		self.fileButton.setObjectName("fileButton")
		self.fileButton.setGeometry(20+150+20, 0, 150, 30)
		self.fileButton.setFont(self.fontButton)
		self.fileButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.fileButton.setStyleSheet(f'background: {self.btnBG}; color: {self.btnTxt}; border: none; border-radius: 5px')
		self.fileButton.setText('Open File')

		self.filenameLabel = QtWidgets.QLabel(self.uploadFrame)
		self.filenameLabel.setObjectName("filenameLabel")
		self.filenameLabel.setGeometry(20, 30+10, 500-20-20, 30)
		self.filenameLabel.setFont(self.fontTiny)
		self.filenameLabel.setStyleSheet(f'background: transparent; border: none; color: {self.lblTxt}; padding: 3px')
		self.filenameLabel.setAlignment(QtCore.Qt.AlignCenter)

		self.descrLabel = QtWidgets.QLabel(self.uploadFrame)
		self.descrLabel.setObjectName("descrLabel")
		self.descrLabel.setGeometry(20, 40+30+10, 150, 30)
		self.descrLabel.setFont(self.fontLabel)
		self.descrLabel.setStyleSheet(f'background: {self.lblBG}; border: 2px solid {self.lblBorder}; border-top-right-radius: 5px; border-top-left-radius: 5px; color: {self.lblTxt}')
		self.descrLabel.setAlignment(QtCore.Qt.AlignCenter)
		self.descrLabel.setText('Description')

		self.borderLabel = QtWidgets.QLabel(self.uploadFrame)
		self.borderLabel.setObjectName("borderLabel")
		self.borderLabel.setGeometry(20, 80+30-2, 500-40, 210)
		self.borderLabel.setStyleSheet(f'background: transparent; border: 2px solid {self.lblBorder}; border-top-right-radius: 5px; border-bottom-right-radius: 5px; border-bottom-left-radius: 5px;')

		self.text1Label = QtWidgets.QLabel(self.uploadFrame)
		self.text1Label.setObjectName("text1Label")
		self.text1Label.setGeometry(20+2, 110-1, 30, 70)
		self.text1Label.setFont(self.fontTinyLabel)
		self.text1Label.setStyleSheet(f'background: {self.lblBG}; border-top: 1px solid {self.lblBorder}; border-bottom: 1px solid {self.lblBorder}; color: {self.lblTxt}')
		self.text1Label.setAlignment(QtCore.Qt.AlignCenter)
		self.text1Label.setText('Text')
		self.text1Label.setStyle(myStyle(-90, QtCore.QPoint(-21, 50)))

		self.text1Edit = QtWidgets.QTextEdit(self.uploadFrame)
		self.text1Edit.setObjectName("text1Edit")
		self.text1Edit.setGeometry(20+2+30, 110-1, 500-40-4-30+1, 70)
		self.text1Edit.setTextColor(QtGui.QColor('white'))
		self.text1Edit.setStyleSheet(f'border: 1px solid {self.lblBorder}; border-top-right-radius: 5px;')
		self.text1Edit.setAcceptRichText(False)

		self.urlLabel = QtWidgets.QLabel(self.uploadFrame)
		self.urlLabel.setObjectName("urlLabel")
		self.urlLabel.setGeometry(20+2, 110-2+70, 30, 70)
		self.urlLabel.setFont(self.fontTinyLabel)
		self.urlLabel.setStyleSheet(f'background: {self.lblBG}; border-top: 1px solid {self.lblBorder}; border-bottom: 1px solid {self.lblBorder}; color: {self.lblTxt}')
		self.urlLabel.setAlignment(QtCore.Qt.AlignCenter)
		self.urlLabel.setText('URL')
		self.urlLabel.setStyle(myStyle(-90, QtCore.QPoint(-21, 50)))

		self.urlEdit = QtWidgets.QTextEdit(self.uploadFrame)
		self.urlEdit.setObjectName("urlEdit")
		self.urlEdit.setGeometry(20+2+30, 110-2+70, 500-40-4-30+1, 70)
		self.urlEdit.setTextColor(QtGui.QColor('white'))
		self.urlEdit.setStyleSheet(f'border: 1px solid {self.lblBorder};')
		self.urlEdit.setAcceptRichText(False)

		self.text2Label = QtWidgets.QLabel(self.uploadFrame)
		self.text2Label.setObjectName("text2Label")
		self.text2Label.setGeometry(20+2, 110-3+140, 30, 70)
		self.text2Label.setFont(self.fontTinyLabel)
		self.text2Label.setStyleSheet(f'background: {self.lblBG}; border-top: 1px solid {self.lblBorder}; border-bottom: 1px solid {self.lblBorder}; color: {self.lblTxt}; border-bottom-left-radius: 5px')
		self.text2Label.setAlignment(QtCore.Qt.AlignCenter)
		self.text2Label.setText('Text')
		self.text2Label.setStyle(myStyle(-90, QtCore.QPoint(-21, 50)))

		self.text2Edit = QtWidgets.QTextEdit(self.uploadFrame)
		self.text2Edit.setObjectName("text2Edit")
		self.text2Edit.setGeometry(20+2+30, 110-3+140, 500-40-4-30+1, 70)
		self.text2Edit.setTextColor(QtGui.QColor('white'))
		self.text2Edit.setStyleSheet(f'border: 1px solid {self.lblBorder}; border-bottom-right-radius: 5px')
		self.text2Edit.setAcceptRichText(False)

		self.text3Edit = QtWidgets.QTextEdit(self.uploadFrame)
		self.text3Edit.setObjectName("text3Edit")
		self.text3Edit.setGeometry(20, 80+30-2, 500-40, 210)
		self.text3Edit.setTextColor(QtGui.QColor('white'))
		self.text3Edit.setAcceptRichText(False)
		self.text3Edit.setStyleSheet(f'background: {self.BG}; border: 2px solid {self.lblBorder}; border-top-right-radius: 5px; border-bottom-right-radius: 5px; border-bottom-left-radius: 5px;')
		self.text3Edit.setVisible(False)

		self.previewLabel = QtWidgets.QLabel(self.uploadFrame)
		self.previewLabel.setObjectName("previewLabel")
		self.previewLabel.setGeometry(20, 118+212, 150, 30)
		self.previewLabel.setFont(self.fontLabel)
		self.previewLabel.setStyleSheet(f'background: {self.lblBG}; border: 2px solid {self.lblBorder}; border-top-right-radius: 5px; border-top-left-radius: 5px; color: {self.lblTxt};')
		self.previewLabel.setAlignment(QtCore.Qt.AlignCenter)
		self.previewLabel.setText('Preview')

		self.previewText = QtWidgets.QTextBrowser(self.uploadFrame)
		self.previewText.setObjectName("previewText")
		self.previewText.setGeometry(20, 330+30-2, 500-40, 490-20-(330+30-2))
		self.previewText.setFont(self.fontPreview)
		self.previewText.setStyleSheet(f'color: {self.btnTxt}; background: {self.BG}; border: 2px solid {self.lblBorder}; border-top-right-radius: 5px; border-bottom-right-radius: 5px; border-bottom-left-radius: 5px;')

		self.uploadButton = QtWidgets.QPushButton(self.uploadFrame)
		self.uploadButton.setObjectName("uploadButton")
		self.uploadButton.setGeometry(500-20-100, 490, 100, 30)
		self.uploadButton.setFont(self.fontButton)
		self.uploadButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.uploadButton.setStyleSheet(f'background: {self.btnBG}; color: {self.btnTxt}; border: none; border-radius: 5px')
		self.uploadButton.setText('Upload')

		self.resetButton = QtWidgets.QPushButton(self.uploadFrame)
		self.resetButton.setObjectName("resetButton")
		self.resetButton.setGeometry(380-100-20, 490, 100, 30)
		self.resetButton.setFont(self.fontButton)
		self.resetButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.resetButton.setStyleSheet(f'background: {self.btnBG}; color: {self.btnTxt}; border: none; border-radius: 5px')
		self.resetButton.setText('Reset')

		self.exitButton = QtWidgets.QPushButton(self.uploadFrame)
		self.exitButton.setObjectName("exitButton")
		self.exitButton.setGeometry(20, 490, 100, 30)
		self.exitButton.setFont(self.fontButton)
		self.exitButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.exitButton.setStyleSheet(f'background: {self.btnBG}; color: {self.btnTxt}; border: none; border-radius: 5px')
		self.exitButton.setText('Exit')

		#Mail
		self.mailFrame = QtWidgets.QFrame(self.centralwidget)
		self.mailFrame.setObjectName("mailFrame")
		self.mailFrame.setGeometry(500, 0, 1200, 700)
		self.mailFrame.setStyleSheet(f"background-color: {self.BG};")

		self.mailLabel = QtWidgets.QLabel(self.mailFrame)
		self.mailLabel.setObjectName("mailLabel")
		self.mailLabel.setGeometry(0, 0, 700, 40)
		self.mailLabel.setStyleSheet(f'border: none; background: transparent; color: {self.lblTxt};')
		self.mailLabel.setText('Mail Box')
		self.mailLabel.setAlignment(QtCore.Qt.AlignCenter)
		self.mailLabel.setFont(self.fontButton)
		self.mailLabel.setDisabled(True)

		self.menuButtonRefresh = QtWidgets.QPushButton(self.mailFrame)
		self.menuButtonRefresh.setObjectName("menuButtonRefresh")
		self.menuButtonRefresh.setGeometry(380, 0, 40, 40)
		self.menuButtonRefresh.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.menuButtonRefresh.setStyleSheet(f"background: transparent; background-image: url(ico/refresh.png); border: none;")

		self.menuButtonSqueeze = QtWidgets.QPushButton(self.mailFrame)
		self.menuButtonSqueeze.setObjectName("menuButtonSqueeze")
		self.menuButtonSqueeze.setGeometry(700-40, 0, 40, 40)
		self.menuButtonSqueeze.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.menuButtonSqueeze.setStyleSheet(f"background: {self.BG}; background-image: url(ico/squeeze.png); border: none;")

		self.lineLabel = QtWidgets.QLabel(self.mailFrame)
		self.lineLabel.setObjectName("lineLabel")
		self.lineLabel.setGeometry(0, 40, 700, 2)
		self.lineLabel.setStyleSheet(f'border-bottom: 2px solid {self.btnBG}; background: transparent')
		self.lineLabel.setDisabled(True)

		self.mailProgressBarLabel = QtWidgets.QLabel(self.mailFrame)
		self.mailProgressBarLabel.setObjectName('mailProgressBarLabel')
		self.mailProgressBarLabel.setGeometry(0, 40, 0, 2)
		self.mailProgressBarLabel.setStyleSheet(f'border-bottom: 2px solid {self.lblTxt}; background: transparent')

		self.emailList = QtWidgets.QListWidget(self.mailFrame)
		self.emailList.setObjectName('emailList')
		self.emailList.setGeometry(0, 40+20, 700-20, 700-60-20)
		self.emailList.setFont(self.fontPreview)
		self.emailList.setStyleSheet("""
		QListWidget{
			border: 2px solid #2B5278;
			border-radius: 5px;
			color: #8593A0;
			background: #0E1621;
			outline: none;
		}
		QListWidget::item:selected{
			color: #FFFFFF;
			background: #2B5278;
			border-radius: 5px;
			margin: 6px 5px 0 5px;
			padding: 5px;
			width: 90%;
		}
		QListWidget::item{
			color: #EEEEEE;
			background: #182533;
			border-radius: 5px;
			margin: 6px 5px 0 5px;
			padding: 5px;
			width: 90%;
		}
		QListWidget::indicator:unchecked {
			background: #6C7883;
			border: none;
			border-radius: 6px;
		}
		QListWidget::indicator:checked {
			background: #83CAFF;
			border: none;
			border-radius: 6px;
		}
		QListWidget::item:hover {
			background: #213F5B;
			color: #FFFFFF;
			border-radius: 5px;
			margin: 6px 5px 0 5px;
			padding: 5px;
			width: 90%;
		}
		""")
		self.emailList.verticalScrollBar().setStyleSheet("""
			QScrollBar:vertical {
				border: none;
				border-radius: 3px;
				background: #242A33;
				width: 6px;
				margin: 0px 0 0px 0;
			}
			QScrollBar::handle:vertical {
				background: #4F555C;
				height: 12px;
				border-radius: 3px;
			}
			QScrollBar::add-line:vertical {
				height: 0px;
			}
			QScrollBar::sub-line:vertical {
				height: 0px;
			}
			QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
				height: 0px;
			}
			QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
				background: none;
			}
		""")
		self.emailList.setTabKeyNavigation(True)
		self.emailList.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
		self.emailList.setWordWrap(True)
		self.emailList.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
		self.emailList.verticalScrollBar().setSingleStep(5)


		#DELETE SECTION
		self.deleteFrame = QtWidgets.QFrame(self.centralwidget)
		self.deleteFrame.setObjectName("deleteFrame")
		self.deleteFrame.setGeometry(0, 160, 500, 700-160)
		self.deleteFrame.setStyleSheet(f"background-color: {self.BG};")

		self.delListLabel = QtWidgets.QLabel(self.deleteFrame)
		self.delListLabel.setObjectName('delListLabel')
		self.delListLabel.setGeometry(20, 0, 150, 32)
		self.delListLabel.setFont(self.fontLabel)
		self.delListLabel.setStyleSheet(f'background: {self.lblBG}; border: 2px solid {self.lblBorder}; border-top-left-radius: 5px; color: {self.lblTxt};')
		self.delListLabel.setAlignment(QtCore.Qt.AlignCenter)
		self.delListLabel.setText('Item list')

		self.delListRefreshButton = QtWidgets.QPushButton(self.deleteFrame)
		self.delListRefreshButton.setObjectName('delListRefreshButton')
		self.delListRefreshButton.setGeometry(20+150-2, 0, 32, 32)
		self.delListRefreshButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.delListRefreshButton.setStyleSheet(f"padding: 0px; background: {self.lblBG}; background-image: url(ico/ref3.png); border: 2px solid {self.lblBorder}; border-top-right-radius: 5px; color: {self.lblTxt};")

		self.delSelectedLabel = QtWidgets.QLabel(self.deleteFrame)
		self.delSelectedLabel.setObjectName('delSelectedLabel')
		self.delSelectedLabel.setGeometry(20, 32+470-32-30, 100, 30)
		self.delSelectedLabel.setFont(self.fontLabel)
		self.delSelectedLabel.setStyleSheet(f'background: {self.lblBG}; border: 2px solid {self.lblBorder}; border-bottom-left-radius: 5px; border-bottom-right-radius: 5px; color: {self.lblTxt};')
		self.delSelectedLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
		self.delSelectedLabel.setText('Selected:')

		self.delSelected = QtWidgets.QLabel(self.deleteFrame)
		self.delSelected.setObjectName('delSelected')
		self.delSelected.setGeometry(120, 32+470-32-30, 500-20-120, 30)
		self.delSelected.setFont(self.fontLabel)
		self.delSelected.setStyleSheet(f'background: {self.BG}; border: none; color: {self.lblTxt};')
		self.delSelected.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
		self.delSelected.setText('')

		self.delList = QtWidgets.QListWidget(self.deleteFrame)
		self.delList.setObjectName('delList')
		self.delList.setGeometry(20, 32-2, 500-40, 470-32-30+4)
		self.delList.setFont(self.fontPreview)
		self.delList.setStyleSheet("""
		QListWidget{
			border: 2px solid #2B5278;
			border-top-right-radius: 5px;
			border-bottom-right-radius: 5px;
			color: #8593A0;
			background: #0E1621;
			outline: none;
		}
		QListWidget::item:selected{
			color: #FFFFFF;
			background: #2B5278;
			border-radius: 5px;
			margin: 6px 5px 0 5px;
			padding: 5px;
			width: 90%;
		}
		QListWidget::item{
			color: #EEEEEE;
			background: #182533;
			border-radius: 5px;
			margin: 6px 5px 0 5px;
			padding: 5px;
			width: 90%;
		}
		QListWidget::indicator:unchecked {
			background: #6C7883;
			border: none;
			border-radius: 6px;
		}
		QListWidget::indicator:checked {
			background: #83CAFF;
			border: none;
			border-radius: 6px;
		}
		QListWidget::item:hover {
			background: #213F5B;
			color: #FFFFFF;
			border-radius: 5px;
			margin: 6px 5px 0 5px;
			padding: 5px;
			width: 90%;
		}
		""")
		self.delList.verticalScrollBar().setStyleSheet("""
			QScrollBar:vertical {
				border: none;
				border-radius: 3px;
				background: #242A33;
				width: 6px;
				margin: 0px 0 0px 0;
			}
			QScrollBar::handle:vertical {
				background: #4F555C;
				height: 12px;
				border-radius: 3px;
			}
			QScrollBar::add-line:vertical {
				height: 0px;
			}
			QScrollBar::sub-line:vertical {
				height: 0px;
			}
			QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
				height: 0px;
			}
			QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
				background: none;
			}
		""")
		self.delList.setTabKeyNavigation(True)
		self.delList.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
		self.delList.setWordWrap(True)
		self.delList.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
		self.delList.verticalScrollBar().setSingleStep(5)

		self.delButton = QtWidgets.QPushButton(self.deleteFrame)
		self.delButton.setObjectName("delButton")
		self.delButton.setGeometry(500-20-100, 490, 100, 30)
		self.delButton.setFont(self.fontButton)
		self.delButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.delButton.setStyleSheet(f'background: {self.btnBG}; color: {self.btnTxt}; border: none; border-radius: 5px')
		self.delButton.setText('Delete')

		self.delResetButton = QtWidgets.QPushButton(self.deleteFrame)
		self.delResetButton.setObjectName("delResetButton")
		self.delResetButton.setGeometry(380-100-20, 490, 100, 30)
		self.delResetButton.setFont(self.fontButton)
		self.delResetButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.delResetButton.setStyleSheet(f'background: {self.btnBG}; color: {self.btnTxt}; border: none; border-radius: 5px')
		self.delResetButton.setText('Reset')

		self.delExitButton = QtWidgets.QPushButton(self.deleteFrame)
		self.delExitButton.setObjectName("delExitButton")
		self.delExitButton.setGeometry(20, 490, 100, 30)
		self.delExitButton.setFont(self.fontButton)
		self.delExitButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.delExitButton.setStyleSheet(f'background: {self.btnBG}; color: {self.btnTxt}; border: none; border-radius: 5px')
		self.delExitButton.setText('Exit')


		#EDIT SECTION
		self.editFrame = QtWidgets.QFrame(self.centralwidget)
		self.editFrame.setObjectName("editFrame")
		self.editFrame.setGeometry(0, 160, 500, 700-160)
		self.editFrame.setStyleSheet(f"background-color: {self.BG};")

		self.ed_ListLabel = QtWidgets.QLabel(self.editFrame)
		self.ed_ListLabel.setObjectName('ed_ListLabel')
		self.ed_ListLabel.setGeometry(20, 0, 150, 32)
		self.ed_ListLabel.setFont(self.fontLabel)
		self.ed_ListLabel.setStyleSheet(f'background: {self.lblBG}; border: 2px solid {self.lblBorder}; border-top-left-radius: 5px; color: {self.lblTxt};')
		self.ed_ListLabel.setAlignment(QtCore.Qt.AlignCenter)
		self.ed_ListLabel.setText('Item list')

		self.ed_ListRefreshButton = QtWidgets.QPushButton(self.editFrame)
		self.ed_ListRefreshButton.setObjectName('ed_ListRefreshButton')
		self.ed_ListRefreshButton.setGeometry(20+150-2, 0, 32, 32)
		self.ed_ListRefreshButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.ed_ListRefreshButton.setStyleSheet(f"padding: 0px; background: {self.lblBG}; background-image: url(ico/ref3.png); border: 2px solid {self.lblBorder}; border-top-right-radius: 5px; color: {self.lblTxt};")

		self.ed_List = QtWidgets.QListWidget(self.editFrame)
		self.ed_List.setObjectName('ed_List')
		self.ed_List.setGeometry(20, 32-2, 500-40, 210-20-30)
		self.ed_List.setFont(self.fontPreview)
		self.ed_List.setStyleSheet("""
		QListWidget{
			border: 2px solid #2B5278;
			border-top-right-radius: 5px;
			border-bottom-right-radius: 5px;
			border-bottom-left-radius: 5px;
			color: #8593A0;
			background: #0E1621;
			outline: none;
		}
		QListWidget::item:selected{
			color: #FFFFFF;
			background: #2B5278;
			border-radius: 5px;
			margin: 6px 5px 0 5px;
			padding: 5px;
			width: 90%;
		}
		QListWidget::item{
			color: #EEEEEE;
			background: #182533;
			border-radius: 5px;
			margin: 6px 5px 0 5px;
			padding: 5px;
			width: 90%;
		}
		QListWidget::indicator:unchecked {
			background: #6C7883;
			border: none;
			border-radius: 6px;
		}
		QListWidget::indicator:checked {
			background: #83CAFF;
			border: none;
			border-radius: 6px;
		}
		QListWidget::item:hover {
			background: #213F5B;
			color: #FFFFFF;
			border-radius: 5px;
			margin: 6px 5px 0 5px;
			padding: 5px;
			width: 90%;
		}
		""")
		self.ed_List.verticalScrollBar().setStyleSheet("""
			QScrollBar:vertical {
				border: none;
				border-radius: 3px;
				background: #242A33;
				width: 6px;
				margin: 0px 0 0px 0;
			}
			QScrollBar::handle:vertical {
				background: #4F555C;
				height: 12px;
				border-radius: 3px;
			}
			QScrollBar::add-line:vertical {
				height: 0px;
			}
			QScrollBar::sub-line:vertical {
				height: 0px;
			}
			QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
				height: 0px;
			}
			QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
				background: none;
			}
		""")
		self.ed_List.setTabKeyNavigation(True)
		self.ed_List.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
		self.ed_List.setWordWrap(True)
		self.ed_List.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
		self.ed_List.verticalScrollBar().setSingleStep(5)

		self.ed_borderLabel = QtWidgets.QLabel(self.editFrame)
		self.ed_borderLabel.setObjectName("ed_borderLabel")
		self.ed_borderLabel.setGeometry(20, 210, 500-40, 210)
		self.ed_borderLabel.setStyleSheet(f'background: transparent; border: 2px solid {self.lblBorder}; border-radius: 5px;')

		self.ed_text1Label = QtWidgets.QLabel(self.editFrame)
		self.ed_text1Label.setObjectName("ed_text1Label")
		self.ed_text1Label.setGeometry(20+2, 110-1+102, 30, 70)
		self.ed_text1Label.setFont(self.fontTinyLabel)
		self.ed_text1Label.setStyleSheet(f'background: {self.lblBG}; border-top: 1px solid {self.lblBorder}; border-bottom: 1px solid {self.lblBorder}; color: {self.lblTxt}; border-top-left-radius: 5px;')
		self.ed_text1Label.setAlignment(QtCore.Qt.AlignCenter)
		self.ed_text1Label.setText('Text')
		self.ed_text1Label.setStyle(myStyle(-90, QtCore.QPoint(-21, 50)))

		self.ed_text1Edit = QtWidgets.QTextEdit(self.editFrame)
		self.ed_text1Edit.setObjectName("ed_text1Edit")
		self.ed_text1Edit.setGeometry(20+2+30, 110-1+102, 500-40-4-30+1, 70)
		self.ed_text1Edit.setTextColor(QtGui.QColor('white'))
		self.ed_text1Edit.setStyleSheet(f'border: 1px solid {self.lblBorder}; border-top-right-radius: 5px;')
		self.ed_text1Edit.setAcceptRichText(False)

		self.ed_urlLabel = QtWidgets.QLabel(self.editFrame)
		self.ed_urlLabel.setObjectName("ed_urlLabel")
		self.ed_urlLabel.setGeometry(20+2, 110-2+70+102, 30, 70)
		self.ed_urlLabel.setFont(self.fontTinyLabel)
		self.ed_urlLabel.setStyleSheet(f'background: {self.lblBG}; border-top: 1px solid {self.lblBorder}; border-bottom: 1px solid {self.lblBorder}; color: {self.lblTxt}')
		self.ed_urlLabel.setAlignment(QtCore.Qt.AlignCenter)
		self.ed_urlLabel.setText('URL')
		self.ed_urlLabel.setStyle(myStyle(-90, QtCore.QPoint(-21, 50)))

		self.ed_urlEdit = QtWidgets.QTextEdit(self.editFrame)
		self.ed_urlEdit.setObjectName("ed_urlEdit")
		self.ed_urlEdit.setGeometry(20+2+30, 110-2+70+102, 500-40-4-30+1, 70)
		self.ed_urlEdit.setTextColor(QtGui.QColor('white'))
		self.ed_urlEdit.setStyleSheet(f'border: 1px solid {self.lblBorder};')
		self.ed_urlEdit.setAcceptRichText(False)

		self.ed_text2Label = QtWidgets.QLabel(self.editFrame)
		self.ed_text2Label.setObjectName("ed_text2Label")
		self.ed_text2Label.setGeometry(20+2, 110-3+140+102, 30, 70)
		self.ed_text2Label.setFont(self.fontTinyLabel)
		self.ed_text2Label.setStyleSheet(f'background: {self.lblBG}; border-top: 1px solid {self.lblBorder}; border-bottom: 1px solid {self.lblBorder}; color: {self.lblTxt}; border-bottom-left-radius: 5px')
		self.ed_text2Label.setAlignment(QtCore.Qt.AlignCenter)
		self.ed_text2Label.setText('Text')
		self.ed_text2Label.setStyle(myStyle(-90, QtCore.QPoint(-21, 50)))

		self.ed_text2Edit = QtWidgets.QTextEdit(self.editFrame)
		self.ed_text2Edit.setObjectName("ed_text2Edit")
		self.ed_text2Edit.setGeometry(20+2+30, 110-3+140+102, 500-40-4-30+1, 70)
		self.ed_text2Edit.setTextColor(QtGui.QColor('white'))
		self.ed_text2Edit.setStyleSheet(f'border: 1px solid {self.lblBorder}; border-bottom-right-radius: 5px')
		self.ed_text2Edit.setAcceptRichText(False)

		self.ed_text3Edit = QtWidgets.QTextEdit(self.editFrame)
		self.ed_text3Edit.setObjectName("ed_text3Edit")
		self.ed_text3Edit.setGeometry(20, 80+30-2+102, 500-40, 210)
		self.ed_text3Edit.setTextColor(QtGui.QColor('white'))
		self.ed_text3Edit.setAcceptRichText(False)
		self.ed_text3Edit.setStyleSheet(f'background: {self.BG}; border: 2px solid {self.lblBorder}; border-top-right-radius: 5px; border-bottom-right-radius: 5px; border-bottom-left-radius: 5px;')
		self.ed_text3Edit.setVisible(False)

		self.ed_fileButton = Button(self.editFrame)
		self.ed_fileButton.setObjectName("ed_fileButton")
		self.ed_fileButton.setGeometry(20, 490-20-30, 100, 30)
		self.ed_fileButton.setFont(self.fontButton)
		self.ed_fileButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.ed_fileButton.setStyleSheet(f'background: {self.btnBG}; color: {self.btnTxt}; border: none; border-radius: 5px')
		self.ed_fileButton.setText('Open File')

		self.ed_filenameLabel = QtWidgets.QLabel(self.editFrame)
		self.ed_filenameLabel.setObjectName("ed_filenameLabel")
		self.ed_filenameLabel.setGeometry(20+100+10, 490-20-30, 500-20-100-10-20, 30)
		self.ed_filenameLabel.setFont(self.fontTiny)
		self.ed_filenameLabel.setStyleSheet(f'background: transparent; border: none; color: {self.lblTxt}; padding: 3px')
		# self.ed_filenameLabel.setStyleSheet(f'background: transparent; border: 1px solid red; color: {self.lblTxt}; padding: 3px')
		self.ed_filenameLabel.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)

		self.editButton = QtWidgets.QPushButton(self.editFrame)
		self.editButton.setObjectName("editButton")
		self.editButton.setGeometry(500-20-100, 490, 100, 30)
		self.editButton.setFont(self.fontButton)
		self.editButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.editButton.setStyleSheet(f'background: {self.btnBG}; color: {self.btnTxt}; border: none; border-radius: 5px')
		self.editButton.setText('Submit')

		self.ed_resetButton = QtWidgets.QPushButton(self.editFrame)
		self.ed_resetButton.setObjectName("ed_resetButton")
		self.ed_resetButton.setGeometry(380-100-20, 490, 100, 30)
		self.ed_resetButton.setFont(self.fontButton)
		self.ed_resetButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.ed_resetButton.setStyleSheet(f'background: {self.btnBG}; color: {self.btnTxt}; border: none; border-radius: 5px')
		self.ed_resetButton.setText('Reset')

		self.ed_exitButton = QtWidgets.QPushButton(self.editFrame)
		self.ed_exitButton.setObjectName("ed_exitButton")
		self.ed_exitButton.setGeometry(20, 490, 100, 30)
		self.ed_exitButton.setFont(self.fontButton)
		self.ed_exitButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.ed_exitButton.setStyleSheet(f'background: {self.btnBG}; color: {self.btnTxt}; border: none; border-radius: 5px')
		self.ed_exitButton.setText('Exit')

		MainWindow.setCentralWidget(self.centralwidget)
		# self.retranslateUi(MainWindow)
		QtCore.QMetaObject.connectSlotsByName(MainWindow)

	def upload_section(self):
		self.current_app_section = 'upload'

		self.menuButtonUpload.setVisible(True)

		self.menuButtonImageUpload.setGeometry(125, 0, 40, 40)
		self.menuButtonImageUpload.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.menuButtonImageUpload.setStyleSheet(f"background-color: {self.btnBG}; background-image: url(ico/upload_inactive.png); border: none;")
		self.menuButtonImageUpload.setEnabled(False)

		self.menuButtonDelete.setVisible(False)

		self.menuButtonImageDelete.setGeometry(500-40-40-40, 0, 40, 40)
		self.menuButtonImageDelete.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.menuButtonImageDelete.setStyleSheet(f"background: {self.BG}; background-image: url(ico/delete.png); border: none;")
		self.menuButtonImageDelete.setEnabled(True)

		self.menuButtonEdit.setVisible(False)

		self.menuButtonImageEdit.setGeometry(500-40-40, 0, 40, 40)
		self.menuButtonImageEdit.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.menuButtonImageEdit.setStyleSheet(f"background: {self.BG}; background-image: url(ico/edit.png); border: none;")
		self.menuButtonImageEdit.setEnabled(True)

		#Frames
		self.uploadFrame.setVisible(True)
		self.deleteFrame.setVisible(False)
		self.editFrame.setVisible(False)

	def delete_section(self):
		self.current_app_section = 'delete'

		self.menuButtonUpload.setVisible(False)

		self.menuButtonImageUpload.setGeometry(0, 0, 40, 40)
		self.menuButtonImageUpload.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.menuButtonImageUpload.setStyleSheet(f"background-color: transparent; background-image: url(ico/upload.png); border: none;")
		self.menuButtonImageUpload.setEnabled(True)

		self.menuButtonDelete.setVisible(True)

		self.menuButtonImageDelete.setGeometry(165, 0, 40, 40)
		self.menuButtonImageDelete.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.menuButtonImageDelete.setStyleSheet(f"background: {self.btnBG}; background-image: url(ico/delete_inactive.png); border: none;")
		self.menuButtonImageDelete.setEnabled(False)

		self.menuButtonEdit.setVisible(False)

		self.menuButtonImageEdit.setGeometry(500-40-40, 0, 40, 40)
		self.menuButtonImageEdit.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.menuButtonImageEdit.setStyleSheet(f"background: {self.BG}; background-image: url(ico/edit.png); border: none;")
		self.menuButtonImageEdit.setEnabled(True)

		#Frames
		self.uploadFrame.setVisible(False)
		self.deleteFrame.setVisible(True)
		self.editFrame.setVisible(False)

	def edit_section(self):
		self.current_app_section = 'edit'

		self.menuButtonUpload.setVisible(False)

		self.menuButtonImageUpload.setGeometry(0, 0, 40, 40)
		self.menuButtonImageUpload.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.menuButtonImageUpload.setStyleSheet(f"background-color: transparent; background-image: url(ico/upload.png); border: none;")
		self.menuButtonImageUpload.setEnabled(True)

		self.menuButtonDelete.setVisible(False)

		self.menuButtonImageDelete.setGeometry(40, 0, 40, 40)
		self.menuButtonImageDelete.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.menuButtonImageDelete.setStyleSheet(f"background: {self.BG}; background-image: url(ico/delete.png); border: none;")
		self.menuButtonImageDelete.setEnabled(True)

		self.menuButtonEdit.setVisible(True)

		self.menuButtonImageEdit.setGeometry(205, 0, 40, 40)
		self.menuButtonImageEdit.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		self.menuButtonImageEdit.setStyleSheet(f"background: {self.btnBG}; background-image: url(ico/edit_inactive.png); border: none;")
		self.menuButtonImageEdit.setEnabled(False)

		#Frames
		self.uploadFrame.setVisible(False)
		self.deleteFrame.setVisible(False)
		self.editFrame.setVisible(True)

