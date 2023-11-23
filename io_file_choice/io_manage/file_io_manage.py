#encoding:utf-8;
import os
import shutil
from enum import IntEnum

not_sep="/" if os.name == "nt" else "\\"


class FileIOResultStatusCodes(IntEnum):
  IO_SUCCESS=0
  SRC_FILE_DELETE=1
  SRC_FILE_NOT_TEXT=2
  SRC_FILE_ENCODE_FAULT=3
  DST_FILE_IN_NON_EXIST_DIR=4
  DST_FILE_NON_PERMISSION=5
  DST_FILE_DECODE_FAULT=6


class FileRevertResultStatusCodes(IntEnum):
  REVERT_SUCCESS=0
  REVERT_FILE_OPENED=1
  REVERT_FILE_DELETE=2
  NO_NEED_REVERT=3
  
  @classmethod
  def code_to_status_str(cls,code):
    if code == cls.REVERT_SUCCESS:
      return "成功:ファイルを無事に置換する前の状態に戻すことができました。"
    if code == cls.REVERT_FILE_OPENED:
      return "失敗:ファイルが開かれたままか、読み取り専用になっておりましたので、元に戻すことができませんでした。"
    if code == cls.REVERT_FILE_DELETE:
      return "失敗:ファイルが元に戻そうとしている際に、消去されたため、元に戻すことができませんでした"
    if code == cls.NO_NEED_REVERT:
      return "失敗:元に戻すものがありませんでした"
    
    return "失敗:予期せぬエラーが発生しました"

  


class FileManageStatus:
  
  def __init__(self,status:int,encode_info:str=""):
    self.__status=status
    self.__encode_info=encode_info
  
  #詳細表示:実際にダイアログ等でユーザーに示す際のもの
  def get_status_detail_str(self):
    if self.__status == FileIOResultStatusCodes.IO_SUCCESS:
      return "成功\nファイルのテキスト置換が無事完了しました"
    if self.__status == FileIOResultStatusCodes.SRC_FILE_DELETE:
      return "失敗\nテキストを置換しようとしているファイルが存在しませんでした。\nもし、ファイル選択時に存在していた場合、書き込みまでの間に削除された可能性があります"
    if self.__status == FileIOResultStatusCodes.SRC_FILE_NOT_TEXT:
      return "失敗\n画像ファイルや実行形式ファイルなど、テキストを扱うのに適切ではないファイル形式のものが指定された可能性があります\n拡張子、MIMEタイプなどを確認しやり直してください"
    if self.__status == FileIOResultStatusCodes.SRC_FILE_ENCODE_FAULT:
      return "失敗\nテキストを置換しようとしているファイルの文字コード形式が、「UTF-8」か「UTF-16」か「UTF-32]か「Shift-JIS」か「ASCII」か「EUC」か「ISO2022JP」以外の\n本システムで利用不可能なものが指定されました。申し訳ありませんが、前述の7文字コード方式以外のファイルは使用できません。"
    if self.__status == FileIOResultStatusCodes.DST_FILE_IN_NON_EXIST_DIR:
      return "失敗\n置換した結果を書き込もうとしているファイルが、存在しないフォルダ内に指定されました\nもし、指定した場所に保存したい場合は、まずはフォルダを作成してください。フォルダの自動作成は行いません"
    if self.__status == FileIOResultStatusCodes.DST_FILE_NON_PERMISSION:
      return "失敗\n置換した結果を書き込もうとしているファイルが、開かれているか、読み取り専用になっています。\nファイルを閉じる、あるいは読み取り専用を解除してからやり直してください"
    if self.__status == FileIOResultStatusCodes.DST_FILE_DECODE_FAULT:
      return f"失敗\n置換後文字列として指定されている文字列の一部に、現在指定されているファイルの{self.__encode_info}方式では利用できない文字が入っておりました\n環境依存文字などの使用はなるべく避けることを推奨いたします"
    
    
    return "失敗\n予期しないエラーが発生しました"
  
  #ファイル書き込み結果の表示(短め・結果レポートファイルに書き込み用)str表示用
  def get_status_str(self):
    if self.__status == FileIOResultStatusCodes.IO_SUCCESS:
      return "置換は正常に行われました"
    if self.__status == FileIOResultStatusCodes.SRC_FILE_DELETE:
      return "テキストを置換しようとしているファイルが存在しませんでした。ファイル選択後、読み取りまでの間に削除された可能性があります。"
    if self.__status == FileIOResultStatusCodes.SRC_FILE_NOT_TEXT:
      return "実行ファイルや画像ファイルなどのテキストの書き込みに適さないものが指定されたので読み取りができませんでした。"
    if self.__status == FileIOResultStatusCodes.SRC_FILE_ENCODE_FAULT:
      return "テキストを置換しようとしているファイルの文字コード方式が本システムでは使用できないものが指定されていたため読み取りができませんでした。本システムで利用可能な文字コード方式は「UTF-8」か「UTF-16」か「UTF-32」か「Shift-JIS」か「ASCII」か「EUC」か「ISO2022JP」の7つです。"
    if self.__status == FileIOResultStatusCodes.DST_FILE_IN_NON_EXIST_DIR:
      return "置換結果を書き込むファイルが、存在しないフォルダの中にあるものが指定されました。"
    if self.__status == FileIOResultStatusCodes.DST_FILE_NON_PERMISSION:
      return "置換結果を書き込むファイルが、書き込み時に閉じられていないか、読み取り専用になっているか、あるいは、書き込み権限がないフォルダが指定されたため書き込みができませんでした。"
    if self.__status == FileIOResultStatusCodes.DST_FILE_DECODE_FAULT:
      return f"置換後文字列として指定されている文字列の一部に、{self.__encode_info}では使用できない文字列が混在しており、正しく書き込みができませんでした"
    
    return "予期しないエラーが発生しました"
      
  def __str__(self):
    status_str="成功" if self.__status == FileIOResultStatusCodes.IO_SUCCESS else "失敗"
    return f"{status_str}:{self.get_status_str()}"
  
  @property
  def status_code(self):
    return self.__status

class FileIOManage:

   def __init__(self,src_file_path_str:str,dst_file_path:str=""):
     
     #現在の作業ディレクトリ(一時的にホームディレクトリに作業場を移す関係で、現在のディレクトリを一時的に変数で保存)
     ini_working_dir=os.getcwd()
     
   
     os.chdir(os.path.expanduser("~"))
     
     #読み出しファイル(=このファイルの文字列を置換する)
     #こちらの入力不備はエラーを事前に出しているので、ユーザーに正しい形で入力してもらったものが来るようになっているため、
     #きちんとしたファイルパス文字列が入っている(行うのは区切り文字の統一と絶対パス化)
     self.__src_file_path_str=src_file_path_str.replace(not_sep,os.sep)
     
     if not os.path.isabs(self.__src_file_path_str):
       self.__src_file_path_str=os.path.abspath(self.__src_file_path_str)
     
     #書き込み先ファイル(=上書きではない場合は,このファイルに置換結果を書く。ここが空文字列なら、上書き扱いとする)
     #書き込み先ファイルについては、入力が不十分でもアプリ側で補えるので、読み取り元とは異なり、エラーは出さず、不備はこちらで補うようにする。
     #以下は補ったうえでの、正式なパス(補う処理は長いので、別途関数で行うこととする)
     self.__dst_file_path_str=self.__class__.normalize_dst_file_path_str(dst_file_path,self.__src_file_path_str)
     
     #ここでは、複数ファイル一気に、書き込みが成功した場合であっても失敗した場合であっても、最後まで行うので
     #各指定ごとの書き込みがうまくいったか保持しておく
     self.__status=None
     
     self.__file_encoding=""
     
     try:
       #エンコーディング(UTF-8かShift-JISかASCIIかEUCかISO2022JP)のどれか
       #いずれでもなかった場合、空文字列が返る
       self.__file_encoding=self.__class__.judge_encode(self.__src_file_path_str)
     #選択時はファイルは存在したのに、肝心の読み取り先ファイルがなくなって、エンコードが調べられなかった場合
     #そのような場合でもとりあえずオブジェクトは生成しておく(だがとりあえず失敗扱いしておく。もしかして、復活して読み取れるかもしれないし・・)
     except FileNotFoundError:
       self.__status=FileManageStatus(FileIOResultStatusCodes.SRC_FILE_DELETE)
     
     
     #置換後、思っていたのと違って、元に戻したくなった場合のために、置換前のファイルの内容を残しておく
     #まだ文字列を読み取っていないとき(つまり、元に戻すものがないとき)は、None.(空配列はファイル自体の内容が空だったことを表すため使わない)
     self.__replace_before_file_contents_for_backup=None
     
     #作業ディレクトリをもとに戻す
     os.chdir(ini_working_dir)
     
   
   #ファイルの内容を1行ずつ取得する
   #失敗時はNoneを返す(=空配列ではないのは、もともと空のファイルだった場合との差別化のため)
   def read_file_all_lines(self):
     file_contents=[]
     self.__status=None
     self.__replace_before_file_contents_for_backup=None
     
     f=None
     try:
       f=open(self.__src_file_path_str,encoding=self.__file_encoding)
       file_contents=f.readlines()
     #存在しないファイルが指定されていたり、ファイルパスを設定後にファイルが消去されていたら,FileNotFoundErrorが出る
     except FileNotFoundError:
       self.__status=FileManageStatus(FileIOResultStatusCodes.SRC_FILE_DELETE)
       return None
     #それかそもそも、画像ファイルや実行形式ファイルなどテキストを扱うものでない場合も同様
     except LookupError:
       self.__status=FileManageStatus(FileIOResultStatusCodes.SRC_FILE_NOT_TEXT)
       return None
     #不正なエンコーディング
     except UnicodeDecodeError:
       self.__status=FileManageStatus(FileIOResultStatusCodes.SRC_FILE_ENCODE_FAULT)
     #ここで、encodingがUTF-8かUTF-16かUTF-32かShift-JISかASCIIかEUC-JPかISO2022JPの7つ以外なら、ここでは空文字列がencodingとして指定されているので
     #再度UnicodeDecodeErrorが出る。その際はファイルの内容が読み取れないことを示す
       return None
     finally:
       if f is not None:
         f.close()
     
     #読み取りに成功した場合、ファイルの内容をそのまま残しておく
     #読み取った内容に対して、引き渡した後に何らかの処理をした際にこちらに影響が出ないよう、読み取った内容はシャローコピーしておく
     self.__replace_before_file_contents_for_backup=file_contents[:]
     
     return [one_line.strip("\n") for one_line in file_contents]
   
   #ファイルに置換後の文字列を書き込む
   def write_file_after_replaced(self,replaced_file_contents:list[str]):
     #何らかの失敗があった場合や成功した場合でも再書き込みできないようにする
     if self.__status is not None:
        return
        
     
     f=None
     try:
       f=open(self.__dst_file_path_str,"w",encoding=self.__file_encoding)
       for one_replaced_line in replaced_file_contents:
          f.write(one_replaced_line+"\n")
     #ここでは、書き込み先が存在しないディレクトリ配下に存在した場合、エラーが出る
     except FileNotFoundError:
       self.__status=FileManageStatus(FileIOResultStatusCodes.DST_FILE_IN_NON_EXIST_DIR)
       return
     #書き込み先ファイルが開かれていた場合や読み取り専用になっていた場合
     except PermissionError:
       self.__status=FileManageStatus(FileIOResultStatusCodes.DST_FILE_NON_PERMISSION)
       return
     #置換後文字列に環境依存文字などが入っていた場合
     except UnicodeDecodeError:
       self.__status=FileManageStatus(FileIOResultStatusCodes.DST_FILE_DECODE_FAULT,self.__file_encoding)
       return
     finally:
       if f is not None:
         f.close()
     
     self.__status=FileManageStatus(FileIOResultStatusCodes.IO_SUCCESS)
    
      
   #実際に、置換後に元に戻す
   #成功時は戻り値として0を返却し、元に戻したいファイルが閉じられていない場合は1を返し、元に戻すファイルを選択後にファイルが消された場合は2を返す
   #そもそも内容が読み取られておらず、戻すものがないときは3を返す
   def revert_to_replace_before_str(self):
     #元に戻すものが存在しないとき
     if self.__replace_before_file_contents_for_backup is None:
        return FileRevertResultStatusCodes.NO_NEED_REVERT
     
     f=None
     try:
       f=open(self.__src_file_path_str,"w",encoding=self.__file_encoding)
       f.writelines(self.__replace_before_file_contents_for_backup)
     #ファイルが開かれっぱなし
     except PermissionError:
       return FileRevertResultStatusCodes.REVERT_FILE_OPENED
     #ファイルが消された
     except FileNotFoundError:
       return FileRevertResultStatusCodes.REVERT_FILE_DELETE
     finally:
       if f is not None:
          f.close()
     
     return FileRevertResultStatusCodes.REVERT_SUCCESS
   
   #ファイルの内容を置換前の状態に戻すことが可能かどうかを返すメソッド
   #戻すことができるかどうかだけを調べる
   def is_revertable_to_replace_before(self):
     #元に戻すものが存在しないとき
     if self.__replace_before_file_contents_for_backup is None:
        return False
     
     #上書きじゃないときは変わっていないので元に戻す必要はない
     if self.__src_file_path_str != self.__dst_file_path_str:
        return False
     
     #そもそも書き込みが終わってないとき
     if self.__status is None:
        return False
     
     #書き込みに失敗した場合(=読み取り専用ファイルや開かれているファイルから読み取って、書き込みしようとしたとき)
     if self.__status.status_code != FileIOResultStatusCodes.IO_SUCCESS:
        return False
        
     
     return True
     
  
   
   def __str__(self):
     src_str=f"ファイル{self.__src_file_path_str}の内容を置換し、"
     dst_str=f"その結果をファイル{self.__dst_file_path_str}に保存"
     if len(self.__dst_file_path_str) == 0 or self.__src_file_path_str == self.__dst_file_path_str:
       dst_str="その結果を上書きで保存"
       
     status_result_str=self.__status and f"{self.__status}" or "まだ、読み取り、書き込みが行われておりません"
     return f"{src_str}{dst_str}\n結果:{status_result_str}"
     
   
   #ファイル選択をし、置換後、元に戻したくなった時に、実際にファイルの内容を開く処理が行えるよう、扱ったそれぞれのパスは公開する
   @property
   def src_file_path_str(self):
     return self.__src_file_path_str
   
   @property
   def dst_file_path_str(self):
     return self.__dst_file_path_str
   
   @classmethod
   def judge_encode(cls,file_path:str):
     file_encodes=("utf_8","utf_8_sig","shift_jis","ascii","euc_jp","iso2022_jp","utf_16","utf_32")
     for one_file_encode in file_encodes:
       f=None
       try:
         f=open(file_path,"rb")
         contents_byte=f.read()
         contents=contents_byte.decode(one_file_encode)
       except UnicodeDecodeError:
         pass
       else:
         return one_file_encode
       finally:
         if f is not None:
           f.close()
     
     return ""
   
   #絶対パス化されていなかったり、拡張子が抜けていたりと、入力が不十分な場合にこちらでその不十分な箇所を補って、正規化する
   @classmethod
   def normalize_dst_file_path_str(cls,original_dst_file_path_str:str,original_src_file_path_str:str):
     
     #書き込み先ファイルパスが未入力の場合は、上書き扱いなので、読み取り元のパスを入れる
     normalized_dst_file_path_str=original_dst_file_path_str.replace(not_sep,os.sep) or original_src_file_path_str.replace(not_sep,os.sep)
     
     if not os.path.isabs(normalized_dst_file_path_str):
       normalized_dst_file_path_str=os.path.abspath(normalized_dst_file_path_str)
     
     #書き込み先のファイルの拡張子を確認
     dst_ext=os.path.splitext(normalized_dst_file_path_str)[1]
     #拡張子があればそれを尊重する。たとえ、読み取り元と書き込み先の拡張子が異なっていても
     if len(dst_ext) != 0:
        return normalized_dst_file_path_str
     
     #以下は書き込み先のファイルの拡張子が指定されなかった場合
     

     #書き込み先が、ディレクトリだった場合は,ディレクトリが指定されたとみなし
     if os.path.isdir(normalized_dst_file_path_str):
       #ファイル名は、読み出し元と同じにする
       file_name=os.path.split(original_src_file_path_str)[1]
       return os.path.join(normalized_dst_file_path_str,file_name)
          
     #それ以外はただの拡張子指定し忘れとみなし、読み出し元と同じ拡張子を補う
     src_ext=os.path.splitext(original_src_file_path_str)[1]
     
     return f"{normalized_dst_file_path_str}{src_ext}"
     
   
     
     
     