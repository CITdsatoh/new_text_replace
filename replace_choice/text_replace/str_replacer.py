#encoding;utf-8;
import re

#第一引数は、現在探索範囲のテキストでちょうど照合を行っている箇所,第二引数は探索したいテキスト
def decide_BM_slide_index(current_checking_str:str,search_str:str):
  
  #現在の見ている範囲(探索範囲)が、探索したいテキストの長さより短い場合はもう絶対、最後までスライドしていいことが自明
  if len(current_checking_str) < len(search_str):
    return len(search_str)
  
  #そもそも、探索したいテキストが1文字しかなかった場合は、1文字しかずれないことが確定
  if len(search_str) == 1:
    return 1
  
  i=len(current_checking_str)-1
  
  while 0 <= i:
    #現在確認している範囲の最後の文字
    current_checking_range_last_char=current_checking_str[i]
    #探索文字列(現在確認しているところの1つ前までを見る)
    search_str_current_range=search_str[0:i]
    if current_checking_range_last_char in search_str_current_range:
      char_index=search_str_current_range.rindex(current_checking_range_last_char)
      return i-char_index
    
    if current_checking_range_last_char != search_str_current_range[-1]:
      return len(search_str)
      
    i -= 1
    
  return len(search_str)



def flatten_list(flatten_before:tuple):
   flattened_list=[]
   for one_elem in flatten_before:
     if type(one_elem) == list or type(one_elem) == tuple:
        flattened_list.extend(flatten_list(tuple(one_elem)))
        continue
     flattened_list.append(one_elem)
   
   return flattened_list
  

#これは実際に指定された条件通りに置換を行うクラス 
class Replacer:

  def __init__(self,before_str:str,after_str:str,replace_mode:str="p",is_ignore_case:bool=False,ng_words_list:tuple=None,ng_words_mode_in_reg_mode:str="NG-p"):
  
    self.__before_str=before_str
    self.__after_str=after_str
    
    self.__replace_mode=replace_mode
   
    #ng_words_listは、生のreplaceでは、置換するキーワード(before_str)をすべて置換してしまうが、このリストは、before_strを含んでるけど置換してほしくない特定のキーワードを指定する配列
    #たとえば、before_str(置換前の文字列)が「京都」で,after_str(置換後の文字列)が「奈良」であったとき、このままだと、例えば、「東京都」は「東奈良」になってしまうし、「京都府」は「奈良府」になってしまう.
    #なので,このリストに「東京都」や「京都府」を登録しておけばその時だけ置換対象から除外するようにする。そのためのリスト。なお、ngリストのngワードはユーザーが指定する
    
    #None(引数がなかったら),空リスト(=空の場合、全部置換してよいということ)にして,そうでなければtupleをlistにする
    #空タプル、空リストはデフォルト引数としない(=副作用があるため)
    #ただし、1行完全一致モードは使用しない
    self.__ng_words_list=[]
    if replace_mode != "e":
      self.__ng_words_list=(ng_words_list and list(ng_words_list)) or []
    
    #置換前の文字列の大文字小文字の違いを無視するかどうか
    self.__is_ignore_case=is_ignore_case
    
    #NGワードの取り扱い方法
    self.__ng_words_mode_in_reg_mode="NG-p"
    
    if self.__replace_mode == "re":
      if ng_words_mode_in_reg_mode in ("NG-p","NG-e"):
       self.__ng_words_mode_in_reg_mode=ng_words_mode_in_reg_mode
    
  
  #引数は置換がなされる文字列
  def replace(self,contents):
     #内容が完全一致したときのみの置換の場合(完全一致置換)
     if self.__replace_mode == "e": 
        if self.__before_str == contents:
           return self.__after_str
        if self.__is_ignore_case:
          if self.__before_str.lower() == contents.lower():
           return self.__after_str
        
        return contents
     
     if self.__replace_mode == "wc":
      #ワイルドカード置換の場合(re.subはワイルドカードでは使用できないし、ワイルドカード置換のメソッドも存在しないため,正規表現に変換する)
      reg_exp_str=self.__class__.wildcard_to_reg_exp(self.__before_str)
      if len(self.__ng_words_list) == 0:
        if self.__is_ignore_case:
          return re.sub(reg_exp_str,self.__after_str,contents,flags=re.IGNORECASE)
        return re.sub(reg_exp_str,self.__after_str,contents)
      
      after_replaced_contents=contents
      #ワイルドカードが「*」だったとき、「.*」という貪欲マッチに変換されるので、ここでは貪欲マッチではなく最短マッチにする
      reg_exp_str=re.sub("(?<!(\\\\))\\.\\*",".*?",reg_exp_str)
      
      reg_match_words_include_empty=flatten_list(tuple(re.findall(reg_exp_str,after_replaced_contents)))
      if self.__is_ignore_case:
        reg_match_words_include_empty=flatten_list(tuple(re.findall(reg_exp_str,after_replaced_contents,re.IGNORECASE)))
      reg_match_words=[one_exp for one_exp in reg_match_words_include_empty if len(one_exp) != 0]
      for one_reg_match_word in reg_match_words:
        if self.any_one_ng_word_match_expr(one_reg_match_word):
          continue
        replace_reg_exp_str=ReplaceInformation.get_br_escaped_reg_exp_str(one_reg_match_word)
        after_replaced_contents=re.sub(replace_reg_exp_str,self.__after_str,after_replaced_contents)
        
      return after_replaced_contents
      
     
     #正規表現置換
     if self.__replace_mode == "re":
       if len(self.__ng_words_list) == 0:
         if self.__is_ignore_case:
           return re.sub(self.__before_str,self.__after_str,contents,flags=re.IGNORECASE)
         return re.sub(self.__before_str,self.__after_str,contents)
       
       after_replaced_contents=contents
       
       #^で始まったときは、指定した言葉のうち冒頭に存在するものだけを置換するようにするため別処理にする
       if self.__before_str.startswith("^"):
         for one_ng_word in self.__ng_words_list:
           #ただし、冒頭に存在するものを置換するといっても、今の置換元文字列で始まる指定したNGワードが冒頭に存在したら、置換を避ける
           if contents.startswith(one_ng_word):
              return contents
           elif not self.__is_ignore_case:
              continue
           if contents.lower().startswith(one_ng_word.lower()):
              return contents
          
         if self.__is_ignore_case:
           return re.sub(self.__before_str,self.__after_str,contents,flags=re.IGNORECASE)
         return re.sub(self.__before_str,self.__after_str,contents)
       
       #$で終わったときは、指定した言葉のうち末尾に存在するものだけを置換するようにするため別処理にする
       if self.__before_str.endswith("$"):
         for one_ng_word in self.__ng_words_list:
            #ただし、末尾に存在するものを置換するといっても、今の置換先文字列で終わる指定したNGワードが末尾に存在したら、置換を避ける
            if contents.endswith(one_ng_word):
               return contents
            elif not self.__is_ignore_case:
               continue
            if contents.lower().endswith(one_ng_word.lower()):
               return contents
               
         if self.__is_ignore_case:
            return re.sub(self.__before_str,self.__after_str,contents,flags=re.IGNORECASE)
         return re.sub(self.__before_str,self.__after_str,contents)
       
       reg_match_words_include_empty=flatten_list(re.findall(self.__before_str,after_replaced_contents))
       if self.__is_ignore_case:
         reg_match_words_include_empty=flatten_list(re.findall(self.__before_str,after_replaced_contents,re.IGNORECASE))
       
       reg_match_words=[one_exp for one_exp in reg_match_words_include_empty if len(one_exp) != 0]
       for one_reg_match_word in reg_match_words:
         if self.any_ng_word_match_expr_in_each_mode(one_reg_match_word):
            continue
         
         replace_reg_exp_str=ReplaceInformation.get_br_escaped_reg_exp_str(one_reg_match_word)
         after_replaced_contents=re.sub(replace_reg_exp_str,self.__after_str,after_replaced_contents)
       
       return after_replaced_contents
     
     
     #通常置換(部分一致置換)
     #この時のみ、ngワード(特定の場合のみ置換しない)が設定可能
     i=0
     replaced_str_tokens=[]
     #ngワード対応のため、replaceメソッドや正規表現は使用しない
     while i < len(contents):
       #検索文字列(置換するキーワード)の長さずつ調べる
       current_checking_str=contents[i:i+len(self.__before_str)]
       if self.__is_ignore_case and current_checking_str.lower() == self.__before_str.lower():
          pass
       elif current_checking_str != self.__before_str:
          slide_index=decide_BM_slide_index(current_checking_str,self.__before_str)
          if self.__is_ignore_case:
            slide_index=decide_BM_slide_index(current_checking_str.lower(),self.__before_str.lower())
            
          replaced_str_tokens.append(contents[i:i+slide_index])
          i += slide_index
          continue
          
       #検索文字列(置換するキーワード文字列)が見つかったとき
       #ngワードを一つずつ調べる
       for one_ng_word in self.__ng_words_list:
          if self.__is_ignore_case:
           if self.__before_str.lower() not in one_ng_word.lower():
               #print(self.__before_str.lower())
               ##print(one_ng_word.lower())
               continue
             
           #ngワードが始まるインデックスを求める
           keyword_index=one_ng_word.lower().index(self.__before_str.lower())
           ng_word_start_index=i-keyword_index
           if contents[ng_word_start_index:ng_word_start_index+len(one_ng_word)].lower() == one_ng_word.lower():
             #大文字小文字の違いを無視するといえど、元の文字列を変えてはいけない
             replaced_str_tokens.append(contents[i:i+len(self.__before_str)])
             i += len(self.__before_str)
             break
           
          if self.__before_str not in one_ng_word:
            continue
          #ngワードが始まるインデックスを求める
          keyword_index=one_ng_word.index(self.__before_str)
          ng_word_start_index=i-keyword_index
          #検索対象文字列(contents)の位置を、ngワード内における、置換するキーワードの位置の分だけ戻す。
          #例えば、「京都」が置換するキーワード文字列で、「東京都」が今見ているngワードであれば,「東京都」という文字列の中に、「京都」という文字列は1番目にあるので,
          #検索対象文字列(contents)のインデックスを1つ分戻し、その1つ分戻したところから,ngワードの長さ分切り出した文字列が,ngワードである「東京都」と等しいかを見る。等しければ見つかったとみなす
          #ngワードが見つかったとき置換せずそのままにする
          if contents[ng_word_start_index:ng_word_start_index+len(one_ng_word)] == one_ng_word:
             replaced_str_tokens.append(contents[i:i+len(self.__before_str)])
             i += len(self.__before_str)
             break
         
       #ngワードが見つからなかったときは置換
       else:
         replaced_str_tokens.append(self.__after_str)
         i += len(self.__before_str)
        
     return "".join(replaced_str_tokens)
     
  #引数として与えた文字列に,登録されたもののうち、いずれか1つのNGワード文字列が含まれているかどうか調べる
  def any_one_ng_word_match_expr(self,expr:str):
    for one_ng_word in self.__ng_words_list:
      if one_ng_word in expr:
        return True
      elif not self.__is_ignore_case:
        continue
      elif one_ng_word.lower() in expr.lower():
        return True
     
    return False
  
  
  
  def any_ng_word_match_expr_in_each_mode(self,expr:str):
    if self.__ng_words_mode_in_reg_mode == "NG-p":
      return self.any_one_ng_word_match_expr(expr)
    
    if expr in self.__ng_words_list:
      return True
    
    if not self.__is_ignore_case:
      return False
    
    ng_words_list_all_lower_char=[one_ng_word.lower() for one_ng_word in self.__ng_words_list]
    return expr.lower() in ng_words_list_all_lower_char
     
  def __str__(self):
    mode_names={"p":"通常モード","e":"1行完全一致置換モード","wc":"ワイルドカード置換モード","re":"正規表現置換モード"}
    ng_word_str="なし" if (self.__replace_mode == "e" or len(self.__ng_words_list) == 0) else ",".join(self.__ng_words_list)
    
    ng_words_mode_strs={"NG-p":"部分一致外し","NG-e":"完全一致外し"}
    ng_words_mode_str=f"(NGワードの取り扱い:{ng_words_mode_strs[self.__ng_words_mode_in_reg_mode]})" if self.__replace_mode =="re" else""
    
    return f"置換前:{self.__before_str},置換後:{self.__after_str},モード:{mode_names[self.__replace_mode]},置換NGワード:{ng_word_str}{ng_words_mode_str}"
    
    
  def __repr__(self):
    return f"{self.__class__.__name__}(\"{self.__before_str}\",\"{self.__after_str}\",\"{self.__replace_mode}\",{tuple(self.__ng_words_list)}),\"{self.__ng_words_mode_in_reg_mode}\""
  
   
  @classmethod
  def wildcard_to_reg_exp(cls,wc_str:str):
    #ワイルドカードから正規表現へ変換する際,エスケープが必要な文字(*は.*に,?は.に変換、[]はワイルドカードの時と意味が変わらないのでそのままでよい)
    anytime_escape_need_chars=("\\","^","$",".","+","(",")","{","}","|","（",")")
    
    #正規表現に変換後(=変換時は1文字ずつ調べるため,ここでは変換結果をいったん、文字の配列としておいておく)
    reg_exp_chars=[]
    
    #[]の内側かどうか(=>[]の内側の時は,*,?,[は文字列として扱われるのでエスケープ処理が必要。そのことを見抜くためフラグを作る)
    #逆に-と]は[]の外側の時のみエスケープ処理を行う
    is_inside_square_para=False
    
    inside_square_only_escape_chars=["*","?","["]
    outside_square_only_escape_chars=["-","]"]
    
    i=0
    
    while i < len(wc_str):
       #[]の内外関係なくエスケープしなければいけない文字
       if wc_str[i] in anytime_escape_need_chars:
          reg_exp_chars.append("\\")
          reg_exp_chars.append(wc_str[i])
          i += 1
          continue
       if is_inside_square_para:
         if wc_str[i] == "]":
           reg_exp_chars.append(wc_str[i])
           is_inside_square_para=False
           i += 1
           continue
         if wc_str[i] in inside_square_only_escape_chars:
           reg_exp_chars.append("\\")
           reg_exp_chars.append(wc_str[i])
           i += 1
           continue
       #以降の処理は[]の内側ではないとき
       if wc_str[i] == "[":
         reg_exp_chars.append(wc_str[i])
         is_inside_square_para=True
         #四角かっこのすぐ次の文字がエクスクラメーションマークなら、これは否定クラスを表すので,正規表現の否定クラスである^を入れる
         if wc_str[i+1] == "!":
           reg_exp_chars.append("^")
           i += 2
           continue
         i += 1
         continue
       #-と]のエスケープ
       if wc_str[i] in outside_square_only_escape_chars:
         reg_exp_chars.append("\\")
         reg_exp_chars.append(wc_str[i])
         i += 1
         continue
       
       #通常時の処理(*を.*にするのと,?を.にする)
       reg_exp_chars.append(wc_str[i].replace("*",".*").replace("?","."))
       i += 1
    
    return "".join(reg_exp_chars)
  
  

#こちらは置換内容がテキストとして入力された後、入力内容を置換しやすいように内部変換する仲介クラス
class ReplaceInformation:
  
  def __init__(self,replace_before:str,replace_after:str,replace_mode:str="p",is_ignore_case:bool=False,ng_words_list:tuple=None,ng_words_mode_in_reg_mode:str="NG-p"):
    
    self.__replace_before=replace_before
    self.__replace_after=replace_after
    self.__replace_mode="p"
    if replace_mode in ("p","e","wc","re"):
      self.__replace_mode=replace_mode
    
    self.__ng_words_list=[]
    if self.__replace_mode != "e":
      self.__ng_words_list=(ng_words_list and list(ng_words_list)) or []
      
    self.__ng_words_mode_in_reg_mode="NG-p"
    if ng_words_mode_in_reg_mode in ("NG-p","NG-e"):
       self.__ng_words_mode_in_reg_mode=ng_words_mode_in_reg_mode
    
    self.__is_ignore_case=is_ignore_case
  
  
  
  #通常モードの時(置換された結果をさらに置換してよい場合)は、そのまま内容を置換オブジェクトに入れて返す
  def get_replace_obj_in_normal_mode(self):
    if self.__replace_mode == "re":
      return Replacer(self.__replace_before,self.__replace_after,self.__replace_mode,self.__is_ignore_case,tuple(self.__ng_words_list),self.__ng_words_mode_in_reg_mode)
    if self.__replace_mode != "e":
      return Replacer(self.__replace_before,self.__replace_after,self.__replace_mode,self.__is_ignore_case,tuple(self.__ng_words_list))
    
    return Replacer(self.__replace_before,self.__replace_after,self.__replace_mode,self.__is_ignore_case)
  
  #「同時置換モード(1度置換)モード」は置換された結果をさらに別の言葉に置換されないようにするモード
  #例えば、「あいうえお」を「かきくけこ」に、「かきくけこ」を「さしすせそ」に置換する際
  #「あいうえお」を「かきくけこ」に置換した後、さらにその「かきくけこ」が「さしすせそ」に置換されてしまう。
  #このモードは置換を1度のみに抑え、「かきくけこ」の置換は、「あいうえお」から置換されたいものでなく、もともと「かきくけこ」だったところだけ置換するようにする
  #一度置換したものがさらに置換されないようするには、ある言葉を置換するときは、「\n置換後の言葉\n」と余計に前後に改行コードをつけることとしている。(=前後の改行コードが、もともとその文字列だったのか置換されたものなのかの判別するためのもの)
  #ただし、部分一致モードでは改行をつけようと、新しい言葉に代わってしまうので、前後の改行付きの置換後の言葉を第一引数のタプルの要素に入れることで、NGワードとして登録し、改行付きのものは置換されないようにする
  def get_replace_obj_in_only_once_replace_mode(self,temp_ng_words:tuple=None):
     escaped_after_replace=self.escaped_replace_after_pattern_in_only_once_replace_mode
     if self.__replace_mode == "re":
       escaped_new_replaced_str=self.__class__.get_br_escaped_reg_exp_str(self.__replace_before)
       return Replacer(escaped_new_replaced_str,escaped_after_replace,self.__replace_mode,self.__is_ignore_case,tuple(self.__ng_words_list),self.__ng_words_mode_in_reg_mode)
     
     if self.__replace_mode == "wc":
       wildcard_reg_exp_str=Replacer.wildcard_to_reg_exp(self.__replace_before)
       #ngワードがある場合は、貪欲マッチではなく最短マッチで置換するようにする
       if len(self.__ng_words_list) != 0:
         wildcard_reg_exp_str=re.sub("(?!<(\\\\))\\.\\*",".*?",wildcard_reg_exp_str)
       
       escaped_new_replaced_str=f"((?!<(\n)){wildcard_reg_exp_str}|{wildcard_reg_exp_str}(?!(\n)))"
       return Replacer(escaped_new_replaced_str,escaped_after_replace,"re",self.__is_ignore_case,tuple(self.__ng_words_list),"NG-p")
       
     
     if self.__replace_mode == "p":
       one_replace_ng_words=self.__ng_words_list[::]
       if temp_ng_words is not None:
          one_replace_ng_words.extend(list(temp_ng_words))
       return Replacer(self.__replace_before,escaped_after_replace,self.__replace_mode,self.__is_ignore_case,tuple(one_replace_ng_words))
     
     return Replacer(self.__replace_before,escaped_after_replace,self.__replace_mode,self.__is_ignore_case)
       
  def __str__(self):
    mode_name_japanese={"p":"通常モード(部分一致)","e":"1行完全一致モード","wc":"ワイルドカード","re":"正規表現"}
    
    match_str="を" if self.__replace_mode in ("p","e") else "にマッチする文字列を"
    replace_str_header=f"「{self.__replace_before}」{match_str}「{self.__replace_after}」に置換"
    #置換後文字列が空ならその文字列を削除するということになる
    if len(self.__replace_after) == 0:
       replace_str_header=f"「{self.__replace_before}」{match_str}削除"
    
    if self.__replace_mode == "e":
      return f"{replace_str_header}\n置換モード:{mode_name_japanese[self.__replace_mode]}"
    
    ng_words_with_bracket=[f"「{one_ng_word}」" for one_ng_word in self.__ng_words_list]
    ng_words_str=(ng_words_with_bracket and ",".join(ng_words_with_bracket)) or "なし"
    match_explaination_str="がつくけど" if self.__replace_mode in ("p","e") else "にマッチするけど"
    ng_words_str=f"置換NGワード({self.__replace_before}){match_explaination_str}置換したくないワード):{ng_words_str}"
   
    case_ignore_str="大文字小文字の違いの無視:する" if self.__is_ignore_case else "大文字小文字の違いの無視:しない"
    
    ng_words_mode_str=""
    if self.__replace_mode != "re":
      pass
    elif len(self.__ng_words_list) != 0:
      ng_words_mode_in_reg_mode_strs={"NG-p":"部分一致外し","NG-e":"完全一致外し"}
      ng_words_mode_str=f"(NGワードの取り扱い:{ng_words_mode_in_reg_mode_strs[self.__ng_words_mode_in_reg_mode]})"
    
    
    return f"対象:{replace_str_header}\n置換モード:{mode_name_japanese[self.__replace_mode]}\n{ng_words_str}{ng_words_mode_str}\n{case_ignore_str}"
  
  
  def __repr__(self):
    return f"{self.__class__.__name__}(\"{self.__replace_before}\",\"{self.__replace_after}\",\"{self.__replace_mode}\",{self.__is_ignore_case},{tuple(self.__ng_words_list)},\"{self.__ng_words_mode_in_reg_mode}\""
  
  #前後に改行コード付きの文字列(=置換の結果それになったことを示すもの)を後読み先読みによって、置換の対象から外すための、正規表現文字列を作り出す
  @classmethod
  def get_br_escaped_reg_exp_str(cls,replace_before:str):
    if replace_before.startswith("^"):
      start_cap_removed_str=replace_before.lstrip("^")
      if replace_before.endswith("$"):
        start_cap_end_dollar_removed_str=start_cap_removed_str.rstrip("$")
        return f"^((?<!(\n)){start_cap_end_dollar_removed_str}|{start_cap_end_dollar_removed_str}(?!(\n)))$"
      return f"^((?<!(\n)){start_cap_removed_str}|{start_cap_removed_str}(?!(\n)))"
    if replace_before.endswith("$"):
      end_dollar_mark_removed_str=replace_before.rstrip("$")
      return f"((?<!(\n)){end_dollar_mark_removed_str}|{end_dollar_mark_removed_str}(?!(\n)))$"
       
    return f"((?<!(\n)){replace_before}|{replace_before}(?!(\n)))"
         
  
  
  @property
  def replace_before_pattern(self):
    return self.__replace_before
  
  @property
  def replace_after_pattern(self):
    return self.__replace_after
  
  @property
  def escaped_replace_after_pattern_in_only_once_replace_mode(self):
    return f"\n{self.__replace_after}\n"
  
   

  