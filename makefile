libtools.so:
	g++ libtool.cpp -O2 -shared -o libtool.so -lSDL -fPIC -std=c++11

clean:
	rm libtool.so
