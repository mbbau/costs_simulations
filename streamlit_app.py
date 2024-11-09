import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Cargar los datos del archivo
costs_data = pd.read_excel('costs_data.xlsx')

# Configurar la página de Streamlit
st.title("Monte Carlo Simulation for Platform Usage")
st.sidebar.header("Simulation Parameters")

# Entradas del usuario en la barra lateral
mean_prompts = st.sidebar.number_input("Average number of prompts per user per month", min_value=1, max_value=500, value=40)

# Parámetros de uso por tipo de modelo
st.sidebar.subheader("Usage Parameters")
image_min = st.sidebar.number_input("Min images per use", min_value=1, max_value=100, value=1)
image_max = st.sidebar.number_input("Max images per use", min_value=image_min, max_value=100, value=5)
runtime_min = st.sidebar.number_input("Min runtime per use (seconds)", min_value=1, max_value=10000, value=10)
runtime_max = st.sidebar.number_input("Max runtime per use (seconds)", min_value=runtime_min, max_value=10000, value=600)
token_min = st.sidebar.number_input("Min tokens per use", min_value=1, max_value=100000, value=100)
token_max = st.sidebar.number_input("Max tokens per use", min_value=token_min, max_value=100000, value=10000)

# Simular 5000 usuarios
num_users = 5000
user_monthly_usage = []

# Grado de libertad para simular prompts con distribución t de Student
degrees_of_freedom = 30

# Simular el uso mensual por cada usuario
for user_id in range(1, num_users + 1):
    num_uses_per_month = int(np.random.standard_t(degrees_of_freedom) * 5 + mean_prompts)
    num_uses_per_month = max(1, num_uses_per_month)
    
    total_monthly_cost = 0

    for _ in range(num_uses_per_month):
        model = costs_data.sample(1).iloc[0]

        # Simular el uso en función del tipo con los parámetros personalizados
        if model['Type'] == 'image_count':
            usage = np.random.randint(image_min, image_max)
        elif model['Type'] == 'run_time':
            usage = np.random.uniform(runtime_min, runtime_max)
        elif model['Type'] in ['input_token_count', 'output_token_count']:
            usage = np.random.randint(token_min, token_max)

        cost_per_use = usage * model['Unit Cost ($)']
        total_monthly_cost += cost_per_use

    user_monthly_usage.append({
        'User ID': user_id,
        'Total Prompts': num_uses_per_month,
        'Total Monthly Cost ($)': total_monthly_cost
    })

# Crear un DataFrame con los resultados
all_simulations_df = pd.DataFrame(user_monthly_usage)

# Mostrar resumen de resultados
st.header("Summary of Results")
st.write(all_simulations_df.describe())

# Graficar la distribución del costo total mensual
st.subheader("Distribution of Total Monthly Cost per User")
plt.figure(figsize=(12, 6))
plt.hist(all_simulations_df['Total Monthly Cost ($)'], bins=30, color='skyblue', edgecolor='black', alpha=0.7)
plt.axvline(all_simulations_df['Total Monthly Cost ($)'].mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: ${all_simulations_df["Total Monthly Cost ($)"].mean():.2f}')
plt.title('Distribution of Total Monthly Cost per User')
plt.xlabel('Total Monthly Cost ($)')
plt.ylabel('Frequency')
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.5)
st.pyplot(plt)

# Scatter plot de la relación entre prompts y costo
st.subheader("Scatter Plot: Number of Prompts vs. Total Cost")
plt.figure(figsize=(12, 6))
plt.scatter(all_simulations_df['Total Prompts'], all_simulations_df['Total Monthly Cost ($)'], alpha=0.5, color='green')
plt.title('Number of Prompts vs. Total Monthly Cost')
plt.xlabel('Total Prompts per Month')
plt.ylabel('Total Monthly Cost ($)')
plt.grid(True, linestyle='--', alpha=0.5)
st.pyplot(plt)
