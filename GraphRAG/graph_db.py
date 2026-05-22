"""will handle all communication with Neo4j database, including creating nodes, relationships, and querying the graph."""

from neo4j import GraphDatabase, basic_auth
from dotenv import load_dotenv
import os

load_dotenv()

import os
from neo4j import GraphDatabase

# ----------------------------------------------------------------------
# Neo4j Connection Configuration
# ----------------------------------------------------------------------

URI = os.environ["NEO4J_URI"]

AUTH = (
    os.environ["NEO4J_USERNAME"],
    os.environ["NEO4J_PASSWORD"],
)


# ----------------------------------------------------------------------
# Driver Management
# ----------------------------------------------------------------------


def get_driver():
    """
    Create and return a Neo4j driver instance.

    The driver manages a connection pool and is safe to reuse.
    """

    driver = GraphDatabase.driver(URI, auth=AUTH)

    # Verify connection immediately
    driver.verify_connectivity()

    return driver


"""  verify_connectivity() will attempt to connect to the Neo4j 
database using the provided URI and authentication credentials. 
If the connection is successful, it will return without error. 
If there is an issue with the connection (e.g., wrong credentials, 
database not running), it will raise an exception immediately, 
allowing you to catch and handle connection issues early in the 
application lifecycle. """


# ----------------------------------------------------------------------
# Graph Cleanup
# ----------------------------------------------------------------------


def clear_graph(driver):
    """
    Delete all nodes and relationships from Neo4j.

    Useful before re-ingesting documents.
    """

    with driver.session() as session:

        session.run("MATCH (n) DETACH DELETE n")

    print("🗑️ Graph cleared")


# ----------------------------------------------------------------------
# Entity Node Creation
# ----------------------------------------------------------------------


def create_entity_node(driver, entity: dict):
    """
    Create or update an entity node.

    Uses MERGE instead of CREATE to avoid duplicates.
    """

    with driver.session() as session:

        session.run(
            """
            MERGE (n:Entity {name: $name})
            SET
                n.type = $type,
                n.entity_id = $entity_id
            """,
            name=entity["name"],
            type=entity.get("type", "Unknown"),
            entity_id=entity.get("id", ""),
        )


# ----------------------------------------------------------------------
# Relationship Creation
# ----------------------------------------------------------------------


def create_relationship(
    driver,
    relationship: dict,
    entity_map: dict,
):
    """
    Create a directed relationship between entities.

    entity_map:
        Maps short IDs (e.g. "e1")
        to full entity names.
    """

    source_id = relationship.get("source")
    target_id = relationship.get("target")

    relation_type = relationship.get(
        "relation",
        "RELATED_TO",
    )

    # --------------------------------------------------------------
    # Resolve entity IDs → names
    # --------------------------------------------------------------
    source_name = entity_map.get(source_id)
    target_name = entity_map.get(target_id)

    # Skip invalid references
    if not source_name or not target_name:
        return

    # --------------------------------------------------------------
    # Neo4j does not allow parameterized relationship types
    # Sanitize relation string before interpolation
    # --------------------------------------------------------------
    safe_relation = "".join(
        char for char in relation_type if char.isalnum() or char == "_"
    )

    if not safe_relation:
        safe_relation = "RELATED_TO"

    # --------------------------------------------------------------
    # Create relationship
    # --------------------------------------------------------------
    with driver.session() as session:

        session.run(
            f"""
            MATCH (a:Entity {{name: $source_name}})
            MATCH (b:Entity {{name: $target_name}})
            MERGE (a)-[:{safe_relation}]->(b)
            """,
            source_name=source_name,
            target_name=target_name,
        )


# ----------------------------------------------------------------------
# Load Full Graph into Neo4j
# ----------------------------------------------------------------------


def load_graph(extracted_data: dict):
    """
    Load extracted graph data into Neo4j.

    Expected format:
    {
        "entities": [...],
        "relationships": [...]
    }
    """

    driver = get_driver()

    entities = extracted_data["entities"]
    relationships = extracted_data["relationships"]

    # --------------------------------------------------------------
    # Build entity ID → entity name map
    # Example:
    #   e1 -> OpenAI
    # --------------------------------------------------------------
    entity_map = {entity["id"]: entity["name"] for entity in entities if "id" in entity}

    # --------------------------------------------------------------
    # Create nodes
    # --------------------------------------------------------------
    print(f"\n⬆️ Writing {len(entities)} nodes to Neo4j...")

    for entity in entities:
        create_entity_node(driver, entity)

    # --------------------------------------------------------------
    # Create relationships
    # --------------------------------------------------------------
    print(f"⬆️ Writing " f"{len(relationships)} relationships to Neo4j...")

    for relationship in relationships:
        create_relationship(
            driver,
            relationship,
            entity_map,
        )

    print("✅ Graph loaded successfully")

    driver.close()


# ----------------------------------------------------------------------
# Fetch Complete Graph
# ----------------------------------------------------------------------


def get_full_graph(driver) -> dict:
    """
    Fetch all nodes and relationships from Neo4j.

    Returns:
    {
        "nodes": [...],
        "links": [...]
    }
    """

    with driver.session() as session:

        # ----------------------------------------------------------
        # Fetch nodes
        # ----------------------------------------------------------
        node_result = session.run("""
            MATCH (n:Entity)
            RETURN
                n.name AS name,
                n.type AS type
            """)

        nodes = [
            {
                "id": record["name"],
                "name": record["name"],
                "type": record["type"] or "Unknown",
            }
            for record in node_result
        ]

        # ----------------------------------------------------------
        # Fetch relationships
        # ----------------------------------------------------------
        link_result = session.run("""
            MATCH (a:Entity)-[r]->(b:Entity)

            RETURN
                a.name AS source,
                b.name AS target,
                type(r) AS relation
            """)

        links = [
            {
                "source": record["source"],
                "target": record["target"],
                "relation": record["relation"],
            }
            for record in link_result
        ]

    return {
        "nodes": nodes,
        "links": links,
    }


# ----------------------------------------------------------------------
# Fetch Contextual Subgraph
# ----------------------------------------------------------------------


def get_subgraph(
    driver,
    entity_names: list[str],
    hops: int = 2,
) -> dict:
    """
    Fetch a contextual subgraph centered around entities.

    Example:
        hops=2

        Entity
          -> neighbors
              -> neighbors of neighbors
    """

    with driver.session() as session:

        # ----------------------------------------------------------
        # Find connected nodes
        # ----------------------------------------------------------
        result = session.run(
            f"""
            MATCH (start:Entity)

            WHERE start.name IN $names

            MATCH path = (start)-[*1..{hops}]-(connected)

            RETURN DISTINCT
                start.name AS start_name,
                connected.name AS conn_name,
                connected.type AS conn_type
            """,
            names=entity_names,
        )

        nodes_seen = set()
        nodes = []

        # ----------------------------------------------------------
        # Collect unique nodes
        # ----------------------------------------------------------
        for record in result:

            candidate_nodes = [
                (
                    record["start_name"],
                    "Entity",
                ),
                (
                    record["conn_name"],
                    record["conn_type"],
                ),
            ]

            for name, node_type in candidate_nodes:

                if name and name not in nodes_seen:

                    nodes_seen.add(name)

                    nodes.append(
                        {
                            "name": name,
                            "type": node_type or "Unknown",
                        }
                    )

        # ----------------------------------------------------------
        # Fetch relationships between discovered nodes
        # ----------------------------------------------------------
        if nodes_seen:

            rel_result = session.run(
                """
                MATCH (a:Entity)-[r]->(b:Entity)

                WHERE
                    a.name IN $names
                    AND b.name IN $names

                RETURN
                    a.name AS source,
                    b.name AS target,
                    type(r) AS relation
                """,
                names=list(nodes_seen),
            )

            links = [
                {
                    "source": record["source"],
                    "target": record["target"],
                    "relation": record["relation"],
                }
                for record in rel_result
            ]

        else:
            links = []

    return {
        "nodes": nodes,
        "links": links,
    }
