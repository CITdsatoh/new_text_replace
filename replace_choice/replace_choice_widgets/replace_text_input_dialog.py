#encoding:utf-8;

from tkinter import simpledialog,messagebox
from replace_choice.replace_choice_widgets.patterns_entry import ReplacePatternEntriesCorner
import tkinter as tk


class ReplaceTextInputDialog(simpledialog.Dialog):
    
    def __init__(self,parent,entry_datas:tuple):
      self.__current_disp_page=0
      ReplacePatternEntriesCorner.reset_id()
      self.__entry_corners=[]
      
      self.__entry_datas=entry_datas
      
      super().__init__(parent)
      
    
    def buttonbox(self):
      self.__title_label=tk.Label(self,text="ファイルテキスト一括置換～置換ワード登録～",font=("serif",18,"bold"))
      self.__title_label.place(x=384,y=0)
      explaination_str="ここでは、ファイル内に存在する指定した置換元文字列、あるいは置換元表現にマッチする文字列をすべて一括で指定した置換後文字列へ置換できます\n置換は1度に最大20件まで行うことができ、その1から順に入力欄の番号が若いほうから順に行います\nなお、置換後文字列が空白の場合、置換元文字列ならびに表現にマッチする文字列をすべて削除することができます"
      self.__explaination_label=tk.Label(self,text=explaination_str,font=("serif",12,"bold"))
      self.__explaination_label.place(x=32,y=40)
      
      self.__replace_before_label=tk.Label(self,text="置換元文字列・表現",font=("times",11,"bold"))
      self.__replace_before_label.place(x=96,y=112)
     
      self.__mode_label=tk.Label(self,text="置換モード",font=("times",11,"bold"))
      self.__mode_label.place(x=288,y=112)
      
      self.__mode_explaination_btn=tk.Button(self,text="詳しく",font=("times",8))
      self.__mode_explaination_btn.place(x=384,y=112)
      self.__mode_explaination_btn.bind("<Button-1>",self.disp_mode_explaination_dialog)
     
      self.__replace_after_label=tk.Label(self,text="置換後文字列",font=("times",11,"bold"))
      self.__replace_after_label.place(x=448,y=112)
      
      self.__page_back_button=tk.Button(self,text="前ページへ戻る",font=("times",11))
      self.__page_back_button.bind("<Button-1>",self.page_back)
      
      self.__jump_page_entry=tk.Entry(self,width=2,font=("times",11))
      self.__jump_page_entry.place(x=256,y=608)
      self.__jump_page_entry.insert(0,"1")
      self.__jump_page_label=tk.Label(self,text="ページ(1-4)",font=("times",11))
      self.__jump_page_label.place(x=320,y=608)
      self.__jump_page_button=tk.Button(self,text="へ移動",font=("times",11))
      self.__jump_page_button.place(x=480,y=608)
      self.__jump_page_button.bind("<Button-1>",self.page_jump)
      self.__page_fin_label=tk.Label(self,text="/5ページ",font=("times",11))
      self.__page_fin_label.place(x=544,y=608)
      
      self.__page_advance_button=tk.Button(self,text="次のページへ進む",font=("times",11))
      self.__page_advance_button.place(x=768,y=608)
      self.__page_advance_button.bind("<Button-1>",self.page_advance)
      
      self.__cancel_button=tk.Button(self,text="登録をキャンセル",font=("times",11))
      self.__cancel_button.place(x=224,y=656)
      self.__cancel_button.bind("<Button-1>",self.cancel)
      
      self.__all_input_cancel_button=tk.Button(self,text="全入力欄の入力取消",font=("times",11))
      self.__all_input_cancel_button.place(x=384,y=656)
      self.__all_input_cancel_button.bind("<Button-1>",self.all_input_cancel)
      
      self.__regist_ok_btn=tk.Button(self,text="内容決定",font=("times",11,"bold"))
      self.__regist_ok_btn.place(x=576,y=656)
      self.__regist_ok_btn.bind("<Button-1>",self.ok)
      
      self.bind("<Escape>",self.cancel)
      self.bind("<Return>",self.ok)
      
      for one_entry_data in self.__entry_datas:
        if one_entry_data is None:
          new_corner=ReplacePatternEntriesCorner(self)
          self.__entry_corners.append(new_corner)
          continue
        new_corner=ReplacePatternEntriesCorner.parse_entries_from_data(self,one_entry_data)
        self.__entry_corners.append(new_corner)
      
      for i in range(0,4):
        self.__entry_corners[i].place(x=56,y=144+(i*112))
      
      self.geometry("1200x750")
      
    
    def validate(self):
      #全20個の入力欄を1つずつ確認し、1つでも入力がおかしい箇所があればFalseを返すことが確定するものの,
      #入力がおかしい欄をすべて確認してから,Falseを返したいので、早期returnせず、フラグ変数を用いる
      is_all_ok=True
      
      error_corners_num=[]
      
      all_inputs=[]
      for i,one_entry_corner in enumerate(self.__entry_corners):
        if not  one_entry_corner.has_any_entry_changed():
           all_inputs.append(None)
           continue
        entry_data=one_entry_corner.get_entries_data()
        if entry_data is None:
           is_all_ok=False
           error_corners_num.append(i)
           continue
        all_inputs.append(entry_data)
      
      
      if not is_all_ok:
        error_corners_num_strs=[f"その{one_num+1}" for one_num in error_corners_num]
        error_corners_whole_str=",".join(error_corners_num_strs)
        messagebox.showerror("入力エラー",f"入力エラーの箇所が{len(error_corners_num)}箇所ありました.具体的には以下の通りです.\n{error_corners_whole_str}\n修正後もう一度実行しなおしてください")
        self.one_page_entries_place_forget()
        first_error_page=int(error_corners_num[0]/4)
        self.one_page_entries_place(first_error_page)
        self.__jump_page_entry.delete(0,tk.END)
        self.__jump_page_entry.insert(0,f"{first_error_page+1}")
        self.back_advance_btn_disp_change(first_error_page)
        self.__jump_page_label["text"]=f"ページ({first_error_page*4+1}-{(first_error_page+1)*4})"
        self.__current_disp_page=first_error_page
        return False
      
      if not any(all_inputs):
        messagebox.showerror("エラー","置換ワードが1箇所も入力されていません。置換をする場合,最低でも1か所は入力してください")
        return False
      
      #最終結果(ダイアログを閉じた後に呼び出し先に引き戻す、ここまでの入力データ)
      self.result=all_inputs[:]
      return True
     
      
    #「登録キャンセル」
    def cancel(self,event=None):
      if self.result is None:
        is_exit=messagebox.askyesno("登録キャンセル","置換ワード登録をやめますか?(やめた場合,ダイアログを開いてから現在まで入力したデータは保存されず、ダイアログを開く前の状態に戻ります)")
        if not is_exit:
          return
          
      super().cancel()
    
    #「全入力欄初期化」・・ここは入力欄の取り消し(=20の入力欄を全部空白にして,ラベルなどを初期表示に戻す)のみを行う。
    #これまで入力したすべてのデータの取り消しはユーザーがこれを実行した後に、「内容決定」ボタンを押さない限り行わない。
    #つまり、これを実行した後でも、キャンセルボタンを押せば、ダイアログを開く前のデータは保存されたままでよい
    def all_input_cancel(self,event=None):
      is_all_cancel=messagebox.askyesno("入力欄全消去","これまでに行った入力を本当にすべて取り消してもよろしいでしょうか?(1つの入力欄の入力を取り消したい場合は各入力欄右側の「入力を取消」ボタンを押してください)")
      if not is_all_cancel:
        return
      
      for one_entry_corner in self.__entry_corners:
        one_entry_corner.all_reset()
      
      self.one_page_entries_place_forget()
      self.one_page_entries_place(0)
      self.back_advance_btn_disp_change(0)
      self.__current_disp_page=0
      self.__jump_page_entry.delete(0,tk.END)
      self.__jump_page_entry.insert(0,f"1")
      self.__jump_page_label["text"]=f"ページ(1-4)"
      
    
    
    #「前のページへ戻る」時の処理
    def page_back(self,event=None):
      if self.__current_disp_page <= 0:
         return
      
      self.one_page_entries_place_forget()  
      self.__current_disp_page -= 1
      self.one_page_entries_place()
      
      self.__jump_page_entry.delete(0,tk.END)
      self.__jump_page_entry.insert(0,f"{self.__current_disp_page+1}")
      self.__jump_page_label["text"]=f"ページ({self.__current_disp_page*4+1}-{(self.__current_disp_page+1)*4})"
      
      #一番先頭のページに戻ってきたとき
      if self.__current_disp_page == 0:
        self.__page_back_button.place_forget()
      #一番最後のページから、最後から2番目のページに戻ってきたとき
      elif self.__current_disp_page == 3:
        self.__page_advance_button.place(x=768,y=608)
     
    def page_advance(self,event=None):
      if 4 <= self.__current_disp_page:
         return 
         
      self.one_page_entries_place_forget()
      self.__current_disp_page += 1
      self.one_page_entries_place()
      
      self.__jump_page_entry.delete(0,tk.END)
      self.__jump_page_entry.insert(0,f"{self.__current_disp_page+1}")
      self.__jump_page_label["text"]=f"ページ({self.__current_disp_page*4+1}-{(self.__current_disp_page+1)*4})"
      
      #一番最後のページにたどり着いたとき
      if self.__current_disp_page == 4:
          self.__page_advance_button.place_forget()
      #1番最初のページから２番目のページにたどり着いたとき
      elif self.__current_disp_page == 1:
          self.__page_back_button.place(x=32,y=608)
     
    #指定されたページに飛ぶとき
    def page_jump(self,event=None):
      new_page=self.__current_disp_page
      try:
        new_page_str=self.__jump_page_entry.get()
        new_page=int(new_page_str)-1
      #整数以外の入力
      except ValueError:
        messagebox.showerror("エラー","ページ数に数字以外が入力されました。ページ数には1から5の整数を入力してください")
        self.__jump_page_entry.delete(0,tk.END)
        self.__jump_page_entry.insert(0,f"{self.__current_disp_page+1}")
        return 
        
      if new_page < 0:
        messagebox.showerror("エラー","指定された数字のページはありません。ページ数は1以上5以下の整数を入力してください!")
        self.__jump_page_entry.delete(0,tk.END)
        self.__jump_page_entry.insert(0,f"{self.__current_disp_page+1}")
        return 
        
      if 4 < new_page:
        messagebox.showerror("エラー","指定された数字のページはありません。ページ数は1以上5以下の整数を入力してください!")
        self.__jump_page_entry.delete(0,tk.END)
        self.__jump_page_entry.insert(0,f"{self.__current_disp_page+1}")
        return 
        
      #以下は正常処理(1から5の整数が入力されたとき)
      #ただし、ここでは1が入力されたときは0,2が入力されたときは1・・というように1引いた数となっているので,
      #0ページ目が最初のページ(=1が入力されたとき),4ページ目が最後のページ(=5が入力されたとき)
        
      #「前のページへ戻る」、「次のページへ進む」ボタンの取り付け・取り外し操作
      self.back_advance_btn_disp_change(new_page)
        
      self.one_page_entries_place_forget()
      self.one_page_entries_place(new_page)
      self.__jump_page_label["text"]=f"ページ({new_page*4+1}-{(new_page+1)*4})"
      self.__current_disp_page=new_page
     
    #指定したページのウィジェットの取り付け
    #ここでは取り付けのみ
    def one_page_entries_place(self,new_page_num:int=None):
      if new_page_num is None:
        new_page_num=self.__current_disp_page
        
      if new_page_num < 0 or 4 < new_page_num:
        return 
        
      start_entries_id=4*new_page_num
      for i in range(start_entries_id,start_entries_id+4):
        self.__entry_corners[i].place(x=56,y=144+((i%4)*112))
     
    #指定したページ番号のウィジェットの取り外し
    #ここでは取り外しのみ
    def one_page_entries_place_forget(self,new_page_num:int=None):
      if new_page_num is None:
        new_page_num=self.__current_disp_page
        
      if new_page_num < 0 or 4 < new_page_num:
        return 
        
      start_entries_id=4*new_page_num
      for i in range(start_entries_id,start_entries_id+4):
        self.__entry_corners[i].place_forget()
      
      
    #前に戻る/次に進むボタンではなく一気にページ遷移するときの「前に戻るボタン」と「次へ進むボタン」の取り付け・取り外しメソッド
    def back_advance_btn_disp_change(self,new_page:int):
      if new_page < 0 or 4 < new_page:
        return 
          
      #0ページ目が最初のページ(=1が入力されたとき),4ページ目が最後のページ(=5が入力されたとき)
      #もともと最初のページにいて,遷移先が最初のページ以外なら戻るボタン復活
      if self.__current_disp_page == 0 and new_page != 0:
        self.__page_back_button.place(x=32,y=608)
        
      #もともと最初以外のページにいて,遷移先が最初のページなら戻るボタンを消す
      if self.__current_disp_page != 0 and new_page == 0:
        self.__page_back_button.place_forget()
        
      #もともと最後のページにいて、遷移先が最後のページ以外なら進むボタン復活
      if self.__current_disp_page == 4 and new_page != 4:
        self.__page_advance_button.place(x=768,y=608)
        
      #もともと最後以外のページにいて、遷移先が最後のページなら進むボタン削除
      if self.__current_disp_page != 4 and new_page == 4:
        self.__page_advance_button.place_forget()
    
    #「各モード」の説明ダイアログ表示
    def disp_mode_explaination_dialog(self,event=None): 
      dialog=ModeExplainDialog(self) 


class ModeExplainDialog(simpledialog.Dialog):
   
   
   def __init__(self,parent=None,title:str="置換モードとは?(詳細説明)"):
     super().__init__(parent,title)
  
   def buttonbox(self):
     self.__main_title=tk.Label(self,text="置換モードとは?",font=("serif",18,"bold"))
     self.__main_title.place(x=256,y=0)
     
     self.__partial_mode_explain_frame=tk.Frame(self,width=1024,height=152,relief=tk.SOLID,borderwidth=3)
     self.__partial_mode_title=tk.Label(self.__partial_mode_explain_frame,text="通常(部分一致)モードとは?",font=("serif",12,"bold"))
     self.__partial_mode_title.place(x=0,y=0)
     self.__partial_mode_label_former=tk.Label(self.__partial_mode_explain_frame,text="他の多数のアプリ同様、通常通り、入力した置換前文字列に一致するものをそのまま置換後文字列へ置換するモードです。\n例：以下の文字列の「バナナ」を「リンゴ」に置換する場合",font=("times",9))
     self.__partial_mode_label_former.place(x=16,y=24)
     self.__partial_mode_label_example_header=tk.Label(self.__partial_mode_explain_frame,text="例:",font=("times",9,"bold"))
     self.__partial_mode_label_example_header.place(x=80,y=72)
     self.__partial_mode_label_example_before=tk.Label(self.__partial_mode_explain_frame,text="バナナおいしい。バナナは食べやすい。バ\nナナは黄色い。バナナマン好き。",font=("times",9,"bold"),bg="#d9d9d9")
     self.__partial_mode_label_example_before.place(x=128,y=72)
     self.__partial_mode_arrow=tk.Label(self.__partial_mode_explain_frame,text="置換後\n→",font=("times",9))
     self.__partial_mode_arrow.place(x=512,y=72)
     self.__partial_mode_label_example_after=tk.Label(self.__partial_mode_explain_frame,text="リンゴおいしい。リンゴは食べやすい。バ\nナナは黄色い。リンゴマン好き。",font=("times",9,"bold"),bg="#d9d9d9")
     self.__partial_mode_label_example_after.place(x=576,y=72)
     self.__partial_mode_label_latter=tk.Label(self.__partial_mode_explain_frame,text="このように、「バナナ」に一致するものがすべて、「リンゴ」に変わります。ただし、置換は行単位で行うので、2行にまたがっているものは置換されませんのでお気をつけください.",font=("times",9))
     self.__partial_mode_label_latter.place(x=16,y=120)
     
     self.__partial_mode_explain_frame.place(x=16,y=32)
     
     self.__exact_mode_explain_frame=tk.Frame(self,width=1024,height=168,relief=tk.SOLID,borderwidth=3)
     self.__exact_mode_title=tk.Label(self.__exact_mode_explain_frame,text="1行完全一致モードとは?",font=("serif",12,"bold"))
     self.__exact_mode_title.place(x=0,y=0)
     self.__exact_mode_label_former=tk.Label(self.__exact_mode_explain_frame,text="ある1行の内容が、入力した置換前文字列と全く同じだった場合に置換後文字列に置換するモードです。通常モードと異なりただ一致しただけでは置換されません。\n例:以下の文字列の「いちご」を「メロン」に置換する場合.",font=("times",9))
     self.__exact_mode_label_former.place(x=16,y=24)
     self.__exact_mode_label_example_header=tk.Label(self.__exact_mode_explain_frame,text="例:",font=("times",9,"bold"))
     self.__exact_mode_label_example_header.place(x=80,y=72)
     self.__exact_mode_label_example_before=tk.Label(self.__exact_mode_explain_frame,text="いちごは赤くておいしい\nいちご\nいちご味のヨーグルト好き",font=("times",9,"bold"),bg="#d9d9d9")
     self.__exact_mode_label_example_before.place(x=128,y=72)
     self.__exact_mode_arrow=tk.Label(self.__exact_mode_explain_frame,text="置換後\n→",font=("times",9))
     self.__exact_mode_arrow.place(x=384,y=72)
     self.__exact_mode_label_example_after=tk.Label(self.__exact_mode_explain_frame,text="いちごは赤くておいしい\nメロン\nいちご味のヨーグルト好き",font=("times",9,"bold"),bg="#d9d9d9")
     self.__exact_mode_label_example_after.place(x=512,y=72)
     self.__exact_mode_label_latter=tk.Label(self.__exact_mode_explain_frame,text="このように、1行(改行から次の改行までの間)の内容が、「いちご」だった場合にのみそのまま、「メロン」に置換されます。",font=("times",9))
     self.__exact_mode_label_latter.place(x=16,y=136)
     
     self.__exact_mode_explain_frame.place(x=16,y=192)
     
     self.__wc_mode_explain_frame=tk.Frame(self,width=1024,height=160,relief=tk.SOLID,borderwidth=3)
     self.__wc_mode_title=tk.Label(self.__wc_mode_explain_frame,text="ワイルドカードモードとは?",font=("serif",12,"bold"))
     self.__wc_mode_title.place(x=0,y=0)
     self.__wc_mode_label_former=tk.Label(self.__wc_mode_explain_frame,text="名の通り、置換元文字列・表現の箇所に入力したワイルドカード表現にマッチする文字列を一気に置換できるモードです。使用できる表現は「*」(任意の長さの文字列),「?」(任意の\n1文字),「[]」(この中の任意の1文字)の3つです。また、「*」と「?」という文字自体を検索したい場合はそれぞれ、「[*]」,「[?]」というように,[]に入れることでエスケープしてください。\n例:以下の文字列の「第?回:」とワイルドカードにマッチした表現を「・」に置換する場合",font=("times",9))
     self.__wc_mode_label_former.place(x=16,y=24)
     self.__wc_mode_label_example_header=tk.Label(self.__wc_mode_explain_frame,text="例:",font=("times",9,"bold"))
     self.__wc_mode_label_example_header.place(x=16,y=72)
     self.__wc_mode_label_example_before=tk.Label(self.__wc_mode_explain_frame,text="ゲスト 第1回:狩野英孝 第2回:春日俊彰 第3回:澤部佑 第10回:久保田かずのぶ",font=("times",9,"bold"),bg="#d9d9d9")
     self.__wc_mode_label_example_before.place(x=48,y=72)
     self.__wc_mode_arrow=tk.Label(self.__wc_mode_explain_frame,text="置換後→",font=("times",9))
     self.__wc_mode_arrow.place(x=512,y=72)
     self.__wc_mode_label_example_after=tk.Label(self.__wc_mode_explain_frame,text="ゲスト ・狩野英孝 ・春日俊彰 ・澤部佑 第10回:久保田かずのぶ",font=("times",9,"bold"),bg="#d9d9d9")
     self.__wc_mode_label_example_after.place(x=576,y=72)
     self.__wc_mode_label_latter=tk.Label(self.__wc_mode_explain_frame,text="このように、「第?(任意の1文字)回:」に一致する、「第1回:」、「第2回:」、「第3回:」が「・」に一気に置換されました。一方で「第10回:」の部分は、「第?回:」に\n一致しませんので、置換されませんでした。なお、代わりに「第*(任意の長さの文字列)回:」も使えますが、\nこの場合、置換結果は、「・久保田かずのぶ」になります。これは、任意の長さの「*」が「1回:狩野英孝 第2回:春日俊彰 第3回:澤部佑 第10」まですべて一致されるとみなされるからです。\n「*」を使用する際は、場合によっては意図した結果とならない場合がございますので、注意してください。",font=("times",9))
     self.__wc_mode_label_latter.place(x=0,y=96)
     
     self.__wc_mode_explain_frame.place(x=16,y=368)
     
     self.__re_mode_explain_frame=tk.Frame(self,width=1024,height=128,relief=tk.SOLID,borderwidth=3)
     self.__re_mode_title=tk.Label(self.__re_mode_explain_frame,text="正規表現モードとは?",font=("serif",12,"bold"))
     self.__re_mode_title.place(x=0,y=0)
     self.__re_mode_label_former=tk.Label(self.__re_mode_explain_frame,text="名の通り、置換元文字列・表現の箇所に正規表現にマッチする文字列を一気に置換できるモードです。正規表現のエンジンはPython3です。\n例:以下の文字列の「[a-zA-Z]{3}」という正規表現にマッチした表現を「英字3字」という文字列に置換する場合",font=("times",9))
     self.__re_mode_label_former.place(x=16,y=24)
     self.__re_mode_label_example_header=tk.Label(self.__re_mode_explain_frame,text="例:",font=("times",9,"bold"))
     self.__re_mode_label_example_header.place(x=80,y=56)
     self.__re_mode_label_example_before=tk.Label(self.__re_mode_explain_frame,text="ああいい天気。It's sunny.\n今日はgood day。どこか出かけたいね。",font=("times",9,"bold"),bg="#d9d9d9")
     self.__re_mode_label_example_before.place(x=128,y=56)
     self.__re_mode_arrow=tk.Label(self.__re_mode_explain_frame,text="置換後\n→",font=("times",9))
     self.__re_mode_arrow.place(x=384,y=56)
     self.__re_mode_label_example_after=tk.Label(self.__re_mode_explain_frame,text="ああいい天気。It's 英字3字ny.\n今日は英字3字d 英字3字。どこか出かけたいね。",font=("times",9,"bold"),bg="#d9d9d9")
     self.__re_mode_label_example_after.place(x=448,y=56)
     self.__re_mode_label_latter=tk.Label(self.__re_mode_explain_frame,text="このように、「[a-zA-Z]{3}」という英字3字を表す正規表現にマッチした文字列が、すべてが「英字3字」という文字列に一気に置換されました\nこのように、正規表現にマッチするものを一気に置換することができます。ただし、他のモード同様、行をまたいだ置換と、不定の長さの後読み先読みは利用できませんのでご注意ください",font=("times",9))
     self.__re_mode_label_latter.place(x=0,y=88)
     
     self.__re_mode_explain_frame.place(x=16,y=536)
     
     self.__exit_button=tk.Button(self,text="了解",font=("times",11,"bold"))
     self.__exit_button.place(x=512,y=664)
     self.__exit_button.bind("<Button-1>",self.ok)
     
     self.geometry("1040x768")
     self.bind("<Escape>",self.cancel)
     self.bind("<Return>",self.ok)
     