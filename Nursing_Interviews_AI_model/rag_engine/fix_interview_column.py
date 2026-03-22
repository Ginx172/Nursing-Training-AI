import pandas as pd

csv_path = "C:/Users/eugdu/MyPythonProjects/Nursing_Interviews_AI_model/rag_engine/document_summaries.csv"

# Încarcă fișierul
df = pd.read_csv(csv_path, encoding="ISO-8859-1")

# Înlocuiește valoarea
df["Suggested Modules"] = df["Suggested Modules"].apply(
    lambda x: x.replace("Interviuri NHS", "Interview NHS") if isinstance(x, str) and "Interview NHS" not in x else x
)

# Salvează modificările
df.to_csv(csv_path, index=False, encoding="utf-8")

print("✅ Am înlocuit cu succes 'Interviuri NHS' cu 'Interview NHS'")
