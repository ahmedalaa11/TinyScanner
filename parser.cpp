#include <stdio.h>
#include <fstream>
#include <iostream>
#include <unordered_map>
#include <queue>
#include <sstream>
#include <string>

using namespace std;

queue<pair<string,string>> tokens;
static pair<string,string> token;


typedef enum {StmtK,ExpK} NodeKind;
typedef enum {IfK,RepeatK,AssignK,ReadK,WriteK} StmtKind;
typedef enum {OpK,ConstK,IdK} ExpKind;

//typedef enum {Void,Integer,Boolean} ExpType;

//typedef enum {IF,THEN,ELSE,END,REPEAT,UNTIL,READ,WRITE,PLUS,MINUS,MULT,DIV,EQUAL,LESSTHAN,OPENBRACKET,CLOSEDBRACKET,SEMICOLON, IDENTIFIER, NUMBER, ASSIGN, COMMENT } TokenType;

typedef struct treeNode
{ 
    struct treeNode * child[3];
    struct treeNode * sibling;
    NodeKind nodekind;
    union { StmtKind stmt; ExpKind exp;} kind;
    union { string op;
            int val;
            string name; } attr;
    //ExpType type; /* for type checking of exps */
} TreeNode;

TreeNode * newExpNode(ExpKind kind);
TreeNode * newStmtNode(StmtKind kind);
pair<string,string> getToken(void);
static void match(string expected);

static TreeNode * stmt_sequence(void);
static TreeNode * statement(void);
static TreeNode * if_stmt(void);
static TreeNode * repeat_stmt(void);
static TreeNode * assign_stmt(void);
static TreeNode * read_stmt(void);
static TreeNode * write_stmt(void);
static TreeNode * exp(void);
static TreeNode * simple_exp(void);
static TreeNode * term(void);
static TreeNode * factor(void);

TreeNode * parse(void);

int main()
{
    ifstream ss;
    ofstream oo;
    ss.open("output.txt",ios::in);

    string line;

    while (getline(ss, line))
    {
        int commaIndex = line.find(",");
        string tokenval = line.substr (0, commaIndex);
        string tokentype = line.substr(commaIndex + 1);
        tokens.push(make_pair(tokenval,tokentype));
    }
    TreeNode * root = parse();
    return 0;
}

// Creates a new expression node for syntax tree construction
TreeNode * newExpNode(ExpKind kind)
{ TreeNode * t = (TreeNode *) malloc(sizeof(TreeNode));
  int i;
  if (t==NULL)
    printf("Out of memory error at line");
  else {
    for (i=0;i<3;i++) t->child[i] = NULL;
    t->sibling = NULL;
    t->nodekind = ExpK;
    t->kind.exp = kind;
    //t->type = Void;
  }
  return t;
}

TreeNode * newStmtNode(StmtKind kind)
{ TreeNode * t = (TreeNode *) malloc(sizeof(TreeNode));
  int i;
  if (t==NULL)
    printf("Out of memory error at line \n");
  else {
    for (i=0;i<3;i++) t->child[i] = NULL;
    t->sibling = NULL;
    t->nodekind = StmtK;
    t->kind.stmt = kind;
  }
  return t;
}

pair<string,string> getToken(void)
{
    return tokens.front();
    tokens.pop();
}

string getTokenVal(void)
{
    return tokens.front().first;
}

string getTokenType(void)
{
    return tokens.front().second;
}

/*static void match(pair<string,string> expected)
{ 
  if(token.second.compare(expected.second) != 0)
  {
    token = getToken();
  } 
  else
  {
    // Error
  }
}*/
static void match(string expected)
{ 
  if(token.second.compare(expected) != 0)
  {
    token = getToken();
  } 
  else
  {
    // Error
  }
}

TreeNode * statement(void)
{
    TreeNode * t = NULL;
    if(token.second.compare("IF")!= 0) t = if_stmt();
    else if(token.second.compare("REPEAT")!= 0) t = repeat_stmt();
    else if(token.second.compare("IDENTIFIER")!= 0) t = assign_stmt();
    else if(token.second.compare("READ")!= 0) t = read_stmt();
    else if(token.second.compare("WRITE")!= 0) t = write_stmt();
    return t;
}

TreeNode * stmt_sequence(void)
{
  TreeNode * t = statement();
  TreeNode * p = t;
  while (token.second.compare("END") != 0 && token.second.compare("ELSE") != 0 && token.second.compare("UNTIL")!= 0)
  {
    TreeNode * q;
    match("SEMI");
    q = statement();
    if (q!=NULL) {
      if (t==NULL) t = p = q;
      else /* now p cannot be NULL either */
      { p->sibling = q;
        p = q;
      }
    }
  }
  return t;
}

TreeNode * if_stmt(void)
{ TreeNode * t = newStmtNode(IfK);
  match("IF");
  if (t!=NULL) t->child[0] = exp();
  match("THEN");
  if (t!=NULL) t->child[1] = stmt_sequence();
  if (token.second.compare("ELSE")!= 0) {
    match("ELSE");
    if (t!=NULL) t->child[2] = stmt_sequence();
  }
  match("END");
  return t;
}

TreeNode * repeat_stmt(void)
{ TreeNode * t = newStmtNode(RepeatK);
  match("REPEAT");
  if (t!=NULL) t->child[0] = stmt_sequence();
  match("UNTIL");
  if (t!=NULL) t->child[1] = exp();
  return t;
}

TreeNode * assign_stmt(void)
{ TreeNode * t = newStmtNode(AssignK);
  if ((t!=NULL) && (token.second.compare("IDENTIFIER")!= 0))
    t->attr.name = token.first;
  match("IDENTIFIER");
  match("ASSIGN");
  if (t!=NULL) t->child[0] = exp();
  return t;
}

TreeNode * read_stmt(void)
{ TreeNode * t = newStmtNode(ReadK);
  match("READ");
  if ((t!=NULL) && (token.second.compare("IDENTIFIER")!= 0))
    t->attr.name = token.first;
  match("IDENTIFIER");
  return t;
}

TreeNode * write_stmt(void)
{ TreeNode * t = newStmtNode(WriteK);
  match("WRITE");
  if (t!=NULL) t->child[0] = exp();
  return t;
}

TreeNode * exp(void)
{ TreeNode * t = simple_exp();
  if ((token.second.compare("LESSTHAN")!= 0)||(token.second.compare("EQUAL")!= 0)) {
    TreeNode * p = newExpNode(OpK);
    if (p!=NULL) {
      p->child[0] = t;
      p->attr.op = token.second;
      t = p;
    }
    match(token.second);
    if (t!=NULL)
      t->child[1] = simple_exp();
  }
  return t;
}

TreeNode * simple_exp(void)
{ TreeNode * t = term();
  while ((token.second.compare("PLUS")!= 0)||(token.second.compare("MINUS")!= 0))
  { TreeNode * p = newExpNode(OpK);
    if (p!=NULL) {
      p->child[0] = t;
      p->attr.op = token.second;
      t = p;
      match(token.second);
      t->child[1] = term();
    }
  }
  return t;
}

TreeNode * term(void)
{ TreeNode * t = factor();
  while ((token.second.compare("MULT")!= 0)||(token.second.compare("DIV")!= 0))
  { TreeNode * p = newExpNode(OpK);
    if (p!=NULL) {
      p->child[0] = t;
      p->attr.op = token.second;
      t = p;
      match(token.second);
      p->child[1] = factor();
    }
  }
  return t;
}

TreeNode * factor(void)
{
  TreeNode * t = NULL;
  if(token.second.compare("NUMBER")!= 0) t = if_stmt();
  {
      t = newExpNode(ConstK);
      if ((t!=NULL) && (token.second.compare("NUMBER")!= 0))
        t->attr.val = stoi(token.first);
      match("NUMBER");
  }
  if(token.second.compare("IDENTIFIER")!= 0) t = if_stmt();
  {
      t = newExpNode(IdK);
      if ((t!=NULL) && (token.second.compare("IDENTIFIER")!= 0))
        t->attr.name = token.first;
      match("ID");
  }
  if(token.second.compare("OPENBRACKET")!= 0) t = if_stmt();
  {
      match("OPENBRACKET");
      t = exp();
      match("CLOSEDBRACKET");
   }
  return t;
}

TreeNode * parse(void)
{ TreeNode * t;
  token = getToken();
  t = stmt_sequence();
  return t;
}