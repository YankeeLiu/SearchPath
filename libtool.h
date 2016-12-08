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
	_node *next = nullptr;		//������һ��������ڵ���Open����Close���У�
	_node *lchild = nullptr;
	_node *rchild = nullptr;
	_node *parentT = nullptr;	//ʹ��BT�洢Tile
	short bf = 0;
	bool bInTree = false;
	bool bAdded = false;
public:
	int gPast;					//ʵ���Ѿ����˵ľ���
	int hEst;					//����ʽ�������Ƴ��ļ�ֵ
	int fValue;					//��ֵ�ܼ�
	int x, y;					//�ڵ��ͼ����
	int tileNum;				//Ψһ���ţ�x * ������ + y��
	_node *children[8];			//ָ���ĸ����ӵ�����
	_node *parent = nullptr;	//���ڵ�
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
	bool insert(node* p);		//���ڵ�������
	node *find(int tileNum);	//ͨ�������ұ����Ƿ��д˽ڵ㣬���򷵻�ָ�룬û�з���Nullptr
	node *getBest();			//��ȡ��ֵ��ã�С���Ľڵ�
	int getLength();			//��ȡ�б���
	void reset();				//�����б�
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
