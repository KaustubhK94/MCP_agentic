flowchart LR

A[User Query]
--> B[FunctionAgent]

B
--> C[MCP Client]

C
--> D[MCP Server]

D
--> E[Tool]

E
--> D
--> C
--> B

B
--> F[Travel State]

F
--> G[LLM Response]



flowchart TD

Bug
-->
Observe

Observe
-->
PrintObject

PrintObject
-->
Type

Type
-->
Vars

Vars
-->
Hierarchy

Hierarchy
-->
Payload

Payload
-->
Fix