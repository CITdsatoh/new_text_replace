#encoding:utf-8;

import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
from tkinter.filedialog import askopenfilename,asksaveasfilename
import os
from io_file_choice.io_manage.file_io_manage import FileIOManage,not_sep


class FilePathEntryCorner(tk.Frame):
  
  __next_entry_id=1
  
  def __init__(self,master=None,w:int=928,h:int=96):
    self.__master=master
    super().__init__(master,width=w,height=h)
    
    self.__entry_id_label=tk.Label(self,text=f"その{self.__class__.__next_entry_id}:",font=("times",11,"bold"))
    self.__entry_id_label.place(x=0,y=16)
    self.__class__.__next_entry_id += 1
    
    self.__src_label=tk.Label(self,text="テキストを置換したいファイル名:",font=("times",11,"bold"))
    self.__src_label.place(x=48,y=0)
    
    self.__src_file_path_entry=tk.Entry(self,width=50,font=("times",11))
    self.__src_file_path_entry.place(x=336,y=0)
    
    self.__src_file_path_choice_btn=tk.Button(self,text="参照",font=("times",11))
    self.__src_file_path_choice_btn.place(x=736,y=0)
    self.__src_file_path_choice_btn.bind("<Button-1>",self.src_file_choice)
    
    self.__src_file_path_reset_btn=tk.Button(self,text="取消",font=("times",11))
    self.__src_file_path_reset_btn.place(x=784,y=0)
    self.__src_file_path_reset_btn.bind("<Button-1>",self.entry_reset)
    
    
    self.__dst_label=tk.Label(self,text="置換結果を書き込むファイル名:",font=("times",11,"bold"))
    self.__dst_label.place(x=48,y=32)
    
    self.__dst_file_path_entry=tk.Entry(self,width=50,font=("times",11))
    self.__dst_file_path_entry.place(x=336,y=32)
    
    self.__dst_file_path_choice_btn=tk.Button(self,text="参照",font=("times",11))
    self.__dst_file_path_choice_btn.place(x=736,y=32)
    self.__dst_file_path_choice_btn.bind("<Button-1>",self.dst_file_choice)
    
    self.__dst_file_path_reset_btn=tk.Button(self,text="取消",font=("times",11))
    self.__dst_file_path_reset_btn.place(x=784,y=32)
    self.__dst_file_path_reset_btn.bind("<Button-1>",self.entry_reset)
    
    self.__all_input_reset_btn=tk.Button(self,text="両入力取消",font=("times",11))
    self.__all_input_reset_btn.place(x=832,y=16)
    self.__all_input_reset_btn.bind("<Button-1>",self.entry_reset)
    
    self.__error_disp_label=tk.Label(self,text="",font=("times",11,"bold"),fg="#ff0000")
    self.__error_disp_label.place(x=64,y=56)
    
    self.__default_label_bg_color=self["bg"]
  
  
  def entry_reset(self,event=None):
     pressed_btn=None
     if event is not None:
       pressed_btn=event.widget
     
     #「テキストを置換するファイル名」の入力欄のそばの「取消」ボタン(src_file_path_reset_btn) が押される→ 「src_file_path_entryの入力欄のみを空にする」
     #「置換結果を書き込むファイル名」の入力欄のそばの「取消」ボタン(dst_file_path_reset_btn)が押される→「dst_file_path_entryの入力欄のみを空にする」
     #「両入力取消」ボタン(all_input_reset_btn)を押す→両方の入力欄を空にする
     #ボタンを押さずにメソッドが呼ばれた場合(eventがNoneの場合)→両方の入力欄を空にする
     
     #「src_file_path_entry」を空にするのは、「dst_file_path_reset_btn」が押されたとき「以外」
     if pressed_btn !=  self.__dst_file_path_reset_btn:
       self.__src_file_path_entry.delete(0,tk.END)
     
     #「dst_file_path_entry」を空にするのは、「src_file_path_reset_btn」が押されたとき「以外」
     if pressed_btn != self.__src_file_path_reset_btn:
       self.__dst_file_path_entry.delete(0,tk.END)
  
  def all_reset(self):
    self.entry_reset()
    self.__error_disp_label["text"]=""
    self.__error_disp_label["bg"]=self.__default_label_bg_color
  
  
  #「テキストを置換するファイル名」の選択(=「置換結果を書き込むファイル名」の選択時と処理内容が異なるのでここはメソッドを分割する)
  def src_file_choice(self,event=None):
    is_continue=True
    while is_continue:
     new_src_file_path=askopenfilename(parent=self.__master,title="テキストを置換したいファイルを選択",initialdir=os.path.expanduser("~"))
     if len(new_src_file_path) != 0:
        self.__src_file_path_entry.delete(0,tk.END)
        self.__src_file_path_entry.insert(0,new_src_file_path.replace(not_sep,os.sep))
        break
     is_continue=messagebox.askyesno("ファイル選択","ファイルの選択がキャンセルされました。もう1度選びなおしますか?")
   
  def dst_file_choice(self,event=None):
    is_continue=True
    extension=os.path.splitext(self.__src_file_path_entry.get())[1].lstrip(".")
    while is_continue:
     new_dst_file_path=asksaveasfilename(parent=self.__master,title="置換結果を書き込むファイルを選択",initialdir=os.path.expanduser("~"),defaultextension=extension)
     if len(new_dst_file_path) != 0:
        self.__dst_file_path_entry.delete(0,tk.END)
        self.__dst_file_path_entry.insert(0,new_dst_file_path.replace(not_sep,os.sep))
        break
     is_continue=messagebox.askyesno("ファイル選択","ファイルの選択がキャンセルされました。もう1度選びなおしますか?")
  
  def get_input_src_file_path(self):
    return self.__src_file_path_entry.get()
  
  def get_input_dst_file_path(self):
    return self.__dst_file_path_entry.get()
  
  #外部から、ファイル名を設定するのは、複数一気に選択したときのみ。むやみに、外部からファイル名を設定されないように、念入りに確認する
  def set_input_src_file_path(self,set_str:str):
    if len(self.__src_file_path_entry.get()) != 0:
      return
    if not os.path.isfile(set_str):
      return 
    if not os.path.isabs(set_str):
      return
    self.__src_file_path_entry.insert(0,set_str)
  
  def get_file_information(self):
     
     if len(self.__src_file_path_entry.get()) == 0:
       #読み取り元が記述されていないのに、書き込み先が記述されている場合はエラーとする
       if len(self.__dst_file_path_entry.get()) !=  0:
          self.__error_disp_label["text"]="エラー：テキストを置換したいファイルが指定されていません。必ず、置換したいファイルは指定してください"
          self.__error_disp_label["bg"]="#ff8888"
          return None
       
       #両方とも入力されていなかった場合は、正常なので、エラーは出さないが、返すものがないのでNoneを返す
       #本来は、両方とも入力されていない場合は、ユーザーからの「この入力欄にはファイルを指定しなくていいよ」という意思表示になるので、呼び出しもとで確かめるべき、
       self.__error_disp_label["bg"]=self.__default_label_bg_color
       self.__error_disp_label["text"]=""
       return None
     
     #作業ディレクトリを一時的に、ユーザーのホームディレクトリにしたいので、後で元に戻せるように、現在の作業ディレクトリ名をとっておく
     ini_working_dir=os.getcwd()
     
     os.chdir(os.path.expanduser("~"))
     
     if not os.path.isfile(self.__src_file_path_entry.get()):
       self.__error_disp_label["text"]="エラー:テキストを置換するファイルが誤ってフォルダが指定されているか、拡張子が抜けているか、あるいは、\n存在しないファイルが指定されています。ファイルは完全な形で入力してください"
       self.__error_disp_label["bg"]="#ff8888"
       os.chdir(ini_working_dir)
       return None
     
     os.chdir(ini_working_dir)
     self.__error_disp_label["text"]=""
     self.__error_disp_label["bg"]=self.__default_label_bg_color
     return FileInformationRepository(self.__src_file_path_entry.get(),self.__dst_file_path_entry.get())
  
  @classmethod
  def parse_from_file_information_obj(cls,master,file_info_obj):
    new_entry_obj=cls(master)
    new_entry_obj.__src_file_path_entry.insert(0,file_info_obj.src_file_path_str)
    new_entry_obj.__dst_file_path_entry.insert(0,file_info_obj.dst_file_path_str)
    return new_entry_obj
  
  @classmethod
  def reset_next_id(cls):
    cls.__next_entry_id=1
     
     


#ユーザーがファイルパス設定ダイアログを閉じて、また開きなおした後でも、閉じる前の状態を継続して利用できるよう
#Replaceの時と同じように保存用クラスを作成する
class FileInformationRepository:

   def __init__(self,src_file_path_str:str,dst_file_path_str:str=""):
     self.__src_file_path_str=src_file_path_str
     self.__dst_file_path_str=dst_file_path_str
   
   #この保存結果から、実際にファイル操作を行うオブジェクトを返却する
   #エラー処理は、もう行われている前提なので、ここでは正しく入力されていることを前提とする
   def get_file_io_manage_obj(self):
     if len(self.__src_file_path_str) == 0 and len(self.__dst_file_path_str) == 0:
        return None
     return FileIOManage(self.__src_file_path_str,self.__dst_file_path_str)
   
   def __str__(self):
     if len(self.__src_file_path_str) == 0 and len(self.__dst_file_path_str) == 0:
       return "未設定"
     
     src_str=f"テキストを置換したいファイル:{self.__src_file_path_str}"
     dst_str=f"置換結果を書き込むファイル:{self.__dst_file_path_str}"
     if len(self.__dst_file_path_str) == 0:
       dst_str=f"置換結果を書き込むファイル:{self.__src_file_path_str}(上書き)"
     
     return f"{src_str}\n{dst_str}"
   
   
   @property
   def src_file_path_str(self):
     return self.__src_file_path_str
   
   @property
   def dst_file_path_str(self):
     return self.__dst_file_path_str
     
          
         
    
       