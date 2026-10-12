# Labelled checker fixtures

Every document here is hand-authored synthetic test data. None is a model output.
The source files are deliberately small so a reader can inspect the expected result.
`manifest.json` lists each input pair and the planted issue code and item ID.

The benchmark matches each expected pair against actual checker findings as a
multiset. An unrelated warning cannot count as a caught defect. Unexpected findings
and missed defects are reported separately. A document with an empty expected list
is a good control. All benchmark defects are structural and within checker scope.

The unit tests also show important limits: a real quote can support a wrong claim,
two differently worded findings can describe the same issue, and an ID link can
connect a requirement to an irrelevant test. Those cases need a person.

