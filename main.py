import sys, os, subprocess, ctypes
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtMultimedia import QSound
from PyQt5.QtCore import Qt, QRect, QLine, QSize, QTimer, QThread, pyqtSignal, pyqtSlot, QObject
from PyQt5.QtGui import QIcon, QCursor, QPalette, QColor
import new_design
from kafs import kaf_dict, kaf_dict_search, years
import time
import ftplib
from bs4 import BeautifulSoup
import inspect
from functools import partial
import imaplib, unicodedata, re
import email, base64
from dat import USER, PASSWORD
try:
    from xml.etree.cElementTree import XML
except ImportError:
    from xml.etree.ElementTree import XML
import zipfile

import sqlite3 as sq3


def ftp_connection():
    print('[INFO] ftp_connection: Connecting to FTP')
    try:
        ftp = ftplib.FTP("nizrp.narod.ru")
        ret = ftp.login(USER, PASSWORD)
    except ftplib.all_errors as e:
        print('[ERROR] ftp_connection: Unable to connect and login', '[ERROR] ftp_connection: {}'.format(e), sep='\n')
        return False
    print('[INFO] ftp_connection: Connection established', sep='\n')
    print('[INFO] ftp_connection: {}'.format(ret.replace('\n', ' \\\\ ')), sep='\n')
    ftp.encoding = 'utf-8'
    return ftp


def ftp_download(ftp, directory, filename, savepath):
    try:
        ftp.cwd(directory)
        print('[INFO] ftp_download: current dir:', ftp.pwd())
        ftp.retrbinary("RETR " + filename, open(savepath + filename, 'wb').write)
        print('[INFO] ftp_download: Downloaded', filename)
        return True
    except ftplib.all_errors as e:
        print("[ERROR] ftp_download: Can't download", filename, '\n[ERROR] ftp_download:', e)
        return False


def ftp_upload(ftp, directory, file, output_file_name):
    def create_missing_dirs(ftp, cdir):
        if cdir:
            try:
                ftp.cwd(cdir)
                print('[INFO] ftp_upload: current dir:', ftp.pwd())
            except:
                create_missing_dirs(ftp, '/'.join(cdir.split('/')[:-1]))
                ftp.mkd(cdir)
                print(f'\n[INFO] ftp_upload: created {cdir}')
                ftp.cwd(cdir)
                print('[INFO] ftp_upload: current dir:', ftp.pwd())

    try:
        # ftp.cwd(directory)
        create_missing_dirs(ftp, directory)

        ftp.storbinary("STOR " + output_file_name, open(file, "rb"), 1024)
        print('[INFO] ftp_upload: Uploaded {} {}'.format(directory, file))
        return True
    except Exception as e:
        print('[ERROR] ftp_upload: Failed to upload {} {}\n[ERROR] ftp_upload: {}'.format(directory, file, e))
        return False


class uploadThread(QThread):
    # signals
    progress_signal = pyqtSignal(int)
    upload_err_signal = pyqtSignal(str)
    # data
    upload_data = []

    def __init__(self, parent=None):
        QThread.__init__(self, parent)

    def run(self):
        self.progress_signal.emit(1)
        ftp = ftp_connection()
        if not ftp:
            self.upload_err_signal.emit('[FTP] connection error')
            print('[ERROR] upload_thread: FTP connection error')
            return
        self.progress_signal.emit(2)
        with ftp as ftp:
            if not ftp_download(ftp, '/', self.upload_data[0], 'html\\'):
                self.upload_err_signal.emit('[FTP] file download error')
                print('[ERROR] upload_thread: Download file error')
                return
            self.progress_signal.emit(3)
            try:
                print('[INFO] upload_thread: copying file')
                CREATE_NO_WINDOW = 0x08000000
                subprocess.call('copy /Y html\\{} html_backup\\{}.{}'.format(self.upload_data[0], self.upload_data[0],
                                                                             str(time.time()).split('.')[0]),
                                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                                creationflags=CREATE_NO_WINDOW)
            except Exception as e:
                self.upload_err_signal.emit('file copy error\n{}'.format(str(e).replace('\n', ' \\\\ ')))
                print('[ERROR] upload_thread: Copy file error',
                      '[ERROR] upload_thread: {}'.format(str(e).replace('\n', ' \\\\ ')))
                return
            self.progress_signal.emit(4)
            print('[INFO] upload_thread: opening webpage', self.upload_data[0])
            with open('html\\' + self.upload_data[0], 'r', encoding='utf-8') as webpage_file:
                contents = webpage_file.read()
                soup = BeautifulSoup(contents, 'html.parser')
                if 'publprepod' in self.upload_data[0]:
                    li = soup.new_tag('li')
                    a = soup.new_tag('a')
                    a['href'] = self.upload_data[1] + self.upload_data[2]
                    a['target'] = '_blank'
                    strong = soup.new_tag('strong')
                    li.string = self.upload_data[7] if self.upload_data[7] != '' else ''
                    strong.string = self.upload_data[6]
                    a.append(strong)
                    li.string.insert_before(a)
                    li.a.insert_before(self.upload_data[5] + ' ')
                    datayear = soup.find_all(attrs={"data-year": self.upload_data[4]})[0]
                    datayear.li.insert_before(li)
                    datayear.li.insert_after('\n')
                    self.progress_signal.emit(5)
                else:
                    li = soup.new_tag('li')
                    a = soup.new_tag('a')
                    a['href'] = self.upload_data[1] + self.upload_data[2]
                    a['target'] = '_blank'
                    br = soup.new_tag('br')
                    br2 = soup.new_tag('br')
                    a.append(' http://nizrp.narod.ru{}{}'.format(self.upload_data[1], self.upload_data[2]))
                    li.insert(0, br2)
                    li.br.insert_before(self.upload_data[4])
                    li.br.insert_after('Режим доступа:')
                    li.append(a)
                    soup.ol.li.insert_before(li)
                    soup.ol.li.insert_after('\n')
                    soup.ol.li.insert_after(br)
                    soup.ol.li.insert_after('\n')
                    self.progress_signal.emit(5)
            print('[INFO] upload_thread: writing down webpage', self.upload_data[0])
            with open('html\\' + self.upload_data[0], 'wb') as webpage_file:
                webpage_file.write(soup.encode('utf-8'))
            self.progress_signal.emit(6)
            print('[INFO] upload_thread: uploading file', self.upload_data[3], self.upload_data[2])
            if not ftp_upload(ftp, self.upload_data[1], self.upload_data[3], self.upload_data[2]):
                self.upload_err_signal.emit('[FTP] File upload error (1)')
                print('[ERROR] upload_thread: Upload file error')
                return
            # self.sleep(1)######################################################################
            self.progress_signal.emit(7)
            print('[INFO] upload_thread: uploading file', self.upload_data[0])
            if not ftp_upload(ftp, '/', 'html\\' + self.upload_data[0], self.upload_data[0]):
                self.upload_err_signal.emit('[FTP] File upload error (2)')
                print('[ERROR] upload_thread: File upload error')
                return
            # self.sleep(1)######################################################################
            self.progress_signal.emit(8)
            if 'publprepod' not in self.upload_data[0]:
                if not self.increase_ebmu(ftp):
                    self.upload_err_signal.emit('increase_ebmu returned False')
                    print('[ERROR] upload_thread: increase_ebmu returned False')
                    return
                self.progress_signal.emit(9)
                print('[INFO] upload_thread: uploading file', 'ebmu_m.htm')
                if not ftp_upload(ftp, '/', 'html\\' + 'ebmu_m.htm', 'ebmu_m.htm'):
                    self.upload_err_signal.emit('[FTP] File upload error (3)')
                    print('[ERROR] upload_thread: File upload error')
                    return
        # self.sleep(1)######################################################################
        self.progress_signal.emit(10)


    def increase_ebmu(self, ftp):
        webpage = 'ebmu_m.htm'
        if not ftp_download(ftp, '/', 'ebmu_m.htm', 'html\\'):
            print('[ERROR] increase_ebmu: Download file error')
            return False
        try:
            print('[INFO] increase_ebmu: copying file')
            CREATE_NO_WINDOW = 0x08000000
            subprocess.call(
                'copy /Y html\\{} html_backup\\{}.{}'.format(webpage, webpage, str(time.time()).split('.')[0]),
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                creationflags=CREATE_NO_WINDOW)
        except Exception as e:
            print('[ERROR] increase_ebmu: Copy file error', '[ERROR] upload: {}'.format(str(e).replace('\n', ' \\\\ ')))
            return False
        print('[INFO] increase_ebmu: opening webpage', webpage)
        with open('html\\' + webpage, 'r', encoding='utf-8') as webpage_file:
            contents = webpage_file.read()
            soup = BeautifulSoup(contents, 'html.parser')
            span = soup.find('span', attrs={"class": "manualsCounter"})
            span.string = str(int(span.string) + 1)
        print('[INFO] upload: writing down webpage', webpage)
        with open('html\\' + webpage, 'wb') as webpage_file:
            webpage_file.write(soup.encode('utf-8'))
        return True


# class mailThread(QThread):
# 	#signals
# 	mail_progress_signal = pyqtSignal(tuple)
# 	email_processed = pyqtSignal(dict)
# 	mail_err_signal = pyqtSignal(str)
# 	mail_interruption = pyqtSignal()
# 	#data
# 	emails = []
# 	interruption_flag = False

# 	def __init__(self, parent=None):
# 		QThread.__init__(self, parent)

# 	def run(self):
# 		try:
# 			connection = imaplib.IMAP4_SSL('imap.gmail.com')
# 			connection.login(<тут твоё мыло>, <тут пароль из настроек почтового ящика (в гугле можно дать доступ приложению (скрипту) к почтовому ящику>)
# 			status, msgs = connection.select("INBOX")
# 			typ, data = connection.search(None, '(FROM "nicrp@yandex.ru")')
# 			id_list = data[0].split()
# 		except:
# 			self.mail_err_signal.emit('[IMAP] connection error')
# 			print('[ERROR] mail_thread: IMAP connection error')
# 			return
# 		email_number = 70
# 		self.mail_progress_signal.emit((email_number+1, 1))
# 		for i, num in enumerate(id_list[-1:(email_number*-1)-1:-1]):
# 			if self.interruption_flag:
# 				self.interruption_flag = False
# 				self.mail_interruption.emit()
# 				print('[WARNING] mail_thread: interruption requested')
# 				return
# 			try:
# 				# if i == 3:
# 				# 	print('Exception')
# 				# 	raise Exception('lolkek')
# 				self.emails.append({'number':num.decode(), 'type':None, 'email type':None, 'subject':None, 'body':None, 'attachments':[]})
# 				typ, message_data = connection.fetch(num, '(RFC822)')
# 				raw_email = message_data[0][1]
# 				# raw_email_string = raw_email.decode('utf-8')
# 				# print(raw_email_string)
# 				email_message = email.message_from_bytes(raw_email)
# 				parser = email.parser.HeaderParser()
# 				header_dict = parser.parsestr(email_message.as_string())
# 				try:
# 					header = str(email.header.make_header(email.header.decode_header(header_dict['Subject'])))
# 				except:
# 					header = 'No header'	
# 				self.emails[i]['subject'] = header
# 			except Exception as e:
# 				self.mail_err_signal.emit('email processing error 1:\n{}'.format(repr(e)))
# 				print('[ERROR] mail_thread: email processing error 1:\n{}'.format(repr(e)))
# 				return
# 			#Определяем тип письма------------------------------------
# 			try:
# 				if 'публикации препод' in header.lower() and 'nobot' not in header.lower():
# 					self.emails[i]['type'] = 'Публикации преподавателей'
# 				elif any(trig in header.lower() for trig in ['пособие', 'пособия', 'методичка', 'методические']):
# 					self.emails[i]['type'] = 'Методические пособия'
# 				else:
# 					self.emails[i]['type'] = 'Другое'
# 			except Exception as e:
# 				self.mail_err_signal.emit('can\'t define email type:\n{}'.format(repr(e)))
# 				print('[ERROR] mail_thread: can\'t define email type:\n{}'.format(repr(e)))
# 				return
# 			#---------------------------------------------------------
# 			#Определяем, составное ли письмо и читаем, что это за части
# 			text = []
# 			try:
# 				if email_message.is_multipart():
# 				#Гуляем по письму, если составное
# 					self.emails[i]['email type'] = 'multipart'
# 					for j, part in enumerate(email_message.walk()):
# 						content_type = part.get_content_type()
# 						#Если это файл, то читаем и сохраняем
# 						try:
# 							if part.get_filename():
# 								filename = str(email.header.make_header(email.header.decode_header(part.get_filename())))
# 								if filename[-5:] == '.docx':
# 									if self.emails[i]['type'] == 'Публикации преподавателей':
# 										with open('mail_files/' + str(i) + '.docx', 'wb') as new_docx:
# 											new_docx.write(part.get_payload(decode=True))
# 										text_from_docx = self.split_text(self.get_text_docx('mail_files/' + str(i) + '.docx'))
# 										os.remove('mail_files/' + str(i) + '.docx')
# 										self.emails[i]['docx_text'] = text_from_docx
# 									self.emails[i]['attachments'].append(filename)
# 								elif filename[-4:] == '.pdf':
# 									with open('mail_files/' + filename, 'wb') as pdf:
# 										pdf.write(part.get_payload(decode=True))
# 									self.emails[i]['attachments'].append(filename)
# 								else:
# 									self.emails[i]['attachments'].append(filename)
# 						#Если это хтмл
# 							elif content_type == 'text/html':
# 								charset = part.get_content_charset()
# 								html = part.get_payload(decode=True).decode(charset)

# 								raw_text = BeautifulSoup(html, 'html.parser').text
# 								text = unicodedata.normalize("NFKC", raw_text)

# 								self.emails[i]['body'] = text
# 								if any(trig in self.emails[i]['body'] for trig in ['пособие', 'пособия', 'методичка', 'методические']) and 'кафедр' in self.emails[i]['body']:
# 									self.emails[i]['type'] = 'Методические пособия'
# 						#Если это просто текст
# 							elif content_type == 'text/plain':
# 								charset = part.get_content_charset()
# 								text = part.get_payload(decode=True).decode(charset)
# 								self.emails[i]['body'] = text
# 						except Exception as e:
# 							self.mail_err_signal.emit('can\'t process email ' + str(i) + '; \nUpload type: ' + self.emails[i]['type'] + '; \nEmail type: ' + self.emails[i]['email type'] + '; \nHeader: ' + self.emails[i]['subject'] + '; \n' + repr(e))
# 							print('[ERROR] mail_thread: can\'t process email ' + str(i) + '; \nUpload type: ' + self.emails[i]['type'] + '; \nEmail type: ' + self.emails[i]['email type'] + '; \nHeader: ' + self.emails[i]['subject'] + '; \n' + repr(e))
# 							return
# 				#А если не составное, то читаем текст
# 				else:
# 					self.emails[i]['email type'] = f'Not multipart'
# 					content_type = email_message.get_content_type()
# 					#Если это html
# 					try:
# 						if content_type == 'text/html':
# 							charset = email_message.get_content_charset()
# 							html = email_message.get_payload(decode=True).decode(charset)
# 							raw_text = BeautifulSoup(html, 'html.parser').text
# 							text = unicodedata.normalize("NFKC", raw_text)
# 							self.emails[i]['body'] = text
# 					#Если это просто текст
# 						elif content_type == 'text/plain':
# 							charset = email_message.get_content_charset()
# 							text = email_message.get_payload(decode=True).decode(charset)
# 							self.emails[i]['body'] = text
# 					except Exception as e:
# 						self.mail_err_signal.emit('can\'t process email ' + str(i) + '; \nUpload type: ' + self.emails[i]['type'] + '; \nEmail type: ' + self.emails[i]['email type'] + '; \nHeader: ' + self.emails[i]['subject'] + '; \n' + repr(e))
# 						print('[ERROR] mail_thread: can\'t process email ' + str(i) + '; \nUpload type: ' + self.emails[i]['type'] + '; \nEmail type: ' + self.emails[i]['email type'] + '; \nHeader: ' + self.emails[i]['subject'] + '; \n' + repr(e))
# 						return
# 			except:
# 				self.mail_err_signal.emit('can\'t define multipart or not')
# 				print('[ERROR] mail_thread: can\'t define multipart or not')
# 				return
# 			self.mail_progress_signal.emit((email_number+1, i+2))
# 			self.email_processed.emit(self.emails[i])

# 	def get_text_docx(self, document):
# 		WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
# 		PARA = WORD_NAMESPACE + 'p'
# 		TEXT = WORD_NAMESPACE + 't'
# 		document = zipfile.ZipFile(document)
# 		xml_content = document.read('word/document.xml')
# 		document.close()
# 		tree = XML(xml_content)
# 		paragraphs = []
# 		for paragraph in tree.iter(PARA):
# 			texts = [node.text for node in paragraph.iter(TEXT)	if node.text]
# 			if texts:
# 				paragraphs.append(''.join(texts))
# 		return ' '.join(paragraphs)

# 	def split_text(self, text_from_docx):
# 		S = []
# 		s1_list = re.findall(r'[А-ЯA-Z]{1}[а-яa-z]{2,20}\s[А-ЯA-Z]\.[А-ЯA-Z]\.', text_from_docx)
# 		s1_end = re.search(s1_list[-1], text_from_docx).end()
# 		s1 = text_from_docx[:s1_end]
# 		s3_begin = re.search(r'//', text_from_docx).end()
# 		s3 = text_from_docx[s3_begin-2:]
# 		s2 = text_from_docx[s1_end:s3_begin-2]
# 		S.append(s1)
# 		S.append(s2)
# 		S.append(s3)
# 		if len(S) == 3:
# 			text_from_docx = S[:]
# 		return text_from_docx

class InternetChecker(QObject):
    def __init__(self, parent=None):
        super(InternetChecker, self).__init__()

    start_call = pyqtSignal()
    isConnected = pyqtSignal(bool)

    @pyqtSlot()
    def start_check2(self):
        import urllib.request
        def is_connected(host='http://google.com'):
            try:
                urllib.request.urlopen(host)
                self.isConnected.emit(True)
                return True
            except Exception as e:
                pass
            self.isConnected.emit(False)
            return False

        is_connected()
        int_timer = QTimer(self)
        int_timer.timeout.connect(is_connected)
        int_timer.start(3000)


class ListElement():
    def __init__(self, sec=None):
        self.sec = sec
        self.text = None
        self.file_path = None


class IndicesLoader(QObject):
    def __init__(self, parent=None):
        super(IndicesLoader, self).__init__()

    started = pyqtSignal()
    finished = pyqtSignal()
    start_call = pyqtSignal(str, str)
    upload_err_signal = pyqtSignal(str)
    loaded_element = pyqtSignal(str)

    def start(self, section, subsection):
        self.started.emit()
        if section == 'Публикации преподавателей':
            webpage = 'publprepod.htm'
            year = subsection
        elif section == 'Методические пособия':
            webpage = kaf_dict[subsection][0]
        print(webpage)

        ftp = ftp_connection()
        if not ftp:
            # self.upload_err_signal.emit('[FTP] connection error')
            print('[ERROR] IndicesLoader thread: FTP connection error')
            return
        # self.progress_signal.emit(2)
        with ftp as ftp:
            if not ftp_download(ftp, '/', webpage, 'html\\'):
                # self.upload_err_signal.emit('[FTP] file download error')
                print('[ERROR] IndicesLoader thread: Download file error')
                return
        with open(f'html\\{webpage}', 'r', encoding='utf-8') as webpage_file:
            contents = webpage_file.read()
            soup = BeautifulSoup(contents, 'html.parser')
            if section == 'Публикации преподавателей':
                datayear = soup.find_all(attrs={"data-year": year})[0]
                elem_list = datayear.find_all('li')
                for i, li in enumerate(elem_list):
                    tag_content = li.text
                    print(f'{i}: {tag_content}')
                    self.loaded_element.emit(tag_content)
            else:
                elem_list = soup.ol.find_all('li')
        self.finished.emit()


class UploadApp(QtWidgets.QMainWindow, new_design.Ui_MainWindow):
    filename = None
    filepath = None
    ed_filename = None
    ed_filepath = None

    selected_indexes = []

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.closeEvent = self.closeEvent1
        self.upload_section()
        # self.background_music = QSound('wav/minecraft_calm.wav')
        # self.background_music.setLoops(1)
        # self.background_music.play()

        # MENU
        # Upload menu
        self.menuButtonUpload.clicked.connect(self.upload_click)
        self.menuButtonImageUpload.clicked.connect(self.upload_click)
        # Delete menu
        self.menuButtonDelete.clicked.connect(self.delete_click)
        self.menuButtonImageDelete.clicked.connect(self.delete_click)
        # Edit menu
        self.menuButtonEdit.clicked.connect(self.edit_click)
        self.menuButtonImageEdit.clicked.connect(self.edit_click)
        # Show Mail
        # self.menuButtonExpand.clicked.connect(self.expand_click)
        # self.menuButtonSqueeze.clicked.connect(self.expand_click)
        # self.menuButtonRefresh.clicked.connect(self.refresh_clicked)

        # UPLOAD
        # Change section
        self.sectionBox.currentIndexChanged.connect(self.change_upload_section)
        # Browse file button
        self.fileButton.clicked.connect(self.get_filepath)
        self.fileButton.dropSignal.connect(self.upload_file_dropped)
        # Update preview
        self.sectionBox.currentIndexChanged.connect(self.update_preview)
        self.kafBox.currentIndexChanged.connect(self.update_preview)
        self.yearBox.currentIndexChanged.connect(self.update_preview)
        self.text1Edit.textChanged.connect(self.update_preview)
        self.text2Edit.textChanged.connect(self.update_preview)
        self.text3Edit.textChanged.connect(self.update_preview)
        self.urlEdit.textChanged.connect(self.update_preview)
        # Menu sound for QComboBox
        # self.sectionBox.currentIndexChanged.connect(self.play_menu_sound)
        # self.kafBox.currentIndexChanged.connect(self.play_menu_sound)
        # self.yearBox.currentIndexChanged.connect(self.play_menu_sound)
        # self.resetButton.clicked.connect(self.play_menu_sound)
        # Reset button
        self.resetButton.clicked.connect(self.reset_upload_fields)
        # Exit button
        self.exitButton.clicked.connect(self.close)
        # Default style
        self.text1Edit.textChanged.connect(lambda w='text1Label': self.def_styles(w))
        self.text2Edit.textChanged.connect(lambda w='text2Label': self.def_styles(w))
        self.text3Edit.textChanged.connect(lambda w='descrLabel': self.def_styles(w))
        self.urlEdit.textChanged.connect(lambda w='urlLabel': self.def_styles(w))
        # Upload button
        self.uploadButton.clicked.connect(self.upload)
        # Upload thread
        self.upload_thread = uploadThread()
        self.upload_thread.started.connect(self.upload_started)
        self.upload_thread.finished.connect(self.upload_finished)
        self.upload_thread.progress_signal.connect(self.upload_progress, Qt.QueuedConnection)
        self.upload_thread.upload_err_signal.connect(self.thread_error_handling, Qt.QueuedConnection)

        # DELETE
        # Reset button
        self.delResetButton.clicked.connect(self.reset_delete_fields)
        # Exit button
        self.delExitButton.clicked.connect(self.close)
        # Refresh button
        self.delListRefreshButton.clicked.connect(self.del_refresh_list)
        # Loader
        self.delete_loader_thread = QThread()
        self.delete_loader_thread.start()
        self.delete_list_loader = IndicesLoader()
        self.delete_list_loader.moveToThread(self.delete_loader_thread)
        self.delete_list_loader.start_call.connect(self.delete_list_loader.start)
        self.delete_list_loader.loaded_element.connect(self.del_add_element, Qt.QueuedConnection)
        self.delete_list_loader.started.connect(self.del_loader_started)
        self.delete_list_loader.finished.connect(self.del_loader_finished)

        # EDIT
        # Reset button
        self.ed_resetButton.clicked.connect(self.reset_edit_fields)
        # Exit button
        self.ed_exitButton.clicked.connect(self.close)
        # File button
        self.ed_fileButton.clicked.connect(self.get_ed_filepath)
        self.ed_fileButton.dropSignal.connect(self.ed_file_dropped)


    def del_loader_started(self):
        self.delListRefreshButton.setEnabled(False)
        print('[INFO] del_loader_started')

    def del_loader_finished(self):
        self.delListRefreshButton.setEnabled(True)
        print('[INFO] del_loader_finished')

    def del_add_element(self, text):
        item = QtWidgets.QListWidgetItem()
        item.setText(f'{self.delList.count()}. {text}')
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Unchecked)
        item.setSizeHint(QSize(item.sizeHint().width(), 100))

    def del_refresh_list(self):
        if self.sectionBox.currentText() == 'Публикации преподавателей':
            self.delete_list_loader.start_call.emit('Публикации преподавателей', self.yearBox.currentText())
        else:
            self.delete_list_loader.start_call.emit('Методические пособия', self.kafBox.currentText())

    def reset_delete_fields(self):
        print('[INFO] reset_delete_fields: resetting fields')
        self.delList.clear()
        self.delSelected.clear()

    def reset_edit_fields(self):
        print('[INFO] reset_edit_fields: resetting fields')
        self.ed_List.clear()
        self.ed_filename = None
        self.ed_filepath = None
        self.ed_filenameLabel.clear()
        self.ed_text1Edit.clear()
        self.ed_text2Edit.clear()
        self.ed_text3Edit.clear()
        self.ed_urlEdit.clear()

    def block_internet_gui(self, isConnected):
        if isConnected:
            self.uploadButton.setEnabled(True)
            self.uploadButton.setStyleSheet(
                f'background: {self.btnBG}; color: {self.btnTxt}; border: none; border-radius: 5px')

            self.delButton.setEnabled(True)
            self.delButton.setStyleSheet(
                f'background: {self.btnBG}; color: {self.btnTxt}; border: none; border-radius: 5px')

            self.editButton.setEnabled(True)
            self.editButton.setStyleSheet(
                f'background: {self.btnBG}; color: {self.btnTxt}; border: none; border-radius: 5px')

            self.delListRefreshButton.setEnabled(True)
            self.delListRefreshButton.setStyleSheet(
                f"padding: 0px; background: {self.lblBG}; background-image: url(ico/ref3.png); border: 2px solid {self.lblBorder}; border-top-right-radius: 5px; color: {self.lblTxt};")

            self.ed_ListRefreshButton.setEnabled(True)
            self.ed_ListRefreshButton.setStyleSheet(
                f"padding: 0px; background: {self.lblBG}; background-image: url(ico/ref3.png); border: 2px solid {self.lblBorder}; border-top-right-radius: 5px; color: {self.lblTxt};")

            self.menuButtonExpand.setEnabled(True)
            self.menuButtonExpand.setStyleSheet(
                f"background: {self.BG}; background-image: url(ico/expand.png); border: none;")

            self.menuButtonRefresh.setEnabled(True)
            self.menuButtonRefresh.setStyleSheet(
                f"background: transparent; background-image: url(ico/refresh.png); border: none;")

            self.menuButtonImageUpload.setEnabled(False if self.current_app_section == 'upload' else True)
            self.menuButtonImageUpload.setStyleSheet(
                "background-color: {b}; background-image: url(ico/{a}.png); border: none;".format(
                    b=self.btnBG if self.current_app_section == 'upload' else self.BG,
                    a='upload' if self.current_app_section != 'upload' else 'upload_inactive'))

            self.menuButtonImageDelete.setEnabled(False if self.current_app_section == 'delete' else True)
            self.menuButtonImageDelete.setStyleSheet(
                "background-color: {b}; background-image: url(ico/{a}.png); border: none;".format(
                    b=self.btnBG if self.current_app_section == 'delete' else self.BG,
                    a='delete' if self.current_app_section != 'delete' else 'delete_inactive'))

            self.menuButtonImageEdit.setEnabled(False if self.current_app_section == 'edit' else True)
            self.menuButtonImageEdit.setStyleSheet(
                "background-color: {b}; background-image: url(ico/{a}.png); border: none;".format(
                    b=self.btnBG if self.current_app_section == 'edit' else self.BG,
                    a='edit' if self.current_app_section != 'edit' else 'edit_inactive'))
        else:
            self.uploadButton.setEnabled(False)
            self.uploadButton.setStyleSheet(f'background: {self.err}; color: red; border: none; border-radius: 5px')

            self.delButton.setEnabled(False)
            self.delButton.setStyleSheet(f'background: {self.err}; color: red; border: none; border-radius: 5px')

            self.editButton.setEnabled(False)
            self.editButton.setStyleSheet(f'background: {self.err}; color: red; border: none; border-radius: 5px')

            self.delListRefreshButton.setEnabled(False)
            self.delListRefreshButton.setStyleSheet(
                f"padding: 0px; background: {self.lblBG}; background-image: url(ico/ref3_err.png); border: 2px solid {self.lblBorder}; border-top-right-radius: 5px; color: {self.lblTxt};")

            self.ed_ListRefreshButton.setEnabled(False)
            self.ed_ListRefreshButton.setStyleSheet(
                f"padding: 0px; background: {self.lblBG}; background-image: url(ico/ref3_err.png); border: 2px solid {self.lblBorder}; border-top-right-radius: 5px; color: {self.lblTxt};")

            self.menuButtonExpand.setEnabled(False)
            self.menuButtonExpand.setStyleSheet(
                f"background: {self.BG}; background-image: url(ico/expand_err.png); border: none;")

            self.menuButtonRefresh.setEnabled(False)
            self.menuButtonRefresh.setStyleSheet(
                f"background: transparent; background-image: url(ico/refresh_err.png); border: none;")

            self.menuButtonImageUpload.setEnabled(False)
            self.menuButtonImageUpload.setStyleSheet(
                f"background-color: {self.btnBG if self.current_app_section == 'upload' else self.BG}; background-image: url(ico/upload_err.png); border: none;")

            self.menuButtonImageDelete.setEnabled(False)
            self.menuButtonImageDelete.setStyleSheet(
                f"background: {self.btnBG if self.current_app_section == 'delete' else self.BG}; background-image: url(ico/delete_err.png); border: none;")

            self.menuButtonImageEdit.setEnabled(False)
            self.menuButtonImageEdit.setStyleSheet(
                f"background: {self.btnBG if self.current_app_section == 'edit' else self.BG}; background-image: url(ico/edit_err.png); border: none;")

    def insert_mail_data(self, item):
        i = self.emailList.row(item)
        if self.email[i]['type'] == 'Публикации преподавателей':
            self.sectionBox.setCurrentIndex(0)
            for year in years:
                if year in self.email[i]['attachments'][0]:
                    self.yearBox.setCurrentIndex(self.yearBox.findText(year, Qt.MatchExactly))
            self.text1Edit.setText(self.email[i]['docx_text'][0])
            self.urlEdit.setText(self.email[i]['docx_text'][1])
            self.text2Edit.setText(self.email[i]['docx_text'][2])
            self.get_filepath('mail_files/{}'.format(
                self.email[i]['attachments'][1] if self.email[i]['attachments'][1][-4:] == '.pdf' else
                self.email[i]['attachments'][0]))

        elif self.email[i]['type'] == 'Методические пособия':
            self.sectionBox.setCurrentIndex(1)
            is_name_detected = False
            for name in kaf_dict_search:
                if is_name_detected:
                    break
                if str(name).lower() in self.email[i]['body'].lower():
                    is_name_detected = name
                    break
                else:
                    for name2 in kaf_dict_search[name]:
                        if name2 and str(name2).lower() in self.email[i]['body'].lower():
                            is_name_detected = name
                            break
            self.text3Edit.setText(self.email[i]['body'])
            if is_name_detected:
                self.kafBox.setCurrentIndex(self.kafBox.findText(is_name_detected, Qt.MatchExactly))

    def mail_list_selection(self):
        for i in range(self.emailList.count()):
            item = self.emailList.item(i)
            if item.isSelected():
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

    def mail_list_item(self, item):
        if item.checkState() == 0:
            item.setSelected(False)
        else:
            item.setSelected(True)

    def mail_interrupted(self):
        print('[INFO] mail_interrupted: setting default MailProgressBar style')
        self.mailProgressBarLabel.setGeometry(0, 40, 0, 2)
        self.mailProgressBarLabel.setStyleSheet(f'border-bottom: 2px solid {self.lblTxt}; background: transparent')

    def mail_error_handling(self, s):
        def move():
            self.mailProgressBarLabel.setGeometry(0, 40, 0, 2)
            self.mailProgressBarLabel.setStyleSheet(f'border-bottom: 2px solid {self.lblTxt}; background: transparent')
            self.previewText.clear()
            timer.stop()

        self.mailProgressBarLabel.setStyleSheet(f'border-bottom: 2px solid {self.err}; background: transparent')
        self.previewText.insertHtml(f'<b><font color="{self.err}">{s}</font></b>')
        QSound.play('wav/minecraft_damage.wav')
        timer = QTimer(self)
        timer.timeout.connect(move)
        timer.start(3000)

    def update_email_list(self, email):
        self.email.append(email)
        upload_type = email['type']
        subj = email['subject']
        body = email['body'].strip() + "\n\n" if email['body'] else ""
        attachments = '\n'.join(email['attachments'])

        item_text = f'[{upload_type}] {subj}.\n\n{body}{attachments}'

        item = QtWidgets.QListWidgetItem()
        # if email['type'] == 'Публикации преподавателей':
        item.setText(item_text)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Unchecked)
        item.setSizeHint(QSize(item.sizeHint().width(), 100))
        self.emailList.addItem(item)

    def mail_progress(self, n):
        def move():
            self.mailProgressBarLabel.setGeometry(0, 40, 0, 2)
            self.mailProgressBarLabel.setStyleSheet(f'border-bottom: 2px solid {self.lblTxt}; background: transparent')
            timer.stop()

        delta = 700 / n[0]
        pos = round(delta * n[1])
        self.mailProgressBarLabel.setGeometry(0, 40, pos if pos < 694 else 700, 2)
        if pos == 700:
            QSound.play('wav/gta_beep.wav')
            timer = QTimer(self)
            timer.timeout.connect(move)
            timer.start(1000)

    def mail_started(self):
        print('[INFO] mail_started: mail thread started')

    def mail_finished(self):
        print('[INFO] mail_finished: mail thread finished')
        self.menuButtonExpand.setEnabled(True)

    def upload_file_dropped(self, s):
        self.get_filepath(s)

    def ed_file_dropped(self, s):
        self.get_ed_filepath(s)

    def upload(self):
        if not self.check_filled(self.update_preview()):
            background_music = QSound.play('wav/minecraft_damage.wav')
            print('[WARNING] upload: empty fields')
            return False
        if self.sectionBox.currentText() == 'Публикации преподавателей':
            webpage = 'publprepod.htm'
            directory = '/lib/publprepod/'
            auth_data = self.text1Edit.toPlainText().strip().replace('\n', ' ')
            name_data = self.urlEdit.toPlainText().strip().replace('\n', ' ')
            mag_data = self.text2Edit.toPlainText().strip().replace('\n', ' ')
            year = self.yearBox.currentText()
            auth_data = auth_data if auth_data != '0' else ''
            mag_data = mag_data if mag_data != '0' else ''
            upload_data = [webpage, directory, self.filename, self.filepath, year, auth_data, name_data, mag_data]
        else:
            if self.kafBox.currentText() not in kaf_dict:
                QSound.play('wav/minecraft_damage.wav')
                print('[ERROR] upload: Kafedra not found')
                return False
            webpage = kaf_dict[self.kafBox.currentText()][0]
            directory = kaf_dict[self.kafBox.currentText()][1]
            kaf_data = self.text3Edit.toPlainText().strip().replace('\n', ' ')
            upload_data = [webpage, directory, self.filename, self.filepath, kaf_data]
        QSound.play('wav/gta_menu.wav')
        # тут идём в другой тред со всеми тяжами
        self.upload_thread.upload_data = list(upload_data)
        self.upload_thread.start()

    def thread_error_handling(self, s):
        def move():
            self.progressBarLabel.setGeometry(-500, 40, 500, 2)
            self.progressBarLabel.setStyleSheet(f'border-bottom: 2px solid {self.lblTxt}; background: transparent')
            self.previewText.clear()
            timer.stop()

        self.progressBarLabel.setStyleSheet(f'border-bottom: 2px solid {self.err}; background: transparent')
        self.previewText.insertHtml(f'<b><font color=red>{s}</font></b>')
        QSound.play('wav/minecraft_damage.wav')
        timer = QTimer(self)
        timer.timeout.connect(move)
        timer.start(3000)

    def upload_progress(self, i):
        def move():
            self.progressBarLabel.setGeometry(-500, 40, 500, 2)
            self.progressBarLabel.setStyleSheet(f'border-bottom: 2px solid {self.lblTxt}; background: transparent')
            timer.stop()

        # 1 i equals 50 pixels
        self.progressBarLabel.setGeometry(-500 + i * 50, 40, 500, 2)
        if i == 10:
            QSound.play('wav/gta_beep.wav')
            timer = QTimer(self)
            timer.timeout.connect(move)
            timer.start(1000)

    def upload_started(self):
        print('[INFO] upload_started: upload thread started')
        self.closeEvent = self.closeEvent2
        self.uploadButton.setEnabled(False)
        self.uploadButton.setStyleSheet(f'background: grey; color: {self.btnTxt}; border: none; border-radius: 5px')
        self.reset_upload_fields()

    def upload_finished(self):
        print('[INFO] upload_finished: upload finished')
        self.closeEvent = self.closeEvent1
        self.uploadButton.setEnabled(True)
        self.uploadButton.setStyleSheet(
            f'background: {self.btnBG}; color: {self.btnTxt}; border: none; border-radius: 5px')

    def check_filled(self, data_tup):
        print('[INFO] check_filled: started checking required fields')
        k = 0
        if data_tup[0]:
            print('[INFO] check_filled: Публикации преподавателей')
            if not data_tup[1]:
                self.text1Label.setStyleSheet(
                    f'background: {self.lblBG}; border-top: 1px solid {self.lblBorder}; border-bottom: 1px solid {self.lblBorder}; color: {self.err}')
                k += 1
                print('[INFO] check_filled: 	text1 is empty')
            if not data_tup[2]:
                self.urlLabel.setStyleSheet(
                    f'background: {self.lblBG}; border-top: 1px solid {self.lblBorder}; border-bottom: 1px solid {self.lblBorder}; color: {self.err}')
                k += 1
                print('[INFO] check_filled: 	URL is empty')
            if not data_tup[3]:
                self.text2Label.setStyleSheet(
                    f'background: {self.lblBG}; border-top: 1px solid {self.lblBorder}; border-bottom: 1px solid {self.lblBorder}; color: {self.err}; border-bottom-left-radius: 5px')
                k += 1
                print('[INFO] check_filled: 	Text 2 is empty')
        elif not data_tup[1]:
            print('[INFO] check_filled: Методические пособия')
            self.descrLabel.setStyleSheet(
                f'background: {self.lblBG}; border: 2px solid {self.lblBorder}; border-top-right-radius: 5px; border-top-left-radius: 5px; color: {self.err}')
            k += 1
            print('[INFO] check_filled: 	Text 3 (description) is empty')
        if not self.filepath:
            self.fileButton.setStyleSheet(
                f'background: {self.btnBG}; color: {self.err}; border: none; border-radius: 5px')
            k += 1
            print('[INFO] check_filled: filepath is empty')
        return False if k > 0 else True

    def def_styles(self, widget_name=None):
        if widget_name is not None:
            print(f'[INFO] def_styles: def styles for {widget_name}')
            if widget_name == 'text1Label':
                self.text1Label.setStyleSheet(
                    f'background: {self.lblBG}; border-top: 1px solid {self.lblBorder}; border-bottom: 1px solid {self.lblBorder}; color: {self.lblTxt}')
            elif widget_name == 'text2Label':
                self.text2Label.setStyleSheet(
                    f'background: {self.lblBG}; border-top: 1px solid {self.lblBorder}; border-bottom: 1px solid {self.lblBorder}; color: {self.lblTxt}; border-bottom-left-radius: 5px')
            elif widget_name == 'descrLabel':
                self.descrLabel.setStyleSheet(
                    f'background: {self.lblBG}; border: 2px solid {self.lblBorder}; border-top-right-radius: 5px; border-top-left-radius: 5px; color: {self.lblTxt}')
            elif widget_name == 'urlLabel':
                self.urlLabel.setStyleSheet(
                    f'background: {self.lblBG}; border-top: 1px solid {self.lblBorder}; border-bottom: 1px solid {self.lblBorder}; color: {self.lblTxt}')
        else:
            print(f'[INFO] def_styles: def styles')
            self.text1Label.setStyleSheet(
                f'background: {self.lblBG}; border-top: 1px solid {self.lblBorder}; border-bottom: 1px solid {self.lblBorder}; color: {self.lblTxt}')
            self.text2Label.setStyleSheet(
                f'background: {self.lblBG}; border-top: 1px solid {self.lblBorder}; border-bottom: 1px solid {self.lblBorder}; color: {self.lblTxt}; border-bottom-left-radius: 5px')
            self.descrLabel.setStyleSheet(
                f'background: {self.lblBG}; border: 2px solid {self.lblBorder}; border-top-right-radius: 5px; border-top-left-radius: 5px; color: {self.lblTxt}')
            self.urlLabel.setStyleSheet(
                f'background: {self.lblBG}; border-top: 1px solid {self.lblBorder}; border-bottom: 1px solid {self.lblBorder}; color: {self.lblTxt}')
            self.fileButton.setStyleSheet(
                f'background: {self.btnBG}; color: {self.btnTxt}; border: none; border-radius: 5px')

    def reset_upload_fields(self):
        print('[INFO] reset_upload_fields: resetting fields')
        self.fileButton.setStyleSheet(
            f'background: {self.btnBG}; color: {self.btnTxt}; border: none; border-radius: 5px')
        self.filename = None
        self.filepath = None
        self.filenameLabel.clear()
        self.text1Edit.clear()
        self.text2Edit.clear()
        self.text3Edit.clear()
        self.urlEdit.clear()
        self.previewText.clear()

    def update_preview(self):
        self.previewText.clear()
        auth_data = self.text1Edit.toPlainText().strip().replace('\n', ' ')
        name_data = self.urlEdit.toPlainText().strip().replace('\n', ' ')
        mag_data = self.text2Edit.toPlainText().strip().replace('\n', ' ')
        kaf_data = self.text3Edit.toPlainText().strip().replace('\n', ' ')
        if self.sectionBox.currentText() == 'Публикации преподавателей':
            content = auth_data + '<font color=#83CAFF>' + name_data + '</font>' + mag_data
            self.previewText.append(content)
            return True, auth_data, name_data, mag_data
        else:
            content = kaf_data + '<br>Режим доступа: <font color=#83CAFF>http://nizrp.narod.ru' + \
                      kaf_dict[self.kafBox.currentText()][1] + (self.filename if self.filename else '') + '</font>'
            self.previewText.insertHtml(content)
            return False, kaf_data

    # QSound.play('wav/gta_menu.wav')

    def get_filepath(self, drop_filepath=None):
        # if drop_filepath is None or drop_filepath is False:
        if not drop_filepath:
            self.filepath = QtWidgets.QFileDialog.getOpenFileName(self, filter='pdf(*.pdf)')[0]
        else:
            self.filepath = drop_filepath

        if len(self.filepath):
            self.filenameLabel.setText(os.path.split(self.filepath)[1])
            print('[INFO] get_filepath: filepath =', self.filepath)
            self.filename = str(int(time.time())) + '.pdf'
            print('[INFO] get_filepath: filename =', self.filename)
            self.fileButton.setStyleSheet(
                f'background: {self.btnBG}; color: {self.btnTxt}; border: none; border-radius: 5px')
            self.update_preview()
            return True
        print('[INFO] get_filepath: dialog canceled')
        self.filepath = None
        self.filename = None

    def get_ed_filepath(self, drop_ed_filepath=None):
        QSound.play('wav/gta_menu.wav')
        if not drop_ed_filepath:
            self.ed_filepath = QtWidgets.QFileDialog.getOpenFileName(self, filter='pdf(*.pdf)')[0]
        else:
            self.ed_filepath = drop_ed_filepath

        if len(self.ed_filepath):
            self.ed_filenameLabel.setText(os.path.split(self.ed_filepath)[1])
            print('[INFO] get_ed_filepath: ed_filepath =', self.ed_filepath)
            self.ed_filename = str(int(time.time())) + '.pdf'
            print('[INFO] get_ed_filepath: ed_filename =', self.ed_filename)
            self.ed_fileButton.setStyleSheet(
                f'background: {self.btnBG}; color: {self.btnTxt}; border: none; border-radius: 5px')
            return True
        print('[INFO] get_ed_filepath: dialog canceled')
        self.ed_filepath = None
        self.ed_filename = None

    def change_upload_section(self):
        if self.sectionBox.currentText() == 'Публикации преподавателей':
            print('[INFO] change_upload_section: changing section to publprepod')
            self.yearLabel.setVisible(True)
            self.yearBox.setVisible(True)
            self.text3Edit.setVisible(False)
        else:
            self.yearLabel.setVisible(False)
            self.yearBox.setVisible(False)
            self.text3Edit.setVisible(True)

    def upload_click(self):
        QSound.play('wav/gta_menu.wav')
        self.upload_section()

    def delete_click(self):
        QSound.play('wav/gta_menu.wav')
        self.delete_section()

    def edit_click(self):
        QSound.play('wav/gta_menu.wav')
        self.edit_section()

    def squeeze_click(self):
        QSound.play('wav/gta_menu.wav')
        self.squeeze_section()
        self.mail_thread.interruption_flag = True

    def expand_click(self):
        if not self.mail_opened:
            self.expand_section()
            if not self.mail_thread.isRunning():  # and self.emailList.count() == 0:
                self.emailList.clear()
                self.mail_thread.start()
            self.mail_opened = True
        else:
            self.squeeze_section()
            if self.mail_thread.isRunning():
                self.mail_thread.interruption_flag = True
                self.menuButtonExpand.setEnabled(False)
            self.mail_opened = False

    def expand_section(self):
        print('[INFO] expand_section: expand')
        self.setFixedSize(1200, 700)
        self.menuButtonExpand.setStyleSheet(
            f"background: {self.BG}; background-image: url(ico/squeeze.png); border: none;")

    def squeeze_section(self):
        print('[INFO] squeeze_section: squeeze')
        self.setFixedSize(500, 700)
        self.menuButtonExpand.setStyleSheet(
            f"background: {self.BG}; background-image: url(ico/expand.png); border: none;")

    def refresh_clicked(self):
        if not self.mail_thread.isRunning():
            self.emailList.clear()
            self.mail_thread.start()

    def play_menu_sound(self):
        QSound.play('wav/gta_menu.wav')

    def closeEvent1(self, event):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle('UploadApp')
        msg.setText('Are you sure?')
        msg.setWindowFlags(
            Qt.Window |
            Qt.CustomizeWindowHint |
            Qt.WindowTitleHint |
            Qt.WindowStaysOnTopHint)
        msg.setIcon(QtWidgets.QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        # ret = msg.exec()
        ret = False
        if ret == QMessageBox.No:
            event.ignore()
        else:
            print('[INFO]: closeEvent1: exiting application', '<{}>'.format(time.asctime(time.localtime(time.time()))))
            event.accept()

    def closeEvent2(self, event):
        print('\n')
        print('[INFO] closeEvent2: ignoring closeEvent')
        event.ignore()


def main():
    print('[INFO] main: Starting application', '<{}>'.format(time.asctime(time.localtime(time.time()))))
    app = QtWidgets.QApplication(sys.argv)
    window = UploadApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    print('\n')
    k = 0
    if not os.path.exists('debug.log'):
        print('[WARNING]: Missing debug.log', '<{}>'.format(time.asctime(time.localtime(time.time()))))
        print('[INFO]: Creating debug.log')
        try:
            open('debug.log', 'w', encoding="utf-8").close()
        except Exception as e:
            print('[ERROR]: failed to create debug.log')
            print('[ERROR]:', e)
            ctypes.windll.user32.MessageBoxW(0, "failed to create debug.log", "Error", 0)
            k += 1
    if k > 0:
        sys.exit()
    with open('debug.log', 'a', encoding="utf-8") as log:
        # sys.stdout = log
        main()
