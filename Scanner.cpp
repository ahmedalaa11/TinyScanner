#include <stdio.h>
#include <fstream>
#include <iostream>
#include <unordered_map>
#include <queue>

using namespace std;

typedef enum {START,INNUM,INID,INASSIGN,INCOMMENT,INSPECIAL,SYNTXERROR}STATE_type;


int main(){

queue<pair<string,string>> accepted;

unordered_map <string,string> ResWord ;
ResWord["if"]="IF";
ResWord["then"]="THEN";
ResWord["else"]="ELSE";
ResWord["end"]="END";
ResWord["repeat"]="REPEAT";
ResWord["until"]="UNTIL";
ResWord["read"]="READ";
ResWord["write"]="WRITE";

unordered_map <string,string> SpSym ;
SpSym["+"]="PLUS";
SpSym["-"]="MINUS";
SpSym["*"]="MULT";
SpSym["/"]="DIV";
SpSym["="]="EQUAL";
SpSym["<"]="LESSTHAN";
SpSym["("]="OPENBRACKET";
SpSym[")"]="CLOSEDBRACKET";
SpSym[";"]="SEMICOLON";

ifstream ss;
ofstream oo;
ss.open("input.txt",ios::in);

STATE_type STATE= START;
STATE_type prevSTATE= START;
string value,temp;
char c;

while(!ss.eof())
{
    ss.get(c);
    if(STATE==START)
        {
        value="";temp="";
        if(c==' '||c=='\n'||c=='\t'){continue;}
        if(c=='{'){STATE=INCOMMENT;}
        if( c>='0' && c<='9' ){STATE=INNUM;}
        if( c>='a' && c<='z' ){STATE=INID;}
        if(c==':'){value=c;STATE=INASSIGN;continue;}
        temp=c;
        if(SpSym.count(temp)){STATE=INSPECIAL;value=c;}
        }
        if(STATE==START){STATE=SYNTXERROR;}

    if(STATE==INNUM)
        {
        if(c>='0' && c<='9'){value=value+c;continue;}
        else{
            if((c==' ')||(c=='\n')||(c=='\t')){accepted.push(make_pair(value,"NUMBER"));STATE= START;continue;}
            temp=c;
            if(SpSym.count(temp)){accepted.push(make_pair(value,"NUMBER"));value=c;STATE=INSPECIAL;}
            else{STATE=SYNTXERROR;}
            }
        }
    if(STATE==INID)
        {
        if( c>='a' && c<='z')
        {value=value+c;continue;}
        else
        {
            if((c==' ')||(c=='\n')||(c=='\t')){
                if (ResWord.count(value))
                {
                accepted.push(make_pair(value,ResWord[value]));
                STATE= START;continue;
                }
                else{accepted.push(make_pair(value,"IDENTIFIER"));STATE= START;continue;}
                }
            temp=c;
            if(SpSym.count(temp)){accepted.push(make_pair(value,"IDENTIFIER"));value=c;STATE=INSPECIAL;}  
            else{STATE=SYNTXERROR;}
        }
        }        
    if(STATE==INASSIGN){
        if(c=='='){value=value+c;accepted.push(make_pair(value,"ASSIGN"));STATE= START;continue;}
        else{STATE=SYNTXERROR;}
        }

    if(STATE==INCOMMENT){
        value=value+c;
        if(c=='}')
        {//accepted.push(make_pair(value,"COMMENT"));
        STATE= START;continue;}
        }
        
    if(STATE==INSPECIAL){
        accepted.push(make_pair(value,SpSym[value]));STATE= START;continue;
        }
    if(STATE==SYNTXERROR){
        value=value+c;
        if((c==' ')||(c=='\n')||(c=='\t'))
        //{accepted.push(make_pair(value,"SYNTXERROR"));STATE= START;continue;}
        }
}
ss.close();
oo.open("tokens.txt",ios::out);
while(!accepted.empty())
{
oo<<accepted.front().first<<","<<accepted.front().second<<endl;
accepted.pop();
}
oo.close();
return 0;
}