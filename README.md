# 資訊/Info
名稱/Name: NewJack  
縮寫/Abbreviation: nj/NJ  
副檔名/File extension: .nj  
相關/Related: jack的派生語言，有參考C++和python  
環境/Environment: python3.8以上  

語法/grammar: ./grammar.bnf  
虛擬碼語法/virtual code: ./vmcode  
編譯器入口/compiler: ./compiler/main.py  
語法高亮(vscode插件)/Syntax Highlight(vscode extension):   
> https://marketplace.visualstudio.com/items?itemName=su2u4.newjack  
> https://marketplace.visualstudio.com/items?itemName=su2u4.newjackvm  

# 使用/use
由於nj編譯器是用python寫成，所以執行時需有python 3.8或以上版本  
## 範例
此指令是將test.nj編譯成test.vm  
```
python ./compiler/main.py ./test.nj -c
```
## 各項參數說明:  
這些flag可以使用一個-與第一個字母組成簡短寫法(ex: -c)  
### --debug
Activates debug mode, providing detailed stack traces and error information when exceptions occur.  
啟動偵錯模式，在發生異常時提供詳細的堆疊追蹤和錯誤資訊。  
### --showast
Displays the Abstract Syntax Tree (AST) generated during the parsing phase.  
顯示解析階段產生的抽象語法樹（AST）。  
### --compile
Compiles the program after parsing, producing a .vm file as output.  
解析後編譯程序，產生.vm 檔案作為輸出。  
### --help
Displays help information. If additional arguments follow this flag, detailed descriptions of those specific options are shown. If no arguments are provided, all available options are displayed.  
顯示幫助資訊。如果此標誌後面有附加參數，則會顯示這些特定選項的詳細描述。如果沒有提供參數，則顯示所有可用選項。  
### --outpath
Specifies the output directory for the compiled result. If not provided, the output defaults to the source file's directory.  
指定編譯結果的輸出目錄。如果未提供，則輸出預設為來源檔案的目錄。  
### --errout
Specifies a file to output error and debug messages. If not provided, these messages are printed to the standard output (stdout).  
指定輸出錯誤和偵錯資訊的檔案。如果未提供，這些訊息將列印到標準輸出（stdout）。  

## 指令語法:
```
python <path>/compiler/main.py <path>/<name>.nj [(--debug|--showast|--compile|--help)] [(--outpath|--errout) <path>]
```

# 語法/grammar
## 變數
nj的變數類型分成四種，分別是全域變數(global)、屬性(attr)、參數(arg)與變數(local)
其中global與attr使用global與describe來聲明  
### global與describe
一個nj檔案由一個global區與許多class組成  
global裡聲明全域變數，格式類似python
```
global {
    global_var_name: global_var_type;
    ...
}
```
class則是由一個describe區、一個constructor與許多function和method組成  
describe裡使用跟global裡一樣的聲明方式聲明class的屬性(attr)
```
class class_name {
    describe {
        attr_name: attr_type;
        ...
    }
}
```

global與describe裡皆不能初始化，變數會被設為0，global應在程式入口處初始化

class、global、describe、constructor、function、method等語句皆是可選的  
### attr與local
arg在subroutine的定義處聲明，使用類似c的語法
```
class class_name {
    function fun_return_type fun_name(arg_type arg_name, ...){
        ...
    }
}
```
而local使用var語句來聲明
```
var var_type var_name;
```
local是唯一可在聲明時初始化的變數類型
```
var var_type var_name = expression;
```
local也可以同時聲明與初始化多個變數
```
var var_type var_name0, var_name1, var_name2 = expression0, expression1, expression2;
```
同一個var語句只能是同一個類型，表達式(expression)可以與變數(local)數量不一樣  
如果表達式(expression)數量多於變數(local)，則多餘的表達式(expression)會被捨棄  
如果表達式(expression)數量少於變數(local)，則多餘的變數(local)會被初始化為0  

attr應在constructor初始化，local可以在聲明時就初始化，也可在使用前再初始化就行  
## subroutine
nj的subroutine分成三種，分別是建構子(constructor)、函式(function)與方法(method)  
三種subroutine的聲明方式
```
class class_name {
    constructor class_name new(arg_type arg_name, ...){
        ...
    }
    function return_var_type fun_name(arg_type arg_name, ...){
        ...
    }
    method return_var_type method_name(arg_type arg_name, ...){
        ...
    }
}
```
### 建構子(constructor)
建構子(constructor)就像是特殊的method，建議取名為new、init等  
回傳值的類型應為此建構子(constructor)所在的class  
第一個參數會是self，類型為目前class，應回傳此self
建構子的呼叫方式:
```
class_name.new(arg, ...);
```
### 函式(function)
函式裡無法使用self，函式無法取得目前class的屬性(attr)，因為沒有目前物件  
函式的呼叫方式:
```
class_name.fun_name(arg, ...);
```
### 方法(method)
method的第一個參數會是self，類型為目前class  
可以使用self來取得目前物件的屬性(attr)  
方法的呼叫方式:
```
obj_name.method_name(arg, ...);
```
## 語句(statement)
nj有var, do, let, if, while, for, return, break這幾個語句  
### var
用來聲明區域變數(local)  
語法:
```
var var_type var_name [{, var_name}] [= expression [{, expression}]] ;
```
### do
用來呼叫所有回傳值為void的subroutine，或者是不需保留回傳值時也可使用  
語法:
```
do (obj.method_name|class.fun_name|class.new)(arg [{, arg}]);
```
### let
用來對變數賦值  
語法:
```
let var = expression;
```
### if
條件判斷式，可以後接elif與else  
語法:
```
if(expression) {
    <statements>
}
elif(expression) {
    <statements>
}
...
else {
    <statements>
}
```
### while
迴圈，可後接else，與python的else同義  
語法:
```
while(expression) {
    <statements>
}
else{
    <statements>
}
```
### for
迴圈，可後接else，與python的else同義  
會新增一個區域變數(local)，變數名由`var_name`聲明  
如果`var_name`後接一個表達式(expression)，則此迴圈由0跑到`var_name`<expression0
如果`var_name`後接一個表達式(expression)，則此迴圈由expression0開始，之後每次增加expression2，直到`var_name`>=expression1  
語法:
```
for(var_name, expression0[;expression1;expression2]) {
    <statements>
}
else{
    <statements>
}
```
### return
回傳值  
如果回傳值的類型為void，則不應回傳任何變數  
建構子(constructor)內的return應回傳self  
語法:
```
return [(var|self)];
```
### break
跳出for-loop與while-loop，且會一併跳過else段  
可後接數字跳出多層迴圈  
語法:
```
break [int];
```
## 表達式(expression)
### 表達式(expression)
表達式由數個term與操作符(operator)組成
語法:
```
<expression> ::= <term> [{<operator> <term>}]
```
### term
term可以是: int, float, char, str, call, var, (expression), -term, !term, false, true, self  
語法:
```
<term> ::= <str> | <int> | <float> | false | true | self | (- | !)<term> | <call> | <var> | (<expression>)
```
### 操作符(operator)
operator列表: +, -, *, /, |, &, <<, >>, ==, !=, >=, <=, >, <
<<與>>是算術移位
==, !=, >=, <=, >, <是邏輯操作符(logical operator)，他們的回傳值一定是true或false
## 其他/other
### 程式入口(enter)
在一個檔案的最外層使用enter關鍵字聲明一段程式碼  
可以視為無class無arg的function  
同時編譯的所有檔案裡只能有一個enter  
在enter裡return會視為關閉程式  
回傳值視為exit code  
語法:
```
enter {
    <statements>
}
```
### self的總結
self只能在建構子(constructor)與方法(method)中使用  
self是關鍵字，所以不能把變數命名成self  
在聲明時與呼叫時皆不用寫出self  
self的類型(type)為當前class
在method中self是呼叫時的物件(obj)  
在constructor中self是一個屬性皆為0的空物件
### 一些細節
操作符(operator)在預設條件下會直接拿變數實際值去計算
所以如果變數是自定義的類型可能會變成拿obj的第一個attr或obj的attr數量去計算  

compiler裡有個built_in.py，裡面放著應為內建的東西  
這只是暫時的，因為目前這些內建的都還沒寫出實現，所以用built_in.py來避免編譯時出錯
