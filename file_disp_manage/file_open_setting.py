#encoding:utf-8;

from tkinter import simpledialog,messagebox,filedialog
import tkinter as tk
import configparser
import os
from io_file_choice.io_manage.file_io_manage import not_sep

class FileOpenApplicationSettingDialog(simpledialog.Dialog):
   
   __file_open_ini_file=os.path.abspath("open_application_by_extension.ini")
   __file_config=configparser.ConfigParser()
   
   __section_name="openApplicationFilePath"
   
   def __init__(self,parent,file_ext:str):
     self.__file_ext=file_ext
     title=f"拡張子{file_ext}を開くアプリケーションの選択"
     super().__init__(parent,title)
   
   def buttonbox(self):
     self.__header_label=tk.Label(self,text=f"拡張子{self.__file_ext}を開くアプリケーションの選択",font=("serif",16,"bold"))
     self.__header_label.place(x=256,y=0)
     
     
     current_file_path=self.__class__.get_open_application_file_path(self.__file_ext)
     
     current_file_str=current_file_path or "既定のアプリ(現在,OSで設定されている拡張子ごとに関連付けられているアプリケーション)"
     
     explaination_header=f"現在、拡張子{self.__file_ext}のファイルは{current_file_str}で開かれることになっています。"
     
     #この文字列が40文字を超えたら、「で開かれる」の部分で改行する
     if 40 < len(explaination_header):
       explaination_header_br_index=explaination_header.index("で開かれる")
       explaination_header=explaination_header[0:explaination_header_br_index]+"\n"+explaination_header[explaination_header_br_index:]
       
     
     explaination_str=f"{explaination_header}\nもし、変更する場合は以下の入力欄に開きたいアプリケーションのパスを入力するか、\n参照ボタンより、アプリケーションのパスを選択してください。"
     self.__explaination_label=tk.Label(self,text=explaination_str,font=("serif",12,"bold"))
     self.__explaination_label.place(x=32,y=32)
     
     self.__application_path_label=tk.Label(self,text="開くアプリケーションのパス(絶対パスのみ、未入力は既定のアプリに戻します)",font=("times",11,"bold"))
     self.__application_path_label.place(x=32,y=128)
     
     self.__application_path_entry=tk.Entry(self,width=60,font=("times",11))
     self.__application_path_entry.place(x=32,y=152)
     if len(current_file_path) != 0:
        self.__application_path_entry.insert(0,current_file_str)
     
     self.__application_path_choice_btn=tk.Button(self,text="参照",font=("times",11))
     self.__application_path_choice_btn.place(x=448,y=152)
     self.__application_path_choice_btn.bind("<Button-1>",self.application_path_choice)
     
     self.__path_delete_btn=tk.Button(self,text="入力取消(既定に戻す)",font=("times",11))
     self.__path_delete_btn.place(x=512,y=152)
     self.__path_delete_btn.bind("<Button-1>",self.application_path_clear)
     
     self.__ok_btn=tk.Button(self,text="決定",font=("times",11,"bold"))
     self.__ok_btn.place(x=320,y=184)
     self.__ok_btn.bind("<Button-1>",self.ok)
     
     self.__cancel_btn=tk.Button(self,text="キャンセル",font=("times",11))
     self.__cancel_btn.place(x=512,y=184)
     self.__cancel_btn.bind("<Button-1>",self.cancel)
     
     self.bind("<Escape>",self.cancel)
     self.bind("<Return>",self.ok)
     self.geometry("768x224")
  
   
   def application_path_choice(self,event=None):
     is_continue=True
     while is_continue:
       new_file_path=filedialog.askopenfilename(parent=self,title="ファイルを開くアプリケーションを選択",filetypes=[("実行形式ファイル", "*.exe;*.com")],initialdir="\\windows\\system32")
       if len(new_file_path) != 0:
         self.__application_path_entry.delete(0,tk.END)
         self.__application_path_entry.insert(0,new_file_path.replace(not_sep,os.sep))
         break
       is_continue=messagebox.askyesno("ファイル選択","ファイルの選択がなされませんでした。もう一度ファイルの選択をやり直しますか?")
   
   def application_path_clear(self,event=None):
     self.__application_path_entry.delete(0,tk.END)
   
   def validate(self):
     input_file_path=self.__application_path_entry.get().replace(not_sep,os.sep)
     if len(input_file_path) == 0:
       return True
     
     if not os.path.isfile(input_file_path):
       messagebox.showerror("エラー","ファイルを開くアプリケーションに、存在しないファイル、あるいは、フォルダが誤って指定されています。もう一度やり直してください。")
       return False
     
     if os.path.splitext(input_file_path)[1] not in (".exe",".com"):
       messagebox.showerror("エラー","ファイルを開くアプリケーションとして設定できるのは、exe形式あるいはcom形式のファイルのみです。拡張子を確認してもう一度やり直してください")
       return False
     
     if not os.path.isabs(input_file_path):
       messagebox.showerror("エラー","ファイルを開くアプリケーションのパスの指定は絶対パスで行ってください。")
       return False
     
     return True
 
   def apply(self):
     input_file_path=self.__application_path_entry.get().replace(not_sep,os.sep)
     #何も入力がなかったので、既定に戻すと設定されたとき
     if len(input_file_path) == 0:
       self.__class__.__file_config.remove_option(self.__class__.__section_name,self.__file_ext)
     else:
       self.__class__.__file_config[self.__class__.__section_name][self.__file_ext]=input_file_path
  
   def cancel(self,event=None):
     if event is not None:
       is_cancel_ok=messagebox.askyesno("設定は保存されていません","設定が保存されていませんが、このままキャンセルしてもよろしいでしょうか?(一度キャンセルすると、ここまで入力したものはに度と元に戻りません)")
       if not is_cancel_ok:
         return
     
     super().cancel()
   
   
   @classmethod
   def read_file_path_from_ini_file(cls):
     cls.__file_config.read(cls.__file_open_ini_file,encoding="utf-8")
     
     if cls.__section_name not in cls.__file_config:
       cls.__file_config[cls.__section_name]={}
   
   @classmethod
   def write_file_path_to_ini_file(cls):
     config_f=None
     try:
       config_f=open(cls.__file_open_ini_file,"w",encoding="utf-8")
       cls.__file_config.write(config_f)
     finally:
       if config_f is not None:
         config_f.close()
 
   @classmethod
   def get_open_application_file_path(cls,ext:str):
     if ext not in cls.__file_config[cls.__section_name]:
        return ""
     return cls.__file_config[cls.__section_name][ext]
     