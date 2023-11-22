#encoding:utf-8;

import tkinter as tk
from replace_choice.replace_choice_widgets.replace_text_input_dialog import ReplaceTextInputDialog
from replace_choice.text_replace.str_replacer import ReplaceInformation
from tkinter import simpledialog,messagebox,scrolledtext


class ReplaceChoiceControler(tk.Frame):
  
  def __init__(self,master,w=768,h=256):
   
   super().__init__(master,width=w,height=h,relief=tk.SOLID,borderwidth=3)
   self.__master=master
   
   #今まで入力した置換内容の保持
   self.__all_inputs_data=[None for i in range(20)]
   
   self.__head_label=tk.Label(self,text="実際に置換したいテキストを入力・設定",font=("serif",14,"bold"))
   self.__head_label.place(x=8,y=0)
   
   self.__explaination_label=tk.Label(self,text="ファイル内のどのテキストをどんなものに置換したいかを以下のボタンを押して、入力してください。\n最大20テキスト分の置換ができます。",font=("times",11))
   self.__explaination_label.place(x=48,y=32)
   
   self.__replace_choice_btn=tk.Button(self,text="テキストを入力・設定",font=("times",11,"bold"))
   self.__replace_choice_btn.place(x=192,y=80)
   self.__replace_choice_btn.bind("<Button-1>",self.replace_text_choice)
   
   self.__disp_current_choice_status_btn=tk.Button(self,text="現在のテキスト入力状況確認",font=("times",11))
   self.__disp_current_choice_status_btn.place(x=384,y=80)
   self.__disp_current_choice_status_btn.bind("<Button-1>",self.disp_current_choice_status)
    
   self.__all_reset_choice_btn=tk.Button(self,text="すべてのテキスト入力設定消去",font=("times",11))
   self.__all_reset_choice_btn.place(x=256,y=112)
   self.__all_reset_choice_btn.bind("<Button-1>",self.all_reset_replace_choice)
   
   #「同時置換モード(1度置換モード)」(=1度だけ置換。置換された結果をさらに置換して、別の結果になるのを防ぐモード)が有効かどうか
   self.__is_only_once_replace_widget_var=tk.BooleanVar(self)
   self.__is_only_once_replace_mode_checkbox=tk.Checkbutton(self,text="同時置換(1度置換)モード(一度、別の言葉から置換された結果をさらに置換して別の結果になることを\n防ぐモード）を有効にする",font=("times",11),variable=self.__is_only_once_replace_widget_var)
   self.__is_only_once_replace_mode_checkbox.place(x=8,y=176)
   
   self.__only_once_mode_explain_dialog_btn=tk.Button(self,text="詳しく",font=("times",11))
   self.__only_once_mode_explain_dialog_btn.place(x=512,y=200)
   self.__only_once_mode_explain_dialog_btn.bind("<Button-1>",self.disp_only_once_mode_explain_dialog)
   
 
  def replace_text_choice(self,event=None):
    setting_dialog=ReplaceTextInputDialog(self.__master,tuple(self.__all_inputs_data))
    setting_result=setting_dialog.result
    if setting_result is not None:
      self.__all_inputs_data=setting_result
      #メインウィンドウのほうに、変化が起きたことを伝える
      self.__master.any_information_changed()
  
  #置換直前に、入力データから実際に置換するための情報が入っているオブジェクト群を得る
  def get_replace_information_objs(self):
    replacers_information=[]
    for one_input_data in self.__all_inputs_data:
       if one_input_data is None:
          continue
       replace_information_obj=one_input_data.get_replace_information_obj()
       if replace_information_obj is not None:
         replacers_information.append(replace_information_obj)
   
    return replacers_information
  
  
  #同時置換モードが有効かどうか(=これに応じて、メインウィンドウで、同時置換用の処理と通常の処理を分岐する)
  def is_only_once_replace(self):
    return  self.__is_only_once_replace_widget_var.get()
  
  #現在入力されているものを表示するダイアログ
  def disp_current_choice_status(self,event=None):
    disp_each_input_strs=self.get_current_choice_strs_list(True)
    dialog=ReplaceTextChoiceStatusDialog(self.__master,tuple(disp_each_input_strs))
  
  def disp_only_once_mode_explain_dialog(self,event=None):
    dialog=OnlyOnceReplaceModeExplainDialog(self.__master)
  
  
  #現在の置換テキストの入力内容の返却(返却値はリストで各要素に入力文字列を入れる)
  #第一引数は、ダイアログ表示の際に見やすくするための行頭にインデントを入れるかどうかを指定
  def get_current_choice_strs_list(self,add_indentation:bool=False):
    each_input_strs=[]
    for i,one_input_data in enumerate(self.__all_inputs_data):
      one_input_str_header=f"その{i+1}:"
      one_input_str_body=one_input_data and f"{one_input_data}" or "未入力"
      if add_indentation:
       #各情報は改行して表示されるので、見やすくするため、one_input_str_headerのバイト数分だけ改行後空白を入れる
       one_line_pads="\u0020"*len(one_input_str_header.encode("utf-8"))
       one_input_str_body=one_input_str_body.replace("\n",f"\n{one_line_pads}")
       
      one_input_whole_str=f"{one_input_str_header}{one_input_str_body}"
      each_input_strs.append(one_input_whole_str)
    
    return each_input_strs
    
  
  def all_reset_replace_choice(self,event=None):
    if event is not None:
       is_all_reset_ok=messagebox.askyesno("今までの登録全削除","今まで選択・入力した置換テキスト情報のすべて(置換元文字列・表現、置換先文字列、置換モード、全置換元文字列・表現に対する登録された全NGワード)を20入力欄分削除してもよろしいでしょうか?(削除後は二度と元に戻すことはできません)")
       if not is_all_reset_ok:
          return
    self.__all_inputs_data=[None for i in range(20)]
    messagebox.showinfo("削除完了","今まで登録・入力した置換テキスト情報がすべて削除されました")
    self.__is_only_once_replace_widget_var.set(False)
  
  


class ReplaceTextChoiceStatusDialog(simpledialog.Dialog):

   def __init__(self,parent,disp_strs:tuple[str],title:str="現在入力されている置換ワード"):
     self.__disp_strs=list(disp_strs)
     super().__init__(parent,title)
   
   def buttonbox(self):
     self.__header_label=tk.Label(self,text="現在入力・設定されている置換ワード",font=("serif",14,"bold"))
     self.__header_label.place(x=128,y=0)
     
     self.__explain_label=tk.Label(self,text="以下が現在入力されている置換ワードです",font=("times",12))
     self.__explain_label.place(x=192,y=64)
     
     self.__chosen_texts_disp_textarea=scrolledtext.ScrolledText(self,height=30,width=100,relief=tk.SOLID,borderwidth=2,font=("times",11,"bold"))   
     self.__chosen_texts_disp_textarea.insert("1.0","\n\n".join(self.__disp_strs))
     self.__chosen_texts_disp_textarea.place(x=32,y=96)
     self.__chosen_texts_disp_textarea["state"]="disabled"
     
     self.__exit_btn=tk.Button(self,text="了解",font=("times",11,"bold"))
     self.__exit_btn.bind("<Button-1>",self.ok)
     self.__exit_btn.place(x=256,y=624)
     
     self.bind("<Return>",self.ok)
     self.bind("<Escape>",self.cancel)
     self.geometry("896x656")



class OnlyOnceReplaceModeExplainDialog(simpledialog.Dialog):

   def __init__(self,parent,title:str="同時置換(1度置換)モードとは?"): 
     super().__init__(parent,title)
   
   def buttonbox(self):
     self.__header_label=tk.Label(self,text="同時置換(1度置換)モードとは?",font=("serif",16,"bold"))
     self.__header_label.place(x=256,y=8)
     
     self.__explain_label_former=tk.Label(self,text="ある別の文字列から置換された文字列を、再度別の文字列へと置換しないようにするモードです.\n例えば、以下のような場合において、今までのリーダーと副リーダーを交換したくなった場合を考えましょう。",font=("times",12))
     self.__explain_label_former.place(x=16,y=48)
     
     self.__example_replace_before_model=tk.Label(self,text="リーダー:山田太郎\n副リーダー：鈴木一郎",font=("times",12,"bold"),bg="#d9d9d9")
     self.__example_replace_before_model.place(x=48,y=96)
     
     self.__example_arrow_model=tk.Label(self,text="こうしたい\n→→→",font=("times",12))
     self.__example_arrow_model.place(x=288,y=96)
     
     self.__example_replace_after_model=tk.Label(self,text="リーダー:鈴木一郎\n副リーダー：山田太郎",font=("times",12,"bold"),bg="#d9d9d9")
     self.__example_replace_after_model.place(x=416,y=96)
     
     self.__explain_label_middle=tk.Label(self,text="このような場合、「山田太郎」という文字列を「鈴木一郎」という文字列に置換し、「鈴木一郎」という文字列を「山田太郎」という\n文字列に置換することを考えるでしょう。しかし、その結果は、以下の通りになります",font=("times",12))
     self.__explain_label_middle.place(x=16,y=160)
     
     self.__example_replace_before_real=tk.Label(self,text="リーダー:山田太郎\n副リーダー：鈴木一郎",font=("times",12,"bold"),bg="#d9d9d9")
     self.__example_replace_before_real.place(x=48,y=224)
     
     self.__example_arrow_model_real=tk.Label(self,text="従来の置換結果\n→→→",font=("times",12))
     self.__example_arrow_model_real.place(x=288,y=224)
     
     self.__example_replace_after_model=tk.Label(self,text="リーダー:山田太郎\n副リーダー：山田太郎",font=("times",12,"bold"),bg="#d9d9d9")
     self.__example_replace_after_model.place(x=416,y=224)
     
     self.__explain_label_latter=tk.Label(self,text="というように両方とも、「山田太郎」になってしまいます。というのは、まず、「山田太郎」が「鈴木一郎」に置き換わりますが、\nこの時点で「鈴木一郎」という文字列が、元から「鈴木一郎」だったところと、「山田太郎」から置換されて「鈴木一郎」になったところと、\n2箇所存在することになります。この後、従来の場合、「鈴木一郎」という文字列が元からあったかどうかに関係なく2箇所とも「山田太郎」に\n置換されてしまい、結果このようになります。",font=("times",12))
     self.__explain_label_latter.place(x=16,y=288)
     
     self.__explain_label_last=tk.Label(self,text="ですが、同時置換(1度置換)モードを利用することによって、1度置換された結果「鈴木一郎」となった文字列は2度と他のものに置換されなくなり、\n以上のような文字列の交換が可能になります。これ以外にも、特に一度置換したものが置換対象になりやすいワイルドカード・正規表現を用いた\n置換を多用する際に使用することを推奨いたします。ただし、このモードを使用する場合、置換速度が従来に比べやや遅くなる場合が\nございますので、本来不必要な場合に、「何となく不安だから、念のために」という理由で使用することは推奨いたしません。",font=("times",12))
     self.__explain_label_last.place(x=16,y=384)
     
     self.__exit_btn=tk.Button(self,text="了解",font=("times",12,"bold"))
     self.__exit_btn.place(x=384,y=480)
     self.__exit_btn.bind("<Button-1>",self.ok)
     
     self.bind("<Escape>",self.cancel)
     self.bind("<Return>",self.ok)
     
     self.geometry("1088x512")
     
     
   
   