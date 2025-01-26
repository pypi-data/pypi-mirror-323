from dataclasses     import dataclass

RENDER__MERMAID__SAMPLE_GRAPH_1 = """\
graph TD
    Start --> Decision{Is it a weekday?}
    Decision -->|Yes| Work
    Decision -->|No| Relax
    Work --> Lunch
    Relax --> Lunch
    Lunch --> End
"""

@dataclass
class Model__Render__Mermaid:
    mermaid_code     : str  = RENDER__MERMAID__SAMPLE_GRAPH_1
