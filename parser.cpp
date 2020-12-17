#include <stdio.h>
#include <fstream>
#include <iostream>
#include <unordered_map>
#include <queue>

using namespace std;

queue<pair<string,string>> tokens;
static pair<string,string> token;

typedef enum {StmtK,ExpK} NodeKind;
typedef enum {IfK,RepeatK,AssignK,ReadK,WriteK} StmtKind;
typedef enum {OpK,ConstK,IdK} ExpKind;
//typedef enum {Void,Integer,Boolean} ExpType;

FILE* listing;
bool endFile = 0;
struct TreeNode
{ 
  TreeNode * child[3];
  TreeNode * sibling;
  NodeKind nodekind;
  struct kind{ StmtKind stmt; ExpKind exp;} kind;
  struct attr{ string op;
          int val;
          string name; 
          } attr;
};

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

void printTree( TreeNode * tree );

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
  ss.close();

  listing = fopen("myfile.txt","w");
  TreeNode * root = parse();
  fcloseall();
  printTree(root);
  return 0;
}

// Creates a new expression node for syntax tree construction
TreeNode * newExpNode(ExpKind kind)
{ 
  TreeNode * t = new TreeNode;
  int i;
  if (t==nullptr)
    printf("Out of memory error at line");
  else
  {
    for (i=0;i<3;i++) t->child[i] = nullptr;
    t->sibling = nullptr;
    t->nodekind = ExpK;
    t->kind.exp = kind;
    //t->type = Void;
  }
  return t;
}

TreeNode * newStmtNode(StmtKind kind)
{ 
  TreeNode * t = new TreeNode;
  if (t==nullptr)
    printf("Out of memory error at line \n");
  else
  {
    for (int i=0;i<3;i++) t->child[i] = nullptr;
    t->sibling = nullptr;
    t->nodekind = StmtK;
    t->kind.stmt = kind;
    //t->attr.name = "";
  }
  return t;
}

pair<string,string> getToken(void)
{
    pair<string,string> temp = tokens.front();
    tokens.pop();
    // عشان مش هنعرف نعمل بوب بعد ما نرجع فعملنا temp pair
    return temp;
}

//string getTokenVal(void){   return tokens.front().first;}
//string getTokenType(void){  return tokens.front().second;}

//static void match(pair<string,string> expected)
static void match(string expected)
{ 
  //if(token.second.compare(expected.second) != 0)
  if(token.second.compare(expected) == 0)
  {
    token = getToken();
    if (token.second.compare("") == 0)
    {
      endFile = 1;
    }
  } 
  else
  {
    // Error
  }
}

// stmt_sequence -> statement {; statement}
TreeNode * stmt_sequence(void)
{
  TreeNode * t = statement();
  TreeNode * p = t;
  while (token.second.compare("END") != 0 && token.second.compare("ELSE") != 0 && token.second.compare("UNTIL")!= 0 && endFile == 1)
  {
    TreeNode * q;
    match("SEMICOLON");
    q = statement();
    if (q!=nullptr)
    {
      if (t==nullptr) t = p = q;
      else /* now p cannot be nullptr either */
      {
        p->sibling = q;
        p = q;
      }
    }
  }
  return t;
}

// statement -> if_stmt | repeat_stmt | assign_stmt | read_stmt | write_stmt
TreeNode * statement(void)
{
  TreeNode * t = nullptr;
  if(token.second.compare("IF")== 0) t = if_stmt();
  else if(token.second.compare("REPEAT")== 0) t = repeat_stmt();
  else if(token.second.compare("IDENTIFIER")== 0) t = assign_stmt();
  else if(token.second.compare("READ")== 0) t = read_stmt();
  else if(token.second.compare("WRITE")== 0) t = write_stmt();
  return t;
}

// if_stmt -> if exp then stmt_sequence [else stmt_sequence] end
TreeNode * if_stmt(void)
{ 
  TreeNode * t = newStmtNode(IfK);
  match("IF");
  if (t!=nullptr) t->child[0] = exp();
  match("THEN");
  if (t!=nullptr) t->child[1] = stmt_sequence();
  if (token.second.compare("ELSE")== 0)
  {
    match("ELSE");
    if (t!=nullptr) t->child[2] = stmt_sequence();
  }
  match("END");
  return t;
}

// repeat_stmt -> repeat stmt_sequence until exp
TreeNode * repeat_stmt(void)
{ 
  TreeNode * t = newStmtNode(RepeatK);
  match("REPEAT");
  if (t!=nullptr) t->child[0] = stmt_sequence();
  match("UNTIL");
  if (t!=nullptr) t->child[1] = exp();
  return t;
}

//assign_stmt -> IDENTIFIER := exp
TreeNode * assign_stmt(void)
{ 
  TreeNode * t = newStmtNode(AssignK);
  if ((t!=nullptr) && (token.second.compare("IDENTIFIER")== 0))
    t->attr.name = token.first;
  match("IDENTIFIER");
  match("ASSIGN");
  if (t!=nullptr) t->child[0] = exp();
  return t;
}

//read_stmt -> read IDENTIFIER
TreeNode * read_stmt(void)
{ 
  TreeNode * t = newStmtNode(ReadK);
  match("READ");
  if ((t!=nullptr) && (token.second.compare("IDENTIFIER")== 0))
    t->attr.name = token.first;
  match("IDENTIFIER");
  return t;
}

//write_stmt -> write exp
TreeNode * write_stmt(void)
{ 
  TreeNode * t = newStmtNode(WriteK);
  match("WRITE");
  if (t!=nullptr) t->child[0] = exp();
  return t;
}

// exp -> simple_exp [comp_op simple_exp]
// comp_op ->  < | = 
TreeNode * exp(void)
{ 
  TreeNode * t = simple_exp();
  if ((token.second.compare("LESSTHAN")== 0)||(token.second.compare("EQUAL")== 0)) {
    TreeNode * p = newExpNode(OpK);
    if (p!=nullptr)
    {
      p->child[0] = t;
      p->attr.op = token.second;
      t = p;
    }
    match(token.second);
    if (t!=nullptr)
      t->child[1] = simple_exp();
  }
  return t;
}

// simple_exp -> term {add_op term}
// add_op -> + | -
TreeNode * simple_exp(void)
{ 
  TreeNode * t = term();
  while ((token.second.compare("PLUS")== 0)||(token.second.compare("MINUS")== 0))
  { TreeNode * p = newExpNode(OpK);
    if (p!=nullptr) {
      p->child[0] = t;
      p->attr.op = token.second;
      t = p;
      match(token.second);
      t->child[1] = term();
    }
  }
  return t;
}

// term -> factor {mul_op factor}
// mul_op -> * | /
TreeNode * term(void)
{ 
  TreeNode * t = factor();
  while ((token.second.compare("MULT")== 0)||(token.second.compare("DIV")== 0))
  { TreeNode * p = newExpNode(OpK);
    if (p!=nullptr) {
      p->child[0] = t;
      p->attr.op = token.second;
      t = p;
      match(token.second);
      p->child[1] = factor();
    }
  }
  return t;
}

// factor -> ( exp ) | NUMBER | IDENTIFIER
TreeNode * factor(void)
{
  TreeNode * t = nullptr;
  if(token.second.compare("NUMBER")== 0)
  {
      t = newExpNode(ConstK);
      if ((t!=nullptr) && (token.second.compare("NUMBER")== 0))
        t->attr.val = stoi(token.first);
      match("NUMBER");
  }
  else if(token.second.compare("IDENTIFIER")== 0)
  {
      t = newExpNode(IdK);
      if ((t!=nullptr) && (token.second.compare("IDENTIFIER")== 0))
        t->attr.name = token.first;
      match("IDENTIFIER");
  }
  else if(token.second.compare("OPENBRACKET")== 0)
  {
      match("OPENBRACKET");
      t = exp();
      match("CLOSEDBRACKET");
   }
  return t;
}

TreeNode * parse(void)
{ 
  TreeNode * t;
  token = getToken();
  t = stmt_sequence();
  return t;
}

void printTree( TreeNode * tree )
{ 
  int i;
  while (tree != nullptr) {
    if (tree->nodekind==StmtK)
    { switch (tree->kind.stmt) {
        case IfK:
          fprintf(listing,"If\n");
          break;
        case RepeatK:
          fprintf(listing,"Repeat\n");
          break;
        case AssignK:
          fprintf(listing,"Assign to: %s\n",tree->attr.name);
          break;
        case ReadK:
          fprintf(listing,"Read: %s\n",tree->attr.name);
          break;
        case WriteK:
          fprintf(listing,"Write\n");
          break;
        default:
          fprintf(listing,"Unknown ExpNode kind\n");
          break;
      }
    }
    else if (tree->nodekind==ExpK)
    { switch (tree->kind.exp) {
        case OpK:
          fprintf(listing,"Op: ");
          //printToken(tree->attr.op,"\0");
          break;
        case ConstK:
          fprintf(listing,"Const: %d\n",tree->attr.val);
          break;
        case IdK:
          fprintf(listing,"Id: %s\n",tree->attr.name);
          break;
        default:
          fprintf(listing,"Unknown ExpNode kind\n");
          break;
      }
    }
    else fprintf(listing,"Unknown node kind\n");
    for (i=0;i<3;i++)
         printTree(tree->child[i]);
    tree = tree->sibling;
  }
}