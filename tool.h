extern "C"{
	void initRenderer(int w, int h, int bpp, int scale);
	void render(int* map, int w, int h);
	int rgb(int r, int g, int b);
	bool handleEvents();

	int* createIntBuffer(int size);
	void destroyIntBuffer(int* buffer);
	
	void getRandomMaze(int* mapMazeRendered, int size, int scale);
	int getBestStep(int *map, int sx, int sy, int ex, int ey, int w, int h);
}
