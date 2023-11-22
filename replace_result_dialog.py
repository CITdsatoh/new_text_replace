#encoding:utf-8;
import tkinter as tk
from tkinter import scrolledtext,simpledialog
import re
import datetime


class ReplaceResultDialog(simpledialog.Dialog):

  def __init__(self,parent,replace_result_strs:tuple[str],title="置換結果"):
    #置換が失敗したときは、赤色で別の枠に記述したいので、成功の文字列と失敗の文字列を分ける
    self.__replace_result_success_strs=[]
    self.__replace_result_failure_strs=[]
    for one_replace_result_str in replace_result_strs:
      #ファイル名に「結果:失敗」という文字列が含まれるている可能性も考えられなくはないので、
      #各結果文字列(IOFileManageのインスタンスのstr)の2行目だけを取り出して考える
      one_replace_result_status_str=one_replace_result_str.split("\n")[1]
      if re.search("結果:失敗:",one_replace_result_status_str):
        self.__replace_result_failure_strs.append(one_replace_result_str)
        continue
      if re.search("結果:成功:",one_replace_result_status_str):
        self.__replace_result_success_strs.append(one_replace_result_str)
         
    
    super().__init__(parent,title)
  
  def buttonbox(self):
    self.__header_label=tk.Label(self,text="ファイル置換結果",font=("serif",14,"bold"))
    self.__header_label.place(x=256,y=0)
    
    self.__explaination_label=tk.Label(self,text="以下に今回のファイル置換の結果を示しておきます。「成功」欄には正常に置換を完了し、\n書き込みまで無事に終了したものを、「失敗」欄にはファイル等に異常があり、\n正常に置換結果の書き込みができなかったものについて、原因を含め記載しております。",font=("serif",12,"bold"))
    self.__explaination_label.place(x=8,y=32)
    
    #成功した書き込み欄と失敗した書き込み欄の大きさ(高さ)は、実際に成功した数と失敗した数の比に合わせて変更する
    #なお、2つの入力欄の高さの合計は20行分とし、ここから分配する
    #おおよそ、成功:失敗=3:1以下(つまり、成功率75%以上)なら、成功15行、失敗5行
    #おおよそ、成功:失敗=3:1~1:3の間(つまり、成功率が25%以上75%未満)なら、成功10行、失敗10行
    #成功率25%未満なら、成功5行,失敗15行とする
    
    sum_of_each_result_num=len(self.__replace_result_success_strs)+len(self.__replace_result_failure_strs)
    success_corner_lines=10
    failure_corner_lines=10
    if 0.75 <= len(self.__replace_result_success_strs)/sum_of_each_result_num:
       success_corner_lines=15
       failure_corner_lines=5
    elif len(self.__replace_result_success_strs)/sum_of_each_result_num < 0.25:
       success_corner_lines=5
       failure_corner_lines=15
    
    
    success_head_label_y_axis=128
    diff=0
    self.__success_header_label=tk.Label(self,text="成功",font=("times",12,"bold"))
    self.__success_header_label.place(x=16,y=success_head_label_y_axis+diff)
    
    self.__success_result_text=scrolledtext.ScrolledText(self,height=success_corner_lines,width=100,relief=tk.SOLID,borderwidth=2,font=("times",11,"bold"))
    success_result_disp_str=self.__replace_result_success_strs and "\n\n".join(self.__replace_result_success_strs) or "なし"
    self.__success_result_text.insert("1.0",success_result_disp_str)
    self.__success_result_text["state"]="disabled"
    diff += 32
    self.__success_result_text.place(x=16,y=success_head_label_y_axis+diff)
    
    diff += 16+(16*success_corner_lines)
    
    self.__success_header_label=tk.Label(self,text="失敗",font=("times",12,"bold"))
    self.__success_header_label.place(x=16,y=success_head_label_y_axis+diff)
    
    diff += 32
    
    self.__failure_result_text=scrolledtext.ScrolledText(self,height=failure_corner_lines,width=100,relief=tk.SOLID,borderwidth=2,font=("times",11,"bold"))
    failure_result_disp_str=self.__replace_result_failure_strs and "\n\n".join(self.__replace_result_failure_strs) or "なし"
    if len(self.__replace_result_failure_strs) != 0:
      self.__failure_result_text["fg"]="#ff0000"
    self.__failure_result_text.insert("1.0",failure_result_disp_str)
    self.__failure_result_text["state"]="disabled"
    self.__failure_result_text.place(x=16,y=success_head_label_y_axis+diff)
    
    diff += 16+(16*failure_corner_lines)
    
    foot_explaination_str="なお、置換を行ったファイルの情報のみならず、置換を行ったテキスト情報を含んだ、さらに詳しい情報が\n必要な場合は、このダイアログを閉じた先のメインウィンドウに存在する\n「置換結果をテキストファイルに出力する」ボタンを\n押してください。すると、それらの情報を含めて、詳細情報をテキストファイルとして保存することができます"
    self.__fin_explaination_label=tk.Label(self,text=foot_explaination_str,font=("times",11,"bold"))
    self.__fin_explaination_label.place(x=8,y=success_head_label_y_axis+diff)
    
    self.__ok_btn=tk.Button(self,text="了解",font=("times",11,"bold"))
    self.__ok_btn.place(x=384,y=success_head_label_y_axis+diff+96)
    self.__ok_btn.bind("<Button-1>",self.ok)
    
    self.bind("<Escape>",self.cancel)
    self.bind("<Return>",self.ok)
    
    self.geometry("896x768")
    
    
    