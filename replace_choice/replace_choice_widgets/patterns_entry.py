#encoding:utf-8;
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import re
from replace_choice.replace_choice_widgets.ng_words_dialogs import NGWordSettingDialog
from replace_choice.text_replace.str_replacer import Replacer,ReplaceInformation


#0が「通常(部分一致)モード」、1が「完全一致モード」、2が「ワイルドカード」、3が「正規表現モード」
mode_names_english=("p","e","wc","re")
  

mode_names_japanese=("通常(部分一致)","1行完全一致","ワイルドカード","正規表現")

class ReplacePatternEntriesCorner(tk.Frame):
  
  
  __current_entry_id=1
  
  def __init__(self,master=None,Width=1200,Height=120):
    super().__init__(master,width=Width,height=Height)
    
    self.__entry_id=self.__class__.__current_entry_id
    self.__class__.__current_entry_id += 1
    
    self.__id_label=tk.Label(self,text=f"その{self.__entry_id}:",font=("times",12,"bold"))
    self.__id_label.place(x=8,y=0)
    
    #置換元文字列(=何を置換するか)
    self.__replace_before_entry=tk.Entry(self,width=20,font=("times",11))
    self.__replace_before_entry.place(x=64,y=0)
    
    #モード選択(通常・1行完全一致・ワイルドカード・正規表現)
    self.__pattern_choice=ttk.Combobox(self,height=4,width=15,state="readonly",font=("helvetica",11),values=mode_names_japanese)
    self.__pattern_choice.current(0);
    self.__pattern_choice.bind("<<ComboboxSelected>>", self.option_button_disp_operation)
    self.__pattern_choice.place(x=216,y=0)
    
    
    
    #「を」ラベル(=「置換元文字列」の入力欄と「置換先文字列」の入力欄の間のラベル)
    self.__from_label=tk.Label(self,text="を",font=("times",12))
    self.__from_label.place(x=360,y=0)
    
    #置換先文字列(=何に置換するか)
    self.__replace_after_entry=tk.Entry(self,width=20,font=("times",11))
    self.__replace_after_entry.place(x=392,y=0)
    
    #「置換先文字列」の入力欄の後のラベル
    self.__to_label=tk.Label(self,text="に置換する",font=("times",12))
    self.__to_label.place(x=552,y=0)
    
    #「ngワード」(=例えば、「京都」を「奈良」に置換したいが、「京都」という文字列を含む「東京都」や「京都府」という文字列は置換してほしくないとき、
    #置換してほしくないワードを設定するダイアログを発動する
    self.__option_setting_button=tk.Button(self,text="置換NGワード設定",font=("times",12))
    self.__option_setting_button.bind("<Button-1>",self.ng_words_setting)
    self.__option_setting_button.place(x=664,y=0)
    
    #置換元文字列別にNGワード集を保存しておく(keyが置換文字列で、valueがそれに対応するNGワード)
    #例えば、「京都」を置換したいが、「東京都」や「京都府」は置換したくない場合は,
    #{"京都":False:["東京都","京都府"]}あるいは,{"京都":True:["東京都","京都府"]}というようにする。変換したくないものをvalueとしてリストに保持する
    #完全一致モード以外は登録できるようにする
    #3重入れ子(1段階目はモード名(p,wc,re),2段階目は置換元文字列表現,3段階目のTrue(False)は大文字小文字を無視するかどうか)
    self.__replace_ng_words_by_replace_before_str={"p":{},"wc":{},"re":{}}
    
    #NGワードの置換外しモード文字列(2重入れ子で1段階目は置換元文字列,2段階目は大文字小文字を無視するかどうかで、
    #valueが置換外しモードの文字列(NG-pが部分一致外し、NG-eが完全一致外し)のどっちかが入る
    self.__ng_words_mode_in_reg_mode={}
    
    self.__ng_words_reset_btn=tk.Button(self,text="NGワード全削除",font=("times",12))
    self.__ng_words_reset_btn.place(x=840,y=0)
    self.__ng_words_reset_btn.bind("<Button-1>",self.ng_words_reset)
    
    
    
    self.__reset_btn=tk.Button(self,text="入力を取消",font=("times",12))
    self.__reset_btn.place(x=976,y=0)
    self.__reset_btn.bind("<Button-1>",self.input_reset)
    
    self.__ignore_case_widget_var=tk.BooleanVar()
    self.__ignore_case_checkbox=tk.Checkbutton(self,text="置換元の表現の大文字小文字の違いを無視する",font=("times",11),variable=self.__ignore_case_widget_var,command=self.option_button_disp_operation)
    self.__ignore_case_widget_var.set(False)
    self.__ignore_case_checkbox.place(x=320,y=24)
    
    self.__ng_words_label=tk.Label(self,text="NGワード一覧:置換元の表現が入力されてません",font=("times",11,"bold"))
    self.__ng_words_label.place(x=16,y=48)
    
    self.__error_disp_corner=tk.Label(self,text="",font=("helvatica",10,"bold"),fg="#ff0000")
    self.__error_disp_corner.place(x=8,y=72)
    
    self.__default_label_bg_color=self["bg"]
    
    self.bind("<KeyPress>",self.mode_choide_operation_by_verical_key)
    
    
  
  #こちらはダイアログが閉じられたとき,このままではデータが消えてしまうので、ここまで入力してきたものを保存するためのものを返す
  #このメソッドが呼ばれたときに現在の情報を取得し、保存用クラス(下記のEntriesDataRepository)に引き渡し、そのインスタンスを返すことでダイアログが閉じられて、再度開きなおした後も情報が利用できるようになる
  def get_entries_data(self):
    
    replace_before_str=self.__replace_before_entry.get()
    replace_after_str=self.__replace_after_entry.get()
    
    #0が「通常(部分一致)モード」、1が「完全一致モード」、2が「ワイルドカード」、3が「正規表現モード」
    replace_mode_num=self.__pattern_choice.current()
    
    is_ignore_case=self.__ignore_case_widget_var.get()
    
    if len(replace_before_str) == 0:
      #置換先文字列が入っているのに置換元文字列が入っていない場合はエラー
      if len(replace_after_str) != 0:
         self.__error_disp_corner["text"]="エラー:置換したい文字列あるいは表現が入力されていません。置換前の文字列を空に設定することはできません"
         self.__error_disp_corner["bg"]="#ffaaaa"
         return None
      #両方とも入力されていない場合は、そこは置換の対象から外したいというユーザーの意思表示ということになるので、エラーは表示しない
      #オブジェクトとして成り立つので,スルーでよい
      #(=基本的には、両方とも未入力の場合は呼び出しもとでそのことを判定し、このメソッドを呼び出すのをやめる方針にしてもらいたい)
   
    if replace_mode_num == 3:
      try:
        #ユーザーが入力した正規表現が正しいかどうか調べるためにダミーで置換操作を行う(=もちろん、そのあとに影響することはない)
        re.sub(replace_before_str,"","dummy")
        re.sub("dummy",replace_after_str,"hoge")
      except re.error:
        self.__error_disp_corner["text"]="エラー:正規表現の形が間違っています。おそらく、以下の3つのいずれかの可能性があります。\n ・特殊文字(+や*など)のエスケープのし忘れ(*は\\*と表記してください)\t・かっこ({}や()や[])の閉じ忘れ\t・不定長の後読み先読みの利用(本システムでは利用できません)"
        self.__error_disp_corner["bg"]="#ffaaaa"
        return None
    elif replace_mode_num == 2:
      try:
        wildcard_reg_exp=Replacer.wildcard_to_reg_exp(self.__replace_before_entry.get())
        re.sub(wildcard_reg_exp,"","dummy")
        re.sub("hoege",replace_after_str,"dummy")
      except re.error:
        self.__error_disp_corner["text"]="エラー:ワイルドカードの記法が間違っています。\n使用できるのは,*(長さ任意の文字列),?(長さ1文字の文字列),[](いずれか1文字)のみです。"
        self.__error_disp_corner["bg"]="#ffaaaa"
        return None
    
    self.__error_disp_corner["text"]=""
    self.__error_disp_corner["bg"]=self.__default_label_bg_color
    
    replace_before_str=self.__replace_before_entry.get()
    replace_after_str=self.__replace_after_entry.get()
    
    replace_mode_english=mode_names_english[replace_mode_num]
    
    return EntriesDataRepository(replace_before_str,replace_after_str,replace_mode_num,is_ignore_case,self.__replace_ng_words_by_replace_before_str,self.__ng_words_mode_in_reg_mode)
    
    
    
  def input_reset(self,event=None):
     self.__replace_before_entry.delete(0,tk.END)
     self.__replace_after_entry.delete(0,tk.END)
     self.__ng_words_label["text"]="NGワード一覧:置換元の表現が入力されてません"
  
  def all_reset(self):
     self.input_reset()
     self.__error_disp_corner["text"]=""
     self.__error_disp_corner["bg"]=self["bg"]
     self.__ignore_case_widget_var.set(False)
     self.__pattern_choice.current(0)
     self.__any_changed=False
  
  def ng_words_setting(self,event=None):
    #0が「通常(部分一致)モード」、1が「完全一致モード」、2が「ワイルドカード」、3が「正規表現モード」
    #「完全一致モード」では、NGワードは使用できない
    current_mode=self.__pattern_choice.current()
    if current_mode == 1:
       return 
    
    current_replace_before_str=self.__replace_before_entry.get()
    
    if len(current_replace_before_str) == 0:
       messagebox.showerror("エラー","置換元文字列・表現が入力されていないので,NGワードを設定することはできません")
       self.__ng_words_label["text"]="NGワード一覧:置換元の表現が入力されてません"
       return
    
    if current_mode == 3:
      try:
         #入力された正規表現が正しいかどうかダミーのデータで確かめる
         re.sub(current_replace_before_str,"","hoge")
      except re.error:
         messagebox.showerror("エラー","置換元文字列・表現が正規表現として不正ですので,NGワードを設定することはできません")
         self.__ng_words_label["text"]="NGワード一覧:置換元の表現が不正です"
         return 
    
    if current_mode == 2:
      try:
         #入力されたワイルドカードが正しいかどうかダミーのデータで確かめる
         re.sub(Replacer.wildcard_to_reg_exp(current_replace_before_str),"","hoge")
      except re.error:
         messagebox.showerror("エラー","置換元文字列・表現がワイルドカードとして不正ですので,NGワードを設定することはできません")
         self.__ng_words_label["text"]="NGワード一覧:置換元の表現が不正です"
         return 
    
    
    self.__option_setting_button["state"]="normal"
    self.__ng_words_reset_btn["state"]="normal"
    
    is_ignore_case=self.__ignore_case_widget_var.get()
    
    current_replace_before_str_to_ng_words=[]
    
    current_mode_english=mode_names_english[current_mode]
    
    #過去に,今入力されている文字列に対するNGワードが登録されている場合のみ、過去に登録したNGワードを読み出す
    if current_replace_before_str in self.__replace_ng_words_by_replace_before_str[current_mode_english].keys():
      if is_ignore_case in self.__replace_ng_words_by_replace_before_str[current_mode_english][current_replace_before_str].keys():
       #過去のその言葉に対する登録したNGワードを探す
       #3重の連想配列になっており,1段階目はモード名,2段階目は,そのNGワードを登録しようとしている置換元文字列表現,3段階目は大文字小文字を無視するかどうか(boolean)
       current_replace_before_str_to_ng_words=self.__replace_ng_words_by_replace_before_str[current_mode_english][current_replace_before_str][is_ignore_case]
    
    current_ng_word_mode_in_reg_mode="NG-p"
    if current_mode == 3:
      current_ng_word_mode_in_reg_mode=self.get_current_ng_words_mode_in_reg_mode()
    
    #この言葉に対するNGワードがまだ登録されていない場合はデフォルトで代入した空リストを渡す
    setting_dialog=NGWordSettingDialog(current_replace_before_str,current_mode_english,is_ignore_case,tuple(current_replace_before_str_to_ng_words),current_ng_word_mode_in_reg_mode,self)    
    setting_result=setting_dialog.result
    if setting_result is not None:
      if current_mode == 3:
        new_ng_words_mode=setting_result.pop()[0]
        if current_replace_before_str not in self.__ng_words_mode_in_reg_mode.keys():
           self.__ng_words_mode_in_reg_mode[current_replace_before_str]={}
        if re.search("[a-zA-Z]",current_replace_before_str):
           self.__ng_words_mode_in_reg_mode[current_replace_before_str][is_ignore_case]=new_ng_words_mode
        else:
           self.__ng_words_mode_in_reg_mode[current_replace_before_str][True]=new_ng_words_mode
           self.__ng_words_mode_in_reg_mode[current_replace_before_str][False]=new_ng_words_mode
         
      if current_replace_before_str not in self.__replace_ng_words_by_replace_before_str[current_mode_english].keys():
         self.__replace_ng_words_by_replace_before_str[current_mode_english][current_replace_before_str]={}
      
      if re.search("[a-zA-Z]",current_replace_before_str):
        self.__replace_ng_words_by_replace_before_str[current_mode_english][current_replace_before_str][is_ignore_case]=setting_result
      #置換したい文字列の中に、アルファベットが1文字も入っていなかった場合は、大文字小文字の違いを無視する場合も無視しない場合も同じ結果になるので,
      else:
        #無視する版(True)にも無視しない版(False)にも同じ設定結果を入れる
        self.__replace_ng_words_by_replace_before_str[current_mode_english][current_replace_before_str][True]=setting_result
        self.__replace_ng_words_by_replace_before_str[current_mode_english][current_replace_before_str][False]=setting_result
        
        
      current_replace_before_str_to_ng_words=setting_result
    
    
    self.__ng_words_label["text"]=self.get_ng_words_label_str_in_each_mode(tuple(current_replace_before_str_to_ng_words))
  
  def ng_words_reset(self,event=None):
    #0が「通常(部分一致)モード」、1が「完全一致モード」、2が「ワイルドカード」、3が「正規表現モード」
    #「通常(部分一致)モード」以外では,NGワードは使用しない(できない)
    current_mode=self.__pattern_choice.current()
    if self.__pattern_choice.current() == 1:
       return 
    
    current_mode_english=mode_names_english[current_mode]
    current_replace_before_str=self.__replace_before_entry.get()
    current_mode_japanese=mode_names_japanese[current_mode]
    
    is_ignore_case=self.__ignore_case_widget_var.get()
    ignore_str="無視する" if is_ignore_case else "無視しない"
    
    if current_replace_before_str not  in self.__replace_ng_words_by_replace_before_str[current_mode_english].keys():
      messagebox.showerror("エラー",f"{current_mode_japanese}モードにおいて、置換元表現{current_replace_before_str}に対する登録されているNGワードはありませんでした")
      return
     
    if is_ignore_case not in self.__replace_ng_words_by_replace_before_str[current_mode_english][current_replace_before_str].keys():
      messagebox.showerror("エラー",f"{current_mode_japanese}モードにおいて、置換元表現{current_replace_before_str}に対する大文字小文字の違いを{ignore_str}時の登録されているNGワードはありませんでした")
      return
      
    if len(self.__replace_ng_words_by_replace_before_str[current_mode_english][current_replace_before_str][is_ignore_case]) == 0:
      messagebox.showerror("エラー",f"{current_mode_japanese}モードにおいて置換元表現{current_replace_before_str}に対する登録されているNGワードはありませんでした")
      return
    
    is_all_reset=messagebox.askyesno("NGワード削除",f"{current_mode_japanese}モードにおいて、置換元表現{current_replace_before_str}に対する登録されているNGワードをすべて削除してもよろしいですか?(NGワードの個別の削除と確認は「置換NGワード設定」ボタンで確認してください)")
    if not is_all_reset:
      self.__ng_words_label["text"]=self.get_ng_words_label_str_in_each_mode()
      return
    
    if re.search("[a-zA-Z]",current_replace_before_str):
      self.__replace_ng_words_by_replace_before_str[current_mode_english][current_replace_before_str][is_ignore_case]=[]
      messagebox.showinfo("削除完了",f"{current_mode_japanese}モードにおいて、置換元表現{current_replace_before_str}に対する大文字小文字の違いを{ignore_str}時のNGワードが削除されました")
    #アルファベットが1文字も含まれない置換元表現は、True（無視する)の場合でもFalse(無視しない)でも、文字列に差はないので、TrueもFalseもリセット(同じ内容を保つ必要がある)
    else:
      self.__replace_ng_words_by_replace_before_str[current_mode_english][current_replace_before_str][True]=[]
      self.__replace_ng_words_by_replace_before_str[current_mode_english][current_replace_before_str][False]=[]
      messagebox.showinfo("削除完了",f"{current_mode_japanese}モードにおいて、置換元表現{current_replace_before_str}に対するNGワードが削除されました")
    
    self.__ng_words_label["text"]=self.get_ng_words_label_str_in_each_mode()
    if current_mode != 3:
       return 
   
    if current_replace_before_str not in self.__ng_words_mode_in_reg_mode.keys():
       return 
    
    if is_ignore_case not in self.__ng_words_mode_in_reg_mode[current_replace_before_str].keys():
       return 
    
    self.__ng_words_mode_in_reg_mode[current_replace_before_str][is_ignore_case]="NG-p"
    if not re.search("[a-zA-Z]",current_replace_before_str):
      reversed_is_ignore_case_flag=not is_ignore_case
      self.__ng_words_mode_in_reg_mode[current_replace_before_str][reversed_is_ignore_case_flag]="NG-p"
           
    
  
  #現在のモードにおける、現在の置換前表現に対するNGワードがなんなのかを示すラベルのための文字列を返す
  #第一引数のタプルには、新たなNGワードが設定されたとき、新たなNGワード用の表示を切り替えるため、新しく登録されたNGワードのタプルを与える
  #第一引数が未入力なら、NGワードが登録されたときではなく、「モード」の切り替え時に呼ばれたということになる   
  def get_ng_words_label_str_in_each_mode(self,new_ng_words:tuple=None): 
     current_choice=self.__pattern_choice.current()
     if current_choice == 1:
       return "「1行完全一致モード」ではNGワードは登録できません"
     
     current_replace_before_str=self.__replace_before_entry.get()
     
     if len(current_replace_before_str) == 0:
       return "NGワード一覧:置換元の表現が入力されてません"
     
     label_header=f"{current_replace_before_str}に対するNGワード一覧({current_replace_before_str}が含まれているが置換しない表現):"
     #2が「ワイルドカード」、3が「正規表現モード」なので、「マッチ」という言葉のほうが適切
     if current_choice in (2,3):
       label_header=f"表現:{current_replace_before_str}に対するNGワード一覧({current_replace_before_str}にマッチするが置換しない表現):"
       
     
     if new_ng_words is not None:
        #新たに登録されたNGワードの登録個数が0ならなしと表示
        new_ng_words_with_bracket=[f"「{one_new_ng_word}」" for one_new_ng_word in new_ng_words]
        ng_words_str=(new_ng_words_with_bracket and ",".join(new_ng_words_with_bracket)) or "なし"
        return f"{label_header}:{ng_words_str}"
     
     mode_name_english=mode_names_english[current_choice]
     #現在入力されているキーワードに対するNGワードがまだ登録されていない場合
     if current_replace_before_str not in self.__replace_ng_words_by_replace_before_str[mode_name_english].keys():
        return f"{label_header}:なし"
     
     is_ignore_case=self.__ignore_case_widget_var.get()
     if is_ignore_case not in self.__replace_ng_words_by_replace_before_str[mode_name_english][current_replace_before_str].keys():
        ignore_str="無視するとき" if is_ignore_case else "無視しないとき"
        return f"{label_header}(大文字小文字の違いを{ignore_str}):なし"
     
     #登録されていた場合,空だった場合(=0個登録されている状態)なら、なしと表示し、それ以外はカンマ区切りで表示
     new_disp_ng_words=self.__replace_ng_words_by_replace_before_str[mode_name_english][current_replace_before_str][is_ignore_case]
     new_disp_ng_words_with_bracket=[f"「{one_new_disp_ng_word}」" for one_new_disp_ng_word in new_disp_ng_words]
     ng_words_str=(new_disp_ng_words_with_bracket and ",".join(new_disp_ng_words_with_bracket)) or "なし"
     
     return f"{label_header}:{ng_words_str}"
  
  #「完全一致モード」の時はNGワードは設定できないので、ボタンの無効化処理を行う
  def option_button_disp_operation(self,event=None):
    current_choice=self.__pattern_choice.current()
    
    #0が「通常(部分一致)モード」、1が「完全一致モード」、2が「ワイルドカード」、3が「正規表現モード」
    if current_choice == 1:
      self.__option_setting_button["state"]="disable"
      self.__ng_words_reset_btn["state"]="disable"
      self.__ng_words_label["text"]="1行完全一致モード」ではNGワードは登録できません"
      return
    
    self.__option_setting_button["state"]="normal"
    self.__ng_words_reset_btn["state"]="normal"
     
    current_replace_before_str=self.__replace_before_entry.get()
    if len(current_replace_before_str) == 0:
       self.__ng_words_label["text"]="NGワード一覧:置換元の表現が入力されてません"
       return
    
    if current_choice == 3:
      try:
         #入力された正規表現が正しいかどうかダミーのデータで確かめる
         re.sub(current_replace_before_str,"","hoge")
      except re.error:
         self.__ng_words_label["text"]="NGワード一覧:置換元の表現が不正です"
         return 
    
    if current_choice == 2:
      try:
         #入力されたワイルドカードが正しいかどうかダミーのデータで確かめる
         re.sub(Replacer.wildcard_to_reg_exp(current_replace_before_str),"","hoge")
      except re.error:
         self.__ng_words_label["text"]="NGワード一覧:置換元の表現が不正です"
         return 
         
    
    self.__ng_words_label["text"]=self.get_ng_words_label_str_in_each_mode()

  
  def mode_choide_operation_by_verical_key(self,event):
    pressed_key=event.keysym
    current_choice=self.__pattern_choice.current()
    next_choice=current_choice
    if pressed_key == "Up":
       next_choice=current_choice-1
       #剰余演算子よりこちらの方が早い
       if next_choice == -1:
         next_choice=len(self.__pattern_choice["values"])-1
       self.__pattern_choice.current(next_choice)
       self.option_button_disp_operation()
    if pressed_key == "Down":
       next_choice=current_choice+1
       #剰余演算子よりこちらの方が早い
       if len(self.__pattern_choice["values"]) == next_choice:
         next_choice=0
       self.__pattern_choice.current(next_choice)
       self.option_button_disp_operation()
  
  
  #エントリー欄が初期状態であるか否かを調べる
  #上記の保存データをクラスに引き渡す際にこのメソッドを利用し、このメソッドがFalseを返したときは初期状態のままということ
  #このメソッドがFalseを返したときはわざわざ、保存用データを作らなくてよい(データ削減のためわざわざ行う)
  def has_any_entry_changed(self):
    if len(self.__replace_before_entry.get()) != 0:
       return True
    if len(self.__replace_after_entry.get()) != 0:
       return True
    if self.__pattern_choice.current() != 0:
       return True
    if self.__ignore_case_widget_var.get():
       return True
    
    for ng_lists in self.__replace_ng_words_by_replace_before_str.values():
      if ng_lists:
         return True
    
    for is_ignore_case_ng_word_mode_str_dict in self.__ng_words_mode_in_reg_mode.values():
       for ng_words_mode_str in is_ignore_case_ng_word_mode_str_dict.values():
          if ng_words_mode_str == "NG-e":
             return True
    
    return False
    
  
  def get_current_ng_words_mode_in_reg_mode(self):
    is_ignore_case=self.__ignore_case_widget_var.get()
    current_mode=self.__pattern_choice.current()
    current_replace_before_str=self.__replace_before_entry.get()
    
    if current_mode != 3:
      return "NG-p"
    
    if current_replace_before_str not in self.__ng_words_mode_in_reg_mode.keys():
       return "NG-p"
    if is_ignore_case not in self.__ng_words_mode_in_reg_mode[current_replace_before_str].keys():
       return "NG-p"
    
    return self.__ng_words_mode_in_reg_mode[current_replace_before_str][is_ignore_case]
  
  
  @classmethod
  def reset_id(cls):
     cls.__current_entry_id=1
  
  #置換ワード設定は、画面の都合上別のダイアログで行うため、その設定ダイアログをユーザーが閉じたとき、このままではデータが消えてしまうので
  #以下のEntriesDataRepositoryクラスでこれまで入力してきたデータを保存して、その保存クラスの情報をもとに、再度、ダイアログが開かれた際に入力欄として起こしなおすメソッド
  @classmethod
  def parse_entries_from_data(cls,master,data_obj):
     new_obj=cls(master)
     new_obj.__replace_before_entry.insert(0,data_obj.replace_before_str)
     new_obj.__replace_after_entry.insert(0,data_obj.replace_after_str)
     new_obj.__replace_ng_words_by_replace_before_str=data_obj.ng_words_by_replace_before_str
     new_obj.__ignore_case_widget_var.set(data_obj.is_ignore_case)
     new_obj.__pattern_choice.current(data_obj.replace_mode_num)
     new_obj.option_button_disp_operation()
     new_obj.__ng_words_mode_in_reg_mode=data_obj.ng_words_mode_in_reg_mode
     return new_obj



#置換ワード設定ダイアログを閉じた後でも、これまで入力してきたデータを保存できるようにする
#一度設定用ダイアログを閉じて、再度ダイアログを開きなおしても、閉じる前の状態から再開できるようにするためのデータの保存場
#本当にただの構造体みたいなもの
class EntriesDataRepository:
    
   def __init__(self,replace_before_str:str,replace_after_str:str,mode_num:int,is_ignore_case:bool,ng_words_dict:dict,ng_words_mode_in_reg_mode:dict):
      self.__replace_before_str=replace_before_str
      self.__replace_after_str=replace_after_str
      #置換モードの数字(0は通常(部分一致),1は1行完全一致,2はワイルドカード,3は正規表現・・ドロップダウンリストとして起こしやすくするため、ここでは数字で保存)
      self.__replace_mode_num=0
      if 0 <= mode_num and mode_num < 4:
         self.__replace_mode_num=mode_num
      
      self.__is_ignore_case=is_ignore_case
      #入れ子の多重辞書なのでディープコピー
      self.__ng_words_by_replace_before_str=eval(repr(ng_words_dict))
      
      #NGワード登録時の「置換外しモード」(正規表現の時にしか使わないけど)
      self.__ng_words_mode_in_reg_mode=eval(repr(ng_words_mode_in_reg_mode))
      
   
   #入力内容から置換情報をまとめたReplaceInformationクラスのインスタンスを得る
   #なお、入力内容が正しいかどうかの確認は呼び出し元ReplacePatternEntriesCornerですでに行っているので考えなくてよい
   #(=ここで正しくないと判定されたときはこのクラスのインスタンスが作られないよう制御されている)
   def get_replace_information_obj(self):
     mode_name_english=mode_names_english[self.__replace_mode_num]
     
     #両入力欄ともに未入力の場合は、入力ミスではなく、「この箇所は置換するものがないですよ」という意思表示なので
     #置換情報(ReplaceInformation)はNoneを返す(上記の通り入力ミスではないので、インスタンスは作られて、ここに飛ぶ)
     if len(self.__replace_before_str) == 0 and len(self.__replace_after_str) == 0:
       return None
       
     ng_list=()
      #「1行完全一致モード」の場合は,NGワードが設定できないので、どんな場合でも空タプルとなる
     if self.__replace_mode_num == 1:
        pass
     elif self.__replace_before_str in self.__ng_words_by_replace_before_str[mode_name_english].keys():
       if self.__is_ignore_case in self.__ng_words_by_replace_before_str[mode_name_english][self.__replace_before_str].keys():
         ng_list=tuple(self.__ng_words_by_replace_before_str[mode_name_english][self.__replace_before_str][self.__is_ignore_case])
     
     if self.__replace_mode_num != 3:
       return ReplaceInformation(self.__replace_before_str,self.__replace_after_str,mode_name_english,self.__is_ignore_case,ng_list)
     
     current_ng_words_mode=self.get_current_ng_words_mode_str()
     return ReplaceInformation(self.__replace_before_str,self.__replace_after_str,mode_name_english,self.__is_ignore_case,ng_list,current_ng_words_mode)
   
   def get_current_ng_words_mode_str(self):
     if self.__replace_mode_num != 3:
       return "NG-p"
     
     if self.__replace_before_str not in self.__ng_words_mode_in_reg_mode.keys():
       return "NG-p"
     
     if self.__is_ignore_case not in self.__ng_words_mode_in_reg_mode[self.__replace_before_str].keys():
       return "NG-p"
     
     return self.__ng_words_mode_in_reg_mode[self.__replace_before_str][self.__is_ignore_case]
   
   def __str__(self):
     if len(self.__replace_before_str) == 0 and len(self.__replace_after_str) == 0:
        return "未入力"
     
     replace_before_label=f"「{self.__replace_before_str}」を" if self.__replace_mode_num in (0,1) else f"「{self.__replace_before_str}」にマッチする文字列を"
     replace_after_label=f"「{self.__replace_after_str}」に置換" if len(self.__replace_after_str) != 0 else f"削除"
     
     current_mode_japanese=f"置換モード:{mode_names_japanese[self.__replace_mode_num]}"
     ignore_case_str="大文字小文字の違いの無視:する" if self.__is_ignore_case else "大文字小文字の違いの無視:しない"
     
     ng_list_label="登録されたNGワード:なし"
     current_mode_english=mode_names_english[self.__replace_mode_num]
     
     ng_words_mode_str=""
     
     if self.__replace_mode_num == 1:
       pass
     elif self.__replace_before_str not in self.__ng_words_by_replace_before_str[current_mode_english].keys():
       pass
     elif self.__is_ignore_case in self.__ng_words_by_replace_before_str[current_mode_english][self.__replace_before_str].keys():
       ng_words_list=self.__ng_words_by_replace_before_str[current_mode_english][self.__replace_before_str][self.__is_ignore_case]
       if len(ng_words_list) != 0:
         ng_words_list_with_bra=[f"「{one_ng_word}」" for one_ng_word in ng_words_list]
         ng_words_str=",".join(ng_words_list_with_bra)
         ng_list_label=f"登録されたNGワード:{ng_words_str}"
         if self.__replace_mode_num == 3:
           ng_words_mode_japanese={"NG-p":"部分一致外し","NG-e":"完全一致外し"}
           current_ng_words_mode=self.get_current_ng_words_mode_str()
           ng_words_mode_str=f"(NGワードの取り扱い方法:{ng_words_mode_japanese[current_ng_words_mode]})"
             
     return f"置換内容:{replace_before_label}{replace_after_label}\n{current_mode_japanese}\n{ignore_case_str}\n{ng_list_label}{ng_words_mode_str}"
     
   
   def __repr__(self):
     return f"{self.__class__.__name__}(\"{self.__replace_before_str}\",\"{self.__replace_after_str}\",{self.__replace_mode_num},{self.__is_ignore_case},{self.__ng_words_by_replace_before_str},\"{self.__ng_words_mode_in_reg_mode}\")"
   
   
   @property
   def replace_before_str(self):
     return self.__replace_before_str
   
   @property
   def replace_after_str(self):
     return self.__replace_after_str
   
   @property
   def replace_mode_num(self):
     return self.__replace_mode_num
   
   @property
   def is_ignore_case(self):
     return self.__is_ignore_case
   
   @property
   def ng_words_by_replace_before_str(self):
     return eval(repr(self.__ng_words_by_replace_before_str))
   
   @property
   def ng_words_mode_in_reg_mode(self):
     return eval(repr(self.__ng_words_mode_in_reg_mode))



