#pragma once

#include <cmath>
#include <cstdlib>
#include <ctime>
#include <SDL/SDL.h>
#include <SDL/SDL_draw.h>
#include <SDL/SDL_framerate.h>

class mazeGenerator{
public:
	static void generateMaze(int *map, bool *path, int w, int h);

private:

};


typedef class _node
{
private:
	friend class list;
	friend class BSTree;
	_node *next = nullptr;		//链表下一项（如果这个节点在Open或者Close表中）
	_node *lchild = nullptr;
	_node *rchild = nullptr;
	_node *parentT = nullptr;	//使用BT存储Tile
	short bf = 0;
	bool bInTree = false;
	bool bAdded = false;
public:
	int gPast;					//实际已经走了的距离
	int hEst;					//启发式函数估计出的价值
	int fValue;					//估值总计
	int x, y;					//节点地图坐标
	int tileNum;				//唯一块编号（x * 总列数 + y）
	_node *children[8];			//指向四个孩子的坐标
	_node *parent = nullptr;	//父节点
	_node();
} node;


class BSTree{
	friend class list;
private:
	typedef enum
	{
		EH = 0,
		LH = 1,
		RH = -1
	}bh_t;
	node *root = nullptr;
public:
	node* searchAVL(int key, node *&parent);
	node* leftbalance(node* parentT, node* child);
	node* rightbalance(node* parentT, node* child);
	void insertNode(node *p);
	void deleteNode(int key);
};


class list{
public:
	bool insert(node* p);		//将节点插入表中
	node *find(int tileNum);	//通过块编号找表中是否有此节点，有则返回指针，没有返回Nullptr
	node *getBest();			//获取估值最好（小）的节点
	int getLength();			//获取列表长度
	void reset();				//重置列表
private:
	BSTree bt;
	node *root = nullptr;
	int length = 0;
	void insertTile();
};


class AStarSearcher
{
public:
	AStarSearcher(int w, int h);
	~AStarSearcher();
	void search(int *map, int sx, int sy, int ex, int ey);
	int getTile(int x, int y);
	void getXY(int tile, int &x, int &y);
	bool getNextStep(int &x, int &y);
	void getFirstStep(int &x, int &y);
	int getStepNum();
	int getW(){ return w; }
	int getH(){ return h; }
private:
	int w = 0;
	int h = 0;
	node *lastNode = nullptr;
	int heuristic(int x, int y, int ex, int ey);
	void GenerateSucc(int *map, node *bestNode, int x, int y, int ex, int ey);
	list OPEN, CLOSE;
};


class renderer{
public:
	renderer(int w, int h, int bpp = 32, int scale = 1);
	~renderer();
	bool handleEvents();
	void render(int *map, size_t w, size_t h);
	void getMouse(Uint16 &x, Uint16 &y);
private:
	SDL_Surface *screen;
	int screenW;
	int screenH;
	int scale = 1;
	int bpp;
	Uint8 *keys;
	SDL_Event event;
	Uint16 mouseX = 0;
	Uint16 mouseY = 0;
};

class memMgr{
public:
	memMgr();
	~memMgr();
	int allocateMem(int size);
	void releaseMem(int buffer);
	int getValue(int buffer, int pos);
	void setValue(int buffer, int pos, int value);
	int* getBuffer(int buffer);
	int registBuffer(int *buffer);
private:
	int *memlist[100];
	int freePosList[100];
	int ptrFreePosList = 99;
};

class mazeGameState{
public:
	mazeGameState(int difficulty, int scale, int initDistance, int blkSz);
	~mazeGameState();

    void getRealBufferPtrs(int *&imageBuffer);
	float move(int action);
    void nextMap();
	void getImage();
    float getReward();
    void setStartEndDistance(int distance);

private:

	void reset();
    void calcuReward();

private:
	int *map;
	float *rewardMat;
	int *renderBuffer;

	int sx = 0, sy = 0, ex = 0, ey = 0;
	int difficulty = 0;
	int scale = 0;
    int startEndDistance = 0;
    int blockSz = 0;
    int size = 0;
};

extern "C"{
	void initRenderer(int w, int h, int bpp, int scale);
	void render(int map, int w, int h);
	int rgb(int r, int g, int b);
	bool handleEvents();

	int createIntBuffer(int size);
	void destroyIntBuffer(int buffer);

    void initGame(int difficulty, int scale);
    float move(int action);
    void nextMap();
    void setStartEndDistance(int distance);

	int getValue(int buffer, int i);
	void setValue(int buffer, int i, int v);
}
