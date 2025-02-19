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
這些指令是將./test4/test.nj編譯成./test4/test.asm，同時產生test.vm與_o0、_o1與_o2版本
```sh
> python ./compiler/main.py ./test4/test.nj ./built_in/list.nj -c
Processing file: D:\NewJack\test4\test.nj
File D:\NewJack\test4\test.nj processed successfully
Processing file: D:\NewJack\built_in\list.nj
File D:\NewJack\built_in\list.nj processed successfully
compile start
compile end
Compile successful: D:\NewJack\test4\test.vm

> python ./format.py ./test4/test.vm
> python ./assembler.py ./test4/test.vm -o0 -o1 -o2
> 
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
python <path>/compiler/main.py <path>/<name>.nj [--debug] [--showast] [--compile] [--help] [--outpath <path>] [--errout <path>]
```
## 工具/tools
還有三個工具，一是format.py，二是assembler.py，三是emulator.py  

format.py可以把.nj文件或.vm文件格式化，可在路徑後方加上vm或nj來無視副檔名強制格式化  
語法:
```
python <path>/format.py (<file path> | <dir path>) [vm | nj]
```
assembler.py可以把.vm轉換成binary file，目前無法拿來執行，預計之後會用python寫出一個模擬器來運行他  
assembler.py接受三個可選的flag(`-o0`、`-o1`和`-o2`)與一個路徑參數，`-o0`、`-o1`和`-o2`這三個flag是為了方便debug，它會輸出中間結果  
語法:
```
python <path>/assembler.py <file path> [-o0][-o1][-o2]
```
emulator.py是一個模擬器，接受一個參數，此參數可以是.vm檔案或者是.asm檔案  
如果是.vm檔案，emulator會把它轉換成.asm後再執行  
語法:
```
python <path>/emulator.py <file path>/<file name>(.asm | .vm)
```
> 註: 目前完全無法得知模擬結果，只能知道vm語法是否有錯誤

# 語法/grammar
## 變數
nj的變數類型分成四種，分別是全域變數(global)、屬性(attr)、參數(arg)與變數(local)
### attr與local
arg在subroutine的定義處聲明，使用類似c的語法
```
class class_name {
    function fun_return_type fun_name(arg_type arg_name, ...){
        ...
    }
}
```
其他的global、attr與local使用var語句來聲明，是否初始化是可選的
```
var <type> <name> [= <expression> ];
```
也可以同時聲明與初始化多個變數
```
var <type> <name> [{, <name>}] [= <expression> [{, <expression>}]];
```
同一個var語句只能是同一個類型，表達式(expression)可以與變數數量不一樣  
如果表達式(expression)數量多於變數，會產生錯誤  
如果表達式(expression)數量少於變數，則多餘的變數會被初始化為0  

global應在main.main聲明並初始化  
attr應在constructor聲明並初始化  
local可以在聲明時就初始化，也可在使用前再初始化就行  
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
let <var> = <expression>;
```
### if
條件判斷式，可以後接elif與else  
語法:
```
if(<expression>) {
    <statements>
}
elif(<expression>) {
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
while(<expression>) {
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
for(var_name, <expression0>[, <expression1>, <expression2>]) {
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
return [(<var>|self)];
```
### break
跳出for-loop與while-loop，且會一併跳過else段  
可後接數字跳出多層迴圈  
跳出多層迴圈時不可跳出超過subroutine  
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
預設的入口函式是main.main，可用編譯時傳入的參數改變  
同時編譯的所有檔案裡只能有一個入口函式  
在入口函式裡return會視為關閉程式  
語法:
```
class main {
    function void main(pass) {
        <statements>
    }
}
```
### self的總結
self只能在建構子(constructor)與方法(method)中使用  
self是關鍵字，所以不能把變數命名成self  
在聲明時與呼叫時皆不用寫出self  
self的類型(type)為當前class
在method中self是呼叫時的物件(obj)  
在constructor中self是一個屬性皆為0的空物件
### 關於pass與void關鍵字
所有空的()內都需要加上pass關鍵字  
如果subroutine回傳值類型為void，return時後方須直接接上;，不可有其他東西  
### 一些細節
操作符(operator)在預設條件下會直接拿變數實際值去計算
所以如果變數是自定義的類型可能會變成拿obj的第一個attr或obj的attr數量去計算  

~~compiler裡有個built_in.py，裡面放著應為內建的東西  
這只是暫時的，因為目前這些內建的都還沒寫出實現，所以用built_in.py來避免編譯時出錯~~  
目前把built_in提出來，裡面放著built_in.py與其他內建類型的nj實現  
目前的built_in.py還只是暫時替代產物，之後會換成透過import或include之類的方式實現  

# 待施工
1. 完全無類型檢查，compiler內應該做一些類型檢查  
2. 缺少泛型或重載運算子等手段  
3. 缺少include或import等手段來導入其他nj file  
4. 完成print、input  
5. 建立與設備通信的定義，方便emulator.py模擬輸出方式  
