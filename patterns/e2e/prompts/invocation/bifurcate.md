You are debugging a production defect. Two live hypotheses remain: (1) the Job
Runner returns the wrong status, or (2) the Web Server mis-records the runner
that accepted the job. Show bifurcation in order:

1. Name both hypotheses explicitly.
2. Design one discriminating probe (direct API call, isolated test, or similar)
   and state **before running** what each outcome would imply — which hypotheses
   a pass refutes, and which a fail refutes.
3. State the observed outcome and which partition it refutes.
4. Bifurcate again on the surviving partition (smaller hypothesis set or next
   checkpoint) until one cause is isolated.

Keep the example concrete but abbreviated. Include at least one small test or
probe snippet.
