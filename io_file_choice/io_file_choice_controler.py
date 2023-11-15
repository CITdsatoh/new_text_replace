#encoding:utf-8;

import tkinter as tk
from io_file_choice.io_file_choice_widgets.file_path_setting_dialog import FilePathSettingDialog
from tkinter import simpledialog,messagebox,scrolledtext


class IOFileChoiceControler(tk.Frame):

  def __init__(self,master,w=768,h=192):
    
    super().__init__(master,width=w,height=h,relief=tk.SOLID,borderwidth=3)
    
    self.__master=master
    
    #今までの入力内容を保持
    self.__input_information=[None for i in range(30)]
    
    self.__head_label=tk.Label(self,text="テキストを置換する対象のファイル選択",font=("serif",14,"bold"))
    self.__head_label.place(x=8,y=0)
    
    self.__short_explaination_label=tk.Label(self,text="上記で実際に設定した置換を行いたいファイルを選択してください。最大30ファイルまで可能です",font=("times",11))
    self.__short_explaination_label.place(x=48,y=32)
    
    self.__file_choice_btn=tk.Button(self,text="ファイル選択",font=("times",11,"bold"))
    self.__file_choice_btn.place(x=224,y=96)
    self.__file_choice_btn.bind("<Button-1>",self.file_choice)
    
    self.__disp_current_choice_status_btn=tk.Button(self,text="現在のファイル選択状況確認",font=("times",11))
    self.__disp_current_choice_status_btn.place(x=384,y=96)
    self.__disp_current_choice_status_btn.bind("<Button-1>",self.disp_current_choice_status)
    
    self.__all_reset_choice_btn=tk.Button(self,text="すべてのファイル選択設定消去",font=("times",11))
    self.__all_reset_choice_btn.place(x=256,y=128)
    self.__all_reset_choice_btn.bind("<Button-1>",self.all_reset_file_choice)
    
  
  def file_choice(self,event=None):
    setting_dialog=FilePathSettingDialog(self.__master,tuple(self.__input_information))
    setting_result=setting_dialog.result
    if setting_result is not None:
      self.__input_information=setting_result
  
  #実際に置換する直前に、入力情報をもとにどのファイルに書き込むかの情報オブジェクトをメインウィンドウに返す
  def get_file_io_objs(self):
     file_managers=[]
     for one_input_information in self.__input_information:
       if one_input_information is None:
          continue
       new_file_manager_obj=one_input_information.get_file_io_manage_obj()
       if new_file_manager_obj is not None:
         file_managers.append(new_file_manager_obj)
     
     return file_managers
  
  
  #これまで、どんなものが入力欄に入っているのかを確認するためのダイアログを表示
  def disp_current_choice_status(self,event=None):
    each_choice_status_strs=[]
    for i,one_input_information in enumerate(self.__input_information):
        one_information_str=one_input_information and f"{one_input_information}" or "未設定"
        one_choice_status_str=f"その{i+1}:{one_information_str}"
        #左揃えにしたいので、2行目以降は、行頭を合わせるために,そのi+1分空白を入れる
        header_bytes_num=(len(f"その{i+1}:".encode("utf-8")))
        line_head_pads="\u0020"*header_bytes_num
        one_choice_status_str=one_choice_status_str.replace("\n",f"\n{line_head_pads}")
        each_choice_status_strs.append(one_choice_status_str)
        
    status_dialog=IOFileChoiceStatusDialog(self.__master,tuple(each_choice_status_strs))
  
  
  def all_reset_file_choice(self,event=None):
    if event is not None:
       is_all_reset_ok=messagebox.askyesno("今までの登録全削除","これまでに選択・入力したファイル情報(置換したいファイルパス・書き込み先ファイルパスすべて)を30入力欄分すべて削除してもよろしいでしょうか?(削除後は二度と元に戻すことはできません。そして、置換後に置換結果が意図したものと異なっており、ファイルのテキストを置換前の状態に戻したいものがある場合、それもできなくなります。)")
       if not is_all_reset_ok:
          return
    self.__input_information=[None for i in range(30)]
    messagebox.showinfo("削除完了","今まで登録・入力したファイル情報がすべて削除されました")
    

class IOFileChoiceStatusDialog(simpledialog.Dialog):

   def __init__(self,parent,status_info_strs:tuple[str],title:str="現在選択されているファイル"):
     self.__status_info_strs=status_info_strs
     super().__init__(parent,title)
   
   def buttonbox(self):
     self.__header_label=tk.Label(self,text="現在選択・入力されている置換ファイル一覧",font=("serif",14,"bold"))
     self.__header_label.place(x=128,y=0)
     
     self.__explain_label=tk.Label(self,text="以下が現在されている置換ファイルです",font=("times",12))
     self.__explain_label.place(x=192,y=64)
     
     self.__chosen_files_disp_textarea=scrolledtext.ScrolledText(self,height=30,width=100,relief=tk.SOLID,borderwidth=2,font=("times",11,"bold"))   
     self.__chosen_files_disp_textarea.insert("1.0","\n\n".join(self.__status_info_strs))
     self.__chosen_files_disp_textarea.place(x=32,y=96)
     self.__chosen_files_disp_textarea["state"]="disabled"
     
     self.__exit_btn=tk.Button(self,text="了解",font=("times",11,"bold"))
     self.__exit_btn.bind("<Button-1>",self.ok)
     self.__exit_btn.place(x=256,y=624)
     
     self.bind("<Return>",self.ok)
     self.bind("<Escape>",self.cancel)
     self.geometry("896x656")
     
     
     
       
       
       
  
       