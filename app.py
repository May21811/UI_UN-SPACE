import streamlit as st
from knowledge_base import KnowledgeBase
from inference_engine import ForwardChaining
from certainty_factor import CertaintyFactor

st.set_page_config(page_title="Sistem Pakar Pemilihan Laptop", layout="centered")
st.title("💻 Sistem Pakar Pemilihan Laptop")
st.write("Temukan kategori laptop yang paling sesuai dengan kebutuhan dan budget Anda.")

# Inisialisasi komponen backend
@st.cache_resource
def init_system():
    kb = KnowledgeBase()
    fc = ForwardChaining(kb)
    return kb, fc

kb, fc = init_system()

st.header("📋 Pilih Kriteria Kebutuhan Anda")
cf_user_dict = {}
kriteria_terpilih = []

opsi_cf = {
    "Tidak": 0.0,
    "Sedikit Yakin": 0.4,
    "Cukup Yakin": 0.6,
    "Yakin": 0.8,
    "Sangat Yakin": 1.0
}

# 1. Menampilkan daftar pertanyaan drop-down kriteria
for g in kb.get_semua_gejala():
    pilihan = st.selectbox(g['pertanyaan'], list(opsi_cf.keys()), key=g['id'])
    bobot = opsi_cf[pilihan]
    
    if bobot > 0:
        kriteria_terpilih.append(g['id'])
        cf_user_dict[g['id']] = bobot

st.write("---")

# 2. Tombol eksekusi diagnosis
if st.button("🔥 Proses Diagnosis", type="primary"):
    if not kriteria_terpilih:
        st.warning("Silakan pilih minimal satu kriteria terlebih dahulu.")
    else:
        # Jalankan Forward Chaining dengan variabel yang sudah benar
        rules_aktif = fc.inferensi(kriteria_terpilih)
        
        if not rules_aktif:
            st.error("Tidak ditemukan rekomendasi laptop yang cocok dengan kombinasi kriteria tersebut. Silakan coba kombinasi lain.")
        else:
            # Hitung Certainty Factor
            hasil_cf = CertaintyFactor.hitung_cf(rules_aktif, cf_user_dict)
            
            st.header("✨ Hasil Rekomendasi Laptop")
            hasil_sorted = sorted(hasil_cf.items(), key=lambda item: item[1], reverse=True)
            
            for laptop_id, nilai_cf in hasil_sorted:
                laptop_data = kb.penyakit[laptop_id]
                persentase = nilai_cf * 100
                
                with st.expander(f"📌 {laptop_data['nama']} — Tingkat Keyakinan: {persentase:.1f}%", expanded=True):
                    st.write(f"**Deskripsi:** {laptop_data['deskripsi']}")
                    
            # Fasilitas Penjelasan
            st.subheader("🔍 Fasilitas Penjelasan (Explanation Facility)")
            st.write(f"**Kriteria Aktif:** {', '.join(kriteria_terpilih)}")
            st.write(f"**Aturan (Rules) yang Terpicu:** {', '.join([r['id'] for r in rules_aktif])}")