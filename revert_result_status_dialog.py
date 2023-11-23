#encoding:utf-8;

import re
import tkinter as tk
from tkinter import simpledialog,scrolledtext

class RevertResultStatusDialog(simpledialog.Dialog):
  
  def __init__(self,parent,revert_results:dict):
    self.__success_strs=[]
    self.__failure_strs=[]
    for file_path_str,result_str in revert_results.items():
      if re.search("成功:",result_str):
        one_str=f"元に戻すファイル:{file_path_str}\n結果:{result_str}"
        self.__success_strs.append(one_str)
        continue
      if re.search("失敗:",result_str):
        one_str=f"元に戻すファイル:{file_path_str}\n結果:{result_str}"
        self.__failure_strs.append(one_str)
           
    super().__init__(parent,"ファイル復元結果")
  
  def buttonbox(self):
    self.__header_label=tk.Label(self,text="ファイルを元に戻した結果",font=("serif",16,"bold"))
    self.__header_label.place(x=256,y=0)
    
    #成功した書き込み欄と失敗した書き込み欄の大きさ(高さ)は、実際に成功した数と失敗した数の比に合わせて変更する
    #なお、2つの入力欄の高さの合計は20行分とし、ここから分配する
    #おおよそ、成功:失敗=3:1以下(つまり、成功率75%以上)なら、成功15行、失敗5行
    #おおよそ、成功:失敗=3:1~1:3の間(つまり、成功率が25%以上75%未満)なら、成功10行、失敗10行
    #成功率25%未満なら、成功5行,失敗15行とする
    
    sum_of_each_result_num=len(self.__success_strs)+len(self.__failure_strs)
    success_corner_lines=10
    failure_corner_lines=10
    if 0.75 <= len(self.__success_strs)/sum_of_each_result_num:
       success_corner_lines=15
       failure_corner_lines=5
    elif len(self.__success_strs)/sum_of_each_result_num < 0.25:
       success_corner_lines=5
       failure_corner_lines=15
    
    
    success_head_label_y_axis=48
    diff=0
    self.__success_header_label=tk.Label(self,text="成功",font=("times",12,"bold"))
    self.__success_header_label.place(x=16,y=success_head_label_y_axis+diff)
    
    self.__success_result_text=scrolledtext.ScrolledText(self,height=success_corner_lines,width=100,relief=tk.SOLID,borderwidth=2,font=("times",11,"bold"))
    success_result_disp_str=self.__success_strs and "\n\n".join(self.__success_strs) or "なし"
    self.__success_result_text.insert("1.0",success_result_disp_str)
    self.__success_result_text["state"]="disabled"
    diff += 32
    self.__success_result_text.place(x=16,y=success_head_label_y_axis+diff)
    
    diff += 32+(16*success_corner_lines)
    
    self.__success_header_label=tk.Label(self,text="失敗",font=("times",12,"bold"))
    self.__success_header_label.place(x=16,y=success_head_label_y_axis+diff)
    
    diff += 32
    
    self.__failure_result_text=scrolledtext.ScrolledText(self,height=failure_corner_lines,width=100,relief=tk.SOLID,borderwidth=2,font=("times",11,"bold"))
    failure_result_disp_str=self.__failure_strs and "\n\n".join(self.__failure_strs) or "なし"
    if len(self.__failure_strs) != 0:
      self.__failure_result_text["fg"]="#ff0000"
    self.__failure_result_text.insert("1.0",failure_result_disp_str)
    self.__failure_result_text["state"]="disabled"
    self.__failure_result_text.place(x=16,y=success_head_label_y_axis+diff)
    
    diff += 16+(16*failure_corner_lines)
    
    
    self.__ok_btn=tk.Button(self,text="了解",font=("times",11,"bold"))
    self.__ok_btn.place(x=384,y=success_head_label_y_axis+diff)
    self.__ok_btn.bind("<Button-1>",self.ok)
    
    self.bind("<Escape>",self.cancel)
    self.bind("<Return>",self.ok)
    
    self.geometry("896x672")
    