#encoding:utf-8;

import tkinter as tk
from io_file_choice.io_file_choice_widgets.file_path_entry import FilePathEntryCorner
from tkinter import messagebox,simpledialog,filedialog
import os


class FilePathSettingDialog(simpledialog.Dialog):

   __ONE_PAGE_WIDGET_NUM=5
   
   def __init__(self,parent,entry_datas,title:str="置換ファイル指定ダイアログ"):
     self.__current_disp_page_num=0
     self.__entry_datas=list(entry_datas)
     self.__entry_corners=[]
     super().__init__(parent,title)
   
   def buttonbox(self):
     self.__header_label=tk.Label(self,text="ファイルテキスト一括置換～置換ファイル設定～",font=("serif",16,"bold"))
     self.__header_label.place(x=448,y=0)
     
     home_dir=os.path.expanduser("~")
     explaination_str=f"ここでは、実際にテキストを置換したいと思っているファイルを選択し設定します。さらに、置換結果を書き込むファイルを選択することで、\n元ファイルとは別のところに書き込みを行います。1度に30ファイルまで設定できます。なお、ファイルの設定は「参照」から選択することも、\n手入力でも設定可能です。さらに、入力は相対パスでも絶対パスでも可能です。相対パスが指定された場合,{home_dir}を基準といたします。\nまた、置換結果を書き込むファイルが何も選択されていない場合は元のファイルに上書き保存されます。"
     self.__header_explaination=tk.Label(self,text=explaination_str,font=("serif",10,"bold"))
     self.__header_explaination.place(x=16,y=32)
     
     FilePathEntryCorner.reset_next_id()
     
     for one_entry_data in self.__entry_datas:
       if one_entry_data is None:
          one_corner=FilePathEntryCorner(self)
          self.__entry_corners.append(one_corner)
          continue
       #以前、ダイアログを閉じたときのデータがあれば、その続きの作業ができるよう、閉じる前のデータを入れたエントリーコーナーを作る
       one_corner=FilePathEntryCorner.parse_from_file_information_obj(self,one_entry_data)
       self.__entry_corners.append(one_corner)
     
     
     self.__page_back_btn=tk.Button(self,text="前のページに戻る",font=("times",11))
     self.__page_back_btn.bind("<Button-1>",self.page_back)
     
     self.__page_advance_btn=tk.Button(self,text="次のページに進む",font=("times",11))
     self.__page_advance_btn.place(x=720,y=624)
     self.__page_advance_btn.bind("<Button-1>",self.page_advance)
     
     
     self.__current_page_entry=tk.Entry(self,width=4,font=("times",11))
     self.__current_page_entry.insert(0,"1")
     self.__current_page_entry.place(x=320,y=624)
     
     self.__current_page_label=tk.Label(self,text=f"ページ(その1-その5)/6ページ",font=("times",11))
     self.__current_page_label.place(x=368,y=624)
     
     self.__page_jump_btn=tk.Button(self,text="ページへ移動",font=("times",11))
     self.__page_jump_btn.place(x=600,y=624)
     self.__page_jump_btn.bind("<Button-1>",self.page_jump)
     
     self.__multiple_choice_btn=tk.Button(self,text="テキスト置換ファイルを複数一括で設定",font=("times",11))
     self.__multiple_choice_btn.place(x=128,y=656)
     self.__multiple_choice_btn.bind("<Button-1>",self.src_file_set_multiple)
     
     self.__cancel_btn=tk.Button(self,text="キャンセル",font=("times",11))
     self.__cancel_btn.place(x=544,y=656)
     self.__cancel_btn.bind("<Button-1>",self.cancel)
     
     self.__all_reset_btn=tk.Button(self,text="全入力取り消し",font=("times",11))
     self.__all_reset_btn.place(x=672,y=656)
     self.__all_reset_btn.bind("<Button-1>",self.all_reset)
     
     self.__ok_btn=tk.Button(self,text="内容確定",font=("times",11,"bold"))
     self.__ok_btn.place(x=448,y=656)
     self.__ok_btn.bind("<Button-1>",self.ok)
     
     self.page_place(0)
   
     self.bind("<Escape>",self.cancel)
     self.bind("<Return>",self.ok)
     
     self.geometry("1134x768")
  
   
   def page_back(self,event=None):
     if self.__current_disp_page_num <= 0:
        return 
        
     self.page_forget()
     self.__current_disp_page_num -= 1
     self.__current_page_entry.delete(0,tk.END)
     self.__current_page_entry.insert(0,f"{self.__current_disp_page_num+1}")
     self.__current_page_label["text"]=f"ページ(その{self.__current_disp_page_num*5+1}-その{(self.__current_disp_page_num+1)*5})/6ページ"
     self.page_place()
     
     #最初のページに戻ってきたとき
     if self.__current_disp_page_num == 0:
       self.__page_back_btn.place_forget()
     
     #最後のページから戻ってきたとき
     if self.__current_disp_page_num == 4:
       self.__page_advance_btn.place(x=720,y=624)
      
   
   def page_advance(self,event=None):
     if 5 <= self.__current_disp_page_num:
       return
       
     self.page_forget()
     self.__current_disp_page_num += 1
     self.__current_page_entry.delete(0,tk.END)
     self.__current_page_entry.insert(0,f"{self.__current_disp_page_num+1}")
     self.__current_page_label["text"]=f"ページ(その{self.__current_disp_page_num*5+1}-その{(self.__current_disp_page_num+1)*5})/6ページ"
     self.page_place()
     #最初のページから2ページ目に進んだとき
     if self.__current_disp_page_num == 1:
       self.__page_back_btn.place(x=96,y=624)
     
     #最後のページに進んだとき
     if self.__current_disp_page_num == 5:
       self.__page_advance_btn.place_forget()
     
   def page_jump(self,event=None):
     jump_page_num=0
     try:
       jump_page_num=int(self.__current_page_entry.get())
     except ValueError:
       messagebox.showerror("エラー","ページ番号が数字以外が入力されました。必ず、移動したいページ番号は1から6の間の整数を入力してください")
       self.__current_page_entry.delete(0,tk.END)
       self.__current_page_entry.insert(0,f"{self.__current_disp_page_num+1}")
       return
     
     #ユーザーが入力する番号と、実際のページ番号はわかりやすいように1つずれている。つまり、ユーザーにとっての1ページ目は、こちらでは0ページ目になり,
     #ユーザーにとっての6ページ目はこちらでは5ページ目になる
     jump_page_num -= 1
     if jump_page_num < 0 or 5 < jump_page_num:
       messagebox.showerror("エラー","指定された番号のページはありません。必ず、移動したいページ番号は1から6の間の整数を入力してください")
       self.__current_page_entry.delete(0,tk.END)
       self.__current_page_entry.insert(0,f"{self.__current_disp_page_num+1}")
       return
     
     #ここからは正常入力時の処理
     self.page_forget()
     self.page_place(jump_page_num)
     self.change_back_advance_btn_disp(self.__current_disp_page_num,jump_page_num)
     self.__current_page_label["text"]=f"ページ(その{jump_page_num*5+1}-その{(jump_page_num+1)*5})/6ページ"
     self.__current_disp_page_num=jump_page_num
     
   
   def cancel(self,event=None):
     if self.result is None:
       is_cancel_ok=messagebox.askyesno("本当に閉じますか?","本当にダイアログを閉じてしまってもよろしいですか?(ここまで選択・入力したファイル情報は保存されず、ダイアログを開く前の状態に戻ります)")
       if not is_cancel_ok:
         return
     super().cancel()
   
   def validate(self):
     if self.count_margin_entries_num() == 0:
        messagebox.showerror("ファイル選択エラー","ファイル選択が1箇所もなされていません。最低限、1か所以上、置換したいファイルを選択するようにしてください")
        return False
     
     error_entry_nums=[]
     file_information_objs=[]
     
     is_ok=True
     
     for i,one_entry_corner in enumerate(self.__entry_corners):
      if len(one_entry_corner.get_input_src_file_path()) == 0 and len(one_entry_corner.get_input_dst_file_path()) == 0:
          file_information_objs.append(None)
          continue
      information_obj=one_entry_corner.get_file_information()
      #「入力情報」がNoneが返された場合は何らかのエラーが存在するということになる
      if information_obj is None:
         is_ok=False
         error_entry_nums.append(i+1)
         continue
      file_information_objs.append(information_obj)
     
     if not is_ok:
        error_entry_strs=[f"その{error_num}" for error_num in error_entry_nums]
        error_entry_one_str=",".join(error_entry_strs)
        messagebox.showerror("エラー",f"入力エラーがある箇所が{len(error_entry_strs)}個ありました。\nエラー箇所:{error_entry_one_str}")
        first_error_page_num=int((error_entry_nums[0]-1)/self.__class__.__ONE_PAGE_WIDGET_NUM)
        self.page_forget()
        self.page_place(first_error_page_num)
        self.__current_page_entry.delete(0,tk.END)
        self.__current_page_entry.insert(0,f"{first_error_page_num+1}")
        self.__current_page_label["text"]=f"ページ(その{first_error_page_num*5+1}-その{(first_error_page_num+1)*5})/6ページ"
        self.change_back_advance_btn_disp(self.__current_disp_page_num,first_error_page_num)
        self.__current_disp_page_num=first_error_page_num
        return False
     
     #ダイアログを閉じなおしても続けられるように、そして、本当のファイル読み書き用オブジェクト(FileIOManageクラスのインスタンス)に変換できるようにバリデーションがうまくいったら、引き渡す
     self.result=file_information_objs[:]
     return True
       
       
   def src_file_set_multiple(self,event=None):
     margin_entry_num=self.count_margin_entries_num()
     messagebox.showinfo("テキスト置換ファイル複数一括設定",f"通常の場合、各ファイル選択入力欄ごとに1つずつ逐次選択しなければなりませんが、ここでは、同じフォルダに存在するファイルに限り、複数で一括選択できます。\nただし、以下の条件の下での選択となります\n・テキスト置換したいファイルのみの選択(それに対応する、置換結果を書き込むファイルは従来通り各入力欄で逐一選択)となります\n・入力欄は全部で30個あり、そのうち現在{margin_entry_num}個入力欄が使用できます。ですので、{margin_entry_num+1}個以上の選択はできません。")
     is_continue=True
     new_src_files=[]
     while is_continue:
       new_src_files=filedialog.askopenfilenames(parent=self,title=f"テキストを置換したいファイルを複数(最大{margin_entry_num}個)選択",initialdir=os.path.expanduser("~"))
       if len(new_src_files) == 0:
         is_continue=messagebox.askyesno("ファイルが選択されませんでした。","ファイルが選択されませんでした。もう一度、ファイルの選択をやり直しますか?")
       elif margin_entry_num < len(new_src_files):
         is_continue=messagebox.askyesno("ファイルの選択個数の上限を超えました","ファイルの選択個数の上限を超えました。もう一度ファイルの選択をやり直しますか?")
       else:
          break
     else:
        return
     
     pad_entry_corner_numbers=[]
     new_src_files_index=0
     
     for i,one_entry_corner in enumerate(self.__entry_corners):
       if len(one_entry_corner.get_input_src_file_path()) == 0 and len(one_entry_corner.get_input_dst_file_path()) == 0:
          one_entry_corner.set_input_src_file_path(new_src_files[new_src_files_index])
          pad_entry_corner_numbers.append(i+1)
          new_src_files_index += 1
       if new_src_files_index == len(new_src_files):
          break
     
     pad_entry_corner_number_strs=[f"その{one_entry_corner_number}" for one_entry_corner_number in pad_entry_corner_numbers]
     pad_entry_corner_number_str=",".join(pad_entry_corner_number_strs)
     
     messagebox.showinfo("完了",f"テキストを置換したいファイルを{len(new_src_files)}個分指定しました。以下の入力欄を確認してください\n入力欄一覧：{pad_entry_corner_number_str}\nなお、上書きではなく、置換結果を書き込みたいファイルを指定する場合は各入力欄で逐一行ってください")
     
     first_pad_page_num=int((pad_entry_corner_numbers[0]-1)/self.__class__.__ONE_PAGE_WIDGET_NUM)
     self.page_forget()
     self.page_place(first_pad_page_num)
     self.__current_page_entry.delete(0,tk.END)
     self.__current_page_entry.insert(0,f"{first_pad_page_num+1}")
     self.__current_page_label["text"]=f"ページ(その{first_pad_page_num*5+1}-その{(first_pad_page_num+1)*5})/6ページ"
     self.change_back_advance_btn_disp(self.__current_disp_page_num,first_pad_page_num)
     self.__current_disp_page_num=first_pad_page_num
          
   def all_reset(self,event=None):
     is_all_reset_ok=messagebox.askyesno("全削除","今まで選択・入力してきたファイル情報を本当にすべて削除しますか?(削除すると、二度と元に戻りません。なお、1か所だけを削除したい場合は各入力欄の右にある「両入力取消」ボタンを押してください)")
     if not is_all_reset_ok:
       return
     
     for one_entry_corner in self.__entry_corners:
       one_entry_corner.all_reset()
     
     self.page_forget()
     self.page_place(0)
     self.change_back_advance_btn_disp(self.__current_disp_page_num,0)
     self.__current_page_entry.delete(0,tk.END)
     self.__current_page_entry.insert(0,"1")
     self.__current_page_label["text"]="ページ(その1-その5)/6ページ"
     self.__current_disp_page_num=0
     messagebox.showinfo("取消完了","全入力欄のファイル選択・入力情報を初期化しました")
   
   
   #あるページのウィジェットを取り付ける
   #ここでは取り付けのみ
   def page_place(self,page_num:int=None):
     if page_num is None:
       page_num=self.__current_disp_page_num
     
     if page_num < 0 or 5 < page_num:
       return
     
     page_start_entry_num=page_num*self.__class__.__ONE_PAGE_WIDGET_NUM
     for i in range(0,self.__class__.__ONE_PAGE_WIDGET_NUM):
        self.__entry_corners[i+page_start_entry_num].place(x=0,y=104+(i*104))
     
   
   #あるページのウィジェットを取り付ける
   #ここでは取り付けのみ
   def page_forget(self,page_num:int=None):
     if page_num is None:
       page_num=self.__current_disp_page_num
     
     if page_num < 0 or 5 < page_num:
       return
     
     page_start_entry_num=page_num*self.__class__.__ONE_PAGE_WIDGET_NUM
     for i in range(0,self.__class__.__ONE_PAGE_WIDGET_NUM):
        self.__entry_corners[i+page_start_entry_num].place_forget()
   
   #「戻るボタン」、「進むボタン」の取り外し取り付け
   def change_back_advance_btn_disp(self,change_before_page_num:int,change_after_page_num:int):
   
     #最初のページから最初以外のページへ進んだとき
     if change_before_page_num == 0 and change_after_page_num != 0:
        self.__page_back_btn.place(x=96,y=624)
     #最初以外から最初のページへ来たとき
     if change_before_page_num != 0 and change_after_page_num == 0:
        self.__page_back_btn.place_forget()
     
     #最後のページ以外から最後のページに来た時
     if change_before_page_num != 5 and change_after_page_num == 5:
        self.__page_advance_btn.place_forget()
     
     #最後から最後以外に来た時
     if change_before_page_num == 5 and change_after_page_num != 5:
        self.__page_advance_btn.place(x=720,y=624)
   
   
   #現在、30入力欄のうち、何も埋まっていない入力欄がいくつあるか
   #複数一括での置換結果ファイル選択時や、実際のバリデーション時に使用
   def count_margin_entries_num(self):
     count=0
     for one_entry_corner in self.__entry_corners:
       if len(one_entry_corner.get_input_src_file_path()) == 0 and len(one_entry_corner.get_input_dst_file_path()) == 0:
           count += 1
     
     return count
     
     
     
     
     