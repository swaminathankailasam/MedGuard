import streamlit as st
import requests
import plotly.graph_objects as go
import re

st.set_page_config(page_title="MedGuard Research", layout="centered", page_icon="⚖️")

# --- BULLETPROOF CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA !important; }
    .stMarkdown, p, div, span, label { color: #1A2B48 !important; }
    
    .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #1A2B48 !important;
        border: 2px solid #D1D5DB !important;
        border-radius: 8px !important;
    }
    
    .stButton>button {
        background-color: #1A2B48 !important;
        color: #FFFFFF !important;
        border-radius: 6px !important;
        font-weight: bold !important;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #2D3E5E !important;
        border-color: #2D3E5E !important;
    }

    .streamlit-expanderHeader {
        background-color: #E2E8F0 !important;
        color: #1A2B48 !important;
        border-radius: 6px !important;
        font-weight: bold !important;
    }
    
    .severity-moderate { color: #D97706 !important; font-weight: bold; }
    .severity-major { color: #DC2626 !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #1A2B48;'>MedGuard AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #6B7280;'>Clinical Interaction Analysis & Pharmacovigilance Research</p>", unsafe_allow_html=True)
st.divider()

user_notes = st.text_area("Clinical Observation Notes:", placeholder="Type or paste patient history here...", height=150)

if st.button("RUN INTERACTION SCAN"):
    if user_notes:
        with st.spinner("Analyzing pharmacological structures..."):
            try:
                response = requests.post("http://127.0.0.1:8000/analyze_notes", json={"notes": user_notes})
                data = response.json()

                if data["status"] == "success":
                    st.markdown(f"**Extracted Entities:** `{', '.join(data['extracted_drugs'])}`")
                    
                    if not data["interactions"]:
                        st.info("No pharmacological interactions detected.")
                    else:
                        for inter in data["interactions"]:
                            sev_class = "severity-major" if inter['severity'] == "Major" else "severity-moderate"
                            
                            with st.expander(f"Interaction: {inter['drug_a']} + {inter['drug_b']}"):
                                st.markdown(f"**🦠 Known Clinical History:** `{inter['known_history']}`")
                                st.markdown(f"**⚠️ Severity:** <span class='{sev_class}'>{inter['severity']}</span>", unsafe_allow_html=True)
                                st.markdown(f"**📈 ML Confidence:** `{inter['confidence']}%`")
                                st.markdown(f"**🩺 Clinical Action:** {inter['clinical_action']}")
                                
                                st.markdown("---")
                                st.markdown("**📊 SHAP Chemical Evidence (Explainable AI):**")
                                
                                # --- PLOTLY DATA PARSER ---
                                features = []
                                shap_vals = []
                                colors = []
                                
                                for r in inter['pharmacological_reasoning']:
                                    # Use Regex to extract the feature name and the SHAP number
                                    match = re.search(r"(.*?):.*\(SHAP:\s*([+-]?\d+\.\d+)\)", r)
                                    if match:
                                        # Clean up the feature name to fit nicely on the graph
                                        feat_name = match.group(1).replace("Drug A [", "A: ").replace("Drug B [", "B: ").replace("]", "")
                                        val = float(match.group(2))
                                        
                                        features.append(feat_name)
                                        shap_vals.append(val)
                                        # Red for danger (positive SHAP), Teal for safe (negative SHAP)
                                        colors.append('#DC2626' if val > 0 else '#0D9488')
                                        
                                # --- DRAW THE INTERACTIVE CHART ---
                                if features:
                                    fig = go.Figure(go.Bar(
                                        x=shap_vals,
                                        y=features,
                                        orientation='h',
                                        marker_color=colors,
                                        text=[f"{v:+.4f}" for v in shap_vals],
                                        textposition='auto'
                                    ))
                                    
                                    fig.update_layout(
                                        margin=dict(l=10, r=10, t=30, b=10),
                                        height=200 + (len(features) * 30),
                                        paper_bgcolor='rgba(0,0,0,0)',
                                        plot_bgcolor='rgba(0,0,0,0)',
                                        font=dict(color='#1A2B48'),
                                        xaxis=dict(title="SHAP Impact Value", zerolinecolor='#9CA3AF', gridcolor='#E5E7EB'),
                                        yaxis=dict(autorange="reversed") # Put the biggest feature on top
                                    )
                                    
                                    st.plotly_chart(fig, use_container_width=True)
                                else:
                                    st.info("Could not render chart. Showing raw data instead.")
                                    for r in inter['pharmacological_reasoning']:
                                        st.write(r)

            except Exception as e:
                st.error(f"Connection lost: Ensure Backend (api.py) is running. (Error: {e})")
    else:
        st.warning("Please enter medical text to proceed.")