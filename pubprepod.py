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
