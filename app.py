import streamlit as st
import pandas as pd
import plotly.express as px

# Chargement des données
@st.cache_data
def load_data():
    confirmed = pd.read_csv("./time_series_covid19_confirmed_global.csv")
    deaths = pd.read_csv("./time_series_covid19_deaths_global.csv")
    recovered = pd.read_csv("./time_series_covid19_recovered_global.csv")
    return confirmed, deaths, recovered

confirmed, deaths, recovered = load_data()

# Transformation des données pour faciliter l'analyse
def prepare_data(df):
    df_long = df.melt(id_vars=["Province/State", "Country/Region", "Lat", "Long"],
                      var_name="Date", value_name="Cases")
    df_long["Date"] = pd.to_datetime(df_long["Date"])
    return df_long

confirmed_long = prepare_data(confirmed)
deaths_long = prepare_data(deaths)
recovered_long = prepare_data(recovered)

# Interface utilisateur avec une barre latérale
st.sidebar.title("Analyse COVID-19")
visualization_type = st.sidebar.selectbox(
    "Sélectionnez le type de visualisation",
    [
        "Cas et Décès Mondiaux",
        "Vaccination",
        "Analyse Temporelle",
        "Taux d'Infection et de Mortalité"
    ]
)

# Visualisation 1 : Cas et Décès Mondiaux
if visualization_type == "Cas et Décès Mondiaux":
    st.title("Analyse des Cas Confirmés et des Décès Mondiaux")

    # Agrégation des données pour obtenir les totaux mondiaux par date
    confirmed_worldwide = confirmed_long.groupby("Date")["Cases"].sum().reset_index()
    deaths_worldwide = deaths_long.groupby("Date")["Cases"].sum().reset_index()

    # Fusion des données pour un affichage combiné
    combined_world_data = confirmed_worldwide.merge(deaths_worldwide, on="Date", suffixes=('_confirmed', '_deaths'))
    
    # Graphique pour visualiser les cas confirmés et les décès
    st.subheader("Tendances des Cas Confirmés et des Décès au Niveau Mondial")
    fig_world_trend = px.line(
        combined_world_data, x="Date",
        y=["Cases_confirmed", "Cases_deaths"],
        labels={"value": "Nombre de Cas", "Date": "Date", "variable": "Type de Cas"},
        title="Évolution des Cas Confirmés et Décès Mondiaux"
    )

    fig_world_trend.update_yaxes(type="log", title="Nombre de Cas (échelle logarithmique)")

    st.plotly_chart(fig_world_trend, use_container_width=True)

    # Point 2
    st.title("Répartition des Cas Confirmés et Décès par Pays")

    # Sélection des pays à comparer
    countries = st.multiselect("Sélectionnez les pays à comparer", confirmed_long["Country/Region"].unique())

    # Sélection de la période
    min_date = confirmed_long['Date'].min()
    max_date = confirmed_long['Date'].max()
    selected_period = st.date_input("Sélectionnez une période (optionnel)", [min_date, max_date], min_value=min_date, max_value=max_date)

    if countries and len(selected_period) == 2:
        start_date, end_date = selected_period
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        if start_date and end_date:
            # Filtrer les données pour la période sélectionnée
            confirmed_countries = confirmed_long[(confirmed_long["Country/Region"].isin(countries)) & (confirmed_long["Date"] >= start_date) & (confirmed_long["Date"] <= end_date)]
            deaths_countries = deaths_long[(deaths_long["Country/Region"].isin(countries)) & (deaths_long["Date"] >= start_date) & (deaths_long["Date"] <= end_date)]

            subtitle = f"du {start_date.strftime('%Y-%m-%d')} au {end_date.strftime('%Y-%m-%d')}"
        else:
            confirmed_countries = confirmed_long[confirmed_long["Country/Region"].isin(countries)]
            deaths_countries = deaths_long[deaths_long["Country/Region"].isin(countries)]

            # Agrégation cumulative sur toute la période
            confirmed_total = confirmed_countries.groupby("Country/Region")["Cases"].sum().reset_index()
            deaths_total = deaths_countries.groupby("Country/Region")["Cases"].sum().reset_index()

            subtitle = "cumulé sur toute la période"

        confirmed_total = confirmed_countries.groupby("Country/Region")["Cases"].sum().reset_index()
        deaths_total = deaths_countries.groupby("Country/Region")["Cases"].sum().reset_index()

        # Fusionner les deux séries de données pour comparer les cas confirmés et décès
        combined_totals = confirmed_total.merge(deaths_total, on="Country/Region", suffixes=('_confirmed', '_deaths'))

        # Création du diagramme en barre groupé
        st.subheader(f"Comparaison des Cas Confirmés et Décès entre Pays {subtitle}")
        fig_comparison = px.bar(
            combined_totals, x="Country/Region",
            y=["Cases_confirmed", "Cases_deaths"],
            labels={"value": "Nombre de Cas", "Country/Region": "Pays", "variable": "Type de Cas"},
            title=f"Répartition des Cas Confirmés et Décès par Pays {subtitle}",
            barmode='group'
        )

        # Affichage du graphique
        st.plotly_chart(fig_comparison, use_container_width=True)

# Visualisation 2 : Vaccination
elif visualization_type == "Vaccination":

    st.title("Analyse des Taux de Vaccination, Cas Confirmés et Décès par Pays")

    # Sélection des pays à comparer
    countries = st.multiselect("Sélectionnez les pays à comparer", recovered_long["Country/Region"].unique())

    # Sélection de la période
    min_date = recovered_long['Date'].min()
    max_date = recovered_long['Date'].max()
    selected_period = st.date_input("Sélectionnez une période (optionnel)", [min_date, max_date], min_value=min_date, max_value=max_date)

    if countries and len(selected_period) == 2:
        start_date, end_date = selected_period
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        if start_date and end_date:
            # Filtrer les données pour la période sélectionnée
            confirmed_countries = confirmed_long[(confirmed_long["Country/Region"].isin(countries)) & (confirmed_long["Date"] >= start_date) & (confirmed_long["Date"] <= end_date)]
            deaths_countries = deaths_long[(deaths_long["Country/Region"].isin(countries)) & (deaths_long["Date"] >= start_date) & (deaths_long["Date"] <= end_date)]
            recovered_countries = recovered_long[(recovered_long["Country/Region"].isin(countries)) & (recovered_long["Date"] >= start_date) & (recovered_long["Date"] <= end_date)]

            subtitle = f"du {start_date.strftime('%Y-%m-%d')} au {end_date.strftime('%Y-%m-%d')}"
        else:
            # Si aucune période n'est sélectionnée, calculer le cumul sur toute la période
            confirmed_countries = confirmed_long[confirmed_long["Country/Region"].isin(countries)]
            deaths_countries = deaths_long[deaths_long["Country/Region"].isin(countries)]
            recovered_countries = recovered_long[recovered_long["Country/Region"].isin(countries)]

            # Agrégation cumulative sur toute la période
            confirmed_total = confirmed_countries.groupby("Country/Region")["Cases"].sum().reset_index()
            deaths_total = deaths_countries.groupby("Country/Region")["Cases"].sum().reset_index()
            recovered_total = recovered_countries.groupby("Country/Region")["Cases"].sum().reset_index()

            subtitle = "cumulé sur toute la période"

        # Agrégation sur la période sélectionnée
        confirmed_total = confirmed_countries.groupby("Country/Region")["Cases"].sum().reset_index()
        deaths_total = deaths_countries.groupby("Country/Region")["Cases"].sum().reset_index()
        recovered_total = recovered_countries.groupby("Country/Region")["Cases"].sum().reset_index()

        # Fusionner les trois séries de données pour comparer les vaccinations, cas et décès
        combined_totals = recovered_total.merge(confirmed_total, on="Country/Region", suffixes=('_recovered', '_confirmed'))
        combined_totals = combined_totals.merge(deaths_total, on="Country/Region")
        combined_totals.rename(columns={"Cases": "Cases_deaths"}, inplace=True)

        # Création du diagramme en barre groupé
        st.subheader(f"Comparaison des Taux de Vaccination, Cas Confirmés et Décès entre Pays {subtitle}")
        fig_vaccination = px.bar(
            combined_totals, x="Country/Region",
            y=["Cases_recovered", "Cases_confirmed", "Cases_deaths"],
            labels={"value": "Nombre de Cas", "Country/Region": "Pays", "variable": "Type de Cas"},
            title=f"Taux de Vaccination, Cas Confirmés et Décès par Pays {subtitle}",
            barmode='group'
        )

        # Affichage du graphique
        st.plotly_chart(fig_vaccination, use_container_width=True)

# Visualisation 3 : Analyse Temporelle
elif visualization_type == "Analyse Temporelle":
    st.title("Évolution des Cas et Décès dans le Temps")

    # Sélection de la période
    min_date = confirmed_long['Date'].min()
    max_date = confirmed_long['Date'].max()
    selected_period = st.date_input("Sélectionnez une période Part 1", [min_date, max_date], min_value=min_date, max_value=max_date)

    if len(selected_period) == 2:
        start_date, end_date = selected_period
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        if start_date and end_date:
            # Filtrer les données pour la période sélectionnée
            confirmed_worldwide = confirmed_long[(confirmed_long["Date"] >= start_date) & (confirmed_long["Date"] <= end_date)]
            deaths_worldwide = deaths_long[(deaths_long["Date"] >= start_date) & (deaths_long["Date"] <= end_date)]

            subtitle = f"du {start_date.strftime('%Y-%m-%d')} au {end_date.strftime('%Y-%m-%d')}"
        else:
            # Si aucune période n'est sélectionnée, afficher l'évolution globale
            confirmed_worldwide = confirmed_long
            deaths_worldwide = deaths_long
            subtitle = "depuis le début de la pandémie"

        # Agrégation des données par date
        confirmed_total = confirmed_worldwide.groupby("Date")["Cases"].sum().reset_index()
        deaths_total = deaths_worldwide.groupby("Date")["Cases"].sum().reset_index()

        # Fusion des données pour un affichage combiné
        combined_world_data = confirmed_total.merge(deaths_total, on="Date", suffixes=('_confirmed', '_deaths'))

        # Graphique pour l'évolution des cas confirmés et décès
        st.subheader(f"Évolution des Cas Confirmés et Décès {subtitle}")
        fig_evolution = px.line(
            combined_world_data, x="Date",
            y=["Cases_confirmed", "Cases_deaths"],
            labels={"value": "Nombre de Cas", "Date": "Date", "variable": "Type de Cas"},
            title="Évolution des Cas Confirmés et Décès"
        )

        # Gestion de l'échelle logarithmique pour équilibrer les valeurs
        fig_evolution.update_yaxes(type="log", title="Nombre de Cas (échelle logarithmique)")

        # Affichage du graphique
        st.plotly_chart(fig_evolution, use_container_width=True)

        # Deuxième partie : Comparaison des tendances des cas et décès entre différentes régions
        st.subheader("Comparaison des Tendances entre Régions")

        # Sélection de la période
        min_date = confirmed_long['Date'].min()
        max_date = confirmed_long['Date'].max()
        selected_period = st.date_input("Sélectionnez une période Part 2", [min_date, max_date], min_value=min_date, max_value=max_date)

        # Extraction des régions disponibles dans les données
        available_regions = confirmed_long["Country/Region"].unique()
        selected_regions = st.multiselect("Sélectionnez les régions à comparer", available_regions)

        if selected_regions and len(selected_period) == 2:
            start_date, end_date = selected_period
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)

            if start_date and end_date:
                # Filtrer les données pour les régions et la période sélectionnées
                confirmed_regions = confirmed_long[(confirmed_long["Country/Region"].isin(selected_regions)) & (confirmed_long["Date"] >= start_date) & (confirmed_long["Date"] <= end_date)]
                deaths_regions = deaths_long[(deaths_long["Country/Region"].isin(selected_regions)) & (deaths_long["Date"] >= start_date) & (deaths_long["Date"] <= end_date)]

                subtitle = f"du {start_date.strftime('%Y-%m-%d')} au {end_date.strftime('%Y-%m-%d')}"
            else:
                # Si aucune période n'est sélectionnée, afficher toutes les données
                confirmed_regions = confirmed_long[confirmed_long["Country/Region"].isin(selected_regions)]
                deaths_regions = deaths_long[deaths_long["Country/Region"].isin(selected_regions)]
                subtitle = "pour toutes les dates disponibles"

            # Graphique pour les cas confirmés par région
            fig_confirmed_regions = px.line(
                confirmed_regions, x="Date", y="Cases", color="Country/Region",
                labels={"Cases": "Cas Confirmés", "Date": "Date", "Country/Region": "Région"},
                title=f"Comparaison des Cas Confirmés entre Régions {subtitle}"
            )
            fig_confirmed_regions.update_yaxes(type="log")  # Appliquer l'échelle logarithmique aux cas confirmés
            st.plotly_chart(fig_confirmed_regions, use_container_width=True)

            # Graphique pour les décès par région
            fig_deaths_regions = px.line(
                deaths_regions, x="Date", y="Cases", color="Country/Region",
                labels={"Cases": "Décès", "Date": "Date", "Country/Region": "Région"},
                title=f"Comparaison des Décès entre Régions {subtitle}"
            )
            fig_deaths_regions.update_yaxes(type="log")  # Appliquer l'échelle logarithmique aux décès
            st.plotly_chart(fig_deaths_regions, use_container_width=True)
# Visualisation 4 : Taux d'Infection et de Mortalité
elif visualization_type == "Taux d'Infection et de Mortalité":
    st.title("Analyse des Taux d'Infection et de Mortalité dans les Pays les Plus Touchés")

    # Sélection des pays à comparer (Pays les plus touchés)
    # Extraction des régions disponibles dans les données
    available_regions = confirmed_long["Country/Region"].unique()
    countries = st.multiselect("Sélectionnez les régions à comparer", available_regions)
    # countries = st.multiselect("Sélectionnez les pays à analyser", confirmed_long["Country/Region"].unique(), default=["United S", "India", "Brazil"])

    # Sélection de la période
    min_date = confirmed_long['Date'].min()
    max_date = confirmed_long['Date'].max()
    selected_period = st.date_input("Sélectionnez une période", [min_date, max_date], min_value=min_date, max_value=max_date)

    if countries and len(selected_period) == 2:
        start_date, end_date = selected_period
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        if start_date and end_date:
            # Filtrer les données pour les pays et la période sélectionnés
            confirmed_countries = confirmed_long[(confirmed_long["Country/Region"].isin(countries)) & (confirmed_long["Date"] >= start_date) & (confirmed_long["Date"] <= end_date)]
            deaths_countries = deaths_long[(deaths_long["Country/Region"].isin(countries)) & (deaths_long["Date"] >= start_date) & (deaths_long["Date"] <= end_date)]

            # Calcul du taux de mortalité
            data_countries = confirmed_countries.merge(deaths_countries, on=["Country/Region", "Date"], suffixes=('_confirmed', '_deaths'))
            data_countries["Mortality Rate (%)"] = (data_countries["Cases_deaths"] / data_countries["Cases_confirmed"]) * 100

            subtitle = f"du {start_date.strftime('%Y-%m-%d')} au {end_date.strftime('%Y-%m-%d')}"

            # Graphique pour les taux d'infection par pays
            st.subheader(f"Taux d'Infection et de Mortalité {subtitle}")
            fig_infection = px.line(
                data_countries, x="Date", y="Cases_confirmed", color="Country/Region",
                labels={"Cases_confirmed": "Taux d'Infection", "Date": "Date", "Country/Region": "Pays"},
                title="Taux d'Infection par Pays"
            )

            fig_mortality = px.line(
                data_countries, x="Date", y="Mortality Rate (%)", color="Country/Region",
                labels={"Mortality Rate (%)": "Taux de Mortalité (%)", "Date": "Date", "Country/Region": "Pays"},
                title="Taux de Mortalité par Pays"
            )

            # Gestion de l'échelle logarithmique si nécessaire
            fig_infection.update_yaxes(type="log", title="Taux d'Infection (échelle logarithmique)")
            fig_mortality.update_yaxes(type="log", title="Taux de Mortalité (%) (échelle logarithmique)")

            # Affichage des graphiques
            st.plotly_chart(fig_infection, use_container_width=True)
            st.plotly_chart(fig_mortality, use_container_width=True)
