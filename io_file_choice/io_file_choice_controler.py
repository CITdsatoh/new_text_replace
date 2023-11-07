#encoding:utf-8;

import tkinter as tk
from io_file_choice.io_file_choice_widgets.file_path_setting_dialog import FilePathSettingDialog
from tkinter import simpledialog,messagebox


class IOFileChoiceControler(tk.Frame):

  def __init__(self,master,w=944,h=256):
    
    super().__init__(master,width=w,height=h,relief=tk.SOLID,borderwidth=3)
    
    #今までの入力内容を保持
    self.__input_information=[None for i in range(30)]
    
    self.__head_label=tk.Label(self,text="テキストを置換する対象のファイル選択",font=("serif",12,"bold"))
    self.__head_label.place(x=8,y=0)
    
    self.__short_explaination_label=tk.Label(self,text="上記で実際に設定した置換を行いたいファイルを選択してください。最大30ファイルまで可能です",font=("times",10))
    self.__short_explaination_label.place(x=128,y=32)
    
    self.__file_choice_btn=tk.Button(self,text="ファイル選択",font=("times",11,"bold"))
    self.__file_choice_btn.place(x=128,y=96)
    self.__file_choice_btn.bind("<Button-1>",self.file_choice)
    
    self.__disp_current_choice_status_btn=tk.Button(self,text="現在のファイル選択状況確認",font=("times",11))
    self.__disp_current_choice_status_btn.place(x=256,y=96)
    self.__disp_current_choice_status_btn.bind("<Button-1>",self.disp_current_choice_status)
    
    self.__all_reset_choice_btn=tk.Button(self,text="すべてのファイル選択設定消去",font=("times",11))
    self.__all_reset_choice_btn.place(x=512,y=96)
    self.__all_reset_choice_btn.bind("<Button-1>",self.all_reset_file_choice)
  
  def file_choice(self,event=None):
    setting_dialog=FilePathSettingDialog(self,tuple(self.__input_information))
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
        each_choice_status_strs.append(one_choice_status_str)
        
    status_dialog=ChoiceStatusDialog(self,tuple(each_choice_status_strs))
  
  
  def all_reset_file_choice(self,event=None):
    if event is not None:
       is_all_reset_ok=messagebox.askyesno("今までの登録全削除","これまでに選択・入力したファイル情報(置換したいファイルパス・書き込み先ファイルパスすべて)を30入力欄分すべて削除してもよろしいでしょうか?(削除後は二度と元に戻すことはできません。そして、置換後に置換結果が意図したものと異なっており、ファイルのテキストを置換前の状態に戻したいものがある場合、それもできなくなります。)")
       if not is_all_reset_ok:
          return
    self.__input_information=[None for i in range(30)]
    messagebox.showinfo("削除完了","今まで登録・入力したファイル情報がすべて削除されました")
    
     
        


class ChoiceStatusDialog(simpledialog.Dialog):

   def __init__(self,parent,status_info_strs:tuple[str],title:str="現在選択されているファイル"):
     self.__status_info_strs=status_info_strs
     super().__init__(parent,title)
   
   def buttonbox(self):
     self.__header_label=tk.Label(self,text="現在選択・入力されているファイル",font=("serif",12,"bold"))
     self.__header_label.place(x=128,y=0)
     
     self.__status_labels=[]
     current_page_line_num=0
     self.__all_page_num=1
     one_page_labels=[]
     for i in range(0,len(self.__status_info_strs)):
       current_status_label=tk.Label(self,text=self.__status_info_strs[i],font=("times",10),relief=tk.SOLID,borderwidth=2)
       current_status_label_line_num=self.__status_info_strs[i].count("\n")+1
       one_page_labels.append(current_status_label)
       current_page_line_num += current_status_label_line_num
       #1ページで20行を超えたら次ページにする
       if 20 <  current_page_line_num:
          self.__status_labels.append(one_page_labels)
          self.__all_page_num += 1
          one_page_labels=[]
          current_page_line_num=0
     else:
        if len(one_page_labels) != 0:
          self.__status_labels.append(one_page_labels)
     
     self.__current_page_num=0
     
     self.page_label_place(0)
     self.__page_back_btn=tk.Button(self,text="前ページへ戻る",font=("times",11))
     self.__page_back_btn.bind("<Button-1>",self.page_back)
     
     self.__page_advance_btn=tk.Button(self,text="次ページへ進む",font=("times",11))
     if 1 < self.__all_page_num:
       self.__page_advance_btn.place(x=384,y=512)
       
     self.__page_advance_btn.bind("<Button-1>",self.page_advance)
     
     self.__exit_btn=tk.Button(self,text="了解",font=("times",11,"bold"))
     self.__exit_btn.place(x=256,y=544)
     self.__exit_btn.bind("<Button-1>",self.ok)
     
     self.bind("<Return>",self.ok)
     self.bind("<Escape>",self.cancel)
     self.geometry("648x512")
   
   
   def page_back(self,event=None):
     if self.__current_page_num <= 0:
       return 
     
     self.page_label_forget()
     self.__current_page_num -= 1
     self.page_label_place()
     
     if self.__current_page_num == self.__all_page_num-2:
       self.__page_advance_btn.place(x=384,y=512)
     if self.__current_page_num == 0:
       self.__page_back_btn.place_forget()
   
   
   
   def page_advance(self,event=None):
     if self.__all_page_num-1 <= self.__current_page_num:
       return
     
     self.page_label_forget()
     self.__current_page_num += 1
     self.page_label_place()
     
     if self.__current_page_num == self.__all_page_num-1:
       self.__page_advance_btn.place_forget()
     if self.__current_page_num == 1:
       self.__page_back_btn.place(x=64,y=512)
   
   def page_label_place(self,page_num:int=None):
     if page_num is None:
        page_num=self.__current_page_num
     
     if page_num < 0 or self.__all_page_num <= page_num:
        return 
     
     current_height=32
     for one_label in self.__status_labels[page_num]:
       one_label.place(x=16,y=current_height)
       label_line_num=one_label["text"].count("\n")+1
       height_diff=24*label_line_num
       current_height += height_diff
       
   def page_label_forget(self,page_num:int=None):
     if page_num is None:
        page_num=self.__current_page_num
     
     if page_num < 0 or self.__all_page_num <= page_num:
        return 
     
     current_height=32
     for one_label in self.__status_labels[page_num]:
       one_label.place_forget()
       
       
       
       
  
       