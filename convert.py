# -*- coding: UTF-8 -*-

import wx, ffmpy, time, os, glob, shutil, json
import threading
from datetime import datetime
from os.path import expanduser as eu

def henkan(files):
    with open('ignore/mysettings.json', 'r', encoding='utf8') as f:
        outdir = json.load(f)['outdir']
    if files == ['']:
        files = []
    for path in files:
        name = path.rsplit(os.sep, 1)[1].rsplit(".",1)[0]
        size = os.path.getsize(path) / 1000 / 1000
        type = path.rsplit(os.sep, 1)[1].rsplit(".", 1)[1]    
        outfile = outdir + name + '.mp3'
        
        if size >= 300:
            if input(path + ' is too large! size=%s y/n? :' % size) != 'y':
                continue
        if not os.path.exists(outfile):
            try:
                ff = ffmpy.FFmpeg(inputs={path : None}, outputs={outfile : "-b:a 128k"})
                ff.run()
            except:
                pass
    print('process end')
                
class FileDropTarget(wx.FileDropTarget):
    """ Drag & Drop Class """
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, files):
        self.window.text_entry.SetLabel(str(files))#[0]
        #wx.Exit()
        thread_obj = threading.Thread(target=henkan, args=[files])  # Threadオブジェクトの作成
        thread_obj.start()
        #henkan(files)
        return 0



class App(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(500, 700), style=wx.DEFAULT_FRAME_STYLE)
        p = wx.Panel(self, wx.ID_ANY)
        layout = wx.BoxSizer(wx.VERTICAL)
        
        label = wx.StaticText(p, wx.ID_ANY, 'ここにファイルをドロップしてください', style=wx.SIMPLE_BORDER | wx.TE_CENTER)
        label.SetBackgroundColour("#e0ffff")
        label.SetDropTarget(FileDropTarget(self))
        layout.Add(label, flag=wx.EXPAND | wx.ALL, border=10, proportion=1)
        
        self.button1 = wx.Button(p, wx.ID_ANY, 'ダウンロードフォルダをチェック')
        self.button1.Bind(wx.EVT_BUTTON, self.btn1push)
        layout.Add(self.button1, flag=wx.EXPAND | wx.ALL, border=15)
        self.button2 = wx.Button(p, wx.ID_ANY, 'ダウンロードフォルダをチェック（再帰）')
        self.button2.Bind(wx.EVT_BUTTON, self.btn2push)
        layout.Add(self.button2, flag=wx.EXPAND | wx.ALL, border=10)
        self.button3 = wx.Button(p, wx.ID_ANY, 'convert')
        self.button3.Bind(wx.EVT_BUTTON, self.btn3push)
        layout.Add(self.button3, flag=wx.EXPAND | wx.ALL, border=10)
        self.button4 = wx.Button(p, wx.ID_ANY, 'DLフォルダの変換済フォルダへすべて移動')
        self.button4.Bind(wx.EVT_BUTTON, self.btn4push)
        layout.Add(self.button4, flag=wx.EXPAND | wx.ALL, border=10)
        
        self.text_entry = wx.TextCtrl(p, wx.ID_ANY, size=(400, 200), style=wx.TE_MULTILINE)
        layout.Add(self.text_entry, flag=wx.EXPAND | wx.ALL, border=10)
        self.text2 = wx.TextCtrl(p, wx.ID_ANY, size=(400, 100), style=wx.TE_MULTILINE)
        layout.Add(self.text2, flag=wx.EXPAND | wx.ALL, border=10)
        
        p.SetSizer(layout)
        icon=wx.EmptyIcon()
        icon_source=wx.Image('icon.jpg',wx.BITMAP_TYPE_JPEG)
        icon.CopyFromBitmap(icon_source.ConvertToBitmap())
        self.SetIcon(icon)
        #self.taskbar = wx.adv.TaskBarIcon()
        #self.taskbar.SetIcon(icon, '')
        self.Show()
        
    def btn1push(self, event):
        ls = glob.glob(eu('~/Downloads/*.mp4'), recursive=True)
        self.text_entry.SetValue('\n'.join(ls))    
    
    def btn2push(self, event):
        ls = glob.glob(eu('~/Downloads/**/*.mp4'), recursive=True)
        self.text_entry.SetValue('\n'.join(ls))
    
    def btn3push(self, event):
        files = self.text_entry.GetValue().split('\n')
        if threading.active_count() <= 1:
            self.text2.SetValue('%s : 変換開始' % datetime.now())
            t = threading.Thread(target=henkan, args=[files])
            t.start()
        else:
            self.text2.SetValue('稼働中のプロセスがあります')
            
    def btn4push(self, event):
        for file in self.text_entry.GetValue().split('\n'):
            shutil.move(file, eu('~/Downloads/変換済/'))
        self.text2.SetValue(self.text2.GetValue() + '%s : 移動しました' % datetime.now())
        

app = wx.App()
App(None, -1, 'ffmpeg convert tool')
app.MainLoop()