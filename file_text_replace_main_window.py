#encoding:utf-8;

from io_file_choice.io_file_choice_controler import IOFileChoiceControler
from replace_choice.replace_choice_controler import ReplaceChoiceControler
from file_disp_manage.src_file_open import SrcFileOpenDialog
from file_disp_manage.file_open_setting import FileOpenApplicationSettingDialog
from io_file_choice.io_manage.file_io_manage import FileRevertResultStatusCodes

import tkinter as tk
from tkinter import messagebox

class FileTextReplaceMainWindow(tk.Tk):
  
  def __init__(self):
    super().__init__()
    FileOpenApplicationSettingDialog.read_file_path_from_ini_file()
    
    self.__main_header=tk.Label(self,text="ファイルテキスト一括置換アプリ",font=("serif",18,"bold"))
    self.__main_header.place(x=256,y=0)
    
    explaination_str="本アプリは、選択したファイル内に存在する、指定したテキストを別の指定したテキストにすべて一括で置換することができるアプリです。\n置換したいテキストの指定はすぐ下にある「実際に置換したいテキストを入力・設定」より、\nテキストを置換するファイルの選択は、そのさらに下にある「テキストを置換する対象のファイル選択」よりお願いします。"
    self.__main_explaination_label=tk.Label(self,text=explaination_str,font=("serif",12,"bold"))
    self.__main_explaination_label.place(x=0,y=48)
    
    self.__replace_text_control=ReplaceChoiceControler(self)
    self.__replace_text_control.place(x=96,y=144)
    
    self.__replace_file_control=IOFileChoiceControler(self)
    self.__replace_file_control.place(x=96,y=416)
    
    self.__replace_exe_btn=tk.Button(self,text="置換実行",font=("times",11,"bold"))
    self.__replace_exe_btn.place(x=352,y=624)
    self.__replace_exe_btn.bind("<Button-1>",self.replace_execute)
    
    
    self.__revert_text_btn=tk.Button(self,text="置換内容を元に戻す",font=("times",11))
    self.__revert_text_btn.place(x=448,y=624)
    self.__revert_text_btn.place_forget()
    self.__revert_text_btn.bind("<Button-1>",self.revert_replaced_text)
    
    self.__exit_btn=tk.Button(self,text="終了",font=("times",11))
    self.__exit_btn.place(x=624,y=624)
    self.__exit_btn.bind("<Button-1>",self.exit)
    
    
    #実際の置換用オブジェクト
    self.__replacers_information=[]
    #実際のファイル読み書きオブジェクト
    self.__file_managers=[]
    
    #元に戻せるファイルと、そのfile_managers内のインデックスをペアとしたdict
    self.__revertable_file_and_index_in_file_managers={}
    
    #置換終了後に内容を変更せず、ボタンが連続で押されていた場合、前回の置換結果からそのまま連続で置換してよいかをメッセージボックスで表示することで警告したい
    #変わってないかどうかを保持するフラグ
    #初期状態は、今後必ず変化があるので、Trueにしておく
    self.__has_any_setting_changed_after_previous_replacement=True
    
    self.title("ファイルテキスト一括置換アプリケーション")
    
    
    self.bind("<Escape>",self.exit)
    self.protocol("<WM_DELETE_WINDOW>",self.exit)
    self.geometry("1024x768")
  
  def replace_execute(self,event=None):
  
    if not self.__has_any_setting_changed_after_previous_replacement:
      is_double_replace_ok=messagebox.askyesno("再置換してもよろしいですか?","前回置換した際より、置換したいテキスト内容、並びに、置換したいファイル内容の変更が全くありませんが、そのまま再置換してもよろしいでしょうか?(上書きを指定している場合、前回置換した結果をさらに置換することになります。ちなみに同時置換(1度置換)モードは、同じ回の置換にのみ有効なので、これが有効になっているかどうかは今は関係ありません。)")
      if not is_double_replace_ok:
         return
    
    #new_replacers_information=self.__replace_text_control.get_replace_information_objs()
    #if len(new_replacers_information) == 0:
      #messagebox.showerror("エラー","置換したいテキスト内容が1つも指定されていないようです。最低1つ以上置換したいテキストを指定してください")
      #return
    
    new_file_managers=self.__replace_file_control.get_file_io_objs()
    if len(new_file_managers) == 0:
      messagebox.showerror("エラー","テキストを置換するファイルが1つも指定されていないようです。最低1つ以上置換するファイルを指定してください")
      return
      
      
    #self.__replacers_information=new_replacers_information
    self.__file_managers=new_file_managers
    
    #置換処理を書く
    #for one_file_manager in self.__file_managers:
     # file_contents_before_replaced=one_file_manage.read_file_all_lines()
      #if file_contents_before_replaced is None:
       #  continue
      #file_contents_after_replaced=self.replace(file_contents_before_replaced)
      #one_file_manage.write_file_after_replaced(file_contents_after_replaced)
    
    #一度置換をし終わったので、次の状態変化(設定ウィンドウが閉じられる)までは、False(今とまだ変わっていない状態)に戻す
    self.__has_any_setting_changed_after_previous_replacement=False
    
    self.file_revert_widget_prepare()
  
  def replace(self,file_contents_before_replaced:list[str]):
    file_contents_after_replaced=[]
    for one_line_before_replaced in file_contents_before_replaced:
      if len(one_line_before_replaced) == 0:
         file_contents_after_replaced.append(one_line_before_replaced)
         continue
      #同時置換(1度置換)モード
      if self.__replace_text_control.is_only_once_replace():
         one_line_after_replaced=self.replace_one_line_in_only_once_mode(one_line_before_replaced)
         #置換結果、その行が空行になった場合、空行として残さず詰める
         if len(one_line_after_replaced) == 0:
            continue
         file_contents_after_replaced.append(one_line_after_replaced)
         continue
      #通常モード
      one_line_after_replaced=self.replace_one_line_in_normal_mode(one_line_before_replaced)
      #置換結果、その行が空行になった場合、空行として残さず詰める
      if len(one_line_after_replaced) == 0:
         continue
      file_contents_after_replaced.append(one_line_after_replaced)
    
    return file_contents_after_replaced  
          
    
  def replace_one_line_in_only_once_mode(self,one_line_before_replaced:str):
    #これから置換するので、とりあえず、置換前の文字列をそのまま入れておく(=これを置換する)
    one_line_after_replaced=one_line_before_replaced
    
    #同時置換(1度置換モード(以前置換したものを別のものに再置換しないようにするモード)では、置換を行うとき,置換された結果としてその文字列になったことを示すため
    #内部的に、「設定された置換後文字列の前後両方に、改行コードを入れたもの」に置換する。
    #(これで、前後に改行コードがあるものは、元から存在した文字列でなく、置換した結果生じたものだとわかる)
    #それでも、部分一致の場合、前後に改行コードがあろうがなかろうが、その語句に一致してしまうので、
    #NGワードとして、ユーザーが指定したものとは別に「置換後文字列の前後に改行コードがついたもの」を指定することによって、
    #「置換された結果の文字列」であるものは置換されなくなる
    ng_words_tmp=[]
    
    for one_replace_information in self.__replacers_information:
      #「置換後文字列の前後に改行コードがついた文字列」が置換されないように、NGワードとして、ユーザーが指定したものとは別にここで指定する
      ng_words_tmp.append(one_replace_information.escaped_replace_after_pattern_in_only_once_replace_mode)
      replace_obj=one_replace_information.get_replace_obj_in_only_once_replace_mode(tuple(ng_words_tmp))
      one_line_after_replaced=replace_obj.replace(one_line_after_replaced)
    
    #置換終了後、内部的に前後に改行コードを入れたので、改行コードを取り除く
    one_line_after_replaced=re.sub("\n(.*)\n","\\1",one_line_after_replaced)
    
    return one_line_after_replaced
 
  def replace_one_line_in_normal_mode(self,one_line_before_replaced:str):
    #これから置換するので、とりあえず、置換前の文字列をそのまま入れておく(=これを置換する)
    one_line_after_replaced=one_line_before_replaced
    
    for one_replace_information in self.__replacers_information:
      replace_obj=one_replace_information.get_replace_obj_in_normal_mode()
      one_line_after_replaced=replace_obj.replace(one_line_after_replaced)
    
    return one_line_after_replaced
       
    
  def file_revert_widget_prepare(self):
    self.__revert_text_btn.place_forget()
    self.__revertable_file_and_index_in_file_managers={}
    for index,one_file_manager in enumerate(self.__file_managers):
       #元に戻せるものだけ(=きちんと読み取れたものと、上書きのもの)を辞書に入れる
       one_file_manager.read_file_all_lines() #テスト中のみ
       print(one_file_manager)
       if one_file_manager.is_revertable_to_replace_before():
          current_file_path_str=one_file_manager.src_file_path_str
          self.__revertable_file_and_index_in_file_managers[current_file_path_str]=index
    
    print(self.__revertable_file_and_index_in_file_managers)
    if len(self.__revertable_file_and_index_in_file_managers.keys()) != 0:
      self.__revert_text_btn.place(x=448,y=624)
      
  
  def revert_replaced_text(self,event=None):
    if len(self.__revertable_file_and_index_in_file_managers.keys()) == 0:
       messagebox.showerror("エラー","現在元に戻すものがありません")
       return
    
    dialog=SrcFileOpenDialog(self,self.__revertable_file_and_index_in_file_managers)
    revert_file_indexs=dialog.result
    if revert_file_indexs is None:
       return
    
    print(revert_file_indexs)
    print("選択されたファイルパス")
    for index in revert_file_indexs:
      print(self.__file_managers[index].src_file_path_str)
      
    
    #元に戻した結果を入れる
    #revert_results={}
    #for one_index in revert_file_indexs:
       #one_io_obj=self.__file_managers[one_index]
       #status_code=one_io_obj.revert_to_replace_before_str()
       #revert_results[one_io_obj.src_file_path_str]=FileRevertResultStatusCodes.code_to_status_str(status_code)
    
    #result_dialog=RevertResultStatusDialog(self,revert_results)
  
  def exit(self,event=None):
    FileOpenApplicationSettingDialog.write_file_path_to_ini_file()
    self.destroy()
  
  #設定ウィンドウが閉じられたときにファイル(テキスト)設定ウィンドウ側から呼び出す
  #こちらのウィンドウは、直接、ファイル(テキスト)設定ウィンドウをインスタンス変数として持っていないため(間に、ファイル設定欄とテキスト設定欄があるため)、こちらから変化があったことはわからない
  #一方で、向こう側からは、設定ウィンドウ側に、閉じた後、フォーカスがこのウィンドウに来させられるようにこのウィンドウをインスタンス変数として持たせているので、
  #循環参照となるが、向こうからこちらに変化を知らせる形でこのメソッドを呼ぶ方が良い
  #(向こうのウィンドウを閉じるときに、向こう側からこのメソッドを呼んで、変化したことを保持するようにする
  def any_information_changed(self):
   self.__revert_text_btn.place_forget()
   self.__revertable_file_and_index_in_file_managers={}
   self.__has_any_setting_changed_after_previous_replacement=True
       
 
 


if __name__ == "__main__":
  main=FileTextReplaceMainWindow()
  main.mainloop()