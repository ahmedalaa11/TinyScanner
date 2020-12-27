import os
import numpy as np
from graphviz import Graph as Digraph

os.system("./scanner")

tokens=[[]]
f = open("output.txt", 'r')
for line in f:
    s=line.split(',')
    s[1]=s[1][0:-1]
    tokens.append(s)
del tokens[0]

for l in tokens:
    if l[1]=='IF' or l[1]== 'THEN' or l[1]== 'ELSE' or l[1]== 'END' or l[1]== 'REPEAT' or l[1]== 'UNTIL' or l[1]== 'READ' or l[1]== 'WRITE' or l[1]== 'ASSIGN' or l[1]== 'PLUS' or l[1]== 'MINUS' or l[1]== 'MULT' or l[1]== 'DIV' or l[1]== 'EQUAL' or l[1]== 'LESSTHAN' or l[1]== 'SEMICOLON' or l[1]== 'OPENBRACKET' or l[1]== 'CLOSEDBRACKET':
        l[1]=l[0]

index = 0
nIndex = 1
nodes = []

class node :
    currIndex=0
    fIndex=0
    content=""
    count=0
    children=[]
    drawIndex=0
    Else = 0

def match(token) :
    global index
    if token ==tokens[index][1]:
        index+=1
        return 1
    else:
        print(token,"Error")
        return 0   

# stmt_sequence -> statement {; statement}
def stmnt_seq(fIndex=0, Else=0):
    global index
    while(1):
        stm(fIndex, Else=Else)
        if(index==len(tokens)):
            break
        if(tokens[index][1]!=";"):
            break
        match(";")

# statement -> if_stmt | repeat_stmt | assign_stmt | read_stmt | write_stmt
def stm(fIndex=0, Else=0):
    global index
    if tokens[index][1]=="read":
        read(fIndex, Else=Else)
    elif tokens[index][1]=="if":
        if_stm(fIndex, Else=Else)
    elif tokens[index][1]=="repeat":
        repeat(fIndex, Else=Else)
    elif tokens[index][1]=="IDENTIFIER":
        assign(fIndex, Else=Else)
    elif tokens[index][1]=="write":
        write(fIndex, Else=Else)
    else:
        print("Token error stm")

# if_stmt -> if exp then stmt_sequence [else stmt_sequence] end    
def if_stm(fIndex=0, Else=0):
    global index
    global nIndex
    match("if")
    content="if"
    currIndex=nIndex
    nIndex+=1
    n=node()
    n.currIndex=currIndex
    n.content=content
    n.fIndex=fIndex
    n.Else=Else
    nodes.append(n)   
    exp(fIndex=currIndex, op=1)
    match("then")
    stmnt_seq(fIndex=currIndex)
    if(tokens[index][1]=="else"):
        match("else")
        stmnt_seq(fIndex=currIndex, Else=1)
    match("end")

# repeat_stmt -> repeat stmt_sequence until exp
def repeat(fIndex, Else=0):
    global nIndex
    global index
    match("repeat")
    content="repeat"
    currIndex=nIndex
    nIndex+=1
    n=node()
    n.currIndex=currIndex
    n.content=content
    n.fIndex=fIndex
    n.Else=Else
    nodes.append(n)
    stmnt_seq(currIndex)
    match("until")
    exp(currIndex, op=1)

# assign_stmt -> IDENTIFIER := exp
def assign(fIndex, Else=0):
    global nIndex
    global index
    match("IDENTIFIER")
    content="assign "+"\n" +"("+str(tokens[index-1][0])+")"
    currIndex=nIndex
    nIndex+=1
    n=node()
    n.currIndex=currIndex
    n.content=content
    n.fIndex=fIndex
    n.Else=Else
    nodes.append(n)
    match(":=")
    exp(fIndex=currIndex)

# read_stmt -> read IDENTIFIER
def read(fIndex=0, Else=0):
    global nIndex
    match("read")
    content="read "+"\n" +"("+str(tokens[index][0])+")"
    currIndex=nIndex
    nIndex+=1
    n=node()
    n.currIndex=currIndex
    n.content=content
    n.fIndex=fIndex
    n.Else=Else
    nodes.append(n)
    match("IDENTIFIER")    

# write_stmt -> write exp    
def write(fIndex, Else=0):
    global nIndex
    global index
    match("write")
    content="write "
    currIndex=nIndex
    nIndex+=1
    n=node()
    n.currIndex=currIndex
    n.content=content
    n.fIndex=fIndex
    n.Else=Else
    nodes.append(n)
    exp(fIndex=currIndex)

reserved = ['if','then','else','end','repeat','until','read','write',':=',';']

# exp -> simple_exp [comp_op simple_exp]
# comp_op ->  < | =                 
def exp (fIndex, op=0, Else=0):
    global index
    global nIndex
    
    addOpIndex=[]
    checkIndex=index
    noQos=0
    
    while(tokens[checkIndex][1]!="<" and tokens[checkIndex][1]!='=' and tokens[checkIndex][1] not in reserved and checkIndex != len(tokens)-1):
        if(tokens[checkIndex][1]=="("): 
            noQos+=1
        elif(tokens[checkIndex][1]==")"):
            noQos-=1
        elif((tokens[checkIndex][1]=="+" or tokens[checkIndex][1]=="-") and noQos==0):
            addOpIndex.append(checkIndex)
        checkIndex+=1    
    
    addOpIndexTemp=[]   
    
    if(tokens[checkIndex][1]=='<' or tokens[checkIndex][1]=='='):
        noQos=0
        while(tokens[checkIndex][1] not in reserved):
            
            if(tokens[checkIndex][1]=="("): 
                noQos+=1
            elif(tokens[checkIndex][1]==")"):
                noQos-=1
            elif((tokens[checkIndex][1]=="+" or tokens[checkIndex][1]=="-") and noQos==0):
                addOpIndexTemp.append(checkIndex)
                
            checkIndex+=1
    
    if(op==0):
        currIndex=fIndex
        simple_exp(fIndex=currIndex,addOpIndex=addOpIndex)    
    else:
        currIndex=nIndex
        nIndex+=1
        n=node()
        n.currIndex=currIndex
        n.fIndex=fIndex
        simple_exp(fIndex=currIndex, addOpIndex=addOpIndex)
        if(tokens[index][1]=="<" ):
            match(tokens[index][1])
            n.content="op"+"\n"+"(<)"
            n.Else=Else
            nodes.append(n)
            simple_exp(fIndex = currIndex, addOpIndex = addOpIndexTemp)
        elif(tokens[index][1]=="=" ):
            match(tokens[index][1])
            n.content="op"+"\n"+"(=)"
            n.Else=Else
            nodes.append(n)
            simple_exp(fIndex = currIndex, addOpIndex = addOpIndexTemp)

# simple_exp -> term {add_op term}
# add_op -> + | -
def simple_exp(fIndex, addOpIndex, Else=0):
    global index
    global nIndex
    
    if(len(addOpIndex)==0):        
        multIndex=[]
        checkIndex=index
        noQos=0
        while(tokens[checkIndex][1]!="+" and tokens[checkIndex][1]!= '-' and
              tokens[checkIndex][1] not in reserved and
             checkIndex != len(tokens)-1):
            if(tokens[checkIndex][1]=="("):
                noQos+=1
            elif(tokens[checkIndex][1]==")"):
                noQos-=1
            elif((tokens[checkIndex][1]=="*" or tokens[checkIndex][1]== "/" ) and  noQos==0):
                multIndex.append(checkIndex)
            checkIndex+=1
            
        term(fIndex, multIndex) 
            
    else:
        addOpNodes=[]
        
        for i in range(len(addOpIndex)-1,-1,-1):
            content="op"+"\n" +"("+str(tokens[addOpIndex[i]][1])+")"
            currIndex=nIndex
            nIndex+=1
            n=node()
            n.currIndex=currIndex
            n.content=content
            n.fIndex=fIndex
            n.Else=Else
            nodes.append(n)
            addOpNodes.append(n)
            fIndex=currIndex
                
        multIndex=[]
        checkIndex=index
        noQos=0
        while(tokens[checkIndex][1]!="+" and tokens[checkIndex][1]!= '-' ):
            if(tokens[checkIndex][1]=="("):
                noQos+=1
            elif(tokens[checkIndex][1]==")"):
                noQos-=1
            elif((tokens[checkIndex][1]=="*" or tokens[checkIndex][1]== "/" ) and  noQos==0):
                multIndex.append(checkIndex)
            checkIndex+=1
        
        term(addOpNodes[len(addOpNodes)-1].currIndex,multIndex)
        multIndex=[]
        for i in range(len(addOpIndex)):
            checkIndex+=1
            match(tokens[index][1])
            noQos=0
            while(tokens[checkIndex][1]!="+" and 
                  tokens[checkIndex][1]!= '-' and
                  tokens[checkIndex][1]!='<'and
                  tokens[checkIndex][1]!='=' and tokens[checkIndex][1] not in reserved):
                if(tokens[checkIndex][1]=="("):
                    noQos+=1
                elif(tokens[checkIndex][1]==")"):
                    noQos-=1
                elif((tokens[checkIndex][1]=="*" or tokens[checkIndex][1]== "/") and noQos==0 ):
                    multIndex.append(checkIndex)
                checkIndex+=1
                
            term(addOpNodes[len(addOpNodes)-1-i].currIndex,multIndex)
            multIndex=[]

# term -> factor {mul_op factor}
# mul_op -> * | /
def term(fIndex,multIndex, Else=0):
    global index
    global nIndex
    
    if(len(multIndex)==0):
        factor(fIndex) 
    else:
        multNodes=[]        

        for i in range(len(multIndex)-1,-1,-1):
            content="op"+"\n" +"("+str(tokens[multIndex[i]][1])+")"
            currIndex=nIndex
            nIndex+=1
            n=node()
            n.currIndex=currIndex
            n.content=content
            n.fIndex=fIndex
            n.Else=Else
            nodes.append(n)
            multNodes.append(n)
            fIndex=currIndex

        factor(multNodes[len(multNodes)-1].currIndex)
        for i in range(len(multIndex)):
            match(tokens[index][1])
            factor(multNodes[len(multNodes)-1-i].currIndex)
 
# factor -> ( exp ) | NUMBER | IDENTIFIER
def factor(fIndex, Else=0):
    global index
    global nIndex

    if(tokens[index][1]=="IDENTIFIER"):
        content="id "+"\n" +"("+str(tokens[index][0])+")"
        currIndex=nIndex
        nIndex+=1
        n=node()
        n.currIndex=currIndex
        n.content=content
        n.fIndex=fIndex
        n.Else=Else
        nodes.append(n)
        match(tokens[index][1])
        
    elif(tokens[index][1]=="NUMBER"):
        content="const "+"\n" +"("+str(tokens[index][0])+")"
        currIndex=nIndex
        nIndex+=1
        n=node()
        n.currIndex=currIndex
        n.content=content
        n.fIndex=fIndex
        n.Else=Else
        nodes.append(n)
        match(tokens[index][1])
        
    elif(tokens[index][1]=="("):
        match("(")
        exp(fIndex)
        match(")")
    else:
        print("Token error factor")

stmnt_seq()

# For visualization
p = Digraph('unix', filename = 'parser.gv')
p.node_attr.update(color = 'green3', style = 'filled')

n=len(nodes)
for i in range (n):
    if("op" in nodes[i].content or "id" in nodes[i].content or "const" in nodes[i].content):
        p.node(str(i),label=str(nodes[i].content))
    else:
        p.node(str(i),label=str(nodes[i].content), shape='box')    
    nodes[i].drawIndex=i 
    
for i in range (n):
    if(nodes[i].content=='if'):
        fElse = 0
        foundElse =0
        
        nodes[i].children=[]
        for j in range (n):
            if(nodes[j].fIndex==nodes[i].currIndex):       
                nodes[i].children.append(nodes[j])           
         
        for j in range(len(nodes[i].children)):
            if(nodes[i].children[j].Else==1):
                fElse=1
        
        if(fElse==0):
            
            p.edge( str(i) , str((nodes[i].children[0].drawIndex)) )
            p.edge( str(i) , str((nodes[i].children[1].drawIndex)) )
            with p.subgraph() as s:
                s.attr(rank = 'same')
                s.node(str(nodes[i].children[1].drawIndex))
                for k in range(2, len(nodes[i].children)):
                    s.node(str(nodes[i].children[k].drawIndex)) 
                    p.edge(str(nodes[i].children[k-1].drawIndex), str(nodes[i].children[k].drawIndex))
    
        else:
            p.edge( str(i) , str((nodes[i].children[0].drawIndex)) )
            p.edge( str(i) , str((nodes[i].children[1].drawIndex)) )
            with p.subgraph() as s:
                s.attr(rank = 'same')
                s.node(str(nodes[i].children[1].drawIndex))
                for k in range(2, len(nodes[i].children)):
                    s.node(str(nodes[i].children[k].drawIndex))
                    if nodes[i].children[k].Else==0 or foundElse==1 :
                        p.edge(str(nodes[i].children[k-1].drawIndex), str(nodes[i].children[k].drawIndex))
                    else:
                        p.edge(str(i), str(nodes[i].children[k].drawIndex))
                        foundElse=1             
                   
for i in range (n):
    if(nodes[i].content=='repeat'):
        nodes[i].children=[]
        for j in range (n):
            if(nodes[j].fIndex==nodes[i].currIndex):        
                nodes[i].children.append(nodes[j])
        p.edge( str(i) , str((nodes[i].children[0].drawIndex)) )

        with p.subgraph() as z:
            z.attr(rank = 'same')
            z.node(str(nodes[i].children[1].drawIndex))
            for k in range(1, len(nodes[i].children)-1):
                z.node(str(nodes[i].children[k].drawIndex)) 
                z.edge(str(nodes[i].children[k-1].drawIndex), str(nodes[i].children[k].drawIndex))    

            p.edge( str(i) , str((nodes[i].children[-1].drawIndex)) )
  
for i in range (n): 
    for j in range(n): 
        if nodes[i].currIndex==nodes[j].fIndex:     
            if nodes[i].content!="if" and nodes[i].content!="repeat" :
                p.edge(str(i),str(j))                
                
noFather=[]

for i in range (n):
    if nodes[i].fIndex == 0:
        noFather.append(nodes[i])

for i in range (len(noFather)-1):
    p.edge(str(noFather[i].drawIndex), str(noFather[i+1].drawIndex),constraint='false')  

p.view()
