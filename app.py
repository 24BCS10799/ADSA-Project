import streamlit as st
from collections import deque, defaultdict
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# ---- Graph logic ----
class SocialGraph:
    def __init__(self):
        self.adj = defaultdict(set)
    def add_user(self, user):
        if user not in self.adj:
            self.adj[user] = set()

    def add_friendship(self, u, v):
        if u != v:
            self.adj[u].add(v)
            self.adj[v].add(u)

    def friends(self, user):
        return set(self.adj[user])

    def users(self):
        return list(self.adj.keys())

    def shortest_path(self, start, goal):
        if start not in self.adj or goal not in self.adj:
            return None
        if start == goal:
            return [start]
        q = deque([start])
        pred = {start: None}
        while q:
            curr = q.popleft()
            for nb in self.adj[curr]:
                if nb not in pred:
                    pred[nb] = curr
                    if nb == goal:
                        path = [goal]
                        while pred[path[-1]] is not None:
                            path.append(pred[path[-1]])
                        path.reverse()
                        return path
                    q.append(nb)
        return None

    def recommend_friends(self, user, k=5):
        """Simple friend recommendation based on mutual friends count"""
        scores = []
        existing = self.adj[user] | {user}
        for candidate in self.adj.keys():
            if candidate in existing:
                continue
            mutual = len(self.adj[user] & self.adj[candidate])
            if mutual > 0:
                scores.append((candidate, mutual))
        scores.sort(key=lambda x: (-x[1], x[0]))
        return scores[:k]

# ---- Build demo network ----
G = SocialGraph()
names = ["Alice","Bob","Carol","Dave","Eve","Frank","Grace","Heidi","Ivan","Judy"]
for n in names:
    G.add_user(n)

friendships = [
    ("Alice","Bob"),("Alice","Carol"),("Alice","Frank"),
    ("Bob","Carol"),("Bob","Dave"),
    ("Carol","Dave"),("Carol","Eve"),
    ("Dave","Eve"),
    ("Eve","Frank"),
    ("Frank","Grace"),
    ("Grace","Heidi"),("Grace","Judy"),
    ("Heidi","Ivan"),("Ivan","Judy")
]
for u,v in friendships:
    G.add_friendship(u,v)

# ---- Streamlit UI ----
st.set_page_config(page_title="Mini Social Network", layout="wide")
st.title("🌐 Mini Social Network")
st.markdown("A simple interactive demo to visualize friendships, find connections, and suggest new friends!")

tab1, tab2, tab3 = st.tabs(["🔗 View Network", "🚀 Shortest Path", "🤝 Friend Suggestions"])

# ---- TAB 1: View Network ----
with tab1:
    st.subheader("Network Graph")
    nx_graph = nx.Graph()
    for u in G.users():
        nx_graph.add_node(u)
        for v in G.friends(u):
            nx_graph.add_edge(u, v)

    fig, ax = plt.subplots(figsize=(6, 4))
    nx.draw(nx_graph, with_labels=True, node_color="#81C784", node_size=1200, font_size=10, font_weight="bold")
    st.pyplot(fig)

    st.write("### Friend Lists")
    for user in sorted(G.users()):
        st.write(f"**{user}** → {', '.join(sorted(G.friends(user)))}")

# ---- TAB 2: Shortest Path ----
with tab2:
    st.subheader("Find the Shortest Path Between Two Users")

    col1, col2 = st.columns(2)
    with col1:
        start = st.selectbox("Select Start User", sorted(G.users()))
    with col2:
        goal = st.selectbox("Select Target User", sorted(G.users()))

    if st.button("Find Path"):
        path = G.shortest_path(start, goal)
        if path:
            st.success(f"Shortest Path ({len(path)-1} connections): {' → '.join(path)}")
        else:
            st.error("No connection found between these users.")

# ---- TAB 3: Friend Suggestions ----
with tab3:
    st.subheader("Friend Suggestions")

    user = st.selectbox("Select a user", sorted(G.users()))

    if st.button("Recommend Friends"):
        recs = G.recommend_friends(user)
        if recs:
            df = pd.DataFrame(recs, columns=["Suggested Friend", "Mutual Friends"])
            st.write(f"### Top Friend Recommendations for {user}")
            st.dataframe(df)
        else:
            st.warning("No new friend recommendations available.")


