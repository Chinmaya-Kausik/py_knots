Implementing various link algorithms in Python, starting with obtaining standard and generalized Seifert Matrices from the braid description of a colored link.

# Instructions for Windows users

Download and run clasper_2_3.exe from the top folder.

# Instructions for other users

Clone/download this repository and run the python program clasper.py.

# Note for developers

If you want to work with the source code, please note the following: The initial implementation was written with a convention for braid notation opposite to that of LinkInfo and Julia Collins. That is, the braid that LinkInfo calls {1, 1, 1} is {-1, -1, -1} in our initial convention. All of the code in the modules sgraph and braid (and some code in other modules) is written with that convention. 

To later align with them, I renamed the initializing instance variable for the class Braid (and the subclass ColBraid) to "braid_wrong," and defined a cached property "self.braid," which contains the negation of the braid notation in braid_wrong. We pass "self.braid" to all future functions. The reason for this was that actually changing all the signs appropriately in the implementation has the risk of introducing several errors, while it is much easier to just "flip the input." Contact me if you're confused/want more details.
