#encoding:utf-8;

import tkinter as tk
from replace_choice.replace_choice_widgets.replace_text_input_dialog import ReplaceTextInputDialog
from replace_choice.text_replace.str_replacer import ReplaceInformation
import re


class FileTextReplaceMainWindow(tk.Tk):

   def __init__(self):
     super().__init__()
     self.title("ファイルテキスト一括置換")
     
     self.__all_inputs_data=[None for i in range(20)]
     
     self.__replacers_information=[]
     
     self.geometry("1200x1000")
     
     self.__exe_button=tk.Button(self,text="実行",font=("times",15))
     self.__exe_button.place(x=256,y=100)
     self.__exe_button.bind("<Button-1>",self.execute)
     
     self.__exit_button=tk.Button(self,text="終了",font=("times",15))
     self.__exit_button.place(x=448,y=100)
     self.__exit_button.bind("<Button-1>",self.exit)
     
     self.bind("<Return>",self.execute)
     self.bind("<Escape>",self.exit)
     

     self.mainloop()
        
   def execute(self,event=None):
     dialog=ReplaceTextInputDialog(self,tuple(self.__all_inputs_data))
     new_result=dialog.result
     if new_result is not None:
       self.__all_inputs_data=new_result
     
     self.__replacers_information=[]
     
     f=None
     try:
       f=open("replace_result.txt","w",encoding="utf-8")
       for i,one_input_data in enumerate(self.__all_inputs_data):
         print("入力内容:その",(i+1),one_input_data,file=f)
         if one_input_data is None:
            continue
         replacer_obj=one_input_data.get_replace_information_obj()
         print("置換内容取得:その",(i+1),replacer_obj,file=f)
         if replacer_obj is not None:
            self.__replacers_information.append(replacer_obj)
     finally:
        if f is not None:
           f.close()
       
     self.file_text_replace()
   
   def file_text_replace(self):
     file_contents_before=[]
     with open("replace_before.txt",encoding="utf-8") as f:
        file_contents_before=f.readlines()
        f.close()
     
     file_contents_before_no_br=[one_line.strip("\n") for one_line in file_contents_before]
     
     file_contents_after=[]
     
     #各1行に対して、1つ目の置換→2つ目の置換→3つ目の置換→・・というように行って、最後の置換まで行ったら、今度はその次の行に対して同じようにする
     
     #1行ずつ取り出す
     for one_line_before_replace in file_contents_before_no_br:
       if len(one_line_before_replace) ==  0:
          file_contents_after.append(one_line_before_replace)
          continue
       
       #ここに、設定された全組み合わせの置換終了後の文字列を格納
       #まだ置換をしていないので、置換前の1行分の文字列をここに入れる
       one_line_after_replace=one_line_before_replace
       
       #一度置換モード(以前置換したものを別のものに再置換しないようにするモード)では、置換を行うとき,置換された結果としてその文字列になったことを示すため
       #内部的に、「設定された置換後文字列の前後両方に、改行コードを入れたもの」に置換する。
       #(これで、前後に改行コードがあるものは、元から存在した文字列でなく、置換した結果生じたものだとわかる)
       #それでも、部分一致の場合、前後に改行コードがあろうがなかろうが、その語句に一致してしまうので、
       #NGワードとして、ユーザーが指定したものとは別に「置換後文字列の前後に改行コードがついたもの」を指定することによって、
       #「置換された結果の文字列」であるものは置換されなくなる
       ng_words_tmp=[]
       
       #各設定された置換を1つずつこなす
       for one_replacer in self.__replacers_information:
         print(one_replacer)
         #「置換後文字列の前後に改行コードがついた文字列」が置換されないように、NGワードとして、ユーザーが指定したものとは別にここで指定する
         ng_words_tmp.append(one_replacer.escaped_replace_after_pattern_in_only_once_replace_mode)
         replace_obj=one_replacer.get_replace_obj_in_only_once_replace_mode(tuple(ng_words_tmp))
         one_line_after_replace=replace_obj.replace(one_line_after_replace)
       
       #置換終了後、内部的に前後に改行コードを入れたので、改行コードを取り除く
       one_line_after_replace=re.sub("\n(.*)\n","\\1",one_line_after_replace)
       #置換結果、その行が空行になった場合、空行として残さず詰める
       if len(one_line_after_replace) != 0:
         file_contents_after.append(one_line_after_replace)
    
     with open("replace_after.txt","w",encoding="utf-8") as f:
       for one_line_after_replace in file_contents_after:
          f.write(one_line_after_replace+"\n")
       
       f.close()
   
   def exit(self,event=None):
     self.destroy() 
   
   def __repr__(self):
      return self.__class__.__name__

if __name__ == "__main__":
  a=FileTextReplaceMainWindow()     