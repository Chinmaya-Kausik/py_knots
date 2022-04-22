Implementing various link algorithms in Python, starting with obtaining standard and generalized Seifert Matrices from the braid description of a colored link.

# Instructions for Windows users

Download and run clasper_2_4.exe from the top folder.

# Instructions for other users

Clone/download this repository and run the python program clasper.py.

# Note for mathematicians (and advanced students)

If you have a project where you want to do more than what the program allows, please contact me at chinmaya.kausik.1@gmail.com. For example, if you want to run batch computations with large braids to search for counterexamples to something, or if you want to use Seifert matrices for a purpose other than the ones the program deals with, I can guide you through the code and provide suggestions (if you need them). I am open to talking about various ways in which you can use the program's code. If I have time, I can also write some of the code for you, but I cannot promise anything in that direction. 

Also note that the program will be significantly faster for long braids once I implement the bottleneck function in a much faster language (specifically, C) and import it to this program, which is written in Python. 

# Note for developers

1. **Speed:** Currently, the algorithm uses the O(n^5) algorithm for Bareiss determinants to compute the symbolic determinant of the presentation matrix. The bottleneck seems to be polynomial arithmetic (specifically, polynomial multiplication and division), for which the next step would be to implement the Bareiss determinant in C using the FLINT library for polynomial arithmetic and import the module to Python, probably using ctypes. If you have any other ideas/suggestions for a better way to do this, please email me at chinmaya.kausik.1@gmail.com

2. **Sign Convention:** 
If you want to work with the source code, please note the following: The initial implementation was written with a convention for braid notation opposite to that of LinkInfo and Julia Collins. That is, the braid that LinkInfo calls {1, 1, 1} was {-1, -1, -1} in our initial convention. All of the code in the modules sgraph and braid (and some code in other modules) is written with that convention. To later align with them, I renamed the initializing instance variable for the class Braid (and the subclass ColBraid) to "braid_wrong," and defined a cached property "self.braid," which contains the negation of the braid notation in braid_wrong. We pass "self.braid" to all future functions. The reason for this was that actually changing all the signs appropriately in the implementation has the risk of introducing several errors, while it is much easier to just "flip the input." Contact me if you're confused/want more details.
