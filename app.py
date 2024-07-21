import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras import datasets, models, layers
import pickle
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import xgboost as xgb
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler
import altair as alt

# Load data and model
df = pd.read_csv('cardekho_dataset.csv')

encoder = OneHotEncoder()
df_encoded = encoder.fit_transform(df[['brand','model', 'seller_type', 'fuel_type', 'transmission_type']])
odf = pd.DataFrame.sparse.from_spmatrix(df_encoded)
dff = df[['vehicle_age', 'km_driven', 'mileage', 'engine', 'max_power', 'selling_price']]
cdf = pd.concat([odf, dff], axis=1)
cdf.columns = cdf.columns.astype(str)

scaler = StandardScaler()
scaler.fit(cdf)

scaler_y = StandardScaler()
scaler_y.fit(df[['selling_price']])

with open('xgboost_model5.pkl', 'rb') as f:
    loaded_model = pickle.load(f)

# Inject custom CSS for the background image
# Inject custom CSS for the background slideshow
# Inject custom CSS for the background slideshow
st.markdown("""
    <style>
    @keyframes slide {
        0% { background: url('https://images.unsplash.com/photo-1488954048779-4d9263af2653?q=80&w=1470&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D') no-repeat center center fixed; }
        50% { background: url('https://images.unsplash.com/photo-1465929517729-473000af12ce?q=80&w=1470&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D') no-repeat center center fixed; }
    }

    .main {
      animation: slide 10s infinite;
      background-size: cover;
      background-position: center;
    }
    .content-box {
      background-color: white;
      padding: 20px;
      border-radius: 10px;
      box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.1);
      margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)




# Main content inside the white box
st.markdown('<div class="content-box">', unsafe_allow_html=True)

st.title("Know the correct price of your Car!")
st.write("Use this app to predict the selling price of your car based on various parameters.")
st.title("Enter the details to predict your car's price")

# Prediction form inside the white box
brand = st.selectbox("Enter brand", (df['brand'].unique()))
bbbb = df[df['brand'] == brand]
model = st.selectbox("Enter Model", bbbb['model'].unique())
aaaa = df[df['model'] == model]

aaaa['engine'] = [int(value) for value in aaaa['engine']]
aaaa['max_power'] = [int(value) for value in aaaa['max_power']]

vehicle_age = st.number_input("Enter age", value=9)
km_driven = st.number_input("Enter km driven", value=120000)
seller_type = 'Individual'
fuel_type = st.selectbox("Enter fuel type", df['fuel_type'].unique())
transmission_type = st.selectbox("Enter transmission type", df['transmission_type'].unique())
mileage = st.number_input("Whats is its mileage (Kmpl)?", value=19.7)
engine = st.selectbox("Enter Engine capacity (cc)", (aaaa['engine'].unique()))
max_power = st.selectbox("Max power in BHP",(aaaa['max_power'].unique()))
seats = st.selectbox("Number of seats",aaaa['seats'].unique())

if vehicle_age < 0:
    st.error("Vehicle age cannot be negative.")
if km_driven < 0:
    st.error("Kilometers driven cannot be negative.")

# Prepare the input data
X = [[brand, model , vehicle_age, km_driven, seller_type, fuel_type, transmission_type, mileage, engine, max_power, seats, 0]]
columns = ['brand','model', 'vehicle_age', 'km_driven', 'seller_type', 'fuel_type', 'transmission_type', 'mileage', 'engine', 'max_power', 'seats', 'selling_price']
X = pd.DataFrame(X, columns=columns)

# One-hot encode the categorical features
X_enc = encoder.transform(X[['brand','model', 'seller_type', 'fuel_type', 'transmission_type']])
X_enc = pd.DataFrame.sparse.from_spmatrix(X_enc)

# Combine encoded and numerical features
X_ndf = X[['vehicle_age', 'km_driven', 'mileage', 'engine', 'max_power', 'selling_price']]
X_ccdf = pd.concat([X_enc, X_ndf], axis=1)

# Ensure the column names are string
X_ccdf.columns = X_ccdf.columns.astype(str)

# Standardize the features
X_norm = scaler.transform(X_ccdf)
X_norm = pd.DataFrame(X_norm, columns=X_ccdf.columns)
X_norm = X_norm.drop(columns=['selling_price'])

# Prepare data for prediction
X_for_tree = xgb.DMatrix(X_norm)
y = loaded_model.predict(X_for_tree)

# Inverse transform the predicted value
y = pd.DataFrame(y)
y.columns = ['selling_price']
yd = scaler_y.inverse_transform(y)
yd = pd.DataFrame(yd)
yd.columns = ['selling_price']

# Display prediction result
st.header(f"Predicted Selling Price: ₹{int(yd['selling_price'][0])}")
st.subheader("Note:")
st.write("The predicted price is based on the provided information and market trends. For a more accurate valuation, consider getting an expert inspection.")

# Define initial layout with three columns
col1, col2, col3 = st.columns(3)

# Container for expanded content
expanded_col = st.container()

with col1:
    if st.button("Download Prediction"):
        prediction = int(yd['selling_price'][0])
        prediction_df = pd.DataFrame({
            "Brand": [brand],
            "Model": [model],
            "Predicted Selling Price": [prediction]
        })
        csv = prediction_df.to_csv(index=False)
        expanded_col.download_button(label="Download Prediction", data=csv, file_name='prediction.csv', mime='text/csv')

with col2:
    if st.button("Dataset Summary"):
        st.session_state.dataset_summary = not st.session_state.get('dataset_summary', False)
        if st.session_state.dataset_summary:
            st.subheader("Dataset Summary")
            st.write(df.describe())

with col3:
    if st.button("Visualizations"):
        st.session_state.visualizations = not st.session_state.get('visualizations', False)
        if st.session_state.visualizations:
            st.subheader("Data Visualizations")
            st.write('Visualization of the data we used for model training')

            st.subheader("Interactive Scatter Plot")
            scatter = alt.Chart(df).mark_circle(size=60).encode(
                x='mileage',
                y='selling_price',
                color='fuel_type',
                tooltip=['brand', 'model', 'mileage', 'selling_price']
            ).interactive()

            st.altair_chart(scatter, use_container_width=True)

            st.subheader("Interactive Scatter Plot")
            scatter = alt.Chart(df).mark_circle(size=60).encode(
                x='vehicle_age',
                y='selling_price',
                tooltip=['brand', 'model', 'mileage', 'selling_price']
            ).interactive()

            st.altair_chart(scatter, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# Sidebar for help
st.sidebar.subheader("Need Help?")
st.sidebar.info("If you have any questions or need assistance, please contact our support team.")
