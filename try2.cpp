#include <stdio.h>
#include <fstream>
#include <iostream>
#include <unordered_map>
#include <queue>

using namespace std;

typedef enum {START,INNUM,INID,INASSIGN,INCOMMENT,INSPECIAL}STATE_type;
//string classify_word(string word){}

int main(){

queue<pair<string,string>> accepted;

unordered_map <string,string> ResWord ;
ResWord["if"]="IF";ResWord["then"]="THEN";ResWord["else"]="ELSE";ResWord["end"]="END";
ResWord["repeat"]="REPEAT";ResWord["untill"]="UNTILL";ResWord["read"]="READ";ResWord["write"]="WRITE";

unordered_map <string,string> SpSym ;
SpSym["+"]="PLUS";SpSym["-"]="MINUS";SpSym["*"]="MULTIPLY";SpSym["/"]="DIVIDED";SpSym["="]="EQUAL";
SpSym["<"]="LESS THAN";SpSym["("]="OPEN BRACKET";SpSym[")"]="CLOSE BRACKET";SpSym[";"]="SEMI COLON";

string code;
code="read x; {input an integer }if 0 < x then { don’t compute if x <= 0 }  fact := 1;";
STATE_type STATE= START;
STATE_type prevSTATE= START;
string value,temp;
for (auto c:code){

    if(STATE==START)
        {
        if(c=='{'){STATE=INCOMMENT;}
        if( c>='0' && c<='9' ){STATE=INNUM;}
        if( c>='a' && c<='z' ){STATE=INID;}
        if(c==':'){STATE=INASSIGN;}
        temp=c;
        if(SpSym.count(temp)){STATE=INSPECIAL;value=c;}
        }

    if(STATE==INNUM)
        {
        if(c>='0' && c<='9'){value=value+c;continue;}
        accepted.push(make_pair(value,"NUM"));value=c;
        if(SpSym.count(value)){STATE=INSPECIAL;}
        else{value="";STATE= START;continue;}
        }
       
    if(STATE==INID){
        if( c>='a' && c<='z')
        {value=value+c;continue;}
        if (ResWord.count(value))
        {
        accepted.push(make_pair(value,ResWord[value]));value="";
        STATE= START;continue;
        }
        accepted.push(make_pair(value,"ID"));value=c;
        if(SpSym.count(value))
        {STATE=INSPECIAL;}   
        else {value="";STATE= START;continue;}
        }        
    if(STATE==INASSIGN){
        value=value+c;
        if( c=='=')
        {
        accepted.push(make_pair(value,"ASSIGN"));
        value="";
        STATE= START;
        continue;
        }
        }

    if(STATE==INCOMMENT){
        value=value+c;
        if(c=='}')
        {accepted.push(make_pair(value,"COMMENT"));value="";STATE= START;continue;}
        }
        
    if(STATE==INSPECIAL){
        accepted.push(make_pair(value,SpSym[value]));value="";STATE= START;continue;
        }

}

while(!accepted.empty())
{
cout<<accepted.front().first<<","<<accepted.front().second<<endl;
accepted.pop();
}
return 0;
}