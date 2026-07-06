# The forward/backward method for developing algorithms
## Example: Circular linked list

Part three of a series on [technical whiteboarding](/blog/interview_01_whiteboard).

Developing an algorithm for an unknown, novel programming problem can be a daunting task. The forward/backward method is a consistent, repeatable approach that guides a developer towards a correct and robust solution. It begins with brainstorming two or three specific test scenario or situation datasets for the problem

![{[width=50%]} Example circular linked lists](/images/Technical_Whiteboarding_FB_0.png)

This example develops an algorithm to detect whether a linked list has a cycle. A cycle happens when a node links “back” earlier in the list. Here, the programmer has created two linked lists, one with and one without a cycle. Visually it is easy to see the cycle as the arrow that goes back to earlier in the first example, and the absence of such an arrow in the second.

The forward/backward process is a problem solving technique to break a large problem into a series of smaller steps. It begins by working from the bottom up, or backwards. Start by drawing the inputs in the top of the working area, and the output at the bottom. If the inputs and output are containers with a generic data type, prefer to draw them using shapes and colors rather than making up specific words or numbers.

![{[width=75%]} Forward/backward: inputs and outputs](/images/Technical_Whiteboarding_FB_1.png)

The programmer writes the inputs and outputs at the top and bottom, respectively, and labels them A1 forward and B1 backward. The programmer then asks which information led to the values false and true.

After this drawing, the output for a test scenario or situation is at the bottom of the visualization and the input is at the top. Call the output B1 and the input A1. Looking at the output, ask what is the immediate precursor information necessary to find that value. This Key Question drives much of the forward backward process - “What is the immediate piece of information that gives this data?” when working backwards, and “what information becomes immediately available to derive, generate, or fill in?” moving forward.

![{[width=75%]} Forward/backward: B2](/images/Technical_Whiteboarding_FB_2.png)

The first answer is that the arrow “points” backwards. Unfortunately, the “direction” of an arrow is not part of a linked list’s definition. A linked list includes only the “next” pointer, not the relationship to the current node. The programmer notices a key difference: a traversal would encounter the blue node twice in the example on the right. On the left, the traversal completes having encountered each node only once. This answer fills in step B2.

For example, if the output is a boolean value, the immediate precursor operation is a comparison. Draw the two values and show the comparison. Or if the output is a list, notate the change that created the output, and draw the list in its previous state directly preceding B1. This precursor to the output step B1 is step B2. Repeat this process. In the comparison example, where did the two values come from? If it was a change to a data structure, where did the information for the change come from? Draw the source of those values as step B3.

![{[width=75%]} Forward/backward: B3](/images/Technical_Whiteboarding_FB_3.png)

Applying the key question again, the programmer recognizes they used a set to track which nodes they had visited and which they had not. This set structure is B3.

After some number of steps working backwards, an intermediate data structure should become apparent that provides the information needed to work forwards to B1. Now, work forwards from A1 to this intermediate step. Describe how to create the data structure, any loops necessary to convert the input to it, and any additional information that might prove useful. These forward steps are A2, A3, etc.

![{[width=75%]} Forward/backward: A2](/images/Technical_Whiteboarding_FB_4.png)

Having moved backwards to needing a visited set, the programmer asks the forward key question: what information becomes available to fill in? The visited set from step B3 answers this. A traversal storing each list item in the set defines forward step A2.

At this point, a complete logical thread connects all the steps from A1 to B1. A1 is the input. A2 maintains a visited list during traversal. B3 checks the visited list. B2 recognizes or does not recognize a duplicate item. B1 returns immediately when the code encounters a duplicate or when the traversal completes.

When the forward and backward steps line up in the visualization using specific values, it’s time to write a general plain language description of each step. These steps should not be specific to any programming language. They should use “big picture” holistic operations, like “traverse the list”, “compare the values”, or “check the set”. Calling out intermediate data structures by variable name is appropriate, but describing the changes to a loop counter is too detailed for a general algorithm.

![Completed visualization and algorithm](/images/Technical_Whiteboarding_FB_Algorithm.png)

This write up describes the forward and backward steps in an algorithmic way. It doesn’t deal with details of the function name or argument variables, but does call out specific names for the set and the traversal variable for the set. It uses concise If statements, and generic operations on the intermediate data structures.

This approach works best with a good understanding of common data structures, their methods, and algorithms. While any problem may require specific domain knowledge, a developer benefits from knowing how to construct and traverse arrays, linked lists, and binary trees. Knowledge of n-ary child trees and hashmaps provides additional skills. Understanding how stacks, queues, and sets augment traversals for these structures provides a solid foundation.

## Recursive algorithms

A problem may have a very clear recursive solution. When the problem rephrases to “Do the same operation on two parts of the input” or “do the operation on the head, and then repeat”, it might be amenable to recursion. Recursion requires two pieces: the base scenario or situation and the operation.

Identify the base scenario or situation first. In most cases, this is either an empty data structure or a single item. Also identify the recursion on one or more parts of the data structure and any logic necessary to combine those results.

In recursion, the empty scenario or situation becomes critical to identify. This scenario or situation defines the base scenario or situation of the recursion. Also consider the one or two item scenario or situation as potential base cases. Failure to identify the base scenario or situation at this time greatly increases the difficulty in the remainder of the interview.

## References

SOLOW, D. 2014\. Chapter 2, The Forward Backward Method. In How to Read and Do Proofs (Sixth Edition). John Wiley & Sons, Danvers, MA, 9-24