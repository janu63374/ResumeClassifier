
import networkx as nx

from backend.app.services.skill_extractor import extract_skills


# Predefined relationships between technical skills
SKILL_RELATIONSHIPS = [
    ("Python", "Django"),
    ("Python", "Flask"),
    ("Python", "FastAPI"),
    ("Python", "Pandas"),
    ("Python", "NumPy"),
    ("JavaScript", "React"),
    ("JavaScript", "Node.js"),
    ("JavaScript", "HTML"),
    ("JavaScript", "CSS"),
    ("HTML", "CSS"),
    ("SQL", "MySQL"),
    ("SQL", "PostgreSQL"),
    ("Git", "GitHub"),
    ("Java", "Spring"),
]


def generate_skill_graph(resume_text):

    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text is required.")

    extracted_skills = extract_skills(resume_text)

    # Extract skill names
    skill_names = {
        item["skill"].strip().lower(): item["skill"].strip()
        for item in extracted_skills
        if isinstance(item, dict) and item.get("skill")
    }

    graph = nx.Graph()

    # Add detected skills as graph nodes
    for skill in skill_names.values():
        graph.add_node(skill)

    # Add relationships when both skills exist in the resume
    for skill_a, skill_b in SKILL_RELATIONSHIPS:

        key_a = skill_a.lower()
        key_b = skill_b.lower()

        if key_a in skill_names and key_b in skill_names:
            graph.add_edge(
                skill_names[key_a],
                skill_names[key_b],
                relationship="related"
            )

    nodes = [
        {
            "skill": node,
            "connections": graph.degree(node)
        }
        for node in graph.nodes()
    ]

    edges = [
        {
            "source": source,
            "target": target,
            "relationship": data["relationship"]
        }
        for source, target, data in graph.edges(data=True)
    ]

    return {
        "total_skills": graph.number_of_nodes(),
        "total_relationships": graph.number_of_edges(),
        "nodes": nodes,
        "edges": edges,
        "message": "Skill relationship graph generated successfully."
    }
