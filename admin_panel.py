"""
Panou de administrare pentru Proprieto ANAF 2026
"""

import streamlit as st
import pandas as pd
from supabase import Client
import auth
from datetime import datetime
from io import BytesIO

def show_users_management(supabase: Client):
    """Gestionare utilizatori (doar pentru admini)"""
    st.header("👥 Gestionare Utilizatori")

    # Tab-uri pentru funcții diferite
    tab1, tab2, tab3 = st.tabs(["Lista Utilizatori", "Adaugă Utilizator", "Statistici"])

    with tab1:
        st.subheader("📋 Utilizatori Înregistrați")

        try:
            # Preluare utilizatori
            result = supabase.table("users").select("*").order("created_at", desc=True).execute()

            if not result.data:
                st.info("Niciun utilizator înregistrat încă.")
            else:
                df = pd.DataFrame(result.data)

                # Formatare date
                df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%d-%m-%Y %H:%M')
                df['last_login'] = pd.to_datetime(df['last_login'], errors='coerce').dt.strftime('%d-%m-%Y %H:%M')

                # Afișare tabel
                for _, user in df.iterrows():
                    with st.container():
                        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

                        with col1:
                            role_icon = "👑" if user['role'] == 'admin' else "👤"
                            st.markdown(f"{role_icon} **{user['nume']}**")
                            st.caption(f"📧 {user['email']}")

                        with col2:
                            status = "🟢 Activ" if user['active'] else "🔴 Inactiv"
                            st.write(status)
                            st.caption(f"Rol: {user['role']}")

                        with col3:
                            st.caption(f"Înregistrat: {user['created_at']}")
                            if user['last_login']:
                                st.caption(f"Ultima auth: {user['last_login']}")
                            else:
                                st.caption("Nu s-a autentificat niciodată")

                        with col4:
                            # Acțiuni (nu poți șterge propriul cont)
                            if user['id'] != st.session_state.user_id:
                                col_a, col_b = st.columns(2)

                                with col_a:
                                    # Toggle active/inactive
                                    new_status = not user['active']
                                    action_label = "🔓 Activează" if not user['active'] else "🔒 Dezactivează"

                                    if st.button(action_label, key=f"toggle_{user['id']}"):
                                        try:
                                            supabase.table("users").update({
                                                "active": new_status
                                            }).eq("id", user['id']).execute()
                                            st.success(f"Utilizator {'activat' if new_status else 'dezactivat'}!")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Eroare: {str(e)}")

                                with col_b:
                                    # Șterge utilizator
                                    if st.button("🗑️", key=f"del_{user['id']}", help="Șterge utilizator"):
                                        try:
                                            supabase.table("users").delete().eq("id", user['id']).execute()
                                            st.success("Utilizator șters!")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Eroare: {str(e)}")
                            else:
                                st.caption("(Cont curent)")

                        st.divider()

        except Exception as e:
            st.error(f"❌ Eroare la încărcarea utilizatorilor: {str(e)}")

    with tab2:
        st.subheader("➕ Adaugă Utilizator Nou")

        with st.form("add_user_form"):
            col1, col2 = st.columns(2)

            with col1:
                new_email = st.text_input("Email*", placeholder="user@exemplu.ro")
                new_nume = st.text_input("Nume Complet*", placeholder="Popescu Ion")

            with col2:
                new_password = st.text_input("Parolă Inițială*", type="password", placeholder="Min 8 caractere")
                new_role = st.selectbox("Rol", ["user", "admin"])

            submitted = st.form_submit_button("👤 Creează Cont", use_container_width=True)

            if submitted:
                if not new_email or not new_nume or not new_password:
                    st.error("❌ Toate câmpurile sunt obligatorii!")
                else:
                    success, message = auth.register_user(
                        supabase,
                        new_email,
                        new_password,
                        new_nume,
                        new_role
                    )

                    if success:
                        st.success(f"✅ {message}")
                        st.info(f"📧 Credențiale: {new_email} / {new_password}")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")

    with tab3:
        st.subheader("📊 Statistici Utilizatori")

        try:
            result = supabase.table("users").select("*").execute()

            if result.data:
                total = len(result.data)
                admins = len([u for u in result.data if u['role'] == 'admin'])
                users = total - admins
                active = len([u for u in result.data if u.get('active', True)])
                inactive = total - active

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Utilizatori", total)
                col2.metric("Administratori", admins)
                col3.metric("Utilizatori", users)
                col4.metric("Activi / Inactivi", f"{active} / {inactive}")

                # Activitate recentă
                st.markdown("### 📅 Activitate Recentă")
                recent = [u for u in result.data if u.get('last_login')]
                recent.sort(key=lambda x: x['last_login'], reverse=True)

                if recent[:5]:
                    for user in recent[:5]:
                        login_time = pd.to_datetime(user['last_login']).strftime('%d-%m-%Y %H:%M')
                        st.text(f"• {user['nume']} ({user['email']}) - {login_time}")
                else:
                    st.info("Nicio activitate recentă.")

        except Exception as e:
            st.error(f"❌ Eroare: {str(e)}")


def show_data_overview(supabase: Client, user_id: str, is_admin: bool):
    """Prezentare generală date (contracte, imobile) pentru toți utilizatorii"""
    st.header("📊 Prezentare Generală Date")

    try:
        # Filtrare: adminii văd tot, userii doar propriile date
        if is_admin:
            imobile_result = supabase.table("imobile").select("*, users(nume, email)").execute()
            contracte_result = supabase.table("contracte").select("*, imobile(nume), users(nume, email)").execute()
        else:
            imobile_result = supabase.table("imobile").select("*").eq("user_id", user_id).execute()
            contracte_result = supabase.table("contracte").select("*, imobile(nume)").eq("user_id", user_id).execute()

        # Statistici generale
        col1, col2, col3 = st.columns(3)
        col1.metric("Imobile Totale", len(imobile_result.data) if imobile_result.data else 0)
        col2.metric("Contracte Active", len(contracte_result.data) if contracte_result.data else 0)

        # Calculare venit total estimat (doar pentru anul curent)
        if contracte_result.data:
            venit_total = 0
            for contract in contracte_result.data:
                venit_total += contract.get('chirie_lunara', 0) * 12

            col3.metric("Venit Anual Estimat", f"{venit_total:,.0f} RON")

        # Tabel imobile
        if is_admin and imobile_result.data:
            st.markdown("### 🏠 Imobile (Toți Utilizatorii)")
            df_imobile = pd.DataFrame(imobile_result.data)

            display_data = []
            for _, row in df_imobile.iterrows():
                display_data.append({
                    'Proprietar': row['users']['nume'] if row.get('users') else 'N/A',
                    'Email': row['users']['email'] if row.get('users') else 'N/A',
                    'Imobil': row['nume'],
                    'Adresă': row.get('adresa', '-'),
                    'Cotă': f"{row['procent_proprietate']}%"
                })

            st.dataframe(pd.DataFrame(display_data), use_container_width=True, hide_index=True)

        # Tabel contracte
        if is_admin and contracte_result.data:
            st.markdown("### 📄 Contracte (Toți Utilizatorii)")
            df_contracte = pd.DataFrame(contracte_result.data)

            display_data = []
            for _, row in df_contracte.iterrows():
                display_data.append({
                    'Proprietar': row['users']['nume'] if row.get('users') else 'N/A',
                    'Imobil': row['imobile']['nume'] if row.get('imobile') else 'N/A',
                    'Locatar': row['locatar'],
                    'Chirie': f"{row['chirie_lunara']:,.0f} {row['moneda']}",
                    'De la': row['data_inceput'],
                    'Până la': row.get('data_sfarsit', 'Nedeterminat')
                })

            st.dataframe(pd.DataFrame(display_data), use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"❌ Eroare la încărcarea datelor: {str(e)}")


def show_system_settings(supabase: Client):
    """Setări sistem (pentru admini)"""
    st.header("⚙️ Setări Sistem")

    tab1, tab2 = st.tabs(["Configurare", "Backup & Export"])

    with tab1:
        st.subheader("🔧 Configurare Aplicație")

        # Salariu minim
        st.markdown("### 💰 Salariu Minim Brut")
        new_salariu = st.number_input(
            "Salariu minim brut (RON)",
            value=4050,
            step=50,
            help="Folosit pentru calculul pragurilor CASS"
        )

        if st.button("💾 Salvează Salariu Minim"):
            st.info("Această setare trebuie actualizată în cod (app.py linia 30)")
            st.code(f"SALARIU_MINIM = {new_salariu}", language="python")

        # Curs BNR default
        st.markdown("### 💱 Curs BNR Default")
        new_curs = st.number_input(
            "Curs mediu EUR/RON",
            value=5.02,
            step=0.01,
            help="Curs folosit implicit pentru conversii"
        )

        if st.button("💾 Salvează Curs Default"):
            st.info("Această setare trebuie actualizată în cod (app.py linia 31)")
            st.code(f"CURS_BNR_DEFAULT = {new_curs}", language="python")

    with tab2:
        st.subheader("💾 Backup & Export Date")

        st.markdown("### 📥 Export Complet")
        st.info("Exportă toate datele din baza de date pentru backup.")

        if st.button("📊 Export Toate Datele (Excel)"):
            try:
                # Export toate tabelele
                users_data = supabase.table("users").select("email, nume, role, active, created_at").execute()
                imobile_data = supabase.table("imobile").select("*").execute()
                contracte_data = supabase.table("contracte").select("*").execute()

                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    if users_data.data:
                        pd.DataFrame(users_data.data).to_excel(writer, sheet_name='Utilizatori', index=False)
                    if imobile_data.data:
                        pd.DataFrame(imobile_data.data).to_excel(writer, sheet_name='Imobile', index=False)
                    if contracte_data.data:
                        pd.DataFrame(contracte_data.data).to_excel(writer, sheet_name='Contracte', index=False)

                st.download_button(
                    "📥 Descarcă Backup Complet",
                    buffer.getvalue(),
                    f"Backup_Proprieto_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            except Exception as e:
                st.error(f"❌ Eroare la export: {str(e)}")
