# Forward and backward method
## Example: Circular linked list

Part three of a series on [technical whiteboarding](/blog/interview_01_whiteboard).

Developing an algorithm for an unknown programming problem is hard. The forward/backward method is a reliable approach that helps developers find correct solutions. Start by brainstorming two or three test cases for the problem

![{[width=50%]} Example circular linked lists](/images/Technical_Whiteboarding_FB_0.png)

This example develops an algorithm to detect whether a linked list has a cycle. A cycle happens when a node links “back” earlier in the list. Here, the programmer has created two linked lists, one with and one without a cycle. Visually it is easy to see the cycle as the arrow that goes back to earlier in the first example, and the absence of such an arrow in the second.

The forward/backward process breaks a large problem into smaller steps. Work backwards first. Draw the inputs at the top and the output at the bottom. If the inputs and output are generic types, use shapes and colors instead of picking specific words or numbers.

![{[width=75%]} Forward/backward: inputs and outputs](/images/Technical_Whiteboarding_FB_1.png)

The programmer writes the inputs and outputs at the top and bottom, respectively, and labels them A1 forward and B1 backward. The programmer then asks which information led to the values false and true.

After this drawing, the output for a test scenario or situation is at the bottom of the visualization and the input is at the top. Call the output B1 and the input A1. Looking at the output, ask what information you need to find it. This Key Question drives the forward backward process: “What immediate information leads to this data?” when working backwards, and “What information can we get next?” moving forward.

![{[width=75%]} Forward/backward: B2](/images/Technical_Whiteboarding_FB_2.png)

The first answer is that the arrow “points” backwards. Unfortunately, the “direction” of an arrow is not part of a linked list’s definition. A linked list includes only the “next” pointer, not the relationship to the current node. The programmer notices a key difference: a traversal would encounter the blue node twice in the example on the right. On the left, the traversal completes having encountered each node only once. This answer fills in step B2.

For example, if the output is a boolean value, use a comparison to get it. Draw the two values and show the comparison. If the output is a list, show the change that created it and draw the previous state before B1. This step before B1 is step B2. Repeat this process. In the comparison example, where did the two values come from? If the change was to a data structure, where did that information come from? Draw the source as step B3.

![{[width=75%]} Forward/backward: B3](/images/Technical_Whiteboarding_FB_3.png)

Applying the key question again, the programmer recognizes they used a set to track which nodes they had visited and which they had not. This set structure is B3.

After working backwards several steps, an intermediate data structure should appear that gives the information needed to work forward to B1. Now work forward from A1 to this step. Describe how to create the data structure, any loops needed to convert the input, and any other useful information. These forward steps are A2, A3, etc.

![{[width=75%]} Forward/backward: A2](/images/Technical_Whiteboarding_FB_4.png)

Having moved backwards to needing a visited set, the programmer asks the forward key question: what information becomes available to fill in? The visited set from step B3 answers this. A traversal storing each list item in the set defines forward step A2.

At this point, a complete logical thread connects all the steps from A1 to B1. A1 is the input. A2 maintains a visited list during traversal. B3 checks the visited list. B2 recognizes or does not recognize a duplicate item. B1 returns immediately when the code encounters a duplicate or when the traversal completes.

When the forward and backward steps match in the visualization by using specific values, write a general plain language description of each step. These steps should not be specific to any programming language. Use “big picture” operations like “traverse the list”, “compare the values”, or “check the set”. Name the intermediate data structures, but don’t describe small changes like loop counters, which are too detailed for a general algorithm.

![Completed visualization and algorithm](/images/Technical_Whiteboarding_FB_Algorithm.png)

This write up describes the forward and backward steps in an algorithmic way. It doesn’t deal with details of the function name or argument variables, but does call out specific names for the set and the traversal variable for the set. It uses concise If statements, and generic operations on the intermediate data structures.

This approach works best with a good understanding of common data structures and algorithms. Any problem may need specific knowledge, but developers should know how to use arrays, linked lists, and binary trees. Learn n-ary trees and hashmaps for more skills. Stacks, queues, and sets facilitate traversing structures and provide a solid foundation.

## Recursive algorithms

A problem may have a clear recursive solution. If you can say “Do the same operation on two parts of the input” or “do the operation on the head, then repeat”, try recursion. Recursion needs two pieces: the base scenario and the operation.

Identify the base scenario first. In most cases, this is an empty data structure or a single item. Also identify the recursion on one or more parts of the data structure and the logic needed to combine the results.

In recursion, the empty scenario is critical to identify. This scenario defines the base scenario of the recursion. Also think about the one or two item scenario as potential base scenarios. If you miss the base scenario now, the interview becomes much harder later.

## References

SOLOW, D. 2014\. Chapter 2, The Forward Backward Method. In How to Read and Do Proofs (Sixth Edition). John Wiley & Sons, Danvers, MA, 9-24