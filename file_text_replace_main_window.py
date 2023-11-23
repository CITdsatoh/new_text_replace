#encoding:utf-8;

from io_file_choice.io_file_choice_controler import IOFileChoiceControler
from replace_choice.replace_choice_controler import ReplaceChoiceControler
from file_disp_manage.src_file_open import SrcFileOpenDialog
from file_disp_manage.file_open_setting import FileOpenApplicationSettingDialog
from io_file_choice.io_manage.file_io_manage import FileRevertResultStatusCodes,not_sep
from replace_result_dialog import  ReplaceResultDialog
from revert_result_status_dialog import RevertResultStatusDialog

import tkinter as tk
from tkinter import messagebox,filedialog
import os
import re
from datetime import datetime
import subprocess
import pathlib
import shutil

class FileTextReplaceMainWindow(tk.Tk):
  
  __log_files_save_dir=os.path.abspath("logs")
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
    
    self.__all_reset_btn=tk.Button(self,text="すべての設定を初期化する",font=("times",11))
    self.__all_reset_btn.place(x=160,y=624)
    self.__all_reset_btn.bind("<Button-1>",self.all_setting_reset)
    
    self.__replace_exe_btn=tk.Button(self,text="置換実行",font=("times",11,"bold"))
    self.__replace_exe_btn.place(x=400,y=624)
    self.__replace_exe_btn.bind("<Button-1>",self.replace_execute)
    
    
    self.__exit_btn=tk.Button(self,text="終了",font=("times",11))
    self.__exit_btn.place(x=512,y=624)
    self.__exit_btn.bind("<Button-1>",self.exit)
    
    self.__revert_text_btn=tk.Button(self,text="置換内容を元に戻す",font=("times",11))
    self.__revert_text_btn.place(x=224,y=664)
    self.__revert_text_btn.place_forget()
    self.__revert_text_btn.bind("<Button-1>",self.revert_replaced_text)
    
    self.__file_write_replace_result=tk.Button(self,text="置換結果をテキストファイルに出力する",font=("times",11))
    self.__file_write_replace_result.place(x=448,y=664)
    self.__file_write_replace_result.place_forget()
    self.__file_write_replace_result.bind("<Button-1>",self.choice_result_write_file_path)
    
    
    
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
    
    #置換時刻
    self.__replace_datetime=None
    
    self.title("ファイルテキスト一括置換アプリケーション")
    
    
    self.bind("<Escape>",self.exit)
    self.protocol("<WM_DELETE_WINDOW>",self.exit)
    self.geometry("1024x768")
  
  def replace_execute(self,event=None):
  
    if not self.__has_any_setting_changed_after_previous_replacement:
      is_double_replace_ok=messagebox.askyesno("再置換してもよろしいですか?","前回置換した際より、置換したいテキスト内容、並びに、置換したいファイル内容の変更が全くありませんが、そのまま再置換してもよろしいでしょうか?(上書きを指定している場合、前回置換した結果をさらに置換することになります。ちなみに同時置換(1度置換)モードは、同じ回の置換にのみ有効なので、これが有効になっているかどうかは今は関係ありません。)")
      if not is_double_replace_ok:
         return
    
      
    new_replacers_information=self.__replace_text_control.get_replace_information_objs()
    if len(new_replacers_information) == 0:
      messagebox.showerror("エラー","置換したいテキスト内容が1つも指定されていないようです。最低1つ以上置換したいテキストを指定してください")
      return
    
    new_file_managers=self.__replace_file_control.get_file_io_objs()
    if len(new_file_managers) == 0:
      messagebox.showerror("エラー","テキストを置換するファイルが1つも指定されていないようです。最低1つ以上置換するファイルを指定してください")
      return
      
      
    self.__replacers_information=new_replacers_information
    self.__file_managers=new_file_managers
    
    #置換処理を書く
    for one_file_manager in self.__file_managers:
     file_contents_before_replaced=one_file_manager.read_file_all_lines()
     if file_contents_before_replaced is None:
         continue
     file_contents_after_replaced=self.replace(file_contents_before_replaced)
     one_file_manager.write_file_after_replaced(file_contents_after_replaced)
    
    #一度置換をし終わったので、次の状態変化(設定ウィンドウが閉じられる)までは、False(今とまだ変わっていない状態)に戻す
    self.__has_any_setting_changed_after_previous_replacement=False
    
    self.file_revert_widget_prepare()
    result_dialog=ReplaceResultDialog(self,tuple(self.get_file_manager_strs_list()))
    self.__replace_datetime=datetime.now()
    #ログ用に毎回裏側で、置換内容レポートを残す。今回はそのログ用に残しておくファイルのパスの文字列を得る
    replace_result_file_path_for_log=self.__class__.get_result_replace_file_path_for_log(self.__replace_datetime,"replace_information_report")
    self.fwrite_result_str(replace_result_file_path_for_log)
    #ログ用に、置換した内容だけでなく、入力内容もログに残す。そのファイルのパス文字列も得る
    input_result_file_path_for_log=self.__class__.get_result_replace_file_path_for_log(self.__replace_datetime,"input_information_report")
    self.fwrite_input_str(input_result_file_path_for_log)
    
    self.__file_write_replace_result.place(x=448,y=664)
    
  
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
       if one_file_manager.is_revertable_to_replace_before():
          current_file_path_str=one_file_manager.src_file_path_str
          self.__revertable_file_and_index_in_file_managers[current_file_path_str]=index
    
    #print(self.__revertable_file_and_index_in_file_managers)
    if len(self.__revertable_file_and_index_in_file_managers.keys()) != 0:
      self.__revert_text_btn.place(x=224,y=664)
      
  
  
  def all_setting_reset(self,event=None):
    is_ok_all_reset=messagebox.askyesno("すべての設定を初期化","これまで入力した置換テキスト情報すべて(置換元文字列・置換後文字列・置換モード・すべてのNGワード情報)、ならびに入力・選択した置換ファイル情報すべてを初期化しますがよろしいでしょうか?(初期化後はこれらの情報は二度と元に戻すことはできません。)")
    if not is_ok_all_reset:
       return
    
    #長文になるので、念のためというのもかねて2回聞いておく
    is_really_ok_all_reset=messagebox.askyesno("本当にすべての設定を初期化","本当に二度と元に戻せなくなりますがよろしいでしょうか?(ちなみに、置換後に、置換前に戻したいファイルがあった場合、それももう戻せなくなります。さらに、前回の置換内容のテキストファイル出力もできなくなります。)")
    if not is_really_ok_all_reset:
       return
    
    self.any_information_changed()
    
    self.__replace_text_control.all_reset_replace_choice()
    self.__replace_file_control.all_reset_file_choice()
    
    
  def revert_replaced_text(self,event=None):
    if len(self.__revertable_file_and_index_in_file_managers.keys()) == 0:
       messagebox.showerror("エラー","現在元に戻すものがありません")
       return
    
    dialog=SrcFileOpenDialog(self,self.__revertable_file_and_index_in_file_managers)
    revert_file_indexs=dialog.result
    if revert_file_indexs is None:
       return
    
    #print(revert_file_indexs)
    #print("選択されたファイルパス")
    #for index in revert_file_indexs:
    #  print(self.__file_managers[index].src_file_path_str)
      
    
    #元に戻した結果を入れる
    revert_results={}
    for one_index in revert_file_indexs:
       one_io_obj=self.__file_managers[one_index]
       status_code=one_io_obj.revert_to_replace_before_str()
       revert_results[one_io_obj.src_file_path_str]=FileRevertResultStatusCodes.code_to_status_str(status_code)
    
    #print(revert_results)
    result_dialog=RevertResultStatusDialog(self,revert_results)
  
  def choice_result_write_file_path(self,event=None):
    if len(self.__file_managers) == 0:
      messagebox.showerror("エラー","置換しようとしているファイルが1つも設定されていないので、結果を出力することはできません")
      return
    
    if len(self.__replacers_information) == 0:
      messagebox.showerror("エラー","置換しようとしている文字列が1つも設定されていないので、結果を出力することはできません")
      return
    
    if self.__replace_datetime is None:
      messagebox.showerror("エラー","まだ置換自体が行われていないようですので、結果を出力することができません")
      return 
    
    ini_file_name="replace_information_report_%d%02d%02d%02d%02d%02d.txt"%(self.__replace_datetime.year,self.__replace_datetime.month,self.__replace_datetime.day,self.__replace_datetime.hour,self.__replace_datetime.minute,self.__replace_datetime.second)
    
    is_continue=True
    while is_continue:
      result_file_path=filedialog.asksaveasfilename(parent=self,title="置換結果の保存先を指定",initialdir=os.path.expanduser("~"),filetypes=[("テキストファイル","*.txt")],initialfile=ini_file_name,defaultextension=".txt")
      if len(result_file_path) == 0:
        is_continue=messagebox.askyesno("ファイル選択を続行","置換結果の保存先が指定されませんでした。もう一度ファイル名を指定しなおしますか?")
        continue
      try:
        if os.path.splitext(result_file_path)[1] != ".txt":
           #拡張子が.pngとか.jsなど.txt以外になっていたらこちらで強制的にtxtにする。ファイル書き込みの時と異なり、ユーザーの意向は尊重しない
           result_file_path += ".txt"
        self.fwrite_result_str(result_file_path)
      except PermissonError:
        messagebox.showerror("エラー",f"{result_file_path}の書き込みに失敗しました。可能性として、該当ファイルが開いたままになっているか、あるいは読み取り専用の状態になっている可能性があります。ご確認の上、もう一度やり直してください")
      else:
        messagebox.showinfo("ファイル書き込み完了","ファイル書き込みが完了しました")
        result_file_dir=os.path.split(result_file_path)[0].replace(not_sep,os.sep)
        subprocess.Popen(["explorer",result_file_dir],shell=True)
        break
    else:
       return
      
  #置換結果をファイルに記述する
  def fwrite_result_str(self,str_file_path:str):
    border_str="-------------------------------------------------------"
    
    replace_basic_header="【基本情報】"
    replace_time_str=f"置換時刻:{self.__replace_datetime.year}年{self.__replace_datetime.month}月{self.__replace_datetime.day}日{self.__replace_datetime.hour}時{self.__replace_datetime.minute}分{self.__replace_datetime.second}秒"
    replace_mode_str="同時置換(1度置換)モード:有効" if self.__replace_text_control.is_only_once_replace() else "同時置換(1度置換)モード:無効" 
    replace_basic_contents=[border_str,replace_basic_header,replace_time_str,replace_mode_str,border_str]
    replace_basic_full_str="\n".join(replace_basic_contents)
    
    
    replace_text_str_header="【置換テキスト情報】"
    replace_text_str_body="\n\n".join(self.get_replace_information_strs_list())
    replace_text_str_contents=[border_str,replace_text_str_header,replace_text_str_body,border_str]
    replace_text_full_str="\n".join(replace_text_str_contents)
    
    replace_file_str_header="【置換ファイル情報と書き込み結果】"
    replace_file_str_body="\n\n".join(self.get_file_manager_strs_list())
    replace_file_str_contents=[border_str,replace_file_str_header,replace_file_str_body,border_str]
    replace_file_full_str="\n".join(replace_file_str_contents)
    
    replace_result_full_contents=[replace_basic_full_str,replace_text_full_str,replace_file_full_str]
    replace_result_full_str="\n\n".join(replace_result_full_contents)
    
    f=None
    try:
      f=open(str_file_path,"w",encoding="utf-8")
      f.write("\n")
      f.write(replace_result_full_str)
      f.write("\n")
    finally:
      if f is not None:
        f.close()
  
  #現在各ダイアログに入力されている内容をログ用にファイルに記述する(こちらはプログラマ用)
  def fwrite_input_str(self,str_file_path:str):
    border_str="-------------------------------------------------------"
     
    input_basic_header="【基本情報】"
    input_time_str=f"置換時刻:{self.__replace_datetime.year}年{self.__replace_datetime.month}月{self.__replace_datetime.day}日{self.__replace_datetime.hour}時{self.__replace_datetime.minute}分{self.__replace_datetime.second}秒"
    input_basic_contents=[border_str,input_basic_header,input_time_str,border_str]
    input_basic_full_str="\n".join(input_basic_contents)
    
    input_text_header="【置換したいテキストの入力内容】"
    input_text_str_body="\n\n".join(self.__replace_text_control.get_current_choice_strs_list())
    input_text_contents=[border_str,input_text_header,input_text_str_body,border_str]
    input_text_full_str="\n".join(input_text_contents)
    
    input_file_header="【テキストを置換したいファイルの入力内容】"
    input_file_str_body="\n\n".join(self.__replace_file_control.get_current_choice_strs_list())
    input_file_contents=[border_str,input_file_header,input_file_str_body,border_str]
    input_file_full_str="\n".join(input_file_contents)
    
    replace_input_full_contents=[input_basic_full_str,input_text_full_str,input_file_full_str]
    replace_input_full_str="\n\n".join(replace_input_full_contents)
    
    f=None
    try:
      f=open(str_file_path,"w",encoding="utf-8")
      f.write("\n")
      f.write(replace_input_full_str)
      f.write("\n")
    finally:
      if f is not None:
        f.close()
   
  def exit(self,event=None):
    try:
      FileOpenApplicationSettingDialog.write_file_path_to_ini_file()
      self.__class__.remove_log_files_over_one_hundred()
    finally:
      self.destroy()
  
  #設定ウィンドウが閉じられたときにファイル(テキスト)設定ウィンドウ側から呼び出す
  #こちらのウィンドウは、直接、ファイル(テキスト)設定ウィンドウをインスタンス変数として持っていないため(間に、ファイル設定欄とテキスト設定欄があるため)、こちらから変化があったことはわからない
  #一方で、向こう側からは、設定ウィンドウ側に、閉じた後、フォーカスがこのウィンドウに来させられるようにこのウィンドウをインスタンス変数として持たせているので、
  #循環参照となるが、向こうからこちらに変化を知らせる形でこのメソッドを呼ぶ方が良い
  #(向こうのウィンドウを閉じるときに、向こう側からこのメソッドを呼んで、変化したことを保持するようにする
  def any_information_changed(self):
   self.__revert_text_btn.place_forget()
   self.__file_write_replace_result.place_forget()
   self.__revertable_file_and_index_in_file_managers={}
   self.__has_any_setting_changed_after_previous_replacement=True
   self.__replace_datetime=None
   self.__replacers_information=[]
   self.__file_managers=[]
  
  #ファイルに置換情報を書き込むとき用(置換テキスト)
  def get_replace_information_strs_list(self):
    return [str(one_information) for one_information in self.__replacers_information]
    
  #ファイルに書き込み用(置換ファイル)
  #ダイアログにも書き込むことを考慮して、list型で、返す
  def get_file_manager_strs_list(self):
    return [str(one_file_manager) for one_file_manager in self.__file_managers]
  
  #ログ用に残しておくために、文字列置換結果を残すファイルパス
  @classmethod
  def get_result_replace_file_path_for_log(cls,replace_datetime:datetime,classification:str):
    path_obj=pathlib.Path(cls.__log_files_save_dir)
    if not path_obj.exists():
       path_obj.mkdir()
    
    datetime_str="%d%02d%02d%02d%02d%02d"%(replace_datetime.year,replace_datetime.month,replace_datetime.day,replace_datetime.hour,replace_datetime.minute,replace_datetime.second)
    path_sub_obj=path_obj/datetime_str
    if not path_sub_obj.exists():
      path_sub_obj.mkdir()
    
    file_name=f"{classification}_{datetime_str}.txt"
    return str(path_sub_obj/file_name)
  
  #ログ用ファイルの削除(毎回の置換ごとに、置換内容と入力内容をログとして、保存しているが、無限にログをとっておくわけにいかないので、100個たまったらここで自動削除する)
  #アプリを閉じるときに行う
  @classmethod
  def remove_log_files_over_one_hundred(cls):
    if not os.path.exists(cls.__log_files_save_dir):
       return
    
    all_log_dirs=[]
    for one_log_dir in os.listdir(cls.__log_files_save_dir):
      one_abs_log_dir=os.path.join(cls.__log_files_save_dir,one_log_dir)
      if os.path.isdir(one_abs_log_dir):
        all_log_dirs.append(one_abs_log_dir)
    
    all_logs_num=100
    current_log_dirs_num=len(all_log_dirs)
    
    if current_log_dirs_num <= all_logs_num:
      return
    
    all_log_dirs.sort(key=os.path.getctime)
    
    for one_log_dir in all_log_dirs:
      if current_log_dirs_num <= all_logs_num:
        break
      try:
        shutil.rmtree(one_log_dir)
        current_log_dirs_num -= 1
      except (FileNotFoundError,PermissionError):
        pass
    
  
    
 


if __name__ == "__main__":
  main=FileTextReplaceMainWindow()
  main.mainloop()