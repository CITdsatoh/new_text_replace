#encoding:utf-8;
from tkinter import simpledialog,messagebox
import tkinter as tk
import subprocess



class SrcFileOpenDialog(simpledialog.Dialog):
  
  def __init__(self,parent,file_path_obj_index_dict:dict[str:int]):
    #こちらに直接,自作のファイル読み書きオブジェクト(IOFileManageクラスのインスタンス)を引き渡すのは、直接参照を引き渡すことになるので、バグのもとになるし、
    #だからと言っていちいちディープコピーするのは、情報が多いので荷が重い。
    #そして、全読み書きオブジェクトが、必ずしも元に戻せるとは限らないから、元に戻せるものだけこちらに引き渡して表示すればよいわけだし
    #ゆえに、ここでは、読み取り先ファイルのパス(文字列)がkey(str型)で、
    #その読み取り先ファイルパスに対するファイル読み書きオブジェクトが、呼び出し元(メインウィンドウ)にあるIOFileManageたちをまとめた配列(メインウィンドウのfile_managersフィールド)の何番目にあるのかをvalue(int型)
    #という辞書情報のみを引き渡す。(=オブジェクトに直接アクセスするのは、呼び出し元のみにする)
    #{"ファイルパス(str)":そのパスに対する読み書きオブジェクトの、メインウィンドウの管理配列(file_managers)の位置(int)}という辞書。
    self.__file_path_obj_index_dict=file_path_obj_index_dict
    
    self.__current_page_num=0
    self.__one_page_widgets=10
    
    self.__file_open_manage_widgets=[]
    
    all_widgets_num=len(self.__file_path_obj_index_dict.keys())
    self.__all_pages_num=int((all_widgets_num-1)/self.__one_page_widgets)+1
    
    super().__init__(parent)
  
  def buttonbox(self):
    self.__header_label=tk.Label(self,text="置換後に元に戻したいファイル選択",font=("serif",14,"bold"))
    self.__header_label.place(x=160,y=8)
    
    self.__explain_label=tk.Label(self,text="ここではファイル置換後、結果が意図するものと異なっていた時、置換前の状態にファイルを戻すことができます。\n元に戻したいファイル名が書かれたところの左にあるチェックを入れ、下の「元に戻す」ボタンを押してください。\nまた、元に戻す前に「ファイル内容を確認」ボタンから、現在のファイルの状態を確認することができます。\nその場合、必ずファイルを閉じてから、「元に戻す」ボタンを押すようにしてください。",font=("times",12))
    self.__explain_label.place(x=8,y=48)
    
    self.__check_label=tk.Label(self,text="元に戻す",font=("times",11,"bold"))
    self.__check_label.place(x=8,y=128)
    
    self.__file_path_head_label=tk.Label(self,text="元に戻したいファイルパス",font=("times",11,"bold"))
    self.__file_path_head_label.place(x=256,y=128)
    
    for one_file_path_str in self.__file_path_obj_index_dict.keys():
      one_file_open_manage_widget=SrcFileOpenManager(self,one_file_path_str)
      self.__file_open_manage_widgets.append(one_file_open_manage_widget)
      
      
   
    self.__page_back_btn=tk.Button(self,text="前ページへ戻る",font=("times",11))
    self.__page_back_btn.bind("<Button-1>",self.page_back)
    
    self.__page_advance_btn=tk.Button(self,text="次ページへ進む",font=("times",11))
    self.__page_advance_btn.bind("<Button-1>",self.page_advance)
    
    self.__current_page_label=tk.Label(self,text=f"1ページ/{self.__all_pages_num}ページ",font=("times",11))
    self.__current_page_label.place(x=224,y=512)
    
    if 1 < self.__all_pages_num:
      self.__page_advance_btn.place(x=576,y=512) 
      
    
    
    self.__revert_ok_btn=tk.Button(self,text="元に戻す",font=("times",11,"bold"))
    self.__revert_ok_btn.place(x=192,y=560)
    self.__revert_ok_btn.bind("<Button-1>",self.ok)
    
    self.__revert_cancel_btn=tk.Button(self,text="キャンセル",font=("times",11))
    self.__revert_cancel_btn.place(x=384,y=560)
    self.__revert_cancel_btn.bind("<Button-1>",self.cancel)
     
    self.__all_check_btn=tk.Button(self,text="すべて選択(チェックを入れる)",font=("times",11))
    self.__all_check_btn.place(x=32,y=608)
    self.__all_check_btn.bind("<Button-1>",self.all_check)
    
    self.__all_remove_check_btn=tk.Button(self,text="すべて選択解除(チェックを外す)",font=("times",11))
    self.__all_remove_check_btn.place(x=320,y=608)
    self.__all_remove_check_btn.bind("<Button-1>",self.all_remove_check)
    
    
    self.bind("<Return>",self.ok)
    self.bind("<Escape>",self.cancel)
    
    self.page_widgets_place(0)
    
    self.geometry("896x664")
  
  
  #開いたファイルすべてを閉じたかどうかを確認し、一つでも閉じていないものがあればFalseを返し、ダイアログを閉じられないようにする
  def is_ok_close_dialog(self):
    for one_file_open_manage_widget in self.__file_open_manage_widgets:
       if one_file_open_manage_widget.is_current_file_opened():
         return False
    return True
  
  
  def cancel(self,event=None):
    if self.result is None:
      if not self.is_ok_close_dialog():
        messagebox.showerror("ダイアログを閉じることはできません","元に戻そうとしているファイルが開かれているので、ダイアログを閉じることはできません。必ず、開いたファイルはすべて閉じてから、ダイアログを閉じるようにしてください")
        return
    
    super().cancel()
  
  def validate(self):
     if not self.is_ok_close_dialog():
       messagebox.showerror("エラー","元に戻そうとしているファイルのうち、現在開かれたままのものがあるので、このままでは元に戻すことができません。必ず、開いたファイルをすべて閉じてから、再度「元に戻す」ボタンを押してみてください")
       return False
     
     #結局は元に戻す処理自体は、呼び出し元(メインウィンドウ)で行うので、ここでは、「元に戻す」と選択された(チェックがついた)、読み書きオブジェクトの、メインウィンドウの管理配列(file_managers)の位置(int)を入れておく
     chosen_revert_file_path_indexs=[]
     for one_file_open_manage_widget in self.__file_open_manage_widgets:
        if one_file_open_manage_widget.get_choice_whether_to_revert():
          src_file_path=one_file_open_manage_widget.src_file_abs_path
          #呼び出し元の管理配列のどこのインデックスかを参照
          this_file_index_in_file_managers=self.__file_path_obj_index_dict[src_file_path]
          chosen_revert_file_path_indexs.append(this_file_index_in_file_managers)
     
     if len(chosen_revert_file_path_indexs) == 0:
       messagebox.showerror("エラー","現在、元に戻すファイルが1つも選択されておりません。必ず、元に戻す場合は1つ以上選択してください。なお、元に戻すのをやめる場合は、「キャンセル」ボタンか右上の「×」ボタンを押してください")
       return False
     
     self.result=chosen_revert_file_path_indexs[:]
          
     return True
  
  
  def all_check(self,event=None):
    for one_file_open_manage_widget in self.__file_open_manage_widgets:
       one_file_open_manage_widget.set_choice_whether_to_revert(True)
  
  def all_remove_check(self,event=None):
    for one_file_open_manage_widget in self.__file_open_manage_widgets:
       one_file_open_manage_widget.set_choice_whether_to_revert(False)
  
  
  def page_back(self,event=None):
    if self.__current_page_num <= 0:
      return
    
    self.page_widgets_place_forget()
    self.__current_page_num -= 1
    self.page_widgets_place()
    self.__current_page_label["text"]=f"{self.__current_page_num+1}ページ/{self.__all_pages_num}ページ"
    
    if self.__current_page_num == self.__all_pages_num-2:
       self.__page_advance_btn.place(x=576,y=512) 
    if self.__current_page_num == 0:
       self.__page_back_btn.place_forget()
  
  def page_advance(self,event=None):
    if self.__all_pages_num-1 <= self.__current_page_num:
      return
    
    self.page_widgets_place_forget()
    self.__current_page_num += 1
    self.page_widgets_place()
    self.__current_page_label["text"]=f"{self.__current_page_num+1}ページ/{self.__all_pages_num}ページ"
    
    if self.__current_page_num == self.__all_pages_num-1:
       self.__page_advance_btn.place_forget() 
    if self.__current_page_num == 1:
       self.__page_back_btn.place(x=32,y=512)
  
  
  def page_widgets_place(self,page_num:int=None):
    if page_num is None:
      page_num=self.__current_page_num
    
    page_start_widget_num=page_num*self.__one_page_widgets
    one_page_widget_num=0
    
    for i in range(page_start_widget_num,page_start_widget_num+self.__one_page_widgets):
       if len(self.__file_open_manage_widgets) <= i:
          break
       self.__file_open_manage_widgets[i].place(x=0,y=176+(one_page_widget_num*32))
       one_page_widget_num += 1
  
  def page_widgets_place_forget(self,page_num:int=None):
    if page_num is None:
      page_num=self.__current_page_num
    
    page_start_widget_num=page_num*self.__one_page_widgets
    
    for i in range(page_start_widget_num,page_start_widget_num+self.__one_page_widgets):
       if len(self.__file_open_manage_widgets) <= i:
          break
       self.__file_open_manage_widgets[i].place_forget()





class SrcFileOpenManager(tk.Frame):

  def __init__(self,master,src_file_abs_path:str,w=896,h=32):
    super().__init__(master,width=w,height=h)
    self.__src_file_abs_path=src_file_abs_path
    
    self.__revert_file_widget_var=tk.BooleanVar()
    self.__revert_file_checkbox=tk.Checkbutton(self,text="",font=("times",11),variable=self.__revert_file_widget_var)
    self.__revert_file_checkbox.place(x=8,y=0)
    
    self.__revert_file_path_disps=tk.Entry(self,width=75,readonlybackground="#ffffff",relief=tk.SOLID,borderwidth=1,font=("times",12,"bold"))
    self.__revert_file_path_disps.insert(0,self.__src_file_abs_path)
    self.__revert_file_path_disps["state"]="readonly"
    self.__revert_file_path_disps.place(x=48,y=0)
    
    #self.__revert_file_path_disps_scroll=tk.Scrollbar(self,orient=tk.HORIZONTAL,command=self.__revert_file_path_disps.xview)
    #self.__revert_file_path_disps["xscrollcommand"]=self.__revert_file_path_disps_scroll.set
    #self.__revert_file_path_disps.place(x=48,y=80)
    
    self.__file_open_btn=tk.Button(self,text="ファイル内容を確認",font=("times",11,"bold"))
    self.__file_open_btn.place(x=656,y=0)
    self.__file_open_btn.bind("<Button-1>",self.src_file_open)
    
    #ファイルを開くプロセス(=ファイルが閉じられているかを確認するために用いる)
    self.__file_open_proc=None
  
  def get_choice_whether_to_revert(self):
    return self.__revert_file_widget_var.get()
    
  #一気に「全チェック」を入れたり、外されたりしたときに用いる
  def set_choice_whether_to_revert(self,new_state:bool):
    self.__revert_file_widget_var.set(new_state)
  
  #実際にファイルを開く
  def src_file_open(self,event=None):
    self.__file_open_proc=subprocess.Popen([self.__src_file_abs_path],shell=True)
  
  #現在、ファイルが開かれているかどうかを返却する(=全ファイルが閉じられるまで、ダイアログを閉じれないようにするため)
  def is_current_file_opened(self):
    if self.__file_open_proc is None:
      return False
    
    return self.__file_open_proc.poll() is None
  
  #実際に開くファイルパス(=後でどのファイルパスが元に戻される対象なのかを比較判定するため、外に出しておく必要がある)
  @property
  def src_file_abs_path(self):
    return self.__src_file_abs_path