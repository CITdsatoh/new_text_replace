#encoding:utf-8;


from tkinter import messagebox,simpledialog
import tkinter as tk
from replace_choice.text_replace.str_replacer import Replacer
import tkinter.ttk as ttk
import re

class NGWordSettingDialog(simpledialog.Dialog):

   #正規表現モードの時は、置換外しのモードを表す情報も必要
   ng_word_mode_names=("NG-p","NG-e")
   
   
   #第一引数は,置換したいワード
   #第二引数は、前回までに登録したNGワード集(=呼び出すたびに取り消さず、前回登録したのも見えるようにするため)
   def __init__(self,replace_before_str:str,replace_mode:str,is_ignore_case:bool=False,old_ng_words:tuple=None,ng_words_mode_in_reg_mode:str="NG-p",parent=None,title:str="置換NGワード設定ダイアログ"):
     self.__ng_words=(old_ng_words and list(old_ng_words)) or []
     self.__replace_before_str=replace_before_str
     self.__replace_mode="p"
     if replace_mode in ("p","wc","re"):
       self.__replace_mode=replace_mode
       
     #ngワードの入力欄
     self.__ng_word_corners=[]
     
     #正規表現モードの時の置換外しモードの文字列
     self.__ng_words_mode_in_reg_mode="NG-p"
     if ng_words_mode_in_reg_mode in self.__class__.ng_word_mode_names:
         self.__ng_words_mode_in_reg_mode=ng_words_mode_in_reg_mode
     
     self.__is_ignore_case=is_ignore_case
     
     super().__init__(parent,title)
     
     
     
   
   def buttonbox(self):
     self.__title_label=tk.Label(self,text="置換NGワード設定",font=("serif",18,"bold"))
     self.__title_label.place(x=224,y=16)
     p_explaination_str="置換NGワードとは?(通常モード)\n置換NGワードとは,ある置換したい単語に対し、その単語が含まれているけど置換したくない言葉を設定することができます。\n例えば、「京都」という言葉を「奈良」に置換した場合\nこのままでは、「東京都」という単語は「東奈良」に、「京都府」という単語は「奈良府」になってしまいます。\nですが、ここでNGワードとして、「東京都」と「京都府」を登録しておけば、\nこれらの単語は「京都」という文字列がつきますが、その部分は「奈良」に置換されなくなります。\n置換1件に対し10個まで設定できます。\nなお、NGワードは、現在置換しようとしている組み合わせにのみに適用されます。\nですので、同時に複数の文字列を置換する際、この置換でNGワードとして登録したものであっても、\n他の箇所で置換対象に当てはまり置換されてしまうということもございますのでご留意ください。"
     wc_explaination_str="置換NGワードとは?(ワイルドカード)\n置換NGワードとは,あるワイルドカードにマッチする文字列を一括で置換したいのに対し、ある特定の、そのワイルドカード表現\nに一致するけど置換したくない言葉を設定することができます。\n例えば、「*川」という表現に一致するワードを他の言葉に置換する場合、「鴨川」、「淀川」、「利根川」、\n「江戸川」、「旧江戸川」、「東京都と千葉県の間を流れる旧江戸川」のいずれも\n「*川」にマッチするので、他の言葉に表現に置換されてしまいます。\nですが、例えば、「江戸川」という言葉をNGワードとして設定した場合,「江戸川」、「旧江戸川」、\n「東京都と千葉県の間を流れる旧江戸川」など「*川」に一致するけど、「江戸川」という言葉がつくものは置換の対象から外れます。\nこのNGワードは置換1件に対し10個まで設定できます。\nなお、NGワードは、現在置換しようとしている組み合わせにのみに適用されます。\nですので、同時に複数の文字列を置換する際、この置換でNGワードとして登録したものであっても、\n他の箇所で置換対象に当てはまり置換されてしまうということもございますのでご留意ください。"
     re_explaination_str="置換NGワードとは?(正規表現)\n置換NGワードとは、ある正規表現のパターンに当てはまる文字列を一括で置換したいものの、ある特定の言葉のみ正規表現のパターンに一致するけど、\n置換したくない言葉を設定します\n例えば、「.{2,4}川」という表現が入力された際、「江戸川」、「利根川」、「旧江戸川」、「アマゾン川」などが表現に一致し、置換されます。\nその中で、例えば、「江戸川」だけは置換してほしくない場合、「江戸川」をNGワードとして設定すれば、置換の対象から外れます。\nまた、置換対象の外し方は「部分一致外し」と「完全一致外し」があります。\n「部分一致外し」の場合は、「江戸川」をNGワードとして登録した場合、「.{2,4}川」にマッチした言葉が、「旧江戸川」、「新旧江戸川」、\n「ああ江戸川」などであっても、「江戸川」がついているので、置換の対象から外れます。\n一方、「完全一致外し」の場合、「江戸川」を指定した場合、ちょうど「江戸川」にマッチしたものしか置換の対象から外れません。\n「.{2,4}川」で「旧江戸川」にマッチした場合、置換されてしまいます。\n詳しくは以下の選択欄の隣にある、「詳しく」ボタンを押して確認してください。\nこのNGワードは置換1件に対し10個まで設定できます。\nなお、NGワードは、現在置換しようとしている組み合わせにのみに適用されます。\nですので、同時に複数の文字列を置換する際、この置換でNGワードとして登録したものであっても、\n他の箇所で置換対象に当てはまり置換されてしまうということもございますのでご留意ください。"
     explaination_strs={"p":p_explaination_str,"wc":wc_explaination_str,"re":re_explaination_str}
     
     self.__mode_explaination_label=tk.Label(self,text=explaination_strs[self.__replace_mode],font=("serif",10,"bold"),bg="#cccccc")
     self.__mode_explaination_label.place(x=16,y=64)
     
     self.__ng_word_mode_label=tk.Label(self,text="置換外し方法:",font=("times",12))
     self.__ng_word_mode_combobox=ttk.Combobox(self,height=2,width=15,state="readonly",font=("helvetica",12),values=("部分一致外し","完全一致外し"))
     self.__ng_word_mode_combobox.current(0)
     self.__ng_word_mode_detail_exp_btn=tk.Button(self,text="詳しく",font=("times",12))
     
     #「正規表現モード」の時は、置換外しのモード選択欄が増える関係で、少し位置がずれる
     height_diff=0
     
     if self.__replace_mode == "re":
       self.__ng_word_mode_label.place(x=128,y=320)
       self.__ng_word_mode_combobox.place(x=288,y=320)
       self.__ng_word_mode_combobox.current(self.__class__.ng_word_mode_names.index(self.__ng_words_mode_in_reg_mode))
       self.__ng_word_mode_detail_exp_btn.place(x=448,y=320)
       self.__ng_word_mode_detail_exp_btn.bind("<Button-1>",self.disp_ng_word_mode_detail)
       #およそ96程度ずれる
       height_diff=96
     
     #ワイルドカードモードは説明が長いので、16ずらす(=「通常(部分一致)モード」の時との高さの差)
     if self.__replace_mode == "wc":
       height_diff=16
     
     
     self.__all_reset_btn=tk.Button(self,text="全入力取消",font=("times",12,"bold"))
     self.__all_reset_btn.bind("<Button-1>",self.all_input_reset)
     self.__all_reset_btn.place(x=320,y=560+height_diff)
     
     self.__ok_btn=tk.Button(self,text="実行",font=("times",12,"bold"))
     self.__ok_btn.bind("<Button-1>",self.ok)
     self.__ok_btn.place(x=448,y=560+height_diff)
     
     self.__cancel_btn=tk.Button(self,text="キャンセル",font=("times",12,"bold"))
     self.__cancel_btn.bind("<Button-1>",self.cancel)
     self.__cancel_btn.place(x=576,y=560+height_diff)
     
     self.bind("<Return>",self.ok)
     self.bind("<Escape>",self.cancel)
     
     self.geometry("1024x768")
     
     for i in range(0,10):
       try:
         #前回までのNGワードが記録されているところには前回登録したNGワードを入れる
         new_corner=OneNGWordEntrance(self,self.__replace_before_str,self.__replace_mode,self.__is_ignore_case,648,48,self.__ng_words[i])
         new_corner.place(x=8+(i%2*448),y=(int(i/2)*64)+256+height_diff)
         #new_corner.mainloop()
         self.__ng_word_corners.append(new_corner)
       #前回のNGワードがないところはそのまま何も与えない(デフォルト引数として空文字列が指定されているため)
       except IndexError:
         new_corner=OneNGWordEntrance(self,self.__replace_before_str,self.__replace_mode,self.__is_ignore_case,648,48)
         new_corner.place(x=8+(i%2*448),y=(int(i/2)*64)+256+height_diff)
         #new_corner.mainloop()
         self.__ng_word_corners.append(new_corner)
       
   
   def all_input_reset(self,event=None):
     is_all_reset_ok=messagebox.askokcancel("入力取り消し","ここに入力してあるNGワードをすべて取消してもよろしいですか?")
     if is_all_reset_ok:
       for one_ng_word_input_corner in self.__ng_word_corners:
         one_ng_word_input_corner.all_reset()
       messagebox.showinfo("入力取消","入力されたNGワードを全取消しました")
   
   
   def disp_ng_word_mode_detail(self,event=None):
      detail=NGWordDetailDialog(self) 
      return
   
   def validate(self):
     is_all_ok=True
     for one_ng_word_input_corner in self.__ng_word_corners:
        #入力の誤りがある箇所を実行時にすべて一気に表示したいので、入力誤りがあるものを見つけた場合、たとえその時点で戻り値はFalseであることが確定していたとしても早期returnしない
        if not one_ng_word_input_corner.check_input_validation():
          is_all_ok=False
     
     return is_all_ok
   
     
   def apply(self):
     new_ng_words=[]
     #validationした後に呼ばれるので、ここでは入力誤りを考慮する必要はない
     for one_ng_word_input_corner in self.__ng_word_corners:
       input_str=one_ng_word_input_corner.get_input_text()
       #空文字列の箇所はそもそもNGワードとして登録していないことを表すので無視してよい
       if len(input_str) != 0:
         new_ng_words.append(input_str)
     
     if self.__replace_mode == "re":
       ng_word_mode_num=self.__ng_word_mode_combobox.current()
       
       #正規表現モードの時は、置換外しのモードを表す情報も必要
       #ユーザーが文字列として入力した「NG-p」と「NG-e」と区別するため、そのまま文字列としてではなく、
       #ユーザーが入れたものではなく、内部処理として入れられたことがわかるように入れ子の配列として、この情報を引き渡す
       #引き渡し側では、一番最後の要素の0番目の要素を参照すること
       new_ng_words.append((self.__class__.ng_word_mode_names[ng_word_mode_num],))
      
     #リストはミュータブルで参照渡しなのでシャローコピーしておく)
     self.result=new_ng_words[:]
   
       



class OneNGWordEntrance(tk.Frame):
    
     def __init__(self,master,replace_before_str:str,replace_mode:str,is_ignore_case:bool,Width:int,Height:int,ini_str:str=""):
        super().__init__(master,width=Width,height=Height)
        self.__replace_before_str=replace_before_str
        self.__replace_mode=replace_mode
        
        self.__title_label=tk.Label(self,text="NGワード入力:",font=("times",12))
        self.__title_label.place(x=16,y=8)
        self.__one_ng_word_input=tk.Entry(self,width=25,font=("times",12))
        self.__one_ng_word_input.insert(0,ini_str)
        self.__one_ng_word_input.place(x=144,y=8)
        
        self.__reset_btn=tk.Button(self,text="取消",font=("times",12))
        self.__reset_btn.bind("<Button-1>",self.reset_input)
        self.__reset_btn.place(x=384,y=8)
        
        self.__is_ignore_case=is_ignore_case
        
        self.__error_disp_label=tk.Label(self,text="",font=("times",10,"bold"),fg="#ff0000")
        self.__error_disp_label.place(x=16,y=32)
     
     def get_input_text(self):
        return self.__one_ng_word_input.get()
     
     def reset_input(self,event=None):
       self.__one_ng_word_input.delete(0,tk.END)
     
     def all_reset(self):
       self.__error_disp_label["text"]=""
       self.reset_input()
     
     #入力内容が正しいか判定
     def check_input_validation(self):
       #何も入力していない場合は正しいとみなす
       if len(self.__one_ng_word_input.get()) == 0:
          self.__error_disp_label["text"]=""
          return True
       
       if self.__replace_mode == "p":
         return self.check_input_validation_in_normal_mode()
          
          
       if self.__replace_mode == "wc":
         return self.check_input_validation_in_wildcard_mode()
       
       if self.__replace_mode == "re":
         return self.check_input_validation_in_regexp_mode()
      
       return False
     
     def check_input_validation_in_normal_mode(self):
       if self.__replace_before_str == self.__one_ng_word_input.get():
          self.__error_disp_label["text"]="置換したい言葉それ自身をNGワードとすることはできません"
          return False
            
       if self.__replace_before_str in self.__one_ng_word_input.get():
          self.__error_disp_label["text"]=""
          return True
       
       if not self.__is_ignore_case:
          self.__error_disp_label["text"]=f"NGワードには、必ず「{self.__replace_before_str}」が含まれた言葉を設定してください!"
          return False
       
       #以下は大文字小文字の違いを無視する場合
       if self.__replace_before_str.lower() == self.__one_ng_word_input.get().lower():
          self.__error_disp_label["text"]="置換したい言葉それ自身をNGワードとすることはできません"
          return False
          
       if self.__replace_before_str.lower() in self.__one_ng_word_input.get().lower():
          self.__error_disp_label["text"]=""
          return True
          
       self.__error_disp_label["text"]=f"NGワードには、必ず「{self.__replace_before_str}」が含まれた言葉を設定してください!"
       return False
     
     def check_input_validation_in_wildcard_mode(self):
        wildcard_reg_exp=Replacer.wildcard_to_reg_exp(self.__replace_before_str)
        if re.search(wildcard_reg_exp,self.__one_ng_word_input.get()):
           self.__error_disp_label["text"]=""
           return True
           
        if not self.__is_ignore_case:
          self.__error_disp_label["text"]=f"NGワードは、必ず、「{self.__replace_before_str}」にマッチするような言葉にしてください!"
          return False
        
        if re.search(wildcard_reg_exp,self.__one_ng_word_input.get(),re.IGNORECASE):
           self.__error_disp_label["text"]=""
           return True
           
        self.__error_disp_label["text"]=f"NGワードは、必ず、「{self.__replace_before_str}」にマッチするような言葉にしてください!"
        return False
     
     def check_input_validation_in_regexp_mode(self):
       if re.search(self.__replace_before_str,self.__one_ng_word_input.get()):
          self.__error_disp_label["text"]=""
          return True
       
       if not self.__is_ignore_case:
         self.__error_disp_label["text"]=f"NGワードは、必ず、正規表現「{self.__replace_before_str}」にマッチするような言葉にしてください!"
         return False
       
       #大文字小文字無視 
       if re.search(self.__replace_before_str,self.__one_ng_word_input.get(),re.IGNORECASE):
         self.__error_disp_label["text"]=""
         return True
          
       
       self.__error_disp_label["text"]=f"NGワードは、必ず、正規表現「{self.__replace_before_str}」にマッチするような言葉にしてください!"
       return False
          

class NGWordDetailDialog(simpledialog.Dialog):
   
   def __init__(self,parent=None,title="置換の外し方とは?(詳細説明)"):
     super().__init__(parent,title)  
   
   def buttonbox(self):
     self.__main_title=tk.Label(self,text="置換の外し方とは?",font=("serif",18,"bold"))
     self.__main_title.place(x=160,y=0)
     self.__partial_mode_title=tk.Label(self,text="部分一致外しとは?",font=("serif",14,"bold"))
     self.__partial_mode_title.place(x=32,y=32)
     partial_explaination_str="部分一致外しとは、指定した正規表現にマッチしたある文字列に、NGワードとして登録した言葉が含まれていれば、\n置換の対象から外すことができるモードです。\n例)正規表現:「.{2,4}川」 検索文字列：「きれいな江戸川」 NGワード:「江戸川」の場合\nこの場合、正規表現にマッチする文字列は「な江戸川」となります。\nこの場合、「な江戸川」には「江戸川」が含まれているので、この、「な江戸川」は置換の対象から外れます。"
     self.__partial_mode_explaination=tk.Label(self,text=partial_explaination_str,font=("times",12),bg="#d9d9d9")
     self.__partial_mode_explaination.place(x=16,y=64)
     
     self.__exact_mode_title=tk.Label(self,text="完全一致外しとは?",font=("serif",14,"bold"))
     self.__exact_mode_title.place(x=32,y=192)
     
     exact_explaination_str="完全一致外しとは、指定した正規表現にマッチしたある文字列と、NGワードとして登録した文字列が等しかった場合にのみ\n置換の対象から外すことができるモードです。\n例)正規表現：「あ{2,5}」 検索文字列：「あああもうヤダああああ」 NGワード「あああ」の場合\nこの場合、正規表現にマッチするのは、冒頭の「あああ」と末尾の「ああああ」となります。\nこの場合、置換の対象から外されるのは、冒頭の「あああ」のみになります。「ああああ」は「あああ」を含みますが、\n文字列として等しくないので置換の対象から外れます。"
     self.__exact_mode_explaination=tk.Label(self,text=exact_explaination_str,font=("times",12),bg="#d9d9d9")
     self.__exact_mode_explaination.place(x=16,y=224)
     
     self.__digest_title=tk.Label(self,text="まとめ",font=("serif",14,"bold"),fg="#ff8888")
     self.__digest_title.place(x=384,y=352)
     digestion_explaination_str="ちなみに、先ほどの部分一致のところで紹介した、「.{2,4}川」の例で、完全一致外しを用いた場合,\n「な江戸川」と「江戸川」は等しくないので、置換の対象から外れなくなります。\n「江戸川」の部分も含めて、置換されてしまいます。\n一方で、「あ{2,5}」の例で部分一致外しを適用した場合、「ああああ」も「あああ」を含むので置換されなくしまいます。\nしたがって、あが3回以上繰り返すものはすべて置換されなくなってしまい、「あ{2,5}」とした意味がなくなってしまうかもしれません。\n不定の文字「.」の繰り返しなどに対しては、「部分一致外し」を\n特定の文字(「あ」など)に対しては「完全一致外し」を用いることを推奨します。"
     self.__digest_label=tk.Label(self,text=digestion_explaination_str,font=("times",12),bg="#ffcccc")
     self.__digest_label.place(x=16,y=384)
     
     self.__exit_btn=tk.Button(self,text="了解",font=("times",12,"bold"))
     self.__exit_btn.place(x=448,y=544)
     self.__exit_btn.bind("<Button-1>",self.ok)
     
     self.geometry("1024x576")
     self.bind("<Escape>",self.ok)
     self.bind("<Return>",self.cancel)
     
    
    
    