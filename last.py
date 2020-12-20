import os
import numpy as np
from graphviz import Graph as Digraph

os.system("./scanner")

tokens=[[]]
f = open("tokens.txt", 'r')
for line in f:
    s=line.split(',')
    s[1]=s[1][0:-1]
    tokens.append(s)
del tokens[0]
tokens.append(['end','END'])

for lst in tokens:
    if lst[1]=='IF' or lst[1]== 'THEN' or lst[1]== 'ELSE' or lst[1]== 'END' or lst[1]== 'REPEAT' or lst[1]== 'UNTIL' or lst[1]== 'READ' or lst[1]== 'WRITE' or lst[1]== 'ASSIGN' or lst[1]== 'PLUS' or lst[1]== 'MINUS' or lst[1]== 'MULT' or lst[1]== 'DIV' or lst[1]== 'EQUAL' or lst[1]== 'LESSTHAN' or lst[1]== 'SEMICOLON' or lst[1]== 'OPENBRACKET' or lst[1]== 'CLOSEDBRACKET':
        lst[1]=lst[0]

index = 0
node_index = 1
nodes = []

class node :
    my_index=0
    father_index=0
    content=""
    count=0
    children=[]
    draw_index=0
    R_U_else = 0

def match(token) :
    global index
    if token==tokens[index][1]:
        index+=1
        return 1
    else:
        print(token,"Error")
        return 0   

# stmt_sequence -> statement {; statement}
def stmnt_seq(father_index=0, R_U_else=0):
    global index
    while(1):
        stm(father_index, R_U_else=R_U_else)
        if(index==len(tokens)):
            break
        if(tokens[index][1]!=";"):
            break
        match(";")

# statement -> if_stmt | repeat_stmt | assign_stmt | read_stmt | write_stmt
def stm(father_index=0, R_U_else=0):
    global index
    if tokens[index][1]=="read":
        read(father_index, R_U_else=R_U_else)
    elif tokens[index][1]=="if":
        if_stm(father_index, R_U_else=R_U_else)
    elif tokens[index][1]=="repeat":
        repeat(father_index, R_U_else=R_U_else)
    elif tokens[index][1]=="IDENTIFIER":
        assign(father_index, R_U_else=R_U_else)
    elif tokens[index][1]=="write":
        write(father_index, R_U_else=R_U_else)
    else:
        print("Token error stm")

# if_stmt -> if exp then stmt_sequence [else stmt_sequence] end    
def if_stm(father_index=0, R_U_else=0):
    global index
    global node_index
    match("if")
    
    content="if"
    my_index=node_index
    node_index+=1
    n=node()
    n.my_index=my_index
    n.content=content
    n.father_index=father_index
    n.R_U_else=R_U_else
    nodes.append(n)   
    
    exp(father_index=my_index, op=1)
    match("then")
    stmnt_seq(father_index=my_index)
    if(tokens[index][1]=="else"):
        match("else")
        stmnt_seq(father_index=my_index, R_U_else=1)
    match("end")

# repeat_stmt -> repeat stmt_sequence until exp
def repeat(father_index, R_U_else=0):
    global node_index
    global index
    match("repeat")
    
    content="repeat"
    my_index=node_index
    node_index+=1
    n=node()
    n.my_index=my_index
    n.content=content
    n.father_index=father_index
    n.R_U_else=R_U_else
    nodes.append(n)
    
    stmnt_seq(my_index)
    match("until")
    exp(my_index, op=1)

# assign_stmt -> IDENTIFIER := exp
def assign(father_index, R_U_else=0):
    global node_index
    global index
    match("IDENTIFIER")
    content="assign "+"\n" +"("+str(tokens[index-1][0])+")"
    my_index=node_index
    node_index+=1
    n=node()
    n.my_index=my_index
    n.content=content
    n.father_index=father_index
    n.R_U_else=R_U_else
    nodes.append(n)
    match(":=")
    exp(father_index=my_index)

# read_stmt -> read IDENTIFIER
def read(father_index=0, R_U_else=0):
    global node_index
    match("read")
    content="read "+"\n" +"("+str(tokens[index][0])+")"
    my_index=node_index
    node_index+=1
    n=node()
    n.my_index=my_index
    n.content=content
    n.father_index=father_index
    n.R_U_else=R_U_else
    nodes.append(n)
    match("IDENTIFIER")    

# write_stmt -> write exp    
def write(father_index, R_U_else=0):
    global node_index
    global index
    match("write")
    content="write "
    my_index=node_index
    node_index+=1
    n=node()
    n.my_index=my_index
    n.content=content
    n.father_index=father_index
    n.R_U_else=R_U_else
    nodes.append(n)
    exp(father_index=my_index)

reserved = ['if','then','else','end','repeat','until','read','write',':=',';']

# exp -> simple_exp [comp_op simple_exp]
# comp_op ->  < | =                 
def exp (father_index, op=0, R_U_else=0):
    # ((x+10)+Y) < 10
    # 6-5 < x
    #(7-2)
    # x = 7
    
    global index
    global node_index
    
    addop_index=[]
    check_index=index
    no_qos=0
    
    while(tokens[check_index][1]!="<" and
          tokens[check_index][1]!='=' and tokens[check_index][1] not in reserved and
         check_index != len(tokens)-1):
        
        if(tokens[check_index][1]=="("): 
            no_qos+=1
        elif(tokens[check_index][1]==")"):
            no_qos-=1
        elif((tokens[check_index][1]=="+" or tokens[check_index][1]=="-") and no_qos==0):
            addop_index.append(check_index)
        check_index+=1    
    
    addop_index2=[]   
    
    if(tokens[check_index][1]=='<' or tokens[check_index][1]=='='):
        no_qos=0
        while(tokens[check_index][1] not in reserved):
            
            if(tokens[check_index][1]=="("): 
                no_qos+=1
            elif(tokens[check_index][1]==")"):
                no_qos-=1
            elif((tokens[check_index][1]=="+" or tokens[check_index][1]=="-") and no_qos==0):
                addop_index2.append(check_index)
                
            check_index+=1
    
    if(op==0):
        my_index=father_index
        simple_exp(father_index=my_index,addop_index=addop_index)    
    else:
        my_index=node_index
        node_index+=1
        n=node()
        n.my_index=my_index
        n.father_index=father_index
        simple_exp(father_index=my_index, addop_index=addop_index)
        if(tokens[index][1]=="<" ):
            match(tokens[index][1])
            n.content="op"+"\n"+"(<)"
            n.R_U_else=R_U_else
            nodes.append(n)
            simple_exp(father_index=my_index,addop_index=addop_index2)
        elif(tokens[index][1]=="=" ):
            match(tokens[index][1])
            n.content="op"+"\n"+"(=)"
            n.R_U_else=R_U_else
            nodes.append(n)
            simple_exp(father_index=my_index,addop_index=addop_index2)

# simple_exp -> term {add_op term}
# add_op -> + | -
def simple_exp(father_index, addop_index, R_U_else=0):
    #(x+10*Y)
    #10+20-30-45
    global index
    global node_index
    
    if(len(addop_index)==0):        
        
        mul_index=[]
        check_index=index
        no_qos=0
        while(tokens[check_index][1]!="+" and tokens[check_index][1]!= '-' and
              tokens[check_index][1] not in reserved and
             check_index != len(tokens)-1):
            if(tokens[check_index][1]=="("):
                no_qos+=1
            elif(tokens[check_index][1]==")"):
                no_qos-=1
            elif((tokens[check_index][1]=="*" or tokens[check_index][1]== "/" ) and  no_qos==0):
                mul_index.append(check_index)
            check_index+=1
            
        term(father_index,mul_index) 
            
    else:
        addop_nodes=[]
        
        for i in range(len(addop_index)-1,-1,-1):
            
            content="op"+"\n" +"("+str(tokens[addop_index[i]][1])+")"
            my_index=node_index
            node_index+=1
            n=node()
            n.my_index=my_index
            n.content=content
            n.father_index=father_index
            n.R_U_else=R_U_else
            nodes.append(n)
            addop_nodes.append(n)
            father_index=my_index
                
        #8+39-30+60-20
        mul_index=[]
        check_index=index
        no_qos=0
        while(tokens[check_index][1]!="+" and tokens[check_index][1]!= '-' ):
            if(tokens[check_index][1]=="("):
                no_qos+=1
            elif(tokens[check_index][1]==")"):
                no_qos-=1
            elif((tokens[check_index][1]=="*" or tokens[check_index][1]== "/" ) and  no_qos==0):
                mul_index.append(check_index)
            check_index+=1
        
        
        term(addop_nodes[len(addop_nodes)-1].my_index,mul_index)
        mul_index=[]
        for i in range(len(addop_index)):
            check_index+=1
            match(tokens[index][1])
            no_qos=0
            while(tokens[check_index][1]!="+" and 
                  tokens[check_index][1]!= '-' and
                  tokens[check_index][1]!='<'and
                  tokens[check_index][1]!='=' and tokens[check_index][1] not in reserved):
                if(tokens[check_index][1]=="("):
                    no_qos+=1
                elif(tokens[check_index][1]==")"):
                    no_qos-=1
                elif((tokens[check_index][1]=="*" or tokens[check_index][1]== "/") and no_qos==0 ):
                    mul_index.append(check_index)
                check_index+=1
                
            term(addop_nodes[len(addop_nodes)-1-i].my_index,mul_index)
            mul_index=[]
                 
 #      8*5/2 + 4*3*3 - 4*3
 #              -
 #           +      20
 #         -    60
 #       +    30     
 #     8   39       

# term -> factor {mul_op factor}
# mul_op -> * | /
def term(father_index,mul_index, R_U_else=0):
    global index
    global node_index
    
    if(len(mul_index)==0):
        factor(father_index) 
    
    else:
        mul_nodes=[]        

        for i in range(len(mul_index)-1,-1,-1):
            
            content="op"+"\n" +"("+str(tokens[mul_index[i]][1])+")"
            my_index=node_index
            node_index+=1
            n=node()
            n.my_index=my_index
            n.content=content
            n.father_index=father_index
            n.R_U_else=R_U_else
            nodes.append(n)
            mul_nodes.append(n)
            father_index=my_index
        #8*(39/30+40)/60*20

        factor(mul_nodes[len(mul_nodes)-1].my_index)
        for i in range(len(mul_index)):
            match(tokens[index][1])
            factor(mul_nodes[len(mul_nodes)-1-i].my_index)
   #          *
  #        /     20
 #     *     60         
#    8  exp
 
# factor -> ( exp ) | NUMBER | IDENTIFIER
def factor(father_index, R_U_else=0):
    global index
    global node_index
    if(tokens[index][1]=="IDENTIFIER"):
        content="id "+"\n" +"("+str(tokens[index][0])+")"
        my_index=node_index
        node_index+=1
        n=node()
        n.my_index=my_index
        n.content=content
        n.father_index=father_index
        n.R_U_else=R_U_else
        nodes.append(n)
        match(tokens[index][1])
        
    elif(tokens[index][1]=="NUMBER"):
        content="const "+"\n" +"("+str(tokens[index][0])+")"
        my_index=node_index
        node_index+=1
        n=node()
        n.my_index=my_index
        n.content=content
        n.father_index=father_index
        n.R_U_else=R_U_else
        nodes.append(n)
        match(tokens[index][1])
        
    elif(tokens[index][1]=="("):
        match("(")
        exp(father_index)
        match(")")
    else:
        print("token error factor")


stmnt_seq()

# For visualization
p = Digraph('unix', filename = 'parser.gv')
p.attr(size = '6,6')
p.node_attr.update(color = 'lightblue2', style = 'filled', ordering = 'out' )

n=len(nodes)
for i in range (n):
    if("op" in nodes[i].content or "id" in nodes[i].content or "const" in nodes[i].content):
        p.node(str(i),label=str(nodes[i].content))
    else:
        p.node(str(i),label=str(nodes[i].content),shape='box')    
    nodes[i].draw_index=i 
    
for i in range (n):
    if(nodes[i].content=='if'):
        feeh_Else = 0
        found_Else =0
        
        nodes[i].children=[]
        for j in range (n):
            if(nodes[j].father_index==nodes[i].my_index):       
                nodes[i].children.append(nodes[j])           
         
        for j in range(len(nodes[i].children)):
            if(nodes[i].children[j].R_U_else==1):
                feeh_Else=1
        
        if(feeh_Else==0):
            
            p.edge( str(i) , str((nodes[i].children[0].draw_index)) )
            p.edge( str(i) , str((nodes[i].children[1].draw_index)) )
            with p.subgraph() as s:
                s.attr(rank = 'same')
                s.node(str(nodes[i].children[1].draw_index))
                for k in range(2, len(nodes[i].children)):
                    s.node(str(nodes[i].children[k].draw_index)) 
                    p.edge(str(nodes[i].children[k-1].draw_index), str(nodes[i].children[k].draw_index))
    
        else:
            p.edge( str(i) , str((nodes[i].children[0].draw_index)) )
            p.edge( str(i) , str((nodes[i].children[1].draw_index)) )
            with p.subgraph() as s:
                s.attr(rank = 'same')
                s.node(str(nodes[i].children[1].draw_index))
                for k in range(2, len(nodes[i].children)):
                    s.node(str(nodes[i].children[k].draw_index))
                    if nodes[i].children[k].R_U_else==0 or found_Else==1 :
                        p.edge(str(nodes[i].children[k-1].draw_index), str(nodes[i].children[k].draw_index))
                    else:
                        p.edge(str(i), str(nodes[i].children[k].draw_index))
                        found_Else=1             
                   
for i in range (n):
    if(nodes[i].content=='repeat'):
        nodes[i].children=[]
        for j in range (n):
            if(nodes[j].father_index==nodes[i].my_index):        
                nodes[i].children.append(nodes[j])

        p.edge( str(i) , str((nodes[i].children[0].draw_index)) )

        with p.subgraph() as sss:

            sss.attr(rank = 'same')
            sss.node(str(nodes[i].children[1].draw_index))
            for k in range(1, len(nodes[i].children)-1):
                sss.node(str(nodes[i].children[k].draw_index)) 
                sss.edge(str(nodes[i].children[k-1].draw_index), str(nodes[i].children[k].draw_index))    

            p.edge( str(i) , str((nodes[i].children[-1].draw_index)) )
  
for i in range (n): 

    for j in range(n):
        
        if nodes[i].my_index==nodes[j].father_index:
              
            if nodes[i].content!="if" and nodes[i].content!="repeat" :
                p.edge(str(i),str(j))                
                
no_father=[]

for i in range (n):
    if nodes[i].father_index == 0:
        no_father.append(nodes[i])
      
for i in range (len(no_father)-1):
    p.edge(str(no_father[i].draw_index), str(no_father[i+1].draw_index),constraint='false')  

p.view()
