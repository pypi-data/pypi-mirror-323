#include "stdafx.h"
#include "nest/nfp.h"
// temp

int main(int argc, char **argv)
{

	/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	// code
	/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

	auto start = std::chrono::high_resolution_clock::now();

	std::vector<std::vector<std::vector<glm::vec3>>> pattern_glm;
	std::vector<std::vector<std::vector<glm::vec3>>> path_glm;
	std::vector<std::vector<std::vector<glm::vec3>>> nfp_glm;
	std::vector<std::vector<std::vector<glm::vec3>>> results;

	nest::nfps(pattern_glm, path_glm, nfp_glm, results);

	auto stop = std::chrono::high_resolution_clock::now();
	auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(stop - start);
	std::cout << "Time taken by function: " << duration.count() << " ms" << std::endl;

	return 0;
}
