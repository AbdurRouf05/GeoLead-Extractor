import pandas as pd

# Baca file Excel
df = pd.read_excel("Leads_United_States_97_leads.xlsx")

# Pisahkan
with_email = df[df["Emails"] != "N/A"]
without_email = df[df["Emails"] == "N/A"]

# Simpan
with_email.to_excel("leads_with_email.xlsx", index=False)
without_email.to_excel("leads_without_email.xlsx", index=False)

print(f"✅ Ada email: {len(with_email)}")
print(f"❌ Tidak ada email: {len(without_email)}")