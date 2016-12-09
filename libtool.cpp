#include "libtool.h"

#pragma comment(lib, "sdl.lib")
#pragma comment(lib, "sdl_draw.lib")
#pragma comment(lib, "sdl_gfx.lib")


void mazeGenerator::generateMaze(int *map, bool *path, int w, int h){

		int startX = 1;
		int startY = 1;

		srand(time(NULL));

		int *tempWall = new int[w * h];
		int tempWallNum = 0;

		for (int i = 0; i < w * h; ++i){
			// ���ȵ�ͼȫ����ʼ��Ϊǽ
			map[i] = -1;
		}

		if (startX > 1) tempWall[tempWallNum++] = startX - 1 + startY * w;
		if (startX + 1 < w - 2) tempWall[tempWallNum++] = startX + 1 + startY * w;
		if (startY > 1) tempWall[tempWallNum++] = startX + (startY - 1) * w;
		if (startY + 1 < h - 2) tempWall[tempWallNum++] = startX + (startY + 1) * w;

		map[startX + startY * w] = 1;

		while (tempWallNum > 0){
			// ��ѡһ��ǽA

			int m = rand() % tempWallNum;
			int k = tempWall[m];
			tempWall[m] = tempWall[tempWallNum - 1];
			tempWall[tempWallNum - 1] = k;

			int x = tempWall[tempWallNum - 1] % w;
			int y = tempWall[tempWallNum - 1] / w;

			--tempWallNum;

			int choose[] = { 1, 2, 3, 4 };	// ��һ��ѡ��

			for (int i = 0; i < 5; ++i){
				// �������choose
				int m = rand() % 4;
				int n = rand() % 4;
				int k = choose[n];
				choose[n] = choose[m];
				choose[m] = k;
			}

			bool chosen = false;
			bool isWall = false;
			int newX = 0, newY = 0;

			for (int i = 0; i < 4 && !chosen; ++i){
				// ����Χ��һ����ͨ·�Ŀ�B
				switch (choose[i])
				{
				case 1:		// ��
					if (y > 1 && map[x + (y - 1) * w] > 0){
						if (map[x + (y + 1) * w] < 0) isWall = true;
						map[x + (y + 1) * w] = 1;
						newX = x;
						newY = y + 1;
						chosen = true;
					}
					break;
				case 2:		// ��
					if (y + 1 < h - 1 && map[x + (y + 1) * w] > 0){
						if (map[x + (y - 1) * w] < 0) isWall = true;
						map[x + (y - 1) * w] = 1;
						newX = x;
						newY = y - 1;
						chosen = true;
					}
					break;
				case 3:		// ��
					if (x > 1 && map[x - 1 + y * w] > 0){
						if (map[x + 1 + y * w] < 0) isWall = true;
						map[x + 1 + y * w] = 1;
						newX = x + 1;
						newY = y;
						chosen = true;
					}
					break;
				case 4:		// ��
					if (x + 1 < w - 1 && map[x + 1 + y * w] > 0){
						if (map[x - 1 + y * w] < 0) isWall = true;
						map[x - 1 + y * w] = 1;
						newX = x - 1;
						newY = y;
						chosen = true;
					}
					break;
				default:
					break;
				}
			}

			if (isWall){
				map[x + y * w] = 1;
				if (newX > 1 && map[newX - 1 + newY * w] < 0) tempWall[tempWallNum++] = newX - 1 + newY * w;
				if (newX + 1 < w - 2 && map[newX + 1 + newY * w] < 0) tempWall[tempWallNum++] = newX + 1 + newY * w;
				if (newY > 1 && map[newX + (newY - 1) * w] < 0) tempWall[tempWallNum++] = newX + (newY - 1) * w;
				if (newY + 1 < h - 2 && map[newX + (newY + 1) * w] < 0) tempWall[tempWallNum++] = newX + (newY + 1) * w;
			}
		}
	}

node::_node(){
	for (size_t i = 0; i < 8; ++i){
		children[i] = nullptr;
	}
}

bool list::insert(node* p){
	if (p){
		p->next = root;
		root = p;
		length++;
		bt.insertNode(p);
		return true;
	}
	return false;
}

node *list::find(int tileNum){
	node *p;
	return bt.searchAVL(tileNum, p);
}

node *list::getBest(){
	node *p = root;
	node *best = root;
	node *bestPre = nullptr;
	while (p->next){
		if (p->next->fValue < best->fValue) {
			best = p->next;
			bestPre = p;
		}
		p = p->next;

	}

	if (best == root){
		//��һ�����
		root = root->next;
	}
	else{
		bestPre->next = best->next;
	}
	length--;
	bt.deleteNode(best->tileNum);
	return best;
}

int list::getLength(){
	return length;
}

void list::reset(){
	if (length){
		node *p = root;
		node *q = root->next;
		delete p;
		while (q){
			p = q;
			q = q->next;
			delete p;
		}
	}
	root = nullptr;
	length = 0;
	bt.root = nullptr;
}


//===============================

node* BSTree::searchAVL(int tileNum, node *&parent){
	node *p = nullptr;
	parent = root->parentT;
	p = root;
	while (p){
		if (p->tileNum == tileNum) return p;

		parent = p;
		if (p->tileNum > tileNum)
			p = p->lchild;
		else
			p = p->rchild;
	}
	return nullptr;
}

node* BSTree::leftbalance(node* parentT, node* child){
	node *cur;
	if (child->bf == RH){
		cur = child->rchild;
		cur->parentT = parentT->parentT;
		child->rchild = cur->lchild;
		if (cur->lchild != nullptr){
			cur->lchild->parentT = child;
		}
		parentT->lchild = cur->rchild;
		if (cur->rchild != nullptr){
			cur->rchild->parentT = parentT;
		}
		cur->lchild = child;
		cur->rchild = parentT;
		child->parentT = cur;

		if (parentT->parentT != nullptr){
			if (parentT->parentT->lchild == parentT){
				parentT->parentT->lchild = cur;
			}
			else{
				parentT->parentT->rchild = cur;
			}
		}
		else{
			root = cur;
		}
		parentT->parentT = cur;
		if (cur->bf == EH){
			parentT->bf = EH;
			child->bf = EH;
		}
		else if (cur->bf == RH){
			parentT->bf = EH;
			child->bf = LH;
		}
		else{
			parentT->bf = RH;
			child->bf = EH;
		}
		cur->bf = EH;
	}
	else{
		child->parentT = parentT->parentT;
		parentT->lchild = child->rchild;
		if (child->rchild != nullptr)
		{
			child->rchild->parentT = parentT;
		}
		child->rchild = parentT;
		if (parentT->parentT != nullptr){
			if (parentT->parentT->lchild == parentT){
				parentT->parentT->lchild = child;
			}
			else{
				parentT->parentT->rchild = child;
			}
		}
		else{
			root = child;
		}
		parentT->parentT = child;

		if (child->bf == LH){
			child->bf = EH;
			parentT->bf = EH;
		}
		else{
			child->bf = RH;
			parentT->bf = LH;
		}
	}
	return root;
}

node* BSTree::rightbalance(node* parentT, node* child){
	node *cur;
	if (child->bf == LH){
		cur = child->lchild;
		cur->parentT = parentT->parentT;
		child->lchild = cur->rchild;
		if (cur->rchild != nullptr){
			cur->rchild->parentT = child;
		}
		parentT->rchild = cur->lchild;
		if (cur->lchild != nullptr){
			cur->lchild->parentT = parentT;
		}
		cur->lchild = parentT;
		cur->rchild = child;
		child->parentT = cur;
		if (parentT->parentT != nullptr){
			if (parentT->parentT->lchild == parentT){
				parentT->parentT->lchild = cur;
			}
			else{
				parentT->parentT->rchild = cur;
			}
		}
		else{
			root = cur;
		}
		parentT->parentT = cur;
		if (cur->bf == EH){
			parentT->bf = EH;
			child->bf = EH;
		}
		else if (cur->bf == LH){
			parentT->bf = EH;
			child->bf = RH;
		}
		else{
			parentT->bf = LH;
			child->bf = EH;
		}
		cur->bf = EH;
	}
	else{
		child->parentT = parentT->parentT;
		parentT->rchild = child->lchild;
		if (child->lchild != nullptr)
			child->lchild->parentT = parentT;
		child->lchild = parentT;
		if (parentT->parentT != nullptr){
			if (parentT->parentT->lchild == parentT){
				parentT->parentT->lchild = child;
			}
			else{
				parentT->parentT->rchild = child;
			}
		}
		else{
			root = child;
		}
		parentT->parentT = child;
		if (child->bf == RH){
			child->bf = EH;
			parentT->bf = EH;
		}
		else{
			child->bf = LH;
			parentT->bf = RH;
		}
	}
	return root;
}

void BSTree::insertNode(node *p){
	if (!root && p){
		root = p;
		return;
	}

	if (p->bAdded){
		p->bInTree = true;
		return;
	}

	p->bInTree = true;
	p->bAdded = true;

	node *parent = nullptr, *child = nullptr;
	searchAVL(p->tileNum, parent);
	p->parentT = parent;

	if (p->tileNum < parent->tileNum){
		parent->lchild = p;
		child = parent->lchild;
	}
	else{
		parent->rchild = p;
		child = parent->rchild;
	}

	while (parent != nullptr){
		if (child == parent->lchild){
			if (parent->bf == RH){
				parent->bf = EH;
				return;
			}
			else if (parent->bf == EH){
				leftbalance(parent, child);
				break;
			}
			else{
				parent->bf = LH;
				child = parent;
				parent = parent->parentT;
			}
		}
		else{
			if (parent->bf == LH){
				//���Һ��ӣ���������ƽ��
				parent->bf = EH;
				return;
			}
			else if (parent->bf == RH){
				//���Һ��ӣ���������parent�Ĳ�ƽ��
				rightbalance(parent, child);
				break;
			}
			else{
				//���Һ��ӣ����ҿ�������parent��parent�Ĳ�ƽ��
				parent->bf = RH;
				child = parent;
				parent = parent->parentT;
			}
		}
	}
	return;
}

void BSTree::deleteNode(int tileNum)
{
	node *q;
	node *p = searchAVL(tileNum, q);
	if (p){
		p->bInTree = false;
	}
}


//==============================

AStarSearcher::AStarSearcher(int pw, int ph){
	w = pw;
	h = ph;
}

int AStarSearcher::getTile(int x, int y){
	return y * w + x;
}

void AStarSearcher::getXY(int tile, int &x, int &y){}

void AStarSearcher::search(int *map, int sx, int sy, int ex, int ey){
	OPEN.reset();
	CLOSE.reset();
	lastNode = nullptr;
	node *startNode = new node;						//��ʼ�ڵ㣨��㣩
	startNode->parent = nullptr;					//��ʼ�ڵ���ǰ��
	startNode->tileNum = getTile(sx, sy);			//�ڽڵ��д�����
	startNode->x = sx, startNode->y = sy;			//�ӿ�Ż�ȡXY���겢����ڵ�
	startNode->gPast = 0;							//�Ѿ��߹��ļ������ʵ�ʼ�ֵ
	startNode->hEst = heuristic(sx, sy, ex, ey);	//������ʽ�������������Ԥ�Ƽ�ֵ
	startNode->fValue = startNode->gPast + startNode->hEst;		//�ܼ�ֵ
	OPEN.insert(startNode);		//����OPEN����

	while (OPEN.getLength() > 0)
	{
		node *bestNode = OPEN.getBest();
		CLOSE.insert(bestNode);
		if (bestNode->x == ex && bestNode->y == ey){
			lastNode = bestNode;
			return;		//������
		}
		GenerateSucc(map, bestNode, bestNode->x, bestNode->y - 1, ex, ey);			//�����Ͻڵ�
		//GenerateSucc(map, bestNode, bestNode->x + 1, bestNode->y - 1, ex, ey);		//�������Ͻڵ�
		GenerateSucc(map, bestNode, bestNode->x + 1, bestNode->y, ex, ey);			//�����ҽڵ�
		//GenerateSucc(map, bestNode, bestNode->x + 1, bestNode->y + 1, ex, ey);		//�������½ڵ�
		GenerateSucc(map, bestNode, bestNode->x, bestNode->y + 1, ex, ey);			//�����½ڵ�
		//GenerateSucc(map, bestNode, bestNode->x - 1, bestNode->y + 1, ex, ey);		//�������½ڵ�
		GenerateSucc(map, bestNode, bestNode->x - 1, bestNode->y, ex, ey);			//������ڵ�
		//GenerateSucc(map, bestNode, bestNode->x - 1, bestNode->y - 1, ex, ey);		//�������Ͻڵ�
	}
	return;
}

void AStarSearcher::GenerateSucc(int *map, node *bestNode, int x, int y, int ex, int ey){
	if (x < 0 || x >= w || y < 0 || y >= h || map[getTile(x, y)] < 0) return;	//�ⲻ��ͨ·
	node *oldNode = nullptr;
	int i;
	if ((oldNode = OPEN.find(getTile(x, y))) != nullptr){
		//��OPEN�����ҵ�������ڵ�,˵�����µ�·,��ô������ҵ�������·���̣��Ƚ�gPast��С����ô�µ�·���ţ�
		for (i = 0; i < 4; ++i)
		if (bestNode->children[i] == nullptr)
			break;
		bestNode->children[i] = oldNode;

		if (oldNode->gPast > bestNode->gPast + map[getTile(x, y)]){
			oldNode->gPast = bestNode->gPast + map[getTile(x, y)];
			oldNode->fValue = oldNode->gPast + oldNode->hEst;
			oldNode->parent = bestNode;
		}

	}
	else if ((oldNode = CLOSE.find(getTile(x, y))) != nullptr){
		//��CLOSE�����ҵ�������ڵ㣬������
		return;
	}
	else
	{
		//����OPEN��CLOSE�����棬�����������ɽڵ�
		node *newNode = new node;
		newNode->parent = bestNode;
		newNode->gPast = bestNode->gPast + map[getTile(x, y)];
		newNode->hEst = heuristic(x, y, ex, ey);
		newNode->fValue = newNode->gPast + newNode->hEst;
		newNode->x = x;
		newNode->y = y;
		newNode->tileNum = getTile(x, y);

		OPEN.insert(newNode);
		for (i = 0; i < 4; ++i)
		if (bestNode->children[i] == nullptr)
			break;
		bestNode->children[i] = newNode;
	}
}

int AStarSearcher::heuristic(int x, int y, int ex, int ey){
	return abs(ex - x) + abs(ey - y);
}

//int AStarSearcher::heuristic(int x, int y, int ex, int ey){
//	return sqrt((ex - x) * (ex - x) + (ey - y) * (ey - y));
//}

AStarSearcher::~AStarSearcher(){
	OPEN.reset();
	CLOSE.reset();
}

int AStarSearcher::getStepNum(){
	if (!lastNode) {
		return 0;
	}
	return lastNode->gPast;
}

bool AStarSearcher::getNextStep(int &x, int &y){
	if (!lastNode) {
		x = -1, y = -1;
		return false;
	}
	x = lastNode->x;
	y = lastNode->y;
	lastNode = lastNode->parent;
	if (lastNode)
		return true;
	else
		return false;
}

void AStarSearcher::getFirstStep(int &x, int &y){
	if (!lastNode) {
		x = -1, y = -1;
		return;
	}

	while (lastNode->parent && lastNode->parent->parent){
		lastNode = lastNode->parent;
	}

	x = lastNode->x;
	y = lastNode->y;
}


//===============================


renderer::renderer(int w, int h, int bpp, int scale) :screenW(w), screenH(h), bpp(bpp), scale(scale) {
	SDL_Init(SDL_INIT_EVERYTHING);
	screen = SDL_SetVideoMode(w, h, 32, SDL_ASYNCBLIT | SDL_HWSURFACE);
	if (!screen){
		throw("error while init sdl");
	}
}


renderer::~renderer(){
	SDL_FreeSurface(screen);
	screen = nullptr;
}


bool renderer::handleEvents(){
	while (SDL_PollEvent(&event)) {
		keys = SDL_GetKeyState(NULL);
		switch (event.type) {
		case SDL_MOUSEMOTION:
			mouseX = event.button.x;
			mouseY = event.button.y;
			break;
		case SDL_QUIT:
			return false;
			break;
		}
	}
	return true;
}


void renderer::render(int *map, size_t w, size_t h){
	float *rmap = (float *)map;
	Draw_FillRect(screen, 0, 0, screen->w, screen->h, 0xffffff);
	float tmp;
	for (size_t y = 0; y < h; ++y){
		for (size_t x = 0; x < w; ++x){
			tmp = rmap[x + y * w];
			if(tmp == 0.5f){
				Draw_FillRect(screen, x * scale, y * scale, scale, scale, RGB(fabs(tmp) * 255,0,0));
			}else if(tmp == 1.0f){
				Draw_FillRect(screen, x * scale, y * scale, scale, scale, RGB(0,fabs(tmp) * 255,0));
			}else{
				Draw_FillRect(screen, x * scale, y * scale, scale, scale, RGB(0,0,fabs(tmp) * 255));
			}	
		}
	}
	SDL_Flip(screen);
}


void renderer::getMouse(Uint16 &x, Uint16 &y){
	x = mouseX / scale;
	y = mouseY / scale;
}


//==============================


memMgr::memMgr(){
	for(int i = 0; i < 100; ++i){
		freePosList[i] = 99 - i;
		memlist[i] = nullptr;
	}
}

memMgr::~memMgr(){
	for(int i = ptrFreePosList + 1; i < 100; ++i){
		delete [](memlist[freePosList[i]]);
	}
}

int memMgr::allocateMem(int size){
	if(ptrFreePosList == 0) return 0;
	int *ptr = new int[size];
	memlist[freePosList[ptrFreePosList]] = ptr;
	return freePosList[ptrFreePosList--];
}

void memMgr::releaseMem(int buffer){
	delete []memlist[buffer];
	freePosList[++ptrFreePosList] = buffer;
}

float memMgr::getValue(int buffer, int pos){
	float *ptr = (float *)memlist[buffer];
	return ptr[pos];
}

void memMgr::setValue(int buffer, int pos, int value){
	memlist[buffer][pos] = value;
}

int* memMgr::getBuffer(int buffer){
	return memlist[buffer];
}

int memMgr::registBuffer(int *buffer){
	if(ptrFreePosList == 0) return 0;
	memlist[freePosList[ptrFreePosList]] = buffer;
	return freePosList[ptrFreePosList--];
}

//==============================

mazeGameState::mazeGameState(int difficulty, int scale, int initDistance, int blkSz):
		difficulty(difficulty), scale(scale), startEndDistance(initDistance), blockSz(blkSz){
	size = difficulty * scale;
	map = new int[size * size];
	rewardMat = new float[size * size];
	renderBuffer = new float[size * size];

	nextMap();
	reset();
}

mazeGameState::~mazeGameState(){
	delete []map;
	delete []rewardMat;
	//delete []renderBuffer;
}

void mazeGameState::getRealBufferPtrs(int *&imageBuffer){
    imageBuffer = (int *)renderBuffer;
}

void mazeGameState::getImage(){
	for (int y = 0; y < size; ++y){
		for (int x = 0; x < size; ++x){
			renderBuffer[x + y * size] = map[x + y * size] == -1 ? -1.0f : 0;
		}
	}
	
    for (int y = -blockSz; y <= blockSz; ++y){
        for (int x = -blockSz; x <= blockSz; ++x) {
            renderBuffer[sx + x + (sy + y) * size] = 0.5f;
            renderBuffer[ex + x + (ey + y) * size] = 1.0f;
        }
    }
}

void mazeGameState::nextMap(){
	int *mapMaze = new int[difficulty * difficulty];
	
	mazeGenerator::generateMaze(mapMaze, nullptr, difficulty, difficulty);

	for (int y = 0; y < size; ++y){
		for (int x = 0; x < size; ++x){
			map[x + y * size] = mapMaze[(x / scale) + (y / scale) * difficulty];
		}
	}

	reset();
	getImage();

	delete []mapMaze;

}

float distance(int x1, int y1, int x2, int y2){
	float dis = sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2));
	return dis;
}

void mazeGameState::setStartEndDistance(int distance){
    startEndDistance = distance;
}

void mazeGameState::calcuReward(){
	float up_distance, down_distance, left_distance, right_distance;
	float tmp_x, tmp_y;
	up_distance = distance(ex, ey, ex, 0);
	down_distance = distance(ex, ey, ex, size);
	left_distance = distance(ex, ey, 0, ey);
	right_distance = distance(ex, ey, size, ey);

	tmp_x = up_distance > down_distance ? 0 : size;
	tmp_y = left_distance > right_distance ? 0 : size;

	float maxDistance = distance(ex, ey, tmp_x, tmp_y);

	for (int y = 0; y < size; ++y){
		for (int x = 0; x < size; ++x){
			rewardMat[x + y * size] = (-distance(ex, ey, x, y) / maxDistance) / 10.0f;
		}
	}

	rewardMat[ex + ey * size] = 0;
}

float mazeGameState::move(int action){
    sx += action == 2 ? 1 : action == 3 ? -1 : 0;
    sy += action == 0 ? 1 : action == 1 ? -1 : 0;


    if(map[sx + sy * size] == -1){
        reset();
        return -10.0f;
    }
    else if(sx == ex && sy == ey){
    	reset();
    	return 0.0f;
    }
    else{
		getImage();
        return rewardMat[sx + sy * size];
    }
}

void mazeGameState::reset(){
	sx = sy = ex = ey = -1;

	while(sx == -1 || sy == -1 || map[sx + sy * size] == -1){
		sx = rand() % (size - 2 * blockSz) + blockSz;
		sy = rand() % (size - 2 * blockSz) + blockSz;
	}

	while(ex == -1 || ey == -1 || map[ex + ey * size] == -1){
		ex = sx + rand() % (2 * startEndDistance) - startEndDistance;
		ey = sy + rand() % (2 * startEndDistance) - startEndDistance;
	}
	calcuReward();
}


//==============================

renderer *mapRenderer = nullptr;
mazeGameState *gameState = nullptr;
memMgr memMan;

int *bufferList[100];
int *freeList[100];
int bufferNum = 0;


int RGB(int r, int g, int b){
	return ((r & 0xff) << 16) | ((g & 0xff) << 8) | (b & 0xff);
}

void initRenderer(int w, int h, int bpp, int scale){
	if(mapRenderer) delete mapRenderer;
	mapRenderer = new renderer(w, h, bpp, scale);
}

int initGame(int difficulty, int scale, int initDistance, int blkSz){
    if(gameState) delete gameState;
    gameState = new mazeGameState(difficulty, scale, initDistance, blkSz);
    int* buffer = nullptr;
    gameState->getRealBufferPtrs(buffer);
    return memMan.registBuffer(buffer);
}

float move(int action){
    return gameState->move(action);
}

void nextMap(){
    gameState->nextMap();
}

void setStartEndDistance(int distance){
    gameState->setStartEndDistance(distance);

}

bool handleEvents(){
	if(mapRenderer) 
		return mapRenderer->handleEvents();
	return false;
}

void render(int map, int w, int h){
	if(mapRenderer)
		mapRenderer->render(memMan.getBuffer(map), w, h);
}

int createIntBuffer(int size){
	return memMan.allocateMem(size);
}

void destroyIntBuffer(int buffer){
	memMan.releaseMem(buffer);
}

int getValue(int buffer, int i){
	return memMan.getValue(buffer, i);
}

void setValue(int buffer, int i, int v){
	memMan.setValue(buffer, i, v);
}
